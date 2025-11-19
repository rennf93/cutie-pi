#!/usr/bin/env python3
"""
Pi-hole Pixel Dashboard
A retro 8-bit style dashboard for Pi-hole with swipeable screens
"""

import pygame
import requests
import time
import math
import os
import subprocess
import shutil
from collections import deque
from datetime import datetime

# Configuration
PIHOLE_API = "http://localhost/api"
PASSWORD_FILE = "/home/renzof/.pihole_password"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
FPS = 30

# Themes
# TODO

# Colors (retro palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 50, 50)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 100, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)


class PixelFont:
    """Pixel art font renderer"""

    def __init__(self) -> None:
        pygame.font.init()
        # Use Press Start 2P for that authentic 8-bit look
        pixel_font = os.path.expanduser("~/.fonts/PressStart2P.ttf")
        fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

        try:
            if os.path.exists(pixel_font):
                self.large = pygame.font.Font(pixel_font, 16)
                self.medium = pygame.font.Font(pixel_font, 12)
                self.small = pygame.font.Font(pixel_font, 8)
                self.tiny = pygame.font.Font(pixel_font, 6)
            else:
                raise FileNotFoundError("Pixel font not found")
        except Exception as e:
            print(f"Error loading pixel font: {e}")
            # Fallback to default
            self.large = pygame.font.Font(fallback, 32)
            self.medium = pygame.font.Font(fallback, 20)
            self.small = pygame.font.Font(fallback, 14)
            self.tiny = pygame.font.SysFont("monospace", 10)


class PiholeAPI:
    """Pi-hole API v6 handler"""

    def __init__(self) -> None:
        self.session_id = None
        self.password = self._load_password()
        self._authenticate()

    def _load_password(self) -> str:
        try:
            with open(PASSWORD_FILE, "r") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error loading password: {e}")
            return ""

    def _authenticate(self) -> None:
        """Authenticate with Pi-hole API v6"""
        if not self.password:
            return
        try:
            response = requests.post(
                f"{PIHOLE_API}/auth", json={"password": self.password}, timeout=5
            )
            if response.ok:
                data = response.json()
                self.session_id = data.get("session", {}).get("sid")
        except Exception as e:
            print(f"Error authenticating: {e}")
            pass

    def _get(self, endpoint: str) -> dict:
        """Make authenticated GET request"""
        headers: dict[str, str] = {}
        if self.session_id:
            headers["sid"] = self.session_id

        try:
            response = requests.get(
                f"{PIHOLE_API}{endpoint}", headers=headers, timeout=5
            )
            if response.ok:
                return response.json()
        except Exception as e:
            print(f"Error making GET request: {e}")
            pass
        return {}

    def get_summary(self) -> dict:
        """Get Pi-hole summary stats"""
        data = self._get("/stats/summary")

        # Map v6 API response to expected format
        queries = data.get("queries", {})
        clients = data.get("clients", {})
        return {
            "dns_queries_today": queries.get("total", 0),
            "ads_blocked_today": queries.get("blocked", 0),
            "ads_percentage_today": queries.get("percent_blocked", 0),
            "unique_clients": clients.get("active", 0),
            "domains_being_blocked": data.get("gravity", {}).get(
                "domains_being_blocked", 0
            ),
            "status": "enabled" if data.get("blocking", True) else "disabled",
        }

    def get_top_blocked(self, count: int = 10) -> dict:
        """Get top blocked domains"""
        data = self._get(f"/stats/top_domains?blocked=true&count={count}")

        # Convert to dict format
        result = {}
        for item in data.get("domains", []):
            result[item.get("domain", "unknown")] = item.get("count", 0)
        return result

    def get_top_clients(self, count: int = 10) -> dict:
        """Get top clients"""
        data = self._get(f"/stats/top_clients?count={count}")

        # Convert to dict format
        result = {}
        for item in data.get("clients", []):
            name = item.get("name") or item.get("ip", "unknown")
            result[name] = item.get("count", 0)
        return result

    def get_overtime(self) -> dict:
        """Get queries over time"""
        data = self._get("/history")

        # Convert to expected format
        domains = {}
        ads = {}

        for item in data.get("history", []):
            timestamp = item.get("timestamp", 0)
            domains[timestamp] = item.get("total", 0)
            ads[timestamp] = item.get("blocked", 0)

        return {"domains_over_time": domains, "ads_over_time": ads}


