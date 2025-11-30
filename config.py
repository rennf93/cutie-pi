"""Configuration and constants for the Pi-hole dashboard"""

import os

from __version__ import __version__
from utils.logger import logger


def _get_int_env(key: str, default: int, min_val: int = 0, max_val: int = 10000) -> int:
    """Get integer from environment with validation"""
    try:
        value = int(os.environ.get(key, str(default)))
    except ValueError:
        logger.warning(f"Invalid {key} value, using default {default}")
        return default

    if value < min_val:
        logger.warning(f"{key}={value} below minimum {min_val}, using {min_val}")
        return min_val
    if value > max_val:
        logger.warning(f"{key}={value} exceeds maximum {max_val}, using {max_val}")
        return max_val
    return value


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

# Display timeout (minutes, 0 = never)
SCREEN_TIMEOUT = _get_int_env("CUTIE_SCREEN_TIMEOUT", 0, min_val=0, max_val=60)

# Visual settings
SCANLINES_ENABLED = os.environ.get("CUTIE_SCANLINES", "true").lower() in ("true", "1", "yes")
SHOW_FPS = os.environ.get("CUTIE_SHOW_FPS", "false").lower() in ("true", "1", "yes")
BRIGHTNESS = _get_int_env("CUTIE_BRIGHTNESS", 100, min_val=10, max_val=100)

# Config file path
CONFIG_FILE = "/etc/cutie-pi/config"


def save_settings(
    theme: str,
    api_interval: int,
    screen_timeout: int,
    scanlines: bool,
    show_fps: bool,
    brightness: int,
) -> bool:
    """Save current settings to config file.

    Returns True if successful, False otherwise.
    """
    try:
        # Read existing config to preserve Pi-hole credentials and display settings
        existing_config: dict[str, str] = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        existing_config[key.strip()] = value.strip().strip('"')

        # Update with new values while preserving others
        existing_config["CUTIE_THEME"] = theme
        existing_config["CUTIE_API_INTERVAL"] = str(api_interval)
        existing_config["CUTIE_SCREEN_TIMEOUT"] = str(screen_timeout)
        existing_config["CUTIE_SCANLINES"] = "true" if scanlines else "false"
        existing_config["CUTIE_SHOW_FPS"] = "true" if show_fps else "false"
        existing_config["CUTIE_BRIGHTNESS"] = str(brightness)

        # Write updated config
        with open(CONFIG_FILE, "w") as f:
            f.write("# Cutie-Pi Configuration\n")
            f.write("# Settings auto-saved by application\n\n")
            for key, value in sorted(existing_config.items()):
                f.write(f'{key}="{value}"\n')

        logger.info(f"Settings saved to {CONFIG_FILE}")
        return True
    except (OSError, PermissionError) as e:
        logger.error(f"Could not save settings to {CONFIG_FILE}: {e}")
        return False


# =============================================================================
# Responsive Layout System
# =============================================================================
# All layout values are calculated as percentages of screen dimensions
# to ensure consistent appearance across different screen sizes
# (240x320, 480x320, 800x480, etc.)
# =============================================================================

