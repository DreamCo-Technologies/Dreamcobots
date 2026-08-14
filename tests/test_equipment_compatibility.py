from framework.equipment_compatibility import Adapter, Equipment, EquipmentRegistry


def test_compatible_equipment():
    registry = EquipmentRegistry([Adapter('usb-pos', frozenset({'USB'}), frozenset({'card_reader.accept'}), authorized=True)])
    result = registry.check(Equipment('terminal-1','payment',frozenset({'USB'}),frozenset({'card_reader.accept'})), frozenset({'card_reader.accept'}))
    assert result.compatible
    assert 'usb-pos' in result.adapters


def test_missing_capability_is_reported():
    registry = EquipmentRegistry([Adapter('usb-pos', frozenset({'USB'}), frozenset({'receipt.print'}), authorized=True)])
    result = registry.check(Equipment('terminal-1','payment',frozenset({'USB'}),frozenset({'receipt.print'})), frozenset({'card_reader.accept'}))
    assert not result.compatible
    assert 'card_reader.accept' in result.missing_capabilities
