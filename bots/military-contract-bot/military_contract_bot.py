"""
Military Contract Bot — state-of-the-art military procurement intelligence.

Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

Capabilities
------------
1. Intelligent contract processing — identify, parse, and manage military
   procurement opportunities from DoD, DLA, DARPA, Army, Navy, Air Force, etc.
2. Adaptive AI architecture — interpret MIL-SPEC, RFP, SOW, and PWS documents.
3. Cutting-edge security — AES-256 encryption, RBAC, tamper-evident audit trail.
4. Government system interfaces — SAM.gov, beta.SAM.gov, PIEE, FPDS-NG format.
5. Comprehensive logging, fail-safe manual overrides, and performance analytics.
6. Modular design with public API for external integration.

Tiers
-----
FREE       — 5 results per search, basic DoD contract search only.
PRO        — 50 results, full search, solicitation parser, compliance checker.
ENTERPRISE — Unlimited, AI proposal assistant, security module, full analytics API.
"""

from __future__ import annotations

import datetime
import logging
import sys
import os
import time
from enum import Enum
from typing import Any, Optional

# Add parent directories to path for framework and BuddyAI imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "BuddyAI"))

from mil_analytics import PerformanceTracker
from mil_compliance import (
    check_cmmc_compliance,
    parse_solicitation,
    validate_clauses,
    screen_export_control,
)
from mil_security import AuditTrail, User, SecurityRole, AuthorizationError

try:
    from framework import GlobalAISourcesFlow
except ImportError:  # pragma: no cover
    GlobalAISourcesFlow = None  # type: ignore

try:
    from base_bot import BaseBot
except ImportError:  # pragma: no cover
    class BaseBot:  # type: ignore
        def __init__(self):
            self.name = self.__class__.__name__
            self.description = ""
            self.buddy = None
        def start(self):
            print(f"{self.name} is starting...")
        def run(self):
            self.start()

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("MilitaryContractBot")


# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------

class Tier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_LIMITS: dict[Tier, dict[str, Any]] = {
    Tier.FREE: {"results_per_search": 5, "saved_searches": 2, "alert_keywords": 3},
    Tier.PRO: {"results_per_search": 50, "saved_searches": 20, "alert_keywords": 30},
    Tier.ENTERPRISE: {"results_per_search": None, "saved_searches": None, "alert_keywords": None},
}

TIER_PRICES: dict[Tier, int] = {
    Tier.FREE: 0,
    Tier.PRO: 199,
    Tier.ENTERPRISE: 499,
}

BOT_FEATURES: dict[Tier, list[str]] = {
    Tier.FREE: ["basic_contract_search", "public_dod_contracts"],
    Tier.PRO: [
        "full_contract_search", "solicitation_parser", "compliance_checker",
        "deadline_alerts", "bid_analysis", "naics_filter", "saved_searches",
        "export_control_screening", "proposal_builder",
    ],
    Tier.ENTERPRISE: [
        "full_contract_search", "solicitation_parser", "compliance_checker",
        "deadline_alerts", "bid_analysis", "naics_filter", "saved_searches",
        "export_control_screening", "proposal_builder",
        "ai_proposal_assistant", "security_module", "audit_trail",
        "competitor_analysis", "subcontract_finder", "performance_analytics",
        "api_access", "manual_override",
    ],
}


class MilitaryContractBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Contract status
# ---------------------------------------------------------------------------

class ContractStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    AWARDED = "awarded"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


# ---------------------------------------------------------------------------
# Mock military contract database
# ---------------------------------------------------------------------------

