# Vulture whitelist - functions/variables that appear unused but are actually used

# BaseScreen methods called dynamically by screen manager
from screens.base import BaseScreen

BaseScreen.update
BaseScreen.draw
BaseScreen.handle_tap

# Theme attributes accessed via __getattr__
from ui.themes import Theme  # noqa: E402

Theme.name
Theme.colors
Theme.style

# Screen classes instantiated dynamically
from screens.stats import StatsScreen  # noqa: E402
from screens.system import SystemScreen  # noqa: E402
from screens.graph import GraphScreen  # noqa: E402
from screens.blocked import BlockedScreen  # noqa: E402
from screens.clients import ClientsScreen  # noqa: E402
from screens.settings import SettingsScreen  # noqa: E402

StatsScreen
SystemScreen
GraphScreen
BlockedScreen
ClientsScreen
SettingsScreen

# Color functions called dynamically based on theme
from ui import colors  # noqa: E402

colors.GLOW_PRIMARY
colors.GLOW_SECONDARY
colors.get_style

# Config values used by other modules
from config import VERSION  # noqa: E402

VERSION
