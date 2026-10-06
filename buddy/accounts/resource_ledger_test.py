import unittest

from buddy.accounts.resource_ledger import ledger


class ResourceLedgerTest(unittest.TestCase):
    def test_resources_are_sandboxed_and_not_mastered(self) -> None:
        report = ledger()
        self.assertGreater(report["count"], 10)
        self.assertFalse(report["logged_in"])
        self.assertEqual(report["mastered"], 0)
        self.assertTrue(all(row["gap"] for row in report["resources"]))


if __name__ == "__main__":
    unittest.main()
