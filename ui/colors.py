"""Color definitions for the dashboard - uses theme system"""

import os

from .themes import get_theme

# Module-level color storage
_colors = {}


def _init_colors() -> None:
    """Initialize colors from current theme"""
    global _colors
    theme = get_theme()
    _colors = theme.colors.copy()
    _colors["_theme_name"] = theme.name
    _colors["_style"] = theme.style


def reload_theme(name: str | None = None) -> None:
    """Reload colors from a new theme"""
    global _colors
    if name is not None:
        os.environ["CUTIE_THEME"] = name
    theme = get_theme(name)
    _colors = theme.colors.copy()
    _colors["_theme_name"] = theme.name
    _colors["_style"] = theme.style


def get_current_theme_name() -> str:
    """Get the name of the currently loaded theme"""
    current_theme_name: str | None = _colors.get("_theme_name")
    if current_theme_name is None:
        return "default"
    return current_theme_name


def get_style() -> str:
    """Get the visual style of the current theme"""
    style: str | None = _colors.get("_style")
    if style is None:
        return "pixel"
    return style


def GLOW_PRIMARY() -> tuple[int, int, int]:
    glow_primary: tuple[int, int, int] | None = _colors.get("GLOW_PRIMARY")
    if glow_primary is None:
        primary: tuple[int, int, int] = _colors.get("PRIMARY", (255, 255, 255))
        return primary
    return glow_primary


def GLOW_SECONDARY() -> tuple[int, int, int]:
    glow_secondary: tuple[int, int, int] | None = _colors.get("GLOW_SECONDARY")
    if glow_secondary is None:
        secondary: tuple[int, int, int] = _colors.get("SECONDARY", (200, 200, 200))
        return secondary
    return glow_secondary


# Initialize on first import
_init_colors()


# Color accessor functions - these always return current theme colors
def BLACK() -> tuple[int, int, int]:
    black: tuple[int, int, int] = _colors["BLACK"]
    return black


def WHITE() -> tuple[int, int, int]:
    white: tuple[int, int, int] = _colors["WHITE"]
    return white


def GRAY() -> tuple[int, int, int]:
    gray: tuple[int, int, int] = _colors["GRAY"]
    return gray


def DARK_GRAY() -> tuple[int, int, int]:
    dark_gray: tuple[int, int, int] = _colors["DARK_GRAY"]
    return dark_gray


def DARKER_GRAY() -> tuple[int, int, int]:
    darker_gray: tuple[int, int, int] = _colors["DARKER_GRAY"]
    return darker_gray


def GREEN() -> tuple[int, int, int]:
    green: tuple[int, int, int] = _colors["GREEN"]
    return green


def DARK_GREEN() -> tuple[int, int, int]:
    dark_green: tuple[int, int, int] = _colors["DARK_GREEN"]
    return dark_green


def RED() -> tuple[int, int, int]:
    red: tuple[int, int, int] = _colors["RED"]
    return red


def ORANGE() -> tuple[int, int, int]:
    orange: tuple[int, int, int] = _colors["ORANGE"]
    return orange


def YELLOW() -> tuple[int, int, int]:
    yellow: tuple[int, int, int] = _colors["YELLOW"]
    return yellow


def CYAN() -> tuple[int, int, int]:
    cyan: tuple[int, int, int] = _colors["CYAN"]
    return cyan


def MAGENTA() -> tuple[int, int, int]:
    magenta: tuple[int, int, int] = _colors["MAGENTA"]
    return magenta


def PURPLE() -> tuple[int, int, int]:
    purple: tuple[int, int, int] = _colors["PURPLE"]
    return purple


# Pi-hole brand colors (static, not themed)
PIHOLE_GREEN = (76, 175, 80)
PIHOLE_RED = (244, 67, 54)
