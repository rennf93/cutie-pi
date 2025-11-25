"""Pixel art font management"""

import os

import pygame

from config import Layout
from utils.logger import logger


def _scale_font_size(base_size: int) -> int:
    """Scale font size based on screen dimensions.

    Uses the minimum of x/y scale to ensure text fits both dimensions.
    Ensures minimum readable sizes.
    """
    # Use scale_min to ensure fonts fit in both dimensions
    scaled = int(base_size * Layout.scale_min)
    # Ensure minimum readable sizes
    if base_size >= 14:  # large
        return max(10, scaled)
    elif base_size >= 10:  # medium
        return max(8, scaled)
    elif base_size >= 8:  # small
        return max(6, scaled)
    else:  # tiny
        return max(5, scaled)


class PixelFont:
    """Pixel art font renderer using Press Start 2P"""

    def __init__(self) -> None:
        pygame.font.init()
        pixel_font = os.path.expanduser("~/.fonts/PressStart2P.ttf")
        fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

        # Scale font sizes based on screen dimensions
        # Reference sizes are for 480x320 display
        large_size = _scale_font_size(16)
        medium_size = _scale_font_size(12)
        small_size = _scale_font_size(8)
        tiny_size = _scale_font_size(6)

        # Fallback fonts are slightly larger
        large_fallback = _scale_font_size(18)
        medium_fallback = _scale_font_size(14)
        small_fallback = _scale_font_size(10)
        tiny_fallback = _scale_font_size(8)

        logger.info(
            f"Font sizes (scale={Layout.scale_min:.2f}): "
            f"large={large_size}, medium={medium_size}, small={small_size}, tiny={tiny_size}"
        )

        try:
            if os.path.exists(pixel_font):
                self.large = pygame.font.Font(pixel_font, large_size)
                self.medium = pygame.font.Font(pixel_font, medium_size)
                self.small = pygame.font.Font(pixel_font, small_size)
                self.tiny = pygame.font.Font(pixel_font, tiny_size)
            else:
                logger.warning(f"Pixel font not found at {pixel_font}, using fallback")
                self.large = pygame.font.Font(fallback, large_fallback)
                self.medium = pygame.font.Font(fallback, medium_fallback)
                self.small = pygame.font.Font(fallback, small_fallback)
                self.tiny = pygame.font.Font(fallback, tiny_fallback)
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            self.large = pygame.font.SysFont("monospace", large_fallback, bold=True)
            self.medium = pygame.font.SysFont("monospace", medium_fallback, bold=True)
            self.small = pygame.font.SysFont("monospace", small_fallback, bold=True)
            self.tiny = pygame.font.SysFont("monospace", tiny_fallback, bold=True)
