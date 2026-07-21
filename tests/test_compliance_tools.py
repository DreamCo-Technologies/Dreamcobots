"""Tests for the Compliance Tools — ComplianceChecker."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _import_checker():
    tools_dir = os.path.join(os.path.dirname(__file__), "..", "compliance-tools")
    sys.path.insert(0, tools_dir)
    import importlib
    return importlib.import_module("compliance_checker")


@pytest.fixture
def cc_module():
    return _import_checker()


@pytest.fixture
def checker(cc_module):
    return cc_module.ComplianceChecker()


@pytest.fixture
def full_gdpr_profile():
    return {
        "data_minimization": True,
        "consent_mechanism": True,
        "right_to_erasure": True,
        "data_breach_notification": True,
        "privacy_policy": True,
        "data_processor_agreements": True,
        "dpo_designation": True,
        "cross_border_transfers": True,
    }


class TestListFrameworks:
    def test_returns_list(self, checker):
        result = checker.list_frameworks()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_framework_keys(self, checker):
        frameworks = checker.list_frameworks()
        for fw in frameworks:
            assert "id" in fw
            assert "name" in fw
            assert "region" in fw
            assert "total_checks" in fw

    def test_includes_gdpr(self, checker):
        ids = [fw["id"] for fw in checker.list_frameworks()]
        assert "GDPR" in ids

    def test_includes_hipaa(self, checker):
        ids = [fw["id"] for fw in checker.list_frameworks()]
        assert "HIPAA" in ids

    def test_includes_pci_dss(self, checker):
        ids = [fw["id"] for fw in checker.list_frameworks()]
        assert "PCI_DSS" in ids

    def test_all_expected_frameworks(self, checker):
        ids = [fw["id"] for fw in checker.list_frameworks()]
        for expected in ("GDPR", "CCPA", "HIPAA", "SOC2", "PCI_DSS", "ADA", "OSHA", "ISO_27001"):
            assert expected in ids


class TestGetFramework:
    def test_get_gdpr(self, checker):
        fw = checker.get_framework("GDPR")
        assert fw["id"] == "GDPR"
        assert fw["region"] == "EU"
        assert isinstance(fw["checks"], list)

    def test_get_hipaa(self, checker):
        fw = checker.get_framework("HIPAA")
        assert fw["id"] == "HIPAA"

    def test_case_insensitive(self, checker):
        fw = checker.get_framework("gdpr")
        assert fw["id"] == "GDPR"

    def test_unknown_framework_returns_error(self, checker):
        result = checker.get_framework("UNKNOWN_XYZ")
        assert "error" in result


class TestCheckCompliance:
    def test_returns_dict(self, checker):
        result = checker.check_compliance("GDPR")
        assert isinstance(result, dict)

    def test_required_keys(self, checker):
        result = checker.check_compliance("GDPR")
        for key in ("framework", "score_pct", "passed", "failed", "total_checks",
                    "risk_level", "findings", "generated_at"):
            assert key in result

    def test_score_zero_no_profile(self, checker):
        result = checker.check_compliance("GDPR")
        assert result["score_pct"] == 0.0

    def test_score_100_full_profile(self, checker, full_gdpr_profile):
        result = checker.check_compliance("GDPR", full_gdpr_profile)
        assert result["score_pct"] == 100.0

    def test_partial_profile_score_between(self, checker):
        profile = {"data_minimization": True, "privacy_policy": True}
        result = checker.check_compliance("GDPR", profile)
        assert 0 < result["score_pct"] < 100

    def test_risk_level_low_for_high_score(self, checker, full_gdpr_profile):
        result = checker.check_compliance("GDPR", full_gdpr_profile)
        assert result["risk_level"] == "low"

    def test_risk_level_high_for_zero_score(self, checker):
        result = checker.check_compliance("GDPR")
        assert result["risk_level"] == "high"

    def test_findings_count_matches_checks(self, checker):
        result = checker.check_compliance("GDPR")
        assert len(result["findings"]) == result["total_checks"]

    def test_findings_have_status(self, checker):
        result = checker.check_compliance("GDPR")
        for finding in result["findings"]:
            assert finding["status"] in ("pass", "fail")

    def test_findings_have_severity(self, checker):
        result = checker.check_compliance("GDPR")
        for finding in result["findings"]:
            assert finding["severity"] in ("critical", "high", "medium", "low")

    def test_findings_have_recommendation(self, checker):
        result = checker.check_compliance("GDPR")
        for finding in result["findings"]:
            assert isinstance(finding["recommendation"], str)
            assert len(finding["recommendation"]) > 0

    def test_unknown_framework_returns_error(self, checker):
        result = checker.check_compliance("NOT_A_FRAMEWORK")
        assert "error" in result

    def test_hipaa_compliance(self, checker):
        profile = {"phi_encryption": True, "access_controls": True, "audit_logs": True}
        result = checker.check_compliance("HIPAA", profile)
        assert result["score_pct"] > 0

    def test_pci_dss_compliance(self, checker):
        result = checker.check_compliance("PCI_DSS")
        assert "framework" in result
        assert result["framework"] == "PCI_DSS"

    def test_audit_log_updated(self, checker):
        checker.check_compliance("GDPR")
        log = checker.get_audit_log()
        assert len(log) >= 1
        assert log[-1]["action"] == "check_compliance"
        assert log[-1]["framework"] == "GDPR"


class TestMultipleFrameworks:
    def test_returns_list(self, checker):
        results = checker.check_multiple_frameworks(["GDPR", "CCPA"])
        assert isinstance(results, list)
        assert len(results) == 2

    def test_each_result_has_framework(self, checker):
        results = checker.check_multiple_frameworks(["GDPR", "HIPAA", "SOC2"])
        framework_ids = [r["framework"] for r in results]
        assert "GDPR" in framework_ids
        assert "HIPAA" in framework_ids
        assert "SOC2" in framework_ids


class TestRiskScore:
    def test_returns_dict(self, checker):
        reports = [checker.check_compliance("GDPR")]
        result = checker.calculate_risk_score(reports)
        assert isinstance(result, dict)

    def test_empty_reports(self, checker):
        result = checker.calculate_risk_score([])
        assert result["overall_risk"] == "unknown"

    def test_high_risk_for_zero_scores(self, checker):
        reports = checker.check_multiple_frameworks(["GDPR", "CCPA"])
        result = checker.calculate_risk_score(reports)
        assert result["overall_risk"] == "high"

    def test_score_in_range(self, checker, full_gdpr_profile):
        reports = [checker.check_compliance("GDPR", full_gdpr_profile)]
        result = checker.calculate_risk_score(reports)
        assert 0 <= result["overall_score_pct"] <= 100

    def test_frameworks_evaluated_list(self, checker):
        reports = checker.check_multiple_frameworks(["GDPR", "CCPA"])
        result = checker.calculate_risk_score(reports)
        assert "frameworks_evaluated" in result


class TestValidateEmail:
    def test_valid_email(self, cc_module):
        assert cc_module.ComplianceChecker.validate_email("user@example.com") is True

    def test_valid_email_with_subdomain(self, cc_module):
        assert cc_module.ComplianceChecker.validate_email("user@mail.example.co.uk") is True

    def test_invalid_no_at(self, cc_module):
        assert cc_module.ComplianceChecker.validate_email("userexample.com") is False

    def test_invalid_no_domain(self, cc_module):
        assert cc_module.ComplianceChecker.validate_email("user@") is False

    def test_invalid_empty(self, cc_module):
        assert cc_module.ComplianceChecker.validate_email("") is False


class TestValidateSSN:
    def test_valid_ssn(self, cc_module):
        assert cc_module.ComplianceChecker.validate_ssn("123-45-6789") is True

    def test_invalid_no_dashes(self, cc_module):
        assert cc_module.ComplianceChecker.validate_ssn("123456789") is False

    def test_invalid_wrong_format(self, cc_module):
        assert cc_module.ComplianceChecker.validate_ssn("12-345-6789") is False


class TestMaskPII:
    def test_masks_email(self, cc_module):
        result = cc_module.ComplianceChecker.mask_pii("Contact john@example.com for info")
        assert "[EMAIL REDACTED]" in result
        assert "john@example.com" not in result

    def test_masks_ssn(self, cc_module):
        result = cc_module.ComplianceChecker.mask_pii("SSN: 123-45-6789 is on file")
        assert "[SSN REDACTED]" in result
        assert "123-45-6789" not in result

    def test_no_pii_unchanged(self, cc_module):
        text = "Hello world this is clean text"
        result = cc_module.ComplianceChecker.mask_pii(text)
        assert result == text

    def test_multiple_pii_types(self, cc_module):
        text = "Email: test@test.com, SSN: 123-45-6789"
        result = cc_module.ComplianceChecker.mask_pii(text)
        assert "[EMAIL REDACTED]" in result
        assert "[SSN REDACTED]" in result


class TestHashIdentifier:
    def test_returns_string(self, cc_module):
        result = cc_module.ComplianceChecker.hash_identifier("user@example.com")
        assert isinstance(result, str)

    def test_returns_sha256_length(self, cc_module):
        result = cc_module.ComplianceChecker.hash_identifier("user@example.com")
        assert len(result) == 64  # SHA-256 hex = 64 chars

    def test_deterministic(self, cc_module):
        a = cc_module.ComplianceChecker.hash_identifier("same_input")
        b = cc_module.ComplianceChecker.hash_identifier("same_input")
        assert a == b

    def test_different_inputs_different_hashes(self, cc_module):
        a = cc_module.ComplianceChecker.hash_identifier("input_one")
        b = cc_module.ComplianceChecker.hash_identifier("input_two")
        assert a != b


class TestAuditLog:
    def test_initially_empty(self, checker):
        assert checker.get_audit_log() == []

    def test_appended_after_check(self, checker):
        checker.check_compliance("GDPR")
        log = checker.get_audit_log()
        assert len(log) == 1

    def test_multiple_checks_logged(self, checker):
        checker.check_compliance("GDPR")
        checker.check_compliance("HIPAA")
        log = checker.get_audit_log()
        assert len(log) == 2

    def test_log_is_copy(self, checker):
        checker.check_compliance("GDPR")
        log = checker.get_audit_log()
        log.clear()
        assert len(checker.get_audit_log()) == 1
