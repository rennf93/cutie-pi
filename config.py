"""Configuration and constants for the Pi-hole dashboard"""

import os

from __version__ import __version__

# Version
VERSION = __version__

# Display settings
SCREEN_WIDTH = int(os.environ.get("CUTIE_SCREEN_WIDTH", "480"))
SCREEN_HEIGHT = int(os.environ.get("CUTIE_SCREEN_HEIGHT", "320"))
FPS = int(os.environ.get("CUTIE_FPS", "30"))

# Pi-hole API settings
PIHOLE_API = os.environ.get("CUTIE_PIHOLE_API", "http://localhost/api")
PIHOLE_PASSWORD = os.environ.get("CUTIE_PIHOLE_PASSWORD", "")

# Update intervals (seconds)
API_UPDATE_INTERVAL = int(os.environ.get("CUTIE_API_INTERVAL", "5"))
SYSTEM_UPDATE_INTERVAL = int(os.environ.get("CUTIE_SYSTEM_INTERVAL", "2"))

# Screen indices
SCREEN_STATS = 0
SCREEN_GRAPH = 1
SCREEN_BLOCKED = 2
SCREEN_CLIENTS = 3
SCREEN_SYSTEM = 4
SCREEN_SETTINGS = 5
TOTAL_SCREENS = 6

# Theme setting
THEME = os.environ.get("CUTIE_THEME", "default")

# Swipe detection
SWIPE_THRESHOLD = int(os.environ.get("CUTIE_SWIPE_THRESHOLD", "50"))
