import unittest

from buddy.learning.study_resource_scheduler import Capability, Resource, choose_next


class StudyResourceSchedulerTests(unittest.TestCase):
    def test_generator_gaps_are_scored_for_every_candidate(self):
        resources = [
            Resource(1, "general", "general", "https://example.com/general"),
            Resource(2, "python", "python", "https://example.com/python"),
            Resource(3, "security", "security", "https://example.com/security"),
        ]
        gaps = (
            gap for gap in [
                Capability("Python", "python", score=0.1, failed_benchmarks=2),
                Capability("Security", "security", score=0.95),
            ]
        )
        chosen = choose_next(resources, gaps)
        self.assertEqual(chosen.id, 2)

    def test_recent_resources_are_excluded(self):
        resources = [
            Resource(1, "python", "python", "https://example.com/python"),
            Resource(2, "security", "security", "https://example.com/security"),
        ]
        chosen = choose_next(
            resources,
            [Capability("Security", "security", score=0.1)],
            recent={2},
        )
        self.assertEqual(chosen.id, 1)

    def test_empty_gap_generator_is_safe(self):
        resource = Resource(1, "general", "general", "https://example.com/general")
        self.assertEqual(choose_next([resource], iter(())), resource)


if __name__ == "__main__":
    unittest.main()
