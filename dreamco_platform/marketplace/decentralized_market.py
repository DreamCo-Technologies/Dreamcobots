from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class BotListing:
    slug: str
    seller_id: str
    capabilities: List[str]
    price: float
    reputation_score: float = 0.0


@dataclass
class Transaction:
    slug: str
    buyer_id: str
    amount: float
    status: str
    created_at: datetime = field(default_factory=datetime.utcnow)


class ReputationEngine:
    def __init__(self) -> None:
        self.ratings: Dict[str, List[tuple[int, datetime]]] = {}

    def rate(self, slug: str, rating: int) -> float:
        now = datetime.utcnow()
        self.ratings.setdefault(slug, []).append((rating, now))
        weighted = 0.0
        total_weight = 0.0
        for score, created_at in self.ratings[slug]:
            age_days = max((now - created_at).days, 0)
            weight = 1 / (1 + age_days / 30)
            weighted += score * weight
            total_weight += weight
        return round(weighted / max(total_weight, 1e-9), 2)


class Marketplace:
    def __init__(self) -> None:
        self.listings: Dict[str, BotListing] = {}
        self.escrow: Dict[str, Transaction] = {}
        self.reputation = ReputationEngine()

    def list_bot(self, listing: BotListing) -> None:
        self.listings[listing.slug] = listing

    def buy_bot(self, slug: str, buyer_id: str) -> Transaction:
        listing = self.listings[slug]
        transaction = Transaction(slug, buyer_id, listing.price, 'escrowed')
        self.escrow[f'{slug}:{buyer_id}'] = transaction
        return transaction

    def confirm_delivery(self, slug: str, buyer_id: str) -> Transaction:
        transaction = self.escrow[f'{slug}:{buyer_id}']
        transaction.status = 'released'
        return transaction

    def rate_bot(self, slug: str, rating: int) -> float:
        score = self.reputation.rate(slug, rating)
        self.listings[slug].reputation_score = score
        return score

    def dispute_transaction(self, slug: str, buyer_id: str) -> Transaction:
        transaction = self.escrow[f'{slug}:{buyer_id}']
        transaction.status = 'disputed'
        return transaction
