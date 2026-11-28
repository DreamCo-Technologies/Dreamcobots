"""Build auditable production packets; planning is not rendering."""
from __future__ import annotations
import hashlib
import json
from typing import Any
from .rights_gate import authorize_asset, authorize_model, require_allowed
from .shot_planner import plan_shots
from .timeline import build_timeline

def build_production_packet(brief: dict[str, Any], storyboard: list[dict[str, Any]], *,
                            assets: list[dict[str, Any]] | None = None,
                            models: list[dict[str, Any]] | None = None,
                            commercial: bool = False) -> dict[str, Any]:
    title = str(brief.get("title") or "").strip()
    objective = str(brief.get("objective") or "").strip()
    if len(title) < 3 or len(objective) < 12:
        raise ValueError("A production title and clear objective are required.")
    asset_records = {str(row.get("asset_id")): row for row in (assets or [])}
    model_records = {str(row.get("model_id")): row for row in (models or [])}
    referenced_assets = sorted({str(asset_id) for shot in storyboard for asset_id in shot.get("asset_ids", [])})
    decisions = []
    for asset_id in referenced_assets:
        record = asset_records.get(asset_id)
        if record is None:
            raise PermissionError(f"Rights record missing for asset {asset_id}")
        use = "commercial_use" if commercial else "display"
        decision = authorize_asset(record, use, commercial=commercial)
        require_allowed(decision)
        decisions.append({"asset_id": decision.asset_id, "use": decision.use, "allowed": decision.allowed,
                          "attribution_required": decision.attribution_required,
                          "share_alike_required": decision.share_alike_required})
    model_decisions = []
    for model_id in brief.get("model_ids", []):
        model = model_records.get(str(model_id))
        if model is None:
            raise PermissionError(f"Model registry record missing for {model_id}")
        decision = authorize_model(model, commercial=commercial)
        require_allowed(decision)
        model_decisions.append({"model_id": model_id, "allowed": True})
    shot_plan = plan_shots(storyboard)
    timeline = build_timeline(shot_plan)
    packet = {"schema": "dreamco.media.production_packet.v1", "title": title, "objective": objective,
              "audience": str(brief.get("audience") or "unspecified"),
              "format": str(brief.get("format") or "video"), "commercial_use": commercial,
              "status": "planned_not_rendered", "rights_decisions": decisions,
              "model_decisions": model_decisions, "shot_plan": shot_plan, "timeline": timeline,
              "deliverables": ["storyboard", "shot_plan", "timeline", "rights_manifest", "render_manifest"],
              "rendered_assets": [], "training_started": False}
    packet["packet_sha256"] = hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return packet
