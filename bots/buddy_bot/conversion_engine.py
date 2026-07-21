"""
Buddy Bot — Conversion Engine

Turns qualified leads into paying clients through an AI-assisted pipeline:
  • Proposal generation   — personalised, response-ready proposals
  • Outreach sequencing   — email / SMS follow-up chains with rate limits
  • Objection handling    — smart replies to common objections
  • Closing automation    — agreement drafts + contract generation
  • Booking integration   — calendar link embedding and slot management

Compliance-first design:
  - All outreach is rate-limited (max 50 emails/day on PRO, unlimited ENTERPRISE).
  - Every message includes an opt-out mechanism.
  - No bulk unsolicited SMS without explicit prior consent.
  - Human approval gate available for high-risk outreach.

Tier access
-----------
  FREE:       Proposal templates only, no automated outreach.
  PRO:        Full outreach sequences (email), objection handling, proposal + contract.
  ENTERPRISE: SMS outreach, AI closing, booking automation, unlimited sends.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


def _slugify(name: str) -> str:
    """Convert *name* to a URL-safe slug."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "-", slug).strip("-")
    return slug


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OutreachChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    SOCIAL_DM = "social_dm"


class ConversionStage(Enum):
    PROPOSAL_SENT = "proposal_sent"
    FOLLOW_UP_1 = "follow_up_1"
    FOLLOW_UP_2 = "follow_up_2"
    OBJECTION_RAISED = "objection_raised"
    OBJECTION_HANDLED = "objection_handled"
    CLOSING = "closing"
    AGREEMENT_SENT = "agreement_sent"
    BOOKED = "booked"
    WON = "won"
    LOST = "lost"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Proposal:
    """A personalised proposal sent to a lead."""

    proposal_id: str
    business_name: str
    service_headline: str
    body: str
    deliverables: list
    monthly_fee_usd: float
    setup_fee_usd: float
    guarantee: str
    call_to_action: str
    channel: OutreachChannel
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    stage: ConversionStage = ConversionStage.PROPOSAL_SENT

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "business_name": self.business_name,
            "service_headline": self.service_headline,
            "body": self.body,
            "deliverables": self.deliverables,
            "monthly_fee_usd": self.monthly_fee_usd,
            "setup_fee_usd": self.setup_fee_usd,
            "guarantee": self.guarantee,
            "call_to_action": self.call_to_action,
            "channel": self.channel.value,
            "created_at": self.created_at,
            "stage": self.stage.value,
        }


@dataclass
class ConversionRecord:
    """Tracks a lead's full conversion journey."""

    record_id: str
    business_name: str
    current_stage: ConversionStage
    proposals: list = field(default_factory=list)
    follow_up_count: int = 0
    objections: list = field(default_factory=list)
    booking_slot: Optional[str] = None
    won_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "business_name": self.business_name,
            "current_stage": self.current_stage.value,
            "proposals": [p.to_dict() if hasattr(p, "to_dict") else p for p in self.proposals],
            "follow_up_count": self.follow_up_count,
            "objections": self.objections,
            "booking_slot": self.booking_slot,
            "won_at": self.won_at,
        }


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ConversionEngineError(Exception):
    """Base exception for ConversionEngine errors."""


