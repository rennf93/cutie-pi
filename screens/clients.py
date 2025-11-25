"""Top clients screen"""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from ui import colors
from ui.components import UIComponents
from ui.fonts import PixelFont

from .base import BaseScreen


def _get_radius() -> int:
    """Get border radius based on theme"""
    return 4 if colors.get_style() == "glow" else 0


class ClientsScreen(BaseScreen):
    """Top clients display"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        super().__init__(font, ui)
        self.clients: dict[str, int] = {}

    def update(self, data: dict) -> None:
        """Update with top clients data"""
        self.clients = data.get("clients", {})

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the clients screen"""
        surface.fill(colors.BLACK())

        # Title
        title = self.font.medium.render("TOP CLIENTS", True, colors.YELLOW())
        surface.blit(title, (10, 10))

        if not self.clients:
            text = self.font.medium.render("No data", True, colors.GRAY())
            surface.blit(text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2))
            return

        y = int(SCREEN_HEIGHT * 0.125)
        row_height = int(SCREEN_HEIGHT * 0.0875)
        max_count = max(self.clients.values()) if self.clients else 1

        # Responsive positioning
        count_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.25)
        bar_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.15)
        max_bar_width = int(SCREEN_WIDTH * 0.125)
        # Calculate max client name length based on available space
        max_client_chars = max(10, int(SCREEN_WIDTH / 10) - 5)
        text_v_offset = int(row_height * 0.29)
        bar_height = int(row_height * 0.43)

        # Color coding for ranks
        rank_colors = [
            colors.YELLOW(),
            colors.WHITE(),
            colors.WHITE(),
            colors.GRAY(),
            colors.GRAY(),
            colors.GRAY(),
            colors.GRAY(),
            colors.GRAY(),
            colors.GRAY(),
        ]

        for i, (client, count) in enumerate(list(self.clients.items())[:9]):
            # Truncate long names - responsive to screen width
            if len(client) > max_client_chars:
                client = client[:max_client_chars - 3] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(
                    surface,
                    (20, 20, 20),
                    (10, y, SCREEN_WIDTH - 20, row_height),
                    border_radius=_get_radius(),
                )

            # Rank with color coding
            rank_text = self.font.small.render(f"{i + 1}.", True, rank_colors[i])
            surface.blit(rank_text, (15, y + text_v_offset))

            # Client name/IP
            client_text = self.font.small.render(client, True, colors.CYAN())
            surface.blit(client_text, (50, y + text_v_offset))

            # Count text - right aligned before bar
            count_text = self.font.small.render(str(count), True, colors.WHITE())
            surface.blit(count_text, (count_x, y + text_v_offset))

            # Query count bar - right side
            bar_width = int((count / max_count) * max_bar_width)
            pygame.draw.rect(
                surface,
                colors.GREEN(),
                (bar_x, y + text_v_offset, bar_width, bar_height),
                border_radius=_get_radius(),
            )

            y += row_height
