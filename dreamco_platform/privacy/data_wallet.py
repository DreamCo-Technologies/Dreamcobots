"""Consent-first personal data connections, use, export, and opt-out controls.

The wallet records encrypted data references and rights metadata, never raw
credentials. Data sale or licensing is off by default and cannot include highly
sensitive, minor, unowned, or unlicensed third-party data.
"""

from __future__ import annotations

import hashlib
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class DataWalletError(ValueError):
    """Raised when a data request lacks consent, rights, or purpose."""


class DataCategory(str, Enum):
    PROFILE = "profile"
    PREFERENCES = "preferences"
    APP_ACTIVITY = "app_activity"
    PURCHASES = "purchases"
    FINANCIAL = "financial"
    VOICE = "voice"
    LIKENESS = "likeness"
    HEALTH = "health"
    LOCATION = "location"
    CONTACTS = "contacts"
    MESSAGES = "messages"
    GOVERNMENT_ID = "government_id"
    CREDENTIALS = "credentials"
    CHILD_DATA = "child_data"


SENSITIVE_CATEGORIES = {
    DataCategory.FINANCIAL,
    DataCategory.VOICE,
    DataCategory.LIKENESS,
    DataCategory.HEALTH,
    DataCategory.LOCATION,
    DataCategory.CONTACTS,
    DataCategory.MESSAGES,
    DataCategory.GOVERNMENT_ID,
    DataCategory.CREDENTIALS,
    DataCategory.CHILD_DATA,
}
NON_TRANSFERABLE_CATEGORIES = SENSITIVE_CATEGORIES
ALLOWED_PURPOSES = {
    "app_functionality",
    "personal_assistance",
    "personalization",
    "private_model_training",
    "portability",
    "analytics_for_user",
    "licensed_data_package",
}


@dataclass(frozen=True)
class DataSource:
    source_id: str
    owner_user_id: str
    display_name: str
    encrypted_reference: str
    categories: tuple[DataCategory, ...]
    acquisition: str
    user_owns_data: bool
    resale_license_confirmed: bool = False
    contains_minor_data: bool = False

    def validate(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9-]{2,63}", self.source_id):
            raise DataWalletError("Data source id must be a stable lowercase slug.")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:/-]{2,127}", self.encrypted_reference):
            raise DataWalletError("Use an encrypted vault reference, never raw data or credentials.")
        if not self.categories:
            raise DataWalletError("At least one data category is required.")
        if len(self.display_name.strip()) < 2:
            raise DataWalletError("A readable data source name is required.")
        if self.acquisition not in {"user_upload", "official_export", "authorized_connector", "public_domain"}:
            raise DataWalletError("Data must come from an approved acquisition route.")


@dataclass(frozen=True)
class DataPermissionRequest:
    source_id: str
    purposes: tuple[str, ...]
    retention_days: int
    explicit_collection_consent: bool
    private_model_training_opt_in: bool = False
    third_party_license_opt_in: bool = False
    recipient_class: str = ""


@dataclass
class PrivacyChoices:
    collection_enabled: bool = True
    personalization_enabled: bool = True
    private_training_enabled: bool = False
    third_party_sale_or_share_enabled: bool = False
    global_opt_out: bool = False
    updated_at: float = field(default_factory=time.time)


