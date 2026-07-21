# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""
Partnership Matchmaking System for the DreamAIInvent Hub.

Connects:
  - AI developers / AI companies
  - Independent inventors
  - Robotics manufacturers
  - Electronics / circuit design firms

Match types supported:
  - Co-development partnerships
  - Licensing agreements
  - Revenue-sharing agreements
  - IoT-focused collaborations
  - Contract manufacturing
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProfileType(Enum):
    AI_DEVELOPER = "ai_developer"
    INVENTOR = "inventor"
    ROBOTICS_MANUFACTURER = "robotics_manufacturer"
    ELECTRONICS_FIRM = "electronics_firm"
    CIRCUIT_DESIGNER = "circuit_designer"
    IOT_SPECIALIST = "iot_specialist"
    AI_COMPANY = "ai_company"


class CollaborationType(Enum):
    CO_DEVELOPMENT = "co_development"
    LICENSING = "licensing"
    REVENUE_SHARING = "revenue_sharing"
    IOT_COLLABORATION = "iot_collaboration"
    CONTRACT_MANUFACTURING = "contract_manufacturing"
    EQUITY_PARTNERSHIP = "equity_partnership"


class MatchStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ---------------------------------------------------------------------------
# Profile & Match data models
# ---------------------------------------------------------------------------

@dataclass
class Profile:
    """Represents a participant in the matchmaking system."""

    profile_id: str
    name: str
    profile_type: ProfileType
    expertise: list
    collaboration_types: list
    location: str = ""
    description: str = ""
    project_needs: list = field(default_factory=list)
    rating: float = 0.0
    completed_partnerships: int = 0
    verified: bool = False

    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "profile_type": self.profile_type.value,
            "expertise": self.expertise,
            "collaboration_types": [c.value for c in self.collaboration_types],
            "location": self.location,
            "description": self.description,
            "project_needs": self.project_needs,
            "rating": self.rating,
            "completed_partnerships": self.completed_partnerships,
            "verified": self.verified,
        }


@dataclass
class Match:
    """Represents a potential or active partnership match."""

    match_id: str
    requester_id: str
    partner_id: str
    collaboration_type: CollaborationType
    project_description: str
    status: MatchStatus = MatchStatus.PENDING
    compatibility_score: float = 0.0
    proposed_terms: dict = field(default_factory=dict)
    messages: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "requester_id": self.requester_id,
            "partner_id": self.partner_id,
            "collaboration_type": self.collaboration_type.value,
            "project_description": self.project_description,
            "status": self.status.value,
            "compatibility_score": self.compatibility_score,
            "proposed_terms": self.proposed_terms,
            "messages": self.messages,
        }


# ---------------------------------------------------------------------------
# Matchmaking Engine
# ---------------------------------------------------------------------------