class Layout:
    """Centralized responsive layout calculations"""

    # Base reference dimensions (original design target)
    _REF_WIDTH = 480
    _REF_HEIGHT = 320

    # Scale factors
    scale_x: float = SCREEN_WIDTH / _REF_WIDTH
    scale_y: float = SCREEN_HEIGHT / _REF_HEIGHT
    scale_min: float = min(scale_x, scale_y)

    # ==========================================================================
    # Common Margins & Padding (scaled from reference 480x320)
    # ==========================================================================
    margin_xs: int = max(2, int(4 * scale_x))    # Extra small: ~4px at 480w
    margin_sm: int = max(4, int(10 * scale_x))   # Small: ~10px at 480w
    margin_md: int = max(6, int(15 * scale_x))   # Medium: ~15px at 480w
    margin_lg: int = max(8, int(25 * scale_x))   # Large: ~25px at 480w

    padding_xs: int = max(2, int(5 * scale_y))   # Extra small vertical
    padding_sm: int = max(4, int(8 * scale_y))   # Small vertical
    padding_md: int = max(6, int(12 * scale_y))  # Medium vertical
    padding_lg: int = max(8, int(17 * scale_y))  # Large vertical

    # ==========================================================================
    # Title & Header positioning
    # ==========================================================================
    title_x: int = margin_sm
    title_y: int = margin_sm
    header_height: int = max(30, int(40 * scale_y))

    # ==========================================================================
    # Row/List layouts
    # ==========================================================================
    row_height_sm: int = max(20, int(28 * scale_y))   # For lists (blocked, clients)
    row_height_md: int = max(28, int(38 * scale_y))   # For settings
    row_start_y: int = max(30, int(40 * scale_y))     # Y position where rows start
    row_padding: int = padding_sm                      # Vertical padding within rows

    # Text positioning within rows
    rank_x: int = margin_md                            # Rank number position
    content_x: int = max(35, int(50 * scale_x))       # Main content start position

    # ==========================================================================
    # Box layouts (info boxes, stats)
    # ==========================================================================
    box_margin: int = int(SCREEN_WIDTH * 0.03)        # Margin around boxes
    box_width: int = int((SCREEN_WIDTH - box_margin * 3) / 2)  # Two-column width
    box_right_x: int = box_margin + box_width + box_margin     # Right column X

    box_padding_x: int = margin_sm                    # Horizontal padding inside boxes
    box_padding_y: int = padding_sm                   # Vertical padding inside boxes
    box_text_offset: int = max(20, int(28 * scale_y)) # Offset for second line in box

    # ==========================================================================
    # Bar elements (progress bars, graphs)
    # ==========================================================================
    bar_height_sm: int = max(10, int(12 * scale_y))   # Small bars (in lists)
    bar_height_md: int = max(18, int(25 * scale_y))   # Medium bars
    bar_height_lg: int = max(45, int(60 * scale_y))   # Large bars (CPU/RAM)

    # ==========================================================================
    # Right-side elements (counts, bars in lists)
    # ==========================================================================
    count_x: int = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.25)      # Count text position
    bar_x: int = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.15)        # Small bar position
    bar_max_width: int = int(SCREEN_WIDTH * 0.125)              # Max width for list bars

    # ==========================================================================
    # Settings screen specific
    # ==========================================================================
    arrow_left_x: int = int(SCREEN_WIDTH * 0.56)
    arrow_right_x: int = SCREEN_WIDTH - int(SCREEN_WIDTH * 0.0625)
    value_x: int = int(SCREEN_WIDTH * 0.60)

    # Arrow tap zones
    arrow_tap_left_start: int = int(SCREEN_WIDTH * 0.54)
    arrow_tap_left_end: int = int(SCREEN_WIDTH * 0.62)
    arrow_tap_right_start: int = SCREEN_WIDTH - 50

    # Arrow dimensions
    arrow_width: int = max(8, int(10 * scale_x))
    arrow_half_height: int = max(5, int(7 * scale_y))

    # ==========================================================================
    # Graph screen specific
    # ==========================================================================
    graph_margin: int = max(30, int(40 * scale_x))
    graph_x: int = graph_margin
    graph_y: int = max(30, int(40 * scale_y))
    graph_width: int = SCREEN_WIDTH - max(45, int(60 * scale_x))
    graph_height: int = SCREEN_HEIGHT - max(70, int(90 * scale_y))

    legend_y: int = SCREEN_HEIGHT - max(30, int(40 * scale_y))
    legend_box_size: int = max(8, int(10 * scale_min))
    legend_spacing: int = margin_md

    # ==========================================================================
    # Text truncation (characters, not pixels)
    # ==========================================================================
    @staticmethod
    def max_chars_for_width(available_width: int, char_width: int = 8) -> int:
        """Calculate max characters that fit in given width"""
        return max(10, available_width // char_width)

    # Pre-calculated max chars for common uses
    max_domain_chars: int = max(10, int(SCREEN_WIDTH / 12))
    max_client_chars: int = max(10, int(SCREEN_WIDTH / 12))

    # ==========================================================================
    # Screen indicator dots
    # ==========================================================================
    indicator_y: int = SCREEN_HEIGHT - margin_sm
    indicator_size: int = max(4, int(6 * scale_min))
    indicator_spacing: int = max(8, int(12 * scale_x))
