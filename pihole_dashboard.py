#!/usr/bin/env python3
"""
Pi-hole Pixel Dashboard
A retro 8-bit style dashboard for Pi-hole with swipeable screens
"""

import pygame
import requests
import time
import math
from collections import deque
from datetime import datetime

# Configuration
PIHOLE_API = "http://localhost/admin/api.php"
PASSWORD_FILE = "/home/renzof/.pihole_password"
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 320
FPS = 30

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
    """Simple pixel font renderer"""
    def __init__(self):
        pygame.font.init()
        # Use a monospace font for that retro feel
        try:
            self.large = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 32)
            self.medium = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 20)
            self.small = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
            self.tiny = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
        except:
            # Fallback to default
            self.large = pygame.font.SysFont("monospace", 32, bold=True)
            self.medium = pygame.font.SysFont("monospace", 20, bold=True)
            self.small = pygame.font.SysFont("monospace", 14)
            self.tiny = pygame.font.SysFont("monospace", 10)

class PiholeAPI:
    """Pi-hole API handler"""
    def __init__(self):
        self.session_id = None
        self.password = self._load_password()
        self._authenticate()

    def _load_password(self):
        try:
            with open(PASSWORD_FILE, 'r') as f:
                return f.read().strip()
        except:
            return ""

    def _authenticate(self):
        """Authenticate with Pi-hole API v6"""
        if not self.password:
            return
        try:
            response = requests.post(
                f"{PIHOLE_API}",
                json={"auth": self.password},
                timeout=5
            )
            if response.ok:
                data = response.json()
                self.session_id = data.get("session", {}).get("sid")
        except:
            pass

    def get_summary(self):
        """Get Pi-hole summary stats"""
        try:
            params = {}
            if self.session_id:
                params["sid"] = self.session_id

            response = requests.get(
                f"{PIHOLE_API}?summaryRaw",
                params=params,
                timeout=5
            )
            if response.ok:
                return response.json()
        except Exception as e:
            pass
        return {}

    def get_top_blocked(self, count=10):
        """Get top blocked domains"""
        try:
            params = {"topItems": count}
            if self.session_id:
                params["sid"] = self.session_id

            response = requests.get(
                f"{PIHOLE_API}",
                params=params,
                timeout=5
            )
            if response.ok:
                data = response.json()
                return data.get("top_ads", {})
        except:
            pass
        return {}

    def get_top_clients(self, count=10):
        """Get top clients"""
        try:
            params = {"topClients": count}
            if self.session_id:
                params["sid"] = self.session_id

            response = requests.get(
                f"{PIHOLE_API}",
                params=params,
                timeout=5
            )
            if response.ok:
                data = response.json()
                return data.get("top_sources", {})
        except:
            pass
        return {}

    def get_overtime(self):
        """Get queries over time"""
        try:
            params = {"overTimeData10mins": ""}
            if self.session_id:
                params["sid"] = self.session_id

            response = requests.get(
                f"{PIHOLE_API}",
                params=params,
                timeout=5
            )
            if response.ok:
                return response.json()
        except:
            pass
        return {}


class Screen:
    """Base screen class"""
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.font = dashboard.font

    def update(self, data):
        pass

    def draw(self, surface):
        pass

    def draw_header(self, surface, title):
        """Draw screen header"""
        pygame.draw.rect(surface, DARK_GREEN, (0, 0, SCREEN_WIDTH, 40))
        text = self.font.medium.render(title, True, BLACK)
        surface.blit(text, (10, 8))

        # Draw page indicators
        for i in range(4):
            x = SCREEN_WIDTH - 60 + i * 15
            color = WHITE if i == self.dashboard.current_screen else GRAY
            pygame.draw.circle(surface, color, (x, 20), 4)

    def draw_pixel_border(self, surface, rect, color):
        """Draw a pixelated border"""
        x, y, w, h = rect
        pygame.draw.rect(surface, color, rect, 2)
        # Corner pixels for that 8-bit feel
        for corner in [(x, y), (x+w-4, y), (x, y+h-4), (x+w-4, y+h-4)]:
            pygame.draw.rect(surface, color, (*corner, 4, 4))


