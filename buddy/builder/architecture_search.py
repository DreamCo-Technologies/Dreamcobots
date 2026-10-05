"""Architecture search choices and missing runtime data.

A method is a choice. Run is off until the user opts in. Missing runtime
fields stay missing until a real run writes them.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METHODS = ["random search", "grid search", "Bayesian optimization", "evolutionary search", "reinforcement search", "differentiable search", "one-shot search", "weight sharing", "early stop", "human review"]
REQUIRED = ["success_rate", "median_latency_ms", "median_model_calls", "adapter", "sandbox_run", "auth", "telemetry"]


def choose(method: str, run: bool) -> dict:
    if method not in METHODS:
        raise ValueError(f"unknown method: {method}")
    return {"method": method, "run": run, "started": False, "frontier_claim": False}


def missing(row: dict) -> list[str]:
    return [name for name in REQUIRED if row.get(name) in (None, "", False)]


def main() -> int:
    report = {"methods": [choose(method, False) for method in METHODS], "missing_runtime": REQUIRED, "production_ready": 0, "frontier_claim": False}
    (ROOT / "reports" / "ARCHITECTURE_SEARCH.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    links = "\n".join(f'<p><button class="btn btn-outline" type="button" data-method="{method}">Run {method}</button> <button class="btn btn-outline" type="button" data-skip="{method}">Skip {method}</button></p>' for method in METHODS)
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Architecture search | Buddy</title><link rel="stylesheet" href="styles.css?v=41"><link rel="stylesheet" href="actions.css?v=4"></head>
<body><div id="nav-placeholder"></div><script src="nav.js"></script><main class="actions-shell">
<header class="actions-header"><div><p class="actions-kicker">Choice</p><h1>Architecture search</h1><p>Run is off until you press it. This is not a frontier model.</p></div></header>
<section class="actions-review"><p><a class="btn btn-primary" href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/reports/ARCHITECTURE_SEARCH.json">Download the resource</a></p>{links}<p id="search-status">No method selected.</p></section>
</main>
<script>
document.querySelectorAll("[data-method]").forEach((button) => button.addEventListener("click", () => {{ localStorage.setItem("dreamco.architecture-search", button.dataset.method); document.getElementById("search-status").textContent = "Run selected for " + button.dataset.method + ". Not started."; }}));
document.querySelectorAll("[data-skip]").forEach((button) => button.addEventListener("click", () => {{ document.getElementById("search-status").textContent = "Skipped " + button.dataset.skip + "."; }}));
</script>
</body></html>
'''
    (ROOT / "website" / "architecture-search.html").write_text(html)
    print(json.dumps({"methods": len(METHODS), "missing": len(REQUIRED)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
