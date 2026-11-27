import unittest

from tools.audit_onet_task_guide_readiness import audit


def task(task_id, **overrides):
    value = {
        "task_id": task_id,
        "learning_summary_status": "not_yet_authored_by_buddy",
        "learning_summary_required": True,
        "practice_required": True,
    }
    value.update(overrides)
    return value


def document(tasks):
    return {
        "schema": "dreamco.onet_task_curricula.v1",
        "source": {"version": "31.0"},
        "occupations": [{
            "occupation_code": "15-1252.00",
            "occupation_title": "Software Developers",
            "task_playbooks": tasks,
        }],
    }


class OnetTaskGuideReadinessTests(unittest.TestCase):
    def test_existing_briefs_are_not_mistaken_for_authored_guides(self):
        report = audit(document([task("1")]))
        self.assertEqual(report["task_count"], 1)
        self.assertEqual(report["ready_for_study_review"], 0)
        self.assertEqual(report["status"], "guide_coverage_gaps")
        self.assertEqual(report["gap_counts"]["guide_not_authored"], 1)
        self.assertFalse(report["completion_claim"])
        self.assertFalse(report["mastery_claim"])

    def test_task_ready_requires_all_artifacts_and_both_reviews(self):
        complete = task(
            "1",
            authored_guide={"status": "authored", "content_path": "guides/15-1252.00/1.md", "version": "1.0"},
            practice_exercises=[{"id": "practice-1"}],
            assessment={"id": "assessment-1"},
            citations=[{"url": "https://example.org/source", "accessed_at": "2026-11-25"}],
            rights_review="approved",
            human_review="approved",
        )
        report = audit(document([complete]))
        self.assertEqual(report["ready_for_study_review"], 1)
        self.assertEqual(report["status"], "all_tasks_ready_for_review")
        self.assertFalse(report["mastery_claim"])

    def test_missing_task_ids_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "task_id"):
            audit(document([task("")]))

    def test_duplicate_task_identity_is_reported(self):
        report = audit(document([task("1"), task("1")]))
        self.assertEqual(report["duplicate_task_count"], 1)
        self.assertEqual(report["status"], "structural_errors")

    def test_unknown_schema_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            audit({"schema": "other", "occupations": []})


if __name__ == "__main__":
    unittest.main()
