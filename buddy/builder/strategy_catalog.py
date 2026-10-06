"""Strategy catalog. A row is a choice with a prospectus.

It does not claim a frontier model, and it does not close a missing runtime gap.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GROUPS = {
    "neural-network": ["supervised", "unsupervised", "self-supervised", "transfer", "fine-tune", "distill", "quantize", "prune", "evaluate"],
    "topology": ["map a graph", "find a hub", "find an isolated node", "keep a route", "record a missing edge"],
    "ontology": ["name a term", "define a term", "link a synonym", "record a conflict", "cite a source"],
    "learning": ["read a note", "compare two views", "keep a counterexample", "repeat a task", "measure a second pass"],
    "resources": ["bot file", "legacy profile", "course note", "model card", "benchmark row"],
}


def catalog() -> dict:
    rows = []
    for group, names in GROUPS.items():
        for name in names:
            rows.append({"group": group, "name": name, "prospectus": f"{name} is a strategy choice for {group}. It is not a completed run.", "button": name, "frontier_claim": False})
    return {"strategies": rows, "count": len(rows), "missing_runtime": True, "production_ready": 0}


def main() -> int:
    report = catalog()
    (ROOT / "reports" / "STRATEGY_CATALOG.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    links = "\n".join(f'<p><a class="btn btn-outline" href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/reports/STRATEGY_CATALOG.json">{row["group"]}: {row["name"]}</a></p>' for row in report["strategies"])
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Strategy choices | Buddy</title><link rel="stylesheet" href="styles.css?v=41"><link rel="stylesheet" href="actions.css?v=4"></head>
<body><div id="nav-placeholder"></div><script src="nav.js"></script><main class="actions-shell">
<header class="actions-header"><div><p class="actions-kicker">Choices</p><h1>{report["count"]} strategy choices</h1><p>Each button opens the prospectus. A choice is not a frontier claim, and the runtime gap is still open.</p></div></header>
<section class="actions-review">{links}</section>
</main></body></html>
'''
    (ROOT / "website" / "strategy-choices.html").write_text(html)
    print(json.dumps({"count": report["count"], "production_ready": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
