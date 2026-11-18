"""Link Wikipedia discovery to goals, benchmarks, and governed learning events.

Search results are references, not training data or ground truth. This module
does not store article bodies and defaults model-weight training to blocked.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote, quote_plus, urlencode, urlparse
from urllib.request import Request, urlopen

from .benchmark_learning_adapter import benchmark_to_event


ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config" / "wikipedia-learning-bridge.json"
POLICY = json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def _as_terms(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, list):
        return " ".join(str(item).strip() for item in value if str(item).strip())
    return ""


def build_target_map(goals: dict[str, Any], benchmarks: dict[str, Any]) -> dict[str, Any]:
    """Give every registered goal and benchmark a Wikipedia discovery query."""
    goal_rows = goals.get("goals", [])
    benchmark_rows = benchmarks.get("tasks", [])
    if not isinstance(goal_rows, list) or not isinstance(benchmark_rows, list):
        raise ValueError("goal registry goals and benchmark registry tasks must be arrays")

    mapped_goals = []
    for row in goal_rows:
        if not isinstance(row, dict):
            raise ValueError("goal registry entries must be objects")
        goal_id = row.get("area_id") or row.get("goal_id")
        label = _as_terms(row.get("goal") or row.get("title"))
        if not goal_id or not label:
            raise ValueError("every goal needs an area_id/goal_id and a goal/title")
        mapped_goals.append({
            "goal_id": str(goal_id),
            "label": label,
            "query": label,
            "wikipedia_search_url": POLICY["source"]["search_page_endpoint"] + quote_plus(label),
            "gate": row.get("gate"),
            "status": row.get("status", "unverified"),
            "benchmark_ids": [],
        })

    mapped_benchmarks = []
    for row in benchmark_rows:
        if isinstance(row, str):
            benchmark_id = label = row.strip()
        elif isinstance(row, dict):
            benchmark_id = str(row.get("benchmark_id") or row.get("id") or row.get("task_id") or "").strip()
            label = _as_terms(row.get("name") or row.get("task") or row.get("title") or benchmark_id)
        else:
            raise ValueError("benchmark entries must be strings or objects")
        if not benchmark_id or not label:
            raise ValueError("every benchmark needs an id and label")
        mapped_benchmarks.append({
            "benchmark_id": benchmark_id,
            "label": label,
            "query": label,
            "wikipedia_search_url": POLICY["source"]["search_page_endpoint"] + quote_plus(label),
        })

    if not mapped_goals or not mapped_benchmarks:
        raise ValueError("both goal and benchmark registries must contain targets")
    return {
        "schema": "dreamco.wikipedia_learning_target_map.v1",
        "source_id": POLICY["source"]["id"],
        "goal_count": len(mapped_goals),
        "benchmark_count": len(mapped_benchmarks),
        "goals": mapped_goals,
        "benchmarks": mapped_benchmarks,
        "training_policy": "retrieval_only_until_explicit_consent_and_page_specific_rights_review",
    }


def _fetch_json(url: str, timeout: int) -> dict[str, Any]:
    parsed = urlparse(url)
    allowed_hosts = POLICY["retrieval_limits"]["allowed_hosts"]
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise ValueError("Wikipedia API requests must use HTTPS on an allowed host")
    request = Request(url, headers={"User-Agent": "DreamCoBuddy/1.0 (Wikipedia research; contact via repository)"})
    with urlopen(request, timeout=timeout) as response:
        final_url = urlparse(response.geturl())
        if final_url.scheme != "https" or final_url.hostname not in allowed_hosts:
            raise ValueError("Wikipedia API redirected outside the allowed HTTPS host")
        if response.status != 200:
            raise RuntimeError(f"Wikipedia search returned HTTP {response.status}")
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Wikipedia search response must be an object")
    return payload


def search_wikipedia(query: str, fetch_json: Callable[[str, int], dict[str, Any]] = _fetch_json,
                     limit: int = 5) -> list[dict[str, Any]]:
    """Read-only English Wikipedia search; injectable fetcher keeps tests offline."""
    query = " ".join(query.split())
    max_results = POLICY["retrieval_limits"]["max_results"]
    if not query or len(query) > 300:
        raise ValueError("query must contain 1 to 300 characters")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= max_results:
        raise ValueError(f"limit must be between 1 and {max_results}")
    endpoint = POLICY["source"]["search_endpoint"]
    url = f"{endpoint}?{urlencode({'q': query, 'limit': limit})}"
    payload = fetch_json(url, POLICY["retrieval_limits"]["timeout_seconds"])
    pages = payload.get("pages", [])
    if not isinstance(pages, list):
        raise ValueError("Wikipedia search pages must be an array")
    results = []
    for page in pages[:limit]:
        if not isinstance(page, dict):
            continue
        title = page.get("title")
        key = page.get("key") or title
        if not isinstance(title, str) or not title.strip() or not isinstance(key, str):
            continue
        article_url = POLICY["source"]["article_base"] + quote(key.replace(" ", "_"), safe="()_,:-")
        source_id = "wiki:" + hashlib.sha256(article_url.encode()).hexdigest()[:20]
        results.append({
            "source_id": source_id,
            "source_family": "wikipedia",
            "title": title,
            "url": article_url,
            "description": page.get("description"),
            "revision_id": page.get("revision"),
            "retrieved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "content_hash": page.get("content_hash"),
            "license_status": page.get("license_status", "unknown"),
            "terms_checked": page.get("terms_checked") is True,
            "body_stored": False,
        })
    return results


def create_learning_event(goal_id: str, benchmark_result: dict[str, Any],
                          sources: list[dict[str, Any]], *, training_consent: bool = False,
                          isolated_training: bool = False, holdout_verified: bool = False,
                          rights_reviewed: bool = False, training_consent_ref: str | None = None,
                          isolation_run_id: str | None = None, holdout_evidence_ref: str | None = None,
                          rights_review_id: str | None = None) -> dict[str, Any]:
    """Link a measured benchmark gap to sources and fail closed on weight training."""
    if not goal_id.strip():
        raise ValueError("goal_id is required")
    if any(not isinstance(source, dict) or source.get("source_family") != "wikipedia"
           or not source.get("source_id") or not source.get("url") for source in sources):
        raise ValueError("sources must be Wikipedia source references with ids and URLs")
    event = benchmark_to_event({**benchmark_result, "goal_id": goal_id})
    rights_ok = bool(sources) and rights_reviewed is True and bool(rights_review_id) and all(
        source.get("license_status") == "approved" and source.get("terms_checked") is True
        for source in sources
    )
    training_ready = all((training_consent is True, bool(training_consent_ref),
                          isolated_training is True, bool(isolation_run_id),
                          holdout_verified is True, bool(holdout_evidence_ref), rights_ok))
    reasons = []
    if training_consent is not True or not training_consent_ref:
        reasons.append("explicit_training_consent_or_evidence_missing")
    if isolated_training is not True or not isolation_run_id:
        reasons.append("isolated_training_not_verified")
    if holdout_verified is not True or not holdout_evidence_ref:
        reasons.append("independent_holdout_not_verified")
    if not rights_ok:
        reasons.append("page_specific_rights_or_terms_review_missing")
    recommendation = (
        "regression_check_and_retest" if event["success"]
        else "review_cited_sources_then_create_original_sandbox_practice_and_retest"
    )
    event.update({
        "goal_ids": [goal_id],
        "wikipedia_source_ids": [source["source_id"] for source in sources],
        "wikipedia_source_refs": [{key: source.get(key) for key in
                                   ("source_id", "title", "url", "revision_id", "retrieved_at", "content_hash")}
                                  for source in sources],
        "recommended_next_step": recommendation,
        "training_eligibility": "candidate_ready_for_review" if training_ready else "blocked",
        "training_block_reasons": reasons,
        "training_evidence_refs": {
            "consent": training_consent_ref,
            "isolation_run": isolation_run_id,
            "holdout": holdout_evidence_ref,
            "rights_review": rights_review_id,
        },
        "raw_article_text_retained": False,
    })
    return event


def build_default_target_map() -> dict[str, Any]:
    goals = json.loads((ROOT / "reports" / "goals_to_gates.json").read_text(encoding="utf-8"))
    benchmarks = json.loads((ROOT / "config" / "buddy-benchmark-task-registry.json").read_text(encoding="utf-8"))
    return build_target_map(goals, benchmarks)
