"""Safe device discovery/control policy primitives for Buddy."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Device:
    device_id: str
    name: str
    transport: str  # bluetooth, wifi, usb, vendor_api, etc.
    capabilities: frozenset[str] = frozenset()
    paired: bool = False
    authorized: bool = False

@dataclass
class DeviceControlSession:
    device_id: str
    allowed_capabilities: set[str] = field(default_factory=set)
    audit: list[str] = field(default_factory=list)

class DeviceRegistry:
    def __init__(self):
        self.devices: dict[str, Device] = {}

    def discover(self, devices):
        for device in devices:
            self.devices[device.device_id] = device
        return list(self.devices.values())

    def controllable(self, device_id: str):
        device = self.devices.get(device_id)
        if not device or not device.paired or not device.authorized:
            return False
        return True

    def authorize(self, device_id: str, capabilities):
        device = self.devices[device_id]
        allowed = set(capabilities) & set(device.capabilities)
        if not device.paired:
            raise PermissionError("Device must be paired before authorization")
        return DeviceControlSession(device_id, allowed, [f"authorized:{sorted(allowed)}"])

    def execute(self, session: DeviceControlSession, capability: str):
        if capability not in session.allowed_capabilities:
            raise PermissionError("Capability was not authorized")
        session.audit.append(f"execute:{capability}")
        return {"device_id": session.device_id, "capability": capability, "status": "authorized"}
