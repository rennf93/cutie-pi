"""Pi-hole statistics screen"""

import math
import subprocess

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH, Layout
from ui import colors
from ui.components import UIComponents
from ui.fonts import PixelFont

from .base import BaseScreen


def _draw_border(
    ui: UIComponents,
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: tuple[int, int, int],
) -> None:
    """Draw border based on theme style"""
    style = colors.get_style()
    if style == "glow":
        glow_color = colors.GLOW_PRIMARY()
        ui.draw_glow_border(surface, rect, color, glow_color)
    elif style == "dashed":
        ui.draw_dashed_border(surface, rect, color)
    elif style == "double":
        ui.draw_double_border(surface, rect, color)
    elif style == "thick":
        ui.draw_thick_border(surface, rect, color)
    elif style == "terminal":
        ui.draw_terminal_border(surface, rect, color)
    elif style == "inverted":
        ui.draw_inverted_border(surface, rect, color)
    else:  # pixel (default)
        ui.draw_pixel_border(surface, rect, color)


def _draw_bar(
    ui: UIComponents,
    surface: pygame.Surface,
    x: int,
    y: int,
    width: int,
    height: int,
    percent: float,
    color: tuple[int, int, int],
) -> None:
    """Draw bar based on theme style"""
    style = colors.get_style()
    if style == "glow":
        # Gradient from color to slightly different shade
        end_color = (
            min(255, color[0] + 50),
            min(255, color[1] + 50),
            min(255, color[2] + 50),
        )
        ui.draw_gradient_bar(surface, x, y, width, height, percent, color, end_color)
    elif style == "dashed":
        ui.draw_dashed_bar(surface, x, y, width, height, percent, color)
    elif style == "double":
        ui.draw_double_bar(surface, x, y, width, height, percent, color)
    elif style == "thick":
        ui.draw_thick_bar(surface, x, y, width, height, percent, color)
    elif style == "terminal":
        ui.draw_terminal_bar(surface, x, y, width, height, percent, color)
    elif style == "inverted":
        ui.draw_inverted_bar(surface, x, y, width, height, percent, color)
    else:  # pixel (default)
        ui.draw_chunky_bar(surface, x, y, width, height, percent, color)


