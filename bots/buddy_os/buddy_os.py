"""
Buddy OS — Main Entry Point

An advanced operating-system-like bot for the DreamCobots ecosystem.

Core capabilities:
  • Device Manager    — universal compatibility (TV, console, phone, tablet,
                        computer, Apple, Google, Samsung, Sony, Microsoft)
  • Bluetooth Engine  — device discovery, pairing, file transfer, streaming
  • Cast Engine       — screen casting via Google Cast, AirPlay, Miracast, HDMI
  • App Framework     — modular apps (mobile, desktop, web, TV, console)
  • Browser Toolkit   — browser-based tools and web-app shortcuts
  • Smart Device Hub  — IFTTT, Matter, Zigbee, Z-Wave, Wi-Fi, Thread
  • NVIDIA Tools Hub  — Isaac, Jetson, Omniverse, CUDA, TensorRT, NeMo, RAPIDS
  • Starlink Manager  — satellite internet management & 25%-markup resale

Buddy OS runs on any device with a compatible runtime — smartphone, tablet,
desktop, smart TV, or gaming console.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.buddy_os import BuddyOS, Tier

    buddy = BuddyOS(tier=Tier.PRO)

    # Register a phone
    phone = buddy.device_manager.register_device(
        "My iPhone", DeviceType.PHONE, DevicePlatform.APPLE
    )
    buddy.device_manager.connect(phone.device_id)

    # Pair a Bluetooth speaker
    buddy.bluetooth.add_discovered_device("AA:BB:CC:DD:EE:FF", "JBL Charge 5")
    buddy.bluetooth.pair_device("AA:BB:CC:DD:EE:FF")
    buddy.bluetooth.connect("AA:BB:CC:DD:EE:FF")

    # Cast a video to a Chromecast
    recv = buddy.cast.add_receiver("Living Room TV", CastProtocol.GOOGLE_CAST)
    session = buddy.cast.start_cast(recv.receiver_id, ContentType.VIDEO, "https://...")

    # Chat with Buddy
    response = buddy.chat("Show me connected devices")
    print(response["message"])
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.buddy_os.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_DEVICE_MANAGER,
    FEATURE_BLUETOOTH,
    FEATURE_CAST_SCREEN,
    FEATURE_MULTI_CAST,
    FEATURE_APP_FRAMEWORK,
    FEATURE_SMART_DEVICES,
    FEATURE_BROWSER_TOOLS,
    FEATURE_OS_KERNEL,
    FEATURE_STARLINK,
    FEATURE_NVIDIA_TOOLS,
    FEATURE_WHITE_LABEL,
    FEATURE_ENTERPRISE_MDM,
    FEATURE_WIFI,
    FEATURE_HARDWARE_PROTOCOLS,
    FEATURE_SECURITY_MANAGER,
    FEATURE_DEPLOYMENT_MANAGER,
    FEATURE_CLOUD_SYNC,
    FEATURE_FLASH_BOOT,
)
from bots.buddy_os.device_manager import (
    DeviceManager,
    Device,
    DeviceType,
    DevicePlatform,
    DeviceStatus,
)
from bots.buddy_os.bluetooth_engine import (
    BluetoothEngine,
    BluetoothDevice,
    BluetoothProfileType,
    BluetoothState,
    FileTransfer,
)
from bots.buddy_os.cast_engine import (
    CastEngine,
    CastReceiver,
    CastSession,
    CastProtocol,
    CastState,
    ContentType,
)
from bots.buddy_os.app_framework import (
    AppRegistry,
    BrowserToolkit,
    SmartDeviceHub,
    NvidiaToolsHub,
    StarlinkManager,
    AppCategory,
    AppPlatform,
    SmartDeviceProtocol,
)
from bots.buddy_os.wifi_engine import (
    WiFiEngine,
    WiFiNetwork,
    WiFiConnection,
    WiFiHotspot,
    WiFiSecurity,
    WiFiBand,
    WiFiConnectionState,
    IoTWiFiDevice,
)
from bots.buddy_os.hardware_protocols import (
    HardwareProtocolsHub,
    UARTManager,
    I2CManager,
    SPIManager,
    OBD2Manager,
    ProtocolType,
    ChannelState,
)
from bots.buddy_os.security_manager import (
    SecurityManager,
    SyncMode,
    DeviceToken,
    EncryptionKey,
    PairingSession,
    AuditEvent,
    AuthStatus,
    EncryptionAlgorithm,
)
from bots.buddy_os.deployment_manager import (
    DeploymentManager,
    BotPackage,
    BootConfig,
    InstallRecord,
    PackageFormat,
    PackageStatus,
    InstallMethod,
)


class BuddyOSError(Exception):
    """Raised when a Buddy OS operation fails."""


class BuddyOSTierError(BuddyOSError):
    """Raised when a feature is not available on the current tier."""


class BuddyOS:
    """
    Buddy OS — Advanced operating-system-like bot.

    Acts as the unified control layer for all device interactions,
    connectivity protocols, and smart-home/app management within the
    DreamCobots ecosystem.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling device limits and feature access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        # Subsystems — instantiated regardless of tier but gated on use
        self.device_manager = DeviceManager(
            max_devices=self.config.max_paired_devices
        )
        self.bluetooth = BluetoothEngine(
            max_paired=self.config.max_paired_devices
        )
        self.cast = CastEngine(
            max_targets=self.config.max_cast_targets
        )
        self.apps = AppRegistry()
        self.browser = BrowserToolkit()
        self.smart_devices = SmartDeviceHub()
        self.nvidia = NvidiaToolsHub()
        self.starlink = StarlinkManager()

        # New subsystems
        self.wifi = WiFiEngine()
        self.hardware = HardwareProtocolsHub()
        self.security = SecurityManager()
        self.deployment = DeploymentManager()

        # Boot the OS kernel
        self._boot_log: list[str] = []
        self._boot()

    # ------------------------------------------------------------------
    # Boot sequence
    # ------------------------------------------------------------------

    def _boot(self) -> None:
        """Initialise the Buddy OS kernel and load default apps."""
        self._boot_log.append("Buddy OS kernel initialised.")
        self._boot_log.append(f"Tier: {self.config.name}")
        self._boot_log.append(f"Max paired devices: {self.config.max_paired_devices or 'unlimited'}")
        self._boot_log.append(f"Max cast targets: {self.config.max_cast_targets or 'unlimited'}")

        # Pre-load built-in browser tools
        self.browser.add_tool(
            "DreamCo Dashboard", "https://dreamcobots.com/dashboard", "Main control panel"
        )
        self.browser.add_tool(
            "Bot Marketplace", "https://dreamcobots.com/marketplace", "Browse and buy bots"
        )

        self._boot_log.append("Default browser tools loaded.")
        self._boot_log.append("WiFi engine ready.")
        self._boot_log.append("Security manager ready.")
        self._boot_log.append("Hardware protocols hub ready.")
        self._boot_log.append("Deployment manager ready.")
        self._boot_log.append("Buddy OS ready.")

    def get_boot_log(self) -> list[str]:
        """Return the OS boot log."""
        return list(self._boot_log)

    # ------------------------------------------------------------------
    # Feature gate
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise BuddyOSTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to access it."
            )

    # ------------------------------------------------------------------
    # High-level convenience methods
    # ------------------------------------------------------------------

    def connect_device(
        self,
        name: str,
        device_type: DeviceType,
        platform: DevicePlatform,
        os_version: str = "",
    ) -> Device:
        """Register and immediately connect a device."""
        self._require_feature(FEATURE_DEVICE_MANAGER)
        device = self.device_manager.register_device(
            name, device_type, platform, os_version
        )
        return self.device_manager.connect(device.device_id)

    def pair_bluetooth(
        self,
        address: str,
        name: str,
        rssi: int = -70,
        profiles: Optional[list] = None,
    ) -> BluetoothDevice:
        """Discover, pair, and connect a Bluetooth device in one step."""
        self._require_feature(FEATURE_BLUETOOTH)
        self.bluetooth.add_discovered_device(address, name, rssi, profiles)
        paired = self.bluetooth.pair_device(address)
        return self.bluetooth.connect(address)

    def cast_to_screen(
        self,
        receiver_name: str,
        protocol: CastProtocol,
        content_url: str,
        content_type: ContentType = ContentType.VIDEO,
        ip_address: str = "",
    ) -> CastSession:
        """Add a receiver and immediately start a cast session."""
        self._require_feature(FEATURE_CAST_SCREEN)
        receiver = self.cast.add_receiver(receiver_name, protocol, ip_address)
        return self.cast.start_cast(receiver.receiver_id, content_type, content_url)

    # ------------------------------------------------------------------
    # System status
    # ------------------------------------------------------------------

    def system_status(self) -> dict:
        """Return a full Buddy OS status snapshot."""
        return {
            "tier": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "connected_devices": [
                d.to_dict() for d in self.device_manager.get_connected_devices()
            ],
            "bluetooth_paired": [
                d.to_dict() for d in self.bluetooth.get_connected_devices()
            ],
            "active_cast_sessions": [
                s.to_dict() for s in self.cast.list_sessions(active_only=True)
            ],
            "installed_apps": len(self.apps.list_apps()),
            "browser_tools": len(self.browser.list_tools()),
            "smart_devices": len(self.smart_devices.list_devices()),
            "nvidia_tools_activated": len(self.nvidia.get_activated_tools()),
            "starlink_subscriptions": len(
                self.starlink.list_subscriptions(active_only=True)
            ),
            "wifi": self.wifi.status(),
            "hardware_protocols": self.hardware.status(),
            "security": {
                "sync_mode": self.security.sync_mode.value,
                "active_tokens": len(self.security.list_tokens(active_only=True)),
                "active_keys": len(self.security.list_keys(active_only=True)),
            },
            "deployment": {
                "packages": len(self.deployment.list_packages()),
                "installed_bots": len(self.deployment.list_installed_bots()),
            },
            "features": self.config.features,
        }

    # ------------------------------------------------------------------
    # Tier management
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self.config
        upgrade = get_upgrade_path(self.tier)
        lines = [
            f"Buddy OS — {cfg.name} Tier",
            f"Price: ${cfg.price_usd_monthly:.2f}/month",
            f"Max paired devices: {cfg.max_paired_devices or 'Unlimited'}",
            f"Max cast targets: {cfg.max_cast_targets or 'Unlimited'}",
            f"Support: {cfg.support_level}",
            f"Features: {', '.join(cfg.features)}",
        ]
        if upgrade:
            lines.append(
                f"Upgrade available: {upgrade.name} at ${upgrade.price_usd_monthly:.2f}/month"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Handle a natural-language message and return a response dict.

        This method makes BuddyOS compatible with the BuddyAI orchestrator.
        """
        msg = message.lower().strip()

        if any(k in msg for k in ("status", "overview", "system")):
            return {
                "response": "buddy_os",
                "message": "Here is your Buddy OS status.",
                "data": self.system_status(),
            }

        if "device" in msg:
            devices = [d.to_dict() for d in self.device_manager.list_devices()]
            return {
                "response": "buddy_os",
                "message": f"You have {len(devices)} device(s) registered.",
                "data": {"devices": devices},
            }

        if "bluetooth" in msg or "bt" in msg:
            paired = [d.to_dict() for d in self.bluetooth.get_connected_devices()]
            return {
                "response": "buddy_os",
                "message": f"{len(paired)} Bluetooth device(s) connected.",
                "data": {"bluetooth_devices": paired},
            }

        if "cast" in msg or "screen" in msg or "airplay" in msg or "chromecast" in msg:
            sessions = [s.to_dict() for s in self.cast.list_sessions(active_only=True)]
            return {
                "response": "buddy_os",
                "message": f"{len(sessions)} active cast session(s).",
                "data": {"cast_sessions": sessions},
            }

        if "app" in msg:
            apps = [a.to_dict() for a in self.apps.list_apps()]
            return {
                "response": "buddy_os",
                "message": f"You have {len(apps)} app(s) installed.",
                "data": {"apps": apps},
            }

        if "starlink" in msg:
            plans = self.starlink.list_plans()
            return {
                "response": "buddy_os",
                "message": "Here are the available Starlink plans.",
                "data": {"plans": plans},
            }

        if "nvidia" in msg or "gpu" in msg:
            tools = self.nvidia.list_tools()
            return {
                "response": "buddy_os",
                "message": "Here are the available NVIDIA tools.",
                "data": {"nvidia_tools": tools},
            }

        if "tier" in msg or "upgrade" in msg or "plan" in msg:
            return {
                "response": "buddy_os",
                "message": self.describe_tier(),
                "data": {},
            }

        if "wifi" in msg or "wireless" in msg or "network" in msg:
            status = self.wifi.status()
            return {
                "response": "buddy_os",
                "message": (
                    f"WiFi: {'scanning' if status['scanning'] else 'idle'}. "
                    f"{status['known_networks']} network(s) known. "
                    f"Active SSID: {status['active_ssid'] or 'none'}."
                ),
                "data": {"wifi": status},
            }

        if "hardware" in msg or "uart" in msg or "i2c" in msg or "spi" in msg or "obd" in msg:
            hw = self.hardware.status()
            return {
                "response": "buddy_os",
                "message": (
                    f"Hardware protocols: {hw['uart_channels']} UART, "
                    f"{hw['i2c_devices']} I2C, {hw['spi_devices']} SPI, "
                    f"{hw['obd2_sessions']} OBD-II session(s)."
                ),
                "data": {"hardware": hw},
            }

        if "security" in msg or "encrypt" in msg or "auth" in msg or "token" in msg:
            sec = {
                "sync_mode": self.security.sync_mode.value,
                "active_tokens": len(self.security.list_tokens(active_only=True)),
                "active_keys": len(self.security.list_keys(active_only=True)),
            }
            return {
                "response": "buddy_os",
                "message": (
                    f"Security: {sec['sync_mode']} mode. "
                    f"{sec['active_tokens']} token(s), {sec['active_keys']} key(s) active."
                ),
                "data": {"security": sec},
            }

        if "deploy" in msg or "install" in msg or "package" in msg or "flash" in msg or "zip" in msg or "usb" in msg:
            dep = {
                "packages": len(self.deployment.list_packages()),
                "installed_bots": len(self.deployment.list_installed_bots()),
                "boot_configs": len(self.deployment.list_boot_configs()),
            }
            return {
                "response": "buddy_os",
                "message": (
                    f"Deployment: {dep['packages']} package(s), "
                    f"{dep['installed_bots']} bot(s) installed, "
                    f"{dep['boot_configs']} boot config(s)."
                ),
                "data": {"deployment": dep},
            }

        return {
            "response": "buddy_os",
            "message": (
                "Buddy OS is running. Ask about devices, Bluetooth, cast, apps, "
                "Starlink, NVIDIA tools, WiFi, hardware protocols, security, or deployment."
            ),
            "data": {},
        }

    # ------------------------------------------------------------------
    # BuddyAI registration helper
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance) -> None:
        """Register this BuddyOS instance with a BuddyAI orchestrator."""
        buddy_bot_instance.register_bot("buddy_os", self)


# ---------------------------------------------------------------------------
# Allow importing enums/types at the bots.buddy_os level for convenience
# ---------------------------------------------------------------------------
from typing import Optional  # noqa: E402 (re-exported)
