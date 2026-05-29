# BuddyAI Base Bot
# All category bots inherit from this class to ensure a consistent interface
# with the Buddy central AI system and the Government Contract & Grant Bot format.

from BuddyAI.navigation import NavigationMixin
from BuddyAI.settings import BotSettings


class BaseBot(NavigationMixin):
    """Base class for all Dreamcobots category bots.

    Every concrete bot must inherit from this class so that Buddy can manage
    them uniformly regardless of category (OOH Occupational, Mobile App,
    Business / Industry Classification).

    All bots automatically receive the full set of 25 universal navigation
    buttons (via :class:`~BuddyAI.navigation.NavigationMixin`) and a per-bot
    settings store with custom-button support (via
    :class:`~BuddyAI.settings.BotSettings`).

    Subclasses should override :meth:`start` and :meth:`run` and are
    expected to provide 100 features, 100 functions, and 100 tools as
    individual methods named ``feature_NNN_<name>``, ``function_NNN_<name>``,
    and ``tool_NNN_<name>`` respectively.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = ""
        self.buddy = None
        self.settings = BotSettings(bot_name=self.name)

    # ------------------------------------------------------------------
    # Buddy integration
    # ------------------------------------------------------------------

    def connect_to_buddy(self, buddy):
        """Register this bot with the Buddy central AI."""
        self.buddy = buddy

    def send_to_buddy(self, message: str):
        """Forward a message to Buddy if connected."""
        if self.buddy:
            return self.buddy.receive(self.name, message)
        return None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Start the bot.  Override in each subclass."""
        print(f"{self.name} is starting...")

    def run(self):
        """Run the bot.  Override in each subclass."""
        self.start()

    # ------------------------------------------------------------------
    # Introspection helpers used by Buddy
    # ------------------------------------------------------------------

    def list_features(self):
        """Return names of all feature methods on this bot."""
        return [m for m in dir(self) if m.startswith("feature_")]

    def list_functions(self):
        """Return names of all function methods on this bot."""
        return [m for m in dir(self) if m.startswith("function_")]

    def list_tools(self):
        """Return names of all tool methods on this bot."""
        return [m for m in dir(self) if m.startswith("tool_")]

    def capabilities_summary(self):
        """Return a dict summarising how many features / functions / tools exist."""
        return {
            "bot": self.name,
            "features": len(self.list_features()),
            "functions": len(self.list_functions()),
            "tools": len(self.list_tools()),
            "nav_buttons": len(self.nav_buttons()),
            "custom_buttons": len(self.settings.list_custom_buttons()),
        }
