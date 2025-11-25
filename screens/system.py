"""System information screen"""

import shutil
from datetime import datetime

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
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
        margin = int(SCREEN_WIDTH * 0.02)
        time_x = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.21)

        info = self.system_info
        title = self.font.medium.render(info.hostname.upper(), True, colors.CYAN())
        surface.blit(title, (margin, 10))

        ip_text = self.font.tiny.render(info.ip_address, True, colors.GRAY())
        surface.blit(ip_text, (margin, 30))

        now = datetime.now()
        time_text = self.font.large.render(now.strftime("%H:%M"), True, colors.WHITE())
        surface.blit(time_text, (time_x, 10))
        date_text = self.font.tiny.render(now.strftime("%a %d %b"), True, colors.GRAY())
        surface.blit(date_text, (time_x, 32))

    def _draw_disk_bar(self, surface: pygame.Surface, y: int) -> None:
        """Draw disk usage bar"""
        margin = int(SCREEN_WIDTH * 0.03)
        label_width = int(SCREEN_WIDTH * 0.09)
        bar_width = int(SCREEN_WIDTH * 0.70)
        info_x = margin + label_width + bar_width + 10

        text = self.font.small.render("DISK", True, colors.GRAY())
        surface.blit(text, (margin, y + 5))
        try:
            total, used, _ = shutil.disk_usage("/")
            disk_percent = (used / total) * 100
            disk_text = f"{used // (1024**3)}G/{total // (1024**3)}G"
        except Exception:
            disk_percent = 0
            disk_text = "N/A"
        bar_height = int(SCREEN_HEIGHT * 0.069)
        _draw_bar(self.ui, surface, margin + label_width, y, bar_width, bar_height, disk_percent, colors.GRAY())
        disk_info = self.font.small.render(disk_text, True, colors.WHITE())
        surface.blit(disk_info, (info_x, y + 5))

    def _draw_info_boxes(self, surface: pygame.Surface) -> None:
        """Draw temp, memory, uptime and fan boxes"""
        info = self.system_info

        # Calculate responsive dimensions
        margin = int(SCREEN_WIDTH * 0.03)
        box_width = int((SCREEN_WIDTH - margin * 3) / 2)
        right_x = margin + box_width + margin
        box_height = int(SCREEN_HEIGHT * 0.156)
        row1_y = int(SCREEN_HEIGHT * 0.297)
        row2_y = int(SCREEN_HEIGHT * 0.5)

        # Temperature box
        _draw_border(self.ui, surface, pygame.Rect(margin, row1_y, box_width, box_height), colors.ORANGE())
        text = self.font.small.render("TEMP", True, colors.ORANGE())
        surface.blit(text, (margin + 10, row1_y + 17))
        temp_color = self._get_threshold_color(info.temp, (60, 75))
        fahr_temp = (info.temp * 9/5) + 32
        temp_text = self.font.large.render(
            f"{info.temp:.0f}°C/{fahr_temp:.0f}°F", True, temp_color
        )
        temp_offset = int(box_width * 0.30)
        center_x = margin + temp_offset + (box_width - temp_offset - temp_text.get_width()) // 2
        surface.blit(temp_text, (center_x, row1_y + 14))

        # Memory box
        _draw_border(self.ui, surface, pygame.Rect(right_x, row1_y, box_width, box_height), colors.CYAN())
        text = self.font.small.render("MEM", True, colors.CYAN())
        surface.blit(text, (right_x + 10, row1_y + 17))
        mem_text = self.font.large.render(
            f"{info.mem_used:.0f}/{info.mem_total:.0f}", True, colors.WHITE()
        )
        surface.blit(mem_text, (right_x + int(box_width * 0.27), row1_y + 14))

        # Uptime box
        _draw_border(self.ui, surface, pygame.Rect(margin, row2_y, box_width, box_height), colors.GREEN())
        text = self.font.small.render("UP", True, colors.GREEN())
        surface.blit(text, (margin + 10, row2_y + 17))
        uptime_text = self.font.large.render(
            info.uptime if info.uptime else "...", True, colors.WHITE()
        )
        surface.blit(uptime_text, (margin + int(box_width * 0.34), row2_y + 14))

        # Fan box
        _draw_border(self.ui, surface, pygame.Rect(right_x, row2_y, box_width, box_height), colors.YELLOW())
        text = self.font.small.render("FAN", True, colors.YELLOW())
        surface.blit(text, (right_x + 10, row2_y + 17))
        fan_percent = int((info.fan_speed / 255) * 100)
        fan_color = colors.WHITE() if fan_percent > 0 else colors.GRAY()
        fan_text = self.font.large.render(f"{fan_percent}%", True, fan_color)
        surface.blit(fan_text, (right_x + int(box_width * 0.41), row2_y + 14))

    def _draw_resource_bars(self, surface: pygame.Surface) -> None:
        """Draw CPU and RAM bars"""
        info = self.system_info

        # Calculate responsive dimensions
        margin = int(SCREEN_WIDTH * 0.03)
        section_width = int((SCREEN_WIDTH - margin * 3) / 2)
        right_x = margin + section_width + margin
        y = int(SCREEN_HEIGHT * 0.703)
        bar_height = int(SCREEN_HEIGHT * 0.188)
        bar_width = int(section_width * 0.91)
        label_offset = int(section_width * 0.07)

        # CPU
        for i, char in enumerate("CPU"):
            text = self.font.small.render(char, True, colors.GREEN())
            surface.blit(text, (margin, y + 8 + i * 15))
        cpu_color = self._get_threshold_color(info.cpu_percent, (70, 90))
        _draw_bar(self.ui, surface, margin + label_offset, y, bar_width, bar_height, info.cpu_percent, cpu_color)
        percent_text = self.font.medium.render(
            f"{info.cpu_percent:.0f}%", True, colors.WHITE()
        )
        surface.blit(percent_text, (margin + label_offset + bar_width // 2 - 20, y + 22))

        # RAM
        for i, char in enumerate("RAM"):
            text = self.font.small.render(char, True, colors.PURPLE())
            surface.blit(text, (right_x, y + 8 + i * 15))
        ram_color = (
            colors.PURPLE()
            if info.mem_percent < 70
            else self._get_threshold_color(info.mem_percent, (70, 90))
        )
        _draw_bar(
            self.ui, surface, right_x + label_offset, y, bar_width, bar_height, info.mem_percent, ram_color
        )
        percent_text = self.font.medium.render(
            f"{info.mem_percent:.0f}%", True, colors.WHITE()
        )
        surface.blit(percent_text, (right_x + label_offset + bar_width // 2 - 20, y + 22))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the system screen"""
        surface.fill(colors.BLACK())
        self._draw_header(surface)
        disk_y = int(SCREEN_HEIGHT * 0.172)
        self._draw_disk_bar(surface, disk_y)
        self._draw_info_boxes(surface)
        self._draw_resource_bars(surface)
