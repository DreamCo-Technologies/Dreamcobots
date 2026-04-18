"""
Buddy OS — WiFi Engine

Provides WiFi connectivity management for Buddy OS:
  • Network scanning and discovery
  • WPA/WPA2/WPA3 authentication
  • Connection lifecycle management
  • IoT device pairing over WiFi
  • Hotspot (access-point) mode
  • Network profile persistence

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class WiFiSecurity(Enum):
    OPEN = "open"
    WEP = "wep"
    WPA = "wpa"
    WPA2 = "wpa2"
    WPA3 = "wpa3"
    WPA2_ENTERPRISE = "wpa2_enterprise"


class WiFiBand(Enum):
    BAND_2_4GHZ = "2.4GHz"
    BAND_5GHZ = "5GHz"
    BAND_6GHZ = "6GHz"    # WiFi 6E / 7


class WiFiConnectionState(Enum):
    DISCONNECTED = "disconnected"
    SCANNING = "scanning"
    AUTHENTICATING = "authenticating"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class HotspotState(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class WiFiNetwork:
    """Represents a discovered WiFi network."""

    ssid: str
    bssid: str
    signal_dbm: int = -70
    channel: int = 6
    band: WiFiBand = WiFiBand.BAND_2_4GHZ
    security: WiFiSecurity = WiFiSecurity.WPA2
    hidden: bool = False

    def to_dict(self) -> dict:
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "signal_dbm": self.signal_dbm,
            "channel": self.channel,
            "band": self.band.value,
            "security": self.security.value,
            "hidden": self.hidden,
        }


@dataclass
class WiFiConnection:
    """Represents an active or saved WiFi connection profile."""

    connection_id: str
    ssid: str
    bssid: str = ""
    security: WiFiSecurity = WiFiSecurity.WPA2
    ip_address: str = ""
    gateway: str = ""
    dns: list = field(default_factory=list)
    state: WiFiConnectionState = WiFiConnectionState.DISCONNECTED
    signal_dbm: int = -70
    auto_reconnect: bool = True

    def is_connected(self) -> bool:
        return self.state == WiFiConnectionState.CONNECTED

    def to_dict(self) -> dict:
        return {
            "connection_id": self.connection_id,
            "ssid": self.ssid,
            "bssid": self.bssid,
            "security": self.security.value,
            "ip_address": self.ip_address,
            "gateway": self.gateway,
            "state": self.state.value,
            "signal_dbm": self.signal_dbm,
            "auto_reconnect": self.auto_reconnect,
        }


@dataclass
class WiFiHotspot:
    """Represents a hosted WiFi access point."""

    hotspot_id: str
    ssid: str
    password: str
    band: WiFiBand = WiFiBand.BAND_2_4GHZ
    security: WiFiSecurity = WiFiSecurity.WPA2
    channel: int = 6
    max_clients: int = 10
    state: HotspotState = HotspotState.INACTIVE
    connected_clients: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "hotspot_id": self.hotspot_id,
            "ssid": self.ssid,
            "band": self.band.value,
            "security": self.security.value,
            "channel": self.channel,
            "max_clients": self.max_clients,
            "state": self.state.value,
            "client_count": len(self.connected_clients),
        }


@dataclass
class IoTWiFiDevice:
    """Represents an IoT device paired over WiFi."""

    device_id: str
    name: str
    mac_address: str
    ip_address: str = ""
    device_type: str = "generic"
    online: bool = False
    state: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "mac_address": self.mac_address,
            "ip_address": self.ip_address,
            "device_type": self.device_type,
            "online": self.online,
        }


# ---------------------------------------------------------------------------
# WiFi Engine
# ---------------------------------------------------------------------------

class WiFiEngine:
    """
    Manages WiFi connectivity, network scanning, IoT pairing, and hotspot mode.
    """

    def __init__(self) -> None:
        self._scanning: bool = False
        self._networks: dict[str, WiFiNetwork] = {}          # keyed by BSSID
        self._connections: dict[str, WiFiConnection] = {}    # keyed by connection_id
        self._active_connection_id: Optional[str] = None
        self._hotspot: Optional[WiFiHotspot] = None
        self._iot_devices: dict[str, IoTWiFiDevice] = {}

    # ------------------------------------------------------------------
    # Scanning
    # ------------------------------------------------------------------

    def start_scan(self) -> dict:
        self._scanning = True
        return {"scanning": True}

    def stop_scan(self) -> dict:
        self._scanning = False
        return {"scanning": False, "networks_found": len(self._networks)}

    def add_discovered_network(
        self,
        ssid: str,
        bssid: str,
        signal_dbm: int = -70,
        channel: int = 6,
        band: WiFiBand = WiFiBand.BAND_2_4GHZ,
        security: WiFiSecurity = WiFiSecurity.WPA2,
        hidden: bool = False,
    ) -> WiFiNetwork:
        """Register a discovered network (used by hardware bridge / tests)."""
        net = WiFiNetwork(
            ssid=ssid,
            bssid=bssid,
            signal_dbm=signal_dbm,
            channel=channel,
            band=band,
            security=security,
            hidden=hidden,
        )
        self._networks[bssid] = net
        return net

    def list_networks(
        self,
        min_signal_dbm: Optional[int] = None,
        security: Optional[WiFiSecurity] = None,
    ) -> list[WiFiNetwork]:
        nets = list(self._networks.values())
        if min_signal_dbm is not None:
            nets = [n for n in nets if n.signal_dbm >= min_signal_dbm]
        if security is not None:
            nets = [n for n in nets if n.security == security]
        return nets

    def get_network(self, bssid: str) -> WiFiNetwork:
        if bssid not in self._networks:
            raise KeyError(f"WiFi network with BSSID '{bssid}' not found.")
        return self._networks[bssid]

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(
        self,
        ssid: str,
        password: str = "",
        bssid: str = "",
        auto_reconnect: bool = True,
    ) -> WiFiConnection:
        """Connect to a WiFi network by SSID (and optionally BSSID)."""
        connection_id = f"wifi_{uuid.uuid4().hex[:8]}"
        # Determine security from known networks, default WPA2
        security = WiFiSecurity.WPA2
        for net in self._networks.values():
            if net.ssid == ssid and (not bssid or net.bssid == bssid):
                security = net.security
                if not bssid:
                    bssid = net.bssid
                break
        if security == WiFiSecurity.OPEN:
            password = ""
        elif not password:
            raise ValueError(f"Password required for {security.value} network '{ssid}'.")

        conn = WiFiConnection(
            connection_id=connection_id,
            ssid=ssid,
            bssid=bssid,
            security=security,
            state=WiFiConnectionState.CONNECTED,
            auto_reconnect=auto_reconnect,
        )
        self._connections[connection_id] = conn
        self._active_connection_id = connection_id
        return conn

    def disconnect(self, connection_id: Optional[str] = None) -> WiFiConnection:
        """Disconnect the specified (or active) connection."""
        cid = connection_id or self._active_connection_id
        if cid is None:
            raise RuntimeError("No active WiFi connection to disconnect.")
        conn = self._get_connection(cid)
        conn.state = WiFiConnectionState.DISCONNECTED
        if self._active_connection_id == cid:
            self._active_connection_id = None
        return conn

    def get_active_connection(self) -> Optional[WiFiConnection]:
        if self._active_connection_id is None:
            return None
        return self._connections.get(self._active_connection_id)

    def list_connections(self, connected_only: bool = False) -> list[WiFiConnection]:
        conns = list(self._connections.values())
        if connected_only:
            conns = [c for c in conns if c.is_connected()]
        return conns

    def get_connection(self, connection_id: str) -> WiFiConnection:
        return self._get_connection(connection_id)

    def forget_network(self, connection_id: str) -> None:
        """Remove a saved network profile."""
        conn = self._get_connection(connection_id)
        if conn.is_connected():
            self.disconnect(connection_id)
        del self._connections[connection_id]

    # ------------------------------------------------------------------
    # Hotspot (Access Point) mode
    # ------------------------------------------------------------------

    def create_hotspot(
        self,
        ssid: str,
        password: str,
        band: WiFiBand = WiFiBand.BAND_2_4GHZ,
        channel: int = 6,
        max_clients: int = 10,
    ) -> WiFiHotspot:
        """Create and start a WiFi hotspot."""
        if len(password) < 8:
            raise ValueError("Hotspot password must be at least 8 characters.")
        hotspot_id = f"ap_{uuid.uuid4().hex[:8]}"
        self._hotspot = WiFiHotspot(
            hotspot_id=hotspot_id,
            ssid=ssid,
            password=password,
            band=band,
            channel=channel,
            max_clients=max_clients,
            state=HotspotState.ACTIVE,
        )
        return self._hotspot

    def stop_hotspot(self) -> WiFiHotspot:
        if self._hotspot is None:
            raise RuntimeError("No active hotspot.")
        self._hotspot.state = HotspotState.INACTIVE
        return self._hotspot

    def get_hotspot(self) -> Optional[WiFiHotspot]:
        return self._hotspot

    def add_hotspot_client(self, mac_address: str) -> None:
        """Simulate a client joining the hotspot."""
        if self._hotspot is None or self._hotspot.state != HotspotState.ACTIVE:
            raise RuntimeError("Hotspot is not active.")
        if len(self._hotspot.connected_clients) >= self._hotspot.max_clients:
            raise RuntimeError("Hotspot client limit reached.")
        if mac_address not in self._hotspot.connected_clients:
            self._hotspot.connected_clients.append(mac_address)

    # ------------------------------------------------------------------
    # IoT device pairing
    # ------------------------------------------------------------------

    def pair_iot_device(
        self,
        name: str,
        mac_address: str,
        ip_address: str = "",
        device_type: str = "generic",
    ) -> IoTWiFiDevice:
        """Pair a WiFi-connected IoT device."""
        device_id = f"iot_{uuid.uuid4().hex[:8]}"
        dev = IoTWiFiDevice(
            device_id=device_id,
            name=name,
            mac_address=mac_address,
            ip_address=ip_address,
            device_type=device_type,
            online=True,
        )
        self._iot_devices[device_id] = dev
        return dev

    def set_iot_device_online(self, device_id: str, online: bool) -> IoTWiFiDevice:
        dev = self._get_iot(device_id)
        dev.online = online
        return dev

    def update_iot_state(self, device_id: str, state: dict) -> IoTWiFiDevice:
        dev = self._get_iot(device_id)
        dev.state.update(state)
        return dev

    def list_iot_devices(self, online_only: bool = False) -> list[IoTWiFiDevice]:
        devs = list(self._iot_devices.values())
        if online_only:
            devs = [d for d in devs if d.online]
        return devs

    def get_iot_device(self, device_id: str) -> IoTWiFiDevice:
        return self._get_iot(device_id)

    def remove_iot_device(self, device_id: str) -> None:
        self._get_iot(device_id)
        del self._iot_devices[device_id]

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict:
        active = self.get_active_connection()
        return {
            "scanning": self._scanning,
            "known_networks": len(self._networks),
            "active_ssid": active.ssid if active else None,
            "hotspot_active": (
                self._hotspot is not None
                and self._hotspot.state == HotspotState.ACTIVE
            ),
            "iot_devices": len(self._iot_devices),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_connection(self, connection_id: str) -> WiFiConnection:
        if connection_id not in self._connections:
            raise KeyError(f"WiFi connection '{connection_id}' not found.")
        return self._connections[connection_id]

    def _get_iot(self, device_id: str) -> IoTWiFiDevice:
        if device_id not in self._iot_devices:
            raise KeyError(f"IoT WiFi device '{device_id}' not found.")
        return self._iot_devices[device_id]
