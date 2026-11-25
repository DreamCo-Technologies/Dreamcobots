"""Internal-first retrieval and evidence-aware registry for Buddy library guides.

This adapter reads only DreamCo-owned guide artifacts. It never fetches packages,
executes library code, downloads external material, or grants training permission.
Unknown knowledge is returned as a gap; callers must explicitly persist it.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
CURRICULUM = ROOT / "config/buddy-universal-library-curriculum.json"
ECOSYSTEMS = ROOT / "config/library_ecosystems.json"
GUIDE_DIR = ROOT / "data/buddy-library-study-guides"
GAP_LOG = ROOT / "data/buddy-library-knowledge-gaps.jsonl"
APPROVED_STATES = {"approved_for_study", "mastered"}
SEARCHABLE_STATES = APPROVED_STATES


@dataclass(frozen=True)
class LibraryGuide:
    canonical_id: str
    name: str
    ecosystem: str
    version_reviewed: str
    status: str
    path: Path
    document: dict[str, Any]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _tokens(value: str) -> set[str]:
    return {part for part in re.findall(r"[a-z0-9][a-z0-9_.+-]*", value.lower()) if len(part) > 1}


def _guide_files(root: Path) -> list[Path]:
    directory = root / "data/buddy-library-study-guides"
    if not directory.exists():
        return []
    return sorted(directory.glob("*.json"))


def load_approved_guides(root: Path = ROOT) -> list[LibraryGuide]:
    guides: list[LibraryGuide] = []
    seen: set[str] = set()
    for path in _guide_files(root):
        data = _read_json(path)
        library = data.get("library") if isinstance(data.get("library"), dict) else {}
        canonical_id = str(library.get("canonical_id", "")).strip()
        name = str(library.get("name", "")).strip()
        status = str(data.get("status", "draft"))
        if not canonical_id or not name:
            raise ValueError(f"library guide missing canonical identity: {path}")
        if canonical_id in seen:
            raise ValueError(f"duplicate library guide canonical_id: {canonical_id}")
        seen.add(canonical_id)
        if status not in {"draft", "review_required", "approved_for_study", "blocked", "stale", "mastered"}:
            raise ValueError(f"invalid library guide status in {path}: {status}")
        if status not in SEARCHABLE_STATES:
            continue
        rights = data.get("rights") if isinstance(data.get("rights"), dict) else {}
        if rights.get("documentation_access") not in {"public", "account_required"}:
            continue
        if rights.get("derivative_summary_permission") not in {"approved", "not_required_for_original_notes"}:
            continue
        guides.append(LibraryGuide(
            canonical_id=canonical_id,
            name=name,
            ecosystem=str(library.get("ecosystem", "")),
            version_reviewed=str(library.get("version_reviewed", "")),
            status=status,
            path=path,
            document=data,
        ))
    return guides


def search_internal_library_knowledge(
    query: str,
    *,
    root: Path = ROOT,
    limit: int = 10,
    include_experimental: bool = False,
) -> dict[str, Any]:
    """Search only reviewed DreamCo guides; return a gap instead of routing by default."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    query_tokens = _tokens(query)
    results = []
    for guide in load_approved_guides(root):
        doc = guide.document
        library = doc.get("library", {})
        learning = doc.get("learning_map", {})
        concepts = learning.get("concepts", []) if isinstance(learning, dict) else []
        use_cases = doc.get("use_cases", [])
        text_parts = [guide.name, guide.canonical_id, guide.ecosystem]
        text_parts.extend(learning.get("objectives", []) if isinstance(learning, dict) else [])
        text_parts.extend(c.get("name", "") + " " + c.get("explanation", "") for c in concepts if isinstance(c, dict))
        for use_case in use_cases:
            if isinstance(use_case, dict):
                text_parts.extend([str(use_case.get("scenario", "")), str(use_case.get("implementation_pattern", ""))])
                if not include_experimental and use_case.get("category") == "experimental":
                    continue
        haystack = _tokens(" ".join(text_parts))
        overlap = query_tokens & haystack
        if not overlap:
            continue
        score = len(overlap) / max(len(query_tokens), 1)
        results.append({
            "canonical_id": guide.canonical_id,
            "name": guide.name,
            "ecosystem": guide.ecosystem,
            "version_reviewed": guide.version_reviewed,
            "status": guide.status,
            "score": round(score, 4),
            "guide_path": guide.path.relative_to(root).as_posix(),
            "source_urls": [
                row.get("url") for row in doc.get("provenance", {}).get("sources", [])
                if isinstance(row, dict) and row.get("url")
            ],
            "evidence_state": doc.get("evaluation", {}).get("evidence_state", "unknown"),
        })
    results.sort(key=lambda row: (-row["score"], row["canonical_id"]))
    matches = results[:limit]
    return {
        "schema": "dreamco.buddy_internal_library_search.v1",
        "query": query,
        "source": "dreamco_approved_library_guides",
        "internal_match_count": len(results),
        "matches": matches,
        "knowledge_gap": None if matches else {
            "status": "internal_knowledge_gap",
            "reason": "No approved, rights-eligible internal library guide matched the request.",
            "next_action": "Create a gap record, discover authoritative first-party sources, review rights, then author an original guide.",
            "external_model_routing_required": False,
        },
        "truth_boundary": "Only approved DreamCo guide artifacts are searched. No match does not prove the subject is unknown externally.",
    }


def record_library_knowledge_gap(
    query: str,
    *,
    reason: str = "no_approved_internal_guide_match",
    root: Path = ROOT,
    requested_by: str = "buddy",
) -> dict[str, Any]:
    """Append a gap event. This does not initiate network access or external routing."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason must be a non-empty string")
    event = {
        "schema": "dreamco.buddy_library_knowledge_gap.v1",
        "query": query.strip()[:1000],
        "reason": reason.strip()[:500],
        "requested_by": requested_by.strip()[:100],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "open",
        "next_action": "discover_authoritative_sources_and_review_rights",
        "external_routing_performed": False,
    }
    path = root / "data/buddy-library-knowledge-gaps.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event


def library_coverage_report(root: Path = ROOT) -> dict[str, Any]:
    curriculum = _read_json(root / "config/buddy-universal-library-curriculum.json")
    ecosystems = _read_json(root / "config/library_ecosystems.json")
    guides = load_approved_guides(root)
    discovered_ecosystems = ecosystems.get("ecosystems", [])
    gap_path = root / "data/buddy-library-knowledge-gaps.jsonl"
    gaps = 0
    if gap_path.is_file():
        gaps = sum(1 for line in gap_path.read_text(encoding="utf-8").splitlines() if line.strip())
    return {
        "schema": "dreamco.buddy_library_coverage_report.v1",
        "catalog_strategy": curriculum.get("scope", {}).get("catalog_strategy"),
        "ecosystem_count": len(discovered_ecosystems),
        "approved_guide_count": len(guides),
        "open_gap_event_count": gaps,
        "ecosystems": [row.get("id") for row in discovered_ecosystems],
        "guide_ids": [guide.canonical_id for guide in guides],
        "status": "partial" if len(guides) == 0 or gaps else "in_progress",
        "worldwide_completeness_claimed": False,
        "truth_boundary": "Ecosystem catalog entries are discovery lanes, not verified package inventories. Approved guide count reflects local DreamCo guide files only.",
    }
