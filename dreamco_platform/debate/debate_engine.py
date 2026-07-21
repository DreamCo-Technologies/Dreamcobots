"""
GlobalAI Debate Team — a team of AI agents (powered by GlobalAISourcesFlow)
that debates every DreamCo task to reach the best possible decision.

Each team member represents one of the 8 pipeline stages and argues from
that stage's perspective. The moderator runs structured rounds (opening,
cross-examination, closing) and synthesises a final consensus verdict.

Usage::

    from dreamco_platform.debate.debate_engine import DebateTeam

    team = DebateTeam()
    verdict = team.deliberate(
        motion="Should we deploy BotX to production tier?",
        context={"sandbox_passed": True, "revenue_forecast": 5000},
    )

GLOBAL AI SOURCES FLOW
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  GLOBAL AI SOURCES FLOW

logger = logging.getLogger(__name__)

DEBATE_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Verdict(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    DEFER = "defer"
    CONDITIONAL = "conditional"


class DebateRound(str, Enum):
    OPENING = "opening"
    CROSS_EXAMINATION = "cross_examination"
    REBUTTAL = "rebuttal"
    CLOSING = "closing"


# ---------------------------------------------------------------------------
# Team member
# ---------------------------------------------------------------------------

@dataclass
class TeamMember:
    """One AI agent on the debate team, specialised in a pipeline stage."""
    name: str
    stage: str
    perspective: str
    learning_method: str
    vote_weight: float = 1.0

    def argue(self, motion: str, round_: DebateRound, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an argument using GlobalAISourcesFlow."""
        flow = GlobalAISourcesFlow(bot_name=self.name)
        result = flow.run_pipeline(
            raw_data={
                "motion": motion,
                "round": round_.value,
                "perspective": self.perspective,
                **context,
            },
            learning_method=self.learning_method,
        )

        # Score is based on context alignment with this member's perspective
        score = self._score_motion(motion, context)
        vote = Verdict.APPROVE if score >= 0.6 else (Verdict.CONDITIONAL if score >= 0.4 else Verdict.REJECT)

        return {
            "member": self.name,
            "stage": self.stage,
            "perspective": self.perspective,
            "round": round_.value,
            "argument": f"[{self.perspective.upper()}] Pipeline validated. Score: {score:.2f}. "
                        f"Recommendation: {vote.value}.",
            "score": round(score, 3),
            "vote": vote.value,
            "weight": self.vote_weight,
            "pipeline_complete": result["pipeline_complete"],
        }

    def _score_motion(self, motion: str, context: Dict[str, Any]) -> float:
        """Compute a perspective-specific score for the motion."""
        base = 0.5
        m = motion.lower()
        # Positive signals per perspective
        signals = {
            "data_quality": ["clean data", "validated", "ingestion", "normalized"],
            "model_performance": ["accuracy", "benchmark", "performance", "latency"],
            "sandbox_safety": ["sandbox passed", "tested", "sandbox_passed"],
            "efficiency": ["efficient", "fast", "cost", "optimized"],
            "innovation": ["new", "feature", "capability", "upgrade"],
            "reliability": ["stable", "uptime", "sla", "reliable"],
            "revenue": ["revenue", "profit", "mrr", "arr", "monetize"],
            "compliance": ["compliant", "audit", "governance", "secure"],
        }
        for kw in signals.get(self.perspective, []):
            if kw in m or str(context).lower().find(kw) >= 0:
                base += 0.1
        # Context gates
        if self.perspective == "sandbox_safety" and context.get("sandbox_passed"):
            base += 0.3
        if self.perspective == "revenue" and context.get("revenue_forecast", 0) > 1000:
            base += 0.2
        if self.perspective == "compliance" and context.get("audit_logs"):
            base += 0.2
        return min(base, 1.0)


# ---------------------------------------------------------------------------
# Debate session
# ---------------------------------------------------------------------------

@dataclass
class DebateSession:
    session_id: str
    motion: str
    context: Dict[str, Any]
    rounds: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    conditions: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "motion": self.motion,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "conditions": self.conditions,
            "rounds": self.rounds,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
        }


# ---------------------------------------------------------------------------
# Debate Team
# ---------------------------------------------------------------------------

