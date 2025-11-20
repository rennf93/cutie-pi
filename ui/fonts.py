"""Pixel art font management"""

import os

import pygame

from utils.logger import logger


class PixelFont:
    """Pixel art font renderer using Press Start 2P"""

    def __init__(self) -> None:
        pygame.font.init()
        pixel_font = os.path.expanduser("~/.fonts/PressStart2P.ttf")
        fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

        try:
            if os.path.exists(pixel_font):
                self.large = pygame.font.Font(pixel_font, 16)
                self.medium = pygame.font.Font(pixel_font, 12)
                self.small = pygame.font.Font(pixel_font, 8)
                self.tiny = pygame.font.Font(pixel_font, 6)
            else:
                logger.warning(f"Pixel font not found at {pixel_font}, using fallback")
                self.large = pygame.font.Font(fallback, 18)
                self.medium = pygame.font.Font(fallback, 14)
                self.small = pygame.font.Font(fallback, 10)
                self.tiny = pygame.font.Font(fallback, 8)
        except Exception as e:
            logger.error(f"Error loading fonts: {e}")
            self.large = pygame.font.SysFont("monospace", 18, bold=True)
            self.medium = pygame.font.SysFont("monospace", 14, bold=True)
            self.small = pygame.font.SysFont("monospace", 10, bold=True)
            self.tiny = pygame.font.SysFont("monospace", 8, bold=True)
