"""Governed multi-device packaging and publishing service contracts."""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from typing import Any


class DistributionError(ValueError):
    """Raised when a distribution request is incomplete or unsupported."""


@dataclass(frozen=True)
class DistributionTarget:
    target_id: str
    name: str
    family: str
    install_mode: str
    artifact: str
    account_requirement: str
    release_gate: str
    public_status: str


TARGETS = (
    DistributionTarget("web_browser", "Any modern web browser", "web", "open_url", "HTTPS web build", "hosting account", "deployment checks", "available_now"),
    DistributionTarget("pwa", "Installable web app", "web", "browser_install_prompt", "manifest, service worker, icons, and HTTPS build", "hosting account", "installability checks", "available_now_supported_browser"),
    DistributionTarget("ios_ipados", "iPhone and iPad", "mobile_tablet", "apple_app_store", "signed iOS/iPadOS archive", "Apple Developer and App Store Connect accounts", "Apple review", "package_and_review_required"),
    DistributionTarget("android", "Android phones and tablets", "mobile_tablet", "google_play", "signed Android App Bundle", "verified Play Console account", "Google Play review", "package_and_review_required"),
    DistributionTarget("android_direct", "Direct Android download", "mobile_tablet", "owner_hosted_download", "signed Android APK", "owner-controlled HTTPS hosting", "signature and sideload safety review", "package_build_required"),
    DistributionTarget("fire_tablet", "Amazon Fire tablets", "mobile_tablet", "amazon_appstore", "signed Android-compatible package", "Amazon Developer account", "Amazon Appstore review", "package_and_review_required"),
    DistributionTarget("windows", "Windows", "desktop", "microsoft_store_or_signed_download", "signed MSIX or desktop installer", "Microsoft Partner Center or signing identity", "package certification", "package_and_review_required"),
    DistributionTarget("macos", "macOS", "desktop", "mac_app_store_or_notarized_download", "signed and notarized macOS app", "Apple Developer account", "notarization or App Store review", "package_and_review_required"),
    DistributionTarget("linux", "Linux", "desktop", "repository_or_direct_download", "AppImage, Flatpak, Snap, deb, or rpm", "owner distribution account as applicable", "package and dependency tests", "package_build_required"),
    DistributionTarget("chromeos", "ChromeOS", "desktop", "pwa_or_google_play", "PWA or compatible Android bundle", "hosting or Play Console account", "installability or Play review", "package_route_selection_required"),
    DistributionTarget("apple_tv", "Apple TV", "tv", "apple_app_store", "signed tvOS archive", "Apple Developer and App Store Connect accounts", "Apple tvOS review", "package_and_review_required"),
    DistributionTarget("android_tv", "Android TV", "tv", "google_play", "TV-compatible Android App Bundle", "verified Play Console account", "TV quality and Play review", "package_and_review_required"),
    DistributionTarget("google_tv", "Google TV", "tv", "google_play", "TV-compatible Android App Bundle", "verified Play Console account", "TV quality and Play review", "package_and_review_required"),
    DistributionTarget("fire_tv", "Amazon Fire TV", "tv", "amazon_appstore", "Fire TV-compatible Android package", "Amazon Developer account", "Amazon Fire TV review", "package_and_review_required"),
    DistributionTarget("samsung_tv", "Samsung Smart TV", "tv", "samsung_tv_store", "signed Tizen widget package", "Samsung Seller Office account", "Samsung TV certification", "package_and_review_required"),
    DistributionTarget("lg_tv", "LG Smart TV", "tv", "lg_content_store", "signed webOS package", "LG Seller Lounge account", "LG content review", "package_and_review_required"),
    DistributionTarget("roku", "Roku", "tv", "roku_channel_store", "Roku channel package", "Roku Developer account", "Roku certification", "package_and_review_required"),
    DistributionTarget("steam", "Steam", "game", "steam_store", "tested depot builds", "Steamworks partner account", "Steam store and build review", "package_and_review_required"),
    DistributionTarget("epic", "Epic Games Store", "game", "epic_games_store", "tested game builds", "Epic publisher account", "Epic product review", "package_and_review_required"),
    DistributionTarget("xbox", "Xbox", "game", "microsoft_store", "approved Xbox package", "authorized Microsoft game-publishing account", "Xbox certification", "publisher_program_required"),
    DistributionTarget("playstation", "PlayStation", "game", "playstation_store", "approved PlayStation package", "authorized PlayStation partner account", "PlayStation certification", "publisher_program_required"),
    DistributionTarget("nintendo", "Nintendo", "game", "nintendo_eshop", "approved Nintendo package", "authorized Nintendo developer account", "Nintendo certification", "publisher_program_required"),
    DistributionTarget("itch", "itch.io", "game", "itch_store", "HTML5 or downloadable game bundle", "itch.io creator account", "rights and package review", "package_build_required"),
    DistributionTarget("meta_quest", "Meta Quest", "vr_xr", "meta_horizon_store", "signed Quest Android bundle", "Meta developer account", "Meta store review", "package_and_review_required"),
    DistributionTarget("lms", "School and college LMS", "education", "lms_import_or_lti", "SCORM, xAPI, Common Cartridge, or LTI package", "institution-authorized LMS account", "accessibility and institutional review", "package_and_review_required"),
    DistributionTarget("smart_display", "Kiosks and smart displays", "embedded_display", "managed_web_or_device_package", "kiosk web build or device-specific package", "owner-managed device fleet", "device and security validation", "package_build_required"),
)

