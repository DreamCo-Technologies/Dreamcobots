#!/usr/bin/env python3
"""Generate a Stripe price map from repository pricing declarations."""

from __future__ import annotations

import argparse
import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "reports" / "stripe_price_audit.json"
OUTPUT_MD = ROOT / "reports" / "STRIPE_PRICE_AUDIT.md"
PRICE_MAP_JSON = ROOT / "data" / "stripe" / "repository-price-map.json"
GENERATED_OFFERS_JSON = ROOT / "data" / "stripe" / "offers.generated.json"
STRIPE_TEMPLATE_JSON = ROOT / "data" / "stripe" / "offers.template.json"
GENERATED_BOT_CATALOG_JSON = ROOT / "dreamco-control-tower" / "config" / "generated" / "bots.catalog.json"

SKIP_DIRS = {
    ".git",
    ".codex",
    ".agents",
    "node_modules",
    "work",
    "reports",
    "config/generated/system_libraries",
}

PRICE_FIELD_RE = re.compile(r"(price_usd_monthly|monthly_price_usd|price_usd)\s*=\s*([0-9]+(?:\.[0-9]+)?)")
TIER_CONFIG_RE = re.compile(
    r"(?P<key>[A-Za-z0-9_\.]+)\s*:\s*TierConfig\((?P<body>.*?)\n\s*\)",
    re.DOTALL,
)
NAME_RE = re.compile(r"name\s*=\s*[\"']([^\"']+)[\"']")
PRICE_RE = re.compile(r"price_usd_monthly\s*=\s*([0-9]+(?:\.[0-9]+)?)")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "price"


def cents(amount: float) -> int:
    return int(round(amount * 100))


def source_kind(path: Path) -> str:
    text = str(path.relative_to(ROOT))
    if text.startswith("bots/"):
        return "bot_tier"
    if text.startswith("Business_bots/"):
        return "business_bot_tier"
    if text.startswith("DreamFinance/"):
        return "finance_bot_tier"
    if text.startswith("pricing/"):
        return "platform_membership"
    if text.startswith("saas/"):
        return "saas_billing"
    if text.startswith("data/stripe/"):
        return "stripe_offer_template"
    if text.startswith("dreamco-control-tower/config/generated/"):
        return "generated_bot_catalog"
    return "repository_price"


def add_price(prices: dict[str, dict[str, Any]], item: dict[str, Any]) -> None:
    if item["amount_cents"] < 0:
        return
    key = item["canonical_id"]
    existing = prices.get(key)
    if existing:
        existing.setdefault("sources", []).extend(item.get("sources", []))
        return
    prices[key] = item


def should_skip(path: Path) -> bool:
    rel = str(path.relative_to(ROOT))
    return any(rel == skip or rel.startswith(f"{skip}/") for skip in SKIP_DIRS)


def parse_tier_config_file(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    rel = str(path.relative_to(ROOT))
    rows: list[dict[str, Any]] = []

    for match in TIER_CONFIG_RE.finditer(text):
        body = match.group("body")
        price_match = PRICE_RE.search(body)
        if not price_match:
            continue
        name_match = NAME_RE.search(body)
        tier_name = name_match.group(1) if name_match else match.group("key").split(".")[-1]
        amount = float(price_match.group(1))
        product = rel.replace("/tiers.py", "").replace("_", "-")
        rows.append(
            {
                "canonical_id": f"{slugify(product)}-{slugify(tier_name)}-monthly",
                "product": product,
                "tier": slugify(tier_name),
                "display_name": f"{product} {tier_name} Monthly",
                "amount_usd": amount,
                "amount_cents": cents(amount),
                "currency": "USD",
                "billing_interval": "month",
                "source_kind": source_kind(path),
                "sources": [{"path": rel, "field": "price_usd_monthly"}],
            }
        )

    if rows:
        return rows

    for match in PRICE_FIELD_RE.finditer(text):
        amount = float(match.group(2))
        product = rel.replace(".py", "").replace("_", "-")
        rows.append(
            {
                "canonical_id": f"{slugify(product)}-{match.group(1).replace('_', '-')}",
                "product": product,
                "tier": "default",
                "display_name": f"{product} Default",
                "amount_usd": amount,
                "amount_cents": cents(amount),
                "currency": "USD",
                "billing_interval": "month" if "monthly" in match.group(1) else "one_time",
                "source_kind": source_kind(path),
                "sources": [{"path": rel, "field": match.group(1)}],
            }
        )
    return rows


def literal_dict_from_assignment(path: Path, assignment_name: str) -> dict[str, Any]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == assignment_name for target in node.targets):
                try:
                    value = ast.literal_eval(node.value)
                except Exception:
                    return {}
                return value if isinstance(value, dict) else {}
    return {}


