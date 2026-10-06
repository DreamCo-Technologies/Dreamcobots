import unittest

from buddy.builder.self_training import start


class SelfTrainingTest(unittest.TestCase):
    def test_training_starts_only_when_enabled_and_downloads_nothing(self) -> None:
        with self.assertRaises(PermissionError):
            start("note", False)
        report = start("loops", True)
        self.assertTrue(report["started"])
        self.assertFalse(report["weights_downloaded"])
        self.assertFalse(report["production_ready"])


if __name__ == "__main__":
    unittest.main()
