import unittest

from benchmarks.model_competition.route import register, route


class ModelRouteTest(unittest.TestCase):
    def test_route_uses_measured_quality_and_refuses_a_guess(self) -> None:
        models = [register("slow", "frontier", "code", 0.9, 0.2, "owner", False), register("fast", "open-source", "code", 0.9, 0.8, "user", True)]
        report = route("code", models)
        self.assertEqual(report["model"], "fast")
        self.assertFalse(report["guessed"])
        free = route("code", models, free_only=True)
        self.assertEqual(free["model"], "fast")
        missing = route("legal", models)
        self.assertIsNone(missing["model"])


if __name__ == "__main__":
    unittest.main()
