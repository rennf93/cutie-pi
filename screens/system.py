"""System information screen"""

import shutil
from datetime import datetime
import pygame
from .base import BaseScreen
from ui.colors import WHITE, GREEN, RED, ORANGE, YELLOW, CYAN, GRAY, PURPLE, BLACK
from ui.fonts import PixelFont
from ui.components import UIComponents
from utils.system_info import SystemInfo


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
        surface.fill(BLACK)
        info = self.system_info

        # Title with hostname
        title = self.font.medium.render(info.hostname.upper(), True, CYAN)
        surface.blit(title, (10, 10))

        # IP address below hostname
        ip_text = self.font.tiny.render(info.ip_address, True, GRAY)
        surface.blit(ip_text, (10, 30))

        # Date and time (right side)
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%a %d %b")

        time_text = self.font.large.render(time_str, True, WHITE)
        surface.blit(time_text, (380, 10))
        date_text = self.font.tiny.render(date_str, True, GRAY)
        surface.blit(date_text, (380, 32))

        y = 55

        # Disk usage - full width bar at top
        text = self.font.small.render("DISK", True, GRAY)
        surface.blit(text, (15, y + 5))
        try:
            total, used, free = shutil.disk_usage("/")
            disk_percent = (used / total) * 100
            disk_text = f"{used // (1024**3)}G/{total // (1024**3)}G"
        except Exception:
            disk_percent = 0
            disk_text = "N/A"
        self.ui.draw_chunky_bar(surface, 60, y, 336, 22, disk_percent, GRAY)
        disk_info = self.font.small.render(disk_text, True, WHITE)
        surface.blit(disk_info, (405, y + 5))

        y = 95

        # Temperature box
        self.ui.draw_pixel_border(surface, pygame.Rect(15, y, 220, 50), ORANGE)
        text = self.font.small.render("TEMP", True, ORANGE)
        surface.blit(text, (25, y + 17))
        temp_color = GREEN if info.temp < 60 else ORANGE if info.temp < 75 else RED
        temp_text = self.font.large.render(f"{info.temp:.0f}C", True, temp_color)
        surface.blit(temp_text, (110, y + 14))

        # Memory box
        self.ui.draw_pixel_border(surface, pygame.Rect(250, y, 220, 50), CYAN)
        text = self.font.small.render("MEM", True, CYAN)
        surface.blit(text, (260, y + 17))
        mem_text = self.font.large.render(f"{info.mem_used:.0f}/{info.mem_total:.0f}", True, WHITE)
        surface.blit(mem_text, (310, y + 14))

        # Middle row - Uptime and Fan
        y = 160

        # Uptime box
        self.ui.draw_pixel_border(surface, pygame.Rect(15, y, 220, 50), GREEN)
        text = self.font.small.render("UP", True, GREEN)
        surface.blit(text, (25, y + 17))
        uptime_text = self.font.large.render(info.uptime if info.uptime else "...", True, WHITE)
        surface.blit(uptime_text, (90, y + 14))

        # Fan box
        self.ui.draw_pixel_border(surface, pygame.Rect(250, y, 220, 50), YELLOW)
        text = self.font.small.render("FAN", True, YELLOW)
        surface.blit(text, (260, y + 17))
        fan_percent = int((info.fan_speed / 255) * 100)
        fan_text = self.font.large.render(
            f"{fan_percent}%", True, WHITE if fan_percent > 0 else GRAY
        )
        surface.blit(fan_text, (340, y + 14))

        # Bottom row - CPU and RAM tall bars with vertical labels
        y = 225
        bar_height = 60

        # CPU - vertical label close to bar
        text = self.font.small.render("C", True, GREEN)
        surface.blit(text, (15, y + 8))
        text = self.font.small.render("P", True, GREEN)
        surface.blit(text, (15, y + 23))
        text = self.font.small.render("U", True, GREEN)
        surface.blit(text, (15, y + 38))
        cpu_color = GREEN if info.cpu_percent < 70 else ORANGE if info.cpu_percent < 90 else RED
        self.ui.draw_chunky_bar(surface, 30, y, 200, bar_height, info.cpu_percent, cpu_color)
        percent_text = self.font.medium.render(f"{info.cpu_percent:.0f}%", True, WHITE)
        surface.blit(percent_text, (100, y + 22))

        # RAM - vertical label close to bar
        text = self.font.small.render("R", True, PURPLE)
        surface.blit(text, (250, y + 8))
        text = self.font.small.render("A", True, PURPLE)
        surface.blit(text, (250, y + 23))
        text = self.font.small.render("M", True, PURPLE)
        surface.blit(text, (250, y + 38))
        ram_color = PURPLE if info.mem_percent < 70 else ORANGE if info.mem_percent < 90 else RED
        self.ui.draw_chunky_bar(surface, 265, y, 200, bar_height, info.mem_percent, ram_color)
        percent_text = self.font.medium.render(f"{info.mem_percent:.0f}%", True, WHITE)
        surface.blit(percent_text, (335, y + 22))
