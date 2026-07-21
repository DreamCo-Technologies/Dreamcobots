"""Arbitrage detection across market venues."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass
class Quote:
    venue: str
    asset: str
    bid: float
    ask: float
    fee_rate: float = 0.0


class ArbitrageDetector:
    def normalize_quote(self, quote: Quote) -> Dict[str, float | str]:
        return {
            'venue': quote.venue,
            'asset': quote.asset,
            'effective_bid': round(quote.bid * (1 - quote.fee_rate), 6),
            'effective_ask': round(quote.ask * (1 + quote.fee_rate), 6),
        }

    def find_opportunities(self, quotes: Iterable[Quote], min_spread: float = 0.0) -> List[Dict[str, object]]:
        by_asset: Dict[str, List[Quote]] = {}
        for quote in quotes:
            by_asset.setdefault(quote.asset, []).append(quote)
        opportunities: List[Dict[str, object]] = []
        for asset, asset_quotes in by_asset.items():
            for buy in asset_quotes:
                for sell in asset_quotes:
                    if buy.venue == sell.venue:
                        continue
                    net_buy = buy.ask * (1 + buy.fee_rate)
                    net_sell = sell.bid * (1 - sell.fee_rate)
                    spread = net_sell - net_buy
                    if spread > min_spread:
                        opportunities.append({
                            'asset': asset,
                            'buy_from': buy.venue,
                            'sell_to': sell.venue,
                            'spread': round(spread, 6),
                            'return_pct': round(spread / max(net_buy, 1e-9), 6),
                        })
        return sorted(opportunities, key=lambda item: item['spread'], reverse=True)

    def best_path(self, quotes: Iterable[Quote]) -> Dict[str, object] | None:
        opportunities = self.find_opportunities(quotes)
        return opportunities[0] if opportunities else None

    def venue_summary(self, quotes: Iterable[Quote]) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for quote in quotes:
            summary[quote.venue] = summary.get(quote.venue, 0) + 1
        return summary


def pairwise_matrix(quotes: Iterable[Quote]) -> Dict[Tuple[str, str], float]:
    quotes = list(quotes)
    detector = ArbitrageDetector()
    matrix: Dict[Tuple[str, str], float] = {}
    for item in detector.find_opportunities(quotes):
        matrix[(str(item['buy_from']), str(item['sell_to']))] = float(item['spread'])
    return matrix
