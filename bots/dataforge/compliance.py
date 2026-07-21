"""Compliance module: GDPR, CCPA, HIPAA, Biometric, Consent, Anonymization, Licensing."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class GDPRComplianceChecker:
    """Checks GDPR compliance for datasets and data operations."""

    REQUIRED_FIELDS = ["consent", "anonymized", "license", "data_subject_rights"]

    def check_compliance(self, dataset_metadata: dict) -> dict:
        """Check if dataset metadata meets GDPR requirements.

        Args:
            dataset_metadata: Metadata dict to check for GDPR compliance.

        Returns:
            Dict with keys 'compliant' (bool) and 'issues' (list of strings).
        """
        issues = []
        for field in self.REQUIRED_FIELDS:
            if field not in dataset_metadata:
                issues.append(f"Missing required GDPR field: {field}")
        if not dataset_metadata.get("consent"):
            issues.append("GDPR: Consent not recorded.")
        if not dataset_metadata.get("anonymized"):
            issues.append("GDPR: Data must be anonymized.")
        compliant = len(issues) == 0
        logger.info("GDPR compliance check: %s, issues: %s", compliant, issues)
        return {"compliant": compliant, "issues": issues}

    def validate_consent(self, user_id: str, consent_record: dict) -> bool:
        """Validate that consent is properly recorded for a user.

        Args:
            user_id: The user identifier.
            consent_record: Dict with 'granted' and 'timestamp' keys.

        Returns:
            True if consent is valid, False otherwise.
        """
        if not consent_record.get("granted"):
            logger.warning("GDPR: No consent granted for user %s", user_id)
            return False
        if not consent_record.get("timestamp"):
            logger.warning("GDPR: Consent has no timestamp for user %s", user_id)
            return False
        logger.info("GDPR: Consent valid for user %s", user_id)
        return True

    def check_right_to_erasure(self, user_id: str, data_store: dict) -> dict:
        """Check and process right to erasure (right to be forgotten) request.

        Args:
            user_id: The user requesting erasure.
            data_store: The data store dict to remove the user from.

        Returns:
            Dict with user_id, erased status, and timestamp.
        """
        erased = user_id in data_store
        if erased:
            del data_store[user_id]
            logger.info("GDPR: Erased data for user %s", user_id)
        else:
            logger.info("GDPR: No data found for user %s to erase", user_id)
        return {"user_id": user_id, "erased": erased, "timestamp": datetime.utcnow().isoformat()}


class CCPAComplianceChecker:
    """Checks CCPA compliance for California Consumer Privacy Act."""

    def check_compliance(self, dataset_metadata: dict) -> dict:
        """Check CCPA compliance for a dataset.

        Args:
            dataset_metadata: Metadata dict to check for CCPA compliance.

        Returns:
            Dict with 'compliant' (bool) and 'issues' (list of strings).
        """
        issues = []
        if not dataset_metadata.get("opt_out_honored"):
            issues.append("CCPA: Opt-out requests must be honored.")
        if not dataset_metadata.get("disclosure_provided"):
            issues.append("CCPA: Must disclose data collection practices.")
        compliant = len(issues) == 0
        logger.info("CCPA compliance: %s, issues: %s", compliant, issues)
        return {"compliant": compliant, "issues": issues}

    def validate_opt_out(self, user_id: str, opt_out_record: dict) -> bool:
        """Validate that a user's opt-out request has been properly recorded.

        Args:
            user_id: The user identifier.
            opt_out_record: Dict with 'opted_out' key.

        Returns:
            True if opt-out is recorded, False otherwise.
        """
        if not opt_out_record.get("opted_out"):
            logger.info("CCPA: User %s has not opted out.", user_id)
            return False
        logger.info("CCPA: Opt-out validated for user %s", user_id)
        return True


class HIPAAAnonymizer:
    """HIPAA-compliant anonymization for Protected Health Information (PHI)."""

    PHI_PATTERNS = {
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "dob": re.compile(r"\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/\d{4}\b"),
        "phone": re.compile(r"\b(\+1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b"),
        "email": re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
        "mrn": re.compile(r"\bMRN[:\s]?\d+\b", re.IGNORECASE),
    }

    def safe_harbor_anonymize(self, record: dict) -> dict:
        """Apply HIPAA Safe Harbor de-identification to a record.

        Args:
            record: Dict record potentially containing PHI.

        Returns:
            New dict with PHI removed from all string fields.
        """
        safe = {}
        for key, value in record.items():
            if isinstance(value, str):
                safe[key] = self.remove_phi(value)
            else:
                safe[key] = value
        logger.debug("HIPAA Safe Harbor anonymization applied.")
        return safe

    def remove_phi(self, text: str) -> str:
        """Remove Protected Health Information from text.

        Args:
            text: Input text potentially containing PHI.

        Returns:
            Text with all PHI patterns replaced by redaction tokens.
        """
        for phi_type, pattern in self.PHI_PATTERNS.items():
            text = pattern.sub(f"[{phi_type.upper()}_REDACTED]", text)
        return text


class BiometricDataProtector:
    """Protects biometric data per BIPA and other biometric privacy laws."""

    def validate_biometric_data(self, record: dict) -> dict:
        """Validate that biometric data has required protections.

        Args:
            record: Data record to validate for biometric compliance.

        Returns:
            Dict with 'valid' (bool) and 'issues' (list of strings).
        """
        issues = []
        if not record.get("synthetic") and not record.get("consent_biometric"):
            issues.append("Biometric: Real biometric data requires explicit consent.")
        if not record.get("anonymized"):
            issues.append("Biometric: Data must be anonymized.")
        valid = len(issues) == 0
        logger.info("Biometric validation: %s, issues: %s", valid, issues)
        return {"valid": valid, "issues": issues}

    def check_consent(self, user_id: str, consent_store: dict) -> bool:
        """Check that biometric consent exists for a user.

        Args:
            user_id: The user identifier.
            consent_store: Dict mapping user IDs to consent records.

        Returns:
            True if biometric consent is recorded for the user.
        """
        has_consent = consent_store.get(user_id, {}).get("biometric_consent", False)
        logger.info("Biometric consent for %s: %s", user_id, has_consent)
        return has_consent


class ConsentManager:
    """Manages user consent records for data collection and selling."""

    def __init__(self):
        """Initialize the ConsentManager with an empty consent log."""
        self._consent_log: dict = {}

    def add_consent(self, user_id: str, consent_type: str, granted: bool = True) -> dict:
        """Add or update a consent record for a user.

        Args:
            user_id: The user identifier.
            consent_type: Type of consent (e.g., 'data_selling', 'marketing').
            granted: Whether consent is granted (default True).

        Returns:
            The consent record dict.
        """
        if user_id not in self._consent_log:
            self._consent_log[user_id] = {}
        self._consent_log[user_id][consent_type] = {
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.info("Consent recorded: user=%s type=%s granted=%s", user_id, consent_type, granted)
        return self._consent_log[user_id][consent_type]

    def check_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if a user has granted a specific type of consent.

        Args:
            user_id: The user identifier.
            consent_type: Type of consent to check.

        Returns:
            True if consent is granted, False otherwise.
        """
        result = self._consent_log.get(user_id, {}).get(consent_type, {}).get("granted", False)
        logger.debug("Check consent: user=%s type=%s -> %s", user_id, consent_type, result)
        return result

    def revoke_consent(self, user_id: str, consent_type: str) -> bool:
        """Revoke a specific consent for a user.

        Args:
            user_id: The user identifier.
            consent_type: Type of consent to revoke.

        Returns:
            True if consent was revoked, False if no record found.
        """
        if user_id in self._consent_log and consent_type in self._consent_log[user_id]:
            self._consent_log[user_id][consent_type]["granted"] = False
            self._consent_log[user_id][consent_type]["revoked_at"] = datetime.utcnow().isoformat()
            logger.info("Consent revoked: user=%s type=%s", user_id, consent_type)
            return True
        logger.warning("No consent record found to revoke: user=%s type=%s", user_id, consent_type)
        return False


