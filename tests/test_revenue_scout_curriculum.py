import unittest

from tools.audit_revenue_scout_curriculum import audit


def program():
    return {
        "schema": "dreamco.buddy.master_scout_opportunity_resource_library.v1",
        "master_scout_team": [
            {"id": "income-scout", "searches": ["jobs", "gigs"]},
            {"id": "grant-scout", "searches": ["grants"]},
        ],
    }


def lanes():
    return {"lanes": [{"id": "jobs"}, {"id": "grants"}]}


def sources():
    return {"categories": {"jobs": ["official_job_boards"], "grants": ["official_grant_sources"]}}


def artifacts():
    return {"schema": "dreamco.revenue_scout_curriculum_artifacts.v1", "artifacts": []}


class RevenueScoutCurriculumAuditTests(unittest.TestCase):
    def test_planning_taxonomy_is_not_mistaken_for_authored_lessons(self):
        report = audit(program(), lanes(), sources(), artifacts())
        self.assertEqual(report["scout_count"], 2)
        self.assertEqual(report["required_module_count"], 16)
        self.assertEqual(report["ready_module_count"], 0)
        self.assertEqual(report["status"], "curriculum_gaps")
        self.assertFalse(report["mastery_claim"])

    def test_module_requires_guide_exercises_assessment_citations_and_reviews(self):
        docs = artifacts()
        docs["artifacts"] = [{
            "scout_id": "income-scout", "module_id": "discover",
            "guide_path": "docs/example.md", "exercises": [{"id": "x"}],
            "assessment": {"id": "a"}, "citations": [{"url": "https://example.org"}],
            "rights_review": "approved", "human_review": "approved",
        }]
        report = audit(program(), lanes(), sources(), docs)
        self.assertEqual(report["ready_module_count"], 0)  # guide path is not a real file in this fixture
        self.assertEqual(report["not_ready_module_count"], 16)

    def test_duplicate_scout_ids_are_rejected(self):
        p = program()
        p["master_scout_team"].append({"id": "income-scout", "searches": []})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(p, lanes(), sources(), artifacts())

    def test_duplicate_lane_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            audit(program(), {"lanes": [{"id": "jobs"}, {"id": "jobs"}]}, sources(), artifacts())

    def test_unknown_artifact_schema_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            audit(program(), lanes(), sources(), {"schema": "other", "artifacts": []})


if __name__ == "__main__":
    unittest.main()
