"""Settings screen for runtime configuration"""

import pygame
from .base import BaseScreen
from ui import colors
from ui.fonts import PixelFont
from ui.components import UIComponents
from ui.themes import list_themes
from config import VERSION


def _get_radius():
    """Get border radius based on theme"""
    return 6 if colors.get_style() == "glow" else 0


class SettingsScreen(BaseScreen):
    """Settings configuration display"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        super().__init__(font, ui)
        self.themes = list_themes()
        self.current_theme_index = 0
        self.selected_option = 0

        # Settings values
        self.scanlines_enabled = True
        self.show_fps = False
        self.brightness = 100  # 0-100
        self.api_interval_index = 0  # Index into API_INTERVALS
        self.screen_timeout_index = 0  # Index into TIMEOUT_OPTIONS

        # Options
        self.API_INTERVALS = [5, 10, 30, 60]  # seconds
        self.TIMEOUT_OPTIONS = [0, 1, 5, 10, 30]  # minutes, 0 = never

        # Track touch for option selection
        self.option_rects: list[pygame.Rect] = []

        # Lock state - settings locked by default
        self.locked = True
        self.lock_rect = pygame.Rect(430, 5, 40, 30)  # Lock icon area

    def update(self, data: dict) -> None:
        """Update settings data"""
        # Get current theme from data or default
        current_theme = data.get("current_theme", "default")
        if current_theme in self.themes:
            self.current_theme_index = self.themes.index(current_theme)

    def handle_tap(self, pos: tuple[int, int]) -> dict | None:
        """Handle tap events, return action dict if action needed"""
        x, y = pos

        # Check if lock icon was tapped
        if self.lock_rect.collidepoint(pos):
            self.locked = not self.locked
            return None

        # If locked, ignore all other taps
        if self.locked:
            return None

        # Check option selection first
        tapped_option = None
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                tapped_option = i
                self.selected_option = i
                break

        if tapped_option is None:
            return None

        # Row height is 38, starting at y=45
        # Each option has arrows on right side for value changes

        # Option 0: Theme
        if tapped_option == 0:
            if x >= 260 and x <= 295:  # Left arrow
                self.current_theme_index = (self.current_theme_index - 1) % len(
                    self.themes
                )
                return {
                    "action": "change_theme",
                    "theme": self.themes[self.current_theme_index],
                }
            elif x >= 430:  # Right arrow
                self.current_theme_index = (self.current_theme_index + 1) % len(
                    self.themes
                )
                return {
                    "action": "change_theme",
                    "theme": self.themes[self.current_theme_index],
                }

        # Option 1: Scanlines (toggle)
        elif tapped_option == 1:
            self.scanlines_enabled = not self.scanlines_enabled
            return {"action": "toggle_scanlines", "enabled": self.scanlines_enabled}

        # Option 2: Show FPS (toggle)
        elif tapped_option == 2:
            self.show_fps = not self.show_fps
            return {"action": "toggle_fps", "enabled": self.show_fps}

        # Option 3: Brightness
        elif tapped_option == 3:
            if x >= 260 and x <= 295:  # Left arrow
                self.brightness = max(10, self.brightness - 10)
            elif x >= 430:  # Right arrow
                self.brightness = min(100, self.brightness + 10)
            return {"action": "set_brightness", "value": self.brightness}

        # Option 4: API Interval
        elif tapped_option == 4:
            if x >= 260 and x <= 295:  # Left arrow
                self.api_interval_index = (self.api_interval_index - 1) % len(
                    self.API_INTERVALS
                )
            elif x >= 430:  # Right arrow
                self.api_interval_index = (self.api_interval_index + 1) % len(
                    self.API_INTERVALS
                )
            return {
                "action": "set_api_interval",
                "value": self.API_INTERVALS[self.api_interval_index],
            }

        # Option 5: Screen Timeout
        elif tapped_option == 5:
            if x >= 260 and x <= 295:  # Left arrow
                self.screen_timeout_index = (self.screen_timeout_index - 1) % len(
                    self.TIMEOUT_OPTIONS
                )
            elif x >= 430:  # Right arrow
                self.screen_timeout_index = (self.screen_timeout_index + 1) % len(
                    self.TIMEOUT_OPTIONS
                )
            return {
                "action": "set_timeout",
                "value": self.TIMEOUT_OPTIONS[self.screen_timeout_index],
            }

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the settings screen"""
        surface.fill(colors.BLACK())

        # Title
        title = self.font.medium.render("SETTINGS", True, colors.CYAN())
        surface.blit(title, (10, 10))

        # Lock icon in top right (before version)
        lock_color = colors.RED() if self.locked else colors.GREEN()
        # Draw lock body
        pygame.draw.rect(surface, lock_color, (445, 15, 16, 12))
        # Draw lock shackle (arch)
        if self.locked:
            # Closed shackle
            pygame.draw.arc(surface, lock_color, (447, 6, 12, 12), 0, 3.14, 2)
        else:
            # Open shackle (shifted right)
            pygame.draw.arc(surface, lock_color, (451, 6, 12, 12), 0, 3.14, 2)

        # Version below lock
        version_text = self.font.tiny.render(f"v{VERSION}", True, colors.GRAY())
        surface.blit(version_text, (480 - version_text.get_width() - 10, 28))

        y = 38
        row_height = 38
        self.option_rects = []

        # Helper to draw a setting row
        def draw_row(label: str, value: str, has_arrows: bool = True):
            nonlocal y
            option_rect = pygame.Rect(15, y, 450, row_height)
            self.option_rects.append(option_rect)

            idx = len(self.option_rects) - 1
            is_selected = self.selected_option == idx
            border_color = colors.GREEN() if is_selected else colors.GRAY()

            # Simple line border instead of full box for compact look
            pygame.draw.rect(
                surface,
                border_color,
                (15, y, 450, row_height),
                1,
                border_radius=_get_radius(),
            )

            # Label
            label_text = self.font.small.render(label, True, border_color)
            surface.blit(label_text, (25, y + 12))

            if has_arrows:
                arrow_color = colors.WHITE() if is_selected else colors.GRAY()
                # Left arrow
                pygame.draw.polygon(
                    surface, arrow_color, [(270, y + 19), (280, y + 12), (280, y + 26)]
                )
                # Right arrow
                pygame.draw.polygon(
                    surface, arrow_color, [(450, y + 19), (440, y + 12), (440, y + 26)]
                )
                # Value centered
                value_text = self.font.small.render(value, True, colors.WHITE())
                text_x = 290 + (140 - value_text.get_width()) // 2
                surface.blit(value_text, (text_x, y + 12))
            else:
                # Toggle - just show value on right
                value_text = self.font.small.render(value, True, colors.WHITE())
                surface.blit(value_text, (420 - value_text.get_width(), y + 12))

            y += row_height + 2

        # Row 0: Theme
        theme_name = self.themes[self.current_theme_index].upper()
        draw_row("THEME", theme_name, has_arrows=True)

        # Row 1: Scanlines
        draw_row(
            "SCANLINES", "ON" if self.scanlines_enabled else "OFF", has_arrows=False
        )

        # Row 2: Show FPS
        draw_row("SHOW FPS", "ON" if self.show_fps else "OFF", has_arrows=False)

        # Row 3: Brightness
        draw_row("BRIGHTNESS", f"{self.brightness}%", has_arrows=True)

        # Row 4: API Interval
        interval = self.API_INTERVALS[self.api_interval_index]
        draw_row("API REFRESH", f"{interval}S", has_arrows=True)

        # Row 5: Screen Timeout
        timeout = self.TIMEOUT_OPTIONS[self.screen_timeout_index]
        timeout_str = "NEVER" if timeout == 0 else f"{timeout}M"
        draw_row("TIMEOUT", timeout_str, has_arrows=True)

        # Instructions at bottom
        if self.locked:
            hint = self.font.tiny.render("TAP LOCK TO EDIT", True, colors.GRAY())
        else:
            hint = self.font.tiny.render("TAP TO CHANGE", True, colors.GRAY())
        surface.blit(hint, (240 - hint.get_width() // 2, 285))
