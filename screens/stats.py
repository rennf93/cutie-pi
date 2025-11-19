"""Pi-hole statistics screen"""

import math
import subprocess
import pygame
from .base import BaseScreen
from ui import colors
from ui.fonts import PixelFont
from ui.components import UIComponents


def _draw_border(ui, surface, rect, color):
    """Draw border - glow or pixel based on theme"""
    if colors.use_glow():
        glow_color = colors.GLOW_PRIMARY()
        ui.draw_glow_border(surface, rect, color, glow_color)
    else:
        ui.draw_pixel_border(surface, rect, color)


def _draw_bar(ui, surface, x, y, width, height, percent, color):
    """Draw bar - gradient or chunky based on theme"""
    if colors.use_glow():
        # Gradient from color to slightly different shade
        end_color = (
            min(255, color[0] + 50),
            min(255, color[1] + 50),
            min(255, color[2] + 50)
        )
        ui.draw_gradient_bar(surface, x, y, width, height, percent, color, end_color)
    else:
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

        # Title
        title = self.font.medium.render("PI-HOLE", True, colors.GREEN())
        surface.blit(title, (10, 10))

        y = 40

        # Total Queries box
        _draw_border(self.ui, surface, pygame.Rect(15, y, 220, 65), colors.GREEN())
        text = self.font.small.render("QUERIES", True, colors.GREEN())
        surface.blit(text, (25, y + 8))
        num = self.font.large.render(f"{int(self.displayed_queries)}", True, colors.WHITE())
        surface.blit(num, (25, y + 30))

        # Blocked box
        _draw_border(self.ui, surface, pygame.Rect(250, y, 220, 65), colors.RED())
        text = self.font.small.render("BLOCKED", True, colors.RED())
        surface.blit(text, (260, y + 8))
        num = self.font.large.render(f"{int(self.displayed_blocked)}", True, colors.WHITE())
        surface.blit(num, (260, y + 30))

        y = 120

        # Block percentage with bar
        text = self.font.small.render("BLOCK RATE", True, colors.CYAN())
        surface.blit(text, (15, y))
        _draw_bar(self.ui, surface, 15, y + 18, 370, 25, self.percent_blocked, colors.CYAN())
        percent_text = self.font.medium.render(f"{self.percent_blocked:.1f}%", True, colors.WHITE())
        surface.blit(percent_text, (395, y + 18))

        y = 175

        # Clients box
        _draw_border(self.ui, surface, pygame.Rect(15, y, 220, 55), colors.YELLOW())
        text = self.font.small.render("CLIENTS", True, colors.YELLOW())
        surface.blit(text, (25, y + 8))
        num = self.font.medium.render(f"{self.clients}", True, colors.WHITE())
        surface.blit(num, (25, y + 28))

        # Blocklist box
        _draw_border(self.ui, surface, pygame.Rect(250, y, 220, 55), colors.PURPLE())
        text = self.font.small.render("BLOCKLIST", True, colors.PURPLE())
        surface.blit(text, (260, y + 8))
        domains_str = self._format_number(self.domains_blocked)
        num = self.font.medium.render(domains_str, True, colors.WHITE())
        surface.blit(num, (260, y + 28))

        y = 245

        # Status box
        status_color = colors.GREEN() if self.status == "enabled" else colors.RED()
        _draw_border(self.ui, surface, pygame.Rect(15, y, 220, 50), status_color)
        text = self.font.small.render("STATUS", True, status_color)
        surface.blit(text, (25, y + 8))
        # Pulsing dot + status text
        pulse = abs(math.sin(self.animation_offset * 0.1)) * 3
        pygame.draw.rect(surface, status_color, (25, y + 28, int(8 + pulse), int(8 + pulse)))
        status_text = self.font.medium.render(self.status.upper(), True, colors.WHITE())
        surface.blit(status_text, (45, y + 25))

        # DNS box
        _draw_border(self.ui, surface, pygame.Rect(250, y, 220, 50), colors.CYAN())
        text = self.font.small.render("DNS", True, colors.CYAN())
        surface.blit(text, (260, y + 8))
        # Get IP dynamically
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=1)
            ip = result.stdout.strip().split()[0] if result.stdout.strip() else "N/A"
        except Exception:
            ip = "N/A"
        dns_text = self.font.medium.render(ip, True, colors.WHITE())
        surface.blit(dns_text, (260, y + 25))

    def _format_number(self, num: int) -> str:
        """Format large numbers with K/M suffix"""
        if num >= 1000000:
            return f"{num / 1000000:.1f}M"
        elif num >= 1000:
            return f"{num / 1000:.0f}K"
        return str(num)
