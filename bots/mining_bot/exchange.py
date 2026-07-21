"""
Multi-Exchange Execution module for the Dreamcobots Mining Bot.

Allows the mining bot to:
  - Query simulated exchange rates for mined coins across multiple platforms.
  - Select the best exchange for coin conversion (highest net USD yield).
  - Route trades through DEX aggregators when ENTERPRISE features are enabled.

All exchange rates are simulated (no live API calls) to make the module
fully testable without external dependencies.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MultiExchangeDisabledError(Exception):
    """Raised when multi-exchange features are not available on this tier."""


@dataclass
class ExchangeQuote:
    """A conversion quote from a single exchange."""

    exchange: str
    coin: str
    amount_coin: float
    rate_usd: float          # USD per coin
    fee_pct: float           # trading fee as percentage
    is_dex: bool = False

    @property
    def gross_usd(self) -> float:
        return self.amount_coin * self.rate_usd

    @property
    def fee_usd(self) -> float:
        return self.gross_usd * (self.fee_pct / 100)

    @property
    def net_usd(self) -> float:
        return round(self.gross_usd - self.fee_usd, 6)

    def to_dict(self) -> Dict:
        return {
            "exchange": self.exchange,
            "coin": self.coin,
            "amount_coin": self.amount_coin,
            "rate_usd": self.rate_usd,
            "fee_pct": self.fee_pct,
            "gross_usd": self.gross_usd,
            "fee_usd": self.fee_usd,
            "net_usd": self.net_usd,
            "is_dex": self.is_dex,
        }


# ---------------------------------------------------------------------------
# Simulated exchange rate table
# ---------------------------------------------------------------------------

_SIMULATED_RATES: Dict[str, Dict[str, float]] = {
    # exchange_name -> coin_symbol -> USD rate
    "Binance": {"BTC": 65_000.0, "ETH": 3_500.0, "LTC": 90.0, "DOGE": 0.12},
    "Coinbase": {"BTC": 65_100.0, "ETH": 3_510.0, "LTC": 91.0, "DOGE": 0.121},
    "Kraken":  {"BTC": 64_900.0, "ETH": 3_490.0, "LTC": 89.5, "DOGE": 0.119},
    "KuCoin":  {"BTC": 64_950.0, "ETH": 3_505.0, "LTC": 90.5, "DOGE": 0.1205},
    "UniswapV3_DEX": {"BTC": 64_800.0, "ETH": 3_480.0, "LTC": 88.0, "DOGE": 0.118},
}

_EXCHANGE_FEES: Dict[str, float] = {
    "Binance": 0.1,
    "Coinbase": 0.5,
    "Kraken": 0.16,
    "KuCoin": 0.1,
    "UniswapV3_DEX": 0.3,
}

_DEX_EXCHANGES = {"UniswapV3_DEX"}


class MultiExchangeRouter:
    """
    Queries multiple exchanges and recommends the best conversion for a
    given quantity of a mined coin.

    Parameters
    ----------
    multi_exchange_enabled : bool
        Whether multi-exchange features are enabled for this tier.
    dex_routing_enabled : bool
        Whether DEX routing is enabled (ENTERPRISE tier only).
    custom_rates : dict, optional
        Override simulated rates for testing.  Format:
        ``{exchange_name: {coin: rate_usd}}``
    """

    def __init__(
        self,
        multi_exchange_enabled: bool = False,
        dex_routing_enabled: bool = False,
        custom_rates: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        self.multi_exchange_enabled = multi_exchange_enabled
        self.dex_routing_enabled = dex_routing_enabled
        self._rates: Dict[str, Dict[str, float]] = (
            custom_rates if custom_rates is not None else dict(_SIMULATED_RATES)
        )

    def _require_enabled(self) -> None:
        if not self.multi_exchange_enabled:
            raise MultiExchangeDisabledError(
                "Multi-exchange execution requires PRO or ENTERPRISE tier."
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_quotes(self, coin: str, amount: float) -> List[ExchangeQuote]:
        """
        Return conversion quotes for *amount* of *coin* from all exchanges.

        DEX quotes are included only when ``dex_routing_enabled`` is True.
        """
        self._require_enabled()
        quotes: List[ExchangeQuote] = []
        for exchange, coin_rates in self._rates.items():
            if exchange in _DEX_EXCHANGES and not self.dex_routing_enabled:
                continue
            if coin not in coin_rates:
                continue
            quotes.append(
                ExchangeQuote(
                    exchange=exchange,
                    coin=coin,
                    amount_coin=amount,
                    rate_usd=coin_rates[coin],
                    fee_pct=_EXCHANGE_FEES.get(exchange, 0.25),
                    is_dex=(exchange in _DEX_EXCHANGES),
                )
            )
        return quotes

    def best_exchange(self, coin: str, amount: float) -> Optional[ExchangeQuote]:
        """Return the quote with the highest net USD yield."""
        quotes = self.get_quotes(coin, amount)
        if not quotes:
            return None
        return max(quotes, key=lambda q: q.net_usd)

    def compare_exchanges(self, coin: str, amount: float) -> Dict:
        """
        Full comparison report for *coin* / *amount*.

        Returns
        -------
        dict with keys: ``coin``, ``amount``, ``quotes`` (list of dicts),
        ``best_exchange``, ``best_net_usd``.
        """
        quotes = self.get_quotes(coin, amount)
        best = self.best_exchange(coin, amount)
        return {
            "coin": coin,
            "amount": amount,
            "quotes": [q.to_dict() for q in quotes],
            "best_exchange": best.exchange if best else None,
            "best_net_usd": best.net_usd if best else 0.0,
        }

    def available_coins(self) -> List[str]:
        """Return the set of coins supported across all exchanges."""
        coins: set = set()
        for rates in self._rates.values():
            coins.update(rates.keys())
        return sorted(coins)
