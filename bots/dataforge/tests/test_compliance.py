"""Tests for compliance modules."""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


class TestGDPRChecker(unittest.TestCase):
    """Tests for GDPRComplianceChecker."""

    def setUp(self):
        """Set up test fixtures."""
        from bots.dataforge.compliance import GDPRComplianceChecker
        self.checker = GDPRComplianceChecker()

    def test_gdpr_checker_compliant(self):
        """Test that fully compliant metadata passes GDPR check."""
        meta = {"consent": True, "anonymized": True, "license": "CC-BY-4.0", "data_subject_rights": True}
        result = self.checker.check_compliance(meta)
        self.assertTrue(result["compliant"])

    def test_gdpr_checker_non_compliant(self):
        """Test that incomplete metadata fails GDPR check."""
        meta = {"consent": False}
        result = self.checker.check_compliance(meta)
        self.assertFalse(result["compliant"])
        self.assertGreater(len(result["issues"]), 0)


class TestCCPAChecker(unittest.TestCase):
    """Tests for CCPAComplianceChecker."""

    def setUp(self):
        """Set up test fixtures."""
        from bots.dataforge.compliance import CCPAComplianceChecker
        self.checker = CCPAComplianceChecker()

    def test_ccpa_checker(self):
        """Test CCPA compliance with all required fields present."""
        meta = {"opt_out_honored": True, "disclosure_provided": True}
        result = self.checker.check_compliance(meta)
        self.assertTrue(result["compliant"])


class TestHIPAAAnonymizer(unittest.TestCase):
    """Tests for HIPAAAnonymizer."""

    def setUp(self):
        """Set up test fixtures."""
        from bots.dataforge.compliance import HIPAAAnonymizer
        self.anon = HIPAAAnonymizer()

    def test_hipaa_anonymizer(self):
        """Test that SSN and email are removed from text."""
        text = "Patient SSN: 123-45-6789 email test@example.com"
        result = self.anon.remove_phi(text)
        self.assertNotIn("123-45-6789", result)
        self.assertNotIn("test@example.com", result)


class TestConsentManager(unittest.TestCase):
    """Tests for ConsentManager."""

    def setUp(self):
        """Set up test fixtures."""
        from bots.dataforge.compliance import ConsentManager
        self.mgr = ConsentManager()

    def test_consent_manager(self):
        """Test adding, checking, and revoking consent."""
        self.mgr.add_consent("user1", "data_selling", True)
        self.assertTrue(self.mgr.check_consent("user1", "data_selling"))
        self.mgr.revoke_consent("user1", "data_selling")
        self.assertFalse(self.mgr.check_consent("user1", "data_selling"))


class TestDataAnonymizer(unittest.TestCase):
    """Tests for DataAnonymizer."""

    def setUp(self):
        """Set up test fixtures."""
        from bots.dataforge.licensing.anonymizer import DataAnonymizer
        self.anon = DataAnonymizer()

    def test_anonymizer(self):
        """Test that email is redacted from text."""
        text = "Contact: john@example.com or call 555-123-4567"
        result = self.anon.anonymize_text(text)
        self.assertNotIn("john@example.com", result)
        self.assertIn("EMAIL_REDACTED", result)


if __name__ == "__main__":
    unittest.main()