class Screen:
    """Base screen class"""

    def __init__(self, dashboard: "Dashboard") -> None:
        self.dashboard = dashboard
        self.font = dashboard.font

    def update(self, data: dict) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def draw_header(self, surface: pygame.Surface, title: str) -> None:
        """Draw screen header"""
        pygame.draw.rect(surface, DARK_GREEN, (0, 0, SCREEN_WIDTH, 40))
        text = self.font.medium.render(title, True, BLACK)
        surface.blit(text, (10, 8))

        # Draw page indicators
        num_screens = len(self.dashboard.screens)
        for i in range(num_screens):
            x = SCREEN_WIDTH - (num_screens * 15) + i * 15
            color = WHITE if i == self.dashboard.current_screen else GRAY
            pygame.draw.circle(surface, color, (x, 20), 4)

    def draw_pixel_border(
        self,
        surface: pygame.Surface,
        rect: tuple[int, int, int, int],
        color: tuple[int, int, int],
    ) -> None:
        """Draw a chunky pixelated border"""
        x, y, w, h = rect
        # Thick chunky border
        pygame.draw.rect(surface, color, rect, 3)
        # Corner blocks for that 8-bit feel
        block = 6
        for corner in [(x, y), (x + w - block, y), (x, y + h - block), (x + w - block, y + h - block)]:
            pygame.draw.rect(surface, color, (*corner, block, block))

    def draw_chunky_bar(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        percent: float,
        color: tuple[int, int, int],
        bg_color: tuple[int, int, int] = DARK_GRAY,
    ) -> None:
        """Draw a segmented pixel-art progress bar"""
        # Chunky segments - calculate how many fit
        segment_width = 6
        segment_gap = 2
        total_segment_size = segment_width + segment_gap
        num_segments = width // total_segment_size

        # Actual width used by segments (last segment has no gap after it)
        actual_width = num_segments * segment_width + (num_segments - 1) * segment_gap

        # Background matches actual segment area
        pygame.draw.rect(surface, bg_color, (x, y, actual_width, height))

        filled_segments = int((percent / 100) * num_segments)
        # Show at least 1 segment if percent > 0
        if percent > 0 and filled_segments == 0:
            filled_segments = 1

        for i in range(num_segments):
            seg_x = x + i * total_segment_size
            if i < filled_segments:
                pygame.draw.rect(surface, color, (seg_x, y + 2, segment_width, height - 4))
            else:
                pygame.draw.rect(surface, (30, 30, 30), (seg_x, y + 2, segment_width, height - 4))

    def draw_scanlines(self, surface: pygame.Surface) -> None:
        """Draw CRT scanline effect"""
        scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(scanline_surface, (0, 0, 0, 60), (0, y), (SCREEN_WIDTH, y), 1)
        surface.blit(scanline_surface, (0, 0))


