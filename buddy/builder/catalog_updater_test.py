import unittest

from buddy.builder.catalog_updater import update


class CatalogUpdaterTest(unittest.TestCase):
    def test_updater_counts_files_and_does_not_mark_ready(self) -> None:
        report = update()
        self.assertGreater(report["new_bots"], 1000)
        self.assertEqual(report["production_ready"], 0)
        self.assertFalse(report["updated_catalog"])


if __name__ == "__main__":
    unittest.main()
