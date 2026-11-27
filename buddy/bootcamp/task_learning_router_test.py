"""Tests for Buddy's task-to-learning resource router."""
import unittest

from buddy.bootcamp.task_learning_router import (
    LearningResource, TaskRequest, build_learning_route, rank_resources,
)


class TaskLearningRouterTests(unittest.TestCase):
    def setUp(self):
        self.resources = [
            LearningResource(
                id="free-python-lab", name="Free Python Lab",
                url="https://example.org/python", skills=("Python", "debugging"),
                modes=("practice",), quality=0.9, supports_execution=True,
            ),
            LearningResource(
                id="paid-python-course", name="Paid Python Course",
                url="https://example.org/paid", skills=("Python",),
                access="paid", cost_per_hour_usd=5.0,
            ),
            LearningResource(
                id="unrelated", name="Unrelated Design Course",
                url="https://example.org/design", skills=("graphic design",),
            ),
        ]

    def test_best_relevant_practice_resource_selected(self):
        task = TaskRequest("Debug a Python script", ("Python", "debugging"))
        route = build_learning_route(task, self.resources)
        self.assertEqual(route["status"], "route_ready")
        self.assertEqual(route["selected_resource"]["resource"]["id"], "free-python-lab")
        self.assertFalse(route["training_started"])

    def test_paid_resource_requires_explicit_opt_in(self):
        task = TaskRequest("Learn Python", ("Python",))
        ranked = rank_resources(task, self.resources)
        self.assertNotIn("paid-python-course", [x["resource"]["id"] for x in ranked])

    def test_paid_and_freemium_resources_require_opt_in_even_at_zero_cost(self):
        resources = [
            LearningResource(id="paid-zero", name="Paid zero-cost listing",
                url="https://example.org/paid", skills=("Python",), access="paid"),
            LearningResource(id="freemium-zero", name="Freemium zero-cost listing",
                url="https://example.org/freemium", skills=("Python",), access="freemium"),
        ]
        task = TaskRequest("Learn Python", ("Python",))
        self.assertEqual(rank_resources(task, resources), [])
        opted_in = TaskRequest("Learn Python", ("Python",), allow_paid=True)
        self.assertEqual(len(rank_resources(opted_in, resources)), 2)

    def test_non_finite_or_negative_resource_numbers_are_excluded(self):
        resources = [
            LearningResource(id="nan-cost", name="NaN cost", url="https://example.org/a",
                skills=("Python",), cost_per_hour_usd=float("nan")),
            LearningResource(id="infinite-cost", name="Infinite cost", url="https://example.org/b",
                skills=("Python",), cost_per_hour_usd=float("inf")),
            LearningResource(id="negative-cost", name="Negative cost", url="https://example.org/c",
                skills=("Python",), cost_per_hour_usd=-1.0),
            LearningResource(id="nan-quality", name="NaN quality", url="https://example.org/d",
                skills=("Python",), quality=float("nan")),
            LearningResource(id="good", name="Valid free resource", url="https://example.org/e",
                skills=("Python",), quality=0.8),
        ]
        ranked = rank_resources(TaskRequest("Learn Python", ("Python",)), resources)
        self.assertEqual([item["resource"]["id"] for item in ranked], ["good"])

    def test_invalid_task_cost_limit_is_rejected(self):
        for invalid in (float("nan"), float("inf"), -1.0):
            with self.subTest(invalid=invalid):
                task = TaskRequest("Learn Python", ("Python",), max_cost_per_hour_usd=invalid)
                with self.assertRaisesRegex(ValueError, "finite non-negative"):
                    rank_resources(task, self.resources)

    def test_no_match_returns_discovery_action(self):
        task = TaskRequest("Repair a diesel engine", ("diesel mechanics",))
        route = build_learning_route(task, self.resources)
        self.assertEqual(route["status"], "no_eligible_resource")

    def test_account_access_requires_permission(self):
        resource = LearningResource(
            id="gated", name="Gated course", url="https://example.org",
            skills=("Python",), requires_account=True,
        )
        task = TaskRequest("Learn Python", ("Python",))
        self.assertEqual(rank_resources(task, [resource]), [])
        allowed = TaskRequest("Learn Python", ("Python",), allow_external_access=True)
        self.assertEqual(len(rank_resources(allowed, [resource])), 1)


if __name__ == "__main__":
    unittest.main()
