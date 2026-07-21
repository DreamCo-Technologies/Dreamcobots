"""Generate monthly DreamCo investor reports from registry and revenue data."""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"


def _run_registry_exports() -> str:
    script = ROOT / "tools" / "generate_master_registry_outputs.py"
    if not script.exists():
        return "Registry export tool not present; using existing data."
    result = subprocess.run(["python", str(script)], capture_output=True, text=True, check=False)
    return result.stdout or result.stderr or "Registry exports completed."


def _aggregate_revenue() -> float:
    stripe_events = REPORTS_DIR / "stripe_events.json"
    if not stripe_events.exists():
        return 0.0
    events = json.loads(stripe_events.read_text())
    return round(sum(float(event.get("amount_usd", 0)) for event in events), 2)


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    month = date.today().strftime("%Y-%m")
    output = REPORTS_DIR / f"{month}-investor-report.md"
    revenue = _aggregate_revenue()
    content = f"""# DreamCo Investor Report — {month}

## Executive Summary
- Registry refresh: {_run_registry_exports().strip()}
- Total recognized revenue: ${revenue:,.2f}
- Report generated from bot profiles and financial event history.

## Bot Fleet Stats
- Bot profiles indexed: {len(list((ROOT / 'bots').glob('*/bot_profile.json')))}
- Prospectus pages available in `docs/prospectus/`
- Platform workflows include compliance, performance, and sandbox governance.

## Revenue
- Aggregated Stripe revenue observed this month: ${revenue:,.2f}
- Benchmark and chaos reports are stored in `reports/` for investor due diligence.
- Revenue quality improves when benchmark and chaos regressions stay within gates.

## Growth
- New prospectus generation and marketplace search increase discovery for monetizable bots.
- Sandbox promotion gates protect revenue quality before bots move to production.
- KPI APIs expose ARR, MRR, and division performance to investor-facing dashboards.

## Roadmap
- Deepen pgvector search coverage across registry, memory, and marketplace surfaces.
- Expand live revenue attribution and leak detection across all enterprise bots.
- Continue Next.js migration work for Empire OS marketplace experiences.
"""
    output.write_text(content)
    print(output)


if __name__ == "__main__":
    main()
