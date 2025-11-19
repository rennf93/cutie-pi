"""System information screen"""

import shutil
from datetime import datetime
import pygame
from .base import BaseScreen
from ui import colors
from ui.fonts import PixelFont
from ui.components import UIComponents
from utils.system_info import SystemInfo


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
        end_color = (
            min(255, color[0] + 50),
            min(255, color[1] + 50),
            min(255, color[2] + 50)
        )
        ui.draw_gradient_bar(surface, x, y, width, height, percent, color, end_color)
    else:
        ui.draw_chunky_bar(surface, x, y, width, height, percent, color)


class SystemScreen(BaseScreen):
    """System information display"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        super().__init__(font, ui)
        self.system_info = SystemInfo()

    def update(self, data: dict) -> None:
        """Update system information"""
        self.system_info.update()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the system screen"""
        surface.fill(colors.BLACK())
        info = self.system_info

        # Title with hostname
        title = self.font.medium.render(info.hostname.upper(), True, colors.CYAN())
        surface.blit(title, (10, 10))

        # IP address below hostname
        ip_text = self.font.tiny.render(info.ip_address, True, colors.GRAY())
        surface.blit(ip_text, (10, 30))

        # Date and time (right side)
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%a %d %b")

        time_text = self.font.large.render(time_str, True, colors.WHITE())
        surface.blit(time_text, (380, 10))
        date_text = self.font.tiny.render(date_str, True, colors.GRAY())
        surface.blit(date_text, (380, 32))

        y = 55

        # Disk usage - full width bar at top
        text = self.font.small.render("DISK", True, colors.GRAY())
        surface.blit(text, (15, y + 5))
        try:
            total, used, free = shutil.disk_usage("/")
            disk_percent = (used / total) * 100
            disk_text = f"{used // (1024**3)}G/{total // (1024**3)}G"
        except Exception:
            disk_percent = 0
            disk_text = "N/A"
        _draw_bar(self.ui, surface, 60, y, 336, 22, disk_percent, colors.GRAY())
        disk_info = self.font.small.render(disk_text, True, colors.WHITE())
        surface.blit(disk_info, (405, y + 5))

        y = 95

        # Temperature box
        _draw_border(self.ui, surface, pygame.Rect(15, y, 220, 50), colors.ORANGE())
        text = self.font.small.render("TEMP", True, colors.ORANGE())
        surface.blit(text, (25, y + 17))
        temp_color = colors.GREEN() if info.temp < 60 else colors.ORANGE() if info.temp < 75 else colors.RED()
        temp_text = self.font.large.render(f"{info.temp:.0f}C", True, temp_color)
        surface.blit(temp_text, (110, y + 14))

        # Memory box
        _draw_border(self.ui, surface, pygame.Rect(250, y, 220, 50), colors.CYAN())
        text = self.font.small.render("MEM", True, colors.CYAN())
        surface.blit(text, (260, y + 17))
        mem_text = self.font.large.render(f"{info.mem_used:.0f}/{info.mem_total:.0f}", True, colors.WHITE())
        surface.blit(mem_text, (310, y + 14))

        # Middle row - Uptime and Fan
        y = 160

        # Uptime box
        _draw_border(self.ui, surface, pygame.Rect(15, y, 220, 50), colors.GREEN())
        text = self.font.small.render("UP", True, colors.GREEN())
        surface.blit(text, (25, y + 17))
        uptime_text = self.font.large.render(info.uptime if info.uptime else "...", True, colors.WHITE())
        surface.blit(uptime_text, (90, y + 14))

        # Fan box
        _draw_border(self.ui, surface, pygame.Rect(250, y, 220, 50), colors.YELLOW())
        text = self.font.small.render("FAN", True, colors.YELLOW())
        surface.blit(text, (260, y + 17))
        fan_percent = int((info.fan_speed / 255) * 100)
        fan_text = self.font.large.render(
            f"{fan_percent}%", True, colors.WHITE() if fan_percent > 0 else colors.GRAY()
        )
        surface.blit(fan_text, (340, y + 14))

        # Bottom row - CPU and RAM tall bars with vertical labels
        y = 225
        bar_height = 60

        # CPU - vertical label close to bar
        text = self.font.small.render("C", True, colors.GREEN())
        surface.blit(text, (15, y + 8))
        text = self.font.small.render("P", True, colors.GREEN())
        surface.blit(text, (15, y + 23))
        text = self.font.small.render("U", True, colors.GREEN())
        surface.blit(text, (15, y + 38))
        cpu_color = colors.GREEN() if info.cpu_percent < 70 else colors.ORANGE() if info.cpu_percent < 90 else colors.RED()
        _draw_bar(self.ui, surface, 30, y, 200, bar_height, info.cpu_percent, cpu_color)
        percent_text = self.font.medium.render(f"{info.cpu_percent:.0f}%", True, colors.WHITE())
        surface.blit(percent_text, (100, y + 22))

        # RAM - vertical label close to bar
        text = self.font.small.render("R", True, colors.PURPLE())
        surface.blit(text, (250, y + 8))
        text = self.font.small.render("A", True, colors.PURPLE())
        surface.blit(text, (250, y + 23))
        text = self.font.small.render("M", True, colors.PURPLE())
        surface.blit(text, (250, y + 38))
        ram_color = colors.PURPLE() if info.mem_percent < 70 else colors.ORANGE() if info.mem_percent < 90 else colors.RED()
        _draw_bar(self.ui, surface, 265, y, 200, bar_height, info.mem_percent, ram_color)
        percent_text = self.font.medium.render(f"{info.mem_percent:.0f}%", True, colors.WHITE())
        surface.blit(percent_text, (335, y + 22))
