"""System information screen"""

import shutil
from datetime import datetime

import pygame

from ui import colors
from ui.components import UIComponents
from ui.fonts import PixelFont
from utils.system_info import SystemInfo

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


class SystemScreen(BaseScreen):
    """System information display"""

    def __init__(self, font: PixelFont, ui: UIComponents) -> None:
        super().__init__(font, ui)
        self.system_info = SystemInfo()

    def update(self, data: dict) -> None:
        """Update system information"""
        self.system_info.update()

    def _get_threshold_color(
        self, value: float, thresholds: tuple[float, float]
    ) -> tuple[int, int, int]:
        """Get color based on value thresholds (low, high)"""
        low, high = thresholds
        green: tuple[int, int, int] = colors.GREEN()
        orange: tuple[int, int, int] = colors.ORANGE()
        red: tuple[int, int, int] = colors.RED()
        if value < low:
            return green
        elif value < high:
            return orange
        return red

    def _draw_header(self, surface: pygame.Surface) -> None:
        """Draw hostname, IP, date and time"""
        info = self.system_info
        title = self.font.medium.render(info.hostname.upper(), True, colors.CYAN())
        surface.blit(title, (10, 10))

        ip_text = self.font.tiny.render(info.ip_address, True, colors.GRAY())
        surface.blit(ip_text, (10, 30))

        now = datetime.now()
        time_text = self.font.large.render(now.strftime("%H:%M"), True, colors.WHITE())
        surface.blit(time_text, (380, 10))
        date_text = self.font.tiny.render(now.strftime("%a %d %b"), True, colors.GRAY())
        surface.blit(date_text, (380, 32))

    def _draw_disk_bar(self, surface: pygame.Surface, y: int) -> None:
        """Draw disk usage bar"""
        text = self.font.small.render("DISK", True, colors.GRAY())
        surface.blit(text, (15, y + 5))
        try:
            total, used, _ = shutil.disk_usage("/")
            disk_percent = (used / total) * 100
            disk_text = f"{used // (1024**3)}G/{total // (1024**3)}G"
        except Exception:
            disk_percent = 0
            disk_text = "N/A"
        _draw_bar(self.ui, surface, 60, y, 336, 22, disk_percent, colors.GRAY())
        disk_info = self.font.small.render(disk_text, True, colors.WHITE())
        surface.blit(disk_info, (405, y + 5))

    def _draw_info_boxes(self, surface: pygame.Surface) -> None:
        """Draw temp, memory, uptime and fan boxes"""
        info = self.system_info
        y = 95

        # Temperature box
        _draw_border(self.ui, surface, pygame.Rect(15, y, 220, 50), colors.ORANGE())
        text = self.font.small.render("TEMP", True, colors.ORANGE())
        surface.blit(text, (25, y + 17))
        temp_color = self._get_threshold_color(info.temp, (60, 75))
        fahr_temp = (info.temp * 9/5) + 32
        temp_text = self.font.large.render(
            f"{info.temp:.0f}°C/{fahr_temp:.0f}°F", True, temp_color
        )
        center_x = 80 + (140 - temp_text.get_width()) // 2
        surface.blit(temp_text, (center_x, y + 14))

        # Memory box
        _draw_border(self.ui, surface, pygame.Rect(250, y, 220, 50), colors.CYAN())
        text = self.font.small.render("MEM", True, colors.CYAN())
        surface.blit(text, (260, y + 17))
        mem_text = self.font.large.render(
            f"{info.mem_used:.0f}/{info.mem_total:.0f}", True, colors.WHITE()
        )
        surface.blit(mem_text, (310, y + 14))

        y = 160

        # Uptime box
        _draw_border(self.ui, surface, pygame.Rect(15, y, 220, 50), colors.GREEN())
        text = self.font.small.render("UP", True, colors.GREEN())
        surface.blit(text, (25, y + 17))
        uptime_text = self.font.large.render(
            info.uptime if info.uptime else "...", True, colors.WHITE()
        )
        surface.blit(uptime_text, (90, y + 14))

        # Fan box
        _draw_border(self.ui, surface, pygame.Rect(250, y, 220, 50), colors.YELLOW())
        text = self.font.small.render("FAN", True, colors.YELLOW())
        surface.blit(text, (260, y + 17))
        fan_percent = int((info.fan_speed / 255) * 100)
        fan_color = colors.WHITE() if fan_percent > 0 else colors.GRAY()
        fan_text = self.font.large.render(f"{fan_percent}%", True, fan_color)
        surface.blit(fan_text, (340, y + 14))

    def _draw_resource_bars(self, surface: pygame.Surface) -> None:
        """Draw CPU and RAM bars"""
        info = self.system_info
        y = 225
        bar_height = 60

        # CPU
        for i, char in enumerate("CPU"):
            text = self.font.small.render(char, True, colors.GREEN())
            surface.blit(text, (15, y + 8 + i * 15))
        cpu_color = self._get_threshold_color(info.cpu_percent, (70, 90))
        _draw_bar(self.ui, surface, 30, y, 200, bar_height, info.cpu_percent, cpu_color)
        percent_text = self.font.medium.render(
            f"{info.cpu_percent:.0f}%", True, colors.WHITE()
        )
        surface.blit(percent_text, (100, y + 22))

        # RAM
        for i, char in enumerate("RAM"):
            text = self.font.small.render(char, True, colors.PURPLE())
            surface.blit(text, (250, y + 8 + i * 15))
        ram_color = (
            colors.PURPLE()
            if info.mem_percent < 70
            else self._get_threshold_color(info.mem_percent, (70, 90))
        )
        _draw_bar(
            self.ui, surface, 265, y, 200, bar_height, info.mem_percent, ram_color
        )
        percent_text = self.font.medium.render(
            f"{info.mem_percent:.0f}%", True, colors.WHITE()
        )
        surface.blit(percent_text, (335, y + 22))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the system screen"""
        surface.fill(colors.BLACK())
        self._draw_header(surface)
        self._draw_disk_bar(surface, 55)
        self._draw_info_boxes(surface)
        self._draw_resource_bars(surface)
