#!/usr/bin/env python3
"""Pi-hole Dashboard - Main entry point"""

import os
import sys
import time
import subprocess
import pygame

from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    API_UPDATE_INTERVAL,
    SWIPE_THRESHOLD,
    TOTAL_SCREENS,
    SCREEN_STATS,
    SCREEN_GRAPH,
    SCREEN_BLOCKED,
    SCREEN_CLIENTS,
    SCREEN_SYSTEM,
)
from ui.fonts import PixelFont
from ui.components import UIComponents
from ui.colors import BLACK
from api.pihole import PiholeAPI
from screens import (
    StatsScreen,
    GraphScreen,
    BlockedScreen,
    ClientsScreen,
    SystemScreen,
)


class Dashboard:
    """Main dashboard application"""

    def __init__(self) -> None:
        # Initialize Pygame
        os.environ["SDL_VIDEODRIVER"] = "x11"
        pygame.init()

        # Setup display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pi-hole Dashboard")
        pygame.mouse.set_visible(False)

        # Initialize components
        self.clock = pygame.time.Clock()
        self.font = PixelFont()
        self.ui = UIComponents(self.font)
        self.api = PiholeAPI()

        # Initialize screens
        self.screens = [
            StatsScreen(self.font, self.ui),
            GraphScreen(self.font, self.ui),
            BlockedScreen(self.font, self.ui),
            ClientsScreen(self.font, self.ui),
            SystemScreen(self.font, self.ui),
        ]

        # State
        self.current_screen = 0
        self.running = True
        self.last_api_update = 0

        # Touch handling
        self.touch_start_x = 0
        self.touch_start_y = 0
        self.is_touching = False

        # Get DNS IP for stats screen
        self.dns_ip = self._get_dns_ip()

    def _get_dns_ip(self) -> str:
        """Get the device IP address"""
        try:
            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            return result.stdout.strip().split()[0] if result.stdout.strip() else "N/A"
        except Exception:
            return "N/A"

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_LEFT:
                    self.current_screen = (self.current_screen - 1) % TOTAL_SCREENS
                elif event.key == pygame.K_RIGHT:
                    self.current_screen = (self.current_screen + 1) % TOTAL_SCREENS
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.touch_start_x, self.touch_start_y = event.pos
                self.is_touching = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_touching:
                    end_x, end_y = event.pos
                    diff_x = end_x - self.touch_start_x

                    if diff_x < -SWIPE_THRESHOLD:
                        # Swipe left - next screen
                        self.current_screen = (self.current_screen + 1) % TOTAL_SCREENS
                    elif diff_x > SWIPE_THRESHOLD:
                        # Swipe right - previous screen
                        self.current_screen = (self.current_screen - 1) % TOTAL_SCREENS

                    self.is_touching = False

    def update(self) -> None:
        """Update dashboard data"""
        current_time = time.time()

        if current_time - self.last_api_update > API_UPDATE_INTERVAL:
            # Fetch all API data
            summary = self.api.get_summary()
            summary["dns_ip"] = self.dns_ip

            overtime = self.api.get_overtime()
            blocked = self.api.get_top_blocked()
            clients = self.api.get_top_clients()

            # Store data for continuous updates
            self._summary = summary
            self._overtime = overtime
            self._blocked = blocked
            self._clients = clients

            self.last_api_update = current_time

        # Update screens every frame for animations
        if hasattr(self, '_summary'):
            self.screens[SCREEN_STATS].update(self._summary)
        if hasattr(self, '_overtime'):
            self.screens[SCREEN_GRAPH].update(self._overtime)
        if hasattr(self, '_blocked'):
            self.screens[SCREEN_BLOCKED].update(self._blocked)
        if hasattr(self, '_clients'):
            self.screens[SCREEN_CLIENTS].update(self._clients)

        # System screen updates more frequently (handled internally)
        self.screens[SCREEN_SYSTEM].update({})

    def draw(self) -> None:
        """Draw the current screen"""
        self.screen.fill(BLACK)

        # Draw current screen
        self.screens[self.current_screen].draw(self.screen)

        # Draw screen indicators
        self.ui.draw_screen_indicators(self.screen, self.current_screen, TOTAL_SCREENS)

        # Draw scanlines effect
        self.ui.draw_scanlines(self.screen)

        pygame.display.flip()

    def run(self) -> None:
        """Main loop"""
        print("Starting Pi-hole Dashboard...")

        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        print("Dashboard closed.")


def main() -> None:
    """Entry point"""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
