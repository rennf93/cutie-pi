"""Query graph screen"""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH, Layout
from ui import colors
from ui.components import UIComponents
from ui.fonts import PixelFont

from .base import BaseScreen


def _get_bar_radius() -> int:
    """Get border radius for bars based on theme"""
    return 2 if colors.get_style() == "glow" else 0


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
        surface.fill(colors.BLACK())

        # Title
        title = self.font.medium.render("QUERY HISTORY", True, colors.GREEN())
        surface.blit(title, (Layout.title_x, Layout.title_y))

        if not self.history:
            no_data = self.font.small.render("NO DATA", True, colors.GRAY())
            surface.blit(no_data, (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2))
            return

        # Graph area - uses Layout system
        graph_x = Layout.graph_x
        graph_y = Layout.graph_y
        graph_width = Layout.graph_width
        graph_height = Layout.graph_height

        # Draw graph background
        radius = 8 if colors.get_style() == "glow" else 0
        pygame.draw.rect(
            surface,
            colors.DARK_GRAY(),
            (graph_x, graph_y, graph_width, graph_height),
            border_radius=radius,
        )

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
                    colors.GREEN(),
                    (
                        x,
                        graph_y + graph_height - total_height,
                        bar_width - 1,
                        total_height,
                    ),
                )

            # Blocked queries bar (red, overlaid)
            blocked_height = int((blocked / max_val) * graph_height)
            if blocked_height > 0:
                pygame.draw.rect(
                    surface,
                    colors.RED(),
                    (
                        x,
                        graph_y + graph_height - blocked_height,
                        bar_width - 1,
                        blocked_height,
                    ),
                )

        # Y-axis labels
        max_label = self.font.tiny.render(str(max_val), True, colors.WHITE())
        surface.blit(max_label, (graph_x - max_label.get_width() - Layout.margin_xs, graph_y))

        zero_label = self.font.tiny.render("0", True, colors.WHITE())
        surface.blit(
            zero_label,
            (graph_x - zero_label.get_width() - Layout.margin_xs, graph_y + graph_height - Layout.margin_sm),
        )

        # Legend - responsive positioning
        legend_y = Layout.legend_y
        legend_size = Layout.legend_box_size
        pygame.draw.rect(surface, colors.GREEN(), (Layout.margin_sm, legend_y, legend_size, legend_size))
        total_label = self.font.tiny.render("TOTAL", True, colors.WHITE())
        surface.blit(total_label, (Layout.margin_sm + legend_size + Layout.margin_xs, legend_y))

        # Position blocked legend relative to screen width
        blocked_legend_x = Layout.margin_sm + legend_size + Layout.margin_xs + total_label.get_width() + Layout.legend_spacing
        pygame.draw.rect(surface, colors.RED(), (blocked_legend_x, legend_y, legend_size, legend_size))
        blocked_label = self.font.tiny.render("BLOCKED", True, colors.WHITE())
        surface.blit(blocked_label, (blocked_legend_x + legend_size + Layout.margin_xs, legend_y))

        # Time labels
        time_label = self.font.tiny.render("LAST 4 HOURS", True, colors.WHITE())
        surface.blit(time_label, (graph_x + graph_width - time_label.get_width(), legend_y))
