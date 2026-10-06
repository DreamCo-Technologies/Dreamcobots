import unittest

from buddy.accounts.course_study import study
from buddy.accounts.plugin_manager import catalog
from buddy.learning.permissioned_views import PermissionError


class PluginManagerTest(unittest.TestCase):
    def test_catalog_stores_no_secrets_and_study_needs_permission(self) -> None:
        report = catalog(["linear"])
        self.assertIn("linear", report["accounts"]["user-added"])
        self.assertFalse(report["secrets_stored"])
        with self.assertRaises(PermissionError):
            study("codecademy", "loops", False)
        learned = study("codecademy", "loops", True)
        self.assertFalse(learned["fetched"])


if __name__ == "__main__":
    unittest.main()