class DataAnonymizationPipeline:
    """Full anonymization pipeline combining HIPAA and general PII removal."""

    def __init__(self):
        """Initialize the pipeline with HIPAA anonymizer and consent manager."""
        self._hipaa = HIPAAAnonymizer()
        self._consent = ConsentManager()

    def anonymize(self, dataset: list) -> list:
        """Anonymize a list of records.

        Args:
            dataset: List of record dicts to anonymize.

        Returns:
            List of anonymized record dicts.
        """
        anonymized = [self._hipaa.safe_harbor_anonymize(r) for r in dataset]
        logger.info("Anonymized %d records.", len(anonymized))
        return anonymized

    def package(self, dataset: list, metadata: dict) -> dict:
        """Package anonymized dataset with metadata.

        Args:
            dataset: List of records to anonymize and package.
            metadata: Metadata dict to attach to the package.

        Returns:
            Package dict with metadata, records, record_count, anonymized flag, and timestamp.
        """
        anon_data = self.anonymize(dataset)
        package = {
            "metadata": metadata,
            "records": anon_data,
            "record_count": len(anon_data),
            "anonymized": True,
            "packaged_at": datetime.utcnow().isoformat(),
        }
        logger.info("Dataset packaged: %d records", len(anon_data))
        return package


class LicenseGenerator:
    """Generates dataset licenses for commercial, non-commercial, and research use."""

    def generate_commercial(self, dataset_name: str, version: str = "1.0") -> str:
        """Generate a commercial license for a dataset.

        Args:
            dataset_name: Name of the dataset.
            version: Version string (default '1.0').

        Returns:
            Commercial license text string.
        """
        return (
            f"COMMERCIAL LICENSE - {dataset_name} v{version}\n"
            "This dataset is licensed for commercial use. Redistribution permitted with attribution.\n"
            "License: CC-BY-4.0 | DataForge AI Systems"
        )

    def generate_non_commercial(self, dataset_name: str, version: str = "1.0") -> str:
        """Generate a non-commercial license for a dataset.

        Args:
            dataset_name: Name of the dataset.
            version: Version string (default '1.0').

        Returns:
            Non-commercial license text string.
        """
        return (
            f"NON-COMMERCIAL LICENSE - {dataset_name} v{version}\n"
            "This dataset may not be used for commercial purposes.\n"
            "License: CC-BY-NC-4.0 | DataForge AI Systems"
        )

    def generate_research_only(self, dataset_name: str, version: str = "1.0") -> str:
        """Generate a research-only license for a dataset.

        Args:
            dataset_name: Name of the dataset.
            version: Version string (default '1.0').

        Returns:
            Research-only license text string.
        """
        return (
            f"RESEARCH-ONLY LICENSE - {dataset_name} v{version}\n"
            "This dataset is licensed for academic and non-profit research use only.\n"
            "License: CC-BY-NC-ND-4.0 | DataForge AI Systems"
        )