class MatchmakingEngine:
    """
    Core engine that scores and surfaces compatible partnerships.
    """

    EXPERTISE_WEIGHT = 0.5
    COLLAB_TYPE_WEIGHT = 0.3
    RATING_WEIGHT = 0.2

    def __init__(self) -> None:
        self._profiles: dict[str, Profile] = {}
        self._matches: dict[str, Match] = {}
        self._match_counter: int = 0

        # Seed with representative profiles
        self._seed_profiles()

    # ------------------------------------------------------------------
    # Profile management
    # ------------------------------------------------------------------

    def register_profile(self, profile: Profile) -> str:
        """Register a new participant profile. Returns profile_id."""
        self._profiles[profile.profile_id] = profile
        return profile.profile_id

    def get_profile(self, profile_id: str) -> Optional[Profile]:
        return self._profiles.get(profile_id)

    def list_profiles(
        self,
        profile_type: Optional[ProfileType] = None,
    ) -> list:
        profiles = list(self._profiles.values())
        if profile_type:
            profiles = [p for p in profiles if p.profile_type == profile_type]
        return profiles

    # ------------------------------------------------------------------
    # Matching
    # ------------------------------------------------------------------

    def find_matches(
        self,
        profile_id: str,
        collaboration_type: Optional[CollaborationType] = None,
        min_score: float = 0.3,
        limit: int = 10,
    ) -> list:
        """
        Return a ranked list of compatible profiles for a given participant.

        Parameters
        ----------
        profile_id:         ID of the requesting profile.
        collaboration_type: Filter results to a specific collaboration type.
        min_score:          Minimum compatibility score (0–1).
        limit:              Maximum number of results.
        """
        requester = self._profiles.get(profile_id)
        if not requester:
            return []

        candidates = [
            p for p in self._profiles.values()
            if p.profile_id != profile_id
        ]
        if collaboration_type:
            candidates = [
                c for c in candidates
                if collaboration_type in c.collaboration_types
            ]

        scored = []
        for candidate in candidates:
            score = self._compute_score(requester, candidate)
            if score >= min_score:
                scored.append({"profile": candidate.to_dict(), "score": round(score, 3)})

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    def _compute_score(self, requester: Profile, candidate: Profile) -> float:
        """Compute a 0–1 compatibility score between two profiles."""
        # Expertise overlap
        req_exp = set(requester.expertise + requester.project_needs)
        cand_exp = set(candidate.expertise)
        if req_exp and cand_exp:
            exp_score = len(req_exp & cand_exp) / max(len(req_exp), len(cand_exp))
        else:
            exp_score = 0.0

        # Collaboration type overlap
        req_collab = set(requester.collaboration_types)
        cand_collab = set(candidate.collaboration_types)
        if req_collab and cand_collab:
            collab_score = len(req_collab & cand_collab) / max(len(req_collab), len(cand_collab))
        else:
            collab_score = 0.0

        # Normalised rating (0–5 → 0–1)
        rating_score = min(candidate.rating / 5.0, 1.0)

        return (
            self.EXPERTISE_WEIGHT * exp_score
            + self.COLLAB_TYPE_WEIGHT * collab_score
            + self.RATING_WEIGHT * rating_score
        )

    # ------------------------------------------------------------------
    # Match lifecycle
    # ------------------------------------------------------------------

    def create_match(
        self,
        requester_id: str,
        partner_id: str,
        collaboration_type: CollaborationType,
        project_description: str,
        proposed_terms: Optional[dict] = None,
    ) -> Match:
        """Initiate a match request between two profiles."""
        self._match_counter += 1
        match_id = f"MATCH-{self._match_counter:04d}"
        requester = self._profiles.get(requester_id)
        partner = self._profiles.get(partner_id)
        score = (
            self._compute_score(requester, partner)
            if requester and partner
            else 0.0
        )
        match = Match(
            match_id=match_id,
            requester_id=requester_id,
            partner_id=partner_id,
            collaboration_type=collaboration_type,
            project_description=project_description,
            status=MatchStatus.PENDING,
            compatibility_score=round(score, 3),
            proposed_terms=proposed_terms or {},
        )
        self._matches[match_id] = match
        return match

    def update_match_status(self, match_id: str, status: MatchStatus) -> bool:
        """Update the status of an existing match. Returns True on success."""
        match = self._matches.get(match_id)
        if not match:
            return False
        match.status = status
        return True

    def send_message(self, match_id: str, sender_id: str, message: str) -> bool:
        """Append a message to a match thread."""
        match = self._matches.get(match_id)
        if not match:
            return False
        match.messages.append({"sender_id": sender_id, "message": message})
        return True

    def get_match(self, match_id: str) -> Optional[Match]:
        return self._matches.get(match_id)

    def list_matches(self, profile_id: Optional[str] = None) -> list:
        matches = list(self._matches.values())
        if profile_id:
            matches = [
                m for m in matches
                if m.requester_id == profile_id or m.partner_id == profile_id
            ]
        return matches

    # ------------------------------------------------------------------
    # Term templates
    # ------------------------------------------------------------------

    def generate_terms_template(self, collaboration_type: CollaborationType) -> dict:
        """Return a pre-filled terms template for the given collaboration type."""
        templates = {
            CollaborationType.LICENSING: {
                "type": "licensing",
                "royalty_rate_pct": 5.0,
                "license_duration_years": 3,
                "territory": "worldwide",
                "exclusivity": False,
                "upfront_fee_usd": 0,
            },
            CollaborationType.REVENUE_SHARING: {
                "type": "revenue_sharing",
                "developer_share_pct": 30,
                "inventor_share_pct": 40,
                "manufacturer_share_pct": 30,
                "payment_frequency": "quarterly",
                "minimum_guarantee_usd": 0,
            },
            CollaborationType.CO_DEVELOPMENT: {
                "type": "co_development",
                "ip_ownership": "joint",
                "development_cost_split_pct": {"party_a": 50, "party_b": 50},
                "milestone_payments": True,
                "nda_required": True,
            },
            CollaborationType.IOT_COLLABORATION: {
                "type": "iot_collaboration",
                "data_ownership": "shared",
                "platform_fee_pct": 10,
                "api_access": True,
                "hardware_certification_required": True,
            },
            CollaborationType.CONTRACT_MANUFACTURING: {
                "type": "contract_manufacturing",
                "minimum_order_quantity": 1000,
                "unit_cost_usd": 0,
                "lead_time_days": 60,
                "quality_standard": "ISO 9001",
                "nda_required": True,
            },
            CollaborationType.EQUITY_PARTNERSHIP: {
                "type": "equity_partnership",
                "equity_stake_pct": 10,
                "vesting_period_years": 4,
                "cliff_months": 12,
                "board_seat": False,
            },
        }
        return templates.get(collaboration_type, {})

    # ------------------------------------------------------------------
    # Seed data
    # ------------------------------------------------------------------

    def _seed_profiles(self) -> None:
        seed = [
            Profile(
                profile_id="SEED-AI-001",
                name="NeuralForge Labs",
                profile_type=ProfileType.AI_COMPANY,
                expertise=["computer vision", "nlp", "edge ai", "robotics ai"],
                collaboration_types=[
                    CollaborationType.CO_DEVELOPMENT,
                    CollaborationType.LICENSING,
                    CollaborationType.REVENUE_SHARING,
                ],
                location="San Francisco, CA",
                description="AI research company specialising in embedded AI for robotics.",
                rating=4.7,
                completed_partnerships=12,
                verified=True,
            ),
            Profile(
                profile_id="SEED-INV-001",
                name="Jordan Inventions LLC",
                profile_type=ProfileType.INVENTOR,
                expertise=["mechanical design", "iot sensors", "wearables"],
                collaboration_types=[
                    CollaborationType.LICENSING,
                    CollaborationType.REVENUE_SHARING,
                    CollaborationType.EQUITY_PARTNERSHIP,
                ],
                project_needs=["computer vision", "machine learning", "firmware"],
                location="Austin, TX",
                description="Independent inventor with 3 granted patents in IoT wearables.",
                rating=4.5,
                completed_partnerships=5,
                verified=True,
            ),
            Profile(
                profile_id="SEED-ROB-001",
                name="Apex Robotics Manufacturing",
                profile_type=ProfileType.ROBOTICS_MANUFACTURER,
                expertise=["servo systems", "CNC fabrication", "embedded systems", "robotics ai"],
                collaboration_types=[
                    CollaborationType.CONTRACT_MANUFACTURING,
                    CollaborationType.CO_DEVELOPMENT,
                    CollaborationType.IOT_COLLABORATION,
                ],
                location="Detroit, MI",
                description="Full-service robotics manufacturer with ISO-certified production lines.",
                rating=4.8,
                completed_partnerships=28,
                verified=True,
            ),
            Profile(
                profile_id="SEED-ELEC-001",
                name="CircuitCraft Electronics",
                profile_type=ProfileType.ELECTRONICS_FIRM,
                expertise=["pcb design", "firmware", "iot sensors", "power management"],
                collaboration_types=[
                    CollaborationType.CO_DEVELOPMENT,
                    CollaborationType.CONTRACT_MANUFACTURING,
                    CollaborationType.IOT_COLLABORATION,
                ],
                location="Shenzhen, China",
                description="Electronics ODM specialising in IoT and consumer electronics.",
                rating=4.6,
                completed_partnerships=40,
                verified=True,
            ),
            Profile(
                profile_id="SEED-CIRC-001",
                name="Precision Circuit Designers",
                profile_type=ProfileType.CIRCUIT_DESIGNER,
                expertise=["analog circuits", "rf engineering", "mixed-signal design", "pcb layout"],
                collaboration_types=[
                    CollaborationType.CO_DEVELOPMENT,
                    CollaborationType.LICENSING,
                ],
                location="Boston, MA",
                description="Boutique circuit design studio with RF and mixed-signal expertise.",
                rating=4.9,
                completed_partnerships=15,
                verified=True,
            ),
            Profile(
                profile_id="SEED-IOT-001",
                name="SmartEdge IoT",
                profile_type=ProfileType.IOT_SPECIALIST,
                expertise=["iot architecture", "mqtt", "edge computing", "machine learning", "firmware"],
                collaboration_types=[
                    CollaborationType.IOT_COLLABORATION,
                    CollaborationType.CO_DEVELOPMENT,
                    CollaborationType.REVENUE_SHARING,
                ],
                location="Seattle, WA",
                description="End-to-end IoT platform provider connecting edge devices to cloud AI.",
                rating=4.4,
                completed_partnerships=9,
                verified=True,
            ),
        ]
        for profile in seed:
            self._profiles[profile.profile_id] = profile
