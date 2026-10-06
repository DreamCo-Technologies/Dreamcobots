import unittest

from buddy.builder.ai_terms import catalog


class AiTermsTest(unittest.TestCase):
    def test_terms_are_plain_and_self_training_is_off(self) -> None:
        report = catalog()
        self.assertGreater(report["count"], 25)
        self.assertFalse(report["self_training_started"])
        self.assertTrue(all(row["plain"] and row["safe"] for row in report["terms"]))


if __name__ == "__main__":
    unittest.main()
