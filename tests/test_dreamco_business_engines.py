#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from marketplace.manufacturing_exchange import RFQ, create_rfq_payload, match_rfq, nonprofit_programs
from money.buddy_hustle_engine import HustleProfile, build_bounded_execution_plan, rank
from tools.dreamco_file_converter import convert


def main() -> int:
    profile = HustleProfile(skills=("coding", "repair"), hours_per_week=15, budget=100, target_income=1000)
    ranked = rank(profile)
    assert ranked and ranked[0]["score"] > 0
    plan = build_bounded_execution_plan(profile, ranked[0]["id"], max_spend=50)
    assert plan["max_spend"] == 50 and "user_pause" in plan["stop_conditions"]

    rfq = RFQ("u1", "custom enclosure", 100, "US", "us_manufacturing", ("assembly",))
    matches = match_rfq(rfq)
    assert matches and matches[0]["requirement_coverage"] == 1.0
    payload = create_rfq_payload(rfq)
    assert payload["direct_deal"] is True and payload["human_approval_required_before_contract"] is True
    assert len(nonprofit_programs()) >= 3

    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "data.json"
        source.write_text(json.dumps([{"name": "A", "value": 1}]), encoding="utf-8")
        out = convert(str(source), "csv", tmp)
        assert out.exists() and out.read_text(encoding="utf-8").splitlines()[0] == "name,value"
    print("dreamco business engines: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
