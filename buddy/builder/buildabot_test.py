import unittest

from buddy.builder.buildabot import choose


class BuildabotTest(unittest.TestCase):
    def test_choice_stays_compatible_and_does_not_rewrite(self) -> None:
        report = choose("hot-loop")
        self.assertEqual(report["language"], "c")
        self.assertFalse(report["rewritten"])
        pages = choose("pages")
        self.assertEqual(pages["language"], "html")


if __name__ == "__main__":
    unittest.main()