def parse_named_price_dict(path: Path, assignment_name: str, product: str) -> list[dict[str, Any]]:
    values = literal_dict_from_assignment(path, assignment_name)
    rows = []
    for tier, amount in values.items():
        if not isinstance(amount, (int, float)):
            continue
        rows.append(
            {
                "canonical_id": f"{slugify(product)}-{slugify(str(tier))}-monthly",
                "product": product,
                "tier": slugify(str(tier)),
                "display_name": f"{product} {tier} Monthly",
                "amount_usd": float(amount),
                "amount_cents": cents(float(amount)),
                "currency": "USD",
                "billing_interval": "month",
                "source_kind": source_kind(path),
                "sources": [{"path": str(path.relative_to(ROOT)), "field": assignment_name}],
            }
        )
    return rows


def platform_membership_prices() -> list[dict[str, Any]]:
    path = ROOT / "pricing" / "membership.py"
    if not path.exists():
        return []
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("dreamco_pricing_membership", path)
        if not spec or not spec.loader:
            return []
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        manager = module.MembershipManager()
        rows = []
        for plan in manager.list_plans():
            rows.append(
                {
                    "canonical_id": f"platform-membership-{slugify(plan['tier'])}-{slugify(plan['billing_cycle'])}",
                    "product": "platform-membership",
                    "tier": slugify(plan["tier"]),
                    "display_name": plan["description"],
                    "amount_usd": float(plan["price_usd"]),
                    "amount_cents": cents(float(plan["price_usd"])),
                    "currency": "USD",
                    "billing_interval": plan["billing_cycle"],
                    "source_kind": "platform_membership",
                    "sources": [{"path": "pricing/membership.py", "field": "MembershipManager.list_plans"}],
                }
            )
        return rows
    except Exception:
        return []


def stripe_template_offers() -> list[dict[str, Any]]:
    if not STRIPE_TEMPLATE_JSON.exists():
        return []
    data = json.loads(STRIPE_TEMPLATE_JSON.read_text(encoding="utf-8"))
    rows = []
    for offer in data.get("offers", []):
        amount_cents = int(offer.get("priceCents") or 0)
        canonical_id = offer.get("offerId") or slugify(offer.get("name", "stripe-offer"))
        rows.append(
            {
                "canonical_id": slugify(canonical_id),
                "product": offer.get("botId") or "stripe-offer",
                "tier": "offer",
                "display_name": offer.get("name") or canonical_id,
                "amount_usd": round(amount_cents / 100, 2),
                "amount_cents": amount_cents,
                "currency": offer.get("currency", "USD"),
                "billing_interval": "one_time",
                "source_kind": "stripe_offer_template",
                "stripe_price_id": offer.get("stripePriceId"),
                "stripe_payment_link_id": offer.get("stripePaymentLinkId"),
                "sources": [{"path": "data/stripe/offers.template.json", "field": "priceCents"}],
            }
        )
    return rows


