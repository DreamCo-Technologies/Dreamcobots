from dreamco_platform.events.shared_contract import load_event_contract, validate_event_envelope


def test_load_event_contract_schema():
    contract = load_event_contract()
    assert contract["schema"] == "dreamco_event_envelope.v1"
    assert "event_type" in contract["required_fields"]


def test_validate_event_envelope_accepts_valid_payload():
    assert (
        validate_event_envelope(
            {
                "event_type": "bot.started",
                "bot_id": "dreambuddy_core",
                "intent": "add_todo",
                "timestamp": "2026-06-01T00:00:00Z",
                "status": "running",
                "correlation_id": "corr-123",
            }
        )
        is True
    )


def test_validate_event_envelope_rejects_missing_field():
    try:
        validate_event_envelope(
            {
                "event_type": "bot.started",
                "bot_id": "dreambuddy_core",
                "timestamp": "2026-06-01T00:00:00Z",
                "status": "running",
                "correlation_id": "corr-123",
            }
        )
    except ValueError as exc:
        assert "missing required field: intent" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing required intent")
