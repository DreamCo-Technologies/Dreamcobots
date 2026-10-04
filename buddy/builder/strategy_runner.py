"""Strategy runner. It records a receipt and does not invent a score."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRATEGIES = ["chain of thought", "ReAct", "Reflexion", "one daily job", "concurrency", "cache", "path filter", "holdout", "counterexample", "second pass", "citation check", "permission check"]


def run(name: str, approved: bool) -> dict:
    if name not in STRATEGIES:
        raise ValueError(f"unknown strategy: {name}")
    if not approved:
        raise PermissionError("approve the run first")
    return {"strategy": name, "approved": True, "score": None, "model_called": False}


def main() -> int:
    report = {"runs": [run(name, True) for name in STRATEGIES], "winner": None}
    (ROOT / "reports" / "STRATEGY_RUNNER.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(report["runs"]), "winner": None}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
