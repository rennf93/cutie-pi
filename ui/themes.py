"""Theme system for Cutie-Pi dashboard"""

import os

from utils.logger import logger


class Theme:
    """Theme color definitions"""

    # Available styles: pixel, glow, dashed, double, thick, terminal, inverted
    def __init__(self, name: str, colors: dict, style: str = "pixel") -> None:
        self.name = name
        self.colors = colors
        self.style = style  # Visual style for borders and bars

    def __getattr__(self, name: str) -> tuple[int, int, int]:
        if name in self.colors:
            color: tuple[int, int, int] = self.colors[name]
            return color
        raise AttributeError(f"Theme has no color '{name}'")


# Define available themes
THEMES = {
    "default": Theme(
        "default",
        {
            # Basic colors
            "BLACK": (0, 0, 0),
            "WHITE": (255, 255, 255),
            "GRAY": (100, 100, 100),
            "DARK_GRAY": (40, 40, 40),
            "DARKER_GRAY": (30, 30, 30),
            # Theme colors
            "PRIMARY": (0, 255, 0),  # Green
            "SECONDARY": (0, 255, 255),  # Cyan
            "ACCENT": (255, 165, 0),  # Orange
            "SUCCESS": (0, 255, 0),  # Green
            "WARNING": (255, 255, 0),  # Yellow
            "ERROR": (255, 50, 50),  # Red
            "INFO": (180, 100, 255),  # Purple
            # Specific colors
            "GREEN": (0, 255, 0),
            "DARK_GREEN": (0, 180, 0),
            "RED": (255, 50, 50),
            "ORANGE": (255, 165, 0),
            "YELLOW": (255, 255, 0),
            "CYAN": (0, 255, 255),
            "MAGENTA": (255, 0, 255),
            "PURPLE": (180, 100, 255),
        },
    ),
    "monochrome": Theme(
        "monochrome",
        {
            # Basic colors
            "BLACK": (0, 0, 0),
            "WHITE": (255, 255, 255),
            "GRAY": (100, 100, 100),
            "DARK_GRAY": (40, 40, 40),
            "DARKER_GRAY": (30, 30, 30),
            # Theme colors - all grayscale
            "PRIMARY": (255, 255, 255),
            "SECONDARY": (200, 200, 200),
            "ACCENT": (180, 180, 180),
            "SUCCESS": (255, 255, 255),
            "WARNING": (200, 200, 200),
            "ERROR": (150, 150, 150),
            "INFO": (180, 180, 180),
            # Specific colors
            "GREEN": (255, 255, 255),
            "DARK_GREEN": (200, 200, 200),
            "RED": (150, 150, 150),
            "ORANGE": (180, 180, 180),
            "YELLOW": (220, 220, 220),
            "CYAN": (200, 200, 200),
            "MAGENTA": (180, 180, 180),
            "PURPLE": (160, 160, 160),
        },
    ),
    "neon": Theme(
        "neon",
        {
            # Vibrant neon with glow effects
            "BLACK": (5, 0, 10),  # Deep purple-black
            "WHITE": (255, 50, 255),  # Bright magenta text
            "GRAY": (150, 50, 150),
            "DARK_GRAY": (60, 20, 60),
            "DARKER_GRAY": (40, 10, 40),
            # Theme colors - HOT PINK/MAGENTA dominant
            "PRIMARY": (255, 0, 255),  # Hot magenta
            "SECONDARY": (255, 100, 255),  # Light magenta
            "ACCENT": (255, 0, 150),  # Pink
            "SUCCESS": (255, 0, 255),
            "WARNING": (255, 100, 200),
            "ERROR": (255, 0, 100),
            "INFO": (200, 0, 255),
            # Specific colors - all pink/magenta spectrum
            "GREEN": (255, 0, 255),
            "DARK_GREEN": (200, 0, 200),
            "RED": (255, 0, 100),
            "ORANGE": (255, 50, 200),
            "YELLOW": (255, 150, 255),
            "CYAN": (255, 100, 255),
            "MAGENTA": (255, 0, 255),
            "PURPLE": (200, 0, 255),
            # Glow colors
            "GLOW_PRIMARY": (255, 100, 255),
            "GLOW_SECONDARY": (255, 150, 255),
        },
        style="glow",
    ),
    "ocean": Theme(
        "ocean",
        {
            # Pure blue/cyan with dashed wave feel
            #   Bright: (0, 150, 255)
            #   Medium: (0, 100, 200)
            #   Dark: (0, 70, 150)
            #   Darker: (0, 40, 100)
            # Basic colors
            "BLACK": (0, 5, 15),  # Deep ocean black
            "WHITE": (0, 180, 255),  # Bright blue for main text
            "GRAY": (0, 80, 160),  # Dark blue for secondary
            "DARK_GRAY": (0, 40, 100),
            "DARKER_GRAY": (0, 25, 70),
            # Theme colors
            "PRIMARY": (0, 180, 255),  # Bright blue
            "SECONDARY": (0, 120, 220),  # Medium blue
            "ACCENT": (0, 200, 255),  # Cyan accent
            "SUCCESS": (0, 200, 255),
            "WARNING": (0, 120, 220),
            "ERROR": (0, 80, 160),
            "INFO": (0, 140, 230),
            # Specific colors - all pure blue spectrum
            "GREEN": (0, 180, 255),  # Bright
            "DARK_GREEN": (0, 120, 220),  # Medium
            "RED": (0, 80, 160),  # Dark
            "ORANGE": (0, 120, 220),  # Medium
            "YELLOW": (0, 180, 255),  # Bright
            "CYAN": (0, 140, 230),  # Medium
            "MAGENTA": (0, 120, 220),  # Medium
            "PURPLE": (0, 80, 160),  # Dark
        },
        style="dashed",
    ),
    "sunset": Theme(
        "sunset",
        {
            # Warm sunset with thick bold borders
            #   Bright: (255, 150, 0)
            #   Medium: (200, 100, 0)
            #   Dark: (150, 70, 0)
            #   Darker: (100, 50, 0)
            # Basic colors
            "BLACK": (10, 5, 0),  # Warm black
            "WHITE": (255, 180, 50),  # Golden orange for main text
            "GRAY": (160, 90, 20),  # Darker orange for secondary
            "DARK_GRAY": (100, 50, 0),
            "DARKER_GRAY": (60, 30, 0),
            # Theme colors
            "PRIMARY": (255, 180, 50),  # Bright golden
            "SECONDARY": (220, 120, 20),  # Medium orange
            "ACCENT": (255, 200, 100),  # Light golden
            "SUCCESS": (255, 200, 100),
            "WARNING": (220, 120, 20),
            "ERROR": (160, 90, 20),
            "INFO": (240, 150, 30),
            # Specific colors - all pure orange spectrum
            "GREEN": (255, 180, 50),  # Bright
            "DARK_GREEN": (220, 120, 20),  # Medium
            "RED": (160, 90, 20),  # Dark
            "ORANGE": (220, 120, 20),  # Medium
            "YELLOW": (255, 200, 100),  # Bright
            "CYAN": (240, 150, 30),  # Medium
            "MAGENTA": (220, 120, 20),  # Medium
            "PURPLE": (160, 90, 20),  # Dark
        },
        style="thick",
    ),
    "matrix": Theme(
        "matrix",
        {
            # Digital rain with terminal aesthetic
            #   Bright: (0, 255, 0)
            #   Medium: (0, 180, 0)
            #   Dark: (0, 120, 0)
            #   Darker: (0, 60, 0)
            # Basic colors
            "BLACK": (0, 5, 0),  # Very dark green-black
            "WHITE": (0, 255, 70),  # Bright matrix green for main text
            "GRAY": (0, 120, 30),  # Dark green for secondary
            "DARK_GRAY": (0, 60, 15),
            "DARKER_GRAY": (0, 35, 8),
            # Theme colors
            "PRIMARY": (0, 255, 70),  # Bright matrix green
            "SECONDARY": (0, 180, 50),  # Medium green
            "ACCENT": (100, 255, 100),  # Light green accent
            "SUCCESS": (100, 255, 100),
            "WARNING": (0, 180, 50),
            "ERROR": (0, 120, 30),
            "INFO": (50, 220, 60),
            # Specific colors - all pure green spectrum
            "GREEN": (0, 255, 70),  # Bright
            "DARK_GREEN": (0, 180, 50),  # Medium
            "RED": (0, 120, 30),  # Dark
            "ORANGE": (0, 180, 50),  # Medium
            "YELLOW": (100, 255, 100),  # Bright
            "CYAN": (50, 220, 60),  # Medium
            "MAGENTA": (0, 180, 50),  # Medium
            "PURPLE": (0, 120, 30),  # Dark
        },
        style="terminal",
    ),
    "cyberpunk": Theme(
        "cyberpunk",
        {
            # High contrast with double-line tech borders
            # Basic colors
            "BLACK": (5, 0, 10),  # Deep purple-black
            "WHITE": (255, 255, 255),
            "GRAY": (100, 80, 120),
            "DARK_GRAY": (40, 30, 50),
            "DARKER_GRAY": (25, 20, 35),
            # Theme colors - cyberpunk pink/cyan
            "PRIMARY": (255, 0, 150),  # Hot pink
            "SECONDARY": (0, 255, 255),  # Cyan
            "ACCENT": (255, 255, 0),  # Yellow
            "SUCCESS": (0, 255, 255),
            "WARNING": (255, 255, 0),
            "ERROR": (255, 0, 50),
            "INFO": (150, 0, 255),
            # Specific colors
            "GREEN": (0, 255, 150),
            "DARK_GREEN": (0, 200, 100),
            "RED": (255, 0, 50),
            "ORANGE": (255, 150, 0),
            "YELLOW": (255, 255, 0),
            "CYAN": (0, 255, 255),
            "MAGENTA": (255, 0, 150),
            "PURPLE": (150, 0, 255),
        },
        style="double",
    ),
    "666": Theme(
        "666",
        {
            # Ominous hellfire with inverted/inset borders
            #   Bright: (220, 0, 0),
            #   Medium: (160, 0, 0),
            #   Dark: (100, 0, 0),
            #   Darker: (60, 0, 0)
            # Basic colors
            "BLACK": (10, 0, 0),  # Deep blood red black
            "WHITE": (220, 0, 0),  # Bright red for main text
            "GRAY": (100, 0, 0),  # Dark red for secondary
            "DARK_GRAY": (60, 0, 0),
            "DARKER_GRAY": (35, 0, 0),
            # Theme colors
            "PRIMARY": (220, 0, 0),  # Bright red
            "SECONDARY": (160, 0, 0),  # Medium red
            "ACCENT": (255, 0, 0),  # Pure bright red accent
            "SUCCESS": (255, 0, 0),
            "WARNING": (160, 0, 0),
            "ERROR": (100, 0, 0),
            "INFO": (180, 0, 0),
            # Specific colors - all pure red spectrum
            "GREEN": (220, 0, 0),  # Bright
            "DARK_GREEN": (160, 0, 0),  # Medium
            "RED": (100, 0, 0),  # Dark
            "ORANGE": (160, 0, 0),  # Medium
            "YELLOW": (255, 0, 0),  # Bright
            "CYAN": (180, 0, 0),  # Medium
            "MAGENTA": (160, 0, 0),  # Medium
            "PURPLE": (100, 0, 0),  # Dark
        },
        style="inverted",
    ),
    "arcade": Theme(
        "arcade",
        {
            # Retrowave/arcade style with glows
            # Purple borders, orange/yellow text, pink accents
            # Basic colors
            "BLACK": (10, 5, 20),  # Deep purple-black
            "WHITE": (255, 200, 50),  # Golden yellow for text
            "GRAY": (100, 80, 120),  # Muted purple-gray
            "DARK_GRAY": (40, 30, 60),  # Dark purple
            "DARKER_GRAY": (25, 20, 40),  # Darker purple
            # Theme colors
            "PRIMARY": (150, 50, 255),  # Purple (borders)
            "SECONDARY": (255, 100, 200),  # Pink
            "ACCENT": (255, 200, 50),  # Golden yellow
            "SUCCESS": (100, 255, 150),  # Mint green
            "WARNING": (255, 150, 50),  # Orange
            "ERROR": (255, 50, 100),  # Hot pink
            "INFO": (100, 200, 255),  # Cyan
            # Specific colors
            "GREEN": (100, 255, 150),  # Mint
            "DARK_GREEN": (50, 200, 100),  # Darker mint
            "RED": (255, 50, 100),  # Hot pink
            "ORANGE": (255, 150, 50),  # Orange
            "YELLOW": (255, 200, 50),  # Golden
            "CYAN": (100, 200, 255),  # Cyan
            "MAGENTA": (255, 100, 200),  # Pink
            "PURPLE": (150, 50, 255),  # Purple
            # Glow colors (for arcade effects)
            "GLOW_PRIMARY": (200, 100, 255),  # Light purple glow
            "GLOW_SECONDARY": (255, 150, 220),  # Light pink glow
        },
        style="glow",
    ),
}


def get_theme(name: str | None = None) -> Theme:
    """Get theme by name, defaults to CUTIE_THEME env var or 'default'"""
    if name is None:
        name = os.environ.get("CUTIE_THEME", "default")

    if name not in THEMES:
        logger.warning(f"Unknown theme '{name}', using default")
        name = "default"

    return THEMES[name]


def list_themes() -> list[str]:
    """Return list of available theme names"""
    return list(THEMES.keys())
