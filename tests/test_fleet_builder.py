import unittest

from tools.fleet_builder import plan


class FleetBuilderTest(unittest.TestCase):
    def test_train_and_deploy_stay_blocked_without_flags(self) -> None:
        report = plan("media", "voice-clone")
        blocked = [row["stage"] for row in report["stages"] if row["status"] == "blocked"]
        self.assertEqual(blocked, ["train", "deploy"])
        self.assertFalse(report["green"])
        self.assertFalse(report["deployed"])


if __name__ == "__main__":
    unittest.main()
