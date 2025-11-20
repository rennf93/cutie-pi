#!/usr/bin/env python3
"""Pi-hole Dashboard - Main entry point"""

import os
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
    SCREEN_SETTINGS,
    THEME,
)
from ui.fonts import PixelFont
from ui.components import UIComponents
from ui import colors
from ui.colors import reload_theme
from utils.logger import logger
from api.pihole import PiholeAPI
from screens import (
    StatsScreen,
    GraphScreen,
    BlockedScreen,
    ClientsScreen,
    SystemScreen,
    SettingsScreen,
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
            SettingsScreen(self.font, self.ui),
        ]

        # Current theme
        self.current_theme = THEME

        # Settings
        self.scanlines_enabled = True
        self.show_fps = False
        self.screen_timeout = 0  # minutes, 0 = never
        self.api_update_interval = API_UPDATE_INTERVAL
        self.last_activity = time.time()
        self.display_asleep = False

        # State
        self.current_screen = 0
        self.running = True
        self.last_api_update: float = 0

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
                self.last_activity = time.time()
                if self.display_asleep:
                    self._wake_display()
                    continue
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_LEFT:
                    self.current_screen = (self.current_screen - 1) % TOTAL_SCREENS
                elif event.key == pygame.K_RIGHT:
                    self.current_screen = (self.current_screen + 1) % TOTAL_SCREENS
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.last_activity = time.time()
                # If display is asleep, wake it and ignore this touch
                if self.display_asleep:
                    self._wake_display()
                    self.is_touching = False
                    continue
                self.touch_start_x, self.touch_start_y = event.pos
                self.is_touching = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.is_touching:
                    end_x, end_y = event.pos
                    diff_x = end_x - self.touch_start_x

                    # Check for tap (not swipe) on settings screen
                    if (
                        abs(diff_x) < SWIPE_THRESHOLD
                        and self.current_screen == SCREEN_SETTINGS
                    ):
                        action = self.screens[SCREEN_SETTINGS].handle_tap(
                            (end_x, end_y)
                        )
                        if action:
                            self._handle_settings_action(action)
                    elif diff_x < -SWIPE_THRESHOLD:
                        # Swipe left - next screen
                        self.current_screen = (self.current_screen + 1) % TOTAL_SCREENS
                    elif diff_x > SWIPE_THRESHOLD:
                        # Swipe right - previous screen
                        self.current_screen = (self.current_screen - 1) % TOTAL_SCREENS

                    self.is_touching = False

    def _handle_settings_action(self, action: dict) -> None:
        """Handle settings changes"""
        action_type = action.get("action")

        if action_type == "change_theme":
            self._change_theme(action["theme"])
        elif action_type == "toggle_scanlines":
            self.scanlines_enabled = action["enabled"]
        elif action_type == "toggle_fps":
            self.show_fps = action["enabled"]
        elif action_type == "set_brightness":
            self._set_brightness(action["value"])
        elif action_type == "set_api_interval":
            self.api_update_interval = action["value"]
        elif action_type == "set_timeout":
            self.screen_timeout = action["value"]

    def _change_theme(self, theme_name: str) -> None:
        """Change the current theme"""
        reload_theme(theme_name)
        self.current_theme = theme_name
        logger.info(f"Theme changed to: {theme_name}")

    def _set_brightness(self, value: int) -> None:
        """Set screen brightness (0-100)"""
        # Try common backlight paths for Raspberry Pi
        brightness_paths = [
            "/sys/class/backlight/rpi_backlight/brightness",
            "/sys/class/backlight/10-0045/brightness",
            "/sys/class/backlight/backlight/brightness",
        ]

        for path in brightness_paths:
            try:
                # Read max brightness
                max_path = path.replace("brightness", "max_brightness")
                with open(max_path, "r") as f:
                    max_brightness = int(f.read().strip())

                # Calculate actual value
                actual = int((value / 100) * max_brightness)

                with open(path, "w") as f:
                    f.write(str(actual))
                logger.info(f"Brightness set to {value}%")
                return
            except (FileNotFoundError, PermissionError, IOError):
                continue

        logger.error("Could not set brightness - no backlight found")

    def _sleep_display(self) -> None:
        """Put display to sleep"""
        if self.display_asleep:
            return

        # Set DISPLAY for xset commands
        env = os.environ.copy()
        env["DISPLAY"] = ":0"

        # Try multiple methods to turn off display
        try:
            # Method 1: DPMS via xset
            subprocess.run(
                ["xset", "dpms", "force", "off"],
                env=env,
                capture_output=True,
                timeout=2,
            )
        except Exception:
            pass

        try:
            # Method 2: Backlight power control
            bl_paths = [
                "/sys/class/backlight/rpi_backlight/bl_power",
                "/sys/class/backlight/10-0045/bl_power",
            ]
            for path in bl_paths:
                try:
                    with open(path, "w") as f:
                        f.write("1")  # 1 = off
                    break
                except (FileNotFoundError, PermissionError):
                    continue
        except Exception:
            pass

        self.display_asleep = True
        logger.info("Display sleeping")

    def _wake_display(self) -> None:
        """Wake display from sleep"""
        if not self.display_asleep:
            return

        # Set DISPLAY for xset commands
        env = os.environ.copy()
        env["DISPLAY"] = ":0"

        # Try multiple methods to turn on display
        try:
            # Method 1: DPMS via xset
            subprocess.run(
                ["xset", "dpms", "force", "on"], env=env, capture_output=True, timeout=2
            )
        except Exception:
            pass

        try:
            # Method 2: Backlight power control
            bl_paths = [
                "/sys/class/backlight/rpi_backlight/bl_power",
                "/sys/class/backlight/10-0045/bl_power",
            ]
            for path in bl_paths:
                try:
                    with open(path, "w") as f:
                        f.write("0")  # 0 = on
                    break
                except (FileNotFoundError, PermissionError):
                    continue
        except Exception:
            pass

        self.display_asleep = False
        self.last_activity = time.time()
        logger.info("Display waking")

    def update(self) -> None:
        """Update dashboard data"""
        current_time = time.time()

        # Check for screen timeout
        if self.screen_timeout > 0 and not self.display_asleep:
            idle_time = current_time - self.last_activity
            if idle_time > self.screen_timeout * 60:  # Convert minutes to seconds
                self._sleep_display()

        if current_time - self.last_api_update > self.api_update_interval:
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
        if hasattr(self, "_summary"):
            self.screens[SCREEN_STATS].update(self._summary)
        if hasattr(self, "_overtime"):
            self.screens[SCREEN_GRAPH].update(self._overtime)
        if hasattr(self, "_blocked"):
            self.screens[SCREEN_BLOCKED].update(self._blocked)
        if hasattr(self, "_clients"):
            self.screens[SCREEN_CLIENTS].update(self._clients)

        # System screen updates more frequently (handled internally)
        self.screens[SCREEN_SYSTEM].update({})

        # Settings screen
        self.screens[SCREEN_SETTINGS].update({"current_theme": self.current_theme})

    def draw(self) -> None:
        """Draw the current screen"""
        # Don't draw anything if display is asleep
        if self.display_asleep:
            return

        self.screen.fill(colors.BLACK())

        # Draw current screen
        self.screens[self.current_screen].draw(self.screen)

        # Draw screen indicators
        self.ui.draw_screen_indicators(self.screen, self.current_screen, TOTAL_SCREENS)

        # Draw scanlines effect (if enabled)
        if self.scanlines_enabled:
            self.ui.draw_scanlines(self.screen)

        # Draw FPS counter (if enabled)
        if self.show_fps:
            fps = self.clock.get_fps()
            fps_text = self.font.tiny.render(f"FPS:{fps:.0f}", True, colors.GRAY())
            surface_width = self.screen.get_width()
            self.screen.blit(fps_text, (surface_width - fps_text.get_width() - 5, 5))

        pygame.display.flip()

    def run(self) -> None:
        """Main loop"""
        logger.info("Starting Pi-hole Dashboard...")

        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        logger.info("Dashboard closed.")


def main() -> None:
    """Entry point"""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
