"""
Contract Generator — Real Estate Assignment Contracts

Generates plain-text assignment contracts for DreamCo real estate deals.
Each contract can be exported as a string for digital signing or PDF
conversion.

Usage
-----
    gen = ContractGenerator()
    text = gen.generate_contract(
        buyer="DreamCo Investments LLC",
        seller="John Smith",
        property_address="123 Main St, Chicago IL 60601",
        price=45000,
    )
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Contract:
    contract_id: str
    buyer: str
    seller: str
    property_address: str
    price: float
    text: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signed: bool = False

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "buyer": self.buyer,
            "seller": self.seller,
            "property_address": self.property_address,
            "price": self.price,
            "signed": self.signed,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# ContractGenerator
# ---------------------------------------------------------------------------


class ContractGenerator:
    """Generates and stores real estate assignment contracts."""

    def __init__(self) -> None:
        self._contracts: List[Contract] = []

    def generate_contract(
        self,
        buyer: str,
        seller: str,
        property_address: str,
        price: float,
        earnest_money: float = 100.0,
        closing_days: int = 30,
    ) -> Contract:
        """
        Generate an assignment contract and store it.

        Parameters
        ----------
        buyer             : Buyer / assignee name.
        seller            : Seller name.
        property_address  : Full property address string.
        price             : Purchase / assignment price in USD.
        earnest_money     : Earnest money deposit amount.
        closing_days      : Number of days to close.

        Returns
        -------
        Contract dataclass instance.
        """
        contract_id = f"DC-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).strftime("%B %d, %Y")

        text = (
            f"ASSIGNMENT CONTRACT\n"
            f"{'=' * 50}\n\n"
            f"Contract ID   : {contract_id}\n"
            f"Date          : {created_at}\n\n"
            f"Buyer         : {buyer}\n"
            f"Seller        : {seller}\n"
            f"Property      : {property_address}\n"
            f"Purchase Price: ${price:,.2f}\n"
            f"Earnest Money : ${earnest_money:,.2f}\n"
            f"Closing Period: {closing_days} days\n\n"
            f"TERMS\n"
            f"-----\n"
            f"This Agreement assigns all rights to purchase the above-described "
            f"property from Seller to Buyer for the stated purchase price. "
            f"Buyer shall deposit earnest money within 3 business days of "
            f"execution. Closing shall occur within {closing_days} calendar days.\n\n"
            f"Both parties agree to the terms stated herein.\n\n"
            f"Seller Signature: ______________________  Date: ____________\n\n"
            f"Buyer Signature : ______________________  Date: ____________\n\n"
            f"Signed,\nDreamCo Investments\n"
        )

        contract = Contract(
            contract_id=contract_id,
            buyer=buyer,
            seller=seller,
            property_address=property_address,
            price=price,
            text=text,
        )
        self._contracts.append(contract)
        return contract

    def get_contract(self, contract_id: str) -> Optional[Contract]:
        """Retrieve a contract by ID."""
        for c in self._contracts:
            if c.contract_id == contract_id:
                return c
        return None

    def list_contracts(self) -> List[dict]:
        """Return all contracts as plain dicts."""
        return [c.to_dict() for c in self._contracts]

    def mark_signed(self, contract_id: str) -> bool:
        """Mark a contract as signed. Returns True if found."""
        contract = self.get_contract(contract_id)
        if contract:
            contract.signed = True
            return True
        return False
