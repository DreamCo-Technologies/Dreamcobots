# Bluetooth connectivity handler for Dreamcobots.
# Supports device discovery, pairing, and bi-directional data transfer.
#
# Full Bluetooth support requires one of the following optional libraries:
#   - PyBluez:  pip install pybluez
#   - Bleak:    pip install bleak
#
# Without those packages this module provides a complete simulation layer
# that can be used for unit tests and environments without Bluetooth hardware.

import time
import uuid


class BluetoothDevice:
    """Represents a discovered or paired Bluetooth device."""

    def __init__(self, address, name, rssi=None):
        self.address = address
        self.name = name
        self.rssi = rssi
        self.paired = False
        self.connected = False

    def to_dict(self):
        return {
            "address": self.address,
            "name": self.name,
            "rssi": self.rssi,
            "paired": self.paired,
            "connected": self.connected,
        }

    def __repr__(self):
        return f"<BluetoothDevice name='{self.name}' address='{self.address}'>"


class BluetoothHandler:
    """
    Manages Bluetooth device discovery, pairing, and bi-directional communication.

    When real Bluetooth hardware and drivers are available the discovery methods
    can be extended to call PyBluez / Bleak.  Without hardware the simulation
    layer allows full testing of the API surface.
    """

    def __init__(self, simulate=True):
        self.simulate = simulate
        self.discovered_devices = {}
        self.paired_devices = {}
        self.connected_devices = {}
        self.data_log = []

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------
    def discover(self, duration=5, limit=10):
        """
        Scan for nearby Bluetooth devices.

        In simulation mode a set of virtual devices is returned.
        Pass simulate=False and ensure PyBluez is installed for real scans.
        """
        if self.simulate:
            simulated = [
                BluetoothDevice("AA:BB:CC:DD:EE:01", "SmartTV-Living", rssi=-55),
                BluetoothDevice("AA:BB:CC:DD:EE:02", "Laptop-Office", rssi=-70),
                BluetoothDevice("AA:BB:CC:DD:EE:03", "Phone-Kitchen", rssi=-80),
                BluetoothDevice("AA:BB:CC:DD:EE:04", "Tablet-Bedroom", rssi=-65),
                BluetoothDevice("AA:BB:CC:DD:EE:05", "SmartWatch-User", rssi=-45),
            ]
            found = simulated[:limit]
        else:
            try:
                import bluetooth  # PyBluez

                raw = bluetooth.discover_devices(duration=duration, lookup_names=True)
                found = [BluetoothDevice(addr, name) for addr, name in raw[:limit]]
            except ImportError:
                print("[Bluetooth] PyBluez not installed – falling back to simulation.")
                return self.discover(duration=duration, limit=limit)

        for device in found:
            self.discovered_devices[device.address] = device
        print(f"[Bluetooth] Discovered {len(found)} device(s).")
        return [d.to_dict() for d in found]

    # ------------------------------------------------------------------
    # Pairing
    # ------------------------------------------------------------------
    def pair(self, address):
        """Pair with a previously discovered device."""
        device = self.discovered_devices.get(address)
        if not device:
            return {"error": f"Device '{address}' not found. Run discover() first."}
        device.paired = True
        self.paired_devices[address] = device
        print(f"[Bluetooth] Paired with {device.name} ({address}).")
        return {"status": "paired", "device": device.to_dict()}

    def unpair(self, address):
        """Remove pairing for a device."""
        device = self.paired_devices.pop(address, None)
        if device:
            device.paired = False
            device.connected = False
            self.connected_devices.pop(address, None)
            print(f"[Bluetooth] Unpaired {device.name} ({address}).")
            return {"status": "unpaired", "device": device.to_dict()}
        return {"error": f"Device '{address}' was not paired."}

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    def connect(self, address):
        """Open a connection to a paired device."""
        device = self.paired_devices.get(address)
        if not device:
            return {"error": f"Device '{address}' is not paired."}
        device.connected = True
        self.connected_devices[address] = device
        print(f"[Bluetooth] Connected to {device.name} ({address}).")
        return {"status": "connected", "device": device.to_dict()}

    def disconnect(self, address):
        """Close the connection to a device."""
        device = self.connected_devices.pop(address, None)
        if device:
            device.connected = False
            print(f"[Bluetooth] Disconnected from {device.name} ({address}).")
            return {"status": "disconnected", "device": device.to_dict()}
        return {"error": f"Device '{address}' is not connected."}

    # ------------------------------------------------------------------
    # Data transfer
    # ------------------------------------------------------------------
    def send_data(self, address, data):
        """Send data to a connected device."""
        device = self.connected_devices.get(address)
        if not device:
            return {"error": f"Device '{address}' is not connected."}
        entry = {
            "direction": "send",
            "address": address,
            "device_name": device.name,
            "data": data,
            "message_id": str(uuid.uuid4()),
            "timestamp": time.time(),
        }
        self.data_log.append(entry)
        print(f"[Bluetooth] → {device.name}: {data}")
        return entry

    def receive_data(self, address, data):
        """Simulate or record data received from a connected device."""
        device = self.connected_devices.get(address)
        device_name = device.name if device else address
        entry = {
            "direction": "receive",
            "address": address,
            "device_name": device_name,
            "data": data,
            "message_id": str(uuid.uuid4()),
            "timestamp": time.time(),
        }
        self.data_log.append(entry)
        print(f"[Bluetooth] ← {device_name}: {data}")
        return entry

    def get_data_log(self):
        """Return all recorded data transfer entries."""
        return list(self.data_log)
