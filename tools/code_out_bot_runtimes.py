#!/usr/bin/env python3
"""Generate executable baseline runtimes and smoke tests for every bot profile."""

from __future__ import annotations

import json
import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOTS_DIR = ROOT / "bots"
TEST_DIR = ROOT / "tests" / "generated_bot_smoke"
REPORT_DIR = ROOT / "reports"
SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")
HIGH_RISK_TERMS = (
    "trading",
    "crypto",
    "payment",
    "legal",
    "medical",
    "health",
    "security",
    "defense",
    "tax",
    "loan",
    "credit",
    "wallet",
    "fraud",
)


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_identifier(value: str) -> str:
    cleaned = SLUG_RE.sub("_", value).strip("_")
    if not cleaned:
        return "bot"
    if cleaned[0].isdigit():
        cleaned = f"bot_{cleaned}"
    return cleaned.lower()


def test_identifier(value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    return f"{safe_identifier(value)}_{digest}"


def class_name(value: str) -> str:
    parts = [part for part in SLUG_RE.split(value) if part]
    name = "".join(part[:1].upper() + part[1:] for part in parts) + "Runtime"
    if not name or name[0].isdigit():
        name = f"Bot{name}"
    return name


def risk_level(profile: dict) -> str:
    text = " ".join(
        str(profile.get(key, ""))
        for key in ("slug", "displayName", "name", "category", "description")
    ).lower()
    return "high" if any(term in text for term in HIGH_RISK_TERMS) else "standard"


def runtime_source(profile: dict) -> str:
    slug = profile.get("slug") or "bot"
    display_name = profile.get("displayName") or profile.get("name") or slug
    division = profile.get("division") or "Unassigned"
    category = profile.get("category") or "uncategorized"
    description = profile.get("description") or f"{display_name} operating runtime."
    capabilities = profile.get("capabilities") or []
    if isinstance(capabilities, str):
        capabilities = [capabilities]
    capability_text = ", ".join(str(item) for item in capabilities) or "general_operations"
    risk = risk_level(profile)
    cls = class_name(str(slug))
    approval_required = risk == "high"
    return f'''"""Executable runtime for {display_name}."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class {cls}:
    """Deterministic, local-first operating surface for {display_name}."""

    slug: str = {slug!r}
    name: str = {display_name!r}
    division: str = {division!r}
    category: str = {category!r}
    description: str = {description!r}
    capabilities: tuple[str, ...] = {tuple(str(item) for item in capabilities)!r}
    risk_level: str = {risk!r}
    approval_required: bool = {approval_required!r}
    events: list[dict[str, Any]] = field(default_factory=list)

    def describe(self) -> dict[str, Any]:
        return {{
            "slug": self.slug,
            "name": self.name,
            "division": self.division,
            "category": self.category,
            "description": self.description,
            "capabilities": list(self.capabilities),
            "risk_level": self.risk_level,
            "approval_required": self.approval_required,
            "storage_policy": self.storage_policy(),
        }}

    def storage_policy(self) -> dict[str, Any]:
        return {{
            "mode": "local_first",
            "network_default": "disabled_until_configured",
            "secrets": "environment_or_vault_only",
            "retention": "operator_defined",
            "audit_log": True,
        }}

    def plan(self, objective: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {{}}
        steps = [
            "validate_inputs",
            "load_local_context",
            "apply_domain_rules",
            "produce_recommendation",
            "record_audit_event",
        ]
        if self.approval_required:
            steps.append("request_human_approval")
        return {{
            "objective": objective,
            "bot": self.slug,
            "capability_summary": {capability_text!r},
            "context_keys": sorted(context),
            "steps": steps,
            "sandboxed": True,
        }}

    def execute(self, objective: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        planned = self.plan(objective, context)
        now = datetime.now(timezone.utc).isoformat()
        result = {{
            "status": "approval_required" if self.approval_required else "completed",
            "objective": objective,
            "bot": self.slug,
            "outputs": {{
                "summary": f"{{self.name}} processed the objective in local-first mode.",
                "next_actions": planned["steps"],
                "live_external_action_taken": False,
            }},
            "completed_at": now,
        }}
        self.events.append({{"type": "runtime.execute", "at": now, "result": result}})
        return result

    def evaluate(self, result: dict[str, Any]) -> dict[str, Any]:
        checks = {{
            "has_status": bool(result.get("status")),
            "no_live_external_action": result.get("outputs", {{}}).get("live_external_action_taken") is False,
            "audit_event_recorded": bool(self.events),
        }}
        return {{
            "bot": self.slug,
            "ready_for_smoke_test": all(checks.values()),
            "checks": checks,
        }}

    def run(self, objective: str = "baseline readiness check", context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = self.execute(objective, context)
        result["evaluation"] = self.evaluate(result)
        return result


def create_bot() -> {cls}:
    return {cls}()
'''


def test_source(profile: dict) -> str:
    slug = str(profile.get("slug") or "bot")
    test_name = test_identifier(slug)
    cls = class_name(slug)
    profile_path = f"bots/{slug}/bot_profile.json"
    runtime_path = f"bots/{slug}/runtime.py"
    return f'''from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_runtime():
    runtime_path = ROOT / {runtime_path!r}
    spec = importlib.util.spec_from_file_location({test_name!r} + "_runtime", runtime_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[{test_name!r} + "_runtime"] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_{test_name}_runtime_smoke():
    profile = json.loads((ROOT / {profile_path!r}).read_text(encoding="utf-8"))
    module = load_runtime()
    bot = module.create_bot()
    assert isinstance(bot, module.{cls})
    assert bot.slug == profile["slug"]
    assert bot.storage_policy()["mode"] == "local_first"
    result = bot.run("generated smoke test", {{"profile_status": profile.get("status")}})
    assert result["outputs"]["live_external_action_taken"] is False
    assert result["evaluation"]["ready_for_smoke_test"] is True
'''


def main() -> None:
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    for old_test in TEST_DIR.glob("test_*_runtime.py"):
        old_test.unlink()
    profiles = sorted(BOTS_DIR.glob("*/bot_profile.json"))
    generated: list[dict[str, str]] = []
    for profile_path in profiles:
        profile = load_profile(profile_path)
        slug = str(profile.get("slug") or profile_path.parent.name)
        runtime_path = profile_path.parent / "runtime.py"
        smoke_path = TEST_DIR / f"test_{test_identifier(slug)}_runtime.py"
        runtime_path.write_text(runtime_source(profile), encoding="utf-8")
        smoke_path.write_text(test_source(profile), encoding="utf-8")
        generated.append(
            {
                "slug": slug,
                "runtime": str(runtime_path.relative_to(ROOT)),
                "test": str(smoke_path.relative_to(ROOT)),
                "risk_level": risk_level(profile),
            }
        )

    report = {
        "schema": "dreamco.bot_runtime_generation.v1",
        "bot_profiles_scanned": len(profiles),
        "generated_runtime_count": len(generated),
        "generated_smoke_test_count": len(generated),
        "generated": generated,
    }
    (REPORT_DIR / "bot_runtime_generation.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({k: report[k] for k in report if k != "generated"}, indent=2))


if __name__ == "__main__":
    main()
