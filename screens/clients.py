"""Top clients screen"""

import pygame
from .base import BaseScreen
from ui.colors import WHITE, GREEN, YELLOW, CYAN, GRAY, BLACK
from ui.fonts import PixelFont
from ui.components import UIComponents


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
        surface.fill(BLACK)

        # Title
        title = self.font.medium.render("TOP CLIENTS", True, YELLOW)
        surface.blit(title, (10, 10))

        if not self.clients:
            text = self.font.medium.render("No data", True, GRAY)
            surface.blit(text, (480 // 2 - 40, 320 // 2))
            return

        y = 40
        row_height = 28
        max_count = max(self.clients.values()) if self.clients else 1

        # Color coding for ranks
        colors = [YELLOW, WHITE, WHITE, GRAY, GRAY, GRAY, GRAY, GRAY, GRAY]

        for i, (client, count) in enumerate(list(self.clients.items())[:9]):
            # Truncate long names
            if len(client) > 25:
                client = client[:22] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(surface, (20, 20, 20), (10, y, 480 - 20, row_height))

            # Rank with color coding
            rank_text = self.font.small.render(f"{i + 1}.", True, colors[i])
            surface.blit(rank_text, (15, y + 8))

            # Client name/IP
            client_text = self.font.small.render(client, True, CYAN)
            surface.blit(client_text, (50, y + 8))

            # Count text - right aligned before bar
            count_text = self.font.small.render(str(count), True, WHITE)
            surface.blit(count_text, (480 - 120, y + 8))

            # Query count bar - right side
            bar_width = int((count / max_count) * 60)
            pygame.draw.rect(surface, GREEN, (480 - 70, y + 8, bar_width, 12))

            y += row_height
