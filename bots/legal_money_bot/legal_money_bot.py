"""LegalMoneyBot — AI-powered legal claim discovery and settlement assistant.

Modules
-------
1. Claim Finder      – Discovers active class actions and settlements via public
                       datasets (PACER mock, FTC complaints, consumer databases).
2. Smart Questionnaire – Auto-eligibility assessment for discovered claims.
3. Settlement Maximizer AI – Negotiation tactics, evidence handling guidance, and
                       payout estimation.
4. Lawyer Matching   – Connects users with contingency-based attorneys.
5. Auto-Filing       – Prepares and submits claim forms on behalf of the user.
6. Referral Tracking – Tracks referral codes and rewards.
7. Notifications     – Sends status updates for active claims.

Legal Disclaimer
----------------
This bot provides educational information and claim discovery assistance only.
It is not a substitute for legal advice. All settlement figures are estimates.
DreamCo does not guarantee any earnings or claim outcomes. Users are encouraged
to consult a qualified attorney for legal decisions.
"""

from __future__ import annotations

import sys
import os
import uuid
import math
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.legal_money_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LegalMoneyBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Mock datasets
# ---------------------------------------------------------------------------

_MOCK_CLASS_ACTIONS = [
    {
        "case_id": "CA-2024-001",
        "title": "Data Breach Settlement – Major Retailer",
        "source": "PACER",
        "category": "data_breach",
        "deadline": "2025-06-30",
        "estimated_payout_usd": 125.0,
        "status": "open",
        "eligibility_criteria": ["us_resident", "shopped_at_retailer_2020_2023"],
        "settlement_fund_usd": 5_000_000,
        "claimants_registered": 18_000,
    },
    {
        "case_id": "CA-2024-002",
        "title": "Overdraft Fee Class Action – Regional Bank",
        "source": "PACER",
        "category": "banking_fees",
        "deadline": "2025-08-15",
        "estimated_payout_usd": 275.0,
        "status": "open",
        "eligibility_criteria": ["bank_account_2018_2022", "charged_overdraft_fee"],
        "settlement_fund_usd": 12_000_000,
        "claimants_registered": 7_200,
    },
    {
        "case_id": "CA-2024-003",
        "title": "Robocall Violations – Telecom Company",
        "source": "FTC",
        "category": "robocall",
        "deadline": "2025-05-01",
        "estimated_payout_usd": 60.0,
        "status": "open",
        "eligibility_criteria": ["received_robocalls_2019_2023"],
        "settlement_fund_usd": 3_200_000,
        "claimants_registered": 42_000,
    },
    {
        "case_id": "CA-2024-004",
        "title": "Wage Theft Settlement – Fast Food Chain",
        "source": "PACER",
        "category": "wage_theft",
        "deadline": "2025-09-20",
        "estimated_payout_usd": 450.0,
        "status": "open",
        "eligibility_criteria": ["employed_by_chain_2017_2023", "hourly_employee"],
        "settlement_fund_usd": 8_500_000,
        "claimants_registered": 3_100,
    },
    {
        "case_id": "CA-2024-005",
        "title": "Student Loan Servicer Misconduct",
        "source": "PACER",
        "category": "student_loans",
        "deadline": "2025-12-01",
        "estimated_payout_usd": 1_200.0,
        "status": "open",
        "eligibility_criteria": ["federal_student_loan_2010_2022", "misapplied_payments"],
        "settlement_fund_usd": 45_000_000,
        "claimants_registered": 9_800,
    },
    {
        "case_id": "CA-2024-006",
        "title": "Defective Product – Auto Airbag Recall",
        "source": "PACER",
        "category": "product_defect",
        "deadline": "2026-03-15",
        "estimated_payout_usd": 700.0,
        "status": "open",
        "eligibility_criteria": ["owns_affected_vehicle_model"],
        "settlement_fund_usd": 22_000_000,
        "claimants_registered": 5_500,
    },
    {
        "case_id": "CA-2024-007",
        "title": "Junk Fees – Cable Provider Settlement",
        "source": "FTC",
        "category": "junk_fees",
        "deadline": "2025-07-31",
        "estimated_payout_usd": 85.0,
        "status": "open",
        "eligibility_criteria": ["cable_subscriber_2015_2023"],
        "settlement_fund_usd": 6_100_000,
        "claimants_registered": 51_000,
    },
    {
        "case_id": "CA-2024-008",
        "title": "False Advertising – Health Supplement",
        "source": "FTC",
        "category": "false_advertising",
        "deadline": "2025-04-30",
        "estimated_payout_usd": 45.0,
        "status": "open",
        "eligibility_criteria": ["purchased_product_2018_2023"],
        "settlement_fund_usd": 1_800_000,
        "claimants_registered": 28_000,
    },
]

