"""Beginner AI term list. A row is a definition, not a trained model."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TERMS = {
    "model": "A program that guesses the next answer from examples.",
    "training": "Showing a model examples so it can adjust.",
    "self-training": "A model using its own checked notes. It stays off until you allow it.",
    "fine-tune": "A small extra lesson on a model that already exists.",
    "prompt": "The instruction you type.",
    "token": "A small piece of text the model counts.",
    "context": "The notes the model can see for this turn.",
    "weight": "A stored number inside a model. Download only if you choose it.",
    "open weight": "A model whose numbers can be downloaded.",
    "closed model": "A model you call through an account.",
    "benchmark": "The same task run again so the score can be compared.",
    "success rate": "Finished runs divided by started runs.",
    "latency": "How long a run took. Use the median.",
    "overfit": "The model memorized the practice set and misses a new example.",
    "hallucination": "A confident answer that is not supported.",
    "citation": "The source attached to a claim.",
    "permission": "Your yes before a site, a file, or a secret is used.",
    "sandbox": "A practice run that does not change the live system.",
    "router": "The piece that picks a model for a task.",
    "ontology": "A list of terms and how they relate.",
    "topology": "The shape of a network: what connects to what.",
    "neural network": "A stack of simple number steps that learn a pattern.",
    "architecture search": "Trying model shapes. Run only if you press Run.",
    "distill": "Teaching a smaller model from a larger one's answers.",
    "quantize": "Storing the numbers with less precision to make them smaller.",
    "evaluate": "Checking the answer against a known case.",
    "counterexample": "A case that shows the claim does not always hold.",
    "rollback": "A way to undo a change.",
    "telemetry": "A record that a run happened, without the secret.",
    "production ready": "Adapter, sandbox, auth, and telemetry exist. A file is not enough.",
}


def catalog() -> dict:
    rows = [{"term": term, "plain": text, "safe": "Do not treat this as a completed run.", "button": term} for term, text in TERMS.items()]
    return {"terms": rows, "count": len(rows), "self_training_started": False, "frontier_claim": False}


def main() -> int:
    report = catalog()
    (ROOT / "reports" / "AI_TERMS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    links = "\n".join(f'<p><a class="btn btn-outline" href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/reports/AI_TERMS.json">{row["term"]}</a> {row["plain"]}</p>' for row in report["terms"])
    html = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>AI terms | Buddy</title><link rel="stylesheet" href="styles.css?v=41"><link rel="stylesheet" href="actions.css?v=4"></head>
<body><div id="nav-placeholder"></div><script src="nav.js"></script><main class="actions-shell">
<header class="actions-header"><div><p class="actions-kicker">Beginner</p><h1>{report["count"]} AI terms</h1><p>Each button opens the downloadable list. Self-training is off. This is not a frontier model.</p></div></header>
<section class="actions-review"><p><a class="btn btn-primary" href="https://github.com/DreamCo-Technologies/Dreamcobots/blob/main/reports/AI_TERMS.json">Download the term list</a></p>{links}</section>
</main></body></html>
'''
    (ROOT / "website" / "ai-terms.html").write_text(html)
    print(json.dumps({"count": report["count"], "self_training_started": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
