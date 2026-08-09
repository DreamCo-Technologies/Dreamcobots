#!/usr/bin/env python3
"""Build DreamCo's deterministic 500-method advertising benchmark catalog.

The first 50 entries preserve the concrete methods from the owner-approved plan.
The remaining 450 are systematic channel x campaign-motion extensions. Every
entry is a benchmark target, not a promise of legality, platform access, ROI or
live execution.
"""
from __future__ import annotations

import json
from pathlib import Path

SEED_METHODS = [
    ("Search", "Google SEO"), ("Search", "Bing SEO"), ("Search", "DuckDuckGo SEO"),
    ("Search", "AI search optimization"), ("Search", "Blog articles"), ("Search", "Guest blogging"),
    ("Search", "Knowledge hubs"), ("Search", "FAQs"), ("Search", "Landing pages"), ("Search", "Case studies"),
    ("Social", "LinkedIn"), ("Social", "Facebook"), ("Social", "Instagram"), ("Social", "X"),
    ("Social", "Threads"), ("Social", "TikTok"), ("Social", "Pinterest"), ("Social", "YouTube"),
    ("Social", "Reddit"), ("Social", "Discord"),
    ("Video", "Product demos"), ("Video", "Tutorials"), ("Video", "Shorts"), ("Video", "Livestreams"),
    ("Video", "Customer testimonials"), ("Video", "Podcasts"), ("Video", "Webinars"), ("Video", "Interviews"),
    ("Video", "Behind-the-scenes videos"), ("Video", "Feature announcements"),
    ("Communities", "GitHub"), ("Communities", "Hacker News"), ("Communities", "Product Hunt"),
    ("Communities", "Indie Hackers"), ("Communities", "Stack Overflow"), ("Communities", "Developer forums"),
    ("Communities", "Facebook Groups"), ("Communities", "Slack communities"), ("Communities", "Discord communities"),
    ("Communities", "Local meetups"),
    ("Partnerships", "Affiliate programs"), ("Partnerships", "Referral programs"), ("Partnerships", "Influencer partnerships"),
    ("Partnerships", "Consultants"), ("Partnerships", "Agencies"), ("Partnerships", "Universities"),
    ("Partnerships", "Startup incubators"), ("Partnerships", "Open-source collaborations"),
    ("Partnerships", "Marketplace listings"), ("Partnerships", "API integrations"),
]

CHANNELS = [
    "SEO", "AI search optimization", "content marketing", "email marketing", "cold outbound",
    "LinkedIn", "Facebook", "Instagram", "X/Threads", "TikTok", "YouTube", "Reddit", "Discord/community",
    "podcasts", "webinars", "events and trade shows", "directories and marketplaces", "associations and chambers",
    "affiliate marketing", "referral marketing", "influencer/creator partnerships", "agency/consultant partnerships",
    "public relations", "local marketing", "developer ecosystem", "open-source ecosystem", "universities/incubators",
    "government-market outreach", "nonprofit partnerships", "product-led growth"
]

MOTIONS = [
    "publish an educational guide", "publish a customer case study", "publish a comparison page",
    "publish an industry benchmark", "publish a problem-solution demo", "run a targeted awareness campaign",
    "run a lead-magnet campaign", "run a free-tool campaign", "run a live demo", "run a customer testimonial campaign",
    "run an expert thought-leadership campaign", "run a partner co-marketing campaign", "run a referral campaign",
    "run a limited pilot campaign", "run a vertical-specific campaign", "run a local/geographic campaign",
    "run an account-based campaign", "run a re-engagement campaign", "run a product-launch campaign",
    "run a measurable conversion experiment"
]

PARALLEL_BOTS = [
    "market-research-bot", "copy-creative-bot", "channel-specialist-bot", "compliance-bot",
    "sandbox-qa-bot", "analytics-bot", "sales-handoff-bot"
]


def record(n: int, channel: str, method: str, source: str) -> dict:
    return {
        "id": f"ADV-{n:03d}", "channel": channel, "method": method, "source": source,
        "owner_bot": "marketing-specialist-bot", "required_parallel_bots": PARALLEL_BOTS,
        "selection_dimensions": ["industry", "target_audience", "budget", "geography", "sales_cycle", "channel_fit", "permissions", "compliance"],
        "benchmark_dimensions": ["qualified_reach", "engagement", "lead_rate", "conversion_rate", "customer_acquisition_cost", "human_time_saved", "revenue", "compliance"],
        "status": "benchmark_target"
    }


def build_catalog() -> list[dict]:
    records = []
    seen = set()
    for channel, method in SEED_METHODS:
        key = method.casefold()
        if key not in seen:
            seen.add(key); records.append(record(len(records) + 1, channel, method, "owner_approved_seed_50"))
    for channel in CHANNELS:
        for motion in MOTIONS:
            method = f"{channel}: {motion}"
            key = method.casefold()
            if key in seen: continue
            seen.add(key); records.append(record(len(records) + 1, channel, method, "systematic_extension"))
            if len(records) == 500: return records
    raise RuntimeError(f"Only generated {len(records)} unique methods; expected 500")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "config/generated/advertising-methods-500.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    methods = build_catalog()
    payload = {
        "schema": "dreamco.advertising_methods.v2", "count": len(methods), "seed_method_count": len(SEED_METHODS),
        "selection_rule": "Buddy selects methods by target customer, industry, budget, geography, permissions, measured channel fit and compliance, then sandbox-tests before live spend/outreach.",
        "truth_rule": "These are campaign methods to test and score, not claims of guaranteed reach, legality, platform access or ROI. Real spend/outreach requires the appropriate permissions and approval.",
        "methods": methods,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "methods": len(methods), "seed_methods": len(SEED_METHODS), "output": str(out.relative_to(root))}, indent=2))


if __name__ == "__main__":
    main()