_MOCK_LAWYERS = [
    {
        "lawyer_id": "LAW-001",
        "name": "Rivera & Associates",
        "specialties": ["data_breach", "consumer_protection", "banking_fees"],
        "contingency_fee_pct": 33.0,
        "state_bar": "CA",
        "licensed_states": ["CA", "NY", "TX", "FL"],
        "rating": 4.8,
        "avg_settlement_usd": 12_500,
        "cases_won": 142,
        "contact": "info@riveralaw.example.com",
    },
    {
        "lawyer_id": "LAW-002",
        "name": "Thompson Legal Group",
        "specialties": ["wage_theft", "employment", "class_action"],
        "contingency_fee_pct": 30.0,
        "state_bar": "TX",
        "licensed_states": ["TX", "OK", "LA", "AR"],
        "rating": 4.6,
        "avg_settlement_usd": 8_200,
        "cases_won": 89,
        "contact": "info@thompsonlegal.example.com",
    },
    {
        "lawyer_id": "LAW-003",
        "name": "Sterling Consumer Law",
        "specialties": ["student_loans", "false_advertising", "junk_fees"],
        "contingency_fee_pct": 25.0,
        "state_bar": "NY",
        "licensed_states": ["NY", "NJ", "CT", "MA"],
        "rating": 4.9,
        "avg_settlement_usd": 18_000,
        "cases_won": 201,
        "contact": "info@sterlingconsumer.example.com",
    },
    {
        "lawyer_id": "LAW-004",
        "name": "Park & Kim LLP",
        "specialties": ["product_defect", "personal_injury", "class_action"],
        "contingency_fee_pct": 35.0,
        "state_bar": "IL",
        "licensed_states": ["IL", "WI", "IN", "MO"],
        "rating": 4.7,
        "avg_settlement_usd": 32_000,
        "cases_won": 315,
        "contact": "info@parkkim.example.com",
    },
    {
        "lawyer_id": "LAW-005",
        "name": "Coastal Rights Attorneys",
        "specialties": ["robocall", "privacy", "consumer_protection"],
        "contingency_fee_pct": 30.0,
        "state_bar": "FL",
        "licensed_states": ["FL", "GA", "SC", "NC"],
        "rating": 4.5,
        "avg_settlement_usd": 5_800,
        "cases_won": 67,
        "contact": "info@coastalrights.example.com",
    },
]

_NEGOTIATION_TACTICS = [
    {
        "tactic": "Document Everything",
        "description": (
            "Compile all receipts, emails, screenshots, and transaction records "
            "related to your claim. Courts and settlement administrators value "
            "well-documented evidence."
        ),
        "impact": "high",
    },
    {
        "tactic": "Submit Early",
        "description": (
            "Filing your claim early can sometimes allow flexibility before fund "
            "caps are hit. Some settlements apply a pro-rata reduction when "
            "claimant numbers exceed projections."
        ),
        "impact": "medium",
    },
    {
        "tactic": "Upgrade Your Claim Class",
        "description": (
            "Many class actions have tiered compensation (e.g., 'Tier 1' for "
            "documented harm, 'Tier 2' for general class members). Providing "
            "supporting evidence can move you into a higher tier."
        ),
        "impact": "high",
    },
    {
        "tactic": "Avoid Opt-Out Deadlines",
        "description": (
            "If you want to pursue individual litigation for a potentially larger "
            "recovery, you must opt out of the class action before the deadline. "
            "Consult an attorney before opting out."
        ),
        "impact": "high",
    },
    {
        "tactic": "Track Claim Status",
        "description": (
            "Monitor your claim status regularly. Settlement administrators "
            "sometimes request additional documentation within short deadlines."
        ),
        "impact": "medium",
    },
    {
        "tactic": "Group Claims with Family",
        "description": (
            "If multiple household members qualify, file separate claims for each "
            "eligible person to maximize the total payout."
        ),
        "impact": "high",
    },
]

