"""Configuration and constants for the Pi-hole dashboard"""

import os

from __version__ import __version__


def _get_int_env(
    key: str, default: int, min_val: int | None = None, max_val: int | None = None
) -> int:
    """Get integer from environment with validation"""
    try:
        value = int(os.environ.get(key, str(default)))
        if min_val is not None and value < min_val:
            print(f"Warning: {key}={value} below minimum {min_val}, using {min_val}")
            return min_val
        if max_val is not None and value > max_val:
            print(f"Warning: {key}={value} exceeds maximum {max_val}, using {max_val}")
            return max_val
        return value
    except ValueError:
        print(f"Warning: Invalid {key} value, using default {default}")
        return default


# Version
VERSION = __version__

# Display settings
SCREEN_WIDTH = _get_int_env("CUTIE_SCREEN_WIDTH", 480, min_val=100, max_val=1920)
SCREEN_HEIGHT = _get_int_env("CUTIE_SCREEN_HEIGHT", 320, min_val=100, max_val=1080)
FPS = _get_int_env("CUTIE_FPS", 30, min_val=1, max_val=120)

# Pi-hole API settings
PIHOLE_API = os.environ.get("CUTIE_PIHOLE_API", "http://localhost/api")
PIHOLE_PASSWORD = os.environ.get("CUTIE_PIHOLE_PASSWORD", "")

# Update intervals (seconds)
API_UPDATE_INTERVAL = _get_int_env("CUTIE_API_INTERVAL", 5, min_val=1, max_val=3600)
SYSTEM_UPDATE_INTERVAL = _get_int_env("CUTIE_SYSTEM_INTERVAL", 2, min_val=1, max_val=60)

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
SWIPE_THRESHOLD = _get_int_env("CUTIE_SWIPE_THRESHOLD", 50, min_val=10, max_val=200)
