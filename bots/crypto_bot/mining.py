"""
Mining — simulated proof-of-work mining engine for supported coins.

Provides realistic hash-rate, profitability, and difficulty models for
all mineable coins in the database.  For coins not in the detailed
MINING_PROFILES mapping a generic profile is generated automatically.

GLOBAL AI SOURCES FLOW: participates via crypto_bot.py pipeline.
"""

from __future__ import annotations

import time
import random
from typing import Optional

from bots.crypto_bot.crypto_database import CRYPTO_DATABASE, get_coin, list_mineable_coins
from bots.crypto_bot.price_feed import get_price


# ---------------------------------------------------------------------------
# Mining profiles (hardware / hashrate / power stats per coin)
# ---------------------------------------------------------------------------

MINING_PROFILES: dict[str, dict] = {
    "BTC": {
        "algorithm": "SHA-256",
        "hashrate": "120 TH/s",
        "hashrate_val": 120e12,
        "power_w": 3_250,
        "daily_coins": 0.00006,
        "difficulty_label": "Very High",
        "hardware": "Antminer S19 XP",
    },
    "LTC": {
        "algorithm": "Scrypt",
        "hashrate": "1000 MH/s",
        "hashrate_val": 1e9,
        "power_w": 1_500,
        "daily_coins": 0.022,
        "difficulty_label": "Medium",
        "hardware": "Antminer L7",
    },
    "DOGE": {
        "algorithm": "Scrypt (merged with LTC)",
        "hashrate": "1200 MH/s",
        "hashrate_val": 1.2e9,
        "power_w": 1_500,
        "daily_coins": 18.0,
        "difficulty_label": "Medium",
        "hardware": "Antminer L7 (merged mine)",
    },
    "XMR": {
        "algorithm": "RandomX",
        "hashrate": "14 KH/s",
        "hashrate_val": 14_000,
        "power_w": 90,
        "daily_coins": 0.0054,
        "difficulty_label": "Medium",
        "hardware": "CPU (Ryzen 9 5950X)",
    },
    "ZEC": {
        "algorithm": "Equihash",
        "hashrate": "500 KSol/s",
        "hashrate_val": 500_000,
        "power_w": 1_400,
        "daily_coins": 0.039,
        "difficulty_label": "Medium",
        "hardware": "Innosilicon A9++",
    },
    "RVN": {
        "algorithm": "KawPoW",
        "hashrate": "25 MH/s",
        "hashrate_val": 25e6,
        "power_w": 180,
        "daily_coins": 44.8,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 3080",
    },
    "ERG": {
        "algorithm": "Autolykos2",
        "hashrate": "200 MH/s",
        "hashrate_val": 200e6,
        "power_w": 200,
        "daily_coins": 1.27,
        "difficulty_label": "Medium",
        "hardware": "NVIDIA RTX 3090",
    },
    "FLUX": {
        "algorithm": "ZelHash",
        "hashrate": "50 KSol/s",
        "hashrate_val": 50_000,
        "power_w": 190,
        "daily_coins": 2.46,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 3080",
    },
    "KAS": {
        "algorithm": "kHeavyHash",
        "hashrate": "5 TH/s",
        "hashrate_val": 5e12,
        "power_w": 2_400,
        "daily_coins": 266.0,
        "difficulty_label": "Medium",
        "hardware": "Antminer KS3",
    },
    "ALPH": {
        "algorithm": "Blake3 (sharded PoW)",
        "hashrate": "800 GH/s",
        "hashrate_val": 800e9,
        "power_w": 230,
        "daily_coins": 4.2,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 4090",
    },
    "BEAM": {
        "algorithm": "BeamHash III",
        "hashrate": "25 Sol/s",
        "hashrate_val": 25,
        "power_w": 200,
        "daily_coins": 22.5,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 3080",
    },
    "GRIN": {
        "algorithm": "Cuckoo Cycle",
        "hashrate": "1.5 GPS",
        "hashrate_val": 1.5e9,
        "power_w": 200,
        "daily_coins": 60.0,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 3080",
    },
    "FIRO": {
        "algorithm": "FiroPoW",
        "hashrate": "30 MH/s",
        "hashrate_val": 30e6,
        "power_w": 180,
        "daily_coins": 3.6,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 3080",
    },
    "VTC": {
        "algorithm": "Verthash",
        "hashrate": "1.5 MH/s",
        "hashrate_val": 1.5e6,
        "power_w": 150,
        "daily_coins": 14.4,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 3060",
    },
    "CFX": {
        "algorithm": "Octopus (PoW portion)",
        "hashrate": "100 MH/s",
        "hashrate_val": 100e6,
        "power_w": 200,
        "daily_coins": 86.4,
        "difficulty_label": "Low",
        "hardware": "NVIDIA RTX 3080",
    },
    "AR": {
        "algorithm": "Proof-of-Access",
        "hashrate": "N/A",
        "hashrate_val": 1,
        "power_w": 150,
        "daily_coins": 0.08,
        "difficulty_label": "Low",
        "hardware": "Standard Server",
    },
    "FIL": {
        "algorithm": "Proof-of-Spacetime",
        "hashrate": "N/A (storage-based)",
        "hashrate_val": 1,
        "power_w": 50,
        "daily_coins": 0.12,
        "difficulty_label": "Medium",
        "hardware": "Storage Miner (16 TB)",
    },
}