TARGET_BY_ID = {target.target_id: target for target in TARGETS}


SERVICE_PACKAGES: tuple[dict[str, Any], ...] = (
    {
        "service_id": "website_pwa_launch",
        "name": "Website and PWA Go-Live",
        "project_types": ["website", "web_app", "creative_tool", "bot_system"],
        "target_families": ["web"],
        "deliverables": ["production build", "HTTPS deployment", "installable PWA", "offline fallback", "analytics-ready handoff", "rollback plan"],
        "commercial_model": "scoped_quote_after_free_assessment",
    },
    {
        "service_id": "mobile_tablet_release",
        "name": "Phone and Tablet Store Release",
        "project_types": ["mobile_app", "web_app", "game", "course"],
        "target_families": ["mobile_tablet"],
        "deliverables": ["signed build plan", "store metadata", "privacy declarations", "screenshots", "test-track packet", "owner submission session"],
        "commercial_model": "scoped_quote_per_platform",
    },
    {
        "service_id": "game_store_release",
        "name": "Game Store Publishing",
        "project_types": ["game", "simulation"],
        "target_families": ["game", "vr_xr"],
        "deliverables": ["store-ready build matrix", "controller and performance tests", "ratings checklist", "store assets", "depot or package plan", "certification evidence"],
        "commercial_model": "scoped_quote_per_store_family",
    },
    {
        "service_id": "tv_living_room_release",
        "name": "TV and Living-Room Distribution",
        "project_types": ["web_app", "game", "simulation", "course", "creative_tool"],
        "target_families": ["tv", "embedded_display"],
        "deliverables": ["remote-control UX review", "ten-foot accessibility", "TV package matrix", "device testing plan", "store metadata", "certification handoff"],
        "commercial_model": "scoped_quote_per_tv_family",
    },
    {
        "service_id": "course_lms_delivery",
        "name": "Course and LMS Delivery",
        "project_types": ["course", "simulation", "game"],
        "target_families": ["education", "web"],
        "deliverables": ["SCORM or xAPI package plan", "LTI integration plan", "accessibility evidence", "assessment validation", "teacher guide", "LMS import handoff"],
        "commercial_model": "scoped_quote_per_learning_environment",
    },
    {
        "service_id": "desktop_distribution",
        "name": "Desktop Packaging and Distribution",
        "project_types": ["desktop_app", "web_app", "game", "simulation", "creative_tool", "bot_system"],
        "target_families": ["desktop"],
        "deliverables": ["platform build matrix", "code-signing plan", "installer packages", "update channel", "security checks", "download or store handoff"],
        "commercial_model": "scoped_quote_per_operating_system",
    },
    {
        "service_id": "multi_platform_launch",
        "name": "Multi-Platform Launch Management",
        "project_types": ["website", "web_app", "mobile_app", "desktop_app", "game", "simulation", "course", "creative_tool", "bot_system"],
        "target_families": ["web", "mobile_tablet", "desktop", "tv", "game", "vr_xr", "education", "embedded_display"],
        "deliverables": ["release architecture", "shared evidence vault", "target-specific packages", "submission calendar", "approval ledger", "launch and rollback coordination"],
        "commercial_model": "custom_scoped_quote",
    },
)


