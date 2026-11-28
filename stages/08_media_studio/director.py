"""DreamCo Media Director: deterministic shot planning and rights-gated render orchestration.

No model, GPU, network, or API dependency is required. The control plane validates and
plans jobs on CPU runners; provider adapters are injected by workers at execution time.
"""
from __future__ import annotations
import hashlib, json, math, re, uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

class MediaPlanError(ValueError):
    """The production request or shot list is invalid."""

class MediaRightsError(PermissionError):
    """An asset is not cleared for the requested media operation."""

class RenderAdapter(Protocol):
    def render_shot(self, shot: Mapping[str, Any], context: Mapping[str, Any]) -> Mapping[str, Any]: ...

ALLOWED_MEDIA_TYPES = {"youtube", "film", "music_video", "advertisement", "podcast"}
REQUIRED_SHOT_FIELDS = ("shot_id", "duration_sec", "visual_prompt")
OPTIONAL_SHOT_FIELDS = {
    "camera_motion", "dialogue_line", "music_cue", "sfx_cue", "character_ids",
    "image_prompt", "video_backend", "voice_backend", "music_backend", "notes",
}

@dataclass(frozen=True)
class Shot:
    shot_id: str
    duration_sec: float
    visual_prompt: str
    camera_motion: str = "static"
    dialogue_line: str = ""
    music_cue: str = ""
    sfx_cue: str = ""
    character_ids: tuple[str, ...] = ()
    image_prompt: str = ""
    video_backend: str = ""
    voice_backend: str = ""
    music_backend: str = ""
    notes: str = ""

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Shot":
        if not isinstance(value, Mapping):
            raise MediaPlanError("Each shot must be an object")
        unknown = set(value) - set(REQUIRED_SHOT_FIELDS) - OPTIONAL_SHOT_FIELDS
        if unknown:
            raise MediaPlanError(f"Unknown shot fields: {', '.join(sorted(unknown))}")
        missing = [name for name in REQUIRED_SHOT_FIELDS if name not in value]
        if missing:
            raise MediaPlanError(f"Missing shot fields: {', '.join(missing)}")
        duration = value["duration_sec"]
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise MediaPlanError("duration_sec must be a number")
        if not math.isfinite(float(duration)) or duration <= 0 or duration > 1800:
            raise MediaPlanError("duration_sec must be finite, greater than 0 and at most 1800")
        for name in ("shot_id", "visual_prompt"):
            if not isinstance(value[name], str) or not value[name].strip():
                raise MediaPlanError(f"{name} must be a non-empty string")
        for name in OPTIONAL_SHOT_FIELDS - {"character_ids"}:
            if name in value and not isinstance(value[name], str):
                raise MediaPlanError(f"{name} must be a string")
        ids = value.get("character_ids", ())
        if not isinstance(ids, (list, tuple)) or any(not isinstance(x, str) or not x for x in ids):
            raise MediaPlanError("character_ids must be a list of non-empty strings")
        normalized = dict(value)
        normalized["duration_sec"] = float(duration)
        normalized["character_ids"] = tuple(ids)
        return cls(**normalized)

@dataclass(frozen=True)
class ProductionPlan:
    job_id: str
    media_type: str
    title: str
    shots: tuple[Shot, ...]
    total_duration_sec: float
    requested_outputs: tuple[str, ...] = ("mp4",)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id, "media_type": self.media_type, "title": self.title,
            "shots": [asdict(shot) for shot in self.shots],
            "total_duration_sec": self.total_duration_sec,
            "requested_outputs": list(self.requested_outputs), "metadata": dict(self.metadata),
            "status": "planned_not_rendered",
        }

def validate_shot_list(shots: Sequence[Mapping[str, Any]]) -> tuple[Shot, ...]:
    if not isinstance(shots, (list, tuple)) or not shots:
        raise MediaPlanError("A production must contain at least one shot")
    if any(not isinstance(item, Mapping) for item in shots):
        raise MediaPlanError("Every shot must be an object")
    parsed = tuple(Shot.from_mapping(item) for item in shots)
    ids = [shot.shot_id for shot in parsed]
    if len(ids) != len(set(ids)):
        raise MediaPlanError("shot_id values must be unique")
    return parsed

def build_production_plan(request: Mapping[str, Any], *, job_id: str | None = None) -> ProductionPlan:
    """Validate a request and produce a serializable render plan."""
    if not isinstance(request, Mapping):
        raise MediaPlanError("request must be an object")
    media_type = str(request.get("media_type", "youtube")).strip().lower()
    if media_type not in ALLOWED_MEDIA_TYPES:
        raise MediaPlanError(f"media_type must be one of: {', '.join(sorted(ALLOWED_MEDIA_TYPES))}")
    title = request.get("title")
    if not isinstance(title, str) or not title.strip():
        raise MediaPlanError("title must be a non-empty string")
    shots = validate_shot_list(request.get("shots", []))
    outputs = request.get("requested_outputs", ["mp4"])
    if not isinstance(outputs, (list, tuple)) or not outputs or any(
        not isinstance(x, str) or not re.fullmatch(r"[a-z0-9]{2,8}", x.lower()) for x in outputs
    ):
        raise MediaPlanError("requested_outputs must be a non-empty list of simple file extensions")
    metadata = request.get("metadata", {})
    if not isinstance(metadata, Mapping):
        raise MediaPlanError("metadata must be an object")
    return ProductionPlan(
        job_id=job_id or uuid.uuid4().hex, media_type=media_type, title=title.strip(),
        shots=shots, total_duration_sec=round(sum(s.duration_sec for s in shots), 3),
        requested_outputs=tuple(x.lower() for x in outputs), metadata=dict(metadata),
    )

