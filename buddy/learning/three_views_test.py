import unittest

from buddy.learning.permissioned_views import grant
from buddy.learning.three_views import answer


class ThreeViewsTest(unittest.TestCase):
    def test_one_question_can_return_three_optional_views(self) -> None:
        grants = [grant("train", "buddy-a", True)]
        single = answer("buddy-a", "Is this safe?", grants, multi_view=False)
        self.assertEqual(len(single["perspectives"]), 1)
        self.assertFalse(single["final"])
        report = answer("buddy-a", "Is this safe?", grants, multi_view=True)
        self.assertEqual(len(report["perspectives"]), 3)
        self.assertTrue(report["generated_views"])
        self.assertFalse(report["live_research"])


if __name__ == "__main__":
    unittest.main()
