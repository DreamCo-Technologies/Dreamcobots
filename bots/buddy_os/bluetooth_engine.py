"""
Buddy OS — Bluetooth Engine

Provides Bluetooth functionality including device discovery, pairing,
file transfer, and data streaming to nearby Bluetooth-enabled devices.

Supports:
  - BlueZ (Linux/Raspberry Pi)
  - CoreBluetooth (Apple iOS/macOS)
  - Android Bluetooth API
  - Windows Bluetooth API

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class BluetoothProfileType(Enum):
    """Standard Bluetooth profiles."""
    A2DP = "a2dp"           # Advanced Audio Distribution (stereo audio)
    HFP = "hfp"             # Hands-Free Profile (calls)
    HID = "hid"             # Human Interface Device (keyboards, mice)
    OPP = "opp"             # Object Push Profile (file transfer)
    FTP = "ftp"             # File Transfer Profile
    PAN = "pan"             # Personal Area Network
    GATT = "gatt"           # Generic Attribute (BLE sensors)
    SPP = "spp"             # Serial Port Profile (raw data stream)


class BluetoothState(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    PAIRING = "pairing"
    PAIRED = "paired"
    CONNECTED = "connected"
    TRANSFERRING = "transferring"
    ERROR = "error"


@dataclass
class BluetoothDevice:
    """Represents a discovered or paired Bluetooth device."""

    address: str
    name: str
    rssi: int = -70
    profiles: list = field(default_factory=list)
    state: BluetoothState = BluetoothState.IDLE
    paired: bool = False
    trusted: bool = False
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "name": self.name,
            "rssi": self.rssi,
            "profiles": [p if isinstance(p, str) else p.value for p in self.profiles],
            "state": self.state.value,
            "paired": self.paired,
            "trusted": self.trusted,
        }


@dataclass
class FileTransfer:
    """Represents an in-progress or completed file transfer."""

    transfer_id: str
    source_address: str
    destination_address: str
    filename: str
    file_size_bytes: int
    bytes_transferred: int = 0
    status: str = "pending"

    @property
    def progress_pct(self) -> float:
        if self.file_size_bytes == 0:
            return 100.0
        return round(self.bytes_transferred / self.file_size_bytes * 100, 1)

    def to_dict(self) -> dict:
        return {
            "transfer_id": self.transfer_id,
            "source": self.source_address,
            "destination": self.destination_address,
            "filename": self.filename,
            "file_size_bytes": self.file_size_bytes,
            "bytes_transferred": self.bytes_transferred,
            "progress_pct": self.progress_pct,
            "status": self.status,
        }


class BluetoothEngine:
    """
    Buddy OS Bluetooth subsystem.

    Handles device discovery, pairing, connection management,
    file transfer, and data streaming over Bluetooth.
    """

    def __init__(self, max_paired: Optional[int] = None) -> None:
        self._discovered: dict[str, BluetoothDevice] = {}
        self._paired: dict[str, BluetoothDevice] = {}
        self._transfers: dict[str, FileTransfer] = {}
        self._transfer_counter: int = 0
        self._max_paired = max_paired
        self._scanning: bool = False

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def start_scan(self) -> dict:
        """Start scanning for nearby Bluetooth devices."""
        self._scanning = True
        return {"scanning": True, "message": "Bluetooth scan started."}

    def stop_scan(self) -> dict:
        """Stop the Bluetooth scan."""
        self._scanning = False
        return {"scanning": False, "message": "Bluetooth scan stopped."}

    def add_discovered_device(
        self,
        address: str,
        name: str,
        rssi: int = -70,
        profiles: Optional[list] = None,
    ) -> BluetoothDevice:
        """Add a device to the discovered list (simulates scan result)."""
        device = BluetoothDevice(
            address=address,
            name=name,
            rssi=rssi,
            profiles=list(profiles or [BluetoothProfileType.GATT]),
        )
        self._discovered[address] = device
        return device

    def get_discovered_devices(self) -> list[BluetoothDevice]:
        """Return the list of discovered (not yet paired) devices."""
        return [d for d in self._discovered.values() if not d.paired]

    # ------------------------------------------------------------------
    # Pairing
    # ------------------------------------------------------------------

    def pair_device(self, address: str) -> BluetoothDevice:
        """Pair with a discovered Bluetooth device."""
        if self._max_paired is not None and len(self._paired) >= self._max_paired:
            raise RuntimeError(
                f"Pairing limit of {self._max_paired} reached. Upgrade your tier."
            )
        if address not in self._discovered:
            raise KeyError(f"Device '{address}' not found in discovered list.")
        device = self._discovered[address]
        device.paired = True
        device.state = BluetoothState.PAIRED
        self._paired[address] = device
        return device

    def unpair_device(self, address: str) -> None:
        """Remove a paired Bluetooth device."""
        if address in self._paired:
            self._paired[address].paired = False
            self._paired[address].state = BluetoothState.IDLE
            del self._paired[address]

    def trust_device(self, address: str) -> BluetoothDevice:
        """Mark a paired device as trusted (auto-reconnect)."""
        device = self._get_paired(address)
        device.trusted = True
        return device

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self, address: str) -> BluetoothDevice:
        """Connect to a paired device."""
        device = self._get_paired(address)
        device.state = BluetoothState.CONNECTED
        return device

    def disconnect(self, address: str) -> BluetoothDevice:
        """Disconnect from a connected device."""
        device = self._get_paired(address)
        device.state = BluetoothState.PAIRED
        return device

    def get_connected_devices(self) -> list[BluetoothDevice]:
        """Return all currently connected Bluetooth devices."""
        return [d for d in self._paired.values() if d.state == BluetoothState.CONNECTED]

    # ------------------------------------------------------------------
    # File transfer
    # ------------------------------------------------------------------

    def send_file(
        self,
        destination_address: str,
        filename: str,
        file_size_bytes: int,
        source_address: str = "local",
    ) -> FileTransfer:
        """Initiate a Bluetooth file transfer (OPP/FTP profile)."""
        device = self._get_paired(destination_address)
        if device.state != BluetoothState.CONNECTED:
            raise RuntimeError(
                f"Device '{destination_address}' is not connected."
            )
        self._transfer_counter += 1
        transfer_id = f"bt_xfer_{self._transfer_counter:04d}"
        transfer = FileTransfer(
            transfer_id=transfer_id,
            source_address=source_address,
            destination_address=destination_address,
            filename=filename,
            file_size_bytes=file_size_bytes,
            bytes_transferred=0,
            status="in_progress",
        )
        self._transfers[transfer_id] = transfer
        return transfer

    def update_transfer_progress(
        self, transfer_id: str, bytes_transferred: int
    ) -> FileTransfer:
        """Update progress on an active file transfer."""
        transfer = self._get_transfer(transfer_id)
        transfer.bytes_transferred = min(bytes_transferred, transfer.file_size_bytes)
        if transfer.bytes_transferred >= transfer.file_size_bytes:
            transfer.status = "completed"
        return transfer

    def get_transfer(self, transfer_id: str) -> FileTransfer:
        return self._get_transfer(transfer_id)

    def list_transfers(self) -> list[FileTransfer]:
        return list(self._transfers.values())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_paired(self, address: str) -> BluetoothDevice:
        if address not in self._paired:
            raise KeyError(f"Device '{address}' is not paired.")
        return self._paired[address]

    def _get_transfer(self, transfer_id: str) -> FileTransfer:
        if transfer_id not in self._transfers:
            raise KeyError(f"Transfer '{transfer_id}' not found.")
        return self._transfers[transfer_id]
