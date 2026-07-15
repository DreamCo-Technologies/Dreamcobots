#!/usr/bin/env python3
"""Generate owner approval packets for production-gated high-risk bots."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APPROVAL_FILE = ROOT / "config" / "production_approvals" / "high_risk_bot_approvals.json"
SMOKE_REPORT = ROOT / "reports" / "generated_bot_smoke_results.json"
OUTPUT_JSON = ROOT / "reports" / "production_approval_packets.json"
OUTPUT_MD = ROOT / "reports" / "PRODUCTION_APPROVAL_PACKETS.md"


LIVE_ACTIONS_BY_RISK = {
    "money_movement": [
        "prepare_invoice_or_checkout_draft",
        "send_payment_link_after_user_confirmation",
        "record_payment_status_from_webhook",
    ],
    "financial_or_trading": [
        "run_market_analysis",
        "prepare_trade_recommendation_for_review",
        "simulate_strategy_without_live_order",
    ],
    "credit_or_loans": [
        "compare_loan_options",
        "prepare_application_checklist",
        "route_to_human_review_before_submission",
    ],
    "legal_or_tax": [
        "prepare_research_summary",
        "draft_review_checklist",
        "route_to_licensed_professional_review",
    ],
    "health_or_medical": [
        "prepare_visit_summary",
        "collect_intake_information",
        "route_to_clinician_or_emergency_guidance",
    ],
    "security_or_defense": [
        "run_authorized_local_scan",
        "prepare_remediation_plan",
        "block_third_party_action_without_written_authorization",
    ],
    "fraud_or_compliance": [
        "flag_risk_for_review",
        "prepare_audit_packet",
        "block_enforcement_action_without_human_approval",
    ],
}


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def allowed_actions_for(entry: dict[str, Any]) -> list[str]:
    actions: list[str] = []
    for reason in entry.get("risk_reasons", []):
        actions.extend(LIVE_ACTIONS_BY_RISK.get(reason, ["prepare_review_packet"]))
    deduped = []
    for action in actions:
        if action not in deduped:
            deduped.append(action)
    return deduped or ["prepare_review_packet"]


def approval_packet(entry: dict[str, Any], smoke_passed: bool) -> dict[str, Any]:
    approved = entry.get("approved") is True
    checklist = entry.get("checklist", {})
    required_before_live = [
        "owner asks Buddy for money-help approval using the required phrase",
        "owner approves specific allowed live actions",
        "sandbox smoke test evidence remains green",
        "secrets stay in environment variables",
        "audit logging is enabled",
        "human review remains required before external impact",
    ]
    if approved:
        required_before_live = [
            item
            for item in required_before_live
            if item not in {"owner asks Buddy for money-help approval using the required phrase", "owner approves specific allowed live actions"}
        ]

    return {
        "slug": entry.get("slug"),
        "name": entry.get("name"),
        "division": entry.get("division"),
        "category": entry.get("category"),
        "risk_reasons": entry.get("risk_reasons", []),
        "status": "live_approved" if approved else "approval_required",
        "required_buddy_money_request": entry.get("required_buddy_money_request"),
        "suggested_allowed_live_actions": entry.get("allowed_live_actions") or allowed_actions_for(entry),
        "blocked_live_actions": entry.get("disallowed_live_actions", []),
        "checklist": {
            **checklist,
            "sandbox_smoke_test_passed": bool(smoke_passed),
        },
        "required_before_live_release": required_before_live,
        "safe_mode_until_approved": {
            "can_run_sandbox": True,
            "can_prepare_recommendations": True,
            "can_create_drafts": True,
            "can_move_money": False,
            "can_place_trades": False,
            "can_send_final_legal_medical_tax_advice": False,
            "can_act_on_third_party_systems": False,
        },
    }


def build_report() -> dict[str, Any]:
    registry = read_json(APPROVAL_FILE, {})
    smoke = read_json(SMOKE_REPORT, {})
    smoke_passed = smoke.get("tests_failed", 1) == 0
    approvals = registry.get("approvals", [])
    packets = [approval_packet(entry, smoke_passed) for entry in approvals]
    by_status = Counter(packet["status"] for packet in packets)
    by_risk = Counter(
        reason
        for packet in packets
        for reason in packet.get("risk_reasons", [])
    )
    by_division = Counter(packet.get("division") or "Unknown" for packet in packets)
    grouped = defaultdict(list)
    for packet in packets:
        grouped[packet["status"]].append(packet["slug"])

    return {
        "schema": "dreamco.production_approval_packets.v1",
        "generated_at": iso_now(),
        "source_registry": str(APPROVAL_FILE.relative_to(ROOT)),
        "summary": {
            "approval_packets": len(packets),
            "live_approved": by_status.get("live_approved", 0),
            "approval_required": by_status.get("approval_required", 0),
            "smoke_tests_passed": smoke.get("tests_passed", 0),
            "smoke_tests_failed": smoke.get("tests_failed", 0),
            "sandbox_safe_production_candidates": len(packets) if smoke_passed else 0,
            "full_live_production_ready_after_approval": by_status.get("live_approved", 0),
        },
        "approval_rule": registry.get("approval_rule"),
        "required_buddy_money_request": registry.get("required_buddy_money_request"),
        "risk_breakdown": dict(by_risk.most_common()),
        "division_breakdown": dict(by_division.most_common()),
        "status_groups": dict(grouped),
        "packets": packets,
        "next_actions": [
            "Review the approval-required bots by risk category before enabling live actions.",
            "Approve only the specific live actions each bot is allowed to perform.",
            "Keep money movement, trading, legal, medical, tax, security, and third-party actions blocked until approved.",
            "Regenerate Buddy capability inventory after approvals so production-ready counts update.",
        ],
    }


def write_markdown(report: dict[str, Any]) -> None:
    summary = report["summary"]
    lines = [
        "# Production Approval Packets",
        "",
        f"Generated: {report['generated_at']}",
        "",
        "## Summary",
        "",
        f"- **Approval packets**: {summary['approval_packets']}",
        f"- **Live approved**: {summary['live_approved']}",
        f"- **Approval required**: {summary['approval_required']}",
        f"- **Smoke tests passed**: {summary['smoke_tests_passed']}",
        f"- **Smoke tests failed**: {summary['smoke_tests_failed']}",
        f"- **Sandbox-safe production candidates**: {summary['sandbox_safe_production_candidates']}",
        "",
        "## Required Buddy Request",
        "",
        report.get("required_buddy_money_request") or "Not configured.",
        "",
        "## Risk Breakdown",
        "",
    ]
    for reason, count in report["risk_breakdown"].items():
        lines.append(f"- **{reason}**: {count}")

    lines += ["", "## First Approval Packets", ""]
    for packet in report["packets"][:25]:
        lines.append(
            f"- **{packet['name']}** (`{packet['slug']}`): {packet['status']} "
            f"- {', '.join(packet['risk_reasons'])}"
        )

    lines += ["", "## Next Actions", ""]
    for action in report["next_actions"]:
        lines.append(f"- {action}")

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUTPUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
