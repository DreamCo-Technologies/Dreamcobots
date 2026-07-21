"""PII anonymizer for DataForge AI datasets."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import re

logger = logging.getLogger(__name__)

PII_PATTERNS = {
    "email": (re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"), "[EMAIL_REDACTED]"),
    "phone": (re.compile(r"\b(\+?1[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})\b"), "[PHONE_REDACTED]"),
    "ssn": (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN_REDACTED]"),
    "credit_card": (re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), "[CC_REDACTED]"),
    "name_pattern": (re.compile(r"\b(Mr\.|Mrs\.|Ms\.|Dr\.)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b"), "[NAME_REDACTED]"),
    "zip_code": (re.compile(r"\b\d{5}(?:-\d{4})?\b"), "[ZIP_REDACTED]"),
    "ip_address": (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "[IP_REDACTED]"),
}


class DataAnonymizer:
    """Removes PII from text and records using regex-based pattern matching."""

    def anonymize_text(self, text: str) -> str:
        """Replace PII patterns in text with redaction tokens.

        Args:
            text: Input text to anonymize.

        Returns:
            Text with all PII patterns replaced by redaction tokens.
        """
        if not isinstance(text, str):
            return text
        for pii_type, (pattern, replacement) in PII_PATTERNS.items():
            text = pattern.sub(replacement, text)
        return text

    def anonymize_record(self, record: dict) -> dict:
        """Anonymize all string fields in a dict record.

        Args:
            record: Dict record to anonymize.

        Returns:
            New dict with all string fields anonymized.
        """
        anonymized = {}
        for key, value in record.items():
            if isinstance(value, str):
                anonymized[key] = self.anonymize_text(value)
            elif isinstance(value, dict):
                anonymized[key] = self.anonymize_record(value)
            elif isinstance(value, list):
                anonymized[key] = self.anonymize_dataset(value)
            else:
                anonymized[key] = value
        logger.debug("Anonymized record with %d fields.", len(anonymized))
        return anonymized

    def anonymize_dataset(self, dataset: list) -> list:
        """Anonymize all records in a dataset list.

        Args:
            dataset: List of records (dicts or strings) to anonymize.

        Returns:
            List with all records anonymized.
        """
        result = []
        for item in dataset:
            if isinstance(item, dict):
                result.append(self.anonymize_record(item))
            elif isinstance(item, str):
                result.append(self.anonymize_text(item))
            else:
                result.append(item)
        logger.info("Anonymized dataset of %d records.", len(dataset))
        return result
