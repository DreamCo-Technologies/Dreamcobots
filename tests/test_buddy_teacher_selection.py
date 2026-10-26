import unittest
from datetime import datetime, timezone
from buddy.certification.teacher_selection import select_teachers

NOW = datetime(2026, 10, 22, tzinfo=timezone.utc)

def record(model="org/teacher", **changes):
    x = dict(domain="coding", independent_verified=True,
             teacher_output_training_permitted=True, license_reviewed=True,
             benchmark_id="original-coding-v1", model_id=model, model_revision="pinned",
             evidence_sha256="a"*64, evaluated_at="2026-10-21T00:00:00Z",
             quality=.9, safety=.98, completion=.95, latency_ms=120, cost_usd=.01)
    x.update(changes)
    return x

class TeacherSelectionTests(unittest.TestCase):
    def test_selects_verified_with_three_trials(self):
        report = select_teachers([record() for _ in range(3)], now=NOW)
        leader = report["domains"]["coding"]["provisional_leader"]
        self.assertEqual(leader["model_id"], "org/teacher")
        self.assertFalse(report["domains"]["coding"]["distillation_authorized"])

    def test_rejects_unlicensed_teacher(self):
        report = select_teachers([record(teacher_output_training_permitted=False) for _ in range(3)], now=NOW)
        self.assertEqual(report["rejected_records"], 3)

    def test_rejects_stale(self):
        report = select_teachers([record(evaluated_at="2025-01-01T00:00:00Z")], now=NOW)
        self.assertEqual(report["rejected_records"], 1)

    def test_does_not_select_single_trial(self):
        report = select_teachers([record()], now=NOW)
        self.assertIsNone(report["domains"]["coding"]["provisional_leader"])

    def test_safety_floor(self):
        report = select_teachers([record(safety=.4)], now=NOW)
        self.assertEqual(report["rejected_records"], 1)

if __name__ == "__main__":
    unittest.main()
