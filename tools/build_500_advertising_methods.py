#!/usr/bin/env python3
"""Build a deterministic 500-method advertising opportunity catalog for DreamCo.

The catalog is intentionally channel-agnostic at generation time: each of 25
channels is paired with 20 reusable campaign motions. The resulting 500 records
can be filtered, scored, sandboxed and assigned to specialist bots.
"""
from __future__ import annotations

import json
from pathlib import Path

CHANNELS = [
    "SEO", "AI search optimization", "content marketing", "email marketing",
    "cold outbound", "LinkedIn", "Facebook", "Instagram", "TikTok", "YouTube",
    "Reddit", "community forums", "podcasts", "webinars", "events and trade shows",
    "directories and marketplaces", "associations and chambers", "affiliate marketing",
    "referral marketing", "partnership marketing", "public relations", "local marketing",
    "developer ecosystem", "government-market outreach", "nonprofit partnerships"
]

MOTIONS = [
    "publish an educational guide", "publish a customer case study",
    "publish a comparison page", "publish an industry benchmark",
    "publish a problem-solution demo", "run a targeted awareness campaign",
    "run a lead-magnet campaign", "run a free-tool campaign",
    "run a webinar or live demo", "run a customer testimonial campaign",
    "run a founder/expert thought-leadership campaign", "run a partner co-marketing campaign",
    "run a referral campaign", "run a limited pilot campaign",
    "run a vertical-specific campaign", "run a local/geographic campaign",
    "run an account-based campaign", "run a re-engagement campaign",
    "run a product-launch campaign", "run a measurable conversion experiment"
]


def build_catalog() -> list[dict]:
    records = []
    n = 0
    for channel in CHANNELS:
        for motion in MOTIONS:
            n += 1
            records.append({
                "id": f"ADV-{n:03d}",
                "channel": channel,
                "method": f"{channel}: {motion}",
                "owner_bot": "marketing-specialist-bot",
                "required_parallel_bots": [
                    "market-research-bot", "copy-creative-bot", "compliance-bot",
                    "sandbox-qa-bot", "analytics-bot", "sales-handoff-bot"
                ],
                "benchmark_dimensions": [
                    "qualified_reach", "engagement", "lead_rate", "conversion_rate",
                    "customer_acquisition_cost", "human_time_saved", "revenue", "compliance"
                ],
                "status": "benchmark_target"
            })
    assert len(records) == 500
    return records


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "config" / "advertising-methods-500.json"
    payload = {
        "schema": "dreamco.advertising_methods.v1",
        "count": 500,
        "truth_rule": "These are campaign methods to test and score, not claims of guaranteed reach, legality, platform access or ROI.",
        "methods": build_catalog(),
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
