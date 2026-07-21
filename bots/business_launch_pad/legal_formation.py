# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""Legal Formation module for Business Launch Pad."""

import uuid
import random
from dataclasses import dataclass, field
from enum import Enum


class EntityType(Enum):
    LLC = "llc"
    CORPORATION = "corporation"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    PARTNERSHIP = "partnership"


class FormationStatus(Enum):
    DRAFT = "draft"
    FILED = "filed"
    APPROVED = "approved"
    ACTIVE = "active"
    DISSOLVED = "dissolved"


@dataclass
class LegalEntity:
    entity_id: str
    business_name: str
    entity_type: EntityType
    state: str
    status: FormationStatus
    ein: str | None
    compliance_items: list[str]


_COMPLIANCE_BASE: dict[str, list[str]] = {
    EntityType.LLC.value: [
        "File Articles of Organization",
        "Draft Operating Agreement",
        "Obtain Registered Agent",
        "Apply for EIN (IRS Form SS-4)",
        "Open Business Bank Account",
        "Apply for Business Licenses",
    ],
    EntityType.CORPORATION.value: [
        "File Articles of Incorporation",
        "Draft Corporate Bylaws",
        "Hold Initial Board Meeting",
        "Issue Stock Certificates",
        "Obtain Registered Agent",
        "Apply for EIN (IRS Form SS-4)",
        "Open Business Bank Account",
        "File Initial Report",
    ],
    EntityType.SOLE_PROPRIETORSHIP.value: [
        "Register DBA (if applicable)",
        "Apply for EIN (if hiring employees)",
        "Obtain Business Licenses",
        "Open Business Bank Account",
    ],
    EntityType.PARTNERSHIP.value: [
        "Draft Partnership Agreement",
        "Register Partnership Name",
        "Apply for EIN (IRS Form SS-4)",
        "Obtain Business Licenses",
        "Open Business Bank Account",
    ],
}

_STATE_REQUIREMENTS: dict[str, dict] = {
    "CA": {"filing_fee": 70, "annual_report": True, "annual_fee": 800, "processing_days": 15},
    "DE": {"filing_fee": 90, "annual_report": True, "annual_fee": 300, "processing_days": 3},
    "NY": {"filing_fee": 200, "annual_report": True, "annual_fee": 25, "processing_days": 7},
    "TX": {"filing_fee": 300, "annual_report": False, "annual_fee": 0, "processing_days": 5},
    "FL": {"filing_fee": 100, "annual_report": True, "annual_fee": 138, "processing_days": 5},
    "WA": {"filing_fee": 200, "annual_report": True, "annual_fee": 60, "processing_days": 5},
    "NV": {"filing_fee": 75, "annual_report": True, "annual_fee": 200, "processing_days": 3},
}

_DEFAULT_FILING = {"filing_fee": 100, "annual_report": True, "annual_fee": 50, "processing_days": 7}


class LegalFormation:
    """Handles business entity formation, EIN registration, and compliance checklists."""

    def __init__(self) -> None:
        self._entities: list[LegalEntity] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def form_entity(self, business_name: str, entity_type: EntityType, state: str) -> LegalEntity:
        """Create a new legal entity in DRAFT status."""
        compliance = self.get_compliance_checklist(entity_type, state)
        entity = LegalEntity(
            entity_id=str(uuid.uuid4()),
            business_name=business_name,
            entity_type=entity_type,
            state=state.upper(),
            status=FormationStatus.DRAFT,
            ein=None,
            compliance_items=compliance,
        )
        self._entities.append(entity)
        return entity

    def file_entity(self, entity_id: str) -> LegalEntity:
        """Transition entity status to FILED."""
        entity = self.get_entity(entity_id)
        entity.status = FormationStatus.FILED
        return entity

    def approve_entity(self, entity_id: str) -> LegalEntity:
        """Transition entity through APPROVED to ACTIVE."""
        entity = self.get_entity(entity_id)
        entity.status = FormationStatus.APPROVED
        entity.status = FormationStatus.ACTIVE
        return entity

    def register_ein(self, entity_id: str) -> str:
        """Generate and assign a fake EIN to an entity."""
        entity = self.get_entity(entity_id)
        prefix = random.randint(10, 99)
        suffix = random.randint(1000000, 9999999)
        ein = f"{prefix}-{suffix}"
        entity.ein = ein
        return ein

    def get_compliance_checklist(self, entity_type: EntityType, state: str) -> list[str]:
        """Return state-specific compliance checklist for the entity type."""
        base = list(_COMPLIANCE_BASE.get(entity_type.value, []))
        reqs = _STATE_REQUIREMENTS.get(state.upper(), _DEFAULT_FILING)
        if reqs.get("annual_report"):
            base.append(f"File Annual Report (state fee: ${reqs['annual_fee']})")
        base.append(f"Pay State Filing Fee (${reqs['filing_fee']})")
        return base

    def list_entities(self) -> list[LegalEntity]:
        """Return all created legal entities."""
        return list(self._entities)

    def get_entity(self, entity_id: str) -> LegalEntity:
        """Retrieve an entity by ID; raises KeyError if not found."""
        for entity in self._entities:
            if entity.entity_id == entity_id:
                return entity
        raise KeyError(f"Entity '{entity_id}' not found")

    def get_filing_requirements(self, state: str) -> dict:
        """Return state-specific filing requirements."""
        reqs = dict(_STATE_REQUIREMENTS.get(state.upper(), _DEFAULT_FILING))
        reqs["state"] = state.upper()
        return reqs