class DebateTeam:
    """
    Structured debate team of 8 AI agents (one per GlobalAI pipeline stage).

    Debate format:
    1. Opening statements (all members)
    2. Cross-examination (members challenge each other)
    3. Rebuttal (members respond to challenges)
    4. Closing arguments (all members)
    5. Moderator synthesises verdict

    GLOBAL AI SOURCES FLOW
    """

    DEFAULT_MEMBERS = [
        TeamMember("DataIngestionAgent", "data_ingestion", "data_quality", "supervised", 1.0),
        TeamMember("LearningClassifier", "learning_classifier", "model_performance", "self_supervised", 1.1),
        TeamMember("SandboxValidator", "sandbox_test", "sandbox_safety", "reinforcement", 1.5),
        TeamMember("PerformanceAnalyst", "performance_analytics", "efficiency", "supervised", 1.2),
        TeamMember("EvolutionEngineer", "hybrid_evolution", "innovation", "federated_learning", 1.0),
        TeamMember("DeploymentGovernor", "deployment", "reliability", "transfer_learning", 1.3),
        TeamMember("RevenueStrategist", "profit_market_intelligence", "revenue", "supervised", 1.4),
        TeamMember("GovernanceCounsel", "governance_security", "compliance", "supervised", 1.5),
    ]

    def __init__(self, members: Optional[List[TeamMember]] = None) -> None:
        self.members = members or [m for m in self.DEFAULT_MEMBERS]
        self._sessions: List[DebateSession] = []
        logger.info("DebateTeam v%s initialized with %d members", DEBATE_VERSION, len(self.members))

    # ------------------------------------------------------------------
    # Core debate flow
    # ------------------------------------------------------------------

    def deliberate(
        self,
        motion: str,
        context: Optional[Dict[str, Any]] = None,
        quick_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Run a full structured debate and return a binding verdict.

        Parameters
        ----------
        motion : str
            The proposal being debated (e.g., "Deploy BotX to production").
        context : dict
            Relevant facts and metrics for the debate.
        quick_mode : bool
            If True, skip cross-examination and rebuttal rounds.
        """
        ctx = context or {}
        session = DebateSession(
            session_id=str(uuid.uuid4()),
            motion=motion,
            context=ctx,
        )

        # Round 1: Opening statements
        session.rounds[DebateRound.OPENING.value] = self._run_round(
            motion, DebateRound.OPENING, ctx
        )

        if not quick_mode:
            # Round 2: Cross-examination
            session.rounds[DebateRound.CROSS_EXAMINATION.value] = self._run_round(
                motion, DebateRound.CROSS_EXAMINATION, ctx
            )
            # Round 3: Rebuttal
            session.rounds[DebateRound.REBUTTAL.value] = self._run_round(
                motion, DebateRound.REBUTTAL, ctx
            )

        # Round 4: Closing arguments
        session.rounds[DebateRound.CLOSING.value] = self._run_round(
            motion, DebateRound.CLOSING, ctx
        )

        # Synthesise verdict
        verdict, confidence, conditions = self._synthesise(session)
        session.verdict = verdict.value
        session.confidence = confidence
        session.conditions = conditions
        session.ended_at = datetime.now(timezone.utc)

        self._sessions.append(session)
        logger.info(
            "Debate concluded | motion=%r verdict=%s confidence=%.3f",
            motion[:80], verdict.value, confidence,
        )
        return session.to_dict()

    def _run_round(
        self,
        motion: str,
        round_: DebateRound,
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        return [member.argue(motion, round_, context) for member in self.members]

    def _synthesise(self, session: DebateSession) -> Tuple[Verdict, float, List[str]]:
        """Compute weighted-vote consensus from closing round."""
        closing = session.rounds.get(DebateRound.CLOSING.value, [])
        if not closing:
            return Verdict.DEFER, 0.5, ["No closing arguments recorded"]

        vote_weights: Dict[str, float] = {}
        for arg in closing:
            vote = arg["vote"]
            vote_weights[vote] = vote_weights.get(vote, 0) + arg["weight"]

        total_weight = sum(vote_weights.values())
        if total_weight == 0:
            return Verdict.DEFER, 0.5, []

        # Normalise weights
        normalised = {v: w / total_weight for v, w in vote_weights.items()}
        top_vote = max(normalised, key=lambda v: normalised[v])
        confidence = normalised[top_vote]

        verdict = Verdict(top_vote) if top_vote in Verdict._value2member_map_ else Verdict.DEFER
        conditions: List[str] = []

        if verdict == Verdict.CONDITIONAL:
            conditions = self._extract_conditions(session)
        elif confidence < 0.6:
            verdict = Verdict.DEFER
            conditions.append("Low consensus confidence — defer to human review")

        return verdict, round(confidence, 3), conditions

    def _extract_conditions(self, session: DebateSession) -> List[str]:
        conditions = []
        ctx = session.context
        if not ctx.get("sandbox_passed"):
            conditions.append("Must pass sandbox validation before deployment")
        if ctx.get("test_coverage", 100) < 80:
            conditions.append("Test coverage must reach 80% before deployment")
        if ctx.get("revenue_forecast", 0) < 100:
            conditions.append("Revenue forecast must exceed $100/mo")
        return conditions

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def quick_vote(self, motion: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fast single-round vote (skips cross-examination and rebuttal)."""
        return self.deliberate(motion, context, quick_mode=True)

    def get_sessions(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self._sessions]

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._sessions)
        verdicts = [s.verdict for s in self._sessions if s.verdict]
        return {
            "total_debates": total,
            "approved": verdicts.count("approve"),
            "rejected": verdicts.count("reject"),
            "deferred": verdicts.count("defer"),
            "conditional": verdicts.count("conditional"),
            "avg_confidence": (
                sum(s.confidence for s in self._sessions if s.confidence)
                / max(1, sum(1 for s in self._sessions if s.confidence))
            ),
            "debate_version": DEBATE_VERSION,
        }

    def __repr__(self) -> str:
        return f"DebateTeam(members={len(self.members)}, sessions={len(self._sessions)})"
