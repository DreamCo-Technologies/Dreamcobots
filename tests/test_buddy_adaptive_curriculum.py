import unittest
from tools.buddy_adaptive_curriculum import Gap, rank_gaps, next_actions

class AdaptiveCurriculumTests(unittest.TestCase):
    def test_largest_gap_is_prioritized(self):
        weak = Gap("reasoning", .3, .7, .5, .8)
        strong = Gap("coding", .95, .95, .95, .98)
        self.assertEqual(rank_gaps([strong, weak])[0].capability, "reasoning")

    def test_actions_match_measured_gaps(self):
        gap = Gap("vision", .5, .4, .6, .7)
        actions = next_actions(gap)
        self.assertIn("study-targeted-resources", actions)
        self.assertIn("run-performance-optimization", actions)
        self.assertIn("run-safety-evaluation", actions)
        self.assertIn("benchmark-retest", actions)

if __name__ == "__main__":
    unittest.main()
