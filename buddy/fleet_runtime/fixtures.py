"""Generated per-bot smoke fixtures.

Every mapped bot gets a deterministic fixture built from its own declared
capabilities. Expectations come from set logic over the capability text and
the synthetic input (for example: the only label fully contained in the probe
text must win), never from running the engine, so a passing fixture is a
real check of the bot's manifest + engine wiring. They are computed at load
time instead of committed, so they cannot drift from the manifests.
"""
from __future__ import annotations

from typing import Any

from .contract import expand
from .engines import ESCALATION_RE, tokens
from .permissions import text_declares_live_action


def _pick_distinct_capability(caps: list[str], prefix: str) -> str | None:
    """First capability that would win a token-overlap ranking outright.

    Derived from set logic (no engine run): the chosen label's tokens all
    appear in the probe text, and no other label's token set is fully
    contained in that text (which would tie at score 1.0).
    """
    for cap in caps:
        own = set(tokens(cap))
        if not own:
            continue
        text = set(tokens(f"{prefix} {cap}"))
        if all(not (set(tokens(other)) and set(tokens(other)) <= text) for other in caps if other != cap):
            return cap
    return None


def derive_fixture(engine: str, caps: list[str]) -> dict[str, Any] | None:
    """Deterministic, bot-specific fixture with independently derived expectations."""
    if not caps or engine == "unmapped":
        return None
    if engine == "analysis":
        cap = caps[0]
        return {"engine": engine, "origin": "generated", "task": {
            "objective": f"Apply {cap} to synthetic records",
            "input": {"records": [{"segment": "a", "units": 3}, {"segment": "b", "units": 5}, {"segment": "a", "units": 4}],
                      "metric": "units", "group_by": "segment", "top_n": 1}},
            "expect": [{"path": "status", "equals": "ok"}, {"path": "result.row_count", "equals": 3},
                       {"path": "result.groups.a.sum", "equals": 7.0}, {"path": "result.top.0.segment", "equals": "b"},
                       {"path": "result.capabilities_considered", "contains": cap}]}
    if engine == "classification":
        cap = _pick_distinct_capability(caps, "Synthetic request regarding")
        if cap is None:
            return None
        text = f"Synthetic request regarding {cap}"
        return {"engine": engine, "origin": "generated", "task": {"objective": "Route a synthetic request", "input": {"text": text}},
                "expect": [{"path": "status", "equals": "ok"}, {"path": "result.top_label", "equals": cap},
                           {"path": "result.confidence", "equals": 1.0},
                           {"path": "result.escalate_to_human", "equals": bool(ESCALATION_RE.search(text))}]}
    if engine == "workflow":
        titles = [f"Prepare: {c}" for c in caps]
        gated = [t for t in titles if text_declares_live_action(t)]
        free = [t for t in titles if t not in gated]
        expect: list[dict[str, Any]] = [{"path": "status", "equals": "ok"}, {"path": "result.progress.total", "equals": len(titles)},
                                        {"path": "result.progress.done", "equals": 0}]
        expect += [{"path": "result.awaiting_owner_approval", "contains": t} for t in gated]
        if free:
            expect.append({"path": "result.next_actions.0", "equals": free[0]})
        return {"engine": engine, "origin": "generated", "task": {"objective": "Plan a synthetic sandbox run", "input": {}}, "expect": expect}
    if engine == "drafting":
        cap = _pick_distinct_capability(caps, "Draft synthetic notes on")
        if cap is None:
            return None
        return {"engine": engine, "origin": "generated", "task": {"objective": f"Draft synthetic notes on {cap}", "input": {}},
                "expect": [{"path": "status", "equals": "ok"}, {"path": "result.sections", "contains": cap},
                           {"path": "result.generated_by", "equals": "offline_deterministic"},
                           {"path": "result.draft_markdown", "contains": "No model was called"}]}
    return None


def build_fixtures(collection: dict[str, Any]) -> dict[str, Any]:
    fixtures = {}
    for compact in collection["bots"]:
        manifest = expand(compact, collection)
        fixture = derive_fixture(manifest["engine"], manifest["capabilities"])
        if fixture:
            fixtures[manifest["slug"]] = fixture
    return {
        "schema": "dreamco.fleet_smoke_fixtures.v1",
        "generator": "buddy/fleet_runtime/fixtures.py",
        "policy": "Generated per-bot fixtures. Expectations are derived from the bot's own declared capabilities by set logic, not by running the engine. Passing proves the bot's capabilities route through its shared engine deterministically offline; it does not prove output quality. Hand-written fixtures in config/bots/smoke-fixtures.json override these. Computed at load time, so they never drift from the manifests.",
        "fixtures": fixtures,
    }
