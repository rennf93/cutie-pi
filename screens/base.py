"""Base screen class for all dashboard screens"""

from abc import ABC, abstractmethod
import pygame
from ui.fonts import PixelFont
from ui.components import UIComponents


class BaseScreen(ABC):
    """Abstract base class for dashboard screens"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        self.font = font
        self.ui = ui

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen content"""
        pass

    @abstractmethod
    def update(self, data: dict) -> None:
        """Update screen with new data"""
        pass
