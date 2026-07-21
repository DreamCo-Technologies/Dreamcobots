"""Consent manager for DataForge AI data collection."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConsentManager:
    """Manages user consent records for data collection and usage."""

    def __init__(self):
        """Initialize the ConsentManager with an empty consent log."""
        self._consent_log: dict = {}

    def record_consent(self, user_id: str, consent_type: str, granted: bool = True) -> dict:
        """Record a consent decision for a user.

        Args:
            user_id: The user identifier.
            consent_type: Type of consent being recorded.
            granted: Whether consent is granted (default True).

        Returns:
            The consent entry dict.
        """
        if user_id not in self._consent_log:
            self._consent_log[user_id] = {}
        entry = {
            "granted": granted,
            "consent_type": consent_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._consent_log[user_id][consent_type] = entry
        logger.info("Consent recorded: user=%s type=%s granted=%s", user_id, consent_type, granted)
        return entry

    def check_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if a user has granted a specific consent type.

        Args:
            user_id: The user identifier.
            consent_type: Type of consent to check.

        Returns:
            True if consent is granted, False otherwise.
        """
        result = self._consent_log.get(user_id, {}).get(consent_type, {}).get("granted", False)
        logger.debug("Consent check: user=%s type=%s -> %s", user_id, consent_type, result)
        return result

    def revoke_consent(self, user_id: str, consent_type: str) -> bool:
        """Revoke a previously granted consent.

        Args:
            user_id: The user identifier.
            consent_type: Type of consent to revoke.

        Returns:
            True if revoked, False if no record found.
        """
        if user_id in self._consent_log and consent_type in self._consent_log[user_id]:
            self._consent_log[user_id][consent_type]["granted"] = False
            self._consent_log[user_id][consent_type]["revoked_at"] = datetime.utcnow().isoformat()
            logger.info("Consent revoked: user=%s type=%s", user_id, consent_type)
            return True
        logger.warning("Revoke failed: no record for user=%s type=%s", user_id, consent_type)
        return False

    def export_consent_log(self) -> dict:
        """Export the full consent log.

        Returns:
            Copy of the full consent log dict.
        """
        logger.info("Exporting consent log with %d users.", len(self._consent_log))
        return dict(self._consent_log)
