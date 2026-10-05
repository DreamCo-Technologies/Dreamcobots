import unittest

from buddy.accounts.own_skills import SKILLS, run_skill


class OwnSkillsTest(unittest.TestCase):
    def test_every_gap_has_a_local_button(self) -> None:
        self.assertGreater(len(SKILLS), 10)
        report = run_skill(SKILLS[0], "hello")
        self.assertEqual(report["button"], SKILLS[0])
        self.assertFalse(report["third_party_called"])


if __name__ == "__main__":
    unittest.main()