class StatsScreen(Screen):
    """Main stats screen with animated counters"""

    def __init__(self, dashboard: "Dashboard") -> None:
        super().__init__(dashboard)
        self.animation_offset = 0
        self.displayed_queries = 0
        self.displayed_blocked = 0

    def update(self, data: dict) -> None:
        # Smooth counter animation
        target_queries = data.get("dns_queries_today", 0)
        target_blocked = data.get("ads_blocked_today", 0)

        self.displayed_queries += (target_queries - self.displayed_queries) * 0.1
        self.displayed_blocked += (target_blocked - self.displayed_blocked) * 0.1

        self.animation_offset = (self.animation_offset + 1) % 360

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        self.draw_header(surface, "PI-HOLE")

        data = self.dashboard.data

        y = 50

        # Total Queries box
        self.draw_pixel_border(surface, (15, y, 220, 65), GREEN)
        text = self.font.small.render("QUERIES", True, GREEN)
        surface.blit(text, (25, y + 8))
        num = self.font.large.render(f"{int(self.displayed_queries)}", True, WHITE)
        surface.blit(num, (25, y + 30))

        # Blocked box
        self.draw_pixel_border(surface, (250, y, 220, 65), RED)
        text = self.font.small.render("BLOCKED", True, RED)
        surface.blit(text, (260, y + 8))
        num = self.font.large.render(f"{int(self.displayed_blocked)}", True, WHITE)
        surface.blit(num, (260, y + 30))

        y = 130

        # Block percentage with chunky bar - wider
        percent = data.get("ads_percentage_today", 0)
        text = self.font.small.render("BLOCK RATE", True, CYAN)
        surface.blit(text, (15, y))
        self.draw_chunky_bar(surface, 15, y + 18, 370, 25, percent, CYAN)
        percent_text = self.font.medium.render(f"{percent:.1f}%", True, WHITE)
        surface.blit(percent_text, (395, y + 18))

        y = 185

        # Clients box
        clients = data.get("unique_clients", 0)
        self.draw_pixel_border(surface, (15, y, 220, 55), YELLOW)
        text = self.font.small.render("CLIENTS", True, YELLOW)
        surface.blit(text, (25, y + 8))
        num = self.font.medium.render(f"{clients}", True, WHITE)
        surface.blit(num, (25, y + 28))

        # Blocklist box
        domains = data.get("domains_being_blocked", 0)
        self.draw_pixel_border(surface, (250, y, 220, 55), PURPLE)
        text = self.font.small.render("BLOCKLIST", True, PURPLE)
        surface.blit(text, (260, y + 8))
        # Format large numbers
        if domains >= 1000000:
            domains_str = f"{domains/1000000:.1f}M"
        elif domains >= 1000:
            domains_str = f"{domains/1000:.0f}K"
        else:
            domains_str = str(domains)
        num = self.font.medium.render(domains_str, True, WHITE)
        surface.blit(num, (260, y + 28))

        y = 255

        # Status box
        status = data.get("status", "unknown")
        color = GREEN if status == "enabled" else RED
        self.draw_pixel_border(surface, (15, y, 220, 50), color)
        text = self.font.small.render("STATUS", True, color)
        surface.blit(text, (25, y + 8))
        # Pulsing dot + status text side by side
        pulse = abs(math.sin(self.animation_offset * 0.1)) * 3
        pygame.draw.rect(surface, color, (25, y + 28, int(8 + pulse), int(8 + pulse)))
        status_text = self.font.medium.render(status.upper(), True, WHITE)
        surface.blit(status_text, (45, y + 25))

        # DNS box - show Pi-hole's IP dynamically
        self.draw_pixel_border(surface, (250, y, 220, 50), CYAN)
        text = self.font.small.render("DNS", True, CYAN)
        surface.blit(text, (260, y + 8))
        # Get IP from system
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=1)
            ip = result.stdout.strip().split()[0] if result.stdout.strip() else "N/A"
        except Exception as e:
            print(f"Error getting IP: {e}")
            ip = "N/A"
        dns_text = self.font.medium.render(ip, True, WHITE)
        surface.blit(dns_text, (260, y + 25))

        # Scanlines
        self.draw_scanlines(surface)

    def draw_gauge(
        self, surface: pygame.Surface, x: int, y: int, radius: int, percent: int
    ) -> None:
        """Draw animated percentage gauge"""
        # Background arc
        pygame.draw.arc(
            surface,
            DARK_GRAY,
            (x - radius, y - radius, radius * 2, radius * 2),
            math.pi * 0.8,
            math.pi * 2.2,
            8,
        )

        # Percentage arc
        end_angle = math.pi * 0.8 + (math.pi * 1.4 * percent / 100)
        color = GREEN if percent > 50 else ORANGE if percent > 20 else RED
        pygame.draw.arc(
            surface,
            color,
            (x - radius, y - radius, radius * 2, radius * 2),
            math.pi * 0.8,
            end_angle,
            8,
        )

        # Center text
        text = self.font.large.render(f"{percent:.1f}%", True, color)
        rect = text.get_rect(center=(x, y + 30))
        surface.blit(text, rect)

        label = self.font.tiny.render("BLOCKED", True, GRAY)
        rect = label.get_rect(center=(x, y + 55))
        surface.blit(label, rect)


