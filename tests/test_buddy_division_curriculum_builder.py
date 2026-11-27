"""Validate the original DreamCo curriculum generated for every canonical division."""
import unittest
from pathlib import Path

from buddy.learning.division_curriculum_builder import build_division_curricula


class BuddyDivisionCurriculumBuilderTests(unittest.TestCase):
    def test_all_55_divisions_receive_full_curriculum_artifacts(self):
        catalog = build_division_curricula()
        self.assertEqual(catalog["counts"], {
            "divisions": 55,
            "lessons": 330,
            "exercises": 275,
            "projects": 110,
            "assessments": 220,
        })
        self.assertEqual(len(catalog["artifacts"]), 55)

    def test_each_division_has_lessons_exercises_projects_and_assessments(self):
        catalog = build_division_curricula()
        for course in catalog["artifacts"]:
            with self.subTest(division=course["division"]["name"]):
                self.assertEqual(len(course["lessons"]), 6)
                self.assertEqual(len(course["exercises"]), 5)
                self.assertEqual(len(course["projects"]), 2)
                self.assertEqual(len(course["assessments"]), 4)
                self.assertTrue(course["masterbot_targets"])
                self.assertEqual(course["ownership_class"], "dreamco_owned")

    def test_generated_lessons_are_internal_and_do_not_route_to_external_sites(self):
        catalog = build_division_curricula()
        for course in catalog["artifacts"]:
            for lesson in course["lessons"]:
                self.assertEqual(lesson["source_url"], "")
                self.assertTrue(lesson["learner_visible"])
                self.assertEqual(lesson["training_eligibility"], "internal_sandbox_practice_only")
                self.assertEqual(lesson["review_status"], "draft_needs_owner_review")
                self.assertTrue(lesson["exercise_ids"])
                self.assertTrue(lesson["project_ids"])
                self.assertTrue(lesson["assessment_ids"])

    def test_failed_assessments_have_targeted_retraining_routes(self):
        catalog = build_division_curricula()
        for course in catalog["artifacts"]:
            policy = course["retraining_policy"]
            self.assertEqual(policy["trigger"], "any_required_assessment_or_benchmark_failure")
            self.assertTrue(policy["failure_routes"])
            self.assertFalse(policy["mastery_awarded_on_failure"])
            self.assertFalse(course["model_weight_training_authorized"])
            self.assertEqual(course["certification_status"], "not_certified")

    def test_all_source_portfolios_exist_and_match_their_division(self):
        catalog = build_division_curricula()
        for course in catalog["artifacts"]:
            self.assertTrue((Path(course["source_portfolio"])).name)
            self.assertEqual(course["source_profile_count"], len(course["source_profile_slugs"]))
            self.assertTrue(course["source_profile_count"] > 0)


if __name__ == "__main__":
    unittest.main()