_QUESTIONNAIRE_TOPICS = {
    "data_breach": [
        "Were you a customer or account holder between the affected dates?",
        "Did you receive a breach notification letter?",
        "Did you experience any unauthorized charges or identity theft?",
        "Do you have records such as account statements or notification emails?",
    ],
    "banking_fees": [
        "Did you hold a checking or savings account during the claim period?",
        "Were overdraft or maintenance fees charged to your account?",
        "Do you have bank statements showing the fees?",
        "Did you request a fee reversal that was denied?",
    ],
    "robocall": [
        "Did you receive unsolicited calls from an automated dialing system?",
        "Were calls made to your mobile phone without prior written consent?",
        "Do you have call logs or voicemails as evidence?",
        "Did you register your number on the Do Not Call Registry?",
    ],
    "wage_theft": [
        "Were you employed by the defendant company during the claim period?",
        "Were you paid hourly wages?",
        "Were you denied overtime pay for hours worked over 40/week?",
        "Do you have pay stubs or employment records?",
    ],
    "student_loans": [
        "Did you hold a federal student loan serviced by the defendant?",
        "Were your payments misapplied or incorrectly processed?",
        "Did you experience a change in loan status that you did not authorize?",
        "Do you have loan statements or correspondence with the servicer?",
    ],
    "product_defect": [
        "Do you own or did you own the affected product model?",
        "Did you experience the defect described in the recall notice?",
        "Do you have proof of purchase (receipt, registration, or VIN record)?",
        "Were you injured or did you incur repair costs due to the defect?",
    ],
    "junk_fees": [
        "Were you a subscriber during the affected period?",
        "Were unexpected fees added to your bill?",
        "Do you have billing statements showing the contested fees?",
        "Did you dispute the fees with the company?",
    ],
    "false_advertising": [
        "Did you purchase the product within the claim period?",
        "Did you rely on the advertising claim when making your purchase?",
        "Do you have a receipt or proof of purchase?",
        "Did the product fail to deliver the advertised benefit?",
    ],
}


# ---------------------------------------------------------------------------
# Main Bot
# ---------------------------------------------------------------------------