def _rights_decision(asset: Mapping[str, Any]) -> Mapping[str, Any]:
    """Use the repository's canonical sellability gate; fail closed if unavailable."""
    try:
        from buddy.media.sellability_gate import decide
    except Exception as exc:
        raise MediaRightsError(f"Canonical media rights gate unavailable: {exc}") from exc
    result = decide(asset)
    if result.get("decision") not in {"sellable", "train_only", "reference_only"}:
        raise MediaRightsError(f"Asset {asset.get('asset_id', '<unknown>')} blocked: {result.get('reasons')}")
    return result

def authorize_render_assets(assets: Sequence[Mapping[str, Any]], *, purpose: str = "commercial_render") -> list[dict[str, Any]]:
    """Check every supplied asset before rendering; empty manifests are denied."""
    if not isinstance(assets, (list, tuple)) or not assets:
        raise MediaRightsError("Rendering requires an explicit, non-empty rights manifest")
    authorized = []
    for asset in assets:
        if not isinstance(asset, Mapping):
            raise MediaRightsError("Every rights manifest entry must be an object")
        result = dict(_rights_decision(asset))
        decision = result["decision"]
        subject_type = asset.get("subject_type")
        if subject_type not in {"synthetic", "no_person", "real_person"}:
            raise MediaRightsError(
                f"Asset {asset.get('asset_id', '<unknown>')} requires an explicit subject_type "
                "(synthetic, no_person, or real_person)"
            )
        if asset.get("commercial_redistribution_allowed") is not True:
            raise MediaRightsError(
                f"Asset {asset.get('asset_id', '<unknown>')} lacks explicit commercial redistribution permission"
            )
        if decision != "sellable":
            raise MediaRightsError(
                f"Asset {asset.get('asset_id', '<unknown>')} is {decision}; render inputs must be sellable"
            )
        if subject_type == "real_person":
            reference_path, registry_path = asset.get("reference_path"), asset.get("consent_registry_path")
            consent_purpose = asset.get("consent_purpose", purpose)
            if not reference_path or not registry_path:
                raise MediaRightsError("Real-person media requires reference_path and consent_registry_path")
            try:
                from buddy.media.consent import ConsentRegistry
                ConsentRegistry(registry_path).require(reference_path, str(asset.get("kind", "image")), consent_purpose)
            except Exception as exc:
                raise MediaRightsError(f"Real-person consent verification failed: {exc}") from exc
        authorized.append({"asset_id": asset.get("asset_id"), "decision": decision,
                           "purpose": purpose, "reasons": result.get("reasons", [])})
    return authorized

def authorize_model_checkpoints(
    model_records: Sequence[Mapping[str, Any]], evidence_root: str | Path
) -> list[dict[str, Any]]:
    """Require every model checkpoint and dependency to pass the commercial license gate."""
    if not isinstance(model_records, (list, tuple)) or not model_records:
        raise MediaRightsError("Rendering requires an explicit, non-empty model checkpoint manifest")
    try:
        from buddy.media.model_license_gate import verify_model_record
    except Exception as exc:
        raise MediaRightsError(f"Model license gate unavailable: {exc}") from exc
    results = []
    for record in model_records:
        if not isinstance(record, Mapping):
            raise MediaRightsError("Every model manifest entry must be an object")
        result = verify_model_record(record, evidence_root)
        if result.get("decision") != "approved":
            raise MediaRightsError(
                f"Model {record.get('model_id', '<unknown>')} blocked: {result.get('reasons')}"
            )
        results.append(result)
    return results


def render_production(plan: ProductionPlan, *, assets: Sequence[Mapping[str, Any]],
                      model_records: Sequence[Mapping[str, Any]], license_evidence_root: str | Path,
                      adapters: Mapping[str, RenderAdapter], context: Mapping[str, Any] | None = None,
                      purpose: str = "commercial_render") -> dict[str, Any]:
    """Render only after asset rights and exact model checkpoint licenses pass."""
    rights = authorize_render_assets(assets, purpose=purpose)
    models = authorize_model_checkpoints(model_records, license_evidence_root)
    outputs, context = [], dict(context or {})
    context.update({"job_id": plan.job_id, "media_type": plan.media_type, "title": plan.title})
    for shot in plan.shots:
        backend = str(shot.video_backend or context.get("default_backend", ""))
        if not backend or backend not in adapters:
            raise MediaPlanError(f"No registered render adapter for shot {shot.shot_id!r}")
        result = adapters[backend].render_shot(asdict(shot), context)
        if not isinstance(result, Mapping) or not result.get("asset_uri"):
            raise MediaPlanError(f"Adapter {backend!r} returned no asset_uri for shot {shot.shot_id!r}")
        outputs.append({"shot_id": shot.shot_id, "backend": backend, **dict(result)})
    digest = hashlib.sha256(json.dumps(plan.to_dict(), sort_keys=True, default=list).encode()).hexdigest()
    return {"job_id": plan.job_id, "status": "rendered", "rights": rights, "models": models, "shots": outputs, "plan_sha256": digest}

def write_plan(plan: ProductionPlan, destination: str | Path) -> Path:
    """Persist a plan atomically; it is not rendered media."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(plan.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(path)
    return path

def load_request(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MediaPlanError(f"Could not load production request: {exc}") from exc
    if not isinstance(value, dict):
        raise MediaPlanError("Production request JSON must contain an object")
    return value

def main(argv: Sequence[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", help="Path to a JSON production request")
    parser.add_argument("--output", default="media-plan.json", help="Output plan path")
    args = parser.parse_args(argv)
    plan = build_production_plan(load_request(args.request))
    write_plan(plan, args.output)
    print(json.dumps({"job_id": plan.job_id, "status": "planned_not_rendered", "output": args.output}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
