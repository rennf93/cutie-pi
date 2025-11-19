"""Query graph screen"""

import pygame
from .base import BaseScreen
from ui.colors import WHITE, GREEN, RED, DARK_GRAY, GRAY, BLACK
from ui.fonts import PixelFont
from ui.components import UIComponents


class GraphScreen(BaseScreen):
    """Query overtime graph display"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        super().__init__(font, ui)
        self.history: list[tuple[int, int]] = []  # (total, blocked) pairs

    def update(self, data: dict) -> None:
        """Update with overtime history data"""
        history_data = data.get("history", [])
        self.history = []

        for entry in history_data[-48:]:  # Last 48 entries (4 hours at 5min intervals)
            total = entry.get("total", 0)
            blocked = entry.get("blocked", 0)
            self.history.append((total, blocked))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the graph screen"""
        surface.fill(BLACK)

        # Title
        title = self.font.medium.render("QUERY HISTORY", True, GREEN)
        surface.blit(title, (10, 10))

        if not self.history:
            no_data = self.font.small.render("NO DATA", True, GRAY)
            surface.blit(no_data, (200, 150))
            return

        # Graph area - extends to bottom
        graph_x = 40
        graph_y = 40
        graph_width = 420
        graph_height = 230

        # Draw graph background
        pygame.draw.rect(surface, DARK_GRAY, (graph_x, graph_y, graph_width, graph_height))

        # Find max value for scaling
        max_val = max(max(t, b) for t, b in self.history) if self.history else 1
        if max_val == 0:
            max_val = 1

        # Draw bars
        bar_width = graph_width // len(self.history) if self.history else 1

        for i, (total, blocked) in enumerate(self.history):
            x = graph_x + i * bar_width

            # Total queries bar (green)
            total_height = int((total / max_val) * graph_height)
            if total_height > 0:
                pygame.draw.rect(
                    surface,
                    GREEN,
                    (x, graph_y + graph_height - total_height, bar_width - 1, total_height),
                )

            # Blocked queries bar (red, overlaid)
            blocked_height = int((blocked / max_val) * graph_height)
            if blocked_height > 0:
                pygame.draw.rect(
                    surface,
                    RED,
                    (x, graph_y + graph_height - blocked_height, bar_width - 1, blocked_height),
                )

        # Y-axis labels
        max_label = self.font.tiny.render(str(max_val), True, WHITE)
        surface.blit(max_label, (graph_x - max_label.get_width() - 5, graph_y))

        zero_label = self.font.tiny.render("0", True, WHITE)
        surface.blit(zero_label, (graph_x - zero_label.get_width() - 5, graph_y + graph_height - 10))

        # Legend
        legend_y = 280
        pygame.draw.rect(surface, GREEN, (10, legend_y, 10, 10))
        total_label = self.font.tiny.render("TOTAL", True, WHITE)
        surface.blit(total_label, (25, legend_y))

        pygame.draw.rect(surface, RED, (100, legend_y, 10, 10))
        blocked_label = self.font.tiny.render("BLOCKED", True, WHITE)
        surface.blit(blocked_label, (115, legend_y))

        # Time labels
        time_label = self.font.tiny.render("LAST 4 HOURS", True, WHITE)
        surface.blit(time_label, (graph_x + graph_width - time_label.get_width(), 280))
