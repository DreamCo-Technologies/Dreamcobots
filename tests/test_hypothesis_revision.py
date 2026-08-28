import pytest

from buddy_os.intelligence.hypothesis_revision import HypothesisRevision, HypothesisRevisionLog


def test_revision_log_preserves_parent_chain():
    log = HypothesisRevisionLog()
    first = HypothesisRevision("r1", "h1", None, "retain", "initial evidence", 0.5, ("e1",))
    second = HypothesisRevision("r2", "h1", "r1", "strengthen", "new supporting evidence", 0.8, ("e2",))
    log.record(first)
    log.record(second)
    assert log.latest("h1") == second
    assert log.history("h1") == (first, second)


def test_revision_log_rejects_broken_history():
    log = HypothesisRevisionLog()
    with pytest.raises(KeyError):
        log.record(HypothesisRevision("r2", "h1", "missing", "strengthen", "reason", 0.7))
    with pytest.raises(ValueError):
        HypothesisRevision("r3", "h1", None, "unknown", "reason", 0.7)
