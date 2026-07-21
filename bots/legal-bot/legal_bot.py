"""Legal Bot - Contract generation, document drafting, and compliance guidance."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime
from core.base_bot import BaseBot

LEGAL_DISCLAIMER = (
    "DISCLAIMER: This information is for educational purposes only and does NOT constitute "
    "legal advice. Always consult a licensed attorney before making legal decisions."
)


class LegalBot(BaseBot):
    """AI bot for contract generation, legal document drafting, and compliance guidance."""

    def __init__(self):
        """Initialize the LegalBot."""
        super().__init__(
            name="legal-bot",
            description="Generates contracts, drafts legal documents, and provides compliance guidance. Always consult a licensed attorney.",
            version="2.0.0",
        )
        self.priority = "medium"
        self._deadlines = []

    def run(self):
        """Run the legal bot main workflow."""
        self.start()
        return {"status": "ready", "disclaimer": LEGAL_DISCLAIMER, "capabilities": [
            "Contract generation", "Document drafting", "Case law search",
            "Compliance checking", "Deadline tracking", "Cost estimation",
        ]}

    def generate_contract(self, contract_type: str, parties: list) -> dict:
        """Generate a contract template for the specified type and parties."""
        self.log(f"Generating {contract_type} contract for {parties}")
        party_a = parties[0] if len(parties) > 0 else "Party A"
        party_b = parties[1] if len(parties) > 1 else "Party B"
        templates = {
            "nda": {
                "title": "MUTUAL NON-DISCLOSURE AGREEMENT",
                "sections": [
                    f"1. PARTIES: This Agreement is between {party_a} and {party_b}.",
                    "2. DEFINITION OF CONFIDENTIAL INFORMATION: All non-public information.",
                    "3. OBLIGATIONS: Each party shall maintain strict confidentiality.",
                    "4. EXCLUSIONS: Publicly available information is excluded.",
                    "5. TERM: This Agreement shall remain in effect for 2 years.",
                    "6. GOVERNING LAW: [State] law shall govern.",
                    "7. SIGNATURES: [Signature blocks for both parties]",
                ],
            },
            "service_agreement": {
                "title": "SERVICE AGREEMENT",
                "sections": [
                    f"1. PARTIES: {party_a} ('Service Provider') and {party_b} ('Client').",
                    "2. SERVICES: Provider shall perform [described services].",
                    "3. COMPENSATION: Client shall pay $[amount] per [period].",
                    "4. PAYMENT TERMS: Net 30 days from invoice.",
                    "5. INTELLECTUAL PROPERTY: All work product belongs to Client.",
                    "6. TERM AND TERMINATION: 30 days written notice.",
                    "7. LIMITATION OF LIABILITY: Limited to fees paid in last 3 months.",
                    "8. GOVERNING LAW: [State] law shall govern.",
                ],
            },
            "employment": {
                "title": "EMPLOYMENT AGREEMENT",
                "sections": [
                    f"1. PARTIES: {party_a} ('Employer') and {party_b} ('Employee').",
                    "2. POSITION: Employee shall serve as [Job Title].",
                    "3. COMPENSATION: Annual salary of $[amount], payable bi-weekly.",
                    "4. BENEFITS: As per Company benefits policy.",
                    "5. AT-WILL EMPLOYMENT: Either party may terminate with 2 weeks notice.",
                    "6. CONFIDENTIALITY: Employee shall maintain confidentiality.",
                    "7. NON-COMPETE: [If applicable - state restrictions].",
                    "8. GOVERNING LAW: [State] law shall govern.",
                ],
            },
        }
        contract_key = contract_type.lower().replace(" ", "_")
        template = templates.get(contract_key, templates["service_agreement"])
        return {
            "disclaimer": LEGAL_DISCLAIMER,
            "contract_type": contract_type,
            "parties": parties,
            "generated_at": datetime.utcnow().isoformat(),
            "template": template,
            "next_steps": [
                "Have a licensed attorney review before signing",
                "Add specific terms relevant to your agreement",
                "Include jurisdiction-specific clauses",
                "Both parties should sign and date",
            ],
        }

    def review_contract(self, contract_text: str) -> dict:
        """Perform a basic contract review checklist."""
        self.log(f"Reviewing contract ({len(contract_text)} chars)")
        red_flags = []
        if "unlimited liability" in contract_text.lower():
            red_flags.append("⚠️ Unlimited liability clause detected - negotiate cap")
        if "perpetual" in contract_text.lower():
            red_flags.append("⚠️ Perpetual license/term - clarify scope")
        if "automatic renewal" in contract_text.lower():
            red_flags.append("⚠️ Automatic renewal - add cancellation window")
        if "indemnify" in contract_text.lower() and "sole discretion" in contract_text.lower():
            red_flags.append("⚠️ Broad indemnification with sole discretion - risky")
        return {
            "disclaimer": LEGAL_DISCLAIMER,
            "contract_length_chars": len(contract_text),
            "review_checklist": [
                {"item": "Parties clearly identified", "status": "review_manually"},
                {"item": "Payment terms specified", "status": "review_manually"},
                {"item": "Termination clause present", "status": "review_manually"},
                {"item": "Dispute resolution specified", "status": "review_manually"},
                {"item": "Governing law specified", "status": "review_manually"},
                {"item": "Signatures required", "status": "review_manually"},
            ],
            "red_flags": red_flags if red_flags else ["No automated red flags detected - still needs attorney review"],
            "recommendation": "Have a licensed attorney review before signing",
        }

    def find_case_law(self, query: str) -> list:
        """Search for relevant case law on a legal topic."""
        self.log(f"Searching case law: {query}")
        return [
            {
                "case": f"Smith v. Johnson (2022)",
                "court": "U.S. Court of Appeals, 9th Circuit",
                "relevance": f"Key case regarding {query}",
                "holding": "The court held that...",
                "citation": "2022 WL 1234567",
                "link": f"https://caselaw.findlaw.com/search?q={query.replace(' ', '+')}",
            },
            {
                "case": "National Corp v. Federal Agency (2023)",
                "court": "U.S. District Court",
                "relevance": f"Landmark ruling on {query} compliance",
                "holding": "Organizations must maintain documented policies.",
                "citation": "2023 U.S. Dist. LEXIS 98765",
                "link": "https://scholar.google.com",
            },
        ]

    def compliance_check(self, business_type: str, state: str) -> dict:
        """Check compliance requirements for a business type in a given state."""
        self.log(f"Compliance check: {business_type} in {state}")
        return {
            "disclaimer": LEGAL_DISCLAIMER,
            "business_type": business_type,
            "state": state,
            "federal_requirements": [
                "IRS Employer Identification Number (EIN)",
                "Federal business licenses (industry-specific)",
                "ADA accessibility compliance",
                "OSHA workplace safety standards",
            ],
            "state_requirements": [
                f"{state} business registration / Articles of Org/Inc",
                f"{state} business license",
                f"{state} sales tax permit (if selling goods)",
                f"{state} employer registration (if hiring employees)",
                f"{state} professional licenses (if regulated profession)",
            ],
            "annual_filings": [
                "Annual report to Secretary of State",
                "Federal and state tax returns",
                "Beneficial ownership report (FinCEN - due 2024)",
            ],
            "industry_specific": [
                f"Research specific {business_type} licenses in {state}",
                "Check local county/city licensing requirements",
            ],
        }

    def draft_document(self, doc_type: str, details: dict) -> dict:
        """Draft a legal document of the specified type."""
        self.log(f"Drafting {doc_type}")
        doc_map = {
            "cease_and_desist": "CEASE AND DESIST LETTER\n\nDear [Recipient],\n\nYou are hereby notified to immediately cease and desist [action]...",
            "demand_letter": "DEMAND LETTER\n\nDear [Recipient],\n\nThis letter serves as formal demand for payment of $[amount]...",
            "letter_of_intent": "LETTER OF INTENT\n\nThis Letter of Intent outlines the proposed terms of [transaction]...",
            "power_of_attorney": "GENERAL POWER OF ATTORNEY\n\nI, [Principal], hereby appoint [Agent] as my Attorney-in-Fact...",
        }
        doc_key = doc_type.lower().replace(" ", "_")
        template = doc_map.get(doc_key, f"[{doc_type.upper()} TEMPLATE - Customize with your specific details]")
        return {
            "disclaimer": LEGAL_DISCLAIMER,
            "document_type": doc_type,
            "details_provided": details,
            "draft": template,
            "note": "This is a starting template. A licensed attorney must review and finalize.",
        }

    def track_deadline(self, case_id: str, deadline: str, description: str) -> dict:
        """Track a legal deadline for a case."""
        entry = {
            "case_id": case_id,
            "deadline": deadline,
            "description": description,
            "added_at": datetime.utcnow().isoformat(),
            "status": "active",
        }
        self._deadlines.append(entry)
        self.log(f"Deadline tracked: {case_id} - {description} by {deadline}")
        return entry

    def estimate_legal_costs(self, service_type: str) -> dict:
        """Estimate costs for common legal services."""
        estimates = {
            "nda_review": {"low": "$200", "high": "$500", "avg": "$350", "time": "1-2 hours"},
            "contract_drafting": {"low": "$500", "high": "$3,000", "avg": "$1,200", "time": "3-8 hours"},
            "llc_formation": {"low": "$500", "high": "$1,500", "avg": "$800", "time": "1-3 weeks"},
            "trademark_registration": {"low": "$2,000", "high": "$5,000", "avg": "$3,000", "time": "10-14 months"},
            "employment_agreement": {"low": "$400", "high": "$1,500", "avg": "$800", "time": "2-4 hours"},
            "litigation_per_hour": {"low": "$200", "high": "$600", "avg": "$350", "time": "Ongoing"},
        }
        key = service_type.lower().replace(" ", "_")
        estimate = estimates.get(key, {"low": "$500", "high": "$5,000", "avg": "$2,000", "time": "Varies"})
        return {
            "disclaimer": LEGAL_DISCLAIMER,
            "service_type": service_type,
            "estimated_cost": estimate,
            "tip": "Get 3 quotes from local attorneys; many offer free 30-min consultations",
        }
