#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "buddy-government-operating-system.json").read_text(encoding="utf-8"))
OUT = ROOT / "config" / "generated" / "government-needs-spending-watch.json"

USA_AGENCIES = "https://api.usaspending.gov/api/v2/references/toptier_agencies/"
GRANTS_SEARCH = "https://api.grants.gov/v1/api/search2"
SAM_SEARCH = "https://api.sam.gov/opportunities/v2/search"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "DreamCo-Buddy-Government-Watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "DreamCo-Buddy-Government-Watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    sources = []
    signals = []
    failures = []

    try:
        doc = get_json(USA_AGENCIES)
        rows = doc.get("results", [])
        sources.append({"id": "usa_spending", "status": "runtime_verified", "records": len(rows), "tested_at": now})
        for row in rows:
            signals.append({
                "signal_type": "federal_agency_spending",
                "agency": row.get("agency_name"),
                "abbreviation": row.get("abbreviation"),
                "fiscal_year": row.get("active_fy"),
                "fiscal_quarter": row.get("active_fq"),
                "outlay_amount": row.get("outlay_amount"),
                "obligated_amount": row.get("obligated_amount"),
                "budget_authority_amount": row.get("budget_authority_amount"),
                "source": "USAspending.gov",
                "status": "evidence_only_not_need_conclusion"
            })
    except Exception as exc:
        failures.append({"source": "usa_spending", "error": str(exc)})

    try:
        doc = post_json(GRANTS_SEARCH, {"keyword": "", "oppStatuses": "forecasted|posted", "rows": 100})
        hits = doc.get("data", {}).get("oppHits", []) or doc.get("oppHits", []) or []
        sources.append({"id": "grants_gov", "status": "runtime_verified", "records": len(hits), "tested_at": now})
        for row in hits[:100]:
            signals.append({
                "signal_type": "federal_grant_opportunity",
                "title": row.get("title"),
                "agency": row.get("agency"),
                "number": row.get("number") or row.get("oppNumber"),
                "open_date": row.get("openDate"),
                "close_date": row.get("closeDate"),
                "source": "Grants.gov",
                "status": "requires_fit_analysis"
            })
    except Exception as exc:
        failures.append({"source": "grants_gov", "error": str(exc)})

    api_key = os.environ.get("SAM_API_KEY")
    if api_key:
        try:
            today = datetime.now().strftime("%m/%d/%Y")
            query = urllib.parse.urlencode({"limit": 100, "api_key": api_key, "postedFrom": "01/01/2026", "postedTo": today})
            doc = get_json(f"{SAM_SEARCH}?{query}")
            hits = doc.get("opportunitiesData", [])
            sources.append({"id": "sam_opportunities", "status": "runtime_verified", "records": len(hits), "tested_at": now})
            for row in hits:
                signals.append({
                    "signal_type": "federal_contract_opportunity",
                    "notice_id": row.get("noticeId"),
                    "title": row.get("title"),
                    "solicitation_number": row.get("solicitationNumber"),
                    "department": row.get("department"),
                    "sub_tier": row.get("subTier"),
                    "office": row.get("office"),
                    "posted_date": row.get("postedDate"),
                    "source": "SAM.gov",
                    "status": "requires_fit_analysis"
                })
        except Exception as exc:
            failures.append({"source": "sam_opportunities", "error": str(exc)})
    else:
        sources.append({"id": "sam_opportunities", "status": "credentials_required", "records": 0, "tested_at": now})

    payload = {
        "schema": "dreamco.government_needs_spending_watch.v1",
        "generated_at": now,
        "source_status": sources,
        "signal_count": len(signals),
        "signals": signals,
        "failures": failures,
        "gap_team": CFG["gap_team"],
        "needs_scoring": CFG["needs_scoring"],
        "interpretation_rule": "Spending, grants and contract notices are evidence of government activity or demand, not proof that DreamCo can win work or that spending is wasteful. Every opportunity needs current-source verification, fit analysis, requirements, cost, risk and approval review.",
        "truth_boundary": CFG["truth_rule"]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "signals": len(signals), "failures": len(failures), "output": str(OUT.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
