"""Settings screen for runtime configuration"""

import pygame

from config import VERSION
from ui import colors
from ui.components import UIComponents
from ui.fonts import PixelFont
from ui.themes import list_themes

from .base import BaseScreen


def _get_radius() -> int:
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

    def _handle_arrow_tap(self, x: int, values: list, index: int) -> int:
        """Handle arrow tap for cycling through values"""
        if x >= 260 and x <= 295:  # Left arrow
            return (index - 1) % len(values)
        elif x >= 430:  # Right arrow
            return (index + 1) % len(values)
        return index

    def _handle_theme_tap(self, x: int) -> dict | None:
        """Handle theme option tap"""
        new_index = self._handle_arrow_tap(x, self.themes, self.current_theme_index)
        if new_index != self.current_theme_index:
            self.current_theme_index = new_index
            return {
                "action": "change_theme",
                "theme": self.themes[self.current_theme_index],
            }
        return None

    def _handle_brightness_tap(self, x: int) -> dict:
        """Handle brightness option tap"""
        if x >= 260 and x <= 295:
            self.brightness = max(10, self.brightness - 10)
        elif x >= 430:
            self.brightness = min(100, self.brightness + 10)
        return {"action": "set_brightness", "value": self.brightness}

    def _handle_api_interval_tap(self, x: int) -> dict:
        """Handle API interval option tap"""
        self.api_interval_index = self._handle_arrow_tap(
            x, self.API_INTERVALS, self.api_interval_index
        )
        return {
            "action": "set_api_interval",
            "value": self.API_INTERVALS[self.api_interval_index],
        }

    def _handle_timeout_tap(self, x: int) -> dict:
        """Handle timeout option tap"""
        self.screen_timeout_index = self._handle_arrow_tap(
            x, self.TIMEOUT_OPTIONS, self.screen_timeout_index
        )
        return {
            "action": "set_timeout",
            "value": self.TIMEOUT_OPTIONS[self.screen_timeout_index],
        }

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

        # Check option selection
        tapped_option = None
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(pos):
                tapped_option = i
                self.selected_option = i
                break

        if tapped_option is None:
            return None

        # Dispatch to option handlers
        handlers = {
            0: lambda: self._handle_theme_tap(x),
            1: lambda: self._toggle_scanlines(),
            2: lambda: self._toggle_fps(),
            3: lambda: self._handle_brightness_tap(x),
            4: lambda: self._handle_api_interval_tap(x),
            5: lambda: self._handle_timeout_tap(x),
        }

        handler = handlers.get(tapped_option)
        return handler() if handler else None

    def _toggle_scanlines(self) -> dict:
        """Toggle scanlines setting"""
        self.scanlines_enabled = not self.scanlines_enabled
        return {"action": "toggle_scanlines", "enabled": self.scanlines_enabled}

    def _toggle_fps(self) -> dict:
        """Toggle FPS display setting"""
        self.show_fps = not self.show_fps
        return {"action": "toggle_fps", "enabled": self.show_fps}

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
        def draw_row(label: str, value: str, has_arrows: bool = True) -> None:
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
                # Toggle - center value like other settings
                value_text = self.font.small.render(value, True, colors.WHITE())
                text_x = 290 + (140 - value_text.get_width()) // 2
                surface.blit(value_text, (text_x, y + 12))

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
