"""Shared capability engines.

Four engines cover most of the fleet. Each takes the bot manifest and a task
and returns a JSON-serialisable result. Engines are deterministic offline;
only ``drafting`` asks the model router for text, and it falls back to a
deterministic outline when no live model is enabled.

Engines never invent facts: analysis works only on records the caller
supplies, and returns ``needs_input`` when there is nothing to analyse.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Any, Callable

from . import router
from .permissions import text_declares_live_action

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset(
    "a an and are as at be by for from has have in into is it its of on or that the this to with your you our "
    "we will can all any per via using use based tool tools engine system management manager".split()
)
ESCALATION_RE = re.compile(r"\b(urgent|emergency|lawsuit|breach|fraud|chargeback|outage|injury|threat)\b", re.I)


def tokens(text: str) -> list[str]:
    out = []
    for raw in TOKEN_RE.findall((text or "").lower()):
        if raw in STOPWORDS or len(raw) < 2:
            continue
        for suffix in ("ing", "ies", "es", "ed", "s"):
            if len(raw) > len(suffix) + 3 and raw.endswith(suffix):
                raw = raw[: -len(suffix)] + ("y" if suffix == "ies" else "")
                break
        out.append(raw)
    return out


def rank_labels(text: str, labels: list[str]) -> list[dict[str, Any]]:
    """Score labels by token overlap with ``text`` (deterministic)."""
    bag = Counter(tokens(text))
    ranked = []
    for index, label in enumerate(labels):
        label_tokens = set(tokens(label))
        if not label_tokens:
            continue
        hits = sum(1 for token in label_tokens if bag[token])
        score = round(hits / len(label_tokens), 4)
        ranked.append({"label": label, "score": score, "matched": sorted(t for t in label_tokens if bag[t]), "_i": index})
    ranked.sort(key=lambda row: (-row["score"], row["_i"]))
    for row in ranked:
        row.pop("_i")
    return ranked


def _objective(task: dict[str, Any]) -> str:
    return str(task.get("objective") or "").strip()


# ---------------------------------------------------------------- analysis
def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def analysis(manifest: dict[str, Any], task: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    data = task.get("input") or {}
    records = data.get("records")
    values = data.get("values")
    if records is None and values is not None:
        records = [{"value": v} for v in values]
    if not isinstance(records, list) or not records:
        return {
            "status": "needs_input",
            "summary": "No records supplied. The analysis engine only analyses caller-supplied data and never fabricates figures.",
            "required_input": ["input.records (list of objects) or input.values (list of numbers)"],
        }
    rows = [row for row in records if isinstance(row, dict)]
    filters = data.get("filters") or {}
    if isinstance(filters, dict) and filters:
        rows = [row for row in rows if all(row.get(k) == v for k, v in filters.items())]
    query = str(data.get("query") or "").strip().lower()
    matches = []
    if query:
        matches = [row for row in rows if any(query in str(v).lower() for v in row.values())]
    fields: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        for key, value in row.items():
            if _is_number(value):
                fields[key].append(float(value))
    stats = {}
    for key in sorted(fields):
        series = fields[key]
        stats[key] = {
            "count": len(series),
            "sum": round(sum(series), 6),
            "mean": round(sum(series) / len(series), 6),
            "min": min(series),
            "max": max(series),
        }
    metric = data.get("metric")
    group_by = data.get("group_by")
    groups = {}
    if group_by:
        bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            bucket[str(row.get(group_by, "∅"))].append(row)
        for key in sorted(bucket):
            entry: dict[str, Any] = {"count": len(bucket[key])}
            if metric:
                nums = [float(r[metric]) for r in bucket[key] if _is_number(r.get(metric))]
                entry["sum"] = round(sum(nums), 6)
                entry["mean"] = round(sum(nums) / len(nums), 6) if nums else None
            groups[key] = entry
    top = []
    if metric:
        top_n = int(data.get("top_n") or 3)
        ranked = sorted((r for r in rows if _is_number(r.get(metric))), key=lambda r: -float(r[metric]))
        top = ranked[: max(1, top_n)]
    return {
        "status": "ok",
        "row_count": len(rows),
        "numeric_fields": stats,
        "groups": groups,
        "top": top,
        "query_matches": matches[:25],
        "query_match_count": len(matches),
        "capabilities_considered": [row["label"] for row in rank_labels(_objective(task), manifest["capabilities"])[:3] if row["score"] > 0],
        "summary": f"Analysed {len(rows)} supplied record(s) across {len(stats)} numeric field(s).",
    }


# ---------------------------------------------------------- classification
def classification(manifest: dict[str, Any], task: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    data = task.get("input") or {}
    text = str(data.get("text") or _objective(task))
    labels = data.get("labels") or manifest["capabilities"]
    if not text.strip() or not labels:
        return {"status": "needs_input", "summary": "Need input.text (or objective) and at least one label.",
                "required_input": ["input.text", "input.labels (optional; defaults to bot capabilities)"]}
    ranked = rank_labels(text, [str(label) for label in labels])
    top = ranked[0] if ranked and ranked[0]["score"] > 0 else None
    escalate = bool(ESCALATION_RE.search(text))
    return {
        "status": "ok",
        "top_label": top["label"] if top else None,
        "confidence": top["score"] if top else 0.0,
        "uncertain": top is None or (len(ranked) > 1 and ranked[1]["score"] == top["score"]),
        "ranked": ranked[:5],
        "escalate_to_human": escalate,
        "summary": (f"Classified as '{top['label']}'" if top else "No label matched; route to a human reviewer.")
        + ("; escalation keyword present." if escalate else "."),
    }


# ----------------------------------------------------------------- workflow
def workflow(manifest: dict[str, Any], task: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    data = task.get("input") or {}
    raw_steps = data.get("steps") or [f"Prepare: {cap}" for cap in manifest["capabilities"]] or ["Prepare plan"]
    completed = {str(s).strip().lower() for s in data.get("completed_steps") or []}
    steps = []
    for index, title in enumerate(raw_steps, start=1):
        title = str(title)
        gated = text_declares_live_action(title)
        steps.append({
            "n": index,
            "title": title,
            "status": "done" if title.strip().lower() in completed else "pending",
            "requires_approval": gated,
            "approval_level": "external_side_effect" if gated else "sandbox",
        })
    pending = [s for s in steps if s["status"] == "pending"]
    next_actions = [s["title"] for s in pending if not s["requires_approval"]][:3]
    blocked = [s["title"] for s in pending if s["requires_approval"]]
    return {
        "status": "ok",
        "objective": _objective(task),
        "steps": steps,
        "progress": {"done": len(steps) - len(pending), "total": len(steps)},
        "next_actions": next_actions,
        "awaiting_owner_approval": blocked,
        "summary": f"{len(steps) - len(pending)}/{len(steps)} steps done; {len(blocked)} step(s) need owner approval before any live action.",
    }


# ----------------------------------------------------------------- drafting
def drafting(manifest: dict[str, Any], task: dict[str, Any], profile: dict[str, Any],
             env: dict[str, str] | None = None) -> dict[str, Any]:
    data = task.get("input") or {}
    objective = _objective(task)
    audience = str(data.get("audience") or manifest.get("target_users") or "the requester")
    tone = str(data.get("tone") or "clear and concise")
    relevant = [row["label"] for row in rank_labels(objective, manifest["capabilities"]) if row["score"] > 0][:4]
    sections = relevant or manifest["capabilities"][:3] or ["Overview"]

    def offline() -> str:
        lines = [f"# {objective or manifest['name']}", "",
                 f"_Offline deterministic outline by {manifest['name']} for {audience} ({tone}). No model was called; replace each section with reviewed content._", ""]
        for section in sections:
            lines += [f"## {section}", f"- Purpose: how '{section}' serves: {objective or 'the request'}", "- Key points: [to be written]", ""]
        lines.append("_No live external action was taken._")
        return "\n".join(lines)

    prompt = (
        f"You are {manifest['name']} in the DreamCo {manifest['division']} division. {manifest.get('description', '')}\n"
        f"Audience: {audience}. Tone: {tone}. Focus capabilities: {', '.join(sections)}.\n"
        f"Task: {objective}\nNever claim live external actions were completed."
    )
    routed = router.complete(prompt, profile, offline, env=env)
    return {
        "status": "ok",
        "draft_markdown": routed["text"],
        "sections": sections,
        "generated_by": routed["mode"],
        "model": routed.get("model"),
        "fallback_reason": routed.get("fallback_reason"),
        "summary": f"Draft with {len(sections)} section(s) via {routed['mode']}.",
    }


ENGINE_FUNCS: dict[str, Callable[..., dict[str, Any]]] = {
    "analysis": analysis,
    "classification": classification,
    "workflow": workflow,
    "drafting": drafting,
}

# Generic smoke task per engine (synthetic data only).
GENERIC_SMOKE_TASKS: dict[str, dict[str, Any]] = {
    "analysis": {"objective": "Summarise the supplied synthetic records", "input": {
        "records": [{"region": "north", "amount": 120}, {"region": "south", "amount": 80}, {"region": "north", "amount": 40}],
        "metric": "amount", "group_by": "region"}},
    "classification": {"objective": "Classify a synthetic request", "input": {"text": "synthetic request for routing"}},
    "workflow": {"objective": "Plan a synthetic sandbox run", "input": {}},
    "drafting": {"objective": "Draft a synthetic sandbox brief", "input": {"audience": "internal reviewer"}},
}
