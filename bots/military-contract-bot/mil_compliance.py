"""
Military compliance module for the Military Contract Bot.

Covers:
- CMMC (Cybersecurity Maturity Model Certification) level checking
- DFARS / FAR clause validation
- ITAR / EAR export control screening
- Military specification (MIL-SPEC) parser
- Solicitation requirement extraction
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# CMMC levels
# ---------------------------------------------------------------------------

CMMC_PRACTICES: dict[int, list[str]] = {
    1: [
        "AC.1.001 - Limit system access to authorised users",
        "AC.1.002 - Limit system access to authorised transactions",
        "IA.1.076 - Identify information system users",
        "IA.1.077 - Authenticate users before allowing access",
        "MP.1.118 - Sanitize/destroy information system media",
        "PE.1.131 - Limit physical access to authorised individuals",
        "PE.1.132 - Escort visitors and monitor visitor activity",
        "SC.1.175 - Monitor, control and protect communications",
        "SI.1.210 - Identify, report, and correct information system flaws",
    ],
    2: [
        "AC.2.005 - Provide privacy and security notices",
        "AC.2.006 - Limit use of portable storage devices",
        "AT.2.056 - Ensure personnel are aware of security risks",
        "AU.2.041 - Ensure actions of individual users can be traced",
        "CM.2.061 - Establish and maintain baseline configurations",
        "IR.2.092 - Establish operational incident-handling capability",
        "RM.2.141 - Periodically assess risk to operations",
    ],
    3: [
        "AC.3.017 - Separate duties of individuals",
        "AC.3.018 - Prevent non-privileged users from executing privileged functions",
        "AU.3.045 - Review and update logged events",
        "CM.3.068 - Restrict, disable, or prevent the use of nonessential programs",
        "IA.3.083 - Use multifactor authentication for local and network access",
        "SC.3.177 - Employ FIPS-validated cryptography",
    ],
}


def check_cmmc_compliance(implemented_controls: list[str], required_level: int) -> dict[str, Any]:
    """Check whether *implemented_controls* satisfy CMMC *required_level*.

    Returns a dict with 'compliant', 'level', 'missing', and 'score'.
    """
    required: list[str] = []
    for lvl in range(1, required_level + 1):
        required.extend(CMMC_PRACTICES.get(lvl, []))

    # Match by practice ID prefix (e.g. "AC.1.001")
    def _id(practice: str) -> str:
        return practice.split(" - ")[0].strip()

    implemented_ids = {c.split(" - ")[0].strip() for c in implemented_controls}
    required_ids = [_id(p) for p in required]
    missing = [p for p in required_ids if p not in implemented_ids]

    total = len(required_ids)
    score = round((total - len(missing)) / total * 100, 1) if total else 100.0
    return {
        "compliant": len(missing) == 0,
        "level": required_level,
        "total_required": total,
        "implemented": total - len(missing),
        "missing": missing,
        "score_pct": score,
    }


# ---------------------------------------------------------------------------
# DFARS / FAR key clauses
# ---------------------------------------------------------------------------

DFARS_CLAUSES: dict[str, str] = {
    "DFARS 252.204-7012": "Safeguarding Covered Defense Information and Cyber Incident Reporting",
    "DFARS 252.227-7013": "Rights in Technical Data — Noncommercial Items",
    "DFARS 252.225-7001": "Buy American Act and Balance of Payments Program",
    "DFARS 252.203-7000": "Requirements Relating to Compensation of Former DoD Officials",
    "DFARS 252.211-7003": "Item Unique Identification and Valuation",
    "FAR 52.204-21": "Basic Safeguarding of Covered Contractor Information Systems",
    "FAR 52.222-26": "Equal Opportunity",
    "FAR 52.222-41": "Service Contract Labor Standards",
    "FAR 52.232-33": "Payment by Electronic Funds Transfer — System for Award Management",
    "FAR 52.233-1": "Disputes",
}

REQUIRED_CLAUSES_BY_VALUE: dict[str, list[str]] = {
    "micro_purchase": [],
    "simplified_acquisition": ["FAR 52.204-21", "FAR 52.222-26"],
    "standard": [
        "FAR 52.204-21", "FAR 52.222-26", "FAR 52.222-41",
        "FAR 52.232-33", "DFARS 252.204-7012",
    ],
    "large": [
        "FAR 52.204-21", "FAR 52.222-26", "FAR 52.222-41",
        "FAR 52.232-33", "FAR 52.233-1",
        "DFARS 252.204-7012", "DFARS 252.225-7001",
        "DFARS 252.211-7003",
    ],
}


def classify_contract_value(value: float) -> str:
    """Return the acquisition threshold category for *value*."""
    if value <= 10_000:
        return "micro_purchase"
    if value <= 250_000:
        return "simplified_acquisition"
    if value <= 10_000_000:
        return "standard"
    return "large"


def validate_clauses(contract_clauses: list[str], contract_value: float) -> dict[str, Any]:
    """Validate that *contract_clauses* include all clauses required for *contract_value*."""
    category = classify_contract_value(contract_value)
    required = REQUIRED_CLAUSES_BY_VALUE[category]
    missing = [c for c in required if c not in contract_clauses]
    return {
        "category": category,
        "required_clauses": required,
        "present": [c for c in required if c in contract_clauses],
        "missing": missing,
        "compliant": len(missing) == 0,
    }


# ---------------------------------------------------------------------------
# Military specification (MIL-SPEC) parser
# ---------------------------------------------------------------------------

# Common MIL-SPEC patterns found in solicitations
_MILSPEC_PATTERN = re.compile(
    r"\b(MIL-(?:STD|SPEC|DTL|PRF|HDBK)-\d+[A-Z]?(?:\s*\([A-Z]+\))?)\b",
    re.IGNORECASE,
)
_FAR_DFARS_PATTERN = re.compile(
    r"\b((?:FAR|DFARS)\s+\d{2}\.\d{3}-\d{4}[A-Z]?)\b",
    re.IGNORECASE,
)
_NAICS_PATTERN = re.compile(r"\bNAICS\s*[:#]?\s*(\d{5,6})\b", re.IGNORECASE)
_SET_ASIDE_PATTERN = re.compile(
    r"\b(small\s+business|8\(a\)|hubzone|wosb|sdvosb|veteran[-\s]owned|"
    r"service[-\s]disabled|disadvantaged\s+business|ibe|indian\s+economic)\b",
    re.IGNORECASE,
)
_CLEARANCE_PATTERN = re.compile(
    r"\b(secret\s+clearance|top\s+secret|ts/sci|confidential\s+clearance|"
    r"security\s+clearance)\b",
    re.IGNORECASE,
)


@dataclass
class SolicitationParsed:
    """Structured result of parsing a raw solicitation text."""
    mil_specs: list[str] = field(default_factory=list)
    far_dfars_clauses: list[str] = field(default_factory=list)
    naics_codes: list[str] = field(default_factory=list)
    set_asides: list[str] = field(default_factory=list)
    clearance_requirements: list[str] = field(default_factory=list)
    raw_excerpt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "mil_specs": self.mil_specs,
            "far_dfars_clauses": self.far_dfars_clauses,
            "naics_codes": self.naics_codes,
            "set_asides": [s.lower() for s in self.set_asides],
            "clearance_requirements": self.clearance_requirements,
        }


def parse_solicitation(text: str) -> SolicitationParsed:
    """Extract structured requirements from raw solicitation *text*."""
    return SolicitationParsed(
        mil_specs=list({m.upper() for m in _MILSPEC_PATTERN.findall(text)}),
        far_dfars_clauses=list({c.upper() for c in _FAR_DFARS_PATTERN.findall(text)}),
        naics_codes=list({n for n in _NAICS_PATTERN.findall(text)}),
        set_asides=list({s for s in _SET_ASIDE_PATTERN.findall(text)}),
        clearance_requirements=list({c for c in _CLEARANCE_PATTERN.findall(text)}),
        raw_excerpt=text[:500],
    )


# ---------------------------------------------------------------------------
# ITAR / EAR export control screener
# ---------------------------------------------------------------------------

_ITAR_KEYWORDS = {
    "munitions", "firearms", "artillery", "missiles", "rockets", "torpedoes",
    "bombs", "explosives", "military aircraft", "combat vehicle", "warship",
    "spacecraft", "satellites", "directed energy", "night vision",
}

_EAR_KEYWORDS = {
    "dual-use", "encryption", "cryptographic", "semiconductor", "nuclear",
    "chemical", "biological", "radar", "sonar", "lasers", "sensors",
}


def screen_export_control(description: str) -> dict[str, Any]:
    """Screen contract *description* for ITAR / EAR sensitivities."""
    desc_lower = description.lower()
    itar_hits = [kw for kw in _ITAR_KEYWORDS if kw in desc_lower]
    ear_hits = [kw for kw in _EAR_KEYWORDS if kw in desc_lower]
    return {
        "itar_flags": itar_hits,
        "ear_flags": ear_hits,
        "requires_review": bool(itar_hits or ear_hits),
        "risk_level": "high" if itar_hits else ("medium" if ear_hits else "low"),
    }
