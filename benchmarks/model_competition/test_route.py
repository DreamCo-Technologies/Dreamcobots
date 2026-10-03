import unittest

from benchmarks.model_competition.route import register, route


class ModelRouteTest(unittest.TestCase):
    def test_route_uses_measured_quality_and_refuses_a_guess(self) -> None:
        models = [register("slow", "frontier", "code", 0.9, 0.2), register("fast", "open-source", "code", 0.9, 0.8)]
        report = route("code", models)
        self.assertEqual(report["model"], "fast")
        self.assertFalse(report["guessed"])
        missing = route("legal", models)
        self.assertIsNone(missing["model"])


if __name__ == "__main__":
    unittest.main()
