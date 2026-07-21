"""
Buddy OS — Device Manager

Manages universal device compatibility across:
  TVs, gaming consoles, phones, tablets, computers (Windows/Linux/macOS),
  Apple ecosystem, Google/Android ecosystem, and smart-home devices.

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class DeviceType(Enum):
    TV = "tv"
    GAMING_CONSOLE = "gaming_console"
    PHONE = "phone"
    TABLET = "tablet"
    COMPUTER = "computer"
    SMART_HOME = "smart_home"
    WEARABLE = "wearable"
    UNKNOWN = "unknown"


class DevicePlatform(Enum):
    APPLE = "apple"
    GOOGLE = "google"
    WINDOWS = "windows"
    LINUX = "linux"
    SAMSUNG = "samsung"
    SONY = "sony"
    MICROSOFT = "microsoft"
    GENERIC = "generic"


class DeviceStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PAIRING = "pairing"
    ERROR = "error"


@dataclass
class Device:
    """Represents a managed device."""

    device_id: str
    name: str
    device_type: DeviceType
    platform: DevicePlatform
    os_version: str = ""
    status: DeviceStatus = DeviceStatus.DISCONNECTED
    capabilities: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def is_connected(self) -> bool:
        return self.status == DeviceStatus.CONNECTED

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "type": self.device_type.value,
            "platform": self.platform.value,
            "os_version": self.os_version,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
        }


# Supported platforms per device type
DEVICE_COMPATIBILITY_MATRIX: dict = {
    DeviceType.TV: [
        DevicePlatform.SAMSUNG,
        DevicePlatform.SONY,
        DevicePlatform.GOOGLE,
        DevicePlatform.APPLE,
        DevicePlatform.GENERIC,
    ],
    DeviceType.GAMING_CONSOLE: [
        DevicePlatform.SONY,
        DevicePlatform.MICROSOFT,
        DevicePlatform.GENERIC,
    ],
    DeviceType.PHONE: [
        DevicePlatform.APPLE,
        DevicePlatform.GOOGLE,
        DevicePlatform.SAMSUNG,
        DevicePlatform.GENERIC,
    ],
    DeviceType.TABLET: [
        DevicePlatform.APPLE,
        DevicePlatform.GOOGLE,
        DevicePlatform.SAMSUNG,
        DevicePlatform.MICROSOFT,
    ],
    DeviceType.COMPUTER: [
        DevicePlatform.APPLE,
        DevicePlatform.WINDOWS,
        DevicePlatform.LINUX,
    ],
    DeviceType.SMART_HOME: [
        DevicePlatform.GOOGLE,
        DevicePlatform.APPLE,
        DevicePlatform.GENERIC,
    ],
    DeviceType.WEARABLE: [
        DevicePlatform.APPLE,
        DevicePlatform.GOOGLE,
        DevicePlatform.SAMSUNG,
    ],
}


class DeviceManager:
    """
    Manages all devices connected to the Buddy OS.

    Supports universal compatibility across TVs, gaming consoles, phones,
    tablets, computers, Apple/Google ecosystems, and smart-home devices.
    """

    def __init__(self, max_devices: Optional[int] = None) -> None:
        self._devices: dict[str, Device] = {}
        self._device_counter: int = 0
        self._max_devices = max_devices

    # ------------------------------------------------------------------
    # Device registration
    # ------------------------------------------------------------------

    def register_device(
        self,
        name: str,
        device_type: DeviceType,
        platform: DevicePlatform,
        os_version: str = "",
        capabilities: Optional[list] = None,
        metadata: Optional[dict] = None,
    ) -> Device:
        """Register a new device with the Buddy OS."""
        if self._max_devices is not None and len(self._devices) >= self._max_devices:
            raise RuntimeError(
                f"Device limit of {self._max_devices} reached. Upgrade your tier."
            )
        if not self._is_compatible(device_type, platform):
            raise ValueError(
                f"{platform.value} is not supported for {device_type.value} devices."
            )
        self._device_counter += 1
        device_id = f"dev_{self._device_counter:04d}"
        device = Device(
            device_id=device_id,
            name=name,
            device_type=device_type,
            platform=platform,
            os_version=os_version,
            status=DeviceStatus.DISCONNECTED,
            capabilities=list(capabilities or []),
            metadata=dict(metadata or {}),
        )
        self._devices[device_id] = device
        return device

    def remove_device(self, device_id: str) -> None:
        """Remove a device from the manager."""
        self._devices.pop(device_id, None)

    # ------------------------------------------------------------------
    # Connection control
    # ------------------------------------------------------------------

    def connect(self, device_id: str) -> Device:
        """Mark a device as connected."""
        device = self._get(device_id)
        device.status = DeviceStatus.CONNECTED
        return device

    def disconnect(self, device_id: str) -> Device:
        """Mark a device as disconnected."""
        device = self._get(device_id)
        device.status = DeviceStatus.DISCONNECTED
        return device

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_devices(
        self,
        device_type: Optional[DeviceType] = None,
        platform: Optional[DevicePlatform] = None,
    ) -> list[Device]:
        """Return devices, optionally filtered by type or platform."""
        devices = list(self._devices.values())
        if device_type is not None:
            devices = [d for d in devices if d.device_type == device_type]
        if platform is not None:
            devices = [d for d in devices if d.platform == platform]
        return devices

    def get_connected_devices(self) -> list[Device]:
        """Return all currently connected devices."""
        return [d for d in self._devices.values() if d.is_connected()]

    def get_device(self, device_id: str) -> Device:
        return self._get(device_id)

    def get_compatibility_matrix(self) -> dict:
        """Return the full device-platform compatibility matrix as a dict."""
        return {
            dtype.value: [p.value for p in platforms]
            for dtype, platforms in DEVICE_COMPATIBILITY_MATRIX.items()
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, device_id: str) -> Device:
        if device_id not in self._devices:
            raise KeyError(f"Device '{device_id}' not found.")
        return self._devices[device_id]

    @staticmethod
    def _is_compatible(device_type: DeviceType, platform: DevicePlatform) -> bool:
        supported = DEVICE_COMPATIBILITY_MATRIX.get(device_type, [])
        return platform in supported
