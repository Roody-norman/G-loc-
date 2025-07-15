from map_manager import MapManager
from camera_feed import CameraFeed
import pygame

def main():
    # Initialize pygame once at the start
    pygame.init()
    
    try:
        # Initialize the camera feed manager
        print("Loading camera feeds...")
        camera_manager = CameraFeed()
        
        # Initialize the map with camera dots
        map_manager = MapManager("config_map_settings.json")
        
        # Add all cameras to the map
        print(f"Adding {len(camera_manager.camera_list)} cameras to the map...")
        for camera in camera_manager.camera_list:
            map_manager.add_camera(camera)
        
        # Main application loop
        print("Starting world map viewer. Click on camera dots to view live feeds.")
        while True:
            selected_camera = map_manager.run()
            if selected_camera:
                camera_manager.show_feed(selected_camera)
                # Recreate map manager to reset display
                map_manager = MapManager("config_map_settings.json")
                for camera in camera_manager.camera_list:
                    map_manager.add_camera(camera)
            else:
                break  # User closed the map window
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