class BuddyDataWallet:
    """Hold source metadata, grants, and privacy choices for one user."""

    def __init__(self, owner_user_id: str):
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", owner_user_id):
            raise DataWalletError("A stable owner id is required.")
        self.owner_user_id = owner_user_id
        self.sources: dict[str, DataSource] = {}
        self.grants: dict[str, dict[str, Any]] = {}
        self.choices = PrivacyChoices()

    def register_source(self, source: DataSource) -> dict[str, Any]:
        source.validate()
        if source.owner_user_id != self.owner_user_id:
            raise DataWalletError("A user can only connect sources to their own wallet.")
        if source.contains_minor_data or DataCategory.CHILD_DATA in source.categories:
            raise DataWalletError("Minor data cannot be connected to this general-purpose data wallet.")
        if DataCategory.CREDENTIALS in source.categories:
            raise DataWalletError("Credentials belong in the secret broker, not the data wallet.")
        self.sources[source.source_id] = source
        return {
            "schema": "dreamco.data_source_receipt.v1",
            "source_id": source.source_id,
            "categories": [category.value for category in source.categories],
            "raw_data_stored_here": False,
            "encrypted_reference_fingerprint": hashlib.sha256(
                source.encrypted_reference.encode("utf-8")
            ).hexdigest()[:20],
        }

    def authorize(self, request: DataPermissionRequest) -> dict[str, Any]:
        source = self.sources.get(request.source_id)
        if source is None:
            raise DataWalletError("The requested data source is not connected.")
        if self.choices.global_opt_out or not self.choices.collection_enabled:
            raise DataWalletError("The user's privacy choices block data use.")
        purposes = tuple(dict.fromkeys(purpose.strip() for purpose in request.purposes if purpose.strip()))
        if not purposes or set(purposes) - ALLOWED_PURPOSES:
            raise DataWalletError("Every data use needs a supported, specific purpose.")
        if not request.explicit_collection_consent:
            raise DataWalletError("Explicit collection consent is required.")
        if request.retention_days < 1 or request.retention_days > 365:
            raise DataWalletError("Retention must be between 1 and 365 days.")
        if "private_model_training" in purposes:
            if not request.private_model_training_opt_in or not self.choices.private_training_enabled:
                raise DataWalletError("Private model training requires a separate user opt-in.")
        if "licensed_data_package" in purposes:
            self._validate_license_request(source, request)

        grant_id = f"data-grant-{uuid.uuid4().hex[:16]}"
        grant = {
            "schema": "dreamco.data_permission_receipt.v1",
            "grant_id": grant_id,
            "source_id": source.source_id,
            "purposes": list(purposes),
            "categories": [category.value for category in source.categories],
            "recipient_class": request.recipient_class or None,
            "created_at": time.time(),
            "expires_at": time.time() + request.retention_days * 86400,
            "revoked_at": None,
            "sale_or_share_opt_in": "licensed_data_package" in purposes,
            "raw_data_in_receipt": False,
        }
        self.grants[grant_id] = grant
        return dict(grant)

    def _validate_license_request(self, source: DataSource, request: DataPermissionRequest) -> None:
        if not request.third_party_license_opt_in or not self.choices.third_party_sale_or_share_enabled:
            raise DataWalletError("Data licensing requires a separate, revocable opt-in.")
        if not source.user_owns_data or not source.resale_license_confirmed:
            raise DataWalletError("The user must own the data and have confirmed resale rights.")
        if set(source.categories) & NON_TRANSFERABLE_CATEGORIES:
            raise DataWalletError("Sensitive personal data cannot be sold or licensed through Buddy.")
        if len(request.recipient_class.strip()) < 3:
            raise DataWalletError("The user must approve the recipient class.")

    def opt_out(self, *, stop_collection: bool = True, stop_sale_or_share: bool = True) -> dict[str, Any]:
        now = time.time()
        if stop_collection:
            self.choices.collection_enabled = False
        if stop_sale_or_share:
            self.choices.third_party_sale_or_share_enabled = False
        self.choices.global_opt_out = stop_collection and stop_sale_or_share
        self.choices.updated_at = now
        revoked = 0
        for grant in self.grants.values():
            if grant["revoked_at"] is None:
                grant["revoked_at"] = now
                revoked += 1
        return {
            "schema": "dreamco.privacy_opt_out_receipt.v1",
            "status": "applied",
            "collection_enabled": self.choices.collection_enabled,
            "sale_or_share_enabled": self.choices.third_party_sale_or_share_enabled,
            "grants_revoked": revoked,
            "non_discrimination_required": True,
        }

    def export_plan(self) -> dict[str, Any]:
        return {
            "schema": "dreamco.data_portability_plan.v1",
            "owner_user_id": self.owner_user_id,
            "format": "machine_readable_json_archive",
            "sources": [
                {
                    "source_id": source.source_id,
                    "categories": [category.value for category in source.categories],
                    "encrypted_reference": "redacted",
                }
                for source in self.sources.values()
            ],
            "grants": [dict(grant) for grant in self.grants.values()],
            "privacy_choices": asdict(self.choices),
            "identity_verification_required": True,
        }
