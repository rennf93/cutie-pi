"""Reusable UI components for the dashboard"""

import pygame
from . import colors
from .fonts import PixelFont


class UIComponents:
    """Collection of reusable UI drawing functions"""

    def __init__(self, font: PixelFont) -> None:
        self.font = font

    def _interpolate_color(
        self, color1: tuple[int, int, int], color2: tuple[int, int, int], factor: float
    ) -> tuple[int, int, int]:
        """Interpolate between two colors"""
        return (
            int(color1[0] + (color2[0] - color1[0]) * factor),
            int(color1[1] + (color2[1] - color1[1]) * factor),
            int(color1[2] + (color2[2] - color1[2]) * factor),
        )

    def draw_glow_border(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
        glow_color: tuple[int, int, int] | None = None,
        border_radius: int = 8,
        glow_size: int = 4,
    ) -> None:
        """Draw a rounded border with glow effect"""
        x, y, w, h = rect

        if glow_color is None:
            glow_color = color

        # Draw glow layers (outer to inner)
        for i in range(glow_size, 0, -1):
            alpha = int(60 * (1 - i / glow_size))
            glow_surface = pygame.Surface((w + i * 4, h + i * 4), pygame.SRCALPHA)
            glow_rect = pygame.Rect(i, i, w + i * 2, h + i * 2)
            pygame.draw.rect(
                glow_surface,
                (*glow_color, alpha),
                glow_rect,
                border_radius=border_radius + i,
                width=2,
            )
            surface.blit(glow_surface, (x - i * 2, y - i * 2))

        # Draw main border
        pygame.draw.rect(surface, color, rect, border_radius=border_radius, width=3)

        # Inner highlight (top-left)
        highlight_color = self._interpolate_color(color, (255, 255, 255), 0.3)
        inner_rect = pygame.Rect(x + 2, y + 2, w - 4, h - 4)
        pygame.draw.rect(
            surface,
            highlight_color,
            inner_rect,
            border_radius=border_radius - 2,
            width=1,
        )

    def draw_gradient_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color_start: tuple[int, int, int],
        color_end: tuple[int, int, int] | None = None,
        bg_color: tuple[int, int, int] | None = None,
        border_radius: int = 4,
    ) -> None:
        """Draw a gradient progress bar with rounded corners"""
        if bg_color is None:
            bg_color = colors.DARK_GRAY()
        if color_end is None:
            color_end = color_start

        # Background
        pygame.draw.rect(
            surface, bg_color, (x, y, width, height), border_radius=border_radius
        )

        # Filled portion
        fill_width = int((percent / 100) * width)
        if fill_width > 0:
            # Create gradient surface
            gradient_surface = pygame.Surface((fill_width, height), pygame.SRCALPHA)

            for i in range(fill_width):
                factor = i / max(fill_width - 1, 1)
                col = self._interpolate_color(color_start, color_end, factor)
                pygame.draw.line(gradient_surface, col, (i, 0), (i, height))

            # Apply rounded corners by masking
            mask_surface = pygame.Surface((fill_width, height), pygame.SRCALPHA)
            pygame.draw.rect(
                mask_surface,
                (255, 255, 255, 255),
                (0, 0, fill_width, height),
                border_radius=border_radius,
            )

            # Combine
            final_surface = pygame.Surface((fill_width, height), pygame.SRCALPHA)
            final_surface.blit(gradient_surface, (0, 0))
            final_surface.blit(
                mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN
            )

            surface.blit(final_surface, (x, y))

    def draw_pixel_border(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a chunky pixelated border"""
        x, y, w, h = rect
        # Thick chunky border
        pygame.draw.rect(surface, color, (x, y, w, h), 3)
        # Corner blocks for that 8-bit feel
        block = 6
        for corner in [
            (x, y),
            (x + w - block, y),
            (x, y + h - block),
            (x + w - block, y + h - block),
        ]:
            pygame.draw.rect(surface, color, (*corner, block, block))

    def draw_dashed_border(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a dashed/dotted border - ocean wave feel"""
        x, y, w, h = rect
        dash_len = 8
        gap_len = 4

        # Top and bottom
        for start_x in range(x, x + w, dash_len + gap_len):
            end_x = min(start_x + dash_len, x + w)
            pygame.draw.line(surface, color, (start_x, y), (end_x, y), 2)
            pygame.draw.line(
                surface, color, (start_x, y + h - 1), (end_x, y + h - 1), 2
            )

        # Left and right
        for start_y in range(y, y + h, dash_len + gap_len):
            end_y = min(start_y + dash_len, y + h)
            pygame.draw.line(surface, color, (x, start_y), (x, end_y), 2)
            pygame.draw.line(
                surface, color, (x + w - 1, start_y), (x + w - 1, end_y), 2
            )

    def draw_double_border(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a double-line border - cyberpunk tech feel"""
        x, y, w, h = rect
        # Outer border
        pygame.draw.rect(surface, color, (x, y, w, h), 2)
        # Inner border with gap
        gap = 4
        pygame.draw.rect(
            surface, color, (x + gap, y + gap, w - gap * 2, h - gap * 2), 1
        )

    def draw_thick_border(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a thick solid border - bold warm feel"""
        x, y, w, h = rect
        # Extra thick border
        pygame.draw.rect(surface, color, (x, y, w, h), 5)

    def draw_terminal_border(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a terminal-style border with corner markers - matrix feel"""
        x, y, w, h = rect
        # Thin main border
        pygame.draw.rect(surface, color, (x, y, w, h), 1)
        # Corner brackets
        bracket_len = 8
        # Top-left
        pygame.draw.line(surface, color, (x, y), (x + bracket_len, y), 2)
        pygame.draw.line(surface, color, (x, y), (x, y + bracket_len), 2)
        # Top-right
        pygame.draw.line(surface, color, (x + w - bracket_len, y), (x + w, y), 2)
        pygame.draw.line(
            surface, color, (x + w - 1, y), (x + w - 1, y + bracket_len), 2
        )
        # Bottom-left
        pygame.draw.line(
            surface, color, (x, y + h - 1), (x + bracket_len, y + h - 1), 2
        )
        pygame.draw.line(surface, color, (x, y + h - bracket_len), (x, y + h), 2)
        # Bottom-right
        pygame.draw.line(
            surface, color, (x + w - bracket_len, y + h - 1), (x + w, y + h - 1), 2
        )
        pygame.draw.line(
            surface, color, (x + w - 1, y + h - bracket_len), (x + w - 1, y + h), 2
        )

    def draw_inverted_border(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
    ) -> None:
        """Draw an inverted/inset border - ominous 666 feel"""
        x, y, w, h = rect
        # Dark outer edge (shadow)
        dark = (max(0, color[0] // 3), max(0, color[1] // 3), max(0, color[2] // 3))
        pygame.draw.line(surface, dark, (x, y), (x + w, y), 3)  # Top
        pygame.draw.line(surface, dark, (x, y), (x, y + h), 3)  # Left
        # Bright inner edge (highlight)
        pygame.draw.line(
            surface, color, (x, y + h - 1), (x + w, y + h - 1), 2
        )  # Bottom
        pygame.draw.line(surface, color, (x + w - 1, y), (x + w - 1, y + h), 2)  # Right

    def draw_chunky_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a segmented pixel-art progress bar"""
        if bg_color is None:
            bg_color = colors.DARK_GRAY()

        # Chunky segments - calculate how many fit
        segment_width = 6
        segment_gap = 2
        total_segment_size = segment_width + segment_gap
        num_segments = width // total_segment_size

        # Actual width used by segments (last segment has no gap after it)
        actual_width = num_segments * segment_width + (num_segments - 1) * segment_gap

        # Background matches actual segment area
        pygame.draw.rect(surface, bg_color, (x, y, actual_width, height))

        filled_segments = int((percent / 100) * num_segments)
        # Show at least 1 segment if percent > 0
        if percent > 0 and filled_segments == 0:
            filled_segments = 1

        for i in range(num_segments):
            seg_x = x + i * total_segment_size
            if i < filled_segments:
                pygame.draw.rect(
                    surface, color, (seg_x, y + 2, segment_width, height - 4)
                )
            else:
                pygame.draw.rect(
                    surface,
                    colors.DARKER_GRAY(),
                    (seg_x, y + 2, segment_width, height - 4),
                )

    def draw_dashed_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a bar with dashed fill - ocean wave feel"""
        if bg_color is None:
            bg_color = colors.DARK_GRAY()

        # Background
        pygame.draw.rect(surface, bg_color, (x, y, width, height))

        # Filled portion with horizontal dashes
        fill_width = int((percent / 100) * width)
        if fill_width > 0:
            dash_height = 2
            gap = 3
            for dy in range(0, height, dash_height + gap):
                if dy + dash_height <= height:
                    pygame.draw.rect(
                        surface, color, (x, y + dy, fill_width, dash_height)
                    )

    def draw_double_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a bar with outline style - cyberpunk tech feel"""
        if bg_color is None:
            bg_color = colors.DARK_GRAY()

        # Background
        pygame.draw.rect(surface, bg_color, (x, y, width, height))

        # Filled portion - outline only
        fill_width = int((percent / 100) * width)
        if fill_width > 4:
            pygame.draw.rect(surface, color, (x, y, fill_width, height), 2)
            # Inner fill slightly dimmer
            inner_color = (color[0] // 2, color[1] // 2, color[2] // 2)
            pygame.draw.rect(
                surface, inner_color, (x + 3, y + 3, fill_width - 6, height - 6)
            )

    def draw_thick_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a solid thick bar - bold warm feel"""
        if bg_color is None:
            bg_color = colors.DARK_GRAY()

        # Background
        pygame.draw.rect(surface, bg_color, (x, y, width, height))

        # Solid fill
        fill_width = int((percent / 100) * width)
        if fill_width > 0:
            pygame.draw.rect(surface, color, (x, y, fill_width, height))
            # Bright edge on top
            bright = (
                min(255, color[0] + 50),
                min(255, color[1] + 50),
                min(255, color[2] + 50),
            )
            pygame.draw.line(surface, bright, (x, y), (x + fill_width, y), 2)

    def draw_terminal_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a bar with scanline effect - matrix terminal feel"""
        if bg_color is None:
            bg_color = colors.DARK_GRAY()

        # Background
        pygame.draw.rect(surface, bg_color, (x, y, width, height))

        # Filled portion
        fill_width = int((percent / 100) * width)
        if fill_width > 0:
            pygame.draw.rect(surface, color, (x, y, fill_width, height))
            # Scanlines over the fill
            for sy in range(y, y + height, 2):
                dark = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.line(surface, dark, (x, sy), (x + fill_width, sy), 1)

    def draw_inverted_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a hollow/inverted bar - ominous 666 feel"""
        if bg_color is None:
            bg_color = colors.DARK_GRAY()

        # Background
        pygame.draw.rect(surface, bg_color, (x, y, width, height))

        # Filled portion - hollow with bright outline
        fill_width = int((percent / 100) * width)
        if fill_width > 0:
            # Dark fill
            dark = (color[0] // 4, color[1] // 4, color[2] // 4)
            pygame.draw.rect(surface, dark, (x, y, fill_width, height))
            # Bright outline
            pygame.draw.rect(surface, color, (x, y, fill_width, height), 2)

    def draw_box(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        value: str,
        border_color: tuple[int, int, int],
        value_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a labeled box with a value"""
        if value_color is None:
            value_color = colors.WHITE()

        rect = pygame.Rect(x, y, width, height)
        self.draw_pixel_border(surface, rect, border_color)

        # Label at top
        label_text = self.font.small.render(label, True, border_color)
        label_x = x + (width - label_text.get_width()) // 2
        surface.blit(label_text, (label_x, y + 8))

        # Value centered
        value_text = self.font.large.render(value, True, value_color)
        value_x = x + (width - value_text.get_width()) // 2
        value_y = y + (height - value_text.get_height()) // 2 + 5
        surface.blit(value_text, (value_x, value_y))

    def draw_scanlines(self, surface: pygame.Surface, alpha: int = 60) -> None:
        """Draw CRT-style scanlines effect"""
        scanline_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for y in range(0, surface.get_height(), 3):
            pygame.draw.line(
                scanline_surface, (0, 0, 0, alpha), (0, y), (surface.get_width(), y)
            )
        surface.blit(scanline_surface, (0, 0))

    def draw_screen_indicators(
        self,
        surface: pygame.Surface,
        current: int,
        total: int,
        y: int = 310,
    ) -> None:
        """Draw screen position indicators"""
        indicator_width = 8
        indicator_spacing = 12
        total_width = total * indicator_spacing - (indicator_spacing - indicator_width)
        start_x = (surface.get_width() - total_width) // 2

        for i in range(total):
            color = colors.WHITE() if i == current else colors.DARK_GRAY()
            pygame.draw.rect(
                surface,
                color,
                (start_x + i * indicator_spacing, y, indicator_width, indicator_width),
            )