class LegalMoneyBot:
    """
    Tier-aware AI-powered legal claim discovery and settlement assistant.

    Legal Disclaimer: This bot provides educational information only. It is not
    legal advice. Consult a qualified attorney before making legal decisions.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    user_id : str | None
        Optional identifier for the current user session.
    """

    DISCLAIMER = (
        "LEGAL DISCLAIMER: LegalMoneyBot provides educational information and "
        "claim discovery assistance only. It is NOT legal advice. All settlement "
        "figures are estimates and are not guaranteed. DreamCo Technologies does "
        "not guarantee any earnings or claim outcomes. Consult a qualified "
        "attorney for legal decisions. Compliant with U.S. regulatory guidelines."
    )

    def __init__(self, tier: Tier = Tier.FREE, user_id: Optional[str] = None) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self.user_id = user_id or str(uuid.uuid4())
        self._questionnaire_count = 0
        self._active_claims: list[dict] = []
        self._referral_code: Optional[str] = None
        self._referrals: list[dict] = []
        self._notifications: list[dict] = []
        self._filed_claims: list[dict] = []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_tier(self, required: Tier, feature: str) -> None:
        """Raise LegalMoneyBotTierError if current tier is below required."""
        tier_order = [Tier.FREE, Tier.PRO, Tier.ENTERPRISE]
        if tier_order.index(self.tier) < tier_order.index(required):
            raise LegalMoneyBotTierError(
                f"'{feature}' requires {required.value.upper()} tier or above. "
                f"Current tier: {self.tier.value.upper()}. "
                f"Upgrade to unlock this feature."
            )

    # ------------------------------------------------------------------
    # 1. Claim Finder
    # ------------------------------------------------------------------

    def find_claims(
        self,
        categories: Optional[list[str]] = None,
        state: Optional[str] = None,
        sources: Optional[list[str]] = None,
    ) -> list[dict]:
        """Discover active class action settlements.

        FREE tier: up to 3 basic results from public databases.
        PRO+: all results with PACER and FTC dataset scanning.
        ENTERPRISE: all results + bulk processing metadata.

        Parameters
        ----------
        categories : list[str] | None
            Filter by claim category (e.g. ``["data_breach", "banking_fees"]``).
        state : str | None
            Filter by 2-letter U.S. state code for lawyer licensing.
        sources : list[str] | None
            Filter by source (``"PACER"``, ``"FTC"``).
            PRO+ required to filter by ``"PACER"`` or ``"FTC"`` independently.
        """
        results = list(_MOCK_CLASS_ACTIONS)

        if sources:
            pacer_ftc_sources = {"PACER", "FTC"}
            requested_restricted = set(s.upper() for s in sources) & pacer_ftc_sources
            if requested_restricted:
                self._require_tier(Tier.PRO, "PACER/FTC source filtering")

        if categories:
            cats_lower = [c.lower() for c in categories]
            results = [r for r in results if r["category"] in cats_lower]

        if sources:
            srcs_upper = [s.upper() for s in sources]
            results = [r for r in results if r["source"] in srcs_upper]

        if self.tier == Tier.FREE:
            results = results[:3]

        return [
            {
                **r,
                "disclaimer": self.DISCLAIMER,
                "tier": self.tier.value,
            }
            for r in results
        ]

    # ------------------------------------------------------------------
    # 2. Smart Questionnaire
    # ------------------------------------------------------------------

    def run_eligibility_questionnaire(self, case_id: str) -> dict:
        """Return eligibility questionnaire for a specific case.

        FREE tier: 3 questionnaire runs per session.
        PRO+: unlimited.

        Returns
        -------
        dict with keys: ``case_id``, ``questions``, ``score_guidance``,
        ``disclaimer``.
        """
        if self.tier == Tier.FREE:
            if self._questionnaire_count >= 3:
                raise LegalMoneyBotTierError(
                    "FREE tier is limited to 3 eligibility questionnaire checks "
                    "per session. Upgrade to PRO for unlimited checks."
                )
            self._questionnaire_count += 1

        case = next((c for c in _MOCK_CLASS_ACTIONS if c["case_id"] == case_id), None)
        if case is None:
            return {
                "case_id": case_id,
                "error": "Case not found in the current dataset.",
                "disclaimer": self.DISCLAIMER,
            }

        questions = _QUESTIONNAIRE_TOPICS.get(case["category"], [
            "Can you confirm you were affected by the events described in the settlement?",
            "Do you have supporting documentation?",
        ])

        return {
            "case_id": case_id,
            "case_title": case["title"],
            "category": case["category"],
            "questions": questions,
            "eligibility_criteria": case["eligibility_criteria"],
            "score_guidance": (
                f"Answer 'yes' to all {len(questions)} questions to maximize "
                "your eligibility score. Each affirmative answer with supporting "
                "documentation increases your estimated payout."
            ),
            "disclaimer": self.DISCLAIMER,
            "tier": self.tier.value,
        }

    def score_eligibility(self, case_id: str, answers: dict[str, bool]) -> dict:
        """Score eligibility based on questionnaire answers.

        PRO+ feature.

        Parameters
        ----------
        case_id : str
            The case to score against.
        answers : dict[str, bool]
            Mapping of question text (or index key) to bool answer.

        Returns
        -------
        dict with ``eligibility_score`` (0–100), ``estimated_payout_usd``,
        ``recommendation``, and ``disclaimer``.
        """
        self._require_tier(Tier.PRO, "eligibility_scoring")

        case = next((c for c in _MOCK_CLASS_ACTIONS if c["case_id"] == case_id), None)
        if case is None:
            return {"case_id": case_id, "error": "Case not found.", "disclaimer": self.DISCLAIMER}

        total_questions = len(answers)
        if total_questions == 0:
            return {
                "case_id": case_id,
                "eligibility_score": 0,
                "estimated_payout_usd": 0.0,
                "recommendation": "No answers provided.",
                "disclaimer": self.DISCLAIMER,
            }

        yes_count = sum(1 for v in answers.values() if v)
        score = round((yes_count / total_questions) * 100)

        base_payout = case["estimated_payout_usd"]
        estimated_payout = round(base_payout * (score / 100), 2)

        if score >= 80:
            recommendation = (
                "Strong eligibility. Proceed with filing your claim. "
                "Gather all supporting documents before submission."
            )
        elif score >= 50:
            recommendation = (
                "Moderate eligibility. You may qualify — consider consulting "
                "a contingency attorney to strengthen your claim."
            )
        else:
            recommendation = (
                "Low eligibility score. Review the eligibility criteria and "
                "consult an attorney if you believe you have a valid claim."
            )

        return {
            "case_id": case_id,
            "case_title": case["title"],
            "eligibility_score": score,
            "estimated_payout_usd": estimated_payout,
            "yes_answers": yes_count,
            "total_questions": total_questions,
            "recommendation": recommendation,
            "disclaimer": self.DISCLAIMER,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # 3. Settlement Maximizer AI
    # ------------------------------------------------------------------

    def get_settlement_tactics(self, case_id: Optional[str] = None) -> dict:
        """Return AI-generated negotiation tactics and evidence guidance.

        PRO+ feature.

        Parameters
        ----------
        case_id : str | None
            Optional case ID for case-specific advice.
        """
        self._require_tier(Tier.PRO, "settlement_maximizer")

        case_context: Optional[dict] = None
        if case_id:
            case_context = next(
                (c for c in _MOCK_CLASS_ACTIONS if c["case_id"] == case_id), None
            )

        tactics = list(_NEGOTIATION_TACTICS)

        result: dict = {
            "tactics": tactics,
            "evidence_checklist": [
                "Receipts or proof of purchase",
                "Bank or account statements",
                "Correspondence (emails, letters, texts) with the defendant",
                "Screenshots of advertisements or product claims",
                "Notification letters (data breach notices, recall notices)",
                "Employment records (pay stubs, offer letters) if applicable",
                "Medical or repair bills if applicable",
            ],
            "disclaimer": self.DISCLAIMER,
            "tier": self.tier.value,
        }

        if case_context:
            result["case_title"] = case_context["title"]
            result["estimated_payout_usd"] = case_context["estimated_payout_usd"]
            result["settlement_fund_usd"] = case_context["settlement_fund_usd"]
            result["deadline"] = case_context["deadline"]
            result["category_specific_advice"] = (
                f"For {case_context['category'].replace('_', ' ')} claims: "
                "Focus on documenting the direct financial harm you experienced. "
                "Settlement administrators give priority to claimants who provide "
                "concrete, verifiable records."
            )

        return result

    # ------------------------------------------------------------------
    # 4. Lawyer Matching
    # ------------------------------------------------------------------

    def match_lawyers(
        self,
        case_id: Optional[str] = None,
        state: Optional[str] = None,
        specialty: Optional[str] = None,
    ) -> list[dict]:
        """Match user with contingency-based attorneys.

        PRO+ feature.

        Parameters
        ----------
        case_id : str | None
            Auto-detects category and state from the case.
        state : str | None
            2-letter U.S. state code filter.
        specialty : str | None
            Legal specialty filter (e.g. ``"data_breach"``).
        """
        self._require_tier(Tier.PRO, "lawyer_matching")

        lawyers = list(_MOCK_LAWYERS)

        effective_specialty = specialty
        if case_id and not effective_specialty:
            case = next((c for c in _MOCK_CLASS_ACTIONS if c["case_id"] == case_id), None)
            if case:
                effective_specialty = case["category"]

        if effective_specialty:
            lawyers = [
                lw for lw in lawyers
                if effective_specialty in lw["specialties"]
            ]

        if state:
            state_upper = state.upper()
            lawyers = [
                lw for lw in lawyers
                if state_upper in lw["licensed_states"]
            ]

        lawyers.sort(key=lambda lw: lw["rating"], reverse=True)

        return [
            {
                **lw,
                "contingency_note": (
                    f"No upfront cost. {lw['name']} charges {lw['contingency_fee_pct']:.0f}% "
                    "only if you win."
                ),
                "disclaimer": self.DISCLAIMER,
                "tier": self.tier.value,
            }
            for lw in lawyers
        ]

    # ------------------------------------------------------------------
    # 5. Auto-Filing Assistance
    # ------------------------------------------------------------------

    def prepare_claim_filing(self, case_id: str, user_profile: dict) -> dict:
        """Prepare an auto-filing package for a claim.

        PRO+ feature.

        Parameters
        ----------
        case_id : str
            The case to file against.
        user_profile : dict
            Must include ``name`` and ``email``. Optional keys:
            ``phone``, ``address``, ``evidence_docs``.

        Returns
        -------
        dict with ``filing_id``, ``form_data``, ``submission_checklist``,
        ``estimated_payout_usd``, and ``disclaimer``.
        """
        self._require_tier(Tier.PRO, "auto_filing")

        case = next((c for c in _MOCK_CLASS_ACTIONS if c["case_id"] == case_id), None)
        if case is None:
            return {
                "case_id": case_id,
                "error": "Case not found.",
                "disclaimer": self.DISCLAIMER,
            }

        required_fields = ["name", "email"]
        missing = [f for f in required_fields if not user_profile.get(f)]
        if missing:
            return {
                "case_id": case_id,
                "error": f"Missing required profile fields: {missing}",
                "disclaimer": self.DISCLAIMER,
            }

        filing_id = f"FILING-{case_id}-{str(uuid.uuid4())[:8].upper()}"
        form_data = {
            "claimant_name": user_profile["name"],
            "claimant_email": user_profile["email"],
            "claimant_phone": user_profile.get("phone", ""),
            "claimant_address": user_profile.get("address", ""),
            "case_id": case_id,
            "case_title": case["title"],
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }

        checklist = [
            f"✓ Complete all fields in the claim form for {case['title']}",
            f"✓ Attach supporting documents (see evidence checklist)",
            f"✓ Submit before the deadline: {case['deadline']}",
            "✓ Save your filing confirmation number",
            "✓ Monitor your email for follow-up requests from the administrator",
        ]

        filing_record = {
            "filing_id": filing_id,
            "case_id": case_id,
            "user_id": self.user_id,
            "status": "prepared",
        }
        self._filed_claims.append(filing_record)

        self._add_notification(
            f"Claim filing prepared for {case['title']}. Filing ID: {filing_id}"
        )

        return {
            "filing_id": filing_id,
            "case_id": case_id,
            "case_title": case["title"],
            "form_data": form_data,
            "submission_checklist": checklist,
            "estimated_payout_usd": case["estimated_payout_usd"],
            "deadline": case["deadline"],
            "disclaimer": self.DISCLAIMER,
            "tier": self.tier.value,
        }

    def get_filed_claims(self) -> list[dict]:
        """Return all claims filed in this session (PRO+)."""
        self._require_tier(Tier.PRO, "auto_filing")
        return list(self._filed_claims)

    # ------------------------------------------------------------------
    # 6. Referral Tracking
    # ------------------------------------------------------------------

    def generate_referral_code(self) -> dict:
        """Generate a unique referral code for the user (PRO+)."""
        self._require_tier(Tier.PRO, "referral_tracking")

        if not self._referral_code:
            self._referral_code = f"LMB-{self.user_id[:8].upper()}"

        return {
            "referral_code": self._referral_code,
            "user_id": self.user_id,
            "reward_per_referral_usd": 10.0,
            "description": (
                "Share your referral code with friends. When they subscribe to "
                "PRO or ENTERPRISE, you earn $10 per referral."
            ),
            "tier": self.tier.value,
        }

    def record_referral(self, referred_user_id: str, plan: str = "pro") -> dict:
        """Record a successful referral (PRO+)."""
        self._require_tier(Tier.PRO, "referral_tracking")

        if not self._referral_code:
            self.generate_referral_code()

        reward_usd = 10.0 if plan == "pro" else 25.0

        referral = {
            "referral_id": str(uuid.uuid4())[:8].upper(),
            "referred_user_id": referred_user_id,
            "referral_code": self._referral_code,
            "plan": plan,
            "reward_usd": reward_usd,
            "status": "confirmed",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        self._referrals.append(referral)

        self._add_notification(
            f"Referral confirmed for user {referred_user_id}. "
            f"You earned ${reward_usd:.2f}!"
        )

        return referral

    def get_referral_summary(self) -> dict:
        """Return referral stats and total earnings (PRO+)."""
        self._require_tier(Tier.PRO, "referral_tracking")

        total_earned = sum(r["reward_usd"] for r in self._referrals)
        return {
            "referral_code": self._referral_code,
            "total_referrals": len(self._referrals),
            "total_earned_usd": round(total_earned, 2),
            "referrals": list(self._referrals),
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # 7. Notifications
    # ------------------------------------------------------------------

    def _add_notification(self, message: str) -> None:
        """Internal helper to queue a notification."""
        self._notifications.append(
            {
                "notification_id": str(uuid.uuid4())[:8].upper(),
                "message": message,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "read": False,
            }
        )

    def get_notifications(self) -> list[dict]:
        """Return all pending notifications (PRO+)."""
        self._require_tier(Tier.PRO, "notifications")
        return list(self._notifications)

    def mark_notification_read(self, notification_id: str) -> dict:
        """Mark a notification as read (PRO+)."""
        self._require_tier(Tier.PRO, "notifications")

        for n in self._notifications:
            if n["notification_id"] == notification_id:
                n["read"] = True
                return {"status": "ok", "notification_id": notification_id}

        return {"status": "not_found", "notification_id": notification_id}

    # ------------------------------------------------------------------
    # 8. Analytics (ENTERPRISE+)
    # ------------------------------------------------------------------

    def get_analytics(self) -> dict:
        """Return usage analytics (ENTERPRISE+)."""
        self._require_tier(Tier.ENTERPRISE, "analytics")

        total_potential = sum(c["estimated_payout_usd"] for c in _MOCK_CLASS_ACTIONS)
        categories = {}
        for c in _MOCK_CLASS_ACTIONS:
            categories[c["category"]] = categories.get(c["category"], 0) + 1

        return {
            "total_active_cases": len(_MOCK_CLASS_ACTIONS),
            "total_potential_payout_usd": round(total_potential, 2),
            "claims_filed_this_session": len(self._filed_claims),
            "referrals_total": len(self._referrals),
            "notifications_unread": sum(1 for n in self._notifications if not n["read"]),
            "questionnaire_runs": self._questionnaire_count,
            "cases_by_category": categories,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Summary and description
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return a summary of active claims and session status."""
        claims = self.find_claims()
        return {
            "user_id": self.user_id,
            "tier": self.tier.value,
            "active_cases_available": len(claims),
            "total_potential_payout_usd": round(
                sum(c["estimated_payout_usd"] for c in claims), 2
            ),
            "claims_filed_this_session": len(self._filed_claims),
            "features": BOT_FEATURES[self.tier.value],
            "disclaimer": self.DISCLAIMER,
        }

    def describe_tier(self) -> str:
        """Print and return a human-readable tier description."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} LegalMoneyBot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for feat in info["features"]:
            lines.append(f"  \u2713 {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def chat(self, message: str) -> dict:
        """Natural-language routing for the bot."""
        msg = message.lower()

        if any(kw in msg for kw in ("find claim", "search claim", "discover claim", "class action")):
            claims = self.find_claims()
            return {
                "message": f"Found {len(claims)} active claims you may qualify for.",
                "data": claims,
            }

        if any(kw in msg for kw in ("questionnaire", "eligibility", "qualify", "am i eligible")):
            return {
                "message": (
                    "Use run_eligibility_questionnaire(case_id) to check your "
                    "eligibility for a specific case."
                ),
                "data": None,
            }

        if any(kw in msg for kw in ("settle", "tactic", "maximize", "negotiate", "evidence")):
            if self.tier == Tier.FREE:
                return {
                    "message": (
                        "Settlement Maximizer AI requires PRO tier or above. Upgrade to unlock!"
                    ),
                    "data": None,
                }
            tactics = self.get_settlement_tactics()
            return {
                "message": f"Here are {len(tactics['tactics'])} settlement tactics.",
                "data": tactics,
            }

        if any(kw in msg for kw in ("lawyer", "attorney", "legal help")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Lawyer matching requires PRO tier or above. Upgrade to unlock!",
                    "data": None,
                }
            lawyers = self.match_lawyers()
            return {
                "message": f"Found {len(lawyers)} contingency-based attorneys.",
                "data": lawyers,
            }

        if any(kw in msg for kw in ("referral", "refer a friend", "invite")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Referral tracking requires PRO tier or above. Upgrade to unlock!",
                    "data": None,
                }
            ref = self.generate_referral_code()
            return {
                "message": f"Your referral code is {ref['referral_code']}.",
                "data": ref,
            }

        if any(kw in msg for kw in ("notification", "update", "status")):
            if self.tier == Tier.FREE:
                return {
                    "message": "Notifications require PRO tier or above. Upgrade to unlock!",
                    "data": None,
                }
            notifications = self.get_notifications()
            return {
                "message": f"You have {len(notifications)} notification(s).",
                "data": notifications,
            }

        return {
            "message": (
                "LegalMoneyBot can help you: find claims, check eligibility, "
                "maximize settlements, match with lawyers, file claims, and "
                "track referrals. What would you like to do?"
            ),
            "data": self.get_summary(),
        }


# ---------------------------------------------------------------------------
# Module-level run() helper
# ---------------------------------------------------------------------------

def run(tier: Tier = Tier.FREE) -> None:  # pragma: no cover
    """Quick demo of the LegalMoneyBot."""
    bot = LegalMoneyBot(tier=tier, user_id="demo-user")
    bot.describe_tier()
    print()

    claims = bot.find_claims()
    print(f"Found {len(claims)} active claims.")
    for c in claims[:3]:
        print(f"  [{c['source']}] {c['title']} — est. ${c['estimated_payout_usd']:.2f}")
    print()

    if tier in (Tier.PRO, Tier.ENTERPRISE):
        q = bot.run_eligibility_questionnaire(claims[0]["case_id"])
        print(f"Questionnaire for '{q['case_title']}':")
        for i, question in enumerate(q["questions"], 1):
            print(f"  Q{i}: {question}")
        print()

        answers = {f"q{i}": True for i in range(len(q["questions"]))}
        score = bot.score_eligibility(claims[0]["case_id"], answers)
        print(f"Eligibility score: {score['eligibility_score']}/100 — {score['recommendation']}")
        print()

    print("Summary:")
    summary = bot.get_summary()
    for k, v in summary.items():
        if k not in ("disclaimer", "features"):
            print(f"  {k}: {v}")


if __name__ == "__main__":  # pragma: no cover
    run(Tier.PRO)
