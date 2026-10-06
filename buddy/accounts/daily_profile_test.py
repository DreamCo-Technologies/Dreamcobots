import unittest

from buddy.accounts.daily_profile import profile
from buddy.accounts.training_sources import catalog
from buddy.learning.permissioned_views import PermissionError


class DailyProfileTest(unittest.TestCase):
    def test_profile_needs_permission_and_does_not_download(self) -> None:
        self.assertGreater(len(catalog()["kinds"]), 20)
        with self.assertRaises(PermissionError):
            profile("loops", False)
        report = profile("loops", True, "org/example")
        self.assertFalse(report["weights_downloaded"])
        self.assertFalse(report["frontier_claim"])


if __name__ == "__main__":
    unittest.main()
