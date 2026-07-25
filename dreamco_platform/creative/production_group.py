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
    OWNER_DIGITAL_DOUBLE = "owner_digital_double"
    LICENSED_ADULT_PERFORMER = "licensed_adult_performer"


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
        if self.mode == ActorMode.ORIGINAL_SYNTHETIC:
            if self.real_person_reference or self.source_media_ref or self.performer_release_ref:
                raise CreativeStudioError(
                    "Original synthetic actors cannot be based on a real person's media or identity."
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
