"""
Global Bot Communication Network (GBN) — Main Module

DreamCo's universal AI-to-AI network that enables standardised communication
between all DreamCo bots and connectivity with external bots/tools via APIs.

Architecture layers
-------------------
1. Universal Bot Protocol (UBP)     — standard message format & validation
2. Messaging Network                — real-time bot-to-bot routing
3. API Gateway                      — external integrations (Slack, Discord, …)
4. Owner Dashboard                  — per-owner monitoring & control
5. Bot Library                      — catalogue of all DreamCo bots
6. Verification System              — trust levels (Basic → Verified → Trusted)
7. Marketplace                      — buy/sell bots and modules

Usage::

    from bots.global_bot_network.global_bot_network import GlobalBotNetwork, Tier

    gbn = GlobalBotNetwork(owner_id="user_123", tier=Tier.PRO)
    gbn.connect_bot("my_finance_bot")
    gbn.send_message("my_finance_bot", "dreamco_bot_2", "Hello!")
    snap = gbn.owner_dashboard.snapshot()

Adheres to the DreamCo bots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.global_bot_network.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_UBP_MESSAGING,
    FEATURE_BOT_REGISTRY,
    FEATURE_BASIC_DASHBOARD,
    FEATURE_REALTIME_DASHBOARD,
    FEATURE_EARNINGS_TRACKER,
    FEATURE_KILL_SWITCH,
    FEATURE_ACTIVITY_LOGS,
    FEATURE_RATE_LIMITING,
    FEATURE_PERMISSIONS,
    FEATURE_BASIC_VERIFICATION,
    FEATURE_ADVANCED_VERIFICATION,
    FEATURE_TRUSTED_BOT_STATUS,
    FEATURE_SLACK_INTEGRATION,
    FEATURE_DISCORD_INTEGRATION,
    FEATURE_OPENAI_INTEGRATION,
    FEATURE_TRELLO_INTEGRATION,
    FEATURE_NOTION_INTEGRATION,
    FEATURE_FULL_API_GATEWAY,
    FEATURE_MARKETPLACE,
    FEATURE_MARKETPLACE_SELL,
    FEATURE_BOT_SUBSCRIPTIONS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
)
from bots.global_bot_network.universal_bot_protocol import (
    UBPMessage,
    MessageType,
    Permission,
    UBPError,
    UBPValidationError,
    UBPPermissionError,
    BROADCAST_TARGET,
    create_message,
    create_ping,
    create_broadcast,
    validate_message,
)
from bots.global_bot_network.messaging_network import (
    MessagingNetwork,
    RateLimitExceeded,
    BotNotConnected,
    DeliveryReceipt,
)
from bots.global_bot_network.api_gateway import (
    APIGateway,
    IntegrationType,
    GatewayResponse,
    IntegrationNotFound,
    IntegrationDisabled,
)
from bots.global_bot_network.owner_dashboard import (
    OwnerDashboard,
    BotNotOwned,
    BotAlreadyKilled,
)
from bots.global_bot_network.bot_library import (
    BotLibrary,
    BotEntry,
    BotCategory,
    BotStatus,
    BotNotFound,
)
from bots.global_bot_network.verification_system import (
    VerificationSystem,
    VerificationLevel,
    VerificationMethod,
    VerificationError,
    BotNotRegistered,
)
from bots.global_bot_network.marketplace import (
    BotMarketplace,
    ListingType,
    ListingStatus,
    Purchase,
    MarketplaceError,
    ListingNotFound,
)
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GBNError(Exception):
    """Base exception for the Global Bot Communication Network."""


class GBNTierError(GBNError):
    """Raised when a feature is not available on the current tier."""


class GBNBotLimitError(GBNError):
    """Raised when the bot limit for the current tier is exceeded."""


# ---------------------------------------------------------------------------
# Global Bot Communication Network
# ---------------------------------------------------------------------------

class GlobalBotNetwork:
    """
    Top-level orchestrator for the DreamCo Global Bot Communication Network.

    Parameters
    ----------
    owner_id : str
        Identifier of the owner/user operating this network instance.
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).

    Attributes
    ----------
    messaging_network : MessagingNetwork
        Routes UBP messages between connected bots.
    api_gateway : APIGateway
        Connects to external platforms (Slack, Discord, OpenAI, …).
    owner_dashboard : OwnerDashboard
        Live dashboard for monitoring bots, earnings, and activity.
    bot_library : BotLibrary
        Catalogue of all registered DreamCo bots.
    verification_system : VerificationSystem
        Manages trust levels for bots on the network.
    marketplace : BotMarketplace
        Bot and module marketplace.
    """

    def __init__(self, owner_id: str, tier: Tier = Tier.FREE) -> None:
        self.owner_id = owner_id
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        # GLOBAL AI SOURCES FLOW — mandatory pipeline
        self.flow = GlobalAISourcesFlow(bot_name="GlobalBotNetwork")

        # Subsystems
        self.messaging_network = MessagingNetwork(
            max_messages_per_minute=self.config.max_messages_per_minute,
            enforce_permissions=self.config.has_feature(FEATURE_PERMISSIONS),
        )
        self.api_gateway = APIGateway()
        self.owner_dashboard = OwnerDashboard(owner_id=owner_id)
        self.bot_library = BotLibrary()
        self.verification_system = VerificationSystem()
        self.marketplace = BotMarketplace()

        # Load all DreamCo bots into the library
        self.bot_library.populate_dreamco_bots()

        # Register default API integrations available on this tier
        self._register_tier_integrations()

        # Track connected bots (owner's bots)
        self._connected_bots: list[str] = []

    # ------------------------------------------------------------------
    # Tier helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise GBNTierError(
                f"Feature '{feature}' is not available on the '{self.tier.value}' tier. "
                f"Upgrade to unlock it."
            )

    def _check_bot_limit(self) -> None:
        if (
            self.config.max_bots is not None
            and len(self._connected_bots) >= self.config.max_bots
        ):
            raise GBNBotLimitError(
                f"Bot limit of {self.config.max_bots} reached on the "
                f"'{self.tier.value}' tier. Upgrade to add more bots."
            )

    def _register_tier_integrations(self) -> None:
        """Register API integrations available on the current tier."""
        if self.config.has_feature(FEATURE_SLACK_INTEGRATION):
            self.api_gateway.register("Slack", IntegrationType.SLACK)
        if self.config.has_feature(FEATURE_DISCORD_INTEGRATION):
            self.api_gateway.register("Discord", IntegrationType.DISCORD)
        if self.config.has_feature(FEATURE_OPENAI_INTEGRATION):
            self.api_gateway.register("OpenAI", IntegrationType.OPENAI)
        if self.config.has_feature(FEATURE_TRELLO_INTEGRATION):
            self.api_gateway.register("Trello", IntegrationType.TRELLO)
        if self.config.has_feature(FEATURE_NOTION_INTEGRATION):
            self.api_gateway.register("Notion", IntegrationType.NOTION)

    # ------------------------------------------------------------------
    # Bot connection
    # ------------------------------------------------------------------

    def connect_bot(
        self,
        bot_id: str,
        display_name: str = "",
        callback: Optional[Callable[[UBPMessage], None]] = None,
    ) -> None:
        """
        Connect a bot to the GBN.

        Registers the bot in the messaging network, owner dashboard, and
        verification system.

        Parameters
        ----------
        bot_id : str
            Unique bot identifier.
        display_name : str, optional
            Human-readable label.
        callback : callable, optional
            Called with each :class:`UBPMessage` delivered to this bot.

        Raises
        ------
        GBNBotLimitError
            If the tier's bot limit has been reached.
        """
        self._require_feature(FEATURE_UBP_MESSAGING)
        self._check_bot_limit()

        self.messaging_network.connect(bot_id, callback)
        self.owner_dashboard.add_bot(bot_id, display_name=display_name)
        self.verification_system.register_bot(bot_id, owner_id=self.owner_id)

        if bot_id not in self._connected_bots:
            self._connected_bots.append(bot_id)

    def disconnect_bot(self, bot_id: str) -> None:
        """Disconnect a bot from the GBN."""
        self.messaging_network.disconnect(bot_id)
        if bot_id in self._connected_bots:
            self._connected_bots.remove(bot_id)

    def list_connected_bots(self) -> list[str]:
        """Return all currently connected bot IDs."""
        return list(self._connected_bots)

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    def send_message(
        self,
        from_bot: str,
        to_bot: str,
        message: str,
        *,
        msg_type: MessageType = MessageType.MESSAGE,
        permissions: Optional[list] = None,
        data: Optional[dict] = None,
    ) -> DeliveryReceipt:
        """
        Send a UBP message from one bot to another (or broadcast).

        Parameters
        ----------
        from_bot : str
            Sending bot ID.
        to_bot : str
            Receiving bot ID, or ``"broadcast"`` for all bots.
        message : str
            Text payload.
        msg_type : MessageType, optional
            Defaults to MESSAGE.
        permissions : list, optional
            Permission flags to attach.
        data : dict, optional
            Structured data payload.

        Returns
        -------
        DeliveryReceipt
        """
        self._require_feature(FEATURE_UBP_MESSAGING)
        ubp_msg = create_message(
            from_bot=from_bot,
            to_bot=to_bot,
            message=message,
            msg_type=msg_type,
            permissions=permissions,
            data=data or {},
        )
        receipt = self.messaging_network.send(ubp_msg)

        # Log to dashboard if this is an owner bot
        if from_bot in self._connected_bots:
            self.owner_dashboard.record_chat(
                from_bot, message, direction="sent", peer=to_bot
            )
        if to_bot in self._connected_bots:
            self.owner_dashboard.record_chat(
                to_bot, message, direction="received", peer=from_bot
            )

        return receipt

    def broadcast(self, from_bot: str, message: str, data: Optional[dict] = None) -> DeliveryReceipt:
        """Broadcast a message to all connected bots."""
        self._require_feature(FEATURE_UBP_MESSAGING)
        ubp_msg = create_broadcast(from_bot, message, data=data)
        return self.messaging_network.send(ubp_msg)

    def ping(self, from_bot: str, to_bot: str) -> DeliveryReceipt:
        """Ping a bot and await its auto-pong."""
        self._require_feature(FEATURE_UBP_MESSAGING)
        ubp_msg = create_ping(from_bot, to_bot)
        return self.messaging_network.send(ubp_msg)

    # ------------------------------------------------------------------
    # API Gateway
    # ------------------------------------------------------------------

    def call_integration(
        self,
        integration_name: str,
        action: str,
        payload: Optional[dict] = None,
        bot_id: str = "",
    ) -> GatewayResponse:
        """
        Route an action to an external integration.

        Parameters
        ----------
        integration_name : str
            Name of the integration (e.g. ``"Slack"``).
        action : str
            Integration action (e.g. ``"send_message"``).
        payload : dict, optional
            Action parameters.
        bot_id : str, optional
            Originating bot (for logging).

        Returns
        -------
        GatewayResponse
        """
        return self.api_gateway.route(
            integration_name=integration_name,
            action=action,
            payload=payload or {},
            bot_id=bot_id,
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify_bot(
        self,
        bot_id: str,
        method: VerificationMethod,
        target_level: VerificationLevel,
        admin: bool = False,
    ) -> dict:
        """
        Advance a bot's verification level.

        Raises
        ------
        GBNTierError
            If the tier does not support the requested verification level.
        """
        if target_level in (VerificationLevel.VERIFIED, VerificationLevel.TRUSTED):
            self._require_feature(FEATURE_ADVANCED_VERIFICATION)
        if target_level == VerificationLevel.TRUSTED:
            self._require_feature(FEATURE_TRUSTED_BOT_STATUS)

        record = self.verification_system.verify(
            bot_id, method=method, target_level=target_level, admin=admin
        )
        return record.to_dict()

    def get_verification_level(self, bot_id: str) -> str:
        """Return the current verification level for *bot_id*."""
        return self.verification_system.get_level(bot_id).value

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------

    def kill_bot(self, bot_id: str, reason: str = "Kill switch activated") -> dict:
        """
        Immediately disable *bot_id* via the owner dashboard kill switch.

        Also disconnects the bot from the messaging network.
        """
        self._require_feature(FEATURE_KILL_SWITCH)
        result = self.owner_dashboard.kill_bot(bot_id, reason=reason)
        self.messaging_network.disconnect(bot_id)
        if bot_id in self._connected_bots:
            self._connected_bots.remove(bot_id)
        return result.to_dict()

    def revive_bot(self, bot_id: str) -> dict:
        """Re-enable a killed bot and reconnect it to the network."""
        self._require_feature(FEATURE_KILL_SWITCH)
        result = self.owner_dashboard.revive_bot(bot_id)
        self.messaging_network.connect(bot_id)
        if bot_id not in self._connected_bots:
            self._connected_bots.append(bot_id)
        return result.to_dict()

    # ------------------------------------------------------------------
    # Earnings
    # ------------------------------------------------------------------

    def record_earning(
        self,
        bot_id: str,
        amount_usd: float,
        source: str,
        description: str = "",
    ) -> dict:
        """Record an earnings event for *bot_id*."""
        self._require_feature(FEATURE_EARNINGS_TRACKER)
        record = self.owner_dashboard.record_earning(
            bot_id, amount_usd=amount_usd, source=source, description=description
        )
        return record.to_dict()

    def total_earnings(self, bot_id: Optional[str] = None) -> float:
        """Return total earnings across all bots (or for a single bot)."""
        self._require_feature(FEATURE_EARNINGS_TRACKER)
        return self.owner_dashboard.total_earnings(bot_id)

    # ------------------------------------------------------------------
    # Marketplace
    # ------------------------------------------------------------------

    def create_listing(
        self,
        title: str,
        description: str,
        listing_type: ListingType,
        price_usd: float,
        tags: Optional[list] = None,
    ):
        """Create a marketplace listing (PRO/ENTERPRISE)."""
        self._require_feature(FEATURE_MARKETPLACE_SELL)
        return self.marketplace.create_listing(
            seller_id=self.owner_id,
            title=title,
            description=description,
            listing_type=listing_type,
            price_usd=price_usd,
            tags=tags or [],
        )

    # ------------------------------------------------------------------
    # Bot library
    # ------------------------------------------------------------------

    def get_bot_info(self, bot_id: str) -> dict:
        """Return library metadata for a registered DreamCo bot."""
        return self.bot_library.get_bot(bot_id).to_dict()

    def search_bots(self, query: str) -> list[dict]:
        """Search the bot library."""
        return self.bot_library.search(query)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_dashboard_snapshot(self) -> dict:
        """Return a full real-time dashboard snapshot."""
        self._require_feature(FEATURE_BASIC_DASHBOARD)
        snapshot = self.owner_dashboard.snapshot()
        snapshot["network_stats"] = self.messaging_network.get_stats()
        snapshot["gateway_stats"] = self.api_gateway.get_stats()
        snapshot["library_stats"] = self.bot_library.get_stats()
        snapshot["verification_stats"] = self.verification_system.get_stats()
        snapshot["marketplace_stats"] = self.marketplace.get_stats()
        snapshot["tier"] = self.tier.value
        return snapshot

    # ------------------------------------------------------------------
    # Chat interface (BuddyAI / framework compat)
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Natural-language routing compatible with BuddyAI orchestrator.

        Supports commands such as:
          "status"     → dashboard snapshot
          "list bots"  → connected bots
          "ping <id>"  → ping a bot
          "broadcast"  → broadcast a message
        """
        msg = message.lower().strip()

        if any(k in msg for k in ("status", "dashboard", "overview")):
            return {"response": "gbn", "data": self.get_dashboard_snapshot()}

        if "list bots" in msg:
            return {"response": "gbn", "data": {"bots": self.list_connected_bots()}}

        if msg.startswith("ping"):
            parts = message.strip().split()
            target = parts[1] if len(parts) > 1 else ""
            if target and self.messaging_network.is_connected(target) and self._connected_bots:
                receipt = self.ping(self._connected_bots[0], target)
                return {"response": "gbn", "data": receipt.to_dict()}
            return {"response": "gbn", "message": f"Cannot ping '{target}'."}

        if "broadcast" in msg:
            if self._connected_bots:
                receipt = self.broadcast(self._connected_bots[0], message)
                return {"response": "gbn", "data": receipt.to_dict()}
            return {"response": "gbn", "message": "No bots connected to broadcast from."}

        if "library" in msg or "search" in msg:
            query = message.replace("library", "").replace("search", "").strip()
            results = self.search_bots(query) if query else self.bot_library.list_bots()
            return {"response": "gbn", "data": {"results": results}}

        return {
            "response": "gbn",
            "message": (
                "DreamCo Global Bot Network is online. "
                f"Connected bots: {len(self._connected_bots)}. "
                "Try: 'status', 'list bots', 'broadcast <msg>', 'search <query>'."
            ),
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        return self.chat(payload.get("command", ""))


# ---------------------------------------------------------------------------
# Module-level run helper (pragma: no cover)
# ---------------------------------------------------------------------------

def run() -> None:  # pragma: no cover
    """Quick demo of the Global Bot Communication Network."""
    gbn = GlobalBotNetwork(owner_id="demo_owner", tier=Tier.PRO)
    gbn.connect_bot("finance_bot", display_name="Finance Bot")
    gbn.connect_bot("crypto_bot", display_name="Crypto Bot")

    gbn.send_message("finance_bot", "crypto_bot", "What is the BTC price?")
    gbn.broadcast("finance_bot", "Network is live!")

    gbn.verify_bot(
        "finance_bot",
        method=VerificationMethod.EMAIL,
        target_level=VerificationLevel.BASIC,
    )

    resp = gbn.call_integration("Slack", "send_message", {"text": "GBN is online!"})
    print("Slack response:", resp.result)

    snap = gbn.get_dashboard_snapshot()
    print("Dashboard:", snap["total_bots"], "bots,", snap["total_earnings_usd"], "USD earned")


if __name__ == "__main__":  # pragma: no cover
    run()
