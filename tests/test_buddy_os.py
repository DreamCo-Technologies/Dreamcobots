"""
Tests for bots/buddy_os/

Covers:
  1. Tiers
  2. Device Manager
  3. Bluetooth Engine
  4. Cast Engine
  5. App Framework (AppRegistry, BrowserToolkit, SmartDeviceHub,
                    NvidiaToolsHub, StarlinkManager)
  6. BuddyOS main class (integration + chat)
  7. WiFi Engine
  8. Hardware Protocols (UART, I2C, SPI, OBD-II)
  9. Security Manager
  10. Deployment Manager
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from bots.buddy_os.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_BLUETOOTH,
    FEATURE_CAST_SCREEN,
    FEATURE_DEVICE_MANAGER,
    FEATURE_MULTI_CAST,
    FEATURE_APP_FRAMEWORK,
    FEATURE_STARLINK,
    FEATURE_NVIDIA_TOOLS,
    FEATURE_WHITE_LABEL,
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
    DEVICE_COMPATIBILITY_MATRIX,
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
    CastProtocol,
    CastState,
    ContentType,
    CastSession,
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
    NVIDIA_MARKUP_PCT,
    STARLINK_MARKUP_PCT,
    NVIDIA_TOOLS,
    STARLINK_PLANS,
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
    UARTParity,
    SPIMode,
    OBD2_PIDS,
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
from bots.buddy_os.buddy_os import BuddyOS, BuddyOSError, BuddyOSTierError


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_tier_price(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_enterprise_unlimited_devices(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_devices()

    def test_free_limited_devices(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_paired_devices is not None
        assert cfg.max_paired_devices > 0

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_no_upgrade_from_enterprise(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_has_bluetooth(self):
        assert FEATURE_BLUETOOTH in get_tier_config(Tier.FREE).features

    def test_enterprise_has_white_label(self):
        assert FEATURE_WHITE_LABEL in get_tier_config(Tier.ENTERPRISE).features

    def test_pro_has_multi_cast(self):
        assert FEATURE_MULTI_CAST in get_tier_config(Tier.PRO).features

    def test_has_feature_method(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_DEVICE_MANAGER)
        assert not cfg.has_feature(FEATURE_WHITE_LABEL)


# ===========================================================================
# 2. Device Manager
# ===========================================================================

class TestDeviceManager:
    def test_register_phone(self):
        dm = DeviceManager()
        device = dm.register_device("My Phone", DeviceType.PHONE, DevicePlatform.APPLE)
        assert device.device_id.startswith("dev_")
        assert device.name == "My Phone"

    def test_register_tv(self):
        dm = DeviceManager()
        device = dm.register_device("Living Room TV", DeviceType.TV, DevicePlatform.SAMSUNG)
        assert device.device_type == DeviceType.TV

    def test_connect_device(self):
        dm = DeviceManager()
        dev = dm.register_device("Tablet", DeviceType.TABLET, DevicePlatform.GOOGLE)
        dm.connect(dev.device_id)
        assert dm.get_device(dev.device_id).status == DeviceStatus.CONNECTED

    def test_disconnect_device(self):
        dm = DeviceManager()
        dev = dm.register_device("PC", DeviceType.COMPUTER, DevicePlatform.WINDOWS)
        dm.connect(dev.device_id)
        dm.disconnect(dev.device_id)
        assert dm.get_device(dev.device_id).status == DeviceStatus.DISCONNECTED

    def test_get_connected_devices(self):
        dm = DeviceManager()
        dev1 = dm.register_device("Phone", DeviceType.PHONE, DevicePlatform.APPLE)
        dev2 = dm.register_device("Tablet", DeviceType.TABLET, DevicePlatform.GOOGLE)
        dm.connect(dev1.device_id)
        connected = dm.get_connected_devices()
        assert len(connected) == 1

    def test_list_devices_by_type(self):
        dm = DeviceManager()
        dm.register_device("Phone1", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.register_device("TV1", DeviceType.TV, DevicePlatform.SAMSUNG)
        phones = dm.list_devices(device_type=DeviceType.PHONE)
        assert len(phones) == 1

    def test_list_devices_by_platform(self):
        dm = DeviceManager()
        dm.register_device("iPhone", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.register_device("iPad", DeviceType.TABLET, DevicePlatform.APPLE)
        dm.register_device("Android", DeviceType.PHONE, DevicePlatform.GOOGLE)
        apple_devices = dm.list_devices(platform=DevicePlatform.APPLE)
        assert len(apple_devices) == 2

    def test_remove_device(self):
        dm = DeviceManager()
        dev = dm.register_device("Phone", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.remove_device(dev.device_id)
        assert len(dm.list_devices()) == 0

    def test_device_limit(self):
        dm = DeviceManager(max_devices=2)
        dm.register_device("D1", DeviceType.PHONE, DevicePlatform.APPLE)
        dm.register_device("D2", DeviceType.TABLET, DevicePlatform.GOOGLE)
        with pytest.raises(RuntimeError, match="limit"):
            dm.register_device("D3", DeviceType.COMPUTER, DevicePlatform.WINDOWS)

    def test_incompatible_platform_raises(self):
        dm = DeviceManager()
        # COMPUTER only supports Apple/Windows/Linux; Samsung is not supported
        with pytest.raises(ValueError):
            dm.register_device("Samsung PC", DeviceType.COMPUTER, DevicePlatform.SAMSUNG)

    def test_compatibility_matrix_returned(self):
        dm = DeviceManager()
        matrix = dm.get_compatibility_matrix()
        assert "phone" in matrix
        assert "apple" in matrix["phone"]

    def test_device_not_found_raises(self):
        dm = DeviceManager()
        with pytest.raises(KeyError):
            dm.get_device("dev_9999")

    def test_device_to_dict(self):
        dm = DeviceManager()
        dev = dm.register_device("Mac", DeviceType.COMPUTER, DevicePlatform.APPLE)
        d = dev.to_dict()
        assert d["name"] == "Mac"
        assert d["type"] == DeviceType.COMPUTER.value


# ===========================================================================
# 3. Bluetooth Engine
# ===========================================================================

class TestBluetoothEngine:
    def test_start_scan(self):
        bt = BluetoothEngine()
        result = bt.start_scan()
        assert result["scanning"] is True

    def test_stop_scan(self):
        bt = BluetoothEngine()
        bt.start_scan()
        result = bt.stop_scan()
        assert result["scanning"] is False

    def test_add_discovered_device(self):
        bt = BluetoothEngine()
        dev = bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "JBL Speaker")
        assert dev.name == "JBL Speaker"

    def test_pair_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        paired = bt.pair_device("AA:BB:CC:DD:EE:FF")
        assert paired.paired is True
        assert paired.state == BluetoothState.PAIRED

    def test_connect_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        connected = bt.connect("AA:BB:CC:DD:EE:FF")
        assert connected.state == BluetoothState.CONNECTED

    def test_disconnect_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        bt.disconnect("AA:BB:CC:DD:EE:FF")
        dev = bt._paired["AA:BB:CC:DD:EE:FF"]
        assert dev.state == BluetoothState.PAIRED

    def test_trust_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.trust_device("AA:BB:CC:DD:EE:FF")
        assert bt._paired["AA:BB:CC:DD:EE:FF"].trusted is True

    def test_unpair_device(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.unpair_device("AA:BB:CC:DD:EE:FF")
        assert "AA:BB:CC:DD:EE:FF" not in bt._paired

    def test_pairing_limit(self):
        bt = BluetoothEngine(max_paired=1)
        bt.add_discovered_device("AA:BB:CC:DD:EE:01", "Dev1")
        bt.add_discovered_device("AA:BB:CC:DD:EE:02", "Dev2")
        bt.pair_device("AA:BB:CC:DD:EE:01")
        with pytest.raises(RuntimeError, match="limit"):
            bt.pair_device("AA:BB:CC:DD:EE:02")

    def test_pair_unknown_raises(self):
        bt = BluetoothEngine()
        with pytest.raises(KeyError):
            bt.pair_device("FF:FF:FF:FF:FF:FF")

    def test_connect_unpaired_raises(self):
        bt = BluetoothEngine()
        with pytest.raises(KeyError):
            bt.connect("FF:FF:FF:FF:FF:FF")

    def test_file_transfer(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        transfer = bt.send_file("AA:BB:CC:DD:EE:FF", "photo.jpg", 1024)
        assert transfer.filename == "photo.jpg"
        assert transfer.status == "in_progress"

    def test_file_transfer_requires_connection(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        with pytest.raises(RuntimeError, match="not connected"):
            bt.send_file("AA:BB:CC:DD:EE:FF", "file.txt", 100)

    def test_transfer_progress(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        transfer = bt.send_file("AA:BB:CC:DD:EE:FF", "video.mp4", 2000)
        bt.update_transfer_progress(transfer.transfer_id, 2000)
        updated = bt.get_transfer(transfer.transfer_id)
        assert updated.status == "completed"
        assert updated.progress_pct == 100.0

    def test_get_connected_bluetooth_devices(self):
        bt = BluetoothEngine()
        bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Phone")
        bt.pair_device("AA:BB:CC:DD:EE:FF")
        bt.connect("AA:BB:CC:DD:EE:FF")
        assert len(bt.get_connected_devices()) == 1

    def test_bluetooth_device_to_dict(self):
        bt = BluetoothEngine()
        dev = bt.add_discovered_device("AA:BB:CC:DD:EE:FF", "Speaker")
        d = dev.to_dict()
        assert d["name"] == "Speaker"
        assert d["address"] == "AA:BB:CC:DD:EE:FF"


# ===========================================================================
# 4. Cast Engine
# ===========================================================================

class TestCastEngine:
    def test_add_google_cast_receiver(self):
        cast = CastEngine()
        recv = cast.add_receiver("Living Room TV", CastProtocol.GOOGLE_CAST, ip_address="192.168.1.5")
        assert recv.protocol == CastProtocol.GOOGLE_CAST

    def test_add_airplay_receiver(self):
        cast = CastEngine()
        recv = cast.add_receiver("Apple TV", CastProtocol.AIRPLAY)
        assert recv.name == "Apple TV"

    def test_start_cast_session(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.MIRACAST)
        session = cast.start_cast(recv.receiver_id, ContentType.VIDEO, "https://example.com/v.mp4")
        assert session.state == CastState.CASTING

    def test_pause_and_resume(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(recv.receiver_id, ContentType.VIDEO, "https://example.com/v.mp4")
        cast.pause_cast(session.session_id)
        assert cast.get_session(session.session_id).state == CastState.PAUSED
        cast.resume_cast(session.session_id)
        assert cast.get_session(session.session_id).state == CastState.CASTING

    def test_stop_cast(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.HDMI)
        session = cast.start_cast(recv.receiver_id, ContentType.SCREEN_MIRROR, "")
        cast.stop_cast(session.session_id)
        assert cast.get_session(session.session_id).state == CastState.STOPPED

    def test_seek(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(recv.receiver_id, ContentType.VIDEO, "url", duration_seconds=3600)
        cast.seek(session.session_id, 120.0)
        assert cast.get_session(session.session_id).position_seconds == 120.0

    def test_seek_clamped(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(recv.receiver_id, ContentType.VIDEO, "url", duration_seconds=60)
        cast.seek(session.session_id, 9999)
        assert cast.get_session(session.session_id).position_seconds == 60.0

    def test_set_volume(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.AIRPLAY)
        cast.set_volume(recv.receiver_id, 0.8)
        assert cast._receivers[recv.receiver_id].volume == 0.8

    def test_volume_clamped(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.AIRPLAY)
        cast.set_volume(recv.receiver_id, 5.0)
        assert cast._receivers[recv.receiver_id].volume == 1.0

    def test_cast_target_limit(self):
        cast = CastEngine(max_targets=1)
        cast.add_receiver("TV1", CastProtocol.GOOGLE_CAST)
        with pytest.raises(RuntimeError, match="limit"):
            cast.add_receiver("TV2", CastProtocol.AIRPLAY)

    def test_list_receivers_by_protocol(self):
        cast = CastEngine()
        cast.add_receiver("TV1", CastProtocol.GOOGLE_CAST)
        cast.add_receiver("TV2", CastProtocol.AIRPLAY)
        cast.add_receiver("TV3", CastProtocol.GOOGLE_CAST)
        google_recvs = cast.list_receivers(protocol=CastProtocol.GOOGLE_CAST)
        assert len(google_recvs) == 2

    def test_list_active_sessions(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        sess = cast.start_cast(recv.receiver_id, ContentType.VIDEO, "url")
        cast.stop_cast(sess.session_id)
        recv2 = cast.add_receiver("TV2", CastProtocol.AIRPLAY)
        cast.start_cast(recv2.receiver_id, ContentType.AUDIO, "audio_url")
        active = cast.list_sessions(active_only=True)
        assert len(active) == 1

    def test_receiver_not_found_raises(self):
        cast = CastEngine()
        with pytest.raises(KeyError):
            cast.start_cast("recv_9999", ContentType.VIDEO, "url")

    def test_session_to_dict(self):
        cast = CastEngine()
        recv = cast.add_receiver("TV", CastProtocol.GOOGLE_CAST)
        session = cast.start_cast(recv.receiver_id, ContentType.VIDEO, "https://example.com")
        d = session.to_dict()
        assert d["content_type"] == ContentType.VIDEO.value


# ===========================================================================
# 5. App Framework
# ===========================================================================

class TestAppRegistry:
    def test_install_app(self):
        reg = AppRegistry()
        app = reg.install("Netflix", AppCategory.ENTERTAINMENT, [AppPlatform.UNIVERSAL])
        assert app.name == "Netflix"
        assert app.enabled is True

    def test_disable_app(self):
        reg = AppRegistry()
        app = reg.install("Slack", AppCategory.COMMUNICATION, [AppPlatform.DESKTOP])
        reg.disable(app.app_id)
        assert reg.get_app(app.app_id).enabled is False

    def test_enable_app(self):
        reg = AppRegistry()
        app = reg.install("Slack", AppCategory.COMMUNICATION, [AppPlatform.DESKTOP])
        reg.disable(app.app_id)
        reg.enable(app.app_id)
        assert reg.get_app(app.app_id).enabled is True

    def test_uninstall_app(self):
        reg = AppRegistry()
        app = reg.install("App", AppCategory.UTILITIES, [AppPlatform.MOBILE])
        reg.uninstall(app.app_id)
        assert len(reg.list_apps()) == 0

    def test_list_apps_by_category(self):
        reg = AppRegistry()
        reg.install("YouTube", AppCategory.ENTERTAINMENT, [AppPlatform.UNIVERSAL])
        reg.install("Slack", AppCategory.COMMUNICATION, [AppPlatform.DESKTOP])
        ents = reg.list_apps(category=AppCategory.ENTERTAINMENT)
        assert len(ents) == 1

    def test_list_apps_enabled_only(self):
        reg = AppRegistry()
        app1 = reg.install("App1", AppCategory.UTILITIES, [AppPlatform.MOBILE])
        app2 = reg.install("App2", AppCategory.UTILITIES, [AppPlatform.MOBILE])
        reg.disable(app2.app_id)
        enabled = reg.list_apps(enabled_only=True)
        assert len(enabled) == 1

    def test_app_not_found_raises(self):
        reg = AppRegistry()
        with pytest.raises(KeyError):
            reg.get_app("app_9999")


class TestBrowserToolkit:
    def test_add_tool(self):
        bt = BrowserToolkit()
        tool = bt.add_tool("Dashboard", "https://example.com", "Control panel")
        assert tool.name == "Dashboard"

    def test_list_tools(self):
        bt = BrowserToolkit()
        bt.add_tool("Tool1", "https://example.com/1")
        bt.add_tool("Tool2", "https://example.com/2")
        assert len(bt.list_tools()) == 2

    def test_remove_tool(self):
        bt = BrowserToolkit()
        tool = bt.add_tool("Tool", "https://example.com")
        bt.remove_tool(tool.tool_id)
        assert len(bt.list_tools()) == 0

    def test_get_tool_not_found_raises(self):
        bt = BrowserToolkit()
        with pytest.raises(KeyError):
            bt.get_tool("btool_9999")


class TestSmartDeviceHub:
    def test_add_device(self):
        hub = SmartDeviceHub()
        dev = hub.add_device("Smart Light", SmartDeviceProtocol.ZIGBEE, room="Living Room")
        assert dev.name == "Smart Light"

    def test_set_online(self):
        hub = SmartDeviceHub()
        dev = hub.add_device("Thermostat", SmartDeviceProtocol.MATTER)
        hub.set_online(dev.device_id, True)
        assert hub.get_device(dev.device_id).online is True

    def test_update_state(self):
        hub = SmartDeviceHub()
        dev = hub.add_device("Light", SmartDeviceProtocol.WIFI)
        hub.update_state(dev.device_id, {"on": True, "brightness": 80})
        assert hub.get_device(dev.device_id).state["on"] is True

    def test_list_by_room(self):
        hub = SmartDeviceHub()
        hub.add_device("Light", SmartDeviceProtocol.ZIGBEE, room="Kitchen")
        hub.add_device("TV", SmartDeviceProtocol.WIFI, room="Living Room")
        kitchen = hub.list_devices(room="Kitchen")
        assert len(kitchen) == 1

    def test_device_not_found_raises(self):
        hub = SmartDeviceHub()
        with pytest.raises(KeyError):
            hub.get_device("sd_9999")


class TestNvidiaToolsHub:
    def test_list_tools_returns_all(self):
        hub = NvidiaToolsHub()
        tools = hub.list_tools()
        assert len(tools) == len(NVIDIA_TOOLS)

    def test_markup_applied(self):
        hub = NvidiaToolsHub()
        for tool in hub.list_tools():
            assert tool["markup_pct"] == NVIDIA_MARKUP_PCT

    def test_activate_tool(self):
        hub = NvidiaToolsHub()
        result = hub.activate_tool("cuda")
        assert result["activated"] is True

    def test_deactivate_tool(self):
        hub = NvidiaToolsHub()
        hub.activate_tool("cuda")
        result = hub.deactivate_tool("cuda")
        assert result["activated"] is False

    def test_get_activated_tools(self):
        hub = NvidiaToolsHub()
        hub.activate_tool("cuda")
        hub.activate_tool("tensorrt")
        activated = hub.get_activated_tools()
        assert len(activated) == 2

    def test_unknown_tool_raises(self):
        hub = NvidiaToolsHub()
        with pytest.raises(KeyError):
            hub.activate_tool("nonexistent_tool")


class TestStarlinkManager:
    def test_list_plans(self):
        mgr = StarlinkManager()
        plans = mgr.list_plans()
        assert len(plans) == len(STARLINK_PLANS)

    def test_markup_applied_to_plans(self):
        mgr = StarlinkManager()
        for plan in mgr.list_plans():
            expected = round(plan["base_monthly_usd"] * (1 + STARLINK_MARKUP_PCT / 100), 2)
            assert plan["marked_up_monthly_usd"] == expected

    def test_create_subscription(self):
        mgr = StarlinkManager()
        sub = mgr.create_subscription("Alice", "residential")
        assert sub.client_name == "Alice"
        assert sub.active is True

    def test_cancel_subscription(self):
        mgr = StarlinkManager()
        sub = mgr.create_subscription("Bob", "roam")
        mgr.cancel_subscription(sub.subscription_id)
        assert not mgr.get_subscription(sub.subscription_id).active

    def test_list_active_subscriptions(self):
        mgr = StarlinkManager()
        mgr.create_subscription("A", "residential")
        sub2 = mgr.create_subscription("B", "business")
        mgr.cancel_subscription(sub2.subscription_id)
        active = mgr.list_subscriptions(active_only=True)
        assert len(active) == 1

    def test_invalid_plan_raises(self):
        mgr = StarlinkManager()
        with pytest.raises(ValueError):
            mgr.create_subscription("X", "invalid_plan")

    def test_subscription_not_found_raises(self):
        mgr = StarlinkManager()
        with pytest.raises(KeyError):
            mgr.get_subscription("sl_9999")


# ===========================================================================
# 6. BuddyOS (integration)
# ===========================================================================

class TestBuddyOS:
    def test_instantiation_free_tier(self):
        buddy = BuddyOS(tier=Tier.FREE)
        assert buddy.tier == Tier.FREE

    def test_instantiation_pro_tier(self):
        buddy = BuddyOS(tier=Tier.PRO)
        assert buddy.config.price_usd_monthly == 49.0

    def test_boot_log_populated(self):
        buddy = BuddyOS()
        assert len(buddy.get_boot_log()) > 0

    def test_system_status_keys(self):
        buddy = BuddyOS(tier=Tier.PRO)
        status = buddy.system_status()
        for key in ("tier", "connected_devices", "bluetooth_paired",
                    "active_cast_sessions", "installed_apps"):
            assert key in status

    def test_connect_device_convenience(self):
        buddy = BuddyOS(tier=Tier.PRO)
        device = buddy.connect_device("iPhone", DeviceType.PHONE, DevicePlatform.APPLE)
        assert device.is_connected()

    def test_pair_bluetooth_convenience(self):
        buddy = BuddyOS(tier=Tier.PRO)
        dev = buddy.pair_bluetooth("AA:BB:CC:DD:EE:FF", "Headphones")
        assert dev.state == BluetoothState.CONNECTED

    def test_cast_to_screen_convenience(self):
        buddy = BuddyOS(tier=Tier.PRO)
        session = buddy.cast_to_screen(
            "Living Room TV", CastProtocol.GOOGLE_CAST, "https://example.com/video.mp4"
        )
        assert session.state == CastState.CASTING

    def test_describe_tier(self):
        buddy = BuddyOS(tier=Tier.FREE)
        desc = buddy.describe_tier()
        assert "Free" in desc
        assert "$0.00" in desc

    def test_chat_status(self):
        buddy = BuddyOS()
        resp = buddy.chat("status")
        assert resp["response"] == "buddy_os"
        assert "data" in resp

    def test_chat_device(self):
        buddy = BuddyOS()
        resp = buddy.chat("show devices")
        assert "device" in resp["message"].lower()

    def test_chat_bluetooth(self):
        buddy = BuddyOS()
        resp = buddy.chat("bluetooth status")
        assert resp["response"] == "buddy_os"

    def test_chat_cast(self):
        buddy = BuddyOS()
        resp = buddy.chat("cast to screen")
        assert resp["response"] == "buddy_os"

    def test_chat_apps(self):
        buddy = BuddyOS()
        resp = buddy.chat("list apps")
        assert "app" in resp["message"].lower()

    def test_chat_starlink(self):
        buddy = BuddyOS()
        resp = buddy.chat("tell me about starlink")
        assert "plans" in resp["data"]

    def test_chat_nvidia(self):
        buddy = BuddyOS()
        resp = buddy.chat("nvidia tools")
        assert "nvidia_tools" in resp["data"]

    def test_chat_tier(self):
        buddy = BuddyOS()
        resp = buddy.chat("upgrade plan")
        assert "Buddy OS" in resp["message"]

    def test_chat_default(self):
        buddy = BuddyOS()
        resp = buddy.chat("hello")
        assert resp["response"] == "buddy_os"

    def test_tier_error_free_feature_blocked(self):
        buddy = BuddyOS(tier=Tier.FREE)
        with pytest.raises(BuddyOSTierError):
            buddy._require_feature(FEATURE_WHITE_LABEL)

    def test_register_with_buddy(self):
        from BuddyAI.buddy_bot import BuddyBot
        orchestrator = BuddyBot()
        buddy_os = BuddyOS(tier=Tier.PRO)
        buddy_os.register_with_buddy(orchestrator)
        assert "buddy_os" in orchestrator.list_bots()

    def test_default_browser_tools_loaded(self):
        buddy = BuddyOS()
        tools = buddy.browser.list_tools()
        assert len(tools) >= 2


# ===========================================================================
# 7. WiFi Engine
# ===========================================================================

class TestWiFiEngine:
    def test_start_scan(self):
        wifi = WiFiEngine()
        result = wifi.start_scan()
        assert result["scanning"] is True

    def test_stop_scan(self):
        wifi = WiFiEngine()
        wifi.start_scan()
        result = wifi.stop_scan()
        assert result["scanning"] is False

    def test_add_discovered_network(self):
        wifi = WiFiEngine()
        net = wifi.add_discovered_network("HomeNet", "AA:BB:CC:DD:EE:01")
        assert net.ssid == "HomeNet"
        assert net.bssid == "AA:BB:CC:DD:EE:01"

    def test_list_networks(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("Net1", "AA:BB:CC:DD:EE:01", signal_dbm=-60)
        wifi.add_discovered_network("Net2", "AA:BB:CC:DD:EE:02", signal_dbm=-80)
        all_nets = wifi.list_networks()
        assert len(all_nets) == 2

    def test_filter_networks_by_signal(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("Strong", "AA:BB:CC:DD:EE:01", signal_dbm=-50)
        wifi.add_discovered_network("Weak", "AA:BB:CC:DD:EE:02", signal_dbm=-90)
        strong = wifi.list_networks(min_signal_dbm=-60)
        assert len(strong) == 1
        assert strong[0].ssid == "Strong"

    def test_filter_networks_by_security(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("WPA3Net", "AA:BB:CC:DD:EE:01",
                                    security=WiFiSecurity.WPA3)
        wifi.add_discovered_network("OpenNet", "AA:BB:CC:DD:EE:02",
                                    security=WiFiSecurity.OPEN)
        wpa3 = wifi.list_networks(security=WiFiSecurity.WPA3)
        assert len(wpa3) == 1

    def test_connect_to_network(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("Home", "AA:BB:CC:DD:EE:01",
                                    security=WiFiSecurity.WPA2)
        conn = wifi.connect("Home", password="password123")
        assert conn.is_connected()
        assert conn.ssid == "Home"

    def test_connect_open_network_no_password(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("CafeWiFi", "AA:BB:CC:DD:EE:02",
                                    security=WiFiSecurity.OPEN)
        conn = wifi.connect("CafeWiFi")
        assert conn.is_connected()

    def test_connect_missing_password_raises(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("Secured", "AA:BB:CC:DD:EE:03",
                                    security=WiFiSecurity.WPA2)
        with pytest.raises(ValueError, match="Password"):
            wifi.connect("Secured")

    def test_disconnect(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("Home", "AA:BB:CC:DD:EE:01",
                                    security=WiFiSecurity.WPA2)
        conn = wifi.connect("Home", password="pass1234")
        wifi.disconnect(conn.connection_id)
        assert not conn.is_connected()

    def test_get_active_connection(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("Home", "AA:BB:CC:DD:EE:01",
                                    security=WiFiSecurity.WPA2)
        conn = wifi.connect("Home", password="pass1234")
        active = wifi.get_active_connection()
        assert active is not None
        assert active.ssid == "Home"

    def test_no_active_connection_initially(self):
        wifi = WiFiEngine()
        assert wifi.get_active_connection() is None

    def test_forget_network(self):
        wifi = WiFiEngine()
        wifi.add_discovered_network("Home", "AA:BB:CC:DD:EE:01",
                                    security=WiFiSecurity.WPA2)
        conn = wifi.connect("Home", password="pass1234")
        wifi.forget_network(conn.connection_id)
        assert len(wifi.list_connections()) == 0

    def test_create_hotspot(self):
        wifi = WiFiEngine()
        hotspot = wifi.create_hotspot("BuddyAP", "securepass")
        assert hotspot.ssid == "BuddyAP"
        assert hotspot.state.value == "active"

    def test_hotspot_short_password_raises(self):
        wifi = WiFiEngine()
        with pytest.raises(ValueError, match="8 characters"):
            wifi.create_hotspot("AP", "short")

    def test_stop_hotspot(self):
        wifi = WiFiEngine()
        wifi.create_hotspot("BuddyAP", "securepass")
        hotspot = wifi.stop_hotspot()
        assert hotspot.state.value == "inactive"

    def test_add_hotspot_client(self):
        wifi = WiFiEngine()
        wifi.create_hotspot("BuddyAP", "securepass")
        wifi.add_hotspot_client("11:22:33:44:55:66")
        assert "11:22:33:44:55:66" in wifi.get_hotspot().connected_clients

    def test_hotspot_client_limit(self):
        wifi = WiFiEngine()
        wifi.create_hotspot("BuddyAP", "securepass", max_clients=1)
        wifi.add_hotspot_client("11:22:33:44:55:01")
        with pytest.raises(RuntimeError, match="limit"):
            wifi.add_hotspot_client("11:22:33:44:55:02")

    def test_pair_iot_device(self):
        wifi = WiFiEngine()
        dev = wifi.pair_iot_device("Smart Bulb", "AA:BB:CC:00:00:01",
                                   ip_address="192.168.1.10",
                                   device_type="light")
        assert dev.online is True
        assert dev.device_type == "light"

    def test_set_iot_device_online(self):
        wifi = WiFiEngine()
        dev = wifi.pair_iot_device("Thermostat", "AA:BB:CC:00:00:02")
        wifi.set_iot_device_online(dev.device_id, False)
        assert not wifi.get_iot_device(dev.device_id).online

    def test_update_iot_state(self):
        wifi = WiFiEngine()
        dev = wifi.pair_iot_device("Smart Light", "AA:BB:CC:00:00:03")
        wifi.update_iot_state(dev.device_id, {"on": True, "brightness": 75})
        assert wifi.get_iot_device(dev.device_id).state["on"] is True

    def test_remove_iot_device(self):
        wifi = WiFiEngine()
        dev = wifi.pair_iot_device("Sensor", "AA:BB:CC:00:00:04")
        wifi.remove_iot_device(dev.device_id)
        assert len(wifi.list_iot_devices()) == 0

    def test_iot_device_not_found_raises(self):
        wifi = WiFiEngine()
        with pytest.raises(KeyError):
            wifi.get_iot_device("iot_9999")

    def test_wifi_status(self):
        wifi = WiFiEngine()
        status = wifi.status()
        assert "scanning" in status
        assert "active_ssid" in status
        assert "iot_devices" in status

    def test_network_to_dict(self):
        wifi = WiFiEngine()
        net = wifi.add_discovered_network("TestNet", "AA:BB:CC:DD:EE:FF")
        d = net.to_dict()
        assert d["ssid"] == "TestNet"
        assert "security" in d


# ===========================================================================
# 8. Hardware Protocols
# ===========================================================================

class TestUARTManager:
    def test_open_channel(self):
        uart = UARTManager()
        ch = uart.open_channel("/dev/ttyUSB0", baud_rate=115200)
        assert ch.state == ChannelState.OPEN
        assert ch.baud_rate == 115200

    def test_close_channel(self):
        uart = UARTManager()
        ch = uart.open_channel("/dev/ttyUSB0")
        uart.close_channel(ch.channel_id)
        assert uart.get_channel(ch.channel_id).state == ChannelState.CLOSED

    def test_write_and_read(self):
        uart = UARTManager()
        ch = uart.open_channel("/dev/ttyUSB0")
        uart.inject_rx(ch.channel_id, b"hello")
        data = uart.read(ch.channel_id, 64)
        assert data == b"hello"

    def test_write_returns_byte_count(self):
        uart = UARTManager()
        ch = uart.open_channel("/dev/ttyUSB0")
        n = uart.write(ch.channel_id, b"test")
        assert n == 4

    def test_read_empty_buffer(self):
        uart = UARTManager()
        ch = uart.open_channel("/dev/ttyUSB0")
        assert uart.read(ch.channel_id) == b""

    def test_write_to_closed_channel_raises(self):
        uart = UARTManager()
        ch = uart.open_channel("/dev/ttyUSB0")
        uart.close_channel(ch.channel_id)
        with pytest.raises(RuntimeError, match="not open"):
            uart.write(ch.channel_id, b"data")

    def test_channel_not_found_raises(self):
        uart = UARTManager()
        with pytest.raises(KeyError):
            uart.get_channel("uart_9999")

    def test_to_dict(self):
        uart = UARTManager()
        ch = uart.open_channel("/dev/ttyUSB0")
        d = ch.to_dict()
        assert d["protocol"] == ProtocolType.UART.value
        assert d["port"] == "/dev/ttyUSB0"


class TestI2CManager:
    def test_add_device(self):
        i2c = I2CManager()
        dev = i2c.add_device(0x48, "Temperature Sensor")
        assert dev.address == 0x48
        assert dev.name == "Temperature Sensor"

    def test_open_device(self):
        i2c = I2CManager()
        dev = i2c.add_device(0x48, "Sensor")
        i2c.open_device(dev.device_id)
        assert i2c.get_device(dev.device_id).state == ChannelState.OPEN

    def test_close_device(self):
        i2c = I2CManager()
        dev = i2c.add_device(0x48, "Sensor")
        i2c.open_device(dev.device_id)
        i2c.close_device(dev.device_id)
        assert i2c.get_device(dev.device_id).state == ChannelState.CLOSED

    def test_write_and_read_register(self):
        i2c = I2CManager()
        dev = i2c.add_device(0x48, "Sensor")
        i2c.open_device(dev.device_id)
        i2c.write_register(dev.device_id, 0x01, 42)
        val = i2c.read_register(dev.device_id, 0x01)
        assert val == 42

    def test_read_unset_register_returns_zero(self):
        i2c = I2CManager()
        dev = i2c.add_device(0x48, "Sensor")
        i2c.open_device(dev.device_id)
        assert i2c.read_register(dev.device_id, 0xFF) == 0

    def test_invalid_address_raises(self):
        i2c = I2CManager()
        with pytest.raises(ValueError, match="range"):
            i2c.add_device(0xFF, "BadDevice")

    def test_write_to_closed_raises(self):
        i2c = I2CManager()
        dev = i2c.add_device(0x48, "Sensor")
        with pytest.raises(RuntimeError, match="not open"):
            i2c.write_register(dev.device_id, 0x01, 1)

    def test_scan_bus(self):
        i2c = I2CManager()
        i2c.add_device(0x48, "Sensor1", bus=1)
        i2c.add_device(0x50, "EEPROM", bus=1)
        i2c.add_device(0x20, "GPIO", bus=2)
        bus1 = i2c.scan_bus(bus=1)
        assert len(bus1) == 2

    def test_device_not_found_raises(self):
        i2c = I2CManager()
        with pytest.raises(KeyError):
            i2c.get_device("i2c_9999")

    def test_to_dict(self):
        i2c = I2CManager()
        dev = i2c.add_device(0x48, "Sensor")
        d = dev.to_dict()
        assert d["protocol"] == ProtocolType.I2C.value
        assert d["address"] == "0x48"


class TestSPIManager:
    def test_add_device(self):
        spi = SPIManager()
        dev = spi.add_device(0, 0, "ADC")
        assert dev.name == "ADC"

    def test_open_and_close(self):
        spi = SPIManager()
        dev = spi.add_device(0, 0, "ADC")
        spi.open_device(dev.device_id)
        assert spi.get_device(dev.device_id).state == ChannelState.OPEN
        spi.close_device(dev.device_id)
        assert spi.get_device(dev.device_id).state == ChannelState.CLOSED

    def test_transfer(self):
        spi = SPIManager()
        dev = spi.add_device(0, 0, "ADC")
        spi.open_device(dev.device_id)
        rx = spi.transfer(dev.device_id, b"\x00\xFF")
        assert rx == bytes([0xFF, 0x00])

    def test_transfer_on_closed_raises(self):
        spi = SPIManager()
        dev = spi.add_device(0, 0, "ADC")
        with pytest.raises(RuntimeError, match="not open"):
            spi.transfer(dev.device_id, b"\x01")

    def test_device_not_found_raises(self):
        spi = SPIManager()
        with pytest.raises(KeyError):
            spi.get_device("spi_9999")

    def test_to_dict(self):
        spi = SPIManager()
        dev = spi.add_device(0, 0, "ADC", clock_hz=500_000)
        d = dev.to_dict()
        assert d["protocol"] == ProtocolType.SPI.value
        assert d["clock_hz"] == 500_000


class TestOBD2Manager:
    def test_open_session(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0", vehicle_vin="1HGCM82633A123456")
        assert session.state == ChannelState.OPEN
        assert session.vehicle_vin == "1HGCM82633A123456"

    def test_close_session(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        obd.close_session(session.session_id)
        assert obd.get_session(session.session_id).state == ChannelState.CLOSED

    def test_read_standard_pid(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        result = obd.read_pid(session.session_id, "0C")
        assert result["name"] == "engine_rpm"

    def test_read_unknown_pid_raises(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        with pytest.raises(KeyError):
            obd.read_pid(session.session_id, "ZZ")

    def test_inject_and_read_live_data(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        obd.inject_live_data(session.session_id, "vehicle_speed", {"value": 90, "unit": "km/h"})
        data = obd.get_live_data(session.session_id)
        assert data["vehicle_speed"]["value"] == 90

    def test_inject_and_read_dtc(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        obd.inject_dtc(session.session_id, "P0300")
        codes = obd.read_dtc(session.session_id)
        assert "P0300" in codes

    def test_clear_dtc(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        obd.inject_dtc(session.session_id, "P0300")
        obd.inject_dtc(session.session_id, "P0420")
        cleared = obd.clear_dtc(session.session_id)
        assert cleared == 2
        assert obd.read_dtc(session.session_id) == []

    def test_list_standard_pids(self):
        obd = OBD2Manager()
        pids = obd.list_standard_pids()
        assert len(pids) == len(OBD2_PIDS)

    def test_read_on_closed_session_raises(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        obd.close_session(session.session_id)
        with pytest.raises(RuntimeError, match="not open"):
            obd.read_pid(session.session_id, "0C")

    def test_session_not_found_raises(self):
        obd = OBD2Manager()
        with pytest.raises(KeyError):
            obd.get_session("obd_9999")

    def test_to_dict(self):
        obd = OBD2Manager()
        session = obd.open_session("/dev/ttyUSB0")
        d = session.to_dict()
        assert d["protocol"] == ProtocolType.OBD2.value


class TestHardwareProtocolsHub:
    def test_instantiation(self):
        hub = HardwareProtocolsHub()
        assert isinstance(hub.uart, UARTManager)
        assert isinstance(hub.i2c, I2CManager)
        assert isinstance(hub.spi, SPIManager)
        assert isinstance(hub.obd2, OBD2Manager)

    def test_status_empty(self):
        hub = HardwareProtocolsHub()
        status = hub.status()
        assert status["uart_channels"] == 0
        assert status["i2c_devices"] == 0

    def test_status_after_adding(self):
        hub = HardwareProtocolsHub()
        hub.uart.open_channel("/dev/ttyUSB0")
        hub.i2c.add_device(0x48, "Sensor")
        status = hub.status()
        assert status["uart_channels"] == 1
        assert status["i2c_devices"] == 1


# ===========================================================================
# 9. Security Manager
# ===========================================================================

class TestSecurityManager:
    def test_default_sync_mode_local(self):
        sec = SecurityManager()
        assert sec.sync_mode == SyncMode.LOCAL
        assert sec.is_local_mode()

    def test_set_sync_mode_cloud(self):
        sec = SecurityManager()
        sec.set_sync_mode(SyncMode.CLOUD)
        assert sec.is_cloud_mode()

    def test_issue_token(self):
        sec = SecurityManager()
        raw_token, dt = sec.issue_token("MyPhone", scopes=["read", "write"])
        assert dt.is_valid()
        assert dt.status == AuthStatus.APPROVED
        assert "read" in dt.scopes

    def test_verify_token_valid(self):
        sec = SecurityManager()
        raw_token, dt = sec.issue_token("MyPhone")
        assert sec.verify_token(dt.token_id, raw_token) is True

    def test_verify_token_wrong_token(self):
        sec = SecurityManager()
        _raw, dt = sec.issue_token("MyPhone")
        assert sec.verify_token(dt.token_id, "wrongtoken") is False

    def test_verify_token_not_found(self):
        sec = SecurityManager()
        assert sec.verify_token("tok_9999", "any") is False

    def test_revoke_token(self):
        sec = SecurityManager()
        _raw, dt = sec.issue_token("MyPhone")
        sec.revoke_token(dt.token_id)
        assert sec.get_token(dt.token_id).status == AuthStatus.REVOKED
        assert not sec.get_token(dt.token_id).is_valid()

    def test_verify_revoked_token_fails(self):
        sec = SecurityManager()
        raw_token, dt = sec.issue_token("MyPhone")
        sec.revoke_token(dt.token_id)
        assert sec.verify_token(dt.token_id, raw_token) is False

    def test_list_active_tokens(self):
        sec = SecurityManager()
        _, dt1 = sec.issue_token("Phone1")
        _, dt2 = sec.issue_token("Phone2")
        sec.revoke_token(dt2.token_id)
        active = sec.list_tokens(active_only=True)
        assert len(active) == 1

    def test_generate_key(self):
        sec = SecurityManager()
        key = sec.generate_key(EncryptionAlgorithm.AES_256_GCM)
        assert key.active is True
        assert key.algorithm == EncryptionAlgorithm.AES_256_GCM
        assert len(key.key_bytes) == 32

    def test_rotate_key(self):
        sec = SecurityManager()
        old_key = sec.generate_key()
        new_key = sec.rotate_key(old_key.key_id)
        assert not sec.get_key(old_key.key_id).active
        assert new_key.active is True

    def test_revoke_key(self):
        sec = SecurityManager()
        key = sec.generate_key()
        sec.revoke_key(key.key_id)
        assert not sec.get_key(key.key_id).active

    def test_encrypt_decrypt(self):
        sec = SecurityManager()
        key = sec.generate_key()
        plaintext = b"Hello, Buddy OS!"
        ciphertext = sec.encrypt(key.key_id, plaintext)
        assert ciphertext != plaintext
        decrypted = sec.decrypt(key.key_id, ciphertext)
        assert decrypted == plaintext

    def test_encrypt_inactive_key_raises(self):
        sec = SecurityManager()
        key = sec.generate_key()
        sec.revoke_key(key.key_id)
        with pytest.raises(RuntimeError, match="inactive"):
            sec.encrypt(key.key_id, b"data")

    def test_key_not_found_raises(self):
        sec = SecurityManager()
        with pytest.raises(KeyError):
            sec.get_key("key_9999")

    def test_initiate_pairing(self):
        sec = SecurityManager()
        session = sec.initiate_pairing("Laptop")
        assert session.device_name == "Laptop"
        assert len(session.pin) == 6
        assert not session.confirmed

    def test_confirm_pairing(self):
        sec = SecurityManager()
        session = sec.initiate_pairing("Laptop")
        token = sec.confirm_pairing(session.session_id, session.pin)
        assert token.is_valid()
        assert sec.get_pairing_session(session.session_id).confirmed

    def test_confirm_pairing_wrong_pin(self):
        sec = SecurityManager()
        session = sec.initiate_pairing("Laptop")
        with pytest.raises(ValueError, match="Incorrect PIN"):
            sec.confirm_pairing(session.session_id, "000000")

    def test_confirm_pairing_twice_raises(self):
        sec = SecurityManager()
        session = sec.initiate_pairing("Laptop")
        sec.confirm_pairing(session.session_id, session.pin)
        with pytest.raises(RuntimeError, match="already confirmed"):
            sec.confirm_pairing(session.session_id, session.pin)

    def test_audit_log_populated(self):
        sec = SecurityManager()
        sec.issue_token("Phone")
        log = sec.get_audit_log()
        assert len(log) > 0

    def test_audit_log_integrity(self):
        sec = SecurityManager()
        sec.issue_token("Phone")
        sec.generate_key()
        assert sec.verify_audit_log() is True

    def test_audit_event_to_dict(self):
        sec = SecurityManager()
        sec.issue_token("Phone")
        event = sec.get_audit_log()[0]
        d = event.to_dict()
        assert "event_type" in d
        assert "actor" in d


# ===========================================================================
# 10. Deployment Manager
# ===========================================================================

class TestDeploymentManager:
    def test_create_zip_package(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package(
            "TestBot", "1.0.0",
            files={"main.py": b"print('hello')", "README.md": b"# TestBot"},
        )
        assert pkg.fmt == PackageFormat.ZIP
        assert pkg.status == PackageStatus.READY
        assert pkg.checksum != ""
        assert pkg.size_bytes > 0

    def test_zip_package_contains_manifest(self):
        import zipfile
        from io import BytesIO
        dm = DeploymentManager()
        pkg = dm.create_zip_package("TestBot", "1.0.0", files={"main.py": b"pass"})
        zb = dm.get_zip_bytes(pkg.package_id)
        with zipfile.ZipFile(BytesIO(zb)) as zf:
            names = zf.namelist()
        assert "install.json" in names
        assert "main.py" in names

    def test_get_zip_bytes(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package("Bot", "0.1", files={"f.py": b"x=1"})
        zb = dm.get_zip_bytes(pkg.package_id)
        assert isinstance(zb, bytes)
        assert len(zb) > 0

    def test_checksum_validation_passes(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package("Bot", "1.0", files={"f.py": b"x=1"})
        assert dm.validate_package(pkg.package_id, pkg.checksum) is True

    def test_checksum_validation_fails(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package("Bot", "1.0", files={"f.py": b"x=1"})
        assert dm.validate_package(pkg.package_id, "deadbeef") is False

    def test_create_boot_config(self):
        dm = DeploymentManager()
        config = dm.create_boot_config(label="Buddy OS v1", timeout_seconds=15)
        assert config.label == "Buddy OS v1"
        assert config.timeout_seconds == 15
        assert "buddy_os" in config.entries

    def test_add_boot_entry(self):
        dm = DeploymentManager()
        config = dm.create_boot_config()
        dm.add_boot_entry(config.config_id, "recovery", "/boot/recovery.img", args="rescue")
        assert "recovery" in dm.get_boot_config(config.config_id).entries

    def test_set_default_boot_entry(self):
        dm = DeploymentManager()
        config = dm.create_boot_config()
        dm.add_boot_entry(config.config_id, "safe_mode", "/boot/safe.img")
        dm.set_default_boot_entry(config.config_id, "safe_mode")
        assert dm.get_boot_config(config.config_id).default_entry == "safe_mode"

    def test_set_nonexistent_default_raises(self):
        dm = DeploymentManager()
        config = dm.create_boot_config()
        with pytest.raises(KeyError):
            dm.set_default_boot_entry(config.config_id, "nonexistent")

    def test_generate_iso_manifest(self):
        dm = DeploymentManager()
        config = dm.create_boot_config()
        manifest = dm.generate_iso_manifest(config.config_id)
        assert manifest["format"] == PackageFormat.ISO.value
        assert "filesystem_layout" in manifest
        assert "instructions" in manifest

    def test_install_bot_usb(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package("Bot", "1.0", files={"main.py": b"pass"})
        record = dm.install_bot(pkg.package_id, method=InstallMethod.USB)
        assert record.method == InstallMethod.USB
        assert record.active is True
        assert dm.get_package(pkg.package_id).status == PackageStatus.INSTALLED

    def test_install_bot_wifi(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package("Bot", "1.0", files={"main.py": b"pass"})
        record = dm.install_bot(pkg.package_id, method=InstallMethod.WIFI)
        assert record.method == InstallMethod.WIFI

    def test_uninstall_bot(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package("Bot", "1.0", files={"main.py": b"pass"})
        record = dm.install_bot(pkg.package_id)
        dm.uninstall_bot(record.record_id)
        assert not dm.get_install_record(record.record_id).active

    def test_install_not_ready_package_raises(self):
        import uuid as _uuid
        dm = DeploymentManager()
        pkg_id = f"pkg_{_uuid.uuid4().hex[:8]}"
        dm._packages[pkg_id] = BotPackage(
            package_id=pkg_id,
            bot_name="Pending",
            version="1.0",
            fmt=PackageFormat.ZIP,
            status=PackageStatus.PENDING,
        )
        with pytest.raises(RuntimeError, match="not ready"):
            dm.install_bot(pkg_id)

    def test_list_installed_bots(self):
        dm = DeploymentManager()
        pkg1 = dm.create_zip_package("BotA", "1.0", files={"f.py": b"x"})
        pkg2 = dm.create_zip_package("BotB", "2.0", files={"f.py": b"y"})
        r1 = dm.install_bot(pkg1.package_id)
        r2 = dm.install_bot(pkg2.package_id)
        dm.uninstall_bot(r2.record_id)
        active = dm.list_installed_bots(active_only=True)
        assert len(active) == 1
        assert active[0].bot_name == "BotA"

    def test_package_not_found_raises(self):
        dm = DeploymentManager()
        with pytest.raises(KeyError):
            dm.get_package("pkg_9999")

    def test_boot_config_not_found_raises(self):
        dm = DeploymentManager()
        with pytest.raises(KeyError):
            dm.get_boot_config("boot_9999")

    def test_install_record_not_found_raises(self):
        dm = DeploymentManager()
        with pytest.raises(KeyError):
            dm.get_install_record("inst_9999")

    def test_package_to_dict(self):
        dm = DeploymentManager()
        pkg = dm.create_zip_package("Bot", "1.0", files={"f.py": b"x"})
        d = pkg.to_dict()
        assert d["bot_name"] == "Bot"
        assert d["format"] == PackageFormat.ZIP.value


# ===========================================================================
# New tier feature-flag tests
# ===========================================================================


class TestNewTierFeatures:
    def test_free_has_wifi(self):
        assert FEATURE_WIFI in get_tier_config(Tier.FREE).features

    def test_free_has_security_manager(self):
        assert FEATURE_SECURITY_MANAGER in get_tier_config(Tier.FREE).features

    def test_pro_has_hardware_protocols(self):
        assert FEATURE_HARDWARE_PROTOCOLS in get_tier_config(Tier.PRO).features

    def test_pro_has_deployment_manager(self):
        assert FEATURE_DEPLOYMENT_MANAGER in get_tier_config(Tier.PRO).features

    def test_pro_has_flash_boot(self):
        assert FEATURE_FLASH_BOOT in get_tier_config(Tier.PRO).features

    def test_enterprise_has_cloud_sync(self):
        assert FEATURE_CLOUD_SYNC in get_tier_config(Tier.ENTERPRISE).features

    def test_free_lacks_cloud_sync(self):
        assert FEATURE_CLOUD_SYNC not in get_tier_config(Tier.FREE).features


# ===========================================================================
# BuddyOS integration tests for new subsystems
# ===========================================================================

class TestBuddyOSNewSubsystems:
    def test_has_wifi_engine(self):
        buddy = BuddyOS()
        assert isinstance(buddy.wifi, WiFiEngine)

    def test_has_hardware_hub(self):
        buddy = BuddyOS()
        assert isinstance(buddy.hardware, HardwareProtocolsHub)

    def test_has_security_manager(self):
        buddy = BuddyOS()
        assert isinstance(buddy.security, SecurityManager)

    def test_has_deployment_manager(self):
        buddy = BuddyOS()
        assert isinstance(buddy.deployment, DeploymentManager)

    def test_system_status_includes_wifi(self):
        buddy = BuddyOS()
        status = buddy.system_status()
        assert "wifi" in status

    def test_system_status_includes_hardware(self):
        buddy = BuddyOS()
        status = buddy.system_status()
        assert "hardware_protocols" in status

    def test_system_status_includes_security(self):
        buddy = BuddyOS()
        status = buddy.system_status()
        assert "security" in status

    def test_system_status_includes_deployment(self):
        buddy = BuddyOS()
        status = buddy.system_status()
        assert "deployment" in status

    def test_chat_wifi(self):
        buddy = BuddyOS()
        resp = buddy.chat("wifi status")
        assert resp["response"] == "buddy_os"
        assert "wifi" in resp["data"]

    def test_chat_wireless(self):
        buddy = BuddyOS()
        resp = buddy.chat("wireless network status")
        assert "wifi" in resp["data"]

    def test_chat_hardware(self):
        buddy = BuddyOS()
        resp = buddy.chat("hardware protocols")
        assert "hardware" in resp["data"]

    def test_chat_uart(self):
        buddy = BuddyOS()
        resp = buddy.chat("uart protocol info")
        assert "hardware" in resp["data"]

    def test_chat_i2c(self):
        buddy = BuddyOS()
        resp = buddy.chat("i2c bus scan")
        assert "hardware" in resp["data"]

    def test_chat_obd(self):
        buddy = BuddyOS()
        resp = buddy.chat("obd diagnostics")
        assert "hardware" in resp["data"]

    def test_chat_security(self):
        buddy = BuddyOS()
        resp = buddy.chat("security status")
        assert "security" in resp["data"]

    def test_chat_auth(self):
        buddy = BuddyOS()
        resp = buddy.chat("auth tokens")
        assert "security" in resp["data"]

    def test_chat_deploy(self):
        buddy = BuddyOS()
        resp = buddy.chat("deploy bot")
        assert "deployment" in resp["data"]

    def test_chat_flash(self):
        buddy = BuddyOS()
        resp = buddy.chat("flash drive boot")
        assert "deployment" in resp["data"]

    def test_chat_zip(self):
        buddy = BuddyOS()
        resp = buddy.chat("create zip package")
        assert "deployment" in resp["data"]

    def test_chat_install(self):
        buddy = BuddyOS()
        resp = buddy.chat("install bot")
        assert "deployment" in resp["data"]

    def test_boot_log_mentions_new_subsystems(self):
        buddy = BuddyOS()
        log = buddy.get_boot_log()
        log_str = " ".join(log).lower()
        assert "wifi" in log_str
        assert "security" in log_str
        assert "hardware" in log_str
        assert "deployment" in log_str

    def test_default_chat_mentions_new_features(self):
        buddy = BuddyOS()
        resp = buddy.chat("hello there")
        msg = resp["message"].lower()
        assert "wifi" in msg or "hardware" in msg or "security" in msg