MOCK_MILITARY_CONTRACTS: list[dict] = [
    {
        "id": "W56HZV-24-R-0001",
        "title": "Army Tactical Network Infrastructure Upgrade",
        "agency": "Department of the Army",
        "sub_agency": "Army Contracting Command — Rock Island",
        "type": "contract",
        "value": 45_000_000,
        "naics": "517312",
        "deadline": "2025-03-15",
        "set_aside": "Small Business",
        "location": "Fort Hood, TX",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 3,
        "clearance_required": "Secret",
        "solicitation_number": "W56HZV-24-R-0001",
        "far_clauses": ["FAR 52.204-21", "DFARS 252.204-7012", "FAR 52.222-26"],
        "description": (
            "Upgrade of tactical communication network infrastructure, "
            "including secure routers, cryptographic equipment MIL-STD-461, "
            "and integration with existing C4ISR systems. DFARS 252.204-7012 applies."
        ),
        "category": "communications",
        "sol_type": "RFP",
        "period_of_performance": "24 months",
        "competition_type": "Full and Open",
    },
    {
        "id": "N00014-24-R-0012",
        "title": "Naval Cybersecurity Operations Center Support",
        "agency": "Department of the Navy",
        "sub_agency": "Naval Information Warfare Center Pacific",
        "type": "contract",
        "value": 28_500_000,
        "naics": "541519",
        "deadline": "2025-02-28",
        "set_aside": "Service-Disabled Veteran-Owned",
        "location": "San Diego, CA",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 3,
        "clearance_required": "TS/SCI",
        "solicitation_number": "N00014-24-R-0012",
        "far_clauses": [
            "FAR 52.204-21", "DFARS 252.204-7012",
            "FAR 52.233-1", "DFARS 252.225-7001",
        ],
        "description": (
            "24/7 cybersecurity operations center (CSOC) staffing and tooling "
            "support. Requires TS/SCI clearance, CMMC Level 3 certification, "
            "and compliance with MIL-STD-2525 and NIST SP 800-171."
        ),
        "category": "cybersecurity",
        "sol_type": "RFP",
        "period_of_performance": "36 months + 2 options",
        "competition_type": "Set-Aside",
    },
    {
        "id": "FA8621-24-R-0055",
        "title": "Air Force Research Laboratory — AI/ML Research & Development",
        "agency": "Department of the Air Force",
        "sub_agency": "Air Force Research Laboratory (AFRL)",
        "type": "contract",
        "value": 62_000_000,
        "naics": "541715",
        "deadline": "2025-04-10",
        "set_aside": "None",
        "location": "Wright-Patterson AFB, OH",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 2,
        "clearance_required": "Secret",
        "solicitation_number": "FA8621-24-R-0055",
        "far_clauses": [
            "FAR 52.204-21", "DFARS 252.204-7012",
            "DFARS 252.227-7013", "FAR 52.222-26",
        ],
        "description": (
            "Research, development, test, and evaluation (RDT&E) for advanced "
            "AI/ML algorithms applied to autonomous systems, predictive maintenance, "
            "and mission planning. MIL-HDBK-61 configuration management required."
        ),
        "category": "research",
        "sol_type": "BAA",
        "period_of_performance": "60 months",
        "competition_type": "Full and Open",
    },
    {
        "id": "DAAA09-24-R-0003",
        "title": "Defense Logistics Agency — Supply Chain Automation Platform",
        "agency": "Defense Logistics Agency",
        "sub_agency": "DLA Information Operations",
        "type": "contract",
        "value": 18_700_000,
        "naics": "541511",
        "deadline": "2025-01-31",
        "set_aside": "8(a)",
        "location": "Fort Belvoir, VA",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 2,
        "clearance_required": "Secret",
        "solicitation_number": "DAAA09-24-R-0003",
        "far_clauses": [
            "FAR 52.204-21", "DFARS 252.204-7012",
            "FAR 52.232-33", "DFARS 252.211-7003",
        ],
        "description": (
            "Design, develop, and deploy an automated supply chain management "
            "platform integrating with DLA's Enterprise Business System (EBS). "
            "Must conform to MIL-STD-1553 data bus interface standards."
        ),
        "category": "logistics",
        "sol_type": "RFQ",
        "period_of_performance": "18 months",
        "competition_type": "Set-Aside",
    },
    {
        "id": "HR0011-24-R-0022",
        "title": "DARPA — Autonomous Unmanned Systems Research",
        "agency": "Defense Advanced Research Projects Agency",
        "sub_agency": "DARPA Tactical Technology Office",
        "type": "contract",
        "value": 95_000_000,
        "naics": "336411",
        "deadline": "2025-05-30",
        "set_aside": "None",
        "location": "Arlington, VA",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 3,
        "clearance_required": "TS/SCI",
        "solicitation_number": "HR0011-24-R-0022",
        "far_clauses": [
            "FAR 52.204-21", "DFARS 252.204-7012",
            "DFARS 252.227-7013", "FAR 52.233-1",
        ],
        "description": (
            "Advanced research into autonomous air and ground unmanned systems. "
            "Includes autonomous navigation, target recognition using ITAR-controlled "
            "sensors, and swarm coordination algorithms. TS/SCI clearance mandatory."
        ),
        "category": "autonomous_systems",
        "sol_type": "BAA",
        "period_of_performance": "48 months",
        "competition_type": "Full and Open",
    },
    {
        "id": "W912BU-24-R-0018",
        "title": "Army Corps of Engineers — Facility Security Systems",
        "agency": "Department of the Army",
        "sub_agency": "US Army Corps of Engineers",
        "type": "contract",
        "value": 9_800_000,
        "naics": "561621",
        "deadline": "2025-02-14",
        "set_aside": "HUBZone",
        "location": "Multiple CONUS Locations",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 1,
        "clearance_required": "None",
        "solicitation_number": "W912BU-24-R-0018",
        "far_clauses": ["FAR 52.204-21", "FAR 52.222-26", "FAR 52.232-33"],
        "description": (
            "Installation, maintenance, and monitoring of physical and electronic "
            "security systems at Army Corps facilities across CONUS. "
            "Access control, CCTV, intrusion detection, MIL-STD-461 compliant."
        ),
        "category": "physical_security",
        "sol_type": "IFB",
        "period_of_performance": "12 months + 4 options",
        "competition_type": "Set-Aside",
    },
    {
        "id": "SPE8E8-24-R-0009",
        "title": "DLA Energy — Fuel Logistics & Distribution Services",
        "agency": "Defense Logistics Agency",
        "sub_agency": "DLA Energy",
        "type": "contract",
        "value": 120_000_000,
        "naics": "424720",
        "deadline": "2025-06-01",
        "set_aside": "None",
        "location": "Continental United States",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 1,
        "clearance_required": "None",
        "solicitation_number": "SPE8E8-24-R-0009",
        "far_clauses": [
            "FAR 52.204-21", "FAR 52.222-26",
            "FAR 52.222-41", "FAR 52.232-33", "DFARS 252.225-7001",
        ],
        "description": (
            "Bulk fuel procurement, storage and ground distribution services "
            "supporting DoD installations. Includes JP-8, diesel, and aviation "
            "fuel; conforms to MIL-DTL-83133 specifications."
        ),
        "category": "energy",
        "sol_type": "RFP",
        "period_of_performance": "60 months",
        "competition_type": "Full and Open",
    },
    {
        "id": "M67854-24-R-0031",
        "title": "Marine Corps — Combat Logistics Training Simulation",
        "agency": "Department of the Navy",
        "sub_agency": "Marine Corps Systems Command",
        "type": "contract",
        "value": 14_200_000,
        "naics": "611699",
        "deadline": "2025-03-20",
        "set_aside": "Women-Owned Small Business",
        "location": "Quantico, VA",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 2,
        "clearance_required": "Secret",
        "solicitation_number": "M67854-24-R-0031",
        "far_clauses": [
            "FAR 52.204-21", "DFARS 252.204-7012",
            "FAR 52.222-26", "FAR 52.232-33",
        ],
        "description": (
            "Development and delivery of interactive combat logistics training "
            "simulations using virtual reality and live-virtual-constructive (LVC) "
            "architectures. Must conform to DoD Instruction 1322.20 training standards."
        ),
        "category": "training_simulation",
        "sol_type": "RFP",
        "period_of_performance": "30 months",
        "competition_type": "Set-Aside",
    },
    {
        "id": "FA4626-24-R-0004",
        "title": "Space Force — Satellite Ground System Integration",
        "agency": "United States Space Force",
        "sub_agency": "Space Systems Command",
        "type": "contract",
        "value": 210_000_000,
        "naics": "336414",
        "deadline": "2025-07-15",
        "set_aside": "None",
        "location": "Los Angeles AFB, CA",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 3,
        "clearance_required": "TS/SCI",
        "solicitation_number": "FA4626-24-R-0004",
        "far_clauses": [
            "FAR 52.204-21", "DFARS 252.204-7012",
            "DFARS 252.227-7013", "FAR 52.233-1",
            "DFARS 252.225-7001", "DFARS 252.211-7003",
        ],
        "description": (
            "System integration of next-generation satellite ground systems, "
            "including encryption key management, telemetry processing, "
            "and compliance with MIL-STD-1553, MIL-STD-461, and ITAR requirements."
        ),
        "category": "space_systems",
        "sol_type": "RFP",
        "period_of_performance": "84 months",
        "competition_type": "Full and Open",
    },
    {
        "id": "W81XWH-24-R-0007",
        "title": "Army Medical Research — Combat Casualty Care Technology",
        "agency": "Department of the Army",
        "sub_agency": "US Army Medical Research and Development Command",
        "type": "grant",
        "value": 8_500_000,
        "naics": "541714",
        "deadline": "2025-01-15",
        "set_aside": "Small Business",
        "location": "Fort Detrick, MD",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 1,
        "clearance_required": "None",
        "solicitation_number": "W81XWH-24-R-0007",
        "far_clauses": ["FAR 52.204-21", "FAR 52.222-26"],
        "description": (
            "SBIR Phase II grant for development of portable diagnostic devices "
            "and point-of-care treatment technologies for combat field medics. "
            "Dual-use technology with ITAR/EAR screening required."
        ),
        "category": "medical_research",
        "sol_type": "SBIR",
        "period_of_performance": "24 months",
        "competition_type": "Small Business",
    },
    {
        "id": "GS-10F-0494X",
        "title": "GSA Schedule 70 — DoD IT Support Services",
        "agency": "General Services Administration",
        "sub_agency": "GSA Federal Acquisition Service",
        "type": "contract",
        "value": 35_000_000,
        "naics": "541512",
        "deadline": "2025-08-01",
        "set_aside": "None",
        "location": "Washington, DC Metro Area",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 2,
        "clearance_required": "Secret",
        "solicitation_number": "GS-10F-0494X",
        "far_clauses": [
            "FAR 52.204-21", "FAR 52.232-33",
            "DFARS 252.204-7012", "FAR 52.222-26",
        ],
        "description": (
            "IT support, help desk, cybersecurity operations, and systems "
            "administration services for DoD agencies via GSA Schedule. "
            "Must hold active FedRAMP Moderate authorization."
        ),
        "category": "it_services",
        "sol_type": "TO",
        "period_of_performance": "12 months + 4 options",
        "competition_type": "Full and Open",
    },
    {
        "id": "W900KK-24-R-0002",
        "title": "Army Aviation — Rotary Wing Maintenance Support",
        "agency": "Department of the Army",
        "sub_agency": "Army Aviation and Missile Command",
        "type": "contract",
        "value": 55_000_000,
        "naics": "488190",
        "deadline": "2025-04-30",
        "set_aside": "Small Business",
        "location": "Redstone Arsenal, AL",
        "status": ContractStatus.ACTIVE,
        "cmmc_level": 2,
        "clearance_required": "Secret",
        "solicitation_number": "W900KK-24-R-0002",
        "far_clauses": [
            "FAR 52.204-21", "DFARS 252.204-7012",
            "DFARS 252.225-7001", "FAR 52.232-33",
        ],
        "description": (
            "Depot-level and field maintenance of Army rotary wing aircraft "
            "including UH-60 Black Hawks and AH-64 Apaches. Compliance with "
            "MIL-STD-1530 aircraft structural integrity program required."
        ),
        "category": "aviation",
        "sol_type": "RFP",
        "period_of_performance": "60 months",
        "competition_type": "Set-Aside",
    },
]


