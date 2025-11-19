"""Top blocked domains screen"""

import pygame
from .base import BaseScreen
from ui import colors
from ui.fonts import PixelFont
from ui.components import UIComponents


def _get_radius():
    """Get border radius based on theme"""
    return 4 if colors.use_glow() else 0


class BlockedScreen(BaseScreen):
    """Top blocked domains display"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        super().__init__(font, ui)
        self.blocked_domains: dict[str, int] = {}

    def update(self, data: dict) -> None:
        """Update with top blocked domains data"""
        self.blocked_domains = data.get("domains", {})

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the blocked domains screen"""
        surface.fill(colors.BLACK())

        # Title
        title = self.font.medium.render("TOP BLOCKED", True, colors.RED())
        surface.blit(title, (10, 10))

        if not self.blocked_domains:
            text = self.font.medium.render("No data", True, colors.GRAY())
            surface.blit(text, (480 // 2 - 40, 320 // 2))
            return

        y = 40
        row_height = 28
        max_count = max(self.blocked_domains.values()) if self.blocked_domains else 1

        for i, (domain, count) in enumerate(list(self.blocked_domains.items())[:9]):
            # Truncate long domains
            if len(domain) > 25:
                domain = domain[:22] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(surface, (20, 20, 20), (10, y, 480 - 20, row_height), border_radius=_get_radius())

            # Rank
            rank_text = self.font.small.render(f"{i + 1}.", True, colors.YELLOW())
            surface.blit(rank_text, (15, y + 8))

            # Domain
            domain_text = self.font.small.render(domain, True, colors.WHITE())
            surface.blit(domain_text, (50, y + 8))

            # Count text - right aligned before bar
            count_text = self.font.small.render(str(count), True, colors.WHITE())
            surface.blit(count_text, (480 - 120, y + 8))

            # Count bar - right side
            bar_width = int((count / max_count) * 60)
            pygame.draw.rect(surface, colors.RED(), (480 - 70, y + 8, bar_width, 12), border_radius=_get_radius())

            y += row_height
