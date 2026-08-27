"""Internal asset exchange primitives for Buddy.

This is a catalog and matching layer, not a payment system. It lets Buddy
compose reusable digital assets while preserving trust, compatibility and
permission boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .digital_asset_registry import DigitalAsset


@dataclass(frozen=True)
class AssetOffer:
    asset_id: str
    capability: str
    compatibility: float
    trust: float
    utility: float
    risk: float
    estimated_cost: float = 0.0

    @property
    def score(self) -> float:
        return max(0.0, self.compatibility * 0.3 + self.trust * 0.25 + self.utility * 0.25 - self.risk * 0.15 - min(self.estimated_cost, 1.0) * 0.05)


class AssetMatcher:
    def match(self, assets: Iterable[DigitalAsset], capability: str) -> List[AssetOffer]:
        offers: List[AssetOffer] = []
        for asset in assets:
            if capability not in asset.capabilities:
                continue
            offers.append(AssetOffer(asset.asset_id, capability, 1.0, asset.trust_score, asset.utility_score, asset.risk_score))
        return sorted(offers, key=lambda offer: (-offer.score, offer.asset_id))
