from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class AffiliateLink:
    affiliate_id: str
    bot_slug: str
    clicks: int
    conversions: int
    revenue_usd: float


class AffiliateTracker:
    def __init__(self) -> None:
        self.links: Dict[Tuple[str, str], AffiliateLink] = {}
        self.click_log: Dict[str, List[int]] = defaultdict(list)

    def record_click(self, affiliate_id: str, bot_slug: str, minute_bucket: int) -> None:
        key = (affiliate_id, bot_slug)
        self.links.setdefault(key, AffiliateLink(affiliate_id, bot_slug, 0, 0, 0.0)).clicks += 1
        self.click_log[affiliate_id].append(minute_bucket)

    def record_conversion(self, affiliate_id: str, bot_slug: str, revenue_usd: float) -> None:
        key = (affiliate_id, bot_slug)
        link = self.links.setdefault(key, AffiliateLink(affiliate_id, bot_slug, 0, 0, 0.0))
        link.conversions += 1
        link.revenue_usd += revenue_usd

    def compute_commission(self, affiliate_id: str, tier: str) -> float:
        pct = {'free': 0.2, 'pro': 0.3, 'enterprise': 0.4}.get(tier, 0.2)
        revenue = sum(link.revenue_usd for key, link in self.links.items() if key[0] == affiliate_id)
        return round(revenue * pct, 2)

    def suspicious_patterns(self, affiliate_id: str) -> bool:
        buckets = self.click_log.get(affiliate_id, [])
        return len(buckets) > 20 and len(set(buckets[-20:])) <= 2



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}



def explain_capabilities() -> str:
    return 'This module provides a fully executable implementation for DreamCo Empire OS orchestration.'