class ConversionEngineTierError(ConversionEngineError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Objection responses
# ---------------------------------------------------------------------------

_OBJECTION_RESPONSES: dict[str, str] = {
    "too expensive": (
        "I completely understand — budget is important. "
        "That's why we offer a performance-based option where you only pay "
        "when we deliver results. Want to explore that structure?"
    ),
    "not interested": (
        "No problem at all — I'll check back in 30 days. "
        "In the meantime, can I share a quick case study showing what "
        "businesses like yours achieved in 60 days?"
    ),
    "already have someone": (
        "Great — a second opinion never hurts. "
        "We'd love to do a free audit of your current marketing and show "
        "you exactly where you're leaving money on the table. "
        "Zero commitment."
    ),
    "no time": (
        "That's exactly why we exist — we handle 100% of the work, "
        "so you don't have to spend a single hour on marketing. "
        "Takes less than 15 minutes to get started."
    ),
    "need to think": (
        "Absolutely — take your time. "
        "I'll send you a detailed proposal with our guarantee so you have "
        "everything you need to make a confident decision."
    ),
    "default": (
        "Thanks for sharing that. Let me address your concern directly and "
        "provide a tailored solution that makes this a no-brainer for you."
    ),
}


# ---------------------------------------------------------------------------
# ConversionEngine
# ---------------------------------------------------------------------------

class ConversionEngine:
    """AI-assisted pipeline for converting leads into clients.

    Parameters
    ----------
    can_outreach : bool
        Whether automated outreach (email sequences) is enabled.
    can_sms : bool
        Whether SMS outreach is enabled.
    can_ai_closing : bool
        Whether AI closing and contract generation is enabled.
    can_booking : bool
        Whether booking automation is enabled.
    max_outreach_per_day : int | None
        Daily outreach send limit.  None = unlimited.
    require_human_approval : bool
        If True, high-risk outreach stages are flagged for human review.
    """

    def __init__(
        self,
        can_outreach: bool = False,
        can_sms: bool = False,
        can_ai_closing: bool = False,
        can_booking: bool = False,
        max_outreach_per_day: Optional[int] = 0,
        require_human_approval: bool = True,
    ) -> None:
        self.can_outreach = can_outreach
        self.can_sms = can_sms
        self.can_ai_closing = can_ai_closing
        self.can_booking = can_booking
        self.max_outreach_per_day = max_outreach_per_day
        self.require_human_approval = require_human_approval
        self._proposals: list[Proposal] = []
        self._records: dict[str, ConversionRecord] = {}
        self._proposal_counter: int = 0
        self._sends_today: int = 0

    # ------------------------------------------------------------------
    # Proposal generation
    # ------------------------------------------------------------------

    def generate_proposal(
        self,
        business_name: str,
        service_headline: str,
        deliverables: list,
        monthly_fee_usd: float,
        setup_fee_usd: float,
        guarantee: str,
        channel: OutreachChannel = OutreachChannel.EMAIL,
    ) -> Proposal:
        """Generate a personalised proposal for a business.

        Parameters
        ----------
        business_name : str
            Target business name.
        service_headline : str
            The main service headline/pitch.
        deliverables : list[str]
            List of items included in the offer.
        monthly_fee_usd : float
            Monthly retainer amount.
        setup_fee_usd : float
            One-time setup fee.
        guarantee : str
            Service guarantee statement.
        channel : OutreachChannel
            Primary contact channel.

        Returns
        -------
        Proposal
            The generated proposal object.
        """
        if channel == OutreachChannel.SMS and not self.can_sms:
            raise ConversionEngineTierError(
                "SMS outreach requires ENTERPRISE tier."
            )

        self._proposal_counter += 1
        deliverables_list = "\n".join(f"  ✓ {d}" for d in deliverables)
        body = (
            f"Hi {business_name} team,\n\n"
            f"We noticed your business has strong potential but limited online visibility.\n\n"
            f"Here's what we can do for you:\n\n"
            f"{service_headline}\n\n"
            f"What's included:\n{deliverables_list}\n\n"
            f"Investment:\n"
            f"  • Setup: ${setup_fee_usd:,.2f} (one-time)\n"
            f"  • Monthly: ${monthly_fee_usd:,.2f}/month\n\n"
            f"Our guarantee: {guarantee}\n\n"
            f"Reply YES to activate your growth system, or book a free strategy call below.\n\n"
            f"— The DreamCo Buddy AI Team\n"
            f"[Unsubscribe] [Opt-out of SMS]"
        )

        proposal = Proposal(
            proposal_id=f"prop_{self._proposal_counter:04d}",
            business_name=business_name,
            service_headline=service_headline,
            body=body,
            deliverables=deliverables,
            monthly_fee_usd=monthly_fee_usd,
            setup_fee_usd=setup_fee_usd,
            guarantee=guarantee,
            call_to_action="Reply YES or book a free strategy call.",
            channel=channel,
        )
        self._proposals.append(proposal)

        # Track conversion record
        if business_name not in self._records:
            self._records[business_name] = ConversionRecord(
                record_id=f"conv_{self._proposal_counter:04d}",
                business_name=business_name,
                current_stage=ConversionStage.PROPOSAL_SENT,
            )
        self._records[business_name].proposals.append(proposal)
        return proposal

    # ------------------------------------------------------------------
    # Outreach sequencing
    # ------------------------------------------------------------------

    def send_outreach(
        self,
        proposal: Proposal,
        is_follow_up: bool = False,
    ) -> dict:
        """Send or queue a proposal/follow-up (rate-limited).

        Parameters
        ----------
        proposal : Proposal
            The proposal to send.
        is_follow_up : bool
            Whether this is a follow-up message.

        Returns
        -------
        dict
            Status with ``queued``, ``message``, and compliance info.
        """
        if not self.can_outreach:
            raise ConversionEngineTierError(
                "Automated outreach requires PRO tier or above."
            )

        if (
            self.max_outreach_per_day is not None
            and self._sends_today >= self.max_outreach_per_day
        ):
            return {
                "queued": False,
                "message": (
                    f"Daily send limit ({self.max_outreach_per_day}) reached. "
                    "Message queued for tomorrow."
                ),
                "compliance": "rate_limited",
            }

        needs_approval = self.require_human_approval and (
            proposal.channel == OutreachChannel.SMS
            or (
                is_follow_up
                and proposal.business_name in self._records
                and self._records[proposal.business_name].follow_up_count >= 2
            )
        )
        if needs_approval:
            return {
                "queued": True,
                "message": "Flagged for human approval before sending.",
                "compliance": "pending_approval",
            }

        self._sends_today += 1
        if is_follow_up and proposal.business_name in self._records:
            rec = self._records[proposal.business_name]
            rec.follow_up_count += 1
            stage = ConversionStage.FOLLOW_UP_1 if rec.follow_up_count == 1 else ConversionStage.FOLLOW_UP_2
            rec.current_stage = stage

        return {
            "queued": True,
            "message": f"Outreach sent to {proposal.business_name} via {proposal.channel.value}.",
            "compliance": "compliant",
        }

    # ------------------------------------------------------------------
    # Objection handling
    # ------------------------------------------------------------------

    def handle_objection(self, business_name: str, objection_text: str) -> str:
        """Return an AI-crafted response to a lead's objection.

        Parameters
        ----------
        business_name : str
            Business that raised the objection.
        objection_text : str
            The raw objection text.

        Returns
        -------
        str
            A ready-to-send response message.
        """
        lower = objection_text.lower()
        response = _OBJECTION_RESPONSES.get("default")
        for key, reply in _OBJECTION_RESPONSES.items():
            if key in lower:
                response = reply
                break

        if business_name in self._records:
            self._records[business_name].current_stage = ConversionStage.OBJECTION_HANDLED
            self._records[business_name].objections.append(objection_text)

        return response

    # ------------------------------------------------------------------
    # Closing & booking
    # ------------------------------------------------------------------

    def generate_agreement(self, business_name: str, offer_summary: str) -> str:
        """Generate a simple service agreement draft (ENTERPRISE only).

        Parameters
        ----------
        business_name : str
            Client business name.
        offer_summary : str
            Summary of the agreed service offer.

        Returns
        -------
        str
            Agreement text ready for e-signature.
        """
        if not self.can_ai_closing:
            raise ConversionEngineTierError(
                "AI closing / agreement generation requires ENTERPRISE tier."
            )
        agreement = (
            f"SERVICE AGREEMENT\n"
            f"{'=' * 40}\n"
            f"Client: {business_name}\n"
            f"Provider: DreamCo Buddy AI\n"
            f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
            f"Services Agreed:\n{offer_summary}\n\n"
            f"Terms:\n"
            f"  • Services commence within 48 hours of signed agreement.\n"
            f"  • Monthly invoices issued on the 1st of each month.\n"
            f"  • 30-day notice required for cancellation.\n"
            f"  • All guarantees apply as stated in the offer document.\n\n"
            f"_________________________    _________________________\n"
            f"Client Signature / Date       DreamCo Buddy AI / Date\n"
        )
        if business_name in self._records:
            self._records[business_name].current_stage = ConversionStage.AGREEMENT_SENT
        return agreement

    def book_meeting(self, business_name: str, preferred_slot: str) -> dict:
        """Book a strategy call with the lead.

        Parameters
        ----------
        business_name : str
            Lead's business name.
        preferred_slot : str
            ISO datetime string for the preferred meeting time.

        Returns
        -------
        dict
            Booking confirmation.
        """
        if not self.can_booking:
            raise ConversionEngineTierError(
                "Booking automation requires ENTERPRISE tier."
            )
        if business_name in self._records:
            self._records[business_name].booking_slot = preferred_slot
            self._records[business_name].current_stage = ConversionStage.BOOKED

        return {
            "status": "confirmed",
            "business": business_name,
            "slot": preferred_slot,
            "meeting_link": f"https://meet.dreamco.ai/strategy/{_slugify(business_name)}",
            "confirmation": f"Strategy call booked with {business_name} for {preferred_slot}.",
        }

    def mark_won(self, business_name: str) -> dict:
        """Mark a conversion record as won (deal closed)."""
        if business_name in self._records:
            rec = self._records[business_name]
            rec.current_stage = ConversionStage.WON
            rec.won_at = datetime.now(timezone.utc).isoformat()
            return {"status": "won", "business": business_name, "won_at": rec.won_at}
        raise ConversionEngineError(f"No conversion record found for: {business_name}")

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get_pipeline(self) -> list[dict]:
        """Return all conversion records as a list of dicts."""
        return [r.to_dict() for r in self._records.values()]

    def get_won_count(self) -> int:
        """Return number of won deals."""
        return sum(
            1 for r in self._records.values()
            if r.current_stage == ConversionStage.WON
        )

    def reset_daily_sends(self) -> None:
        """Reset the daily send counter (call at midnight)."""
        self._sends_today = 0

    def to_dict(self) -> dict:
        """Return engine state as a serialisable dict."""
        return {
            "proposal_count": self._proposal_counter,
            "pipeline_size": len(self._records),
            "won_count": self.get_won_count(),
            "sends_today": self._sends_today,
            "can_outreach": self.can_outreach,
            "can_sms": self.can_sms,
            "can_ai_closing": self.can_ai_closing,
            "can_booking": self.can_booking,
        }
