import pytest
from framework.device_control_policy import Device, DeviceRegistry


def test_discovery_does_not_grant_control():
    registry = DeviceRegistry()
    registry.discover([Device('tv-1', 'TV', 'wifi', frozenset({'media.volume'}))])
    assert not registry.controllable('tv-1')


def test_paired_authorized_device_can_use_allowed_capability():
    registry = DeviceRegistry()
    registry.discover([Device('speaker-1', 'Speaker', 'bluetooth', frozenset({'media.volume'}), paired=True, authorized=True)])
    session = registry.authorize('speaker-1', {'media.volume'})
    assert registry.execute(session, 'media.volume')['status'] == 'authorized'


def test_unapproved_capability_is_rejected():
    registry = DeviceRegistry()
    registry.discover([Device('speaker-1', 'Speaker', 'bluetooth', frozenset({'media.volume'}), paired=True, authorized=True)])
    session = registry.authorize('speaker-1', {'media.volume'})
    with pytest.raises(PermissionError):
        registry.execute(session, 'camera.capture')
