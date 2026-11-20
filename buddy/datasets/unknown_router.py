"""Turn unknown tasks into sourced research and division-routing work items."""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any
from .hub import DatasetHub
from .sources import discover

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config/masterbot-65-registry.json"
ALIASES = {
 "DreamFinance": ["finance","accounting","economics","banking"],
 "DreamRealEstate": ["real estate","property","housing","mortgage"],
 "DreamSalesPro": ["sales","crm","customer","marketing"],
 "DreamAIInfra": ["machine learning","model","cloud","infrastructure"],
 "DreamData": ["database","sql","analytics","data engineering"],
 "DreamCyber": ["security","cyber","network","vulnerability"],
 "DreamHealth": ["health","medical","biology"],
 "DreamEducation": ["education","teaching","curriculum","learning"],
 "DreamConstruction": ["construction","engineering","building","cad"],
 "DreamProduction": ["manufacturing","industrial","production"],
 "DreamCodeLab": ["code","programming","software","repository"],
 "DreamResearch": ["research","science","literature","study"],
 "DreamBenchmark": ["benchmark","evaluation","testing","quality"],
 "DreamKnowledge": ["knowledge","retrieval","search","documentation"],
 "DreamVision": ["image","vision","visual","video"],
 "DreamVoice": ["audio","speech","voice"],
 "DreamProduct": ["product","design","prototype","invention"],
 "DreamSimulation": ["simulation","physics","modeling","robotics"],
 "DreamDiscovery": ["discovery","unknown","investigation"],
 "DreamResource": ["resource","dataset","catalog","funding"],
 "DreamFuture": ["forecast","prediction","time series"],
}
def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))

def route_problem(problem: str, hub: DatasetHub | None = None, external: bool = False) -> dict[str, Any]:
    clean = " ".join((problem or "").split())
    if len(clean) < 8:
        raise ValueError("Describe the unknown problem in at least eight characters")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    bots = registry.get("divisions", [])
    tokens = _tokens(clean)
    ranked = []
    for bot in bots:
        name = bot["name"]
        tags = ALIASES.get(name, [name.lower().replace("dream", "")])
        score = sum(1 for tag in tags if _tokens(tag) & tokens)
        if score:
            ranked.append({"masterbot_id": bot["id"], "masterbot": name, "score": score, "routing_status": "KEYWORD_CANDIDATE_REQUIRES_REVIEW"})
    ranked.sort(key=lambda x: (-x["score"], x["masterbot_id"]))
    local = (hub or DatasetHub()).search(clean, limit=15)
    outside = discover(clean, limit=5) if external else {"query": clean, "results": [], "source_errors": {"network": "Not requested"}, "downloaded_files": False, "training_approved": False}
    status = "CANDIDATES_FOUND_REQUIRES_REVIEW" if local or outside["results"] or ranked else "MISSING_DATA_RESEARCH_REQUIRED"
    return {
        "schema": "dreamco.unknown_problem_route.v1", "problem": clean,
        "capability_gap": "UNCLASSIFIED_REQUIRES_SPECIALIST_REVIEW",
        "masterbot_candidates": ranked[:5], "local_dataset_candidates": local,
        "external_metadata_candidates": outside["results"], "external_model_candidates": outside.get("model_results", []), "source_errors": outside["source_errors"],
        "status": status, "next_actions": [
            "verify_primary_masterbot_and_collaborators", "review_source_license_terms_and_access",
            "inspect_authorized_sample", "create_versioned_dataset_card_and_quality_report",
            "create_holdout_benchmark_fixture", "retest_unknown_problem"
        ],
        "claims": {"problem_solved": False, "datasets_downloaded": False, "weights_trained": False, "mastery_awarded": False}
    }
