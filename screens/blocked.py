"""Top blocked domains screen"""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH, Layout
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
        surface.blit(title, (Layout.title_x, Layout.title_y))

        if not self.blocked_domains:
            text = self.font.medium.render("No data", True, colors.GRAY())
            surface.blit(text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2))
            return

        y = Layout.row_start_y
        row_height = Layout.row_height_sm
        max_count = max(self.blocked_domains.values()) if self.blocked_domains else 1

        for i, (domain, count) in enumerate(list(self.blocked_domains.items())[:9]):
            # Truncate long domains - responsive to screen width
            if len(domain) > Layout.max_domain_chars:
                domain = domain[: Layout.max_domain_chars - 3] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(
                    surface,
                    (20, 20, 20),
                    (Layout.margin_sm, y, SCREEN_WIDTH - Layout.margin_sm * 2, row_height),
                    border_radius=_get_radius(),
                )

            # Rank
            rank_text = self.font.small.render(f"{i + 1}.", True, colors.YELLOW())
            surface.blit(rank_text, (Layout.rank_x, y + Layout.row_padding))

            # Domain
            domain_text = self.font.small.render(domain, True, colors.WHITE())
            surface.blit(domain_text, (Layout.content_x, y + Layout.row_padding))

            # Count text - right aligned before bar
            count_text = self.font.small.render(str(count), True, colors.WHITE())
            surface.blit(count_text, (Layout.count_x, y + Layout.row_padding))

            # Count bar - right side
            bar_width = int((count / max_count) * Layout.bar_max_width)
            pygame.draw.rect(
                surface,
                colors.RED(),
                (Layout.bar_x, y + Layout.row_padding, bar_width, Layout.bar_height_sm),
                border_radius=_get_radius(),
            )

            y += row_height