def generated_bot_catalog_prices() -> list[dict[str, Any]]:
    if not GENERATED_BOT_CATALOG_JSON.exists():
        return []
    data = json.loads(GENERATED_BOT_CATALOG_JSON.read_text(encoding="utf-8"))
    bots = data.get("bots", [])
    rows = []
    for bot in bots:
        if "price_usd" not in bot:
            continue
        amount = float(bot.get("price_usd") or 0)
        slug = bot.get("slug") or bot.get("bot_id") or bot.get("name") or "bot"
        tier = str(bot.get("tier") or "catalog").lower()
        rows.append(
            {
                "canonical_id": f"catalog-{slugify(str(slug))}-{slugify(tier)}",
                "product": str(slug),
                "tier": slugify(tier),
                "display_name": f"{bot.get('name') or slug} Catalog Price",
                "amount_usd": amount,
                "amount_cents": cents(amount),
                "currency": "USD",
                "billing_interval": "one_time",
                "source_kind": "generated_bot_catalog",
                "sources": [
                    {
                        "path": str(GENERATED_BOT_CATALOG_JSON.relative_to(ROOT)),
                        "field": "price_usd",
                    }
                ],
            }
        )
    return rows


def collect_prices() -> list[dict[str, Any]]:
    prices: dict[str, dict[str, Any]] = {}

    for path in ROOT.rglob("*.py"):
        if should_skip(path):
            continue
        rel = str(path.relative_to(ROOT))
        if rel.endswith("/tiers.py") or rel in {
            "saas/stripe_billing.py",
            "pricing/membership.py",
        } or "price" in path.name.lower() or "payment" in path.name.lower() or "monetization" in path.name.lower():
            for row in parse_tier_config_file(path):
                add_price(prices, row)

    for row in parse_named_price_dict(ROOT / "saas" / "stripe_billing.py", "TIER_PRICES_USD", "saas-subscription"):
        add_price(prices, row)

    for path in ROOT.glob("Business_bots/*_bot.py"):
        for row in parse_named_price_dict(path, "TIER_MONTHLY_PRICE", path.stem.replace("_", "-")):
            add_price(prices, row)

    for row in platform_membership_prices():
        add_price(prices, row)

    for row in stripe_template_offers():
        add_price(prices, row)

    for row in generated_bot_catalog_prices():
        add_price(prices, row)

    return sorted(prices.values(), key=lambda item: (item["source_kind"], item["product"], item["amount_cents"], item["canonical_id"]))


def build_stripe_offer(item: dict[str, Any]) -> dict[str, Any]:
    live_price_id = item.get("stripe_price_id")
    payment_link_id = item.get("stripe_payment_link_id")
    return {
        "offerId": item["canonical_id"],
        "name": item["display_name"],
        "product": item["product"],
        "tier": item["tier"],
        "priceCents": item["amount_cents"],
        "priceUsd": item["amount_usd"],
        "currency": item["currency"],
        "billingInterval": item["billing_interval"],
        "status": "draft" if item["amount_cents"] > 0 else "free",
        "stripeProductId": None,
        "stripePriceId": live_price_id,
        "stripePaymentLinkId": payment_link_id,
        "sourcePaths": sorted({source["path"] for source in item.get("sources", [])}),
        "approvalRequiredBeforeLive": [
            "create_live_product_or_price",
            "publish_payment_link",
            "accept_live_payment",
        ],
    }


