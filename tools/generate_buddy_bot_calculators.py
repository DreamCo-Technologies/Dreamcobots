#!/usr/bin/env python3
"""Generate a safe interactive calculator contract for every Buddy bot profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "config" / "master_bot_registry.json"
DIVISION_FORMULAS = ROOT / "shared" / "division-formulas.ts"
CONFIG_OUT = ROOT / "config" / "generated" / "bot_calculators.json"
WEB_OUT = ROOT / "website" / "data" / "bot-calculators.json"
REPORT_OUT = ROOT / "reports" / "BOT_CALCULATORS.md"


def field(key: str, label: str, unit: str, default: float, maximum: float, step: float = 1) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "unit": unit,
        "default": default,
        "min": 0,
        "max": maximum,
        "step": step,
    }


TEMPLATES: dict[str, dict[str, Any]] = {
    "real_estate_flip": {
        "name": "Real Estate Deal",
        "inputs": [
            field("purchase_price", "Purchase price", "currency", 180000, 1000000000, 1000),
            field("repair_costs", "Repair costs", "currency", 35000, 100000000, 500),
            field("after_repair_value", "After-repair value", "currency", 290000, 1000000000, 1000),
            field("holding_cost_monthly", "Monthly holding cost", "currency", 1800, 10000000, 100),
            field("holding_months", "Holding months", "months", 4, 240, 1),
            field("selling_costs", "Selling and financing costs", "currency", 18000, 100000000, 500),
        ],
        "outputs": [("maximum_offer", "70% maximum offer", "currency"), ("total_cost", "Total cost", "currency"), ("net_value", "Estimated net profit", "currency"), ("roi", "Estimated ROI", "percent")],
    },
    "car_flip": {
        "name": "Vehicle Flip",
        "inputs": [
            field("purchase_price", "Purchase price", "currency", 8500, 10000000, 100),
            field("repair_costs", "Repair and reconditioning", "currency", 1200, 1000000, 50),
            field("transport_costs", "Transport costs", "currency", 300, 1000000, 25),
            field("fees", "Taxes and selling fees", "currency", 400, 1000000, 25),
            field("sale_price", "Expected sale price", "currency", 13500, 10000000, 100),
        ],
        "outputs": [("total_cost", "All-in cost", "currency"), ("net_value", "Estimated net profit", "currency"), ("roi", "Estimated ROI", "percent"), ("margin", "Estimated margin", "percent")],
    },
    "commerce_margin": {
        "name": "Commerce Margin",
        "inputs": [
            field("units", "Units", "number", 100, 100000000, 1),
            field("sale_price", "Sale price per unit", "currency", 45, 10000000, 0.01),
            field("unit_cost", "Cost per unit", "currency", 18, 10000000, 0.01),
            field("fees", "Platform and operating fees", "currency", 350, 100000000, 1),
            field("marketing_cost", "Marketing cost", "currency", 500, 100000000, 1),
            field("return_rate", "Return or waste rate", "percent", 5, 100, 0.1),
        ],
        "outputs": [("gross_value", "Gross revenue", "currency"), ("total_cost", "Estimated total cost", "currency"), ("net_value", "Estimated net value", "currency"), ("margin", "Estimated margin", "percent"), ("break_even_units", "Break-even units", "number")],
    },
    "sales_funnel": {
        "name": "Sales Funnel",
        "inputs": [
            field("leads", "Qualified leads", "number", 250, 100000000, 1),
            field("conversion_rate", "Conversion rate", "percent", 8, 100, 0.1),
            field("average_value", "Average customer value", "currency", 500, 100000000, 1),
            field("campaign_cost", "Campaign and sales cost", "currency", 3500, 1000000000, 1),
        ],
        "outputs": [("converted", "Estimated customers", "number"), ("gross_value", "Estimated gross value", "currency"), ("cost_per_acquisition", "Cost per acquisition", "currency"), ("net_value", "Estimated net value", "currency"), ("roi", "Estimated ROI", "percent")],
    },
    "cash_flow": {
        "name": "Cash Flow",
        "inputs": [
            field("initial_investment", "Initial investment", "currency", 10000, 1000000000, 100),
            field("opening_cash", "Opening cash reserve", "currency", 25000, 1000000000, 100),
            field("monthly_income", "Monthly income", "currency", 8000, 1000000000, 100),
            field("monthly_expense", "Monthly expense", "currency", 5000, 1000000000, 100),
            field("months", "Projection months", "months", 12, 1200, 1),
        ],
        "outputs": [("total_inflow", "Projected inflow", "currency"), ("total_outflow", "Projected outflow", "currency"), ("net_value", "Projected net cash", "currency"), ("roi", "Estimated ROI", "percent"), ("runway", "Opening-cash runway", "months")],
    },
    "software_unit_economics": {
        "name": "Software Unit Economics",
        "inputs": [
            field("users", "Paying users", "number", 100, 100000000, 1),
            field("monthly_price", "Monthly price per user", "currency", 25, 10000000, 0.01),
            field("variable_cost", "Variable cost per user", "currency", 3, 10000000, 0.01),
            field("fixed_cost", "Fixed monthly cost", "currency", 900, 1000000000, 1),
            field("build_cost", "Build and launch cost", "currency", 12000, 1000000000, 100),
            field("months", "Projection months", "months", 12, 1200, 1),
        ],
        "outputs": [("monthly_revenue", "Monthly recurring revenue", "currency"), ("monthly_net", "Monthly contribution", "currency"), ("payback", "Build-cost payback", "months"), ("net_value", "Projected period value", "currency"), ("roi", "Estimated ROI", "percent")],
    },
    "risk_reduction": {
        "name": "Risk Reduction",
        "inputs": [
            field("events", "Exposures or events", "number", 100, 100000000, 1),
            field("baseline_probability", "Baseline incident probability", "percent", 12, 100, 0.1),
            field("residual_probability", "Expected residual probability", "percent", 5, 100, 0.1),
            field("average_loss", "Average impact per incident", "currency", 2000, 1000000000, 1),
            field("mitigation_cost", "Mitigation cost", "currency", 7500, 1000000000, 1),
        ],
        "outputs": [("baseline_risk", "Baseline expected loss", "currency"), ("residual_risk", "Residual expected loss", "currency"), ("avoided_loss", "Estimated avoided loss", "currency"), ("net_value", "Net risk-reduction value", "currency"), ("roi", "Estimated mitigation ROI", "percent")],
    },
    "learning_outcomes": {
        "name": "Learning Outcomes",
        "inputs": [
            field("learners", "Learners", "number", 100, 100000000, 1),
            field("completion_rate", "Expected completion rate", "percent", 75, 100, 0.1),
            field("improvement_rate", "Measured outcome improvement", "percent", 20, 100, 0.1),
            field("value_per_learner", "Value per improved learner", "currency", 250, 100000000, 1),
            field("program_cost", "Program cost", "currency", 10000, 1000000000, 1),
        ],
        "outputs": [("completers", "Estimated completers", "number"), ("gross_value", "Outcome-adjusted value", "currency"), ("cost_per_completion", "Cost per completion", "currency"), ("net_value", "Estimated net value", "currency"), ("roi", "Estimated ROI", "percent")],
    },
    "project_estimate": {
        "name": "Project Estimate",
        "inputs": [
            field("units", "Tasks, rooms, or work units", "number", 20, 100000000, 1),
            field("hours_per_unit", "Hours per unit", "hours", 3, 100000, 0.1),
            field("hourly_cost", "Labor cost per hour", "currency", 45, 1000000, 0.01),
            field("materials", "Materials and direct costs", "currency", 4000, 1000000000, 1),
            field("contingency_rate", "Contingency", "percent", 12, 100, 0.1),
        ],
        "outputs": [("labor_hours", "Estimated labor hours", "hours"), ("labor_cost", "Estimated labor cost", "currency"), ("subtotal", "Estimate subtotal", "currency"), ("contingency", "Contingency reserve", "currency"), ("total_cost", "Recommended project budget", "currency")],
    },
    "operations_efficiency": {
        "name": "Operations Efficiency",
        "inputs": [
            field("items", "Items or transactions", "number", 1000, 1000000000, 1),
            field("minutes_per_item", "Minutes per item", "minutes", 8, 100000, 0.1),
            field("time_reduction", "Expected time reduction", "percent", 25, 100, 0.1),
            field("error_rate", "Current error rate", "percent", 4, 100, 0.1),
            field("cost_per_error", "Cost per error", "currency", 35, 100000000, 1),
            field("hourly_value", "Labor value per hour", "currency", 30, 1000000, 0.01),
            field("tool_cost", "Tool or process cost", "currency", 1500, 1000000000, 1),
        ],
        "outputs": [("baseline_hours", "Baseline labor hours", "hours"), ("hours_saved", "Estimated hours saved", "hours"), ("labor_value", "Estimated labor value", "currency"), ("error_cost", "Current error-cost exposure", "currency"), ("net_value", "Estimated net value", "currency")],
    },
    "creative_project": {
        "name": "Creative Production",
        "inputs": [
            field("units", "Scenes, assets, or production units", "number", 12, 10000000, 1),
            field("hours_per_unit", "Hours per unit", "hours", 6, 100000, 0.1),
            field("hourly_cost", "Production cost per hour", "currency", 50, 1000000, 0.01),
            field("asset_cost", "Rights and asset cost", "currency", 2500, 1000000000, 1),
            field("distribution_cost", "Distribution and promotion", "currency", 1500, 1000000000, 1),
            field("expected_revenue", "Conservative expected revenue", "currency", 12000, 1000000000, 100),
        ],
        "outputs": [("labor_hours", "Production hours", "hours"), ("total_cost", "Estimated production cost", "currency"), ("break_even", "Break-even revenue", "currency"), ("net_value", "Estimated net value", "currency"), ("roi", "Estimated ROI", "percent")],
    },
    "research_value": {
        "name": "Research and Decision Value",
        "inputs": [
            field("decisions", "Decisions or deliverables supported", "number", 10, 100000000, 1),
            field("hours_saved", "Hours saved", "hours", 30, 10000000, 0.1),
            field("hourly_value", "Value per hour", "currency", 60, 1000000, 0.01),
            field("avoided_cost", "Conservative avoided cost", "currency", 3000, 1000000000, 1),
            field("tool_cost", "Research and tool cost", "currency", 1000, 1000000000, 1),
        ],
        "outputs": [("time_value", "Time value", "currency"), ("gross_value", "Estimated gross value", "currency"), ("net_value", "Estimated net value", "currency"), ("value_per_decision", "Value per decision", "currency"), ("roi", "Estimated ROI", "percent")],
    },
    "subscription": {
        "name": "Subscription Economics",
        "inputs": [
            field("subscribers", "Subscribers", "number", 250, 100000000, 1),
            field("monthly_price", "Monthly price", "currency", 19, 10000000, 0.01),
            field("monthly_churn", "Monthly churn", "percent", 4, 100, 0.1),
            field("variable_cost", "Variable cost per subscriber", "currency", 3, 1000000, 0.01),
            field("fixed_cost", "Fixed monthly cost", "currency", 1200, 1000000000, 1),
        ],
        "outputs": [("monthly_revenue", "Monthly recurring revenue", "currency"), ("monthly_net", "Monthly contribution", "currency"), ("annual_net", "Annualized contribution", "currency"), ("churned", "Estimated monthly churned users", "number"), ("contribution_ltv", "Estimated contribution LTV", "currency")],
    },
}


DIVISION_DEFAULTS = {
    "DreamRealEstate": "real_estate_flip",
    "DreamRetail": "commerce_margin", "DreamTrade": "commerce_margin", "DreamMarket": "commerce_margin",
    "DreamAgriculture": "commerce_margin", "DreamFood": "commerce_margin",
    "DreamSalesPro": "sales_funnel", "DreamInfluence": "sales_funnel", "DreamSocial": "sales_funnel",
    "DreamContent": "creative_project", "DreamCustIntel": "sales_funnel",
    "DreamFinance": "cash_flow", "DreamEntFinance": "cash_flow", "DreamLoans": "cash_flow",
    "DreamPayments": "cash_flow", "DreamCrypto": "cash_flow", "DreamBizLaunch": "cash_flow",
    "DreamCodeLab": "software_unit_economics", "DreamAIInfra": "software_unit_economics",
    "DreamAutomation": "operations_efficiency", "DreamAgents": "software_unit_economics",
    "DreamCyber": "risk_reduction", "DreamLegal": "risk_reduction", "DreamProtection": "risk_reduction",
    "DreamHealth": "risk_reduction", "DreamMilitary": "risk_reduction",
    "DreamEducation": "learning_outcomes",
    "DreamConstruction": "project_estimate", "DreamMaintenance": "project_estimate",
    "DreamTransport": "operations_efficiency", "DreamProduction": "operations_efficiency",
    "DreamProServices": "project_estimate", "DreamAdmin": "operations_efficiency",
    "DreamOps": "operations_efficiency", "DreamFlow": "operations_efficiency",
    "DreamArts": "creative_project", "GameTitan": "creative_project",
    "DreamPersonalCare": "subscription",
}


def read_division_formula_references() -> dict[str, list[dict[str, Any]]]:
    text = DIVISION_FORMULAS.read_text(encoding="utf-8")
    starts = list(re.finditer(r"^  ([A-Za-z][A-Za-z0-9]+): \[$", text, re.MULTILINE))
    references: dict[str, list[dict[str, Any]]] = {}
    entry = re.compile(
        r'\{ id: (\d+), name: "((?:[^"\\]|\\.)*)", formula: "((?:[^"\\]|\\.)*)", description: "((?:[^"\\]|\\.)*)" \}'
    )
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        rows = []
        for item in entry.finditer(text[match.end():end]):
            rows.append({
                "id": int(item.group(1)),
                "name": item.group(2).replace('\\"', '"'),
                "formula": item.group(3).replace('\\"', '"'),
                "description": item.group(4).replace('\\"', '"'),
                "execution": "reference_only_not_evaluated",
            })
        references[match.group(1)] = rows
    return references


def template_for(bot: dict[str, Any]) -> str:
    identity = bot["identity"]
    capability_text = " ".join(item["name"] for item in bot.get("capabilities", []))
    text = f"{identity['slug']} {identity['display_name']} {identity['category']} {capability_text}".lower()
    if "car" in text and any(word in text for word in ("flip", "resale", "vehicle")):
        return "car_flip"
    if identity["division"] == "DreamRealEstate":
        return "real_estate_flip"
    keyword_rules = [
        (("subscription", "membership", "churn", "retention"), "subscription"),
        (("lead", "sales", "conversion", "campaign", "marketing", "advertis"), "sales_funnel"),
        (("student", "education", "learning", "course", "curriculum", "training"), "learning_outcomes"),
        (("security", "legal", "risk", "compliance", "safety", "health", "medical"), "risk_reduction"),
        (("construction", "estimate", "maintenance", "repair", "contractor"), "project_estimate"),
        (("inventory", "logistics", "transport", "production", "manufactur", "workflow", "operations"), "operations_efficiency"),
        (("game", "music", "video", "film", "artist", "creative", "design"), "creative_project"),
        (("software", "code", "api", "website", "app builder", "developer", "agent"), "software_unit_economics"),
    ]
    for words, template_id in keyword_rules:
        if any(word in text for word in words):
            return template_id
    return DIVISION_DEFAULTS.get(identity["division"], "research_value")


def build_registry() -> dict[str, Any]:
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    references = read_division_formula_references()
    division_indexes: Counter[str] = Counter()
    calculators = []
    for bot in master["bots"]:
        identity = bot["identity"]
        division = identity["division"]
        index = division_indexes[division]
        division_indexes[division] += 1
        template_id = template_for(bot)
        template = TEMPLATES[template_id]
        division_rows = references.get(division, [])
        assigned_reference = division_rows[index % len(division_rows)] if division_rows else {
            "id": None,
            "name": f"{identity['display_name']} outcome efficiency",
            "formula": "NetValue = GrossOutcomeValue - TotalApprovedCost",
            "description": "Fallback planning reference for a division without a legacy formula set.",
            "execution": "reference_only_not_evaluated",
        }
        capability = bot.get("capabilities", [{}])[0].get("name", identity["category"])
        fingerprint = hashlib.sha256(
            f"{identity['slug']}:{template_id}:{assigned_reference['name']}".encode("utf-8")
        ).hexdigest()[:16]
        calculators.append({
            "schema": "dreamco.bot_calculator.v1",
            "calculator_id": f"calculator-{identity['slug']}",
            "fingerprint": fingerprint,
            "bot": {
                "slug": identity["slug"],
                "display_name": identity["display_name"],
                "division": division,
                "category": identity["category"],
                "emoji": bot["logo"]["emoji"],
            },
            "name": f"{identity['display_name']} {template['name']} Calculator",
            "objective": f"Estimate the measurable value, cost, or outcome of {capability.lower()} using user-provided assumptions.",
            "template_id": template_id,
            "inputs": template["inputs"],
            "outputs": [
                {"key": key, "label": label, "unit": unit}
                for key, label, unit in template["outputs"]
            ],
            "assigned_division_formula": assigned_reference,
            "engine": {
                "status": "local_interactive_ready",
                "source": "website/calculator-engine.js",
                "network_required": False,
                "arbitrary_expression_evaluation": False,
            },
            "guardrails": [
                "planning estimate only",
                "show assumptions and never guarantee profit or outcomes",
                "do not use as legal, tax, lending, investment, medical, or safety advice",
                "live transactions require separate owner approval",
            ],
            "links": {
                "calculator": f"calculator.html?bot={identity['slug']}",
                "buddy": f"buddy.html?bot={identity['slug']}",
                "prospectus": f"bots.html?prospectus={identity['slug']}",
            },
        })
    template_counts = Counter(item["template_id"] for item in calculators)
    return {
        "schema": "dreamco.bot_calculator_registry.v1",
        "truth_policy": {
            "calculator": "A deterministic local planning calculator with bounded numeric inputs.",
            "assigned_division_formula": "A research reference displayed for the bot; it is not executed as code.",
            "result": "An estimate from user-entered assumptions, not verified revenue, advice, or a guarantee.",
        },
        "summary": {
            "calculators": len(calculators),
            "unique_calculator_ids": len({item["calculator_id"] for item in calculators}),
            "bots_covered": len({item["bot"]["slug"] for item in calculators}),
            "divisions_covered": len({item["bot"]["division"] for item in calculators}),
            "interactive_local_calculators": sum(item["engine"]["status"] == "local_interactive_ready" for item in calculators),
            "calculator_templates": len(TEMPLATES),
            "legacy_division_formula_references": sum(len(rows) for rows in references.values()),
        },
        "template_counts": dict(sorted(template_counts.items())),
        "calculators": calculators,
    }


def build_report(registry: dict[str, Any]) -> str:
    summary = registry["summary"]
    lines = [
        "# Buddy Bot Calculator Registry",
        "",
        "Every cataloged Buddy bot has a unique local calculator contract and public calculator route.",
        "",
        "## Coverage",
        "",
        f"- Calculators: {summary['calculators']:,}",
        f"- Unique calculator ids: {summary['unique_calculator_ids']:,}",
        f"- Bots covered: {summary['bots_covered']:,}",
        f"- Divisions covered: {summary['divisions_covered']}",
        f"- Safe interactive templates: {summary['calculator_templates']}",
        f"- Legacy division formula references: {summary['legacy_division_formula_references']:,}",
        "",
        "## Runtime Contract",
        "",
        "The public engine uses explicit calculator functions and bounded numeric inputs. It never evaluates formula text or arbitrary user code. Results are planning estimates and do not guarantee revenue, approval, safety, or legal compliance.",
        "",
        "## Template Coverage",
        "",
    ]
    lines.extend(f"- `{name}`: {count:,} bots" for name, count in registry["template_counts"].items())
    return "\n".join(lines) + "\n"


def stable_json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = build_registry()
    expected_json = stable_json(registry)
    expected_report = build_report(registry)
    if args.check:
        for path, expected in ((CONFIG_OUT, expected_json), (WEB_OUT, expected_json), (REPORT_OUT, expected_report)):
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                raise SystemExit(f"Generated output is stale: {path.relative_to(ROOT)}")
        print(json.dumps({"ok": True, **registry["summary"]}, indent=2))
        return 0
    for path in (CONFIG_OUT, WEB_OUT, REPORT_OUT):
        path.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_OUT.write_text(expected_json, encoding="utf-8")
    WEB_OUT.write_text(expected_json, encoding="utf-8")
    REPORT_OUT.write_text(expected_report, encoding="utf-8")
    print(json.dumps({"ok": True, **registry["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
