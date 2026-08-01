"""Governed film, synthetic-performer, and visual-simulation planning for Buddy."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .studio import ConsentEvidence, CreativeStudioError


ROOT = Path(__file__).resolve().parents[2]


class ActorMode(str, Enum):
    ORIGINAL_SYNTHETIC = "original_synthetic"
    COMPANY_MASCOT = "company_mascot"
    OWNER_DIGITAL_DOUBLE = "owner_digital_double"
    LICENSED_ADULT_PERFORMER = "licensed_adult_performer"


class ProductionFormat(str, Enum):
    FEATURE_FILM = "feature_film"
    DOCUMENTARY = "documentary"
    ANIMATED_SERIES = "animated_series"
    MUSIC_VIDEO = "music_video"
    COMMERCIAL = "commercial"
    FAMILY_LEARNING = "family_learning"
    SOCIAL_LIVE_SHOW = "social_live_show"


class SimulationDomain(str, Enum):
    VEHICLE_SERVICE = "vehicle_service"
    VEHICLE_CUSTOMIZATION = "vehicle_customization"
    BUILDING_DESIGN = "building_design"
    CONSTRUCTION_PRACTICE = "construction_practice"
    PRODUCT_INVENTION = "product_invention"
    EQUIPMENT_TRAINING = "equipment_training"
    SCIENCE_LEARNING = "science_learning"
    BUSINESS_OPERATIONS = "business_operations"
    CUSTOM = "custom"


class ModelSource(str, Enum):
    PROCEDURAL_ORIGINAL = "procedural_original"
    OWNER_UPLOAD = "owner_upload"
    LICENSED_CATALOG = "licensed_catalog"
    MEASURED_SCAN = "measured_scan"


@dataclass(frozen=True)
class SyntheticActorBrief:
    name: str
    project_title: str
    character_description: str
    mode: ActorMode = ActorMode.ORIGINAL_SYNTHETIC
    use_voice: bool = False
    use_likeness: bool = False
    source_media_ref: str = ""
    performer_release_ref: str = ""
    adult_confirmed: bool = False
    real_person_reference: bool = False
    deceptive_authority_impersonation: bool = False
    consent: ConsentEvidence | None = None

    def validate(self) -> None:
        if len(self.name.strip()) < 2 or len(self.project_title.strip()) < 3:
            raise CreativeStudioError("An actor name and project title are required.")
        if len(self.character_description.strip()) < 20:
            raise CreativeStudioError("Describe an original character and intended performance.")
        if self.deceptive_authority_impersonation:
            raise CreativeStudioError("Deceptive authority impersonation is blocked.")
        if self.mode in {ActorMode.ORIGINAL_SYNTHETIC, ActorMode.COMPANY_MASCOT}:
            if self.real_person_reference or self.source_media_ref or self.performer_release_ref:
                raise CreativeStudioError(
                    "Original synthetic actors and company mascots cannot be based on a real person's media or identity."
                )
            return
        if not self.adult_confirmed:
            raise CreativeStudioError("Synthetic performer workflows require an adult subject.")
        if not self.source_media_ref:
            raise CreativeStudioError("An owner-controlled performer media reference is required.")
        if self.mode == ActorMode.OWNER_DIGITAL_DOUBLE:
            if self.consent is None:
                raise CreativeStudioError("Active owner consent is required for a digital double.")
            self.consent.validate(needs_voice=self.use_voice, needs_likeness=self.use_likeness)
            if not self.use_voice and not self.use_likeness:
                raise CreativeStudioError("Choose voice, likeness, or both for an owner digital double.")
            return
        if not self.performer_release_ref:
            raise CreativeStudioError("A verified written performer-release reference is required.")


@dataclass(frozen=True)
class ProductionBrief:
    title: str
    objective: str
    audience: str
    production_format: ProductionFormat
    cast: tuple[SyntheticActorBrief, ...] = ()
    duration_minutes: int = 3
    aspect_ratio: str = "16:9"
    target_platforms: tuple[str, ...] = ("web",)
    selected_workspaces: tuple[str, ...] = (
        "story",
        "timeline",
        "image",
        "dialogue",
        "music",
        "sound",
        "accessibility",
        "delivery",
    )
    commercial_use: bool = False
    live_mode: bool = False

    def validate(self, production: dict[str, Any]) -> None:
        if len(self.title.strip()) < 3 or len(self.objective.strip()) < 15:
            raise CreativeStudioError("A title and detailed production objective are required.")
        if not self.audience.strip():
            raise CreativeStudioError("A production audience is required.")
        if self.duration_minutes < 1 or self.duration_minutes > 600:
            raise CreativeStudioError("Production duration must be between 1 and 600 minutes per master.")
        if self.aspect_ratio not in {"16:9", "9:16", "1:1", "4:3", "2.39:1"}:
            raise CreativeStudioError("Choose a supported master aspect ratio.")
        platforms = tuple(dict.fromkeys(item.strip().lower() for item in self.target_platforms if item.strip()))
        if not platforms or len(platforms) > 20:
            raise CreativeStudioError("Choose between one and 20 target platforms.")
        workspace_ids = {item["id"] for item in production["editing_workspaces"]}
        if not self.selected_workspaces or set(self.selected_workspaces) - workspace_ids:
            raise CreativeStudioError("Every selected editing workspace must exist in the production catalog.")
        names = [actor.name.strip().casefold() for actor in self.cast]
        if len(names) != len(set(names)):
            raise CreativeStudioError("Each cast member needs a unique production name.")
        if len(self.cast) > 100:
            raise CreativeStudioError("Split casts larger than 100 roles into production units.")
        for actor in self.cast:
            actor.validate()
        if self.live_mode and self.production_format != ProductionFormat.SOCIAL_LIVE_SHOW:
            raise CreativeStudioError("Live mode is available only for a social live show plan.")


@dataclass(frozen=True)
class SimulationBrief:
    title: str
    objective: str
    audience: str
    domain: SimulationDomain
    model_source: ModelSource = ModelSource.PROCEDURAL_ORIGINAL
    model_ref: str = ""
    rights_ref: str = ""
    modifications: tuple[str, ...] = ()
    fidelity: str = "concept"
    target_platform: str = "web"
    convert_to_game: bool = True

    def validate(self) -> None:
        if len(self.title.strip()) < 3 or len(self.objective.strip()) < 15:
            raise CreativeStudioError("A title and detailed simulation objective are required.")
        if not self.audience.strip():
            raise CreativeStudioError("A simulation audience is required.")
        if self.fidelity not in {"concept", "training", "engineering_review"}:
            raise CreativeStudioError("Fidelity must be concept, training, or engineering_review.")
        if self.model_source != ModelSource.PROCEDURAL_ORIGINAL:
            if not self.model_ref or not self.rights_ref:
                raise CreativeStudioError(
                    "Imported or scanned models require both an asset reference and an ownership or license reference."
                )
        if len(self.modifications) > 50 or any(len(item.strip()) < 2 for item in self.modifications):
            raise CreativeStudioError("Use between zero and 50 clearly named modifications.")


class BuddyProductionGroup:
    """Build auditable production and simulation plans without claiming a render exists."""

    def __init__(self) -> None:
        self.production = self._load("config/buddy-hollywood-production-group.json")
        self.foundry = self._load("config/buddy-simulation-foundry.json")

    @staticmethod
    def _load(relative_path: str) -> dict[str, Any]:
        return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))

    def build_actor_plan(self, brief: SyntheticActorBrief) -> dict[str, Any]:
        brief.validate()
        source_fingerprint = self._fingerprint(brief.source_media_ref)
        release_fingerprint = self._fingerprint(brief.performer_release_ref)
        consent_fingerprint = brief.consent.audit_fingerprint() if brief.consent else None
        return {
            "schema": "dreamco.buddy_synthetic_actor_plan.v1",
            "status": "character_plan_ready",
            "actor": {
                "name": brief.name,
                "project_title": brief.project_title,
                "character_description": brief.character_description,
                "mode": brief.mode.value,
                "voice_requested": brief.use_voice,
                "likeness_requested": brief.use_likeness,
                "real_person_reference": brief.real_person_reference,
            },
            "evidence": {
                "source_media_fingerprint": source_fingerprint,
                "performer_release_fingerprint": release_fingerprint,
                "owner_consent_fingerprint": consent_fingerprint,
                "raw_media_stored": False,
            },
            "performance_pipeline": [
                "character and originality review",
                "performance and emotional-beat brief",
                "voice, face, body, wardrobe, and movement design",
                "storyboard and animatic",
                "test performance",
                "facial motion and lip-sync review",
                "continuity and artifact review",
                "owner or performer approval",
                "labeled master and provenance record",
            ],
            "quality_gates": self.production["quality_gates"],
            "render_state": "renderer_configuration_required",
            "hard_blocks": self.production["actor_hard_blocks"],
            "publish_requires_owner_approval": True,
        }

    def build_production_plan(self, brief: ProductionBrief) -> dict[str, Any]:
        brief.validate(self.production)
        format_profile = next(
            item for item in self.production["production_formats"]
            if item["id"] == brief.production_format.value
        )
        workspace_ids = set(brief.selected_workspaces)
        workspaces = [
            item for item in self.production["editing_workspaces"]
            if item["id"] in workspace_ids
        ]
        cast = [self.build_actor_plan(actor) for actor in brief.cast]
        live_plan = None
        if brief.production_format == ProductionFormat.SOCIAL_LIVE_SHOW:
            live_plan = {
                "requested": brief.live_mode,
                "status": "private_rehearsal_ready_live_adapter_required",
                "controls": self.production["live_social_controls"],
                "go_live_requires_fresh_owner_approval": True,
                "autonomous_broadcast_started": False,
                "credentials_stored": False,
            }
        return {
            "schema": "dreamco.buddy_professional_production_plan.v1",
            "status": "production_packet_ready",
            "production": {
                "title": brief.title,
                "objective": brief.objective,
                "audience": brief.audience,
                "format": brief.production_format.value,
                "duration_minutes": brief.duration_minutes,
                "aspect_ratio": brief.aspect_ratio,
                "target_platforms": list(dict.fromkeys(brief.target_platforms)),
                "commercial_use_requested": brief.commercial_use,
            },
            "planning_units": format_profile["planning_units"],
            "required_deliverables": format_profile["required_deliverables"],
            "departments": self.production["departments"],
            "cast": cast,
            "editing_workspaces": workspaces,
            "timeline": {
                "interchange_contract": "OpenTimelineIO-compatible timeline manifest",
                "tracks": ["picture", "dialogue", "music", "effects", "captions", "metadata"],
                "media_embedded": False,
                "rendered_timeline_created": False,
            },
            "toolchain": [
                {
                    **tool,
                    "installed": False,
                    "execution_taken": False,
                    "license_review_required": True,
                }
                for tool in self.production["professional_toolchain"]
            ],
            "live": live_plan,
            "quality_gates": self.production["quality_gates"],
            "delivery_profiles": self.production["delivery_profiles"],
            "release": {
                "rendered_assets_exist": False,
                "master_quality_control_passed": False,
                "rights_review_passed": False,
                "platform_submission_or_publish_taken": False,
                "owner_approval_required": True,
            },
            "truth_boundary": self.production["quality_claim"],
        }

    def build_simulation_plan(self, brief: SimulationBrief) -> dict[str, Any]:
        brief.validate()
        domain = next(item for item in self.foundry["domains"] if item["id"] == brief.domain.value)
        game_conversion = None
        if brief.convert_to_game:
            game_conversion = {
                "status": "game_design_ready",
                "stages": self.foundry["simulation_to_game"]["stages"],
                "required_evidence": self.foundry["simulation_to_game"]["required_evidence"],
                "safe_failure": True,
                "restart_and_recovery": True,
                "owner_or_instructor_controls": True,
            }
        return {
            "schema": "dreamco.buddy_simulation_plan.v1",
            "status": "simulation_packet_ready",
            "brief": {
                **asdict(brief),
                "domain": brief.domain.value,
                "model_source": brief.model_source.value,
                "model_ref": "redacted" if brief.model_ref else "",
                "rights_ref": "redacted" if brief.rights_ref else "",
            },
            "model_ingestion": {
                "source": brief.model_source.value,
                "asset_fingerprint": self._fingerprint(brief.model_ref),
                "rights_fingerprint": self._fingerprint(brief.rights_ref),
                "supported_formats": self.foundry["supported_model_formats"],
                "checks": [
                    "file and malware scan",
                    "license and provenance",
                    "units, scale, axes, and origin",
                    "geometry, normals, materials, rigs, and animation",
                    "level-of-detail and performance budget",
                ],
            },
            "variant_workbench": {
                "controls": self.foundry["variant_controls"],
                "requested_modifications": list(brief.modifications),
                "before_after_comparison": True,
                "render_state": "renderer_configuration_required",
            },
            "simulation_loop": [
                "define measurable starting state",
                "choose a legal action or modification",
                "apply the bounded model",
                "show visual and measured consequences",
                "explain assumptions and uncertainty",
                "score the objective",
                "reset, compare, and export evidence",
            ],
            "domain_review": domain["review"],
            "routes": [
                {"bot": "3d-asset-mgr", "role": "model ingestion, materials, variants, and provenance"},
                {"bot": "immersive-xr", "role": "interactive scene, spatial controls, and device checks"},
                {"bot": "mfg-analytics-elite", "role": "digital-twin assumptions, measurements, and scenario evidence"},
                {"bot": "safety-mfg", "role": "failure modes, physical safety, and qualified-review gates"},
                *(
                    [
                        {"bot": "games-app-bot", "role": "practice loop, levels, feedback, and packaging"},
                        {"bot": "game-ai-player", "role": "deterministic bot playtesting"},
                    ]
                    if brief.convert_to_game
                    else []
                ),
            ],
            "game_conversion": game_conversion,
            "sandbox": {
                "network_default": "off",
                "deterministic_seed": 42,
                "no_live_machine_or_account_control": True,
                "checks": [
                    "load and reset",
                    "legal actions only",
                    "source assumptions visible",
                    "known limits visible",
                    "accessibility and input coverage",
                    "qualified review gate for safety-critical use",
                ],
            },
            "truth_boundary": self.foundry["truth_boundary"],
            "publish_requires_owner_approval": True,
        }

    @staticmethod
    def _fingerprint(reference: str) -> str | None:
        if not reference:
            return None
        return hashlib.sha256(reference.encode("utf-8")).hexdigest()
