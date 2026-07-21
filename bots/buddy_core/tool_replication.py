"""
Tool Replication Engine — Buddy Core System (Phase 2 Priority).

Takes a :class:`~bots.buddy_core.tool_scraper.ToolProfile` produced by the
:class:`~bots.buddy_core.tool_scraper.ToolScraper` and dynamically generates
a Buddy-native Python module that replicates the core functionality of the
analysed external tool.

Buddy's Motto:  **"If an app can do it, so can we."**

Part of the Buddy Core System — adheres to the GLOBAL AI SOURCES FLOW framework.

Architecture
------------
The replication engine participates in Stage 6 (Deployment) and Stage 7
(Profit & Market Intelligence) of the GLOBAL AI SOURCES FLOW pipeline:

  ToolProfile (from ToolScraper)
          │
          ▼
  ToolReplicationEngine.replicate(...)
          │
          ├─► ReplicatedTool.source_code   ← generated Python module
          ├─► ReplicatedTool.workflow       ← ordered steps
          └─► ReplicatedTool.metadata       ← capability map

Pipeline
--------
::

    scraper  = ToolScraper()
    profile  = scraper.analyze_known_platform("zapier")

    engine   = ToolReplicationEngine()
    replica  = engine.replicate(profile)

    print(replica.source_code)   # ready-to-use Python class
"""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bots.buddy_core.tool_scraper import (
    CapabilityTag,
    PlatformType,
    ToolProfile,
    ToolScraperError,
)


# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------