_ELECTRICITY_RATE_USD_PER_KWH = 0.10


def _generic_profile(symbol: str) -> dict:
    """Generate a basic mining profile for coins not in MINING_PROFILES."""
    coin = get_coin(symbol)
    algo = coin.get("algorithm", "Unknown") if coin else "Unknown"
    return {
        "algorithm": algo,
        "hashrate": "Simulated",
        "hashrate_val": 1,
        "power_w": 200,
        "daily_coins": 0.5,
        "difficulty_label": "Low",
        "hardware": "Generic Miner",
    }


def get_mining_profile(symbol: str) -> dict:
    """Return the mining profile for *symbol*, generating a generic one if needed."""
    sym = symbol.upper()
    return MINING_PROFILES.get(sym, _generic_profile(sym))


def simulate_mining(
    symbol: str,
    duration_hours: float = 1.0,
    electricity_rate: float = _ELECTRICITY_RATE_USD_PER_KWH,
    use_live_price: bool = False,
) -> dict:
    """
    Simulate mining *symbol* for *duration_hours*.

    Returns a dict with:
      coins_mined        : amount of coin produced
      revenue_usd        : gross revenue at current price
      electricity_cost   : electricity cost for the session
      net_profit_usd     : revenue minus electricity cost
      hashrate           : human-readable hashrate string
      algorithm          : mining algorithm name
      hardware           : recommended hardware
      duration_hours     : duration of the simulation
    """
    sym = symbol.upper()
    coin = get_coin(sym)
    if not coin:
        raise ValueError(f"Unknown coin: {sym}")
    if not coin.get("mineable", False):
        raise ValueError(
            f"{sym} ({coin['name']}) is not a mineable coin. "
            "Only proof-of-work coins can be mined."
        )

    profile = get_mining_profile(sym)
    price = get_price(sym, use_live=use_live_price) or coin["price_usd"]

    # Apply small variance to simulate real-world fluctuations
    seed = int(time.time() / 3600) + hash(sym + str(int(duration_hours)))
    rng = random.Random(seed)
    variance = rng.uniform(0.92, 1.08)

    coins_per_hour = profile["daily_coins"] / 24.0
    coins_mined = round(coins_per_hour * duration_hours * variance, 8)
    revenue_usd = round(coins_mined * price, 6)

    energy_kwh = profile["power_w"] * duration_hours / 1000.0
    electricity_cost = round(energy_kwh * electricity_rate, 6)
    net_profit_usd = round(revenue_usd - electricity_cost, 6)

    return {
        "symbol": sym,
        "name": coin["name"],
        "algorithm": profile["algorithm"],
        "hardware": profile["hardware"],
        "hashrate": profile["hashrate"],
        "duration_hours": duration_hours,
        "coins_mined": coins_mined,
        "price_usd": price,
        "revenue_usd": revenue_usd,
        "power_w": profile["power_w"],
        "energy_kwh": round(energy_kwh, 4),
        "electricity_rate_usd_per_kwh": electricity_rate,
        "electricity_cost_usd": electricity_cost,
        "net_profit_usd": net_profit_usd,
        "profitable": net_profit_usd > 0,
        "difficulty_label": profile["difficulty_label"],
    }


def mining_leaderboard(
    symbols: Optional[list[str]] = None,
    use_live_price: bool = False,
    top_n: int = 10,
) -> list[dict]:
    """
    Return a ranked list of the most profitable coins to mine right now.

    Parameters
    ----------
    symbols     : list of coin symbols to evaluate (default: all mineable)
    use_live_price : fetch live prices from CoinGecko
    top_n       : return the top N results
    """
    if symbols is None:
        symbols = [c["symbol"] for c in list_mineable_coins()]

    results = []
    for sym in symbols:
        try:
            result = simulate_mining(sym, duration_hours=24.0, use_live_price=use_live_price)
            result["daily_profit_usd"] = result["net_profit_usd"]
            results.append(result)
        except (ValueError, KeyError):
            continue

    results.sort(key=lambda r: r["daily_profit_usd"], reverse=True)
    return results[:top_n]


def calculate_break_even(
    symbol: str,
    hardware_cost_usd: float,
    use_live_price: bool = False,
) -> dict:
    """
    Calculate how many days until a mining setup breaks even.

    Parameters
    ----------
    symbol             : coin to mine
    hardware_cost_usd  : upfront cost of the mining hardware
    """
    daily = simulate_mining(symbol, duration_hours=24.0, use_live_price=use_live_price)
    daily_profit = daily["net_profit_usd"]

    if daily_profit <= 0:
        return {
            "symbol": symbol.upper(),
            "hardware_cost_usd": hardware_cost_usd,
            "daily_profit_usd": daily_profit,
            "break_even_days": None,
            "profitable": False,
            "message": "This coin is not currently profitable to mine at the given electricity rate.",
        }

    days = hardware_cost_usd / daily_profit
    return {
        "symbol": symbol.upper(),
        "hardware_cost_usd": hardware_cost_usd,
        "daily_profit_usd": round(daily_profit, 4),
        "break_even_days": round(days, 1),
        "break_even_months": round(days / 30, 1),
        "profitable": True,
        "message": f"Break-even in approximately {days:.0f} days.",
    }
