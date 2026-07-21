"""
Tier configuration specific to the Business Automation Bot.

Extends the platform-wide FREE/PRO/ENTERPRISE tier structure with
automation workflows and sector-specific features.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config

# ------------------------------------------------------------------
# Business-automation-specific features per tier
# ------------------------------------------------------------------

BA_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "Meeting scheduling",
        "Task reminders",
        "Email drafting (3/day)",
        "Basic calendar sync",
    ],
    Tier.PRO.value: [
        "CRM integration (Salesforce, HubSpot)",
        "Invoice generation & tracking",
        "Report automation (PDF/CSV export)",
        "Multi-step workflow builder",
        "Slack/Teams notifications",
    ],
    Tier.ENTERPRISE.value: [
        "Full ERP integration",
        "Custom workflow orchestration",
        "Multi-tenant white-label deployment",
        "Audit trails & compliance exports",
        "Dedicated workflow engineer",
    ],
}

# Workflow IDs available per tier (higher tiers include all lower-tier workflows)
BA_WORKFLOWS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "meeting_scheduler",
        "task_reminder",
        "email_drafter",
    ],
    Tier.PRO.value: [
        "meeting_scheduler",
        "task_reminder",
        "email_drafter",
        "invoice_generator",
        "crm_sync",
        "report_automation",
        "slack_notifier",
    ],
    Tier.ENTERPRISE.value: [
        "meeting_scheduler",
        "task_reminder",
        "email_drafter",
        "invoice_generator",
        "crm_sync",
        "report_automation",
        "slack_notifier",
        "erp_integration",
        "workflow_orchestrator",
        "audit_exporter",
        "white_label_deploy",
    ],
}


def get_ba_tier_info(tier: Tier) -> dict:
    """Return Business Automation tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "ba_features": BA_EXTRA_FEATURES[tier.value],
        "workflows": BA_WORKFLOWS[tier.value],
        "support_level": cfg.support_level,
    }