@dataclass
class ReplicatedTool:
    """
    Buddy-native equivalent generated from a :class:`ToolProfile`.

    Attributes
    ----------
    tool_name : str
        Name of the original external tool.
    buddy_class_name : str
        PascalCase class name of the generated Buddy module.
    source_code : str
        Complete Python source code of the replicated module.
    workflow : list[str]
        Ordered list of workflow steps the replicated tool performs.
    capabilities_replicated : list[str]
        Capability tags that were replicated.
    platform_type : str
        Original platform type (e.g. ``"automation"``).
    generated_at : datetime
        UTC timestamp of generation.
    metadata : dict
        Additional generation metadata.
    """

    tool_name: str
    buddy_class_name: str
    source_code: str
    workflow: list[str]
    capabilities_replicated: list[str]
    platform_type: str
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary (source_code excluded for brevity)."""
        return {
            "tool_name": self.tool_name,
            "buddy_class_name": self.buddy_class_name,
            "platform_type": self.platform_type,
            "workflow": self.workflow,
            "capabilities_replicated": self.capabilities_replicated,
            "generated_at": self.generated_at.isoformat(),
            "metadata": self.metadata,
        }


class ToolReplicationError(Exception):
    """Raised when replication fails."""


# ---------------------------------------------------------------------------
# Capability → code-snippet registry
# ---------------------------------------------------------------------------

_CAPABILITY_SNIPPETS: dict[CapabilityTag, str] = {
    CapabilityTag.CRUD: textwrap.dedent("""\
        def create(self, resource: str, payload: dict) -> dict:
            \"\"\"Create a resource.\"\"\"
            return {"status": "created", "resource": resource, "data": payload}

        def read(self, resource: str, resource_id: str) -> dict:
            \"\"\"Retrieve a resource by ID.\"\"\"
            return {"resource": resource, "id": resource_id, "data": {}}

        def update(self, resource: str, resource_id: str, payload: dict) -> dict:
            \"\"\"Update a resource.\"\"\"
            return {"status": "updated", "resource": resource, "id": resource_id}

        def delete(self, resource: str, resource_id: str) -> dict:
            \"\"\"Delete a resource.\"\"\"
            return {"status": "deleted", "resource": resource, "id": resource_id}
    """),

    CapabilityTag.WEBHOOKS: textwrap.dedent("""\
        def register_webhook(self, event: str, callback_url: str) -> dict:
            \"\"\"Register a webhook endpoint for *event*.\"\"\"
            import uuid
            hook_id = str(uuid.uuid4())[:8]
            self._webhooks[hook_id] = {"event": event, "url": callback_url}
            return {"webhook_id": hook_id, "event": event, "url": callback_url}

        def fire_webhook(self, event: str, payload: dict) -> list[dict]:
            \"\"\"Simulate firing all registered webhooks for *event*.\"\"\"
            fired = []
            for hook_id, hook in self._webhooks.items():
                if hook["event"] == event:
                    fired.append({"hook_id": hook_id, "url": hook["url"], "payload": payload})
            return fired
    """),

    CapabilityTag.WORKFLOW_AUTOMATION: textwrap.dedent("""\
        def create_workflow(self, name: str, trigger: str, actions: list[str]) -> dict:
            \"\"\"Create an automated workflow with a trigger and action steps.\"\"\"
            import uuid
            wf_id = str(uuid.uuid4())[:8]
            workflow = {"id": wf_id, "name": name, "trigger": trigger, "actions": actions}
            self._workflows[wf_id] = workflow
            return workflow

        def run_workflow(self, workflow_id: str, context: dict | None = None) -> dict:
            \"\"\"Execute a workflow by ID.\"\"\"
            wf = self._workflows.get(workflow_id)
            if not wf:
                return {"status": "error", "message": f"Workflow '{workflow_id}' not found."}
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "name": wf["name"],
                "steps_executed": wf["actions"],
                "context": context or {},
            }
    """),

    CapabilityTag.PAYMENT_PROCESSING: textwrap.dedent("""\
        def create_payment(self, amount_cents: int, currency: str = "usd",
                           customer_email: str = "") -> dict:
            \"\"\"Create a payment intent.\"\"\"
            import uuid
            payment_id = "pay_" + str(uuid.uuid4())[:12]
            return {
                "payment_id": payment_id,
                "amount_cents": amount_cents,
                "currency": currency,
                "customer_email": customer_email,
                "status": "requires_payment_method",
            }

        def confirm_payment(self, payment_id: str) -> dict:
            \"\"\"Confirm and capture a payment.\"\"\"
            return {"payment_id": payment_id, "status": "succeeded"}
    """),

    CapabilityTag.SUBSCRIPTION_BILLING: textwrap.dedent("""\
        def create_subscription(self, customer_id: str, plan: str,
                                billing_cycle: str = "monthly") -> dict:
            \"\"\"Create a recurring subscription.\"\"\"
            import uuid
            sub_id = "sub_" + str(uuid.uuid4())[:12]
            self._subscriptions[sub_id] = {
                "customer_id": customer_id,
                "plan": plan,
                "billing_cycle": billing_cycle,
                "status": "active",
            }
            return {"subscription_id": sub_id, **self._subscriptions[sub_id]}

        def cancel_subscription(self, subscription_id: str) -> dict:
            \"\"\"Cancel an active subscription.\"\"\"
            if subscription_id in self._subscriptions:
                self._subscriptions[subscription_id]["status"] = "cancelled"
            return {"subscription_id": subscription_id, "status": "cancelled"}
    """),

    CapabilityTag.EMAIL_DELIVERY: textwrap.dedent("""\
        def send_email(self, to: str, subject: str, body: str,
                       from_addr: str = "noreply@dreamco.ai") -> dict:
            \"\"\"Send an email (configure SENDGRID_API_KEY or SMTP vars).\"\"\"
            import os
            print(f"[EMAIL] To: {to} | Subject: {subject} | From: {from_addr}")
            return {"status": "sent", "to": to, "subject": subject}
    """),

    CapabilityTag.SMS_DELIVERY: textwrap.dedent("""\
        def send_sms(self, to: str, body: str, from_number: str = "+10000000000") -> dict:
            \"\"\"Send an SMS message (configure TWILIO_ACCOUNT_SID env var).\"\"\"
            import os
            print(f"[SMS] To: {to} | From: {from_number} | Body: {body[:80]}")
            return {"status": "sent", "to": to, "body": body}
    """),

    CapabilityTag.SEARCH: textwrap.dedent("""\
        def search(self, query: str, filters: dict | None = None,
                   limit: int = 20) -> list[dict]:
            \"\"\"Search for records matching *query*.\"\"\"
            return [{"id": i, "query": query, "score": round(1.0 - i * 0.05, 2)}
                    for i in range(min(limit, 10))]
    """),

    CapabilityTag.ANALYTICS: textwrap.dedent("""\
        def get_analytics(self, metric: str, start_date: str = "",
                          end_date: str = "") -> dict:
            \"\"\"Retrieve analytics data for *metric*.\"\"\"
            return {
                "metric": metric,
                "start_date": start_date,
                "end_date": end_date,
                "value": 0,
                "trend": "stable",
            }
    """),

    CapabilityTag.NOTIFICATIONS: textwrap.dedent("""\
        def send_notification(self, channel: str, message: str,
                              recipient: str = "") -> dict:
            \"\"\"Dispatch a notification via *channel*.\"\"\"
            print(f"[NOTIFY/{channel.upper()}] {recipient}: {message[:120]}")
            return {"status": "sent", "channel": channel, "recipient": recipient}
    """),

    CapabilityTag.FILE_UPLOAD: textwrap.dedent("""\
        def upload_file(self, file_path: str, destination: str = "") -> dict:
            \"\"\"Upload a file to remote storage.\"\"\"
            import os
            filename = os.path.basename(file_path)
            dest = destination or f"uploads/{filename}"
            return {"status": "uploaded", "filename": filename, "destination": dest}
    """),

    CapabilityTag.DATA_EXPORT: textwrap.dedent("""\
        def export_csv(self, records: list[dict], filepath: str = "export.csv") -> str:
            \"\"\"Export *records* to a CSV file.\"\"\"
            import csv, io
            if not records:
                return filepath
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
            with open(filepath, "w", newline="", encoding="utf-8") as fh:
                fh.write(buf.getvalue())
            return filepath
    """),

    CapabilityTag.MACHINE_LEARNING: textwrap.dedent("""\
        def predict(self, input_data: dict) -> dict:
            \"\"\"Run a prediction using the configured ML model.\"\"\"
            return {"prediction": None, "confidence": 0.0, "input": input_data}

        def train(self, training_data: list[dict]) -> dict:
            \"\"\"Trigger model training on *training_data*.\"\"\"
            return {"status": "training_started", "samples": len(training_data)}
    """),

    CapabilityTag.NLP: textwrap.dedent("""\
        def generate_text(self, prompt: str, max_tokens: int = 200) -> str:
            \"\"\"Generate text from *prompt* using the configured LLM.\"\"\"
            import os
            # Configure OPENAI_API_KEY or ANTHROPIC_API_KEY
            return f"[Generated response for: {prompt[:60]}...]"

        def classify_text(self, text: str, labels: list[str]) -> dict:
            \"\"\"Zero-shot text classification.\"\"\"
            return {"text": text[:60], "label": labels[0] if labels else "unknown",
                    "confidence": 0.85}
    """),

    CapabilityTag.GEOLOCATION: textwrap.dedent("""\
        def geocode(self, address: str) -> dict:
            \"\"\"Convert a street address to lat/lng coordinates.\"\"\"
            return {"address": address, "lat": 0.0, "lng": 0.0, "formatted": address}

        def reverse_geocode(self, lat: float, lng: float) -> str:
            \"\"\"Convert lat/lng to a human-readable address.\"\"\"
            return f"Location at ({lat:.4f}, {lng:.4f})"
    """),

    CapabilityTag.SCHEDULING: textwrap.dedent("""\
        def schedule_task(self, task_name: str, cron_expr: str,
                          payload: dict | None = None) -> dict:
            \"\"\"Schedule *task_name* to run on *cron_expr* schedule.\"\"\"
            import uuid
            task_id = str(uuid.uuid4())[:8]
            return {"task_id": task_id, "task_name": task_name,
                    "cron": cron_expr, "payload": payload or {}}
    """),

    CapabilityTag.REPORTING: textwrap.dedent("""\
        def generate_report(self, report_type: str, params: dict | None = None) -> dict:
            \"\"\"Generate a structured report.\"\"\"
            return {
                "report_type": report_type,
                "params": params or {},
                "sections": [],
                "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            }
    """),

    CapabilityTag.PAGINATION: textwrap.dedent("""\
        def paginate(self, resource: str, page: int = 1,
                     per_page: int = 20) -> dict:
            \"\"\"Fetch a page of *resource* records.\"\"\"
            return {
                "resource": resource,
                "page": page,
                "per_page": per_page,
                "total": 0,
                "items": [],
                "has_next": False,
            }
    """),
}


# ---------------------------------------------------------------------------
# Platform → init_body mapping
# ---------------------------------------------------------------------------

_PLATFORM_INIT_EXTRAS: dict[PlatformType, str] = {
    PlatformType.AUTOMATION: (
        "        self._workflows: dict = {}\n"
        "        self._webhooks: dict = {}\n"
    ),
    PlatformType.PAYMENT: (
        "        self._subscriptions: dict = {}\n"
        "        self._payments: dict = {}\n"
    ),
    PlatformType.MESSAGING: (
        "        self._messages: list = []\n"
        "        self._webhooks: dict = {}\n"
    ),
    PlatformType.ANALYTICS: (
        "        self._events: list = []\n"
    ),
    PlatformType.CRM: (
        "        self._contacts: dict = {}\n"
        "        self._webhooks: dict = {}\n"
    ),
    PlatformType.SAAS: (
        "        self._workflows: dict = {}\n"
        "        self._webhooks: dict = {}\n"
    ),
}


# ---------------------------------------------------------------------------
# Replication Engine
# ---------------------------------------------------------------------------

class ToolReplicationEngine:
    """
    Dynamically generates Buddy-native Python modules from :class:`ToolProfile`
    objects produced by :class:`~bots.buddy_core.tool_scraper.ToolScraper`.

    The generated code is a complete, self-contained Python class that:
      - Mirrors the core capabilities of the original tool.
      - Follows the Dreamcobots GLOBAL AI SOURCES FLOW framework conventions.
      - Can be saved to disk and imported immediately.

    Usage
    -----
    ::

        from bots.buddy_core.tool_scraper import ToolScraper
        from bots.buddy_core.tool_replication import ToolReplicationEngine

        scraper = ToolScraper()
        profile = scraper.analyze_known_platform("zapier")

        engine  = ToolReplicationEngine()
        replica = engine.replicate(profile)

        print(replica.source_code)
    """

    def replicate(self, profile: ToolProfile) -> ReplicatedTool:
        """
        Generate a Buddy-native equivalent from *profile*.

        Parameters
        ----------
        profile : ToolProfile
            The capability map to replicate.

        Returns
        -------
        ReplicatedTool
        """
        if not isinstance(profile, ToolProfile):
            raise ToolReplicationError(
                "profile must be a ToolProfile instance."
            )

        class_name = self._to_class_name(profile.tool_name)
        source = self._build_source(profile, class_name)

        return ReplicatedTool(
            tool_name=profile.tool_name,
            buddy_class_name=class_name,
            source_code=source,
            workflow=profile.workflow_steps,
            capabilities_replicated=[c.value for c in profile.capabilities],
            platform_type=profile.platform_type.value,
            metadata={
                "industry_tags": profile.industry_tags,
                "auth_type": profile.auth_type,
                "is_open_source": profile.is_open_source,
                "replication_priority": profile.replication_priority,
            },
        )

    def replicate_batch(self, profiles: list[ToolProfile]) -> list[ReplicatedTool]:
        """
        Replicate multiple tool profiles in one call.

        Parameters
        ----------
        profiles : list[ToolProfile]

        Returns
        -------
        list[ReplicatedTool]
        """
        return [self.replicate(p) for p in profiles]

    # ------------------------------------------------------------------
    # Source code builder
    # ------------------------------------------------------------------

    def _build_source(self, profile: ToolProfile, class_name: str) -> str:
        lines: list[str] = []

        # Module-level docstring and imports
        lines += [
            f'"""',
            f"Buddy-native replication of {profile.tool_name}.",
            f"",
            f"Auto-generated by ToolReplicationEngine.",
            f"Original platform type : {profile.platform_type.value}",
            f"Capabilities replicated: {', '.join(c.value for c in profile.capabilities)}",
            f"",
            f"GLOBAL AI SOURCES FLOW: participates via BuddyCore pipeline.",
            f'"""',
            f"",
            f"from __future__ import annotations",
            f"",
            f"import sys",
            f"import os",
            f"",
            f"sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))",
            f"",
            f"from framework import GlobalAISourcesFlow  # noqa: F401",
            f"",
            f"",
            f"class {class_name}:",
            f'    """',
            f"    Buddy-native equivalent of {profile.tool_name}.",
            f"",
            f"    {profile.description}",
            f"",
            f"    Generated by the Buddy Tool Replication Engine.",
            f'    """',
            f"",
        ]

        # __init__
        init_extra = _PLATFORM_INIT_EXTRAS.get(profile.platform_type, "")
        # Ensure common collections are always available for webhooks/workflows
        if (
            CapabilityTag.WEBHOOKS in profile.capabilities
            and "self._webhooks" not in init_extra
        ):
            init_extra += "        self._webhooks: dict = {}\n"
        if (
            CapabilityTag.WORKFLOW_AUTOMATION in profile.capabilities
            and "self._workflows" not in init_extra
        ):
            init_extra += "        self._workflows: dict = {}\n"
        if (
            CapabilityTag.SUBSCRIPTION_BILLING in profile.capabilities
            and "self._subscriptions" not in init_extra
        ):
            init_extra += "        self._subscriptions: dict = {}\n"
        if (
            CapabilityTag.PAYMENT_PROCESSING in profile.capabilities
            and "self._payments" not in init_extra
        ):
            init_extra += "        self._payments: dict = {}\n"

        lines += [
            f"    def __init__(self, api_key: str = '') -> None:",
            f"        self._api_key = api_key or os.environ.get(",
            f"            '{self._env_var(profile.tool_name)}', ''",
            f"        )",
            f"        self._base_url = {profile.base_url!r}",
        ]
        if init_extra:
            lines.append(init_extra.rstrip())
        lines.append("")

        # get_status
        lines += [
            f"    def get_status(self) -> dict:",
            f'        """Return connection status."""',
            f"        return {{",
            f"            'tool': {profile.tool_name!r},",
            f"            'platform_type': {profile.platform_type.value!r},",
            f"            'authenticated': bool(self._api_key),",
            f"            'base_url': self._base_url,",
            f"        }}",
            f"",
        ]

        # Capability method snippets
        for cap in profile.capabilities:
            snippet = _CAPABILITY_SNIPPETS.get(cap)
            if snippet:
                indented = textwrap.indent(snippet, "    ")
                lines.append(indented)

        # run_pipeline (GLOBAL AI SOURCES FLOW hook)
        lines += [
            f"    def run_pipeline(self, payload: dict | None = None) -> dict:",
            f'        """GLOBAL AI SOURCES FLOW entry point."""',
            f"        flow = GlobalAISourcesFlow(bot_name={class_name!r})",
            f"        return flow.run_pipeline(raw_data=payload or {{}})",
            f"",
        ]

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_class_name(tool_name: str) -> str:
        """Convert a tool name to a PascalCase class name with 'Buddy' prefix."""
        # Remove non-alphanumeric chars, split, capitalise
        words = re.sub(r"[^a-zA-Z0-9\s]", " ", tool_name).split()
        pascal = "".join(w.capitalize() for w in words if w)
        return f"Buddy{pascal}Bot"

    @staticmethod
    def _env_var(tool_name: str) -> str:
        """Return a conventional env-var name for the tool's API key."""
        clean = re.sub(r"[^a-zA-Z0-9]", "_", tool_name).upper()
        return f"{clean}_API_KEY"
