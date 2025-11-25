"""Top blocked domains screen"""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from ui import colors
from ui.components import UIComponents
from ui.fonts import PixelFont

from .base import BaseScreen


def _get_radius() -> int:
    """Get border radius based on theme"""
    return 4 if colors.get_style() == "glow" else 0


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
            surface.blit(text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2))
            return

        y = int(SCREEN_HEIGHT * 0.125)
        row_height = int(SCREEN_HEIGHT * 0.0875)
        max_count = max(self.blocked_domains.values()) if self.blocked_domains else 1

        # Responsive positioning
        count_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.25)
        bar_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.15)
        max_bar_width = int(SCREEN_WIDTH * 0.125)
        # Calculate max domain length based on available space
        max_domain_chars = max(10, int(SCREEN_WIDTH / 10) - 5)
        text_v_offset = int(row_height * 0.29)
        bar_height = int(row_height * 0.43)

        for i, (domain, count) in enumerate(list(self.blocked_domains.items())[:9]):
            # Truncate long domains - responsive to screen width
            if len(domain) > max_domain_chars:
                domain = domain[:max_domain_chars - 3] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(
                    surface,
                    (20, 20, 20),
                    (10, y, SCREEN_WIDTH - 20, row_height),
                    border_radius=_get_radius(),
                )

            # Rank
            rank_text = self.font.small.render(f"{i + 1}.", True, colors.YELLOW())
            surface.blit(rank_text, (15, y + text_v_offset))

            # Domain
            domain_text = self.font.small.render(domain, True, colors.WHITE())
            surface.blit(domain_text, (50, y + text_v_offset))

            # Count text - right aligned before bar
            count_text = self.font.small.render(str(count), True, colors.WHITE())
            surface.blit(count_text, (count_x, y + text_v_offset))

            # Count bar - right side
            bar_width = int((count / max_count) * max_bar_width)
            pygame.draw.rect(
                surface,
                colors.RED(),
                (bar_x, y + text_v_offset, bar_width, bar_height),
                border_radius=_get_radius(),
            )

            y += row_height