class StatsScreen(Screen):
    """Main stats screen with animated counters"""
    def __init__(self, dashboard):
        super().__init__(dashboard)
        self.animation_offset = 0
        self.displayed_queries = 0
        self.displayed_blocked = 0

    def update(self, data):
        # Smooth counter animation
        target_queries = data.get("dns_queries_today", 0)
        target_blocked = data.get("ads_blocked_today", 0)

        self.displayed_queries += (target_queries - self.displayed_queries) * 0.1
        self.displayed_blocked += (target_blocked - self.displayed_blocked) * 0.1

        self.animation_offset = (self.animation_offset + 1) % 360

    def draw(self, surface):
        surface.fill(BLACK)
        self.draw_header(surface, "< PI-HOLE STATS >")

        data = self.dashboard.data

        # Animated scanning line effect
        scan_y = 40 + (self.animation_offset % 280)
        pygame.draw.line(surface, (0, 50, 0), (0, scan_y), (SCREEN_WIDTH, scan_y), 1)

        # Total Queries box
        self.draw_pixel_border(surface, (20, 60, 200, 80), GREEN)
        text = self.font.small.render("TOTAL QUERIES", True, GREEN)
        surface.blit(text, (30, 70))
        num = self.font.large.render(f"{int(self.displayed_queries):,}", True, WHITE)
        surface.blit(num, (30, 95))

        # Blocked box
        self.draw_pixel_border(surface, (260, 60, 200, 80), RED)
        text = self.font.small.render("BLOCKED", True, RED)
        surface.blit(text, (270, 70))
        num = self.font.large.render(f"{int(self.displayed_blocked):,}", True, WHITE)
        surface.blit(num, (270, 95))

        # Block percentage with animated gauge
        percent = data.get("ads_percentage_today", 0)
        self.draw_gauge(surface, 120, 200, 80, percent)

        # Clients and domains
        clients = data.get("unique_clients", 0)
        domains = data.get("domains_being_blocked", 0)

        text = self.font.small.render(f"CLIENTS: {clients}", True, CYAN)
        surface.blit(text, (280, 180))

        text = self.font.small.render(f"BLOCKLIST: {domains:,}", True, YELLOW)
        surface.blit(text, (280, 210))

        # Status indicator
        status = data.get("status", "unknown")
        color = GREEN if status == "enabled" else RED
        pygame.draw.circle(surface, color, (440, 280), 10)
        # Pulsing effect
        pulse = abs(math.sin(self.animation_offset * 0.05)) * 5
        pygame.draw.circle(surface, color, (440, 280), int(10 + pulse), 2)

        text = self.font.tiny.render(status.upper(), True, color)
        surface.blit(text, (420, 295))

        # Date and time
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")

        time_text = self.font.medium.render(time_str, True, WHITE)
        surface.blit(time_text, (280, 250))

        date_text = self.font.tiny.render(date_str, True, GRAY)
        surface.blit(date_text, (280, 275))

    def draw_gauge(self, surface, x, y, radius, percent):
        """Draw animated percentage gauge"""
        # Background arc
        pygame.draw.arc(surface, DARK_GRAY, (x-radius, y-radius, radius*2, radius*2),
                       math.pi * 0.8, math.pi * 2.2, 8)

        # Percentage arc
        end_angle = math.pi * 0.8 + (math.pi * 1.4 * percent / 100)
        color = GREEN if percent > 50 else ORANGE if percent > 20 else RED
        pygame.draw.arc(surface, color, (x-radius, y-radius, radius*2, radius*2),
                       math.pi * 0.8, end_angle, 8)

        # Center text
        text = self.font.large.render(f"{percent:.1f}%", True, color)
        rect = text.get_rect(center=(x, y + 30))
        surface.blit(text, rect)

        label = self.font.tiny.render("BLOCKED", True, GRAY)
        rect = label.get_rect(center=(x, y + 55))
        surface.blit(label, rect)