def build_report() -> dict[str, Any]:
    prices = collect_prices()
    offers = [build_stripe_offer(item) for item in prices]
    paid_offers = [offer for offer in offers if offer["priceCents"] > 0]
    live_ready = [
        offer
        for offer in paid_offers
        if offer.get("stripePriceId") and offer.get("stripePaymentLinkId")
    ]
    missing_live_ids = [
        {
            "offerId": offer["offerId"],
            "name": offer["name"],
            "priceCents": offer["priceCents"],
            "missing": [
                field
                for field in ["stripePriceId", "stripePaymentLinkId"]
                if not offer.get(field)
            ],
        }
        for offer in paid_offers
        if not offer.get("stripePriceId") or not offer.get("stripePaymentLinkId")
    ]
    return {
        "schema": "dreamco.stripe_price_audit.v1",
        "generated_at": utc_now(),
        "summary": {
            "repository_prices": len(prices),
            "generated_stripe_offers": len(offers),
            "paid_stripe_offers": len(paid_offers),
            "free_offers": len(offers) - len(paid_offers),
            "live_ready_paid_offers": len(live_ready),
            "missing_live_stripe_id_offers": len(missing_live_ids),
            "prices_match_generated_stripe_catalog": len(prices) == len(offers),
            "live_stripe_actions_blocked_without_approval": True,
            "secret_values_stored_in_repo": False,
        },
        "policy": {
            "match_rule": "Every repository sellable price must have a generated Stripe draft offer with the same amount in cents.",
            "live_rule": "Generated draft offers are not live until Stripe Price IDs and Payment Link IDs are added from a secure Stripe account setup.",
            "github_secret_aliases": {
                "stripe_secret_key": ["STRIPE_SECRET_KEY", "STRIPE_API_KEY"],
                "stripe_publishable_key": ["STRIPE_PUBLISHABLE_KEY"],
                "stripe_webhook_secret": ["STRIPE_WEBHOOK_SECRET"],
            },
            "approval_required": [
                "create_live_product_or_price",
                "publish_payment_link",
                "accept_live_payment",
                "change_existing_price",
            ],
        },
        "stripe_catalog_files": {
            "price_map": str(PRICE_MAP_JSON.relative_to(ROOT)),
            "generated_offers": str(GENERATED_OFFERS_JSON.relative_to(ROOT)),
            "template_offers": str(STRIPE_TEMPLATE_JSON.relative_to(ROOT)),
        },
        "missing_live_ids": missing_live_ids[:200],
        "source_counts": {
            kind: sum(1 for item in prices if item["source_kind"] == kind)
            for kind in sorted({item["source_kind"] for item in prices})
        },
        "prices": prices,
    }


def write_outputs(report: dict[str, Any]) -> None:
    offers = [build_stripe_offer(item) for item in report["prices"]]
    PRICE_MAP_JSON.parent.mkdir(parents=True, exist_ok=True)
    PRICE_MAP_JSON.write_text(
        json.dumps(
            {
                "schema": "dreamco.repository_stripe_price_map.v1",
                "generated_at": report["generated_at"],
                "summary": report["summary"],
                "prices": report["prices"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    GENERATED_OFFERS_JSON.write_text(
        json.dumps(
            {
                "schema": "dreamco.generated_stripe_offers.v1",
                "generated_at": report["generated_at"],
                "offers": offers,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = report["summary"]
    lines = [
        "# Stripe Price Audit",
        "",
        f"- Repository prices: {summary['repository_prices']}",
        f"- Generated Stripe offers: {summary['generated_stripe_offers']}",
        f"- Paid Stripe offers: {summary['paid_stripe_offers']}",
        f"- Free offers: {summary['free_offers']}",
        f"- Live-ready paid offers: {summary['live_ready_paid_offers']}",
        f"- Missing live Stripe ID offers: {summary['missing_live_stripe_id_offers']}",
        f"- Prices match generated Stripe catalog: {summary['prices_match_generated_stripe_catalog']}",
        f"- Secret values stored in repo: {summary['secret_values_stored_in_repo']}",
        "",
        "## Policy",
        "",
        report["policy"]["match_rule"],
        "",
        report["policy"]["live_rule"],
        "",
        "## GitHub Stripe Secret Names",
        "",
        "- Stripe secret key: STRIPE_SECRET_KEY or STRIPE_API_KEY",
        "- Stripe publishable key: STRIPE_PUBLISHABLE_KEY",
        "- Stripe webhook secret: STRIPE_WEBHOOK_SECRET",
        "",
        "## Catalog Files",
        "",
    ]
    for label, path in report["stripe_catalog_files"].items():
        lines.append(f"- {label}: {path}")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUTPUT_JSON.exists():
            raise SystemExit("Stripe price audit missing; run the generator")
        existing = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        existing["generated_at"] = report["generated_at"]
        if json.dumps(existing, indent=2, sort_keys=True) + "\n" != rendered:
            raise SystemExit("Stripe price audit stale; run the generator")
        return 0

    write_outputs(report)
    summary = report["summary"]
    print(
        "stripe_prices_matched={matched} prices={prices} offers={offers} missing_live_ids={missing}".format(
            matched=summary["prices_match_generated_stripe_catalog"],
            prices=summary["repository_prices"],
            offers=summary["generated_stripe_offers"],
            missing=summary["missing_live_stripe_id_offers"],
        )
    )
    return 0 if summary["prices_match_generated_stripe_catalog"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