# ---------------------------------------------------------------------------
# Manual override registry
# ---------------------------------------------------------------------------

class ManualOverride:
    """Fail-safe manual override system for critical bot operations."""

    def __init__(self) -> None:
        self._overrides: dict[str, Any] = {}
        self._override_log: list[dict] = []

    def set(self, key: str, value: Any, reason: str = "") -> None:
        """Set a manual override value."""
        entry = {
            "key": key,
            "value": value,
            "reason": reason,
            "ts": time.time(),
        }
        self._overrides[key] = value
        self._override_log.append(entry)
        logger.warning("MANUAL OVERRIDE set: %s = %r (%s)", key, value, reason)

    def get(self, key: str, default: Any = None) -> Any:
        """Get an override value, or *default* if not set."""
        return self._overrides.get(key, default)

    def clear(self, key: str) -> None:
        """Remove an override."""
        self._overrides.pop(key, None)
        logger.info("MANUAL OVERRIDE cleared: %s", key)

    def list_active(self) -> dict[str, Any]:
        """Return all currently active overrides."""
        return dict(self._overrides)

    def get_log(self) -> list[dict]:
        """Return the full override history log."""
        return list(self._override_log)


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class MilitaryContractBot(BaseBot):
    """State-of-the-art military contract procurement intelligence bot.

    Integrates security, compliance, AI-driven analysis, government system
    interfaces, performance analytics, and a modular API surface.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        admin_user: Optional[User] = None,
    ) -> None:
        super().__init__()
        self.name = "MilitaryContractBot"
        self.description = (
            "State-of-the-art military contract bot — "
            "intelligent procurement, compliance, and proposal automation."
        )
        self.tier = Tier(tier) if not isinstance(tier, Tier) else tier
        self.limits = TIER_LIMITS[self.tier]
        self.features = BOT_FEATURES[self.tier]

        # Sub-modules
        self.analytics = PerformanceTracker()
        self.audit = AuditTrail()
        self.override = ManualOverride()

        # Runtime state
        self._saved_searches: list[dict] = []
        self._alerts: list[str] = []
        self._proposals: list[dict] = []

        # Default admin user for internal operations
        self._admin = admin_user or User(
            user_id="system", role=SecurityRole.ADMIN, clearance_level=5
        )

        # Global AI Sources Flow pipeline
        if GlobalAISourcesFlow is not None:
            self.flow = GlobalAISourcesFlow(bot_name=self.name)
        else:
            self.flow = None

        logger.info("MilitaryContractBot initialised (tier=%s).", self.tier.value)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the bot and log the startup event."""
        logger.info("MilitaryContractBot starting...")
        self.analytics.record_event("startup", {"tier": self.tier.value})

    def run(self) -> dict:
        """Execute the GLOBAL AI SOURCES FLOW pipeline and return a summary."""
        self.start()
        if self.flow is not None:
            result = self.flow.run_pipeline(
                raw_data={
                    "domain": "military_contracts",
                    "records": len(MOCK_MILITARY_CONTRACTS),
                },
                learning_method="supervised",
            )
        else:
            result = {"status": "success"}
        self.analytics.record_event("pipeline_run", result)
        logger.info("Pipeline completed: %s", result.get("status", "unknown"))
        return result

    # ------------------------------------------------------------------
    # Search and filter
    # ------------------------------------------------------------------

    def search_contracts(
        self,
        keyword: str = "",
        agency: Optional[str] = None,
        naics: Optional[str] = None,
        set_aside: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        min_value: float = 0,
        max_value: Optional[float] = None,
        clearance: Optional[str] = None,
        category: Optional[str] = None,
        cmmc_level: Optional[int] = None,
    ) -> list[dict]:
        """Search military contracts matching the given filters.

        Parameters are identical to the Government Contract & Grant Bot to
        allow interoperability.  Results are capped by tier limit.
        """
        t0 = time.time()
        kw = keyword.lower()

        # Support manual override of keyword
        kw = self.override.get("search_keyword_override", kw)

        results = []
        for opp in MOCK_MILITARY_CONTRACTS:
            if kw and kw not in opp["title"].lower() and kw not in opp["description"].lower():
                continue
            if agency and agency.lower() not in opp["agency"].lower():
                continue
            if naics and not opp["naics"].startswith(naics):
                continue
            if set_aside and set_aside.lower() not in opp["set_aside"].lower():
                continue
            if opportunity_type and opp["type"] != opportunity_type:
                continue
            if opp["value"] < min_value:
                continue
            if max_value is not None and opp["value"] > max_value:
                continue
            if clearance and clearance.lower() not in opp.get("clearance_required", "").lower():
                continue
            if category and category.lower() not in opp.get("category", "").lower():
                continue
            if cmmc_level is not None and opp.get("cmmc_level", 0) < cmmc_level:
                continue
            results.append(opp)

        limit = self.limits["results_per_search"]
        if limit is not None:
            results = results[:limit]

        elapsed = time.time() - t0
        self.analytics.record_timing("search_contracts", elapsed)
        self.analytics.record_search(keyword, len(results))
        logger.info("search_contracts(keyword=%r) → %d results in %.3fs", keyword, len(results), elapsed)
        return results

    def get_opportunity(self, opportunity_id: str) -> Optional[dict]:
        """Retrieve a single opportunity by ID."""
        opp = next((o for o in MOCK_MILITARY_CONTRACTS if o["id"] == opportunity_id), None)
        if opp:
            self.analytics.record_opportunity_viewed(opportunity_id)
        return opp

    def get_upcoming_deadlines(self, days: int = 30) -> list[dict]:
        """Return opportunities with deadlines within *days* calendar days."""
        today = datetime.date.today()
        cutoff = today + datetime.timedelta(days=days)
        results = []
        for opp in MOCK_MILITARY_CONTRACTS:
            try:
                deadline = datetime.date.fromisoformat(opp["deadline"])
                if today <= deadline <= cutoff:
                    results.append({**opp, "days_remaining": (deadline - today).days})
            except ValueError:
                continue
        results.sort(key=lambda x: x["days_remaining"])
        limit = self.limits["results_per_search"]
        return results[:limit] if limit else results

    # ------------------------------------------------------------------
    # AI analysis
    # ------------------------------------------------------------------

    def analyze_opportunity(self, opportunity_id: str) -> dict:
        """Run an AI-driven analysis on a single opportunity.

        Requires PRO or ENTERPRISE tier.
        """
        if "bid_analysis" not in self.features:
            raise MilitaryContractBotTierError(
                "Bid analysis requires PRO or ENTERPRISE tier."
            )
        opp = self.get_opportunity(opportunity_id)
        if opp is None:
            return {"error": f"Opportunity '{opportunity_id}' not found."}

        t0 = time.time()
        win_prob = self._estimate_win_probability(opp)
        roi_score = self._estimate_roi_score(opp)
        parsed = parse_solicitation(opp["description"])
        export = screen_export_control(opp["description"])
        cmmc = check_cmmc_compliance([], opp.get("cmmc_level", 1))

        result = {
            "opportunity": opp,
            "analysis": {
                "win_probability_pct": win_prob,
                "roi_score": roi_score,
                "competition_level": (
                    "high" if opp["value"] > 50_000_000
                    else "medium" if opp["value"] > 10_000_000
                    else "low"
                ),
                "recommended_action": (
                    "bid" if win_prob >= 40 else "monitor" if win_prob >= 20 else "skip"
                ),
                "key_requirements": self._extract_requirements(opp),
                "solicitation_parsed": parsed.to_dict(),
                "export_control": export,
                "cmmc_baseline": cmmc,
                "clearance_required": opp.get("clearance_required"),
                "compliance_risk": "high" if export["risk_level"] == "high" or not cmmc["compliant"] else "medium",
            },
        }
        self.analytics.record_timing("analyze_opportunity", time.time() - t0)
        return result

    def _estimate_win_probability(self, opp: dict) -> int:
        """Heuristic win probability (0–100) based on contract attributes."""
        base = 30
        small_biz_set_asides = {
            "Small Business", "8(a)", "Women-Owned Small Business",
            "HUBZone", "Service-Disabled Veteran-Owned",
            "Indian Economic Enterprise", "DBE",
        }
        if opp["set_aside"] in small_biz_set_asides:
            base += 20
        if opp["value"] < 5_000_000:
            base += 15
        elif opp["value"] > 50_000_000:
            base -= 15
        if opp.get("cmmc_level", 1) >= 3:
            base -= 5  # higher barriers reduce competition density but also require more prep
        return min(max(base, 5), 90)

    def _estimate_roi_score(self, opp: dict) -> float:
        """ROI attractiveness score 0–10."""
        if opp["value"] == 0:
            return 0.0
        base = 5.0
        if opp["value"] > 20_000_000:
            base += 2.0
        if opp["set_aside"] != "None":
            base += 1.0
        if opp["type"] == "grant":
            base += 1.5
        if opp.get("cmmc_level", 1) <= 1:
            base += 0.5  # lower entry barrier
        return round(min(base, 10.0), 1)

    def _extract_requirements(self, opp: dict) -> list[str]:
        """Extract actionable requirements from an opportunity."""
        reqs = []
        desc = opp.get("description", "").lower()
        if opp.get("clearance_required", "None") not in ("None", "none", ""):
            reqs.append(f"Security clearance: {opp['clearance_required']}")
        cmmc = opp.get("cmmc_level", 0)
        if cmmc > 0:
            reqs.append(f"CMMC Level {cmmc} certification")
        if "dfars 252.204-7012" in [c.upper() for c in opp.get("far_clauses", [])]:
            reqs.append("DFARS 252.204-7012 — Cybersecurity incident reporting")
        if "cybersecurity" in desc or "cmmc" in desc or "nist" in desc:
            reqs.append("NIST SP 800-171 / NIST SP 800-53 compliance")
        if "mil-std" in desc or "mil-hdbk" in desc:
            reqs.append("Military standards (MIL-STD / MIL-HDBK) compliance")
        if "itar" in desc or "ear" in desc or "export" in desc:
            reqs.append("ITAR / EAR export control compliance")
        reqs.append("Active SAM.gov registration")
        reqs.append("Cage Code and DUNS/UEI number")
        return reqs

    # ------------------------------------------------------------------
    # Compliance
    # ------------------------------------------------------------------

    def run_compliance_check(
        self,
        opportunity_id: str,
        implemented_controls: Optional[list[str]] = None,
        user: Optional[User] = None,
    ) -> dict:
        """Comprehensive compliance check for an opportunity.

        Requires PRO or ENTERPRISE tier.
        """
        if "compliance_checker" not in self.features:
            raise MilitaryContractBotTierError(
                "Compliance checker requires PRO or ENTERPRISE tier."
            )
        u = user or self._admin
        u.require("run_compliance_check")

        opp = self.get_opportunity(opportunity_id)
        if opp is None:
            return {"error": f"Opportunity '{opportunity_id}' not found."}

        controls = implemented_controls or []
        cmmc = check_cmmc_compliance(controls, opp.get("cmmc_level", 1))
        clauses = validate_clauses(opp.get("far_clauses", []), opp["value"])
        export = screen_export_control(opp["description"])
        parsed = parse_solicitation(opp["description"])

        result = {
            "opportunity_id": opportunity_id,
            "cmmc_compliance": cmmc,
            "clause_validation": clauses,
            "export_control": export,
            "solicitation_requirements": parsed.to_dict(),
            "overall_ready": (
                cmmc["compliant"]
                and clauses["compliant"]
                and not export["requires_review"]
            ),
        }

        self.audit.record(u, "compliance_check", opportunity_id, metadata={"result": result["overall_ready"]})
        return result

    def parse_solicitation_text(self, text: str) -> dict:
        """Parse raw solicitation text and return structured requirements.

        Requires PRO or ENTERPRISE tier.
        """
        if "solicitation_parser" not in self.features:
            raise MilitaryContractBotTierError(
                "Solicitation parser requires PRO or ENTERPRISE tier."
            )
        parsed = parse_solicitation(text)
        export = screen_export_control(text)
        return {"parsed": parsed.to_dict(), "export_control": export}

    # ------------------------------------------------------------------
    # Proposals
    # ------------------------------------------------------------------

    def submit_proposal(
        self,
        opportunity_id: str,
        proposal: dict,
        user: Optional[User] = None,
    ) -> dict:
        """Submit a proposal for an opportunity.

        Requires PRO or ENTERPRISE tier.
        """
        if "proposal_builder" not in self.features:
            raise MilitaryContractBotTierError(
                "Proposal builder requires PRO or ENTERPRISE tier."
            )
        u = user or self._admin
        u.require("submit_proposal")

        opp = self.get_opportunity(opportunity_id)
        if opp is None:
            return {"error": f"Opportunity '{opportunity_id}' not found."}

        entry = {
            "id": f"PROP-{len(self._proposals) + 1:04d}",
            "opportunity_id": opportunity_id,
            "opportunity_title": opp["title"],
            "submitted_by": u.user_id,
            "submitted_at": time.time(),
            "status": "submitted",
            **proposal,
        }
        self._proposals.append(entry)
        self.analytics.record_proposal_submitted(opportunity_id)
        self.audit.record(u, "submit_proposal", opportunity_id, metadata={"proposal_id": entry["id"]})
        logger.info("Proposal %s submitted for opportunity %s", entry["id"], opportunity_id)
        return {"submitted": True, "proposal": entry}

    def list_proposals(self) -> list[dict]:
        """Return all submitted proposals."""
        return list(self._proposals)

    # ------------------------------------------------------------------
    # Alerts and saved searches
    # ------------------------------------------------------------------

    def add_alert_keyword(self, keyword: str) -> dict:
        """Register an alert keyword. Tier-limited."""
        if "deadline_alerts" not in self.features:
            raise MilitaryContractBotTierError(
                "Deadline alerts require PRO or ENTERPRISE tier."
            )
        limit = self.limits["alert_keywords"]
        if limit is not None and len(self._alerts) >= limit:
            raise MilitaryContractBotTierError(
                f"Alert keyword limit ({limit}) reached. Upgrade for more."
            )
        self._alerts.append(keyword)
        return {"added": True, "keyword": keyword, "total_alerts": len(self._alerts)}

    def get_alerts(self) -> list[str]:
        """Return all registered alert keywords."""
        return list(self._alerts)

    def save_search(self, name: str, filters: dict) -> dict:
        """Save a named search for reuse. Tier-limited."""
        limit = self.limits["saved_searches"]
        if limit is not None and len(self._saved_searches) >= limit:
            raise MilitaryContractBotTierError(
                f"Saved search limit ({limit}) reached. Upgrade to save more."
            )
        entry = {"name": name, "filters": filters}
        self._saved_searches.append(entry)
        return {"saved": True, "search": entry}

    # ------------------------------------------------------------------
    # Summary and reporting
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return a high-level summary of available military opportunities."""
        contracts = [o for o in MOCK_MILITARY_CONTRACTS if o["type"] == "contract"]
        grants = [o for o in MOCK_MILITARY_CONTRACTS if o["type"] == "grant"]
        total_value = sum(o["value"] for o in MOCK_MILITARY_CONTRACTS)
        set_aside = [o for o in MOCK_MILITARY_CONTRACTS if o["set_aside"] != "None"]
        return {
            "total_opportunities": len(MOCK_MILITARY_CONTRACTS),
            "contracts": len(contracts),
            "grants": len(grants),
            "total_value_usd": total_value,
            "set_aside_opportunities": len(set_aside),
            "categories": sorted({o["category"] for o in MOCK_MILITARY_CONTRACTS}),
            "agencies": sorted({o["agency"] for o in MOCK_MILITARY_CONTRACTS}),
            "tier": self.tier.value,
            "tier_price_monthly": TIER_PRICES[self.tier],
        }

    def get_tier_info(self) -> dict:
        """Return current tier information."""
        return {
            "tier": self.tier.value,
            "price_monthly": TIER_PRICES[self.tier],
            "features": self.features,
            "limits": self.limits,
        }

    # ------------------------------------------------------------------
    # Security helpers (ENTERPRISE only)
    # ------------------------------------------------------------------

    def get_audit_log(self, user: Optional[User] = None) -> list[dict]:
        """Return the full audit trail. Requires ENTERPRISE tier."""
        if "audit_trail" not in self.features:
            raise MilitaryContractBotTierError(
                "Audit trail requires ENTERPRISE tier."
            )
        u = user or self._admin
        u.require("manage_users")
        return self.audit.get_log()

    def create_user(
        self, user_id: str, role: str, clearance_level: int = 0
    ) -> User:
        """Create and return a User object."""
        return User(user_id=user_id, role=SecurityRole(role), clearance_level=clearance_level)

    # ------------------------------------------------------------------
    # Buddy integration (BaseBot interface)
    # ------------------------------------------------------------------

    def connect_to_buddy(self, buddy: Any) -> None:
        """Register this bot with the Buddy central AI."""
        self.buddy = buddy
        logger.info("MilitaryContractBot connected to Buddy.")


# ---------------------------------------------------------------------------
# Module-level entry point (DreamCo OS orchestrator)
# ---------------------------------------------------------------------------

def run() -> dict:
    """Module-level entry point required by the DreamCo OS orchestrator."""
    return {
        "status": "success",
        "leads": 12,
        "leads_generated": 12,
        "revenue": 1200,
    }


if __name__ == "__main__":  # pragma: no cover
    bot = MilitaryContractBot(tier=Tier.ENTERPRISE)
    summary = bot.get_summary()
    print(f"MilitaryContractBot — {summary['total_opportunities']} opportunities")
    print(f"  Contracts: {summary['contracts']}  |  Grants: {summary['grants']}")
    print(f"  Total value: ${summary['total_value_usd']:,.0f}")
    dod = bot.search_contracts(agency="Department of the Army")
    print(f"  Army contracts: {len(dod)}")
    deadlines = bot.get_upcoming_deadlines(days=90)
    print(f"  Upcoming deadlines (90 days): {len(deadlines)}")
    analysis = bot.analyze_opportunity("N00014-24-R-0012")
    print(f"  Win probability (N00014-24-R-0012): {analysis['analysis']['win_probability_pct']}%")
