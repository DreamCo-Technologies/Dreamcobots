"""
Buyer Network Bot

Manages a regional buyer pipeline and provides real-time buyer-matching
for new real-estate deals.  Supports deal auctions where multiple buyers
compete, driving up the assignment fee.

Key Features
------------
  - Buyer registration with regional preferences and buy-box criteria
  - Real-time matching: find buyers for a new deal in < 1 s
  - Deal auction: collect offers from matched buyers and select winner
  - Pipeline ownership analytics per region

Revenue hook output:
    {
        "revenue": total assignment fees collected,
        "leads_generated": deals matched to buyers,
        "conversion_rate": closed / submitted ratio,
        "action": description,
    }
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class DealStatus(Enum):
    AVAILABLE = "available"
    UNDER_CONTRACT = "under_contract"
    CLOSED = "closed"
    EXPIRED = "expired"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Buyer:
    buyer_id: str
    name: str
    email: str
    phone: str
    regions: List[str]  # e.g. ["Chicago", "Atlanta"]
    max_price: float
    min_beds: int = 0
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "buyer_id": self.buyer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "regions": self.regions,
            "max_price": self.max_price,
            "min_beds": self.min_beds,
            "active": self.active,
            "registered_at": self.registered_at,
        }


@dataclass
class Deal:
    deal_id: str
    address: str
    region: str
    asking_price: float
    beds: int
    status: DealStatus = DealStatus.AVAILABLE
    assignment_fee: float = 0.0
    matched_buyers: List[str] = field(default_factory=list)  # buyer_ids
    winning_buyer_id: Optional[str] = None
    submitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    closed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "deal_id": self.deal_id,
            "address": self.address,
            "region": self.region,
            "asking_price": self.asking_price,
            "beds": self.beds,
            "status": self.status.value,
            "assignment_fee": self.assignment_fee,
            "matched_buyers": self.matched_buyers,
            "winning_buyer_id": self.winning_buyer_id,
            "submitted_at": self.submitted_at,
            "closed_at": self.closed_at,
        }


@dataclass
class AuctionBid:
    bid_id: str
    deal_id: str
    buyer_id: str
    amount: float
    submitted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "bid_id": self.bid_id,
            "deal_id": self.deal_id,
            "buyer_id": self.buyer_id,
            "amount": self.amount,
            "submitted_at": self.submitted_at,
        }


# ---------------------------------------------------------------------------
# BuyerNetwork
# ---------------------------------------------------------------------------


class BuyerNetwork:
    """
    Regional buyer pipeline with real-time matching and deal auctions.

    Usage
    -----
    network = BuyerNetwork()
    buyer = network.register_buyer("Alice", "alice@ex.com", "+15550001111",
                                   regions=["Chicago"], max_price=150_000)
    deal  = network.submit_deal("123 Oak Ave", "Chicago", asking_price=95_000, beds=3)
    matches = network.match_buyers(deal.deal_id)
    result  = network.run_auction(deal.deal_id)
    """

    def __init__(self) -> None:
        self._buyers: Dict[str, Buyer] = {}
        self._deals: Dict[str, Deal] = {}
        self._bids: Dict[str, List[AuctionBid]] = {}  # deal_id → bids
        self._total_revenue: float = 0.0
        self._closed_deals: int = 0

    # ------------------------------------------------------------------
    # Buyer management
    # ------------------------------------------------------------------

    def register_buyer(
        self,
        name: str,
        email: str,
        phone: str,
        regions: List[str],
        max_price: float,
        min_beds: int = 0,
    ) -> Buyer:
        """Register a new buyer in the network."""
        buyer_id = f"buyer_{uuid.uuid4().hex[:8]}"
        buyer = Buyer(
            buyer_id=buyer_id,
            name=name,
            email=email,
            phone=phone,
            regions=regions,
            max_price=max_price,
            min_beds=min_beds,
        )
        self._buyers[buyer_id] = buyer
        return buyer

    def deactivate_buyer(self, buyer_id: str) -> bool:
        """Deactivate a buyer (remove from matching pool)."""
        if buyer_id in self._buyers:
            self._buyers[buyer_id].active = False
            return True
        return False

    def list_buyers(self, region: Optional[str] = None) -> List[dict]:
        buyers = [b for b in self._buyers.values() if b.active]
        if region:
            buyers = [b for b in buyers if region in b.regions]
        return [b.to_dict() for b in buyers]

    # ------------------------------------------------------------------
    # Deal management
    # ------------------------------------------------------------------

    def submit_deal(
        self,
        address: str,
        region: str,
        asking_price: float,
        beds: int,
        assignment_fee: float = 5_000.0,
    ) -> Deal:
        """Submit a new deal into the pipeline."""
        deal_id = f"deal_{uuid.uuid4().hex[:8]}"
        deal = Deal(
            deal_id=deal_id,
            address=address,
            region=region,
            asking_price=asking_price,
            beds=beds,
            assignment_fee=assignment_fee,
        )
        self._deals[deal_id] = deal
        self._bids[deal_id] = []
        return deal

    def get_deal(self, deal_id: str) -> dict:
        return self._get_deal(deal_id).to_dict()

    def list_deals(self, status: Optional[DealStatus] = None) -> List[dict]:
        deals = list(self._deals.values())
        if status:
            deals = [d for d in deals if d.status == status]
        return [d.to_dict() for d in deals]

    # ------------------------------------------------------------------
    # Real-time matching
    # ------------------------------------------------------------------

    def match_buyers(self, deal_id: str) -> List[dict]:
        """
        Find all active buyers whose criteria match this deal.

        Matching criteria:
          - Buyer region overlaps deal region
          - Buyer max_price >= deal asking_price
          - Buyer min_beds <= deal beds
        """
        deal = self._get_deal(deal_id)
        matched = [
            b for b in self._buyers.values()
            if b.active
            and deal.region in b.regions
            and b.max_price >= deal.asking_price
            and b.min_beds <= deal.beds
        ]
        deal.matched_buyers = [b.buyer_id for b in matched]
        return [b.to_dict() for b in matched]

    # ------------------------------------------------------------------
    # Auction
    # ------------------------------------------------------------------

    def place_bid(self, deal_id: str, buyer_id: str, amount: float) -> AuctionBid:
        """Place a bid from a buyer on an available deal."""
        deal = self._get_deal(deal_id)
        if deal.status != DealStatus.AVAILABLE:
            raise ValueError(f"Deal '{deal_id}' is not available for bidding.")
        if buyer_id not in self._buyers:
            raise KeyError(f"Buyer '{buyer_id}' not found.")

        bid = AuctionBid(
            bid_id=f"bid_{uuid.uuid4().hex[:8]}",
            deal_id=deal_id,
            buyer_id=buyer_id,
            amount=amount,
        )
        self._bids[deal_id].append(bid)
        return bid

    def run_auction(self, deal_id: str) -> dict:
        """
        Select the highest bidder, mark the deal under contract,
        and record the assignment fee revenue.
        """
        deal = self._get_deal(deal_id)
        bids = self._bids.get(deal_id, [])

        if not bids:
            # Auto-match and use asking price if no bids
            matched = self.match_buyers(deal_id)
            if matched:
                best_buyer_id = matched[0]["buyer_id"]
                winning_amount = deal.assignment_fee
            else:
                return {"deal_id": deal_id, "status": "no_buyers", "revenue": 0}
        else:
            winning_bid = max(bids, key=lambda b: b.amount)
            best_buyer_id = winning_bid.buyer_id
            winning_amount = winning_bid.amount

        deal.winning_buyer_id = best_buyer_id
        deal.status = DealStatus.UNDER_CONTRACT
        deal.assignment_fee = winning_amount
        deal.closed_at = datetime.now(timezone.utc).isoformat()
        self._total_revenue += winning_amount
        self._closed_deals += 1

        return {
            "deal_id": deal_id,
            "winning_buyer_id": best_buyer_id,
            "assignment_fee": winning_amount,
            "status": deal.status.value,
        }

    # ------------------------------------------------------------------
    # Revenue output (standard DreamCo format)
    # ------------------------------------------------------------------

    def get_revenue_output(self) -> dict:
        total_deals = len(self._deals)
        conversion_rate = (
            round(self._closed_deals / total_deals, 4) if total_deals else 0.0
        )
        return {
            "revenue": round(self._total_revenue, 2),
            "leads_generated": total_deals,
            "conversion_rate": conversion_rate,
            "action": f"Buyer network: {self._closed_deals}/{total_deals} deals closed",
        }

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_pipeline_stats(self, region: Optional[str] = None) -> dict:
        deals = list(self._deals.values())
        if region:
            deals = [d for d in deals if d.region == region]
        closed = [d for d in deals if d.status in (DealStatus.UNDER_CONTRACT, DealStatus.CLOSED)]
        return {
            "region": region or "all",
            "total_deals": len(deals),
            "available": len([d for d in deals if d.status == DealStatus.AVAILABLE]),
            "closed": len(closed),
            "total_revenue": round(sum(d.assignment_fee for d in closed), 2),
            "active_buyers": len([b for b in self._buyers.values() if b.active]),
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_deal(self, deal_id: str) -> Deal:
        if deal_id not in self._deals:
            raise KeyError(f"Deal '{deal_id}' not found.")
        return self._deals[deal_id]
