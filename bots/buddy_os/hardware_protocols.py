"""
Buddy OS — Hardware Protocols Engine

Provides low-level hardware communication protocols for Buddy OS:
  • UART  — Universal Asynchronous Receiver-Transmitter (serial)
  • I2C   — Inter-Integrated Circuit (two-wire sensor bus)
  • SPI   — Serial Peripheral Interface (four-wire high-speed bus)
  • OBD-II — On-Board Diagnostics II (automotive diagnostics via ELM327)

All channels are simulated in software; real hardware adapters can be
plugged in by swapping the transport layer.

GLOBAL AI SOURCES FLOW: participates via buddy_os.py pipeline.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ProtocolType(Enum):
    UART = "uart"
    I2C = "i2c"
    SPI = "spi"
    OBD2 = "obd2"


class ChannelState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    ERROR = "error"


class UARTParity(Enum):
    NONE = "none"
    EVEN = "even"
    ODD = "odd"


class SPIMode(Enum):
    MODE_0 = 0   # CPOL=0, CPHA=0
    MODE_1 = 1   # CPOL=0, CPHA=1
    MODE_2 = 2   # CPOL=1, CPHA=0
    MODE_3 = 3   # CPOL=1, CPHA=1


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class UARTChannel:
    """Represents a UART (serial) communication channel."""

    channel_id: str
    port: str
    baud_rate: int = 9600
    data_bits: int = 8
    parity: UARTParity = UARTParity.NONE
    stop_bits: float = 1.0
    state: ChannelState = ChannelState.CLOSED
    rx_buffer: list = field(default_factory=list)
    tx_buffer: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "channel_id": self.channel_id,
            "protocol": ProtocolType.UART.value,
            "port": self.port,
            "baud_rate": self.baud_rate,
            "data_bits": self.data_bits,
            "parity": self.parity.value,
            "stop_bits": self.stop_bits,
            "state": self.state.value,
        }


@dataclass
class I2CDevice:
    """Represents a device on the I2C bus."""

    device_id: str
    address: int          # 7-bit or 10-bit I2C address (0x00-0x7F)
    name: str
    bus: int = 1          # Linux i2c bus number
    state: ChannelState = ChannelState.CLOSED
    registers: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "protocol": ProtocolType.I2C.value,
            "address": hex(self.address),
            "name": self.name,
            "bus": self.bus,
            "state": self.state.value,
        }


@dataclass
class SPIDevice:
    """Represents a device connected via SPI."""

    device_id: str
    bus: int
    chip_select: int
    name: str
    clock_hz: int = 1_000_000
    mode: SPIMode = SPIMode.MODE_0
    bits_per_word: int = 8
    state: ChannelState = ChannelState.CLOSED

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "protocol": ProtocolType.SPI.value,
            "bus": self.bus,
            "chip_select": self.chip_select,
            "name": self.name,
            "clock_hz": self.clock_hz,
            "mode": self.mode.value,
            "bits_per_word": self.bits_per_word,
            "state": self.state.value,
        }


@dataclass
class OBD2Session:
    """Represents an OBD-II diagnostic session with a vehicle."""

    session_id: str
    port: str                    # Serial port or Bluetooth address of ELM327
    vehicle_vin: str = ""
    state: ChannelState = ChannelState.CLOSED
    dtc_codes: list = field(default_factory=list)   # Diagnostic Trouble Codes
    live_data: dict = field(default_factory=dict)   # PIDs: rpm, speed, temp…

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "protocol": ProtocolType.OBD2.value,
            "port": self.port,
            "vehicle_vin": self.vehicle_vin,
            "state": self.state.value,
            "dtc_count": len(self.dtc_codes),
            "live_data_keys": list(self.live_data.keys()),
        }


# ---------------------------------------------------------------------------
# UART Manager
# ---------------------------------------------------------------------------

class UARTManager:
    """Manages UART (serial) channels."""

    def __init__(self) -> None:
        self._channels: dict[str, UARTChannel] = {}

    def open_channel(
        self,
        port: str,
        baud_rate: int = 9600,
        data_bits: int = 8,
        parity: UARTParity = UARTParity.NONE,
        stop_bits: float = 1.0,
    ) -> UARTChannel:
        """Open a new UART channel on *port*."""
        channel_id = f"uart_{uuid.uuid4().hex[:8]}"
        ch = UARTChannel(
            channel_id=channel_id,
            port=port,
            baud_rate=baud_rate,
            data_bits=data_bits,
            parity=parity,
            stop_bits=stop_bits,
            state=ChannelState.OPEN,
        )
        self._channels[channel_id] = ch
        return ch

    def close_channel(self, channel_id: str) -> UARTChannel:
        ch = self._get(channel_id)
        ch.state = ChannelState.CLOSED
        return ch

    def write(self, channel_id: str, data: bytes) -> int:
        """Write bytes to the TX buffer. Returns bytes written."""
        ch = self._get_open(channel_id)
        ch.tx_buffer.append(data)
        return len(data)

    def read(self, channel_id: str, size: int = 64) -> bytes:
        """Read up to *size* bytes from the RX buffer."""
        ch = self._get_open(channel_id)
        if not ch.rx_buffer:
            return b""
        raw = ch.rx_buffer.pop(0)
        return raw[:size]

    def inject_rx(self, channel_id: str, data: bytes) -> None:
        """Inject bytes into RX buffer (for testing / hardware bridge)."""
        ch = self._get(channel_id)
        ch.rx_buffer.append(data)

    def list_channels(self) -> list[UARTChannel]:
        return list(self._channels.values())

    def get_channel(self, channel_id: str) -> UARTChannel:
        return self._get(channel_id)

    # helpers
    def _get(self, channel_id: str) -> UARTChannel:
        if channel_id not in self._channels:
            raise KeyError(f"UART channel '{channel_id}' not found.")
        return self._channels[channel_id]

    def _get_open(self, channel_id: str) -> UARTChannel:
        ch = self._get(channel_id)
        if ch.state != ChannelState.OPEN:
            raise RuntimeError(f"UART channel '{channel_id}' is not open.")
        return ch


# ---------------------------------------------------------------------------
# I2C Manager
# ---------------------------------------------------------------------------

class I2CManager:
    """Manages I2C bus devices."""

    def __init__(self) -> None:
        self._devices: dict[str, I2CDevice] = {}

    def add_device(self, address: int, name: str, bus: int = 1) -> I2CDevice:
        """Register a device on the I2C bus at *address*."""
        if not (0 <= address <= 0x7F):
            raise ValueError(f"I2C address 0x{address:02X} out of range (0x00-0x7F).")
        device_id = f"i2c_{uuid.uuid4().hex[:8]}"
        dev = I2CDevice(device_id=device_id, address=address, name=name, bus=bus)
        self._devices[device_id] = dev
        return dev

    def open_device(self, device_id: str) -> I2CDevice:
        dev = self._get(device_id)
        dev.state = ChannelState.OPEN
        return dev

    def close_device(self, device_id: str) -> I2CDevice:
        dev = self._get(device_id)
        dev.state = ChannelState.CLOSED
        return dev

    def write_register(self, device_id: str, register: int, value: int) -> None:
        """Write *value* to *register* on the device."""
        dev = self._get_open(device_id)
        dev.registers[register] = value

    def read_register(self, device_id: str, register: int) -> int:
        """Read from *register* on the device (returns 0 if unset)."""
        dev = self._get_open(device_id)
        return dev.registers.get(register, 0)

    def scan_bus(self, bus: int = 1) -> list[dict]:
        """Return list of device dicts on the given bus."""
        return [d.to_dict() for d in self._devices.values() if d.bus == bus]

    def list_devices(self) -> list[I2CDevice]:
        return list(self._devices.values())

    def get_device(self, device_id: str) -> I2CDevice:
        return self._get(device_id)

    # helpers
    def _get(self, device_id: str) -> I2CDevice:
        if device_id not in self._devices:
            raise KeyError(f"I2C device '{device_id}' not found.")
        return self._devices[device_id]

    def _get_open(self, device_id: str) -> I2CDevice:
        dev = self._get(device_id)
        if dev.state != ChannelState.OPEN:
            raise RuntimeError(f"I2C device '{device_id}' is not open.")
        return dev


# ---------------------------------------------------------------------------
# SPI Manager
# ---------------------------------------------------------------------------

class SPIManager:
    """Manages SPI bus devices."""

    def __init__(self) -> None:
        self._devices: dict[str, SPIDevice] = {}

    def add_device(
        self,
        bus: int,
        chip_select: int,
        name: str,
        clock_hz: int = 1_000_000,
        mode: SPIMode = SPIMode.MODE_0,
        bits_per_word: int = 8,
    ) -> SPIDevice:
        device_id = f"spi_{uuid.uuid4().hex[:8]}"
        dev = SPIDevice(
            device_id=device_id,
            bus=bus,
            chip_select=chip_select,
            name=name,
            clock_hz=clock_hz,
            mode=mode,
            bits_per_word=bits_per_word,
        )
        self._devices[device_id] = dev
        return dev

    def open_device(self, device_id: str) -> SPIDevice:
        dev = self._get(device_id)
        dev.state = ChannelState.OPEN
        return dev

    def close_device(self, device_id: str) -> SPIDevice:
        dev = self._get(device_id)
        dev.state = ChannelState.CLOSED
        return dev

    def transfer(self, device_id: str, tx_data: bytes) -> bytes:
        """
        Full-duplex SPI transfer. Returns RX bytes (same length as TX).

        NOTE: This is a simulated echo-invert response (each TX byte XOR 0xFF).
        Real hardware drivers should override this method with actual SPI I/O.
        """
        self._get_open(device_id)
        return bytes(b ^ 0xFF for b in tx_data)

    def write(self, device_id: str, data: bytes) -> None:
        """Half-duplex write (ignore RX)."""
        self._get_open(device_id)

    def read(self, device_id: str, length: int) -> bytes:
        """Half-duplex read — returns zero bytes as placeholder."""
        self._get_open(device_id)
        return bytes(length)

    def list_devices(self) -> list[SPIDevice]:
        return list(self._devices.values())

    def get_device(self, device_id: str) -> SPIDevice:
        return self._get(device_id)

    # helpers
    def _get(self, device_id: str) -> SPIDevice:
        if device_id not in self._devices:
            raise KeyError(f"SPI device '{device_id}' not found.")
        return self._devices[device_id]

    def _get_open(self, device_id: str) -> SPIDevice:
        dev = self._get(device_id)
        if dev.state != ChannelState.OPEN:
            raise RuntimeError(f"SPI device '{device_id}' is not open.")
        return dev


# ---------------------------------------------------------------------------
# OBD-II Manager
# ---------------------------------------------------------------------------

# Standard PID definitions (mode 01)
OBD2_PIDS: dict[str, dict] = {
    "0D": {"name": "vehicle_speed", "unit": "km/h", "formula": "A"},
    "0C": {"name": "engine_rpm", "unit": "rpm", "formula": "((A*256)+B)/4"},
    "05": {"name": "coolant_temp", "unit": "°C", "formula": "A-40"},
    "11": {"name": "throttle_position", "unit": "%", "formula": "A*100/255"},
    "5C": {"name": "oil_temp", "unit": "°C", "formula": "A-40"},
    "42": {"name": "battery_voltage", "unit": "V", "formula": "((A*256)+B)/1000"},
}


class OBD2Manager:
    """Manages OBD-II diagnostic sessions with vehicles."""

    def __init__(self) -> None:
        self._sessions: dict[str, OBD2Session] = {}

    def open_session(self, port: str, vehicle_vin: str = "") -> OBD2Session:
        """Open an OBD-II session on *port* (serial or BT address)."""
        session_id = f"obd_{uuid.uuid4().hex[:8]}"
        session = OBD2Session(
            session_id=session_id,
            port=port,
            vehicle_vin=vehicle_vin,
            state=ChannelState.OPEN,
        )
        self._sessions[session_id] = session
        return session

    def close_session(self, session_id: str) -> OBD2Session:
        session = self._get(session_id)
        session.state = ChannelState.CLOSED
        return session

    def read_pid(self, session_id: str, pid: str) -> dict:
        """Read a live-data PID. Returns the PID definition + simulated value."""
        session = self._get_open(session_id)
        pid_upper = pid.upper()
        if pid_upper not in OBD2_PIDS:
            raise KeyError(f"PID '{pid}' is not in the standard PID table.")
        definition = OBD2_PIDS[pid_upper]
        # Simulate a plausible reading (e.g., 0 for now — real driver injects real data)
        session.live_data[definition["name"]] = {"value": 0, "unit": definition["unit"]}
        return dict(definition, value=0)

    def inject_live_data(self, session_id: str, key: str, value: Any) -> None:
        """Inject live telemetry data (for hardware bridge / testing)."""
        session = self._get_open(session_id)
        session.live_data[key] = value

    def read_dtc(self, session_id: str) -> list[str]:
        """Return stored Diagnostic Trouble Codes."""
        return list(self._get_open(session_id).dtc_codes)

    def inject_dtc(self, session_id: str, code: str) -> None:
        """Inject a DTC (for testing or hardware bridge)."""
        session = self._get_open(session_id)
        if code not in session.dtc_codes:
            session.dtc_codes.append(code)

    def clear_dtc(self, session_id: str) -> int:
        """Clear all stored DTCs. Returns count cleared."""
        session = self._get_open(session_id)
        count = len(session.dtc_codes)
        session.dtc_codes.clear()
        return count

    def get_live_data(self, session_id: str) -> dict:
        return dict(self._get_open(session_id).live_data)

    def list_sessions(self) -> list[OBD2Session]:
        return list(self._sessions.values())

    def get_session(self, session_id: str) -> OBD2Session:
        return self._get(session_id)

    def list_standard_pids(self) -> list[dict]:
        return [{"pid": k, **v} for k, v in OBD2_PIDS.items()]

    # helpers
    def _get(self, session_id: str) -> OBD2Session:
        if session_id not in self._sessions:
            raise KeyError(f"OBD-II session '{session_id}' not found.")
        return self._sessions[session_id]

    def _get_open(self, session_id: str) -> OBD2Session:
        session = self._get(session_id)
        if session.state != ChannelState.OPEN:
            raise RuntimeError(f"OBD-II session '{session_id}' is not open.")
        return session


# ---------------------------------------------------------------------------
# Unified Hardware Protocols Hub
# ---------------------------------------------------------------------------

class HardwareProtocolsHub:
    """
    Unified entry-point for all hardware communication protocols.

    Exposes UART, I2C, SPI, and OBD-II managers as attributes.
    """

    def __init__(self) -> None:
        self.uart = UARTManager()
        self.i2c = I2CManager()
        self.spi = SPIManager()
        self.obd2 = OBD2Manager()

    def status(self) -> dict:
        """Return a quick summary of all active hardware channels."""
        return {
            "uart_channels": len(self.uart.list_channels()),
            "i2c_devices": len(self.i2c.list_devices()),
            "spi_devices": len(self.spi.list_devices()),
            "obd2_sessions": len(self.obd2.list_sessions()),
        }