class GraphScreen(Screen):
    """Query graph over time"""
    def __init__(self, dashboard):
        super().__init__(dashboard)
        self.queries_history = deque(maxlen=48)  # 8 hours of 10-min intervals
        self.blocked_history = deque(maxlen=48)

    def update(self, data):
        overtime = self.dashboard.overtime_data
        if overtime:
            domains = overtime.get("domains_over_time", {})
            ads = overtime.get("ads_over_time", {})

            if domains:
                self.queries_history = deque(list(domains.values())[-48:], maxlen=48)
            if ads:
                self.blocked_history = deque(list(ads.values())[-48:], maxlen=48)

    def draw(self, surface):
        surface.fill(BLACK)
        self.draw_header(surface, "< QUERY GRAPH >")

        if not self.queries_history:
            text = self.font.medium.render("Loading data...", True, GRAY)
            surface.blit(text, (SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2))
            return

        # Graph area
        graph_x = 50
        graph_y = 60
        graph_w = SCREEN_WIDTH - 70
        graph_h = 200

        # Draw grid
        for i in range(5):
            y = graph_y + i * (graph_h // 4)
            pygame.draw.line(surface, DARK_GRAY, (graph_x, y), (graph_x + graph_w, y), 1)

        # Draw axes
        pygame.draw.line(surface, WHITE, (graph_x, graph_y), (graph_x, graph_y + graph_h), 2)
        pygame.draw.line(surface, WHITE, (graph_x, graph_y + graph_h), (graph_x + graph_w, graph_y + graph_h), 2)

        # Calculate max for scaling
        max_val = max(max(self.queries_history) if self.queries_history else 1, 1)

        # Draw bars
        bar_width = graph_w // len(self.queries_history) - 1

        for i, (queries, blocked) in enumerate(zip(self.queries_history, self.blocked_history)):
            x = graph_x + i * (bar_width + 1)

            # Queries bar
            h = int((queries / max_val) * graph_h)
            pygame.draw.rect(surface, DARK_GREEN, (x, graph_y + graph_h - h, bar_width, h))

            # Blocked portion
            h_blocked = int((blocked / max_val) * graph_h)
            pygame.draw.rect(surface, RED, (x, graph_y + graph_h - h_blocked, bar_width, h_blocked))

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


class TopBlockedScreen(Screen):
    """Top blocked domains"""
    def __init__(self, dashboard):
        super().__init__(dashboard)
        self.scroll_offset = 0

    def draw(self, surface):
        surface.fill(BLACK)
        self.draw_header(surface, "< TOP BLOCKED >")

        blocked = self.dashboard.top_blocked
        if not blocked:
            text = self.font.medium.render("No data", True, GRAY)
            surface.blit(text, (SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2))
            return

        y = 60
        for i, (domain, count) in enumerate(list(blocked.items())[:8]):
            # Truncate long domains
            if len(domain) > 35:
                domain = domain[:32] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(surface, (20, 20, 20), (10, y-2, SCREEN_WIDTH-20, 28))

            # Rank
            rank_text = self.font.small.render(f"{i+1}.", True, YELLOW)
            surface.blit(rank_text, (15, y))

            # Domain
            domain_text = self.font.tiny.render(domain, True, WHITE)
            surface.blit(domain_text, (45, y + 2))

            # Count bar
            max_count = max(blocked.values()) if blocked else 1
            bar_width = int((count / max_count) * 100)
            pygame.draw.rect(surface, RED, (SCREEN_WIDTH - 130, y + 5, bar_width, 12))

            # Count text
            count_text = self.font.tiny.render(str(count), True, WHITE)
            surface.blit(count_text, (SCREEN_WIDTH - 25, y + 2))

            y += 30


class ClientsScreen(Screen):
    """Top clients"""
    def draw(self, surface):
        surface.fill(BLACK)
        self.draw_header(surface, "< TOP CLIENTS >")

        clients = self.dashboard.top_clients
        if not clients:
            text = self.font.medium.render("No data", True, GRAY)
            surface.blit(text, (SCREEN_WIDTH//2 - 40, SCREEN_HEIGHT//2))
            return

        y = 60
        for i, (client, count) in enumerate(list(clients.items())[:8]):
            # Truncate long names
            if len(client) > 30:
                client = client[:27] + "..."

            # Alternating row colors
            if i % 2 == 0:
                pygame.draw.rect(surface, (20, 20, 20), (10, y-2, SCREEN_WIDTH-20, 28))

            # Rank with color coding
            colors = [YELLOW, WHITE, WHITE, GRAY, GRAY, GRAY, GRAY, GRAY]
            rank_text = self.font.small.render(f"{i+1}.", True, colors[i])
            surface.blit(rank_text, (15, y))

            # Client name/IP
            client_text = self.font.small.render(client, True, CYAN)
            surface.blit(client_text, (45, y))

            # Query count bar
            max_count = max(clients.values()) if clients else 1
            bar_width = int((count / max_count) * 100)
            pygame.draw.rect(surface, GREEN, (SCREEN_WIDTH - 130, y + 5, bar_width, 12))

            # Count
            count_text = self.font.tiny.render(str(count), True, WHITE)
            surface.blit(count_text, (SCREEN_WIDTH - 25, y + 2))

            y += 30


class Dashboard:
    """Main dashboard controller"""
    def __init__(self):
        pygame.init()

        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pi-hole Dashboard")
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.font = PixelFont()
        self.api = PiholeAPI()

        # Data
        self.data = {}
        self.top_blocked = {}
        self.top_clients = {}
        self.overtime_data = {}

        # Screens
        self.screens = [
            StatsScreen(self),
            GraphScreen(self),
            TopBlockedScreen(self),
            ClientsScreen(self)
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

    def fetch_data(self):
        """Fetch all data from Pi-hole API"""
        self.data = self.api.get_summary()
        self.top_blocked = self.api.get_top_blocked()
        self.top_clients = self.api.get_top_clients()
        self.overtime_data = self.api.get_overtime()

    def handle_events(self):
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

    def next_screen(self):
        """Transition to next screen"""
        if not self.transitioning:
            self.transitioning = True
            self.transition_direction = -1
            self.transition_progress = 0
            self.next_screen_index = (self.current_screen + 1) % len(self.screens)

    def prev_screen(self):
        """Transition to previous screen"""
        if not self.transitioning:
            self.transitioning = True
            self.transition_direction = 1
            self.transition_progress = 0
            self.next_screen_index = (self.current_screen - 1) % len(self.screens)

    def update(self):
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
            self.transition_progress += 0.15
            if self.transition_progress >= 1:
                self.current_screen = self.next_screen_index
                self.transitioning = False
                self.transition_progress = 0

    def draw(self):
        """Draw the dashboard"""
        if self.transitioning:
            # Draw transition animation
            offset = int(self.transition_progress * SCREEN_WIDTH * self.transition_direction)

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

    def run(self):
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
