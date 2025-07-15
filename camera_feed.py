import pygame
import webbrowser
import threading
import time
import re

class CameraFeed:
    def __init__(self):
        self.camera_list = self.load_all_cameras()
        self.current_status = "Ready"
        self.feed_thread = None
        self.stop_thread = False
        
        # Patterns for different feed types
        self.youtube_pattern = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        )
        self.interactive_sites = [
            'hdontap.com',
            'earthcam.com',
            'skylinewebcams.com',
            'webcamtaxi.com'
        ]

    def load_all_cameras(self):
        """Load cameras from all region files"""
        from regions.north_america import NORTH_AMERICA_CAMERAS
        from regions.europe import EUROPE_CAMERAS
        from regions.asia import ASIA_CAMERAS
        from regions.oceania import OCEANIA_CAMERAS
        from regions.africa import AFRICA_CAMERAS
        from regions.south_america import SOUTH_AMERICA_CAMERAS
        
        return (NORTH_AMERICA_CAMERAS + EUROPE_CAMERAS + 
                ASIA_CAMERAS + OCEANIA_CAMERAS + 
                AFRICA_CAMERAS + SOUTH_AMERICA_CAMERAS)

    def requires_browser(self, url):
        """Check if URL requires browser interaction"""
        url_lower = url.lower()
        if self.youtube_pattern.search(url_lower):
            return True
        return any(site in url_lower for site in self.interactive_sites)

    def open_in_browser(self, url):
        """Handle browser-based feeds"""
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            self.current_status = f"Browser error: {str(e)}"
            return False

    def show_feed(self, camera_data):
        """Main feed display function"""
        # Reset state
        self.current_status = "Starting..."
        self.stop_thread = False

        # Check feed type
        if self.requires_browser(camera_data["feed_url"]):
            self.current_status = "Opening in browser..."
            
            # Start thread to open browser
            self.feed_thread = threading.Thread(
                target=self.open_in_browser,
                args=(camera_data["feed_url"],),
                daemon=True
            )
            self.feed_thread.start()
        else:
            self.current_status = "Direct feeds not supported - opening in browser"
            self.open_in_browser(camera_data["feed_url"])

        # Initialize display window
        pygame.init()
        screen = pygame.display.set_mode((900, 650))
        pygame.display.set_caption(f"Feed: {camera_data['name']}")
        font = pygame.font.SysFont('Arial', 24)
        small_font = pygame.font.SysFont('Arial', 16)
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Clear screen
            screen.fill((0, 0, 0))

            # Display camera info
            info = [
                f"{camera_data['name']}",
                f"Location: {camera_data['city']}, {camera_data['country']}",
                f"Coordinates: {camera_data['latitude']}, {camera_data['longitude']}",
                "",
                f"Feed URL: {camera_data['feed_url']}",
                "",
                self.current_status
            ]
            
            for i, line in enumerate(info):
                if line:  # Skip empty lines
                    text = font.render(line, True, (255, 255, 255))
                    screen.blit(text, (20, 20 + i * 30))

            # Additional help text
            help_texts = [
                "Tip: The live feed should open in your web browser",
                "If nothing happens, try clicking the URL above",
                "Press ESC to return to the map"
            ]
            
            for i, text in enumerate(help_texts):
                help_surface = small_font.render(text, True, (200, 200, 200))
                screen.blit(help_surface, (20, 220 + i * 25))

            pygame.display.flip()
            clock.tick(30)

            # Close window after browser opens
            if "Opening in browser" in self.current_status and self.feed_thread:
                if not self.feed_thread.is_alive():
                    pygame.time.delay(2000)  # Give browser time to open
                    running = False

        # Clean up
        self.stop_thread = True
        if self.feed_thread and self.feed_thread.is_alive():
            self.feed_thread.join(timeout=1)
        pygame.quit()
