"""Official-resource IP search plans and owner-reviewed filing packets."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class IPError(ValueError):
    """Raised when an IP request is incomplete or overclaims legal certainty."""


class IPType(str, Enum):
    PATENT = "patent"
    TRADEMARK = "trademark"
    COPYRIGHT = "copyright"


OFFICIAL_IP_RESOURCES = {
    IPType.PATENT: [
        "https://www.uspto.gov/patents/search",
        "https://ppubs.uspto.gov/pubwebapp/",
    ],
    IPType.TRADEMARK: [
        "https://www.uspto.gov/trademarks/search",
        "https://tmsearch.uspto.gov/",
    ],
    IPType.COPYRIGHT: [
        "https://copyright.gov/registration/",
        "https://www.copyright.gov/forms/",
    ],
}


@dataclass(frozen=True)
class IPBrief:
    owner_user_id: str
    ip_type: IPType
    title_or_mark: str
    description: str
    jurisdiction: str = "US"
    owner_attests_rights: bool = False

    def validate(self) -> None:
        if len(self.title_or_mark.strip()) < 2 or len(self.description.strip()) < 20:
            raise IPError("A title or mark and detailed description are required.")
        if not self.owner_user_id.strip() or not self.jurisdiction.strip():
            raise IPError("Owner and jurisdiction are required.")


class BuddyIPAssistant:
    """Build search logs and filing drafts without making legal conclusions."""

    def search_plan(self, brief: IPBrief) -> dict[str, Any]:
        brief.validate()
        normalized = " ".join(brief.title_or_mark.lower().split())
        fingerprint = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:20]
        steps = {
            IPType.PATENT: [
                "break the invention into concepts, synonyms, and classifications",
                "search published patents and applications",
                "review claims, drawings, citations, and related families",
                "record potentially relevant prior art with source links",
                "ask a qualified patent professional to assess patentability and freedom to operate",
            ],
            IPType.TRADEMARK: [
                "search exact wording",
                "search similar spelling, sound, meaning, and commercial impression",
                "search related goods and services beyond one class",
                "record live federal results and relevant common-law sources",
                "ask a qualified trademark professional to review likelihood of confusion",
            ],
            IPType.COPYRIGHT: [
                "identify work type, authors, owners, publication status, and creation dates",
                "separate copyrightable authorship from facts, ideas, and third-party material",
                "prepare a rights and source manifest",
                "select the official registration option and required deposit material",
                "review the public-record effect before filing",
            ],
        }[brief.ip_type]
        return {
            "schema": "dreamco.ip_search_plan.v1",
            "search_id": f"ip-search-{fingerprint}",
            "brief": asdict(brief),
            "steps": steps,
            "official_resources": OFFICIAL_IP_RESOURCES[brief.ip_type],
            "legal_conclusion": None,
            "comprehensive_clearance_claimed": False,
            "professional_review_recommended": True,
        }

    def filing_packet(self, brief: IPBrief, *, search_evidence_refs: tuple[str, ...]) -> dict[str, Any]:
        brief.validate()
        if not brief.owner_attests_rights:
            raise IPError("The owner must attest that the information and claimed rights are theirs to submit.")
        if not search_evidence_refs:
            raise IPError("Search or authorship evidence is required before preparing a filing packet.")
        return {
            "schema": "dreamco.ip_filing_packet.v1",
            "packet_id": f"ip-packet-{uuid.uuid4().hex[:16]}",
            "ip_type": brief.ip_type.value,
            "jurisdiction": brief.jurisdiction,
            "status": "draft_for_owner_and_professional_review",
            "sections": [
                "owner and applicant details",
                "work, mark, or invention description",
                "classification or work type",
                "dates and publication or use facts",
                "rights and source manifest",
                "search evidence log",
                "declarations and fee preview",
            ],
            "evidence_references": list(search_evidence_refs),
            "official_resources": OFFICIAL_IP_RESOURCES[brief.ip_type],
            "filing_submitted": False,
            "fee_paid": False,
            "owner_presence_required": True,
            "legal_advice_provided": False,
        }
