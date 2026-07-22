"""Owner-controlled business, prototype, website, and app release workflows.

Buddy prepares evidence and official handoffs. Government registrations, store
agreements, fees, signing identities, and final submissions remain user actions.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class LaunchpadError(ValueError):
    """Raised when a launch request is incomplete or unsafe."""


class StoreTarget(str, Enum):
    WEB = "web"
    PWA = "pwa"
    APPLE = "apple_app_store"
    GOOGLE_PLAY = "google_play"
    MICROSOFT = "microsoft_store"
    STEAM = "steam"
    EPIC = "epic_games_store"
    CUSTOM = "custom_store"


OFFICIAL_RESOURCES = {
    "us_business_registration": "https://www.sba.gov/business-guide/launch-your-business/register-your-business",
    "apple_submission": "https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app",
    "google_play_setup": "https://support.google.com/googleplay/android-developer/answer/9859152",
    "google_play_review": "https://support.google.com/googleplay/android-developer/answer/9859455",
}


STORE_REQUIREMENTS: dict[StoreTarget, dict[str, Any]] = {
    StoreTarget.WEB: {
        "artifact": "versioned static or server build",
        "account": "domain and hosting account",
        "checks": ["production build", "HTTPS", "privacy policy", "accessibility", "rollback"],
    },
    StoreTarget.PWA: {
        "artifact": "web app manifest and service worker",
        "account": "domain and hosting account",
        "checks": ["installability", "offline fallback", "icons", "HTTPS", "privacy policy"],
    },
    StoreTarget.APPLE: {
        "artifact": "signed platform build",
        "account": "authorized App Store Connect role",
        "checks": ["metadata", "privacy details", "screenshots", "review access", "signing", "app review"],
        "official": OFFICIAL_RESOURCES["apple_submission"],
    },
    StoreTarget.GOOGLE_PLAY: {
        "artifact": "signed Android App Bundle",
        "account": "verified Play Console developer account",
        "checks": ["store listing", "data safety", "privacy policy", "content declarations", "testing track", "review"],
        "official": OFFICIAL_RESOURCES["google_play_setup"],
    },
    StoreTarget.MICROSOFT: {
        "artifact": "signed store package",
        "account": "authorized partner account",
        "checks": ["package validation", "listing", "age rating", "privacy", "certification"],
    },
    StoreTarget.STEAM: {
        "artifact": "tested game depot build",
        "account": "authorized distribution partner account",
        "checks": ["store page", "build branches", "content survey", "controller support", "review"],
    },
    StoreTarget.EPIC: {
        "artifact": "tested game build",
        "account": "authorized publisher account",
        "checks": ["product page", "build", "achievements policy", "cross-play review", "release approval"],
    },
    StoreTarget.CUSTOM: {
        "artifact": "store-specific signed package",
        "account": "owner-authorized publisher account",
        "checks": ["official requirements captured", "sandbox upload", "policy review", "owner submission"],
    },
}


@dataclass(frozen=True)
class BusinessFormationBrief:
    owner_user_id: str
    business_name: str
    country: str
    region: str
    entity_type: str
    business_purpose: str
    owner_count: int = 1

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", self.owner_user_id):
            raise LaunchpadError("A stable owner id is required.")
        if len(self.business_name.strip()) < 2 or len(self.business_purpose.strip()) < 10:
            raise LaunchpadError("Business name and a clear purpose are required.")
        if not self.country.strip() or not self.region.strip():
            raise LaunchpadError("Country and state, province, or region are required.")
        if self.owner_count < 1 or self.owner_count > 100:
            raise LaunchpadError("Owner count must be between 1 and 100.")


@dataclass(frozen=True)
class PrototypeBrief:
    owner_user_id: str
    title: str
    product_type: str
    objective: str
    target_users: str
    preferred_stack: tuple[str, ...] = ()

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", self.owner_user_id):
            raise LaunchpadError("A stable owner id is required.")
        if len(self.title.strip()) < 3 or len(self.objective.strip()) < 15:
            raise LaunchpadError("Prototype title and a detailed objective are required.")
        if self.product_type not in {
            "website", "web_app", "mobile_app", "desktop_app", "game",
            "simulation", "course", "creative_tool", "bot_system",
        }:
            raise LaunchpadError("Unsupported prototype type.")
        if not self.target_users.strip():
            raise LaunchpadError("Target users are required.")


@dataclass(frozen=True)
class AppReleaseBrief:
    owner_user_id: str
    app_name: str
    package_id: str
    version: str
    targets: tuple[StoreTarget, ...]
    privacy_policy_url: str
    support_url: str
    handles_personal_data: bool = False
    targets_children: bool = False

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", self.owner_user_id):
            raise LaunchpadError("A stable owner id is required.")
        if len(self.app_name.strip()) < 2 or not self.targets:
            raise LaunchpadError("App name and at least one release target are required.")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{2,159}", self.package_id):
            raise LaunchpadError("Use a valid package or bundle identifier.")
        if not re.fullmatch(r"[0-9]+(?:\.[0-9A-Za-z-]+){0,3}", self.version):
            raise LaunchpadError("Use a version such as 1.0.0.")
        for label, value in (("privacy policy", self.privacy_policy_url), ("support", self.support_url)):
            if not value.startswith("https://"):
                raise LaunchpadError(f"The {label} URL must use HTTPS.")


class ReleaseCouncil:
    """Deterministic evidence gate before an owner can submit a release."""

    REQUIRED = ("build", "tests", "security", "privacy", "accessibility", "rights", "rollback")

    def review(self, evidence: dict[str, bool]) -> dict[str, Any]:
        checks = {name: evidence.get(name) is True for name in self.REQUIRED}
        missing = [name for name, passed in checks.items() if not passed]
        return {
            "schema": "dreamco.release_council_review.v1",
            "status": "approved_for_owner_submission" if not missing else "changes_required",
            "checks": checks,
            "missing": missing,
            "automatic_external_submission": False,
            "owner_confirmation_required": True,
        }


class BuddyLaunchpad:
    """Build formation, prototype, and release packets routed through Buddy."""

    def business_formation_plan(self, brief: BusinessFormationBrief) -> dict[str, Any]:
        brief.validate()
        plan_id = f"formation-{uuid.uuid4().hex[:16]}"
        return {
            "schema": "dreamco.business_formation_plan.v1",
            "plan_id": plan_id,
            "status": "official_handoff_required",
            "brief": asdict(brief),
            "steps": [
                "confirm location and entity structure with a qualified professional",
                "search state and local name availability",
                "identify registered-agent requirements",
                "prepare formation document draft",
                "review licenses, permits, tax ids, insurance, and banking needs",
                "show exact filing destination and fee to the owner",
                "require owner review and presence for filing and payment",
                "record receipt and continuing-compliance dates",
            ],
            "official_resources": [OFFICIAL_RESOURCES["us_business_registration"]]
            if brief.country.strip().upper() in {"US", "USA", "UNITED STATES"}
            else [],
            "legal_advice_provided": False,
            "filing_submitted": False,
            "payment_made": False,
            "owner_presence_required": True,
        }

    def prototype_plan(self, brief: PrototypeBrief) -> dict[str, Any]:
        brief.validate()
        fingerprint = hashlib.sha256(
            f"{brief.owner_user_id}:{brief.title}:{brief.objective}".encode("utf-8")
        ).hexdigest()[:20]
        return {
            "schema": "dreamco.prototype_build_plan.v1",
            "prototype_id": f"prototype-{fingerprint}",
            "status": "ready_for_local_build",
            "brief": asdict(brief),
            "build_loop": [
                "turn the prompt into acceptance criteria",
                "select the smallest licensed stack that fits",
                "scaffold a runnable vertical slice",
                "start a live preview",
                "run unit, integration, accessibility, and security checks",
                "show evidence and accept natural-language revisions",
                "checkpoint and package the prototype",
            ],
            "outputs": [
                "source code", "test suite", "local preview", "rights manifest",
                "deployment manifest", "rollback checkpoint", "owner handoff",
            ],
            "network_default": "off",
            "external_spend_allowed": False,
        }

    def app_release_plan(self, brief: AppReleaseBrief) -> dict[str, Any]:
        brief.validate()
        targets = []
        for target in dict.fromkeys(brief.targets):
            requirement = STORE_REQUIREMENTS[target]
            targets.append({"target": target.value, **requirement, "status": "evidence_required"})
        return {
            "schema": "dreamco.app_release_plan.v1",
            "release_id": f"release-{uuid.uuid4().hex[:16]}",
            "status": "council_review_required",
            "app": {
                "name": brief.app_name,
                "package_id": brief.package_id,
                "version": brief.version,
                "handles_personal_data": brief.handles_personal_data,
                "targets_children": brief.targets_children,
            },
            "targets": targets,
            "shared_evidence": list(ReleaseCouncil.REQUIRED),
            "privacy_policy_url": brief.privacy_policy_url,
            "support_url": brief.support_url,
            "owner_account_required": True,
            "store_review_required": any(target not in {StoreTarget.WEB, StoreTarget.PWA} for target in brief.targets),
            "automatic_submission": False,
        }
