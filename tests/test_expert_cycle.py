import unittest

from tools.daily_repo_cycle import cycle
from tools.expert_section_scan import scan


class ExpertCycleTest(unittest.TestCase):
    def test_scan_does_not_approve_or_delete(self) -> None:
        report = scan()
        self.assertFalse(report["expert_approved"])
        self.assertFalse(report["deleted"])
        daily = cycle()
        self.assertFalse(daily["green"])
        self.assertEqual(daily["train"]["status"], "planned")
        self.assertGreater(daily["bootcamp"]["courses"], 50)


if __name__ == "__main__":
    unittest.main()
