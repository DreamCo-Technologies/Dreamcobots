#!/usr/bin/env python3
"""Generate Buddy's first-class innovation engine registry and report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.innovation import InnovationEngine, InnovationWeights


OUT_JSON = ROOT / "config" / "generated" / "buddy_innovation_engine.json"
OUT_MD = ROOT / "reports" / "BUDDY_INNOVATION_ENGINE.md"


def build_registry() -> dict:
    return {
        "schema": "dreamco.buddy_innovation_engine.v1",
        "status": "local_runtime_ready",
        "engine": "dreamco_platform/innovation/engine.py",
        "design_lenses": [
            {
                "id": lens,
                "concept": profile["concept"],
                "architecture": profile["architecture"],
                "known_risks": profile["risks"],
            }
            for lens, profile in sorted(InnovationEngine.LENSES.items())
        ],
        "modes": {
            mode: InnovationWeights.for_mode(mode).normalized()
            for mode in ("balanced", "bold", "trusted", "lean")
        },
        "recognized_constraints": sorted(InnovationEngine.CONSTRAINT_MODIFIERS),
        "execution_contract": [
            "generate six competing designs",
            "score utility, novelty, feasibility, trust, efficiency, and observability",
            "select a winner using user-selected priorities",
            "record durable execution checkpoints",
            "create a content-addressed rollback snapshot",
            "emit an implementation dependency graph",
            "block production until observed evidence and owner approval exist",
        ],
        "required_observed_checks": list(InnovationEngine.REQUIRED_OBSERVED_CHECKS),
        "integrations": [
            "Buddy Creative Studio",
            "Buddy local CLI",
            "Buddy website status sync",
            "DreamCo durable execution runtime",
            "DreamCo evolutionary ranking engine",
        ],
        "truth_boundary": {
            "design_scores": "heuristic comparison only",
            "production_claim": "forbidden until all observed checks pass",
            "live_external_action_taken": False,
        },
    }


def write_report(registry: dict) -> None:
    lines = [
        "# Buddy Innovation Engine",
        "",
        "Buddy now compares competing system designs before implementation instead of accepting the first generated idea.",
        "",
        "## Design Lenses",
        "",
    ]
    lines.extend(f"- `{item['id']}`: {item['concept']}" for item in registry["design_lenses"])
    lines.extend(["", "## Evidence Gate", ""])
    lines.extend(f"- `{item}`" for item in registry["required_observed_checks"])
    lines.extend(
        [
            "",
            "Design scores are transparent heuristics for comparing plans. They are never treated as production test evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = build_registry()
    if args.check:
        if not OUT_JSON.exists() or not OUT_MD.exists():
            raise SystemExit("Innovation registry outputs are missing. Run without --check.")
        current = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        if current != registry:
            raise SystemExit("Innovation registry is stale. Regenerate it.")
        print(json.dumps({"ok": True, "design_lenses": len(current["design_lenses"])}, indent=2))
        return 0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(registry)
    print(json.dumps({"ok": True, "output": str(OUT_JSON.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
