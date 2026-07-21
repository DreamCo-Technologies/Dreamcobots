"""Tests for EventBus."""

import pytest
from BuddyAI.event_bus import EventBus


def test_subscribe_and_publish():
    bus = EventBus()
    received = []
    bus.subscribe("test.event", lambda d: received.append(d))
    bus.publish("test.event", {"value": 42})
    assert received == [{"value": 42}]


def test_multiple_subscribers():
    bus = EventBus()
    calls = []
    bus.subscribe("ev", lambda d: calls.append("a"))
    bus.subscribe("ev", lambda d: calls.append("b"))
    bus.publish("ev")
    assert calls == ["a", "b"]


def test_emit_is_alias_for_publish():
    bus = EventBus()
    received = []
    bus.subscribe("x", lambda d: received.append(d))
    bus.emit("x", "hello")
    assert received == ["hello"]


def test_unsubscribe():
    bus = EventBus()
    calls = []
    handler = lambda d: calls.append(d)
    bus.subscribe("ev", handler)
    bus.unsubscribe("ev", handler)
    bus.publish("ev", 1)
    assert calls == []


def test_unsubscribe_nonexistent_does_not_raise():
    bus = EventBus()
    bus.unsubscribe("ev", lambda d: None)  # should not raise


def test_no_subscribers_does_not_raise():
    bus = EventBus()
    bus.publish("nonexistent.event", {"foo": "bar"})


def test_subscriber_exception_does_not_stop_others():
    bus = EventBus()
    calls = []

    def bad(d):
        raise RuntimeError("oops")

    def good(d):
        calls.append(d)

    bus.subscribe("ev", bad)
    bus.subscribe("ev", good)
    bus.publish("ev", "data")
    assert calls == ["data"]


def test_clear_specific_event():
    bus = EventBus()
    calls_a, calls_b = [], []
    bus.subscribe("a", lambda d: calls_a.append(d))
    bus.subscribe("b", lambda d: calls_b.append(d))
    bus.clear("a")
    bus.publish("a", 1)
    bus.publish("b", 2)
    assert calls_a == []
    assert calls_b == [2]


def test_clear_all():
    bus = EventBus()
    calls = []
    bus.subscribe("x", lambda d: calls.append(d))
    bus.clear()
    bus.publish("x", 1)
    assert calls == []


def test_subscriber_count():
    bus = EventBus()
    bus.subscribe("ev", lambda d: None)
    bus.subscribe("ev", lambda d: None)
    assert bus.subscriber_count("ev") == 2
    assert bus.subscriber_count("other") == 0
