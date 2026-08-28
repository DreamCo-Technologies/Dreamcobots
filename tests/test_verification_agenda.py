import pytest

from buddy_os.intelligence.verification_agenda import VerificationAgenda, VerificationTask


def test_agenda_prioritizes_pending_tasks_and_tracks_coverage():
    agenda = VerificationAgenda()
    agenda.add(VerificationTask("low", "check B", 0.2, ("B",)))
    agenda.add(VerificationTask("high", "check A", 0.9, ("A",)))
    assert [task.task_id for task in agenda.pending()] == ["high", "low"]
    assert agenda.coverage(("A", "B", "C")) == pytest.approx(2 / 3)


def test_agenda_rejects_duplicates_and_invalid_status():
    agenda = VerificationAgenda()
    agenda.add(VerificationTask("x", "check", 0.5))
    with pytest.raises(ValueError):
        agenda.add(VerificationTask("x", "duplicate", 0.5))
    with pytest.raises(ValueError):
        VerificationTask("bad", "bad", 0.5, status="unknown")
