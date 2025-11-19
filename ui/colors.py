"""Color definitions for the dashboard - uses theme system"""

import os
from .themes import get_theme

# Module-level color storage
_colors = {}


def _init_colors():
    """Initialize colors from current theme"""
    global _colors
    theme = get_theme()
    _colors = theme.colors.copy()
    _colors["_theme_name"] = theme.name
    _colors["_use_glow"] = theme.use_glow


def reload_theme(name: str = None) -> None:
    """Reload colors from a new theme"""
    global _colors
    if name:
        os.environ["CUTIE_THEME"] = name
    theme = get_theme(name)
    _colors = theme.colors.copy()
    _colors["_theme_name"] = theme.name
    _colors["_use_glow"] = theme.use_glow


def get_current_theme_name() -> str:
    """Get the name of the currently loaded theme"""
    return _colors.get("_theme_name", "default")


def use_glow() -> bool:
    """Check if current theme uses glow effects"""
    return _colors.get("_use_glow", False)


def GLOW_PRIMARY():
    return _colors.get("GLOW_PRIMARY", _colors.get("PRIMARY", (255, 255, 255)))


def GLOW_SECONDARY():
    return _colors.get("GLOW_SECONDARY", _colors.get("SECONDARY", (200, 200, 200)))


# Initialize on first import
_init_colors()


# Color accessor functions - these always return current theme colors
def BLACK():
    return _colors["BLACK"]


def WHITE():
    return _colors["WHITE"]


def GRAY():
    return _colors["GRAY"]


def DARK_GRAY():
    return _colors["DARK_GRAY"]


def DARKER_GRAY():
    return _colors["DARKER_GRAY"]


def GREEN():
    return _colors["GREEN"]


def DARK_GREEN():
    return _colors["DARK_GREEN"]


def RED():
    return _colors["RED"]


def ORANGE():
    return _colors["ORANGE"]


def YELLOW():
    return _colors["YELLOW"]


def CYAN():
    return _colors["CYAN"]


def MAGENTA():
    return _colors["MAGENTA"]


def PURPLE():
    return _colors["PURPLE"]


# Pi-hole brand colors (static, not themed)
PIHOLE_GREEN = (76, 175, 80)
PIHOLE_RED = (244, 67, 54)
