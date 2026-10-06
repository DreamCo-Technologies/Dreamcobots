import unittest

from buddy.accounts.own_model import build_plan, own_model
from buddy.learning.permissioned_views import PermissionError


class OwnModelTest(unittest.TestCase):
    def test_owner_study_does_not_download_and_user_can_choose(self) -> None:
        report = own_model(["support-bot"], {"youtube": "channel"}, False, True)
        self.assertFalse(report["weights_downloaded"])
        self.assertFalse(report["secrets_stored"])
        self.assertGreater(len(report["experts"]), 5)
        with self.assertRaises(PermissionError):
            own_model(["support-bot"], {"youtube": "channel"}, True, True)
        plan = build_plan(77, 119)
        self.assertFalse(plan["deleted"])
        self.assertFalse(plan["frontier_claim"])


if __name__ == "__main__":
    unittest.main()
