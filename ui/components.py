"""Reusable UI components for the dashboard"""

import pygame
from . import colors
from .fonts import PixelFont


class UIComponents:
    """Collection of reusable UI drawing functions"""

    def __init__(self, font: PixelFont) -> None:
        self.font = font

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
        for corner in [(x, y), (x + w - block, y), (x, y + h - block), (x + w - block, y + h - block)]:
            pygame.draw.rect(surface, color, (*corner, block, block))

    def draw_chunky_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] = None,
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
                pygame.draw.rect(surface, color, (seg_x, y + 2, segment_width, height - 4))
            else:
                pygame.draw.rect(surface, colors.DARKER_GRAY(), (seg_x, y + 2, segment_width, height - 4))

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
        value_color: tuple[int, int, int] = None,
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
            pygame.draw.line(scanline_surface, (0, 0, 0, alpha), (0, y), (surface.get_width(), y))
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
