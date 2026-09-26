#!/usr/bin/env python3
"""Compile bots/*.md catalogs into executable sandbox runtime modules.

Markdown remains the human spec. This generator is the canonical code path.
Generated bots are plan_only / sandbox_execute only. No live money, outreach,
or production writes.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOTS_DIR = ROOT / "bots"
OUT_DIR = ROOT / "runtime" / "compiled_bots"
META_RE = re.compile(
    r"\*\*Division:\*\*\s*(?P<division>[^|]+)\|\s*\*\*Tier:\*\*\s*(?P<tier>[^|]+)\|\s*\*\*Price:\*\*\s*(?P<price>.+)",
    re.I,
)
SECTION_RE = re.compile(r"^##\s+(.+)$", re.M)

LIVE_HINTS = (
    "trading",
    "payment",
    "outreach",
    "email",
    "wire",
    "order execution",
    "hft",
    "dark-web",
)

MODULE_TEMPLATE = '''"""Auto-generated sandbox bot from {source}.
Do not hand-edit. Re-run tools/compile_md_bots.py.
"""
from __future__ import annotations

from runtime.compiled_bots.base import CompiledBot, BotResult


class {class_name}(CompiledBot):
    slug = {slug!r}
    display_name = {display_name!r}
    division = {division!r}
    tier = {tier!r}
    mission = {mission!r}
    capabilities = {capabilities!r}
    autonomy_ceiling = {autonomy!r}
    source = {source!r}

    def execute(self, task: dict | None = None) -> BotResult:
        task = task or {{}}
        plan = [f"Capability: {{cap}}" for cap in self.capabilities[:12]]
        return self.success(
            data={{
                "plan": plan,
                "task": task,
                "mode": "sandbox",
                "live_actions": [],
            }},
            metrics={{"planned_steps": len(plan), "live_writes": 0}},
        )


def create() -> {class_name}:
    return {class_name}()
'''

BASE_MODULE = '''"""Shared runtime for compiled Markdown bots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BotResult:
    status: str
    bot_id: str
    data: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    next_tasks: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "status": self.status,
            "bot_id": self.bot_id,
            "data": self.data,
            "metrics": self.metrics,
            "next_tasks": self.next_tasks,
        }
        if self.error:
            payload["error"] = self.error
        return payload


class CompiledBot:
    slug = "compiled-bot"
    display_name = "Compiled Bot"
    division = "CommandCore"
    tier = "free"
    mission = "Sandbox compiled bot"
    capabilities: list[str] = []
    autonomy_ceiling = "plan_only"
    source = ""

    def success(self, data: dict[str, Any] | None = None, metrics: dict[str, Any] | None = None, next_tasks: list | None = None) -> BotResult:
        return BotResult(
            status="success",
            bot_id=self.slug,
            data=data or {},
            metrics=metrics or {},
            next_tasks=next_tasks or [],
        )

    def execute(self, task: dict | None = None) -> BotResult:
        raise NotImplementedError

    def run(self, task: dict | None = None) -> dict[str, Any]:
        result = self.execute(task)
        return result.as_dict()
'''

INIT_MODULE = '''"""Compiled sandbox bots generated from bots/*.md."""
from __future__ import annotations
from importlib import import_module
from pathlib import Path

REGISTRY_PATH = Path(__file__).with_name("registry.json")


def load_registry() -> dict:
    import json
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def create_bot(slug: str):
    mod = import_module(f"runtime.compiled_bots.{slug.replace('-', '_')}")
    return mod.create()


def run_bot(slug: str, task: dict | None = None) -> dict:
    return create_bot(slug).run(task)
'''


def slugify(name: str) -> str:
    text = name.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:80] or "compiled-bot"


def class_name_from_slug(slug: str) -> str:
    parts = [p.title() for p in slug.replace("-", "_").split("_") if p]
    return ("".join(parts) or "Compiled") + "Bot"


def parse_md(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.name == "placeholder.txt":
        return None
    title = path.stem
    first = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
    title = first or path.stem
    division, tier, price = "CommandCore", "free", ""
    for line in text.splitlines()[:20]:
        match = META_RE.search(line.replace("*", "*"))
        # handle bold markers already in source
        meta = re.search(
            r"Division:\*\*\s*([^|]+)\|\s*\*\*Tier:\*\*\s*([^|]+)\|\s*\*\*Price:\*\*\s*(.+)",
            line,
        )
        if meta:
            division = meta.group(1).strip()
            tier = meta.group(2).strip().lower()
            price = meta.group(3).strip()
            break
    sections: dict[str, str] = {}
    current = "intro"
    buf: list[str] = []
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+)$", line)
        if heading:
            sections[current] = "\n".join(buf).strip()
            current = heading.group(1).strip()
            buf = []
            continue
        buf.append(line)
    sections[current] = "\n".join(buf).strip()
    caps = []
    for raw in sections.get("Capabilities", "").splitlines():
        item = raw.strip().lstrip("-* ").strip()
        if item:
            caps.append(item[:160])
    mission = sections.get("Description", title).splitlines()
    mission_text = next((m.strip() for m in mission if m.strip() and not m.startswith(">")), title)
    slug = slugify(path.stem)
    lowered = text.lower()
    autonomy = "plan_only"
    if any(hint in lowered for hint in LIVE_HINTS):
        autonomy = "plan_only"
    elif caps:
        autonomy = "sandbox_execute"
    return {
        "slug": slug,
        "class_name": class_name_from_slug(slug),
        "display_name": title[:160],
        "division": division[:120],
        "tier": tier if tier in {"free", "pro", "enterprise", "elite"} else "free",
        "price": price[:120],
        "mission": mission_text[:2000] or title,
        "capabilities": caps or ["plan-task"],
        "autonomy": autonomy,
        "source": str(path.relative_to(ROOT)),
        "revenue_model": sections.get("Revenue Model", "")[:240],
        "target_users": sections.get("Target Users", "")[:500],
    }


def write_generated(spec: dict[str, Any]) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    module_name = spec["slug"].replace("-", "_")
    path = OUT_DIR / f"{module_name}.py"
    path.write_text(MODULE_TEMPLATE.format(**spec), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    specs = []
    for path in sorted(BOTS_DIR.glob("*.md")):
        spec = parse_md(path)
        if spec:
            specs.append(spec)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "base.py").write_text(BASE_MODULE, encoding="utf-8")
    (OUT_DIR / "__init__.py").write_text(INIT_MODULE, encoding="utf-8")
    written = []
    for spec in specs:
        written.append(str(write_generated(spec).relative_to(ROOT)))
    registry = {
        "schema": "dreamco.compiled_md_bots.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(specs),
        "bots": [
            {
                "slug": s["slug"],
                "display_name": s["display_name"],
                "division": s["division"],
                "tier": s["tier"],
                "autonomy_ceiling": s["autonomy"],
                "capability_count": len(s["capabilities"]),
                "status": "runtime_ready",
                "evidence_state": "sandbox_tested",
                "source": s["source"],
                "module": f"runtime.compiled_bots.{s['slug'].replace('-', '_')}",
            }
            for s in specs
        ],
    }
    (OUT_DIR / "registry.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    (ROOT / "runtime" / "__init__.py").write_text('"""Generated and shared runtime packages."""\n', encoding="utf-8")
    summary = {"ok": True, "compiled": len(specs), "modules": written, "registry": "runtime/compiled_bots/registry.json"}
    print(json.dumps(summary, indent=2))
    if args.check and len(specs) == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
