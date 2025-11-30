#!/usr/bin/env python3
"""Pi-hole Dashboard - Main entry point"""

import contextlib
import os
import subprocess
import time

import pygame

from api.pihole import PiholeAPI
from config import (
    API_UPDATE_INTERVAL,
    BRIGHTNESS,
    FPS,
    SCANLINES_ENABLED,
    SCREEN_BLOCKED,
    SCREEN_CLIENTS,
    SCREEN_GRAPH,
    SCREEN_HEIGHT,
    SCREEN_SETTINGS,
    SCREEN_STATS,
    SCREEN_SYSTEM,
    SCREEN_TIMEOUT,
    SCREEN_WIDTH,
    SHOW_FPS,
    SWIPE_THRESHOLD,
    THEME,
    TOTAL_SCREENS,
    save_settings,
)
from screens import (
    BlockedScreen,
    ClientsScreen,
    GraphScreen,
    SettingsScreen,
    StatsScreen,
    SystemScreen,
)
from ui import colors
from ui.colors import reload_theme
from ui.components import UIComponents
from ui.fonts import PixelFont
from utils.logger import logger


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

        # Settings (loaded from config file via environment variables)
        self.scanlines_enabled = SCANLINES_ENABLED
        self.show_fps = SHOW_FPS
        self.screen_timeout = SCREEN_TIMEOUT  # minutes, 0 = never
        self.brightness = BRIGHTNESS
        self.api_update_interval = API_UPDATE_INTERVAL
        self.last_activity = time.time()
        self.display_asleep = False

        # Apply initial brightness if not 100%
        if self.brightness != 100:
            self._set_brightness(self.brightness)

        # Sync settings screen with loaded config values
        settings_screen = self.screens[SCREEN_SETTINGS]
        settings_screen.scanlines_enabled = self.scanlines_enabled
        settings_screen.show_fps = self.show_fps
        settings_screen.brightness = self.brightness
        # Find the index for api_interval and screen_timeout
        if self.api_update_interval in settings_screen.API_INTERVALS:
            settings_screen.api_interval_index = settings_screen.API_INTERVALS.index(
                self.api_update_interval
            )
        if self.screen_timeout in settings_screen.TIMEOUT_OPTIONS:
            settings_screen.screen_timeout_index = settings_screen.TIMEOUT_OPTIONS.index(
                self.screen_timeout
            )

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

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard events"""
        self.last_activity = time.time()
        if self.display_asleep:
            self._wake_display()
            return
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_LEFT:
            self.current_screen = (self.current_screen - 1) % TOTAL_SCREENS
        elif event.key == pygame.K_RIGHT:
            self.current_screen = (self.current_screen + 1) % TOTAL_SCREENS

    def _handle_mouse_down(self, event: pygame.event.Event) -> None:
        """Handle mouse/touch down events"""
        self.last_activity = time.time()
        if self.display_asleep:
            self._wake_display()
            self.is_touching = False
            return
        self.touch_start_x, self.touch_start_y = event.pos
        self.is_touching = True

    def _handle_mouse_up(self, event: pygame.event.Event) -> None:
        """Handle mouse/touch up events"""
        if not self.is_touching:
            return

        end_x, end_y = event.pos
        diff_x = end_x - self.touch_start_x

        # Check for tap (not swipe) on settings screen
        if abs(diff_x) < SWIPE_THRESHOLD and self.current_screen == SCREEN_SETTINGS:
            action = self.screens[SCREEN_SETTINGS].handle_tap((end_x, end_y))
            if action:
                self._handle_settings_action(action)
        elif diff_x < -SWIPE_THRESHOLD:
            self.current_screen = (self.current_screen + 1) % TOTAL_SCREENS
        elif diff_x > SWIPE_THRESHOLD:
            self.current_screen = (self.current_screen - 1) % TOTAL_SCREENS

        self.is_touching = False

    def handle_events(self) -> None:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_up(event)

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
            self.brightness = action["value"]
            self._set_brightness(action["value"])
        elif action_type == "set_api_interval":
            self.api_update_interval = action["value"]
        elif action_type == "set_timeout":
            self.screen_timeout = action["value"]
        elif action_type == "lock_settings":
            self._save_settings()

    def _change_theme(self, theme_name: str) -> None:
        """Change the current theme"""
        reload_theme(theme_name)
        self.current_theme = theme_name
        logger.info(f"Theme changed to: {theme_name}")

    def _save_settings(self) -> None:
        """Save current settings to config file"""
        success = save_settings(
            theme=self.current_theme,
            api_interval=self.api_update_interval,
            screen_timeout=self.screen_timeout,
            scanlines=self.scanlines_enabled,
            show_fps=self.show_fps,
            brightness=self.brightness,
        )
        if success:
            logger.info("Settings saved to config file")
        else:
            logger.warning("Failed to save settings to config file")

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
                with open(max_path) as f:
                    max_brightness = int(f.read().strip())

                # Calculate actual value
                actual = int((value / 100) * max_brightness)

                with open(path, "w") as f:
                    f.write(str(actual))
                logger.info(f"Brightness set to {value}%")
                return
            except OSError:
                continue

        logger.error("Could not set brightness - no backlight found")

    def _sleep_display(self) -> None:
        """Put display to sleep using multiple methods for broad hardware support"""
        if self.display_asleep:
            return

        sleep_success = False

        # Method 1: Framebuffer blanking (works for most displays including PiTFT)
        try:
            with open("/sys/class/graphics/fb0/blank", "w") as f:
                f.write("1")  # 1 = blank
            sleep_success = True
            logger.debug("Display sleep: framebuffer blanking")
        except (FileNotFoundError, PermissionError, OSError):
            pass

        # Method 2: Backlight power control (various paths for different displays)
        bl_power_paths = [
            "/sys/class/backlight/rpi_backlight/bl_power",
            "/sys/class/backlight/10-0045/bl_power",
            "/sys/class/backlight/soc:backlight/bl_power",
            "/sys/class/backlight/backlight/bl_power",
        ]
        for path in bl_power_paths:
            try:
                with open(path, "w") as f:
                    f.write("1")  # 1 = off
                sleep_success = True
                logger.debug(f"Display sleep: backlight power {path}")
                break
            except (FileNotFoundError, PermissionError, OSError):
                continue

        # Method 3: Backlight brightness to 0
        bl_brightness_paths = [
            "/sys/class/backlight/rpi_backlight/brightness",
            "/sys/class/backlight/10-0045/brightness",
            "/sys/class/backlight/soc:backlight/brightness",
            "/sys/class/backlight/backlight/brightness",
        ]
        for path in bl_brightness_paths:
            try:
                # Store original brightness for wake
                with open(path) as f:
                    self._saved_brightness = f.read().strip()
                with open(path, "w") as f:
                    f.write("0")
                sleep_success = True
                self._brightness_path = path
                logger.debug(f"Display sleep: brightness to 0 via {path}")
                break
            except (FileNotFoundError, PermissionError, OSError):
                continue

        # Method 4: DPMS via xset (for X11 environments)
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        try:
            result = subprocess.run(
                ["xset", "dpms", "force", "off"],
                env=env,
                capture_output=True,
                timeout=2,
            )
            if result.returncode == 0:
                sleep_success = True
                logger.debug("Display sleep: DPMS force off")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        self.display_asleep = True
        if sleep_success:
            logger.info("Display sleeping")
        else:
            logger.warning("Display sleep: no working method found")

    def _wake_display(self) -> None:
        """Wake display from sleep using multiple methods for broad hardware support"""
        if not self.display_asleep:
            return

        # Method 1: Framebuffer unblanking
        try:
            with open("/sys/class/graphics/fb0/blank", "w") as f:
                f.write("0")  # 0 = unblank
            logger.debug("Display wake: framebuffer unblanking")
        except (FileNotFoundError, PermissionError, OSError):
            pass

        # Method 2: Backlight power control
        bl_power_paths = [
            "/sys/class/backlight/rpi_backlight/bl_power",
            "/sys/class/backlight/10-0045/bl_power",
            "/sys/class/backlight/soc:backlight/bl_power",
            "/sys/class/backlight/backlight/bl_power",
        ]
        for path in bl_power_paths:
            try:
                with open(path, "w") as f:
                    f.write("0")  # 0 = on
                logger.debug(f"Display wake: backlight power {path}")
                break
            except (FileNotFoundError, PermissionError, OSError):
                continue

        # Method 3: Restore backlight brightness
        if hasattr(self, "_brightness_path") and hasattr(self, "_saved_brightness"):
            try:
                with open(self._brightness_path, "w") as f:
                    f.write(self._saved_brightness)
                logger.debug(f"Display wake: brightness restored via {self._brightness_path}")
            except (FileNotFoundError, PermissionError, OSError):
                pass

        # Method 4: DPMS via xset
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        try:
            subprocess.run(
                ["xset", "dpms", "force", "on"],
                env=env,
                capture_output=True,
                timeout=2,
            )
            logger.debug("Display wake: DPMS force on")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
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
            self.screen.blit(fps_text, ((surface_width - fps_text.get_width()) // 2, 5))

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
