"""
Price Feed — simulated real-time prices with optional CoinGecko API integration.

In offline/free mode the feed applies a small seeded random walk to the baseline
prices from crypto_database.py, giving realistic-looking price movement without
requiring any API key.

When COINGECKO_API_KEY environment variable is set the feed will attempt to
fetch live prices from CoinGecko's free public endpoint (no key required for
basic use) and fall back to the simulator if the request fails.

GLOBAL AI SOURCES FLOW: participates via crypto_bot.py pipeline.
"""

from __future__ import annotations

import os
import random
import time
from typing import Optional

from bots.crypto_bot.crypto_database import CRYPTO_DATABASE, get_coin


# ---------------------------------------------------------------------------
# Price cache
# ---------------------------------------------------------------------------

_PRICE_CACHE: dict[str, dict] = {}
_CACHE_TTL_SECONDS: float = 60.0  # refresh every 60 s in live mode


def _simulate_price(symbol: str, base_price: float) -> float:
    """Apply a small deterministic random walk to *base_price*."""
    seed = int(time.time() / 60) + hash(symbol)
    rng = random.Random(seed)
    change_pct = rng.uniform(-0.05, 0.05)  # ±5 %
    return round(base_price * (1 + change_pct), 8)


def _fetch_coingecko(symbols: list[str]) -> dict[str, float]:
    """
    Attempt to fetch prices from CoinGecko public API.
    Returns a mapping {SYMBOL: price_usd} for symbols that were found.
    Returns an empty dict on any error so callers can fall back.
    """
    try:
        import urllib.request
        import json

        ids_map = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
            "DOGE": "dogecoin", "TON": "the-open-network",
            "AVAX": "avalanche-2", "DOT": "polkadot", "LINK": "chainlink",
            "MATIC": "matic-network", "LTC": "litecoin", "ATOM": "cosmos",
            "UNI": "uniswap", "AAVE": "aave", "XMR": "monero",
            "ZEC": "zcash", "ALGO": "algorand", "VET": "vechain",
            "FIL": "filecoin", "ICP": "internet-computer", "NEAR": "near",
            "FTM": "fantom", "HBAR": "hedera-hashgraph", "XLM": "stellar",
            "TRX": "tron", "EOS": "eos", "USDT": "tether", "USDC": "usd-coin",
            "DAI": "dai", "MKR": "maker", "COMP": "compound-coin",
            "SNX": "havven", "CRV": "curve-dao-token", "GRT": "the-graph",
            "FET": "fetch-ai", "OCEAN": "ocean-protocol", "RNDR": "render-token",
            "SHIB": "shiba-inu", "PEPE": "pepe", "SAND": "the-sandbox",
            "MANA": "decentraland", "AXS": "axie-infinity", "RVN": "ravencoin",
            "ERG": "ergo", "KAS": "kaspa", "CRO": "crypto-com-chain",
            "OKB": "okb", "AR": "arweave", "HNT": "helium",
            "INJ": "injective-protocol", "SUI": "sui", "APT": "aptos",
            "OP": "optimism", "ARB": "arbitrum", "IMX": "immutable-x",
            "STX": "blockstack", "KAVA": "kava", "ROSE": "oasis-network",
        }

        wanted_ids = [ids_map[s] for s in symbols if s in ids_map]
        if not wanted_ids:
            return {}

        ids_param = ",".join(wanted_ids)
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={ids_param}&vs_currencies=usd"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "DreamcobotsCryptoBot/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        reverse_map = {v: k for k, v in ids_map.items()}
        result: dict[str, float] = {}
        for cg_id, prices in data.items():
            sym = reverse_map.get(cg_id)
            if sym and "usd" in prices:
                result[sym] = float(prices["usd"])
        return result

    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_price(symbol: str, use_live: bool = False) -> Optional[float]:
    """
    Return the current price for *symbol* in USD.

    If *use_live* is True and a network request succeeds, returns the live
    CoinGecko price; otherwise returns a simulated price.
    """
    sym = symbol.upper()
    coin = get_coin(sym)
    base = coin["price_usd"] if coin else None

    if use_live:
        cached = _PRICE_CACHE.get(sym)
        if cached and time.time() - cached["fetched_at"] < _CACHE_TTL_SECONDS:
            return cached["price"]
        live = _fetch_coingecko([sym])
        if live.get(sym):
            _PRICE_CACHE[sym] = {"price": live[sym], "fetched_at": time.time()}
            return live[sym]

    if base is None:
        return None
    return _simulate_price(sym, base)


def get_prices(symbols: list[str], use_live: bool = False) -> dict[str, float]:
    """
    Return a mapping {SYMBOL: price_usd} for all symbols in the list.
    Symbols not found in the database are omitted.
    """
    result: dict[str, float] = {}

    if use_live:
        uncached = []
        for sym in [s.upper() for s in symbols]:
            cached = _PRICE_CACHE.get(sym)
            if cached and time.time() - cached["fetched_at"] < _CACHE_TTL_SECONDS:
                result[sym] = cached["price"]
            else:
                uncached.append(sym)

        if uncached:
            live = _fetch_coingecko(uncached)
            now = time.time()
            for sym, price in live.items():
                result[sym] = price
                _PRICE_CACHE[sym] = {"price": price, "fetched_at": now}
            # fall back for any that weren't returned live
            for sym in uncached:
                if sym not in result:
                    coin = get_coin(sym)
                    if coin:
                        result[sym] = _simulate_price(sym, coin["price_usd"])
        return result

    for sym in [s.upper() for s in symbols]:
        coin = get_coin(sym)
        if coin:
            result[sym] = _simulate_price(sym, coin["price_usd"])
    return result


def get_price_change_24h(symbol: str) -> float:
    """
    Return a simulated 24-hour price change percentage for *symbol*.
    Values are deterministically seeded per-coin per-day so they are
    stable within a single day.
    """
    sym = symbol.upper()
    seed = int(time.time() / 86400) + hash(sym)
    rng = random.Random(seed)
    return round(rng.uniform(-15.0, 15.0), 2)


def get_market_summary(symbols: list[str], use_live: bool = False) -> list[dict]:
    """
    Return a list of market summary dicts for the given symbols, combining
    price data with static metadata from the database.
    """
    prices = get_prices(symbols, use_live=use_live)
    summary = []
    for sym in [s.upper() for s in symbols]:
        coin = get_coin(sym)
        if not coin:
            continue
        price = prices.get(sym, coin["price_usd"])
        change = get_price_change_24h(sym)
        summary.append({
            "symbol": sym,
            "name": coin["name"],
            "category": coin["category"],
            "price_usd": price,
            "change_24h_pct": change,
            "market_cap_usd": coin["market_cap_usd"],
            "volume_24h_usd": coin["volume_24h_usd"],
            "circulating_supply": coin["circulating_supply"],
        })
    return summary
