#!/usr/bin/env python3
"""Fail-closed PR inventory validator; stdlib only."""
import json
from pathlib import Path
p=Path(__file__).with_name("open-pr-inventory.json")
data=json.loads(p.read_text())
prs=data["prs"]
assert data["count"]==len(prs), "count mismatch"
assert len({x["number"] for x in prs})==len(prs), "duplicate PR"
assert all(x["url"].endswith("/pull/"+str(x["number"])) for x in prs), "invalid URL"
assert all(x["status"]=="pending_individual_review" for x in prs), "unverified PR mislabeled"
print(f"Validated {len(prs)} PRs; none asserted merge-ready.")