@dataclass(frozen=True)
class DistributionBrief:
    owner_user_id: str
    project_name: str
    product_type: str
    target_ids: tuple[str, ...]
    audience: str
    source_reference: str
    rights_confirmed: bool
    targets_children: bool = False

    def validate(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{2,80}", self.owner_user_id):
            raise DistributionError("A stable owner id is required.")
        if len(self.project_name.strip()) < 3 or not self.audience.strip():
            raise DistributionError("Project name and audience are required.")
        allowed_types = {item for package in SERVICE_PACKAGES for item in package["project_types"]}
        if self.product_type not in allowed_types:
            raise DistributionError("Unsupported product type.")
        if not self.target_ids or len(set(self.target_ids)) != len(self.target_ids):
            raise DistributionError("Select one or more unique distribution targets.")
        unknown = sorted(set(self.target_ids) - TARGET_BY_ID.keys())
        if unknown:
            raise DistributionError(f"Unknown distribution targets: {', '.join(unknown)}")
        if not self.source_reference.strip():
            raise DistributionError("A source or build reference is required.")
        if not self.rights_confirmed:
            raise DistributionError("Distribution rights must be confirmed before packaging.")


class BuddyDistributionService:
    """Prepare install and release packets without impersonating a store publisher."""

    @staticmethod
    def catalog() -> dict[str, Any]:
        return {
            "schema": "dreamco.distribution_catalog.v1",
            "truth_policy": {
                "universal_access": "The HTTPS web app works on compatible browsers; no single native binary runs on every device.",
                "install_now": "Only the website and supported-browser PWA paths are immediately available.",
                "native_release": "Native device and store releases require target packages, owner accounts, provider terms, review, and fees where applicable.",
                "commercial_service": "A service listing is an offer to scope work, not evidence of checkout, store acceptance, or completed delivery.",
            },
            "targets": [asdict(target) for target in TARGETS],
            "service_packages": list(SERVICE_PACKAGES),
            "summary": {
                "targets": len(TARGETS),
                "families": len({target.family for target in TARGETS}),
                "services": len(SERVICE_PACKAGES),
                "available_now": sum(target.public_status.startswith("available_now") for target in TARGETS),
            },
        }

    def build_plan(self, brief: DistributionBrief) -> dict[str, Any]:
        brief.validate()
        digest = hashlib.sha256(
            f"{brief.owner_user_id}:{brief.project_name}:{':'.join(brief.target_ids)}".encode("utf-8")
        ).hexdigest()[:20]
        targets = [asdict(TARGET_BY_ID[target_id]) for target_id in brief.target_ids]
        matched_services = [
            package["service_id"]
            for package in SERVICE_PACKAGES
            if brief.product_type in package["project_types"]
            and any(target["family"] in package["target_families"] for target in targets)
        ]
        return {
            "schema": "dreamco.distribution_plan.v1",
            "plan_id": f"distribution-{digest}",
            "status": "release_evidence_plan_ready",
            "brief": asdict(brief),
            "targets": targets,
            "matched_services": matched_services,
            "shared_gates": ["build", "tests", "security", "privacy", "accessibility", "rights", "rollback"],
            "children_review_required": brief.targets_children,
            "owner_account_required": any(target["install_mode"] not in {"open_url", "browser_install_prompt"} for target in targets),
            "provider_review_required": any("review" in target["release_gate"] or "certification" in target["release_gate"] for target in targets),
            "automatic_store_submission": False,
            "automatic_payment": False,
            "quote_generated": False,
            "next_step": "Buddy prepares a scoped assessment, evidence checklist, and owner-approved quote before paid work begins.",
        }
