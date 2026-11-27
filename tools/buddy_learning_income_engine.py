"""Evidence-first task distillation and income opportunity scoring.

Standard library only. No autonomous external actions or model training.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256
from typing import Any
import json
import re

SENSITIVE = ("password", "credential", "bank account", "medical record", "private key", "social security")
MONEY = ("payment", "invoice", "purchase", "transfer", "charge", "refund", "trade")
EXTERNAL = ("send", "publish", "deploy", "delete", "email", "post", "update account")
DOMAINS = ("coding", "research", "sales", "design", "education", "finance", "operations", "personal")


@dataclass(frozen=True)
class TaskPacket:
    task_id: str
    goal: str
    domain: str
    constraints: tuple[str, ...]
    success_criteria: tuple[str, ...]
    tools: tuple[str, ...]
    risk: str
    approval_required: bool
    mode: str
    source: str
    consent_to_learn: bool = False
    evidence: tuple[str, ...] = ()
    status: str = "proposed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def distill_task(goal: str, *, domain: str = "operations",
                 constraints: tuple[str, ...] = (),
                 success_criteria: tuple[str, ...] = (),
                 tools: tuple[str, ...] = (), source: str = "user",
                 consent_to_learn: bool = False, mode: str = "guide") -> TaskPacket:
    goal = " ".join(goal.split())
    if not goal or len(goal) > 4000:
        raise ValueError("goal must contain 1-4000 characters")
    if domain not in DOMAINS:
        raise ValueError("unsupported domain")
    if mode not in ("guide", "watch", "sandbox", "execute"):
        raise ValueError("unsupported mode")
    lower = goal.lower()
    sensitive = any(term in lower for term in SENSITIVE)
    money = any(term in lower for term in MONEY)
    external = any(re.search(r"\b" + re.escape(term) + r"\b", lower) for term in EXTERNAL)
    approval = sensitive or money or external or mode == "execute"
    risk = "high" if sensitive or money else "medium" if external or mode == "execute" else "low"
    digest = sha256(json.dumps([goal, domain, source], sort_keys=True).encode()).hexdigest()[:16]
    return TaskPacket(
        task_id="task_" + digest, goal=goal, domain=domain,
        constraints=tuple(constraints), success_criteria=tuple(success_criteria),
        tools=tuple(tools), risk=risk, approval_required=approval,
        mode=mode, source=source, consent_to_learn=consent_to_learn,
    )


def opportunity_score(*, demand: float, margin: float, repeatability: float,
                      automation_readiness: float, risk: float, evidence_quality: float) -> dict[str, Any]:
    values = (demand, margin, repeatability, automation_readiness, risk, evidence_quality)
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 1 for v in values):
        raise ValueError("scores must be numbers from 0 to 1")
    score = round(100 * (0.25*demand + 0.25*margin + 0.20*repeatability +
                         0.15*automation_readiness + 0.15*evidence_quality) * (1 - 0.6*risk), 2)
    return {"score": score, "status": "hypothesis", "verified_revenue": False,
            "needs_market_validation": evidence_quality < 0.8}


def propose_learning_example(packet: TaskPacket, *, outcome: str, evidence: tuple[str, ...],
                             holdout: bool = False) -> dict[str, Any]:
    if outcome not in ("success", "failure"):
        raise ValueError("outcome must be success or failure")
    if not packet.consent_to_learn:
        raise PermissionError("explicit learning consent required")
    if not evidence:
        raise ValueError("evidence required")
    return {"task_id": packet.task_id, "outcome": outcome, "evidence": list(evidence),
            "split": "holdout" if holdout else "candidate",
            "training_eligible": not holdout, "review_status": "pending"}


def execution_decision(packet: TaskPacket, *, approved: bool = False,
                       adapter_verified: bool = False) -> dict[str, Any]:
    if packet.mode != "execute":
        return {"allowed": False, "reason": "guided_or_observation_mode"}
    if packet.approval_required and not approved:
        return {"allowed": False, "reason": "approval_required"}
    if not adapter_verified:
        return {"allowed": False, "reason": "unverified_adapter"}
    return {"allowed": True, "reason": "eligible_for_separate_runtime_policy_checks"}