class StatsScreen(BaseScreen):
    """Main Pi-hole statistics display with animated counters"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        super().__init__(font, ui)
        self.animation_offset = 0
        self.displayed_queries = 0.0
        self.displayed_blocked = 0.0
        self.total_queries = 0
        self.blocked = 0
        self.percent_blocked = 0.0
        self.clients = 0
        self.domains_blocked = 0
        self.status = "enabled"

    def update(self, data: dict) -> None:
        """Update with Pi-hole summary data"""
        self.total_queries = data.get("dns_queries_today", 0)
        self.blocked = data.get("ads_blocked_today", 0)
        self.percent_blocked = data.get("ads_percentage_today", 0)
        self.clients = data.get("unique_clients", 0)
        self.domains_blocked = data.get("domains_being_blocked", 0)
        self.status = data.get("status", "enabled")

        # Smooth counter animation
        self.displayed_queries += (self.total_queries - self.displayed_queries) * 0.1
        self.displayed_blocked += (self.blocked - self.displayed_blocked) * 0.1
        self.animation_offset = (self.animation_offset + 1) % 360

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the stats screen"""
        surface.fill(colors.BLACK())

        # Use Layout system for responsive dimensions
        margin = Layout.box_margin
        box_width = Layout.box_width
        right_x = Layout.box_right_x
        bar_width = int(SCREEN_WIDTH * 0.77)  # Bar width for block rate
        percent_x = margin + bar_width + Layout.margin_sm

        # Vertical spacing based on screen height
        title_y = int(SCREEN_HEIGHT * 0.03)
        row1_y = int(SCREEN_HEIGHT * 0.125)
        row1_box_h = int(SCREEN_HEIGHT * 0.20)
        row2_y = int(SCREEN_HEIGHT * 0.375)
        bar_height = int(SCREEN_HEIGHT * 0.078)
        row3_y = int(SCREEN_HEIGHT * 0.547)
        row3_box_h = int(SCREEN_HEIGHT * 0.172)
        row4_y = int(SCREEN_HEIGHT * 0.766)
        row4_box_h = int(SCREEN_HEIGHT * 0.156)

        # Text offsets within boxes
        label_offset_y = Layout.padding_sm
        value_offset_y = Layout.box_text_offset

        # Title
        title = self.font.medium.render("PI-HOLE", True, colors.GREEN())
        surface.blit(title, (margin, title_y))

        # Total Queries box
        _draw_border(self.ui, surface, pygame.Rect(margin, row1_y, box_width, row1_box_h), colors.GREEN())
        text = self.font.small.render("QUERIES", True, colors.GREEN())
        surface.blit(text, (margin + Layout.box_padding_x, row1_y + label_offset_y))
        num = self.font.large.render(
            f"{int(self.displayed_queries)}", True, colors.WHITE()
        )
        surface.blit(num, (margin + Layout.box_padding_x, row1_y + value_offset_y))

        # Blocked box
        _draw_border(self.ui, surface, pygame.Rect(right_x, row1_y, box_width, row1_box_h), colors.RED())
        text = self.font.small.render("BLOCKED", True, colors.RED())
        surface.blit(text, (right_x + Layout.box_padding_x, row1_y + label_offset_y))
        num = self.font.large.render(
            f"{int(self.displayed_blocked)}", True, colors.WHITE()
        )
        surface.blit(num, (right_x + Layout.box_padding_x, row1_y + value_offset_y))

        # Block percentage with bar
        text = self.font.small.render("BLOCK RATE", True, colors.CYAN())
        surface.blit(text, (margin, row2_y))
        _draw_bar(
            self.ui, surface, margin, row2_y + Layout.padding_lg, bar_width, bar_height, self.percent_blocked, colors.CYAN()
        )
        percent_text = self.font.medium.render(
            f"{self.percent_blocked:.1f}%", True, colors.WHITE()
        )
        surface.blit(percent_text, (percent_x, row2_y + Layout.padding_lg))

        # Clients box
        _draw_border(self.ui, surface, pygame.Rect(margin, row3_y, box_width, row3_box_h), colors.YELLOW())
        text = self.font.small.render("CLIENTS", True, colors.YELLOW())
        surface.blit(text, (margin + Layout.box_padding_x, row3_y + label_offset_y))
        num = self.font.medium.render(f"{self.clients}", True, colors.WHITE())
        surface.blit(num, (margin + Layout.box_padding_x, row3_y + value_offset_y))

        # Blocklist box
        _draw_border(self.ui, surface, pygame.Rect(right_x, row3_y, box_width, row3_box_h), colors.PURPLE())
        text = self.font.small.render("BLOCKLIST", True, colors.PURPLE())
        surface.blit(text, (right_x + Layout.box_padding_x, row3_y + label_offset_y))
        domains_str = self._format_number(self.domains_blocked)
        num = self.font.medium.render(domains_str, True, colors.WHITE())
        surface.blit(num, (right_x + Layout.box_padding_x, row3_y + value_offset_y))

        # Status box
        status_color = colors.GREEN() if self.status == "enabled" else colors.RED()
        _draw_border(self.ui, surface, pygame.Rect(margin, row4_y, box_width, row4_box_h), status_color)
        text = self.font.small.render("STATUS", True, status_color)
        surface.blit(text, (margin + Layout.box_padding_x, row4_y + label_offset_y))
        # Pulsing dot + status text
        pulse = abs(math.sin(self.animation_offset * 0.1)) * 3
        dot_size = max(6, int(8 * Layout.scale_min))
        pygame.draw.rect(
            surface, status_color, (margin + Layout.box_padding_x, row4_y + value_offset_y, int(dot_size + pulse), int(dot_size + pulse))
        )
        status_text = self.font.medium.render(self.status.upper(), True, colors.WHITE())
        surface.blit(status_text, (margin + Layout.box_padding_x + dot_size + Layout.margin_md, row4_y + value_offset_y - 3))

        # DNS box
        _draw_border(self.ui, surface, pygame.Rect(right_x, row4_y, box_width, row4_box_h), colors.CYAN())
        text = self.font.small.render("DNS", True, colors.CYAN())
        surface.blit(text, (right_x + Layout.box_padding_x, row4_y + label_offset_y))
        # Get IP dynamically
        try:
            result = subprocess.run(
                ["hostname", "-I"], capture_output=True, text=True, timeout=1
            )
            ip = result.stdout.strip().split()[0] if result.stdout.strip() else "N/A"
        except Exception:
            ip = "N/A"
        dns_text = self.font.medium.render(ip, True, colors.WHITE())
        surface.blit(dns_text, (right_x + Layout.box_padding_x, row4_y + value_offset_y - 3))

    def _format_number(self, num: int) -> str:
        """Format large numbers with K/M suffix"""
        if num >= 1000000:
            return f"{num / 1000000:.1f}M"
        elif num >= 1000:
            return f"{num / 1000:.0f}K"
        return str(num)
