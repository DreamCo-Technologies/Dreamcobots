"""Fail-closed, deterministic assembly of independently authored study-guide drafts.

This module does not fetch or transcribe source media and does not generate text with an
LLM. Callers provide independently written lesson fields and factual notes. The existing
Stage 01 policy gate must authorize fact extraction for the exact catalog item first.
Commercial publication remains blocked pending explicit owner review and rights evidence.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
POLICY_GATE_PATH = ROOT / "stages" / "01_policy_gate" / "policy_gate.py"
REQUIRED = ("guide_id", "title", "learning_objectives", "lesson", "practice_lab", "assessment", "safety_notes")
HEX_64 = re.compile(r"^[a-f0-9]{64}$")
TOKEN_RE = re.compile(r"[a-z0-9_]+")


def _load_policy_gate():
    spec = importlib.util.spec_from_file_location("dreamco_stage01_policy_gate", POLICY_GATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Stage 01 policy gate could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def ngram_containment(candidate: str, reference: str, n: int = 8) -> float:
    """Fraction of candidate n-grams also present in a reference; screening heuristic only."""
    if n < 2:
        raise ValueError("n must be at least 2")
    c, r = _tokens(candidate), _tokens(reference)
    if len(c) < n or len(r) < n:
        return 0.0
    candidate_grams = {tuple(c[i:i+n]) for i in range(len(c) - n + 1)}
    reference_grams = {tuple(r[i:i+n]) for i in range(len(r) - n + 1)}
    return len(candidate_grams & reference_grams) / len(candidate_grams) if candidate_grams else 0.0


def validate_guide(guide: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(guide, dict):
        return ["guide_not_object"]
    allowed = set(REQUIRED) | {"division_id", "onet_task_codes", "owner_review_status"}
    for key in REQUIRED:
        if key not in guide:
            errors.append(f"missing:{key}")
    extra = set(guide) - allowed
    if extra:
        errors.extend(f"unexpected:{key}" for key in sorted(extra))
    for key in ("guide_id", "title", "lesson", "practice_lab", "assessment"):
        if key in guide and (not isinstance(guide[key], str) or not guide[key].strip()):
            errors.append(f"invalid:{key}")
    for key in ("learning_objectives", "safety_notes"):
        if key in guide and (
            not isinstance(guide[key], list)
            or not guide[key]
            or any(not isinstance(item, str) or not item.strip() for item in guide[key])
        ):
            errors.append(f"invalid:{key}")
    if "division_id" in guide and (
        not isinstance(guide["division_id"], int) or isinstance(guide["division_id"], bool)
        or not 1 <= guide["division_id"] <= 65
    ):
        errors.append("invalid:division_id")
    if "onet_task_codes" in guide and (
        not isinstance(guide["onet_task_codes"], list)
        or any(not isinstance(item, str) or not item.strip() for item in guide["onet_task_codes"])
    ):
        errors.append("invalid:onet_task_codes")
    if guide.get("owner_review_status", "draft") not in {"draft", "in_review", "approved", "rejected"}:
        errors.append("invalid:owner_review_status")
    return errors


def build_guide(
    *,
    source_record: dict[str, Any],
    policy_registry: dict[str, Any],
    authored_content: dict[str, Any],
    similarity_references: list[str],
    similarity_threshold: float = 0.04,
) -> dict[str, Any]:
    """Build a draft only after Stage 01 authorizes fact extraction for this catalog item."""
    if not isinstance(source_record, dict):
        raise TypeError("source_record must be an object")
    if source_record.get("schema") != "dreamco.source_catalog_record.v1":
        raise ValueError("unsupported or missing source catalog record schema")
    if not source_record.get("source_id") or not source_record.get("video_id"):
        raise ValueError("catalog record must include source_id and video_id")
    if not HEX_64.fullmatch(str(source_record.get("content_sha256", "")).lower()):
        raise ValueError("catalog record must include a valid SHA-256 content hash")
    if source_record.get("license_record_verified") is not True:
        raise PermissionError("BLOCKED_MISSING_ITEM_LICENSE_EVIDENCE")
    if not isinstance(similarity_references, list) or not similarity_references:
        raise PermissionError("BLOCKED_MISSING_ORIGINALITY_REFERENCE_SET")
    if any(not isinstance(ref, str) or len(_tokens(ref)) < 8 for ref in similarity_references):
        raise ValueError("every originality reference must contain at least eight tokens")
    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError("similarity_threshold must be between 0 and 1")

    decision = _load_policy_gate().evaluate_source(
        source_record, policy_registry, purpose="fact_extraction"
    )
    if not decision.get("allowed"):
        raise PermissionError(str(decision.get("reason", "BLOCKED_BY_STAGE01_POLICY")))

    guide = dict(authored_content)
    guide.setdefault("owner_review_status", "draft")
    errors = validate_guide(guide)
    if errors:
        raise ValueError("invalid study guide: " + ", ".join(errors))

    candidate_text = " ".join(
        [guide["title"], *guide["learning_objectives"], guide["lesson"],
         guide["practice_lab"], guide["assessment"], *guide["safety_notes"]]
    )
    scores = [ngram_containment(candidate_text, ref, n=8) for ref in similarity_references]
    max_score = max(scores, default=1.0)
    originality_passed = max_score < similarity_threshold
    source_fingerprint = str(source_record["content_sha256"]).lower()
    provenance = {
        "schema": "dreamco.guide_provenance.v1",
        "source_id": source_record["source_id"],
        "video_id": source_record["video_id"],
        "source_url": source_record.get("source_url"),
        "source_record_sha256": _canonical_digest(source_record),
        "source_content_sha256": source_fingerprint,
        "policy_decision": decision,
        "source_use": "fact_extraction_only",
        "transcript_downloaded": False,
        "media_downloaded": False,
    }
    quality = {
        "schema": "dreamco.guide_quality_report.v1",
        "schema_valid": True,
        "originality_passed": originality_passed,
        "similarity_method": "8gram_candidate_containment_heuristic",
        "similarity_threshold": similarity_threshold,
        "max_similarity": round(max_score, 8),
        "reference_count": len(similarity_references),
        "human_rights_review_required": True,
        "owner_review_required": True,
        "commercial_release_authorized": False,
        "warning": "An n-gram score is not proof of originality, non-infringement, or commercial rights.",
    }
    release_status = "draft_review_required" if originality_passed else "quarantined_similarity_review"
    return {
        "guide": guide,
        "provenance": provenance,
        "quality_report": quality,
        "release_status": release_status,
        "artifact_sha256": _canonical_digest({"guide": guide, "provenance": provenance, "quality_report": quality}),
    }


def write_guide_bundle(bundle: dict[str, Any], output_dir: Path) -> tuple[Path, Path, Path]:
    """Write three separate, deterministic JSON artifacts; never overwrite existing output."""
    if bundle.get("release_status") not in {"draft_review_required", "quarantined_similarity_review"}:
        raise ValueError("unsupported release status")
    output_dir.mkdir(parents=True, exist_ok=True)
    guide_id = str(bundle["guide"]["guide_id"])
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", guide_id):
        raise ValueError("guide_id contains unsafe path characters")
    paths = (
        output_dir / f"{guide_id}.guide.json",
        output_dir / f"{guide_id}.provenance.json",
        output_dir / f"{guide_id}.quality.json",
    )
    if any(path.exists() for path in paths):
        raise FileExistsError("refusing to overwrite an existing guide artifact")
    values = (bundle["guide"], bundle["provenance"], bundle["quality_report"])
    written: list[Path] = []
    try:
        for path, value in zip(paths, values):
            path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            written.append(path)
    except Exception:
        for path in written:
            path.unlink(missing_ok=True)
        raise
    return paths
