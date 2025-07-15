
import pygame
import json
import math
import sys
from pygame.locals import *
from PIL import Image, ImageChops

class MapManager:
    def __init__(self, config_path):
        # Load configuration
        with open(config_path) as f:
            self.settings = json.load(f)
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.settings["window_width"], self.settings["window_height"])
        )
        pygame.display.set_caption("World Map Viewer - Scroll to Zoom, Drag to Pan")
        
        # Load and preprocess map image
        self.original_map = self._load_and_crop_map(self.settings["map_image"])
        self.map_width, self.map_height = self.original_map.get_size()
        
        # Zoom/pan variables
        self.zoom_level = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 4.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        
        # Camera dots
        self.camera_dots = []
        self.selected_camera = None
        
        # Calculate initial scale to fit window
        self.base_scale = min(
            self.settings["window_width"] / self.map_width,
            self.settings["window_height"] / self.map_height
        )
        
        # Center map initially
        self._center_map()

    def _load_and_crop_map(self, image_path):
        """Remove white background and return clean map surface"""
        try:
            pil_img = Image.open(image_path)
            
            # Remove white background (adjust RGB values if needed)
            bg = Image.new("RGB", pil_img.size, (255, 255, 255))
            diff = ImageChops.difference(pil_img.convert("RGB"), bg)
            bbox = diff.getbbox()
            
            if bbox:
                pil_img = pil_img.crop(bbox)
            
            # Convert to pygame surface
            return pygame.image.fromstring(
                pil_img.tobytes(), 
                pil_img.size, 
                pil_img.mode
            )
        except Exception as e:
            print(f"Error loading map image: {e}")
            sys.exit(1)

    def _center_map(self):
        """Center the map in the window"""
        self.offset_x = (self.settings["window_width"] - self.map_width * self.base_scale * self.zoom_level) / 2
        self.offset_y = (self.settings["window_height"] - self.map_height * self.base_scale * self.zoom_level) / 2

    def add_camera(self, camera_data):
        """Add a camera marker to the map"""
        self.camera_dots.append({
            "lat": camera_data["latitude"],
            "lon": camera_data["longitude"],
            "data": camera_data,
            "base_radius": self.settings["dot_radius"]
        })
        self._update_camera_positions()

    def latlon_to_pixel(self, lat, lon):
        """Convert geographic coordinates to screen pixels using Mercator projection"""
        # Clamp latitude to avoid infinity at poles
        lat = max(min(lat, 89.99), -89.99)
        
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        
        # Mercator projection math
        x = (lon_rad + math.pi) * (self.map_width / (2 * math.pi))
        y = (math.log(math.tan(math.pi/4 + lat_rad/2))) * (self.map_height / (2 * math.pi))
        y = self.map_height/2 - y  # Flip Y axis
        
        # Apply current zoom and pan
        screen_x = int(x * self.base_scale * self.zoom_level + self.offset_x)
        screen_y = int(y * self.base_scale * self.zoom_level + self.offset_y)
        
        return screen_x, screen_y

    def _update_camera_positions(self):
        """Update all camera positions after zoom/pan"""
        for dot in self.camera_dots:
            dot["x"], dot["y"] = self.latlon_to_pixel(dot["lat"], dot["lon"])
            # Scale dot size inversely with zoom
            dot["current_radius"] = max(3, dot["base_radius"] / self.zoom_level)

    def _constrain_map(self):
        """Keep map within window boundaries"""
        scaled_width = self.map_width * self.base_scale * self.zoom_level
        scaled_height = self.map_height * self.base_scale * self.zoom_level
        
        # Prevent zooming out too far
        if scaled_width < self.settings["window_width"] and scaled_height < self.settings["window_height"]:
            self.zoom_level = min(
                self.settings["window_width"] / (self.map_width * self.base_scale),
                self.settings["window_height"] / (self.map_height * self.base_scale)
            )
            self._center_map()
            return
        
        # Horizontal constraints
        if scaled_width <= self.settings["window_width"]:
            self.offset_x = (self.settings["window_width"] - scaled_width) / 2
        else:
            self.offset_x = min(0, self.offset_x)  # Left edge
            self.offset_x = max(self.settings["window_width"] - scaled_width, self.offset_x)  # Right edge
        
        # Vertical constraints
        if scaled_height <= self.settings["window_height"]:
            self.offset_y = (self.settings["window_height"] - scaled_height) / 2
        else:
            self.offset_y = min(0, self.offset_y)  # Top edge
            self.offset_y = max(self.settings["window_height"] - scaled_height, self.offset_y)  # Bottom edge

    def zoom(self, factor, mouse_pos=None):
        """Zoom centered on mouse position with boundaries"""
        mouse_pos = mouse_pos or (self.settings["window_width"]//2, self.settings["window_height"]//2)
        
        # Store mouse position in map coordinates before zoom
        old_lat, old_lon = self.pixel_to_latlon(mouse_pos[0], mouse_pos[1])
        
        # Apply zoom with boundaries
        new_zoom = self.zoom_level * factor
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
            
        self.zoom_level = new_zoom
        
        # Calculate new position to keep mouse point stable
        new_x, new_y = self.latlon_to_pixel(old_lat, old_lon)
        self.offset_x += mouse_pos[0] - new_x
        self.offset_y += mouse_pos[1] - new_y
        
        # Ensure map stays within bounds
        self._constrain_map()
        self._update_camera_positions()

    def pixel_to_latlon(self, x, y):
        """Convert screen pixels back to geographic coordinates"""
        # Remove offset and zoom
        map_x = (x - self.offset_x) / (self.base_scale * self.zoom_level)
        map_y = (y - self.offset_y) / (self.base_scale * self.zoom_level)
        
        # Convert to lat/lon (inverse Mercator)
        lon = (map_x / self.map_width) * 360 - 180
        lat_rad = 2 * math.atan(math.exp((self.map_height/2 - map_y) * (2 * math.pi / self.map_height))) - math.pi/2
        lat = math.degrees(lat_rad)
        
        return lat, lon

    def draw_map(self):
        """Draw everything with proper boundaries"""
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Calculate scaled map size
        scaled_width = int(self.map_width * self.base_scale * self.zoom_level)
        scaled_height = int(self.map_height * self.base_scale * self.zoom_level)
        
        # Scale map
        scaled_map = pygame.transform.scale(self.original_map, (scaled_width, scaled_height))
        
        # Draw map
        self.screen.blit(scaled_map, (self.offset_x, self.offset_y))
        
        # Draw camera dots
        for dot in self.camera_dots:
            if (0 <= dot["x"] < self.settings["window_width"] and 
                0 <= dot["y"] < self.settings["window_height"]):
                color = (255, 0, 0) if dot == self.selected_camera else (255, 255, 0)
                pygame.draw.circle(self.screen, color, (dot["x"], dot["y"]), int(dot["current_radius"]))
        
        pygame.display.flip()

    def handle_events(self):
        """Handle all input events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    clicked_camera = self.handle_click(event.pos)
                    if clicked_camera:
                        return clicked_camera
                
                elif event.button == 4:  # Mouse wheel up (zoom in)
                    self.zoom(1.1, event.pos)
                
                elif event.button == 5:  # Mouse wheel down (zoom out)
                    self.zoom(0.9, event.pos)
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self.dragging = False
            
            elif event.type == MOUSEMOTION:
                if self.dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.offset_x += dx
                    self.offset_y += dy
                    self.last_mouse_pos = event.pos
                    self._constrain_map()
                    self._update_camera_positions()
        
        return None

    def handle_click(self, pos):
        """Check if camera was clicked (considering zoom)"""
        for dot in self.camera_dots:
            distance = ((pos[0] - dot["x"])**2 + (pos[1] - dot["y"])**2)**0.5
            if distance <= dot["current_radius"] * 2:  # Use current radius for hit detection
                self.selected_camera = dot
                return dot["data"]
        return None

    def run(self):
        """Main loop"""
        clock = pygame.time.Clock()
        
        while True:
            result = self.handle_events()
            if result is not None:
                if result is False:  # Window closed
                    pygame.quit()
                    return None
                return result  # Camera selected
            
            self.draw_map()
            clock.tick(60)

if __name__ == "__main__":
    # Test with known locations
    test_config = {
        "map_image": "world_map.jpg",
        "window_width": 1200,
        "window_height": 700,
        "dot_radius": 5
    }
    
    with open("test_config.json", "w") as f:
        json.dump(test_config, f)
    
    manager = MapManager("test_config.json")
    
    test_cameras = [
        {"latitude": 51.5074, "longitude": -0.1278, "name": "London"},
        {"latitude": 40.7128, "longitude": -74.0060, "name": "New York"},
        {"latitude": 35.6762, "longitude": 139.6503, "name": "Tokyo"},
        {"latitude": -33.8688, "longitude": 151.2093, "name": "Sydney"},
        {"latitude": 0, "longitude": 0, "name": "Prime Meridian/Equator"}
    ]
    
    for cam in test_cameras:
        manager.add_camera(cam)
    
    manager.run()
