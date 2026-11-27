#!/usr/bin/env python3
"""Deterministic, auditable PR integration workstream report. No merges or network calls."""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RULES = {
 "security_and_access": r"security|auth|identity|allowlist|permission|safety|fail.closed|approval",
 "ci_and_production": r"ci|actions|workflow|production|readiness|evidence gate|keep green|recovery|self.fix|preflight|deps|bump|encoding",
 "training_and_models": r"train|model|benchmark|hugging.face|hf|distill|teacher|bootcamp|curriculum|tokeniz|learning",
 "bots_and_agents": r"bot|agent|capability|fleet|division|masterbot|task|specialist",
 "pages_and_ui": r"pages|website|homepage|navigation|dashboard|portal|console|control.plane|workbench|hub",
 "business_and_payments": r"money|revenue|payment|income|merchant|invention",
}
def classify(title):
    return sorted(k for k, pat in RULES.items() if re.search(pat, title, re.I)) or ["manual_triage"]

def build(data):
    prs = data["prs"]
    if len(prs) != data["count"] or len({p["number"] for p in prs}) != len(prs):
        raise ValueError("incomplete or duplicated PR inventory")
    groups = defaultdict(list)
    for p in prs:
        for group in classify(p["title"]):
            groups[group].append(p["number"])
    return {
        "inventory_count": len(prs),
        "classified_count": len({n for nums in groups.values() for n in nums}),
        "workstreams": dict(sorted(groups.items())),
        "merge_policy": "NO_AUTO_MERGE: require diff inspection, required checks, security review, production isolation, and owner approvals",
        "note": "Classification is title-only triage, not code review, integration, test, or readiness evidence.",
    }

if __name__ == "__main__":
    data = json.loads((ROOT / "open-pr-inventory.json").read_text())
    report = build(data)
    assert report["inventory_count"] == report["classified_count"]
    out = ROOT / "open-pr-workstreams.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Classified {report['classified_count']} PRs into {len(report['workstreams'])} workstreams; no merges.")
