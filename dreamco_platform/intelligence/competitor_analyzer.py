from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass
class CompetitorProfile:
    name: str
    pricing_model: str
    key_features: List[str]
    weaknesses: List[str]


@dataclass
class CompetitorAlert:
    type: str
    impact_score: float
    details: str


class CompetitorAnalyzer:
    def __init__(self, dreamco_positioning: Dict[str, object] | None = None) -> None:
        self.dreamco_positioning = dreamco_positioning or {'price': 99, 'features': {'automation', 'analytics', 'governance'}}

    def analyze(self, profiles: Iterable[CompetitorProfile], updates: Iterable[dict]) -> List[CompetitorAlert]:
        alerts = []
        for update in updates:
            profile = next((profile for profile in profiles if profile.name == update['name']), None)
            if not profile:
                continue
            if 'new_price' in update:
                impact = abs(update['new_price'] - self.dreamco_positioning['price']) / max(self.dreamco_positioning['price'], 1)
                alerts.append(CompetitorAlert('price_change', round(impact, 2), f"{profile.name} repriced to {update['new_price']}"))
            if 'new_feature' in update:
                delta = 1.0 if update['new_feature'] not in self.dreamco_positioning['features'] else 0.3
                alerts.append(CompetitorAlert('new_feature', delta, f"{profile.name} launched {update['new_feature']}"))
            if 'funding' in update:
                alerts.append(CompetitorAlert('funding', min(1.0, update['funding'] / 100_000_000), f"{profile.name} raised {update['funding']:,}"))
        return sorted(alerts, key=lambda item: item.impact_score, reverse=True)

def compare_positioning(self, profile: CompetitorProfile) -> dict:
    dreamco_features = set(self.dreamco_positioning['features'])
    competitor_features = set(profile.key_features)
    return {
        'feature_gap': sorted(competitor_features - dreamco_features),
        'feature_advantage': sorted(dreamco_features - competitor_features),
        'pricing_model': profile.pricing_model,
        'weaknesses': list(profile.weaknesses),
    }


def watchlist_summary(self, profiles: Iterable[CompetitorProfile]) -> List[dict]:
    return [
        {'name': profile.name, 'gap_count': len(self.compare_positioning(profile)['feature_gap'])}
        for profile in profiles
    ]


CompetitorAnalyzer.compare_positioning = compare_positioning
CompetitorAnalyzer.watchlist_summary = watchlist_summary
