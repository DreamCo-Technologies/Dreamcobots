#!/usr/bin/env python3
"""Publish the O*NET-aligned goal graph for GitHub Pages."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "website" / "data" / "goal-graph.json"

OCCUPATIONS = [
    {"soc": "15-1252.00", "title": "Software Developers", "division": "DreamCodeLab", "dream": "Ship software without a body shop", "middlemen": ["staffing firms"], "hubQuery": "code generation"},
    {"soc": "13-2011.00", "title": "Accountants and Auditors", "division": "DreamFinance", "dream": "See the money yourself", "middlemen": ["bookkeeping mills"], "hubQuery": "accounting"},
    {"soc": "13-1071.00", "title": "Human Resources Specialists", "division": "DreamBizLaunch", "dream": "Hire without a recruiter cut", "middlemen": ["recruiting agencies"], "hubQuery": "recruiting"},
    {"soc": "11-9141.00", "title": "Property Managers", "division": "DreamRealEstate", "dream": "Manage the property you own", "middlemen": ["property-management firms"], "hubQuery": "property management"},
    {"soc": "35-1012.00", "title": "Food Supervisors", "division": "DreamBizLaunch", "dream": "Open the shop without a restaurant consultant", "middlemen": ["restaurant gurus"], "hubQuery": "restaurant"},
    {"soc": "27-3043.00", "title": "Writers and Authors", "division": "DreamContent", "dream": "Publish the work you mean", "middlemen": ["vanity presses"], "hubQuery": "writing"},
    {"soc": "15-2051.00", "title": "Data Scientists", "division": "DreamData", "dream": "Answer from your data", "middlemen": ["BI agencies"], "hubQuery": "data science"},
    {"soc": "41-3091.00", "title": "Sales Representatives of Services", "division": "DreamSalesPro", "dream": "Sell the service you deliver", "middlemen": ["lead-gen agencies"], "hubQuery": "b2b sales"},
]


def main() -> int:
    report = {
        "schema": "dreamco.goal_graph.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "truth": "Pages catalog is not the hosted matcher. Hub cards are licenses, not downloads.",
        "occupations": OCCUPATIONS,
        "hooks": ["onet", "huggingface", "github-actions"],
        "live_stripe": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"occupations": len(OCCUPATIONS), "output": str(OUT.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
