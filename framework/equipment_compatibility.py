"""Vendor-neutral equipment compatibility primitives for Buddy."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Equipment:
    equipment_id: str
    category: str
    protocols: frozenset[str] = frozenset()
    capabilities: frozenset[str] = frozenset()
    vendor: str | None = None
    model: str | None = None

@dataclass(frozen=True)
class Adapter:
    adapter_id: str
    protocols: frozenset[str]
    capabilities: frozenset[str]
    sandboxed: bool = True
    authorized: bool = False

@dataclass
class CompatibilityResult:
    equipment_id: str
    compatible: bool
    supported_capabilities: set[str] = field(default_factory=set)
    missing_capabilities: set[str] = field(default_factory=set)
    adapters: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

class EquipmentRegistry:
    def __init__(self, adapters=()):
        self.adapters = list(adapters)

    def check(self, equipment: Equipment, required_capabilities=frozenset()):
        result = CompatibilityResult(equipment.equipment_id, False)
        for adapter in self.adapters:
            if not adapter.sandboxed or not adapter.authorized:
                continue
            if equipment.protocols & adapter.protocols:
                supported = equipment.capabilities & adapter.capabilities & required_capabilities
                if supported:
                    result.adapters.append(adapter.adapter_id)
                    result.supported_capabilities.update(supported)
        result.missing_capabilities.update(required_capabilities - result.supported_capabilities)
        result.compatible = bool(required_capabilities <= result.supported_capabilities) if required_capabilities else bool(result.adapters)
        if not result.adapters:
            result.reasons.append('No authorized sandboxed adapter matches the equipment protocols.')
        if result.missing_capabilities:
            result.reasons.append('One or more requested capabilities are not supported by the available adapters.')
        return result
