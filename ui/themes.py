"""Theme system for Cutie-Pi dashboard"""

import os


class Theme:
    """Theme color definitions"""

    def __init__(self, name: str, colors: dict) -> None:
        self.name = name
        self.colors = colors

    def __getattr__(self, name: str):
        if name in self.colors:
            return self.colors[name]
        raise AttributeError(f"Theme has no color '{name}'")


# Define available themes
THEMES = {
    "default": Theme("default", {
        # Basic colors
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "GRAY": (100, 100, 100),
        "DARK_GRAY": (40, 40, 40),
        "DARKER_GRAY": (30, 30, 30),
        # Theme colors
        "PRIMARY": (0, 255, 0),       # Green
        "SECONDARY": (0, 255, 255),   # Cyan
        "ACCENT": (255, 165, 0),      # Orange
        "SUCCESS": (0, 255, 0),       # Green
        "WARNING": (255, 255, 0),     # Yellow
        "ERROR": (255, 50, 50),       # Red
        "INFO": (180, 100, 255),      # Purple
        # Specific colors
        "GREEN": (0, 255, 0),
        "DARK_GREEN": (0, 180, 0),
        "RED": (255, 50, 50),
        "ORANGE": (255, 165, 0),
        "YELLOW": (255, 255, 0),
        "CYAN": (0, 255, 255),
        "MAGENTA": (255, 0, 255),
        "PURPLE": (180, 100, 255),
    }),

    "monochrome": Theme("monochrome", {
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
    }),

    "neon": Theme("neon", {
        # Basic colors
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "GRAY": (100, 100, 100),
        "DARK_GRAY": (40, 40, 40),
        "DARKER_GRAY": (30, 30, 30),
        # Theme colors - HOT PINK/MAGENTA dominant
        "PRIMARY": (255, 0, 255),     # Hot magenta
        "SECONDARY": (255, 100, 255), # Light magenta
        "ACCENT": (255, 0, 150),      # Pink
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
    }),

    "ocean": Theme("ocean", {
        # Pure blue/cyan only
        # Bright: (0, 150, 255), Medium: (0, 100, 200), Dark: (0, 70, 150), Darker: (0, 40, 100)

        # Basic colors
        "BLACK": (0, 0, 0),
        "WHITE": (0, 150, 255),       # Bright blue for main text
        "GRAY": (0, 70, 150),         # Dark blue for secondary
        "DARK_GRAY": (0, 40, 100),
        "DARKER_GRAY": (0, 30, 80),
        # Theme colors
        "PRIMARY": (0, 150, 255),     # Bright blue
        "SECONDARY": (0, 100, 200),   # Medium blue
        "ACCENT": (0, 150, 255),
        "SUCCESS": (0, 150, 255),
        "WARNING": (0, 100, 200),
        "ERROR": (0, 70, 150),
        "INFO": (0, 100, 200),
        # Specific colors - all pure blue spectrum
        "GREEN": (0, 150, 255),       # Bright
        "DARK_GREEN": (0, 100, 200),  # Medium
        "RED": (0, 70, 150),          # Dark
        "ORANGE": (0, 100, 200),      # Medium
        "YELLOW": (0, 150, 255),      # Bright
        "CYAN": (0, 100, 200),        # Medium
        "MAGENTA": (0, 100, 200),     # Medium
        "PURPLE": (0, 70, 150),       # Dark
    }),

    "sunset": Theme("sunset", {
        # Pure orange/amber only
        # Bright: (255, 150, 0), Medium: (200, 100, 0), Dark: (150, 70, 0), Darker: (100, 50, 0)

        # Basic colors
        "BLACK": (0, 0, 0),
        "WHITE": (255, 150, 0),       # Bright orange for main text
        "GRAY": (150, 70, 0),         # Dark orange for secondary
        "DARK_GRAY": (100, 50, 0),
        "DARKER_GRAY": (70, 35, 0),
        # Theme colors
        "PRIMARY": (255, 150, 0),     # Bright orange
        "SECONDARY": (200, 100, 0),   # Medium orange
        "ACCENT": (255, 150, 0),
        "SUCCESS": (255, 150, 0),
        "WARNING": (200, 100, 0),
        "ERROR": (150, 70, 0),
        "INFO": (200, 100, 0),
        # Specific colors - all pure orange spectrum
        "GREEN": (255, 150, 0),       # Bright
        "DARK_GREEN": (200, 100, 0),  # Medium
        "RED": (150, 70, 0),          # Dark
        "ORANGE": (200, 100, 0),      # Medium
        "YELLOW": (255, 150, 0),      # Bright
        "CYAN": (200, 100, 0),        # Medium
        "MAGENTA": (200, 100, 0),     # Medium
        "PURPLE": (150, 70, 0),       # Dark
    }),

    "matrix": Theme("matrix", {
        # Pure green only - like 666 but green
        # Bright: (0, 200, 0), Medium: (0, 150, 0), Dark: (0, 100, 0), Darker: (0, 60, 0)

        # Basic colors
        "BLACK": (0, 0, 0),
        "WHITE": (0, 200, 0),         # Bright green for main text
        "GRAY": (0, 100, 0),          # Dark green for secondary
        "DARK_GRAY": (0, 60, 0),
        "DARKER_GRAY": (0, 40, 0),
        # Theme colors
        "PRIMARY": (0, 200, 0),       # Bright green
        "SECONDARY": (0, 150, 0),     # Medium green
        "ACCENT": (0, 200, 0),
        "SUCCESS": (0, 200, 0),
        "WARNING": (0, 150, 0),
        "ERROR": (0, 100, 0),
        "INFO": (0, 150, 0),
        # Specific colors - all pure green spectrum
        "GREEN": (0, 200, 0),         # Bright
        "DARK_GREEN": (0, 150, 0),    # Medium
        "RED": (0, 100, 0),           # Dark
        "ORANGE": (0, 150, 0),        # Medium
        "YELLOW": (0, 200, 0),        # Bright
        "CYAN": (0, 150, 0),          # Medium
        "MAGENTA": (0, 150, 0),       # Medium
        "PURPLE": (0, 100, 0),        # Dark
    }),

    "cyberpunk": Theme("cyberpunk", {
        # Basic colors
        "BLACK": (0, 0, 0),
        "WHITE": (255, 255, 255),
        "GRAY": (100, 100, 100),
        "DARK_GRAY": (40, 40, 40),
        "DARKER_GRAY": (30, 30, 30),
        # Theme colors - cyberpunk pink/cyan
        "PRIMARY": (255, 0, 150),     # Hot pink
        "SECONDARY": (0, 255, 255),   # Cyan
        "ACCENT": (255, 255, 0),      # Yellow
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
    }),

    "666": Theme("666", {
        # 4 shades of pure red only - no pink/magenta
        # Bright: (200, 0, 0), Medium: (150, 0, 0), Dark: (100, 0, 0), Darker: (60, 0, 0)

        # Basic colors
        "BLACK": (0, 0, 0),
        "WHITE": (200, 0, 0),         # Bright red for main text
        "GRAY": (100, 0, 0),          # Dark red for secondary
        "DARK_GRAY": (60, 0, 0),
        "DARKER_GRAY": (40, 0, 0),
        # Theme colors
        "PRIMARY": (200, 0, 0),       # Bright red
        "SECONDARY": (150, 0, 0),     # Medium red
        "ACCENT": (200, 0, 0),
        "SUCCESS": (200, 0, 0),
        "WARNING": (150, 0, 0),
        "ERROR": (100, 0, 0),
        "INFO": (150, 0, 0),
        # Specific colors - all pure red spectrum
        "GREEN": (200, 0, 0),         # Bright
        "DARK_GREEN": (150, 0, 0),    # Medium
        "RED": (100, 0, 0),           # Dark
        "ORANGE": (150, 0, 0),        # Medium
        "YELLOW": (200, 0, 0),        # Bright
        "CYAN": (150, 0, 0),          # Medium
        "MAGENTA": (150, 0, 0),       # Medium
        "PURPLE": (100, 0, 0),        # Dark
    }),
}


def get_theme(name: str = None) -> Theme:
    """Get theme by name, defaults to CUTIE_THEME env var or 'default'"""
    if name is None:
        name = os.environ.get("CUTIE_THEME", "default")

    if name not in THEMES:
        print(f"Unknown theme '{name}', using default")
        name = "default"

    return THEMES[name]


def list_themes() -> list[str]:
    """Return list of available theme names"""
    return list(THEMES.keys())
