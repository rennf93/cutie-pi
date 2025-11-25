"""Settings screen for runtime configuration"""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH, VERSION, Layout
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
        self.lock_rect = pygame.Rect(
            SCREEN_WIDTH - Layout.margin_lg * 2, Layout.margin_xs,
            Layout.margin_lg + Layout.margin_sm, Layout.margin_lg
        )

    def update(self, data: dict) -> None:
        """Update settings data"""
        # Get current theme from data or default
        current_theme = data.get("current_theme", "default")
        if current_theme in self.themes:
            self.current_theme_index = self.themes.index(current_theme)

    def _handle_arrow_tap(self, x: int, values: list, index: int) -> int:
        """Handle arrow tap for cycling through values"""
        if x >= Layout.arrow_tap_left_start and x <= Layout.arrow_tap_left_end:
            return (index - 1) % len(values)
        elif x >= Layout.arrow_tap_right_start:
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
        if x >= Layout.arrow_tap_left_start and x <= Layout.arrow_tap_left_end:
            self.brightness = max(10, self.brightness - 10)
        elif x >= Layout.arrow_tap_right_start:
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
        surface.blit(title, (Layout.title_x, Layout.title_y))

        # Lock icon in top right (before version)
        lock_x = SCREEN_WIDTH - Layout.margin_lg - Layout.margin_sm
        lock_y = Layout.margin_md
        lock_body_w = max(12, int(16 * Layout.scale_x))
        lock_body_h = max(9, int(12 * Layout.scale_y))
        lock_color = colors.RED() if self.locked else colors.GREEN()
        # Draw lock body
        pygame.draw.rect(surface, lock_color, (lock_x, lock_y, lock_body_w, lock_body_h))
        # Draw lock shackle (arch)
        shackle_w = max(9, int(12 * Layout.scale_x))
        shackle_h = max(9, int(12 * Layout.scale_y))
        if self.locked:
            # Closed shackle
            pygame.draw.arc(
                surface, lock_color,
                (lock_x + 2, lock_y - shackle_h + 3, shackle_w, shackle_h),
                0, 3.14, 2
            )
        else:
            # Open shackle (shifted right)
            pygame.draw.arc(
                surface, lock_color,
                (lock_x + Layout.margin_xs, lock_y - shackle_h + 3, shackle_w, shackle_h),
                0, 3.14, 2
            )

        # Version below lock
        version_text = self.font.tiny.render(f"v{VERSION}", True, colors.GRAY())
        surface.blit(version_text, (SCREEN_WIDTH - version_text.get_width() - Layout.margin_sm, lock_y + lock_body_h + 3))

        y = Layout.row_start_y
        row_height = Layout.row_height_md
        row_spacing = Layout.margin_xs
        self.option_rects = []

        # Responsive positioning for arrows and values
        left_arrow_x = Layout.arrow_left_x
        value_start_x = Layout.value_x
        right_arrow_x = Layout.arrow_right_x
        arrow_v_offset = row_height // 2
        arrow_half_h = Layout.arrow_half_height
        arrow_w = Layout.arrow_width
        text_v_offset = int(row_height * 0.32)

        # Helper to draw a setting row
        def draw_row(label: str, value: str, has_arrows: bool = True) -> None:
            nonlocal y
            row_width = SCREEN_WIDTH - Layout.margin_md * 2
            option_rect = pygame.Rect(Layout.rank_x, y, row_width, row_height)
            self.option_rects.append(option_rect)

            idx = len(self.option_rects) - 1
            is_selected = self.selected_option == idx
            border_color = colors.GREEN() if is_selected else colors.GRAY()

            # Simple line border instead of full box for compact look
            pygame.draw.rect(
                surface,
                border_color,
                (Layout.rank_x, y, row_width, row_height),
                1,
                border_radius=_get_radius(),
            )

            # Label
            label_text = self.font.small.render(label, True, border_color)
            surface.blit(label_text, (Layout.margin_lg, y + text_v_offset))

            if has_arrows:
                arrow_color = colors.WHITE() if is_selected else colors.GRAY()
                # Left arrow - responsive position
                pygame.draw.polygon(
                    surface, arrow_color, [
                        (left_arrow_x, y + arrow_v_offset),
                        (left_arrow_x + arrow_w, y + arrow_v_offset - arrow_half_h),
                        (left_arrow_x + arrow_w, y + arrow_v_offset + arrow_half_h)
                    ]
                )
                # Right arrow - positioned relative to screen width
                pygame.draw.polygon(
                    surface, arrow_color, [
                        (right_arrow_x, y + arrow_v_offset),
                        (right_arrow_x - arrow_w, y + arrow_v_offset - arrow_half_h),
                        (right_arrow_x - arrow_w, y + arrow_v_offset + arrow_half_h)
                    ]
                )
                # Value centered between arrows
                value_text = self.font.small.render(value, True, colors.WHITE())
                value_area_width = right_arrow_x - arrow_w - value_start_x
                text_x = value_start_x + (value_area_width - value_text.get_width()) // 2
                surface.blit(value_text, (text_x, y + text_v_offset))
            else:
                # Toggle - center value like other settings
                value_text = self.font.small.render(value, True, colors.WHITE())
                value_area_width = right_arrow_x - arrow_w - value_start_x
                text_x = value_start_x + (value_area_width - value_text.get_width()) // 2
                surface.blit(value_text, (text_x, y + text_v_offset))

            y += row_height + row_spacing

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
        hint_y = SCREEN_HEIGHT - Layout.header_height
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, hint_y))