class GraphScreen(Screen):
    """Query graph over time"""

    def __init__(self, dashboard: "Dashboard") -> None:
        super().__init__(dashboard)
        self.queries_history: deque[int] = deque(maxlen=48)  # 8 hours of 10-min intervals
        self.blocked_history: deque[int] = deque(maxlen=48)

    def update(self, data: dict) -> None:
        overtime = self.dashboard.overtime_data
        if overtime:
            domains = overtime.get("domains_over_time", {})
            ads = overtime.get("ads_over_time", {})

            if domains:
                self.queries_history = deque(list(domains.values())[-48:], maxlen=48)
            if ads:
                self.blocked_history = deque(list(ads.values())[-48:], maxlen=48)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        self.draw_header(surface, "GRAPH")

        if not self.queries_history:
            text = self.font.medium.render("Loading data...", True, GRAY)
            surface.blit(text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
            return

        # Graph area - full width
        graph_x = 15
        graph_y = 50
        graph_w = SCREEN_WIDTH - 30
        graph_h = 220

        # Draw grid
        for i in range(5):
            y = graph_y + i * (graph_h // 4)
            pygame.draw.line(
                surface, DARK_GRAY, (graph_x, y), (graph_x + graph_w, y), 1
            )

        # Draw axes
        pygame.draw.line(
            surface, WHITE, (graph_x, graph_y), (graph_x, graph_y + graph_h), 2
        )
        pygame.draw.line(
            surface,
            WHITE,
            (graph_x, graph_y + graph_h),
            (graph_x + graph_w, graph_y + graph_h),
            2,
        )

        # Calculate max for scaling
        max_val = max(max(self.queries_history) if self.queries_history else 1, 1)

        # Draw bars
        bar_width = graph_w // len(self.queries_history) - 1

        for i, (queries, blocked) in enumerate(
            zip(self.queries_history, self.blocked_history)
        ):
            x = graph_x + i * (bar_width + 1)

            # Queries bar
            h = int((queries / max_val) * graph_h)
            pygame.draw.rect(
                surface, DARK_GREEN, (x, graph_y + graph_h - h, bar_width, h)
            )

            # Blocked portion
            h_blocked = int((blocked / max_val) * graph_h)
            pygame.draw.rect(
                surface, RED, (x, graph_y + graph_h - h_blocked, bar_width, h_blocked)
            )

        # Legend
        pygame.draw.rect(surface, DARK_GREEN, (graph_x, graph_y + graph_h + 15, 10, 10))
        text = self.font.tiny.render("Queries", True, WHITE)
        surface.blit(text, (graph_x + 15, graph_y + graph_h + 13))

        pygame.draw.rect(surface, RED, (graph_x + 80, graph_y + graph_h + 15, 10, 10))
        text = self.font.tiny.render("Blocked", True, WHITE)
        surface.blit(text, (graph_x + 95, graph_y + graph_h + 13))

        # Time labels
        text = self.font.tiny.render("-8h", True, GRAY)
        surface.blit(text, (graph_x, graph_y + graph_h + 30))
        text = self.font.tiny.render("now", True, GRAY)
        surface.blit(text, (graph_x + graph_w - 20, graph_y + graph_h + 30))

        # Scanlines
        self.draw_scanlines(surface)


class TopBlockedScreen(Screen):
    """Top blocked domains"""

    def __init__(self, dashboard: "Dashboard") -> None:
        super().__init__(dashboard)
        self.scroll_offset = 0

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        self.draw_header(surface, "BLOCKED")

        blocked = self.dashboard.top_blocked
        if not blocked:
            text = self.font.medium.render("No data", True, GRAY)
            surface.blit(text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2))
            return

        y = 50
        row_height = 28
        for i, (domain, count) in enumerate(list(blocked.items())[:9]):
            # Truncate long domains
            if len(domain) > 25:
                domain = domain[:22] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(
                    surface, (20, 20, 20), (10, y, SCREEN_WIDTH - 20, row_height)
                )

            # Rank - vertically centered
            rank_text = self.font.small.render(f"{i + 1}.", True, YELLOW)
            surface.blit(rank_text, (15, y + 8))

            # Domain - vertically centered
            domain_text = self.font.small.render(domain, True, WHITE)
            surface.blit(domain_text, (50, y + 8))

            # Count text - right aligned before bar
            count_text = self.font.small.render(str(count), True, WHITE)
            surface.blit(count_text, (SCREEN_WIDTH - 120, y + 8))

            # Count bar - right side
            max_count = max(blocked.values()) if blocked else 1
            bar_width = int((count / max_count) * 60)
            pygame.draw.rect(surface, RED, (SCREEN_WIDTH - 70, y + 8, bar_width, 12))

            y += row_height

        # Scanlines
        self.draw_scanlines(surface)


class ClientsScreen(Screen):
    """Top clients"""

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        self.draw_header(surface, "CLIENTS")

        clients = self.dashboard.top_clients
        if not clients:
            text = self.font.medium.render("No data", True, GRAY)
            surface.blit(text, (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2))
            return

        y = 50
        row_height = 28
        for i, (client, count) in enumerate(list(clients.items())[:9]):
            # Truncate long names
            if len(client) > 25:
                client = client[:22] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(
                    surface, (20, 20, 20), (10, y, SCREEN_WIDTH - 20, row_height)
                )

            # Rank with color coding - vertically centered
            colors = [YELLOW, WHITE, WHITE, GRAY, GRAY, GRAY, GRAY, GRAY, GRAY]
            rank_text = self.font.small.render(f"{i + 1}.", True, colors[i])
            surface.blit(rank_text, (15, y + 8))

            # Client name/IP - vertically centered
            client_text = self.font.small.render(client, True, CYAN)
            surface.blit(client_text, (50, y + 8))

            # Count text - right aligned before bar
            count_text = self.font.small.render(str(count), True, WHITE)
            surface.blit(count_text, (SCREEN_WIDTH - 120, y + 8))

            # Query count bar - right side
            max_count = max(clients.values()) if clients else 1
            bar_width = int((count / max_count) * 60)
            pygame.draw.rect(surface, GREEN, (SCREEN_WIDTH - 70, y + 8, bar_width, 12))

            y += row_height

        # Scanlines
        self.draw_scanlines(surface)


class SystemScreen(Screen):
    """System info screen - CPU, RAM, Temp, etc."""

    def __init__(self, dashboard: "Dashboard") -> None:
        super().__init__(dashboard)
        self.cpu_percent = 0
        self.mem_percent = 0
        self.mem_used = 0
        self.mem_total = 0
        self.temp = 0
        self.uptime = ""
        self.ip_address = ""
        self.hostname = ""
        self.fan_speed = 0
        self.fan_rpm = 0
        self.last_update = 0

    def get_system_info(self) -> None:
        """Fetch system information"""
        try:
            # CPU usage
            with open("/proc/stat", "r") as f:
                cpu_line = f.readline()
                cpu_times = list(map(int, cpu_line.split()[1:]))
                idle = cpu_times[3]
                total = sum(cpu_times)
                if hasattr(self, "_last_cpu"):
                    idle_delta = idle - self._last_cpu[0]
                    total_delta = total - self._last_cpu[1]
                    if total_delta > 0:
                        self.cpu_percent = 100 * (1 - idle_delta / total_delta)
                self._last_cpu = (idle, total)

            # Memory
            with open("/proc/meminfo", "r") as f:
                meminfo: dict[str, int] = {}
                for line in f:
                    parts = line.split()
                    meminfo[parts[0].rstrip(":")] = int(parts[1])
                self.mem_total = meminfo.get("MemTotal", 0) / 1024  # MB
                mem_available = meminfo.get("MemAvailable", 0) / 1024
                self.mem_used = self.mem_total - mem_available
                self.mem_percent = (
                    (self.mem_used / self.mem_total * 100) if self.mem_total > 0 else 0
                )

            # Temperature
            try:
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    self.temp = int(f.read().strip()) / 1000
            except Exception as e:
                print(f"Error getting temperature: {e}")
                self.temp = 0

            # Uptime
            try:
                with open("/proc/uptime", "r") as f:
                    uptime_secs = float(f.read().split()[0])
                    days = int(uptime_secs // 86400)
                    hours = int((uptime_secs % 86400) // 3600)
                    mins = int((uptime_secs % 3600) // 60)
                    if days > 0:
                        self.uptime = f"{days}d {hours}h {mins}m"
                    else:
                        self.uptime = f"{hours}h {mins}m"
            except Exception as e:
                print(f"Error getting uptime: {e}")
                self.uptime = "N/A"

            # IP Address
            try:
                result = subprocess.run(
                    ["hostname", "-I"], capture_output=True, text=True, timeout=2
                )
                self.ip_address = (
                    result.stdout.strip().split()[0] if result.stdout.strip() else "N/A"
                )
            except Exception as e:
                print(f"Error getting IP address: {e}")
                self.ip_address = "N/A"

            # Hostname
            try:
                with open("/etc/hostname", "r") as f:
                    self.hostname = f.read().strip()
            except Exception as e:
                print(f"Error getting hostname: {e}")
                self.hostname = "unknown"

            # Fan speed (RPM) - read directly from fan input
            fan_rpm_paths = [
                "/sys/devices/platform/cooling_fan/hwmon/hwmon2/fan1_input",
                "/sys/devices/platform/cooling_fan/hwmon/hwmon3/fan1_input",
                "/sys/devices/platform/cooling_fan/hwmon/hwmon1/fan1_input",
            ]
            fan_found = False
            for fan_path in fan_rpm_paths:
                try:
                    with open(fan_path, "r") as f:
                        self.fan_rpm = int(f.read().strip())
                        # Convert RPM to percentage (max ~10000 RPM for Pi 5 fan)
                        self.fan_speed = min(255, int((self.fan_rpm / 10000) * 255))
                        fan_found = True
                        break
                except Exception:
                    continue
            if not fan_found:
                self.fan_rpm = 0
                self.fan_speed = 0

        except Exception as e:
            print(f"Error getting system info: {e}")
            pass

    def update(self, data: dict) -> None:
        current_time = time.time()
        if current_time - self.last_update > 2:  # Update every 2 seconds
            self.get_system_info()
            self.last_update = current_time
        # Initial call
        if not self.uptime:
            self.get_system_info()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        self.draw_header(surface, "SYSTEM")

        y = 50

        # Hostname and IP
        text = self.font.medium.render(self.hostname, True, CYAN)
        surface.blit(text, (15, y))
        text = self.font.tiny.render(self.ip_address, True, GRAY)
        surface.blit(text, (15, y + 20))

        # Date and time (right side) - bigger and more prominent
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%a %d %b")

        time_text = self.font.large.render(time_str, True, WHITE)
        surface.blit(time_text, (SCREEN_WIDTH - 100, y))
        date_text = self.font.tiny.render(date_str, True, GRAY)
        surface.blit(date_text, (SCREEN_WIDTH - 100, y + 22))

        y = 90

        # Disk usage - full width bar at top
        text = self.font.small.render("DISK", True, GRAY)
        surface.blit(text, (15, y + 5))
        try:
            total, used, free = shutil.disk_usage("/")
            disk_percent = (used / total) * 100
            disk_text = f"{used // (1024**3)}G/{total // (1024**3)}G"
        except Exception as e:
            print(f"Error getting disk usage: {e}")
            disk_percent = 0
            disk_text = "N/A"
        self.draw_chunky_bar(surface, 60, y, 336, 22, disk_percent, GRAY)
        disk_info = self.font.small.render(disk_text, True, WHITE)
        surface.blit(disk_info, (405, y + 5))

        y = 130

        # Temperature box
        self.draw_pixel_border(surface, (15, y, 220, 50), ORANGE)
        text = self.font.small.render("TEMP", True, ORANGE)
        surface.blit(text, (25, y + 17))
        temp_color = GREEN if self.temp < 60 else ORANGE if self.temp < 75 else RED
        temp_text = self.font.large.render(f"{self.temp:.0f}C", True, temp_color)
        surface.blit(temp_text, (110, y + 14))

        # Memory box
        self.draw_pixel_border(surface, (250, y, 220, 50), CYAN)
        text = self.font.small.render("MEM", True, CYAN)
        surface.blit(text, (260, y + 17))
        mem_text = self.font.large.render(f"{self.mem_used:.0f}/{self.mem_total:.0f}", True, WHITE)
        surface.blit(mem_text, (310, y + 14))

        # Middle row - Uptime and Fan
        y = 195

        # Uptime box
        self.draw_pixel_border(surface, (15, y, 220, 50), GREEN)
        text = self.font.small.render("UP", True, GREEN)
        surface.blit(text, (25, y + 17))
        uptime_text = self.font.large.render(self.uptime if self.uptime else "...", True, WHITE)
        surface.blit(uptime_text, (90, y + 14))

        # Fan box
        self.draw_pixel_border(surface, (250, y, 220, 50), YELLOW)
        text = self.font.small.render("FAN", True, YELLOW)
        surface.blit(text, (260, y + 17))
        fan_percent = int((self.fan_speed / 255) * 100)
        fan_text = self.font.large.render(
            f"{fan_percent}%", True, WHITE if fan_percent > 0 else GRAY
        )
        surface.blit(fan_text, (340, y + 14))

        # Bottom row - CPU and RAM tall bars with vertical labels
        y = 250
        bar_height = 60

        # CPU - label close to bar
        text = self.font.small.render("C", True, GREEN)
        surface.blit(text, (15, y + 8))
        text = self.font.small.render("P", True, GREEN)
        surface.blit(text, (15, y + 23))
        text = self.font.small.render("U", True, GREEN)
        surface.blit(text, (15, y + 38))
        cpu_color = GREEN if self.cpu_percent < 70 else ORANGE if self.cpu_percent < 90 else RED
        self.draw_chunky_bar(surface, 30, y, 200, bar_height, self.cpu_percent, cpu_color)
        percent_text = self.font.medium.render(f"{self.cpu_percent:.0f}%", True, WHITE)
        surface.blit(percent_text, (100, y + 22))

        # RAM - label close to bar
        text = self.font.small.render("R", True, PURPLE)
        surface.blit(text, (250, y + 8))
        text = self.font.small.render("A", True, PURPLE)
        surface.blit(text, (250, y + 23))
        text = self.font.small.render("M", True, PURPLE)
        surface.blit(text, (250, y + 38))
        ram_color = PURPLE if self.mem_percent < 70 else ORANGE if self.mem_percent < 90 else RED
        self.draw_chunky_bar(surface, 265, y, 200, bar_height, self.mem_percent, ram_color)
        percent_text = self.font.medium.render(f"{self.mem_percent:.0f}%", True, WHITE)
        surface.blit(percent_text, (335, y + 22))

        # Add scanlines for that CRT effect
        self.draw_scanlines(surface)


class Dashboard:
    """Main dashboard controller"""

    def __init__(self) -> None:
        pygame.init()

        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pi-hole Dashboard")
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.font = PixelFont()
        self.api = PiholeAPI()

        # Data
        self.data: dict = {}
        self.top_blocked: dict = {}
        self.top_clients: dict = {}
        self.overtime_data: dict = {}

        # Screens
        self.screens = [
            StatsScreen(self),
            GraphScreen(self),
            TopBlockedScreen(self),
            ClientsScreen(self),
            SystemScreen(self),
        ]
        self.current_screen = 0

        # Touch handling
        self.touch_start = None
        self.last_update = 0
        self.update_interval = 5  # seconds

        # Transition animation
        self.transitioning = False
        self.transition_direction = 0
        self.transition_progress = 0

    def fetch_data(self) -> None:
        """Fetch all data from Pi-hole API"""
        self.data = self.api.get_summary()
        self.top_blocked = self.api.get_top_blocked()
        self.top_clients = self.api.get_top_clients()
        self.overtime_data = self.api.get_overtime()

    def handle_events(self) -> bool:
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_LEFT:
                    self.prev_screen()
                elif event.key == pygame.K_RIGHT:
                    self.next_screen()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.touch_start = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.touch_start:
                    dx = event.pos[0] - self.touch_start[0]
                    if abs(dx) > 50:  # Swipe threshold
                        if dx > 0:
                            self.prev_screen()
                        else:
                            self.next_screen()
                    self.touch_start = None

        return True

    def next_screen(self) -> None:
        """Transition to next screen"""
        if not self.transitioning:
            self.transitioning = True
            self.transition_direction = -1
            self.transition_progress = 0
            self.next_screen_index = (self.current_screen + 1) % len(self.screens)

    def prev_screen(self) -> None:
        """Transition to previous screen"""
        if not self.transitioning:
            self.transitioning = True
            self.transition_direction = 1
            self.transition_progress = 0
            self.next_screen_index = (self.current_screen - 1) % len(self.screens)

    def update(self) -> None:
        """Update dashboard state"""
        # Fetch new data periodically
        current_time = time.time()
        if current_time - self.last_update > self.update_interval:
            self.fetch_data()
            self.last_update = current_time

        # Update current screen
        self.screens[self.current_screen].update(self.data)

        # Handle transition animation
        if self.transitioning:
            self.transition_progress: float = self.transition_progress + 0.15
            if self.transition_progress >= 1:
                self.current_screen: int = self.next_screen_index
                self.transitioning: bool = False
                self.transition_progress: float = 0

    def draw(self) -> None:
        """Draw the dashboard"""
        if self.transitioning:
            # Draw transition animation
            offset = int(
                self.transition_progress * SCREEN_WIDTH * self.transition_direction
            )

            # Current screen sliding out
            current_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screens[self.current_screen].draw(current_surface)
            self.screen.blit(current_surface, (offset, 0))

            # Next screen sliding in
            next_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screens[self.next_screen_index].draw(next_surface)
            next_offset = offset - (SCREEN_WIDTH * self.transition_direction)
            self.screen.blit(next_surface, (next_offset, 0))
        else:
            self.screens[self.current_screen].draw(self.screen)

        pygame.display.flip()

    def run(self) -> None:
        """Main loop"""
        # Initial data fetch
        self.fetch_data()

        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()
