#!/usr/bin/env python3
"""Build self-contained DreamXXX system packages from App_bots/*.json."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_BOTS = ROOT / "App_bots"
SYSTEMS = ROOT / "systems"

ORCHESTRATOR = '''"""System orchestrator for {name}. Catalog-driven; no live money writes."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


class SystemOrchestrator:
    def __init__(self) -> None:
        self.catalog = json.loads((HERE / "bots.json").read_text(encoding="utf-8"))

    def list_bots(self) -> list:
        bots = self.catalog.get("bots", self.catalog.get("items", []))
        if isinstance(bots, dict):
            return list(bots.keys())
        return bots if isinstance(bots, list) else []

    def run_all(self, task=None):
        return {
            "status": "success",
            "system": self.catalog.get("system_name", HERE.name),
            "bot_count": len(self.list_bots()),
            "mode": "catalog",
            "task": task or {{}},
        }}


if __name__ == "__main__":
    print(json.dumps(SystemOrchestrator().run_all(), indent=2))
'''

README = """# {name}

Self-contained DreamCo system generated from `{source}`.

- Catalog: `bots.json`
- Orchestrator: `system_orchestrator.py`
- Live financial, outreach, and production writes stay behind repo permission gates.
"""


def slug_to_system(stem: str) -> str:
    if stem.startswith("Dream") or stem in {"CommandCore", "GameTitan"}:
        return stem
    return f"Dream{stem}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="all")
    args = parser.parse_args()
    SYSTEMS.mkdir(parents=True, exist_ok=True)
    built = []
    if not APP_BOTS.exists():
        print("No App_bots directory")
        return 0
    for path in sorted(APP_BOTS.glob("*.json")):
        if path.name.startswith("masterbots"):
            continue
        name = slug_to_system(path.stem)
        dest = SYSTEMS / name
        dest.mkdir(parents=True, exist_ok=True)
        raw = json.loads(path.read_text(encoding="utf-8"))
        catalog = {
            "system_name": name,
            "source": str(path.relative_to(ROOT)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "description": f"Self-contained system package for {name}",
            "bots": raw if isinstance(raw, list) else raw.get("bots", raw),
            "orchestrator": "system_orchestrator.py",
        }
        (dest / "bots.json").write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
        (dest / "system_orchestrator.py").write_text(ORCHESTRATOR.format(name=name), encoding="utf-8")
        (dest / "README.md").write_text(README.format(name=name, source=path.relative_to(ROOT)), encoding="utf-8")
        (dest / "__init__.py").write_text(f"""System package for {name}.\n"""
, encoding="utf-8")
        built.append(name)
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": args.mode,
        "systems": built,
        "count": len(built),
    }
    (SYSTEMS / "catalog_index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(index))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
