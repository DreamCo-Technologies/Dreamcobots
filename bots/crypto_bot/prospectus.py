"""
Prospectus — per-coin prospectus pages with market stats and real-time data.

GLOBAL AI SOURCES FLOW: participates via crypto_bot.py pipeline.
"""

from __future__ import annotations

from bots.crypto_bot.crypto_database import CRYPTO_DATABASE, get_coin, list_categories
from bots.crypto_bot.price_feed import get_price, get_price_change_24h


# ---------------------------------------------------------------------------
# Prospectus builder
# ---------------------------------------------------------------------------

def _format_large_number(n: float | None) -> str:
    """Return a human-readable abbreviation for large numbers."""
    if n is None:
        return "Unlimited"
    if n >= 1_000_000_000_000:
        return f"${n / 1_000_000_000_000:.2f}T"
    if n >= 1_000_000_000:
        return f"${n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"${n / 1_000_000:.2f}M"
    return f"${n:,.2f}"


def _format_supply(n: float | None) -> str:
    if n is None:
        return "Unlimited"
    if n >= 1_000_000_000_000:
        return f"{n / 1_000_000_000_000:.2f}T"
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    return f"{n:,.0f}"


def get_coin_prospectus(symbol: str, use_live_price: bool = False) -> dict:
    """
    Return a full prospectus dict for *symbol*.

    Parameters
    ----------
    symbol          : coin ticker (e.g. "BTC")
    use_live_price  : fetch live price from CoinGecko

    Raises
    ------
    ValueError if the symbol is not in the database.
    """
    sym = symbol.upper()
    coin = get_coin(sym)
    if not coin:
        raise ValueError(
            f"Unknown cryptocurrency symbol: {sym}. "
            f"Use list_all_prospectuses() to see supported coins."
        )

    price = get_price(sym, use_live=use_live_price) or coin["price_usd"]
    change_24h = get_price_change_24h(sym)
    market_cap = coin["circulating_supply"] * price if coin.get("circulating_supply") else coin.get("market_cap_usd", 0)

    # Build investment thesis points
    thesis = []
    if coin["category"] == "Layer 1":
        thesis.append("Core blockchain infrastructure — potential to power an entire ecosystem.")
    elif coin["category"] in ("DeFi",):
        thesis.append("Decentralised finance — eliminates intermediaries in lending/borrowing/trading.")
    elif coin["category"] in ("Privacy", "Privacy / Mining"):
        thesis.append("Privacy-preserving — transactions are untraceable and unlinkable.")
    elif coin["category"] == "Payments":
        thesis.append("Built for fast, low-cost global payments.")
    elif coin["category"] == "Layer 2":
        thesis.append("Scales the base layer — dramatically reduces fees and latency.")
    elif coin["category"] == "Stablecoin":
        thesis.append("Price-stable asset — ideal for holding value or earning yield.")
    elif "Meme" in coin["category"]:
        thesis.append("Community-driven — momentum and social sentiment drive value.")
    elif "Storage" in coin["category"]:
        thesis.append("Decentralised storage — disrupts traditional cloud providers.")
    elif "AI" in coin["category"] or "Data" in coin["category"]:
        thesis.append("AI / Data economy — captures value from the machine-learning wave.")
    elif "NFT" in coin["category"] or "Metaverse" in coin["category"]:
        thesis.append("Digital ownership layer — enables creator economies and virtual worlds.")
    elif coin["mineable"]:
        thesis.append("Proof-of-work security — backed by real energy expenditure.")

    if coin["max_supply"]:
        thesis.append(
            f"Scarce supply — hard cap of {_format_supply(coin['max_supply'])} coins."
        )
    else:
        thesis.append("Inflationary supply — relies on utility demand to maintain value.")

    if coin["launch_year"] <= 2015:
        thesis.append("Battle-tested — operational for over a decade.")

    return {
        "symbol": sym,
        "name": coin["name"],
        "category": coin["category"],
        "website": coin.get("website", ""),
        "description": coin["description"],
        "launch_year": coin["launch_year"],
        "algorithm": coin["algorithm"],
        "mineable": coin["mineable"],

        # Market data
        "current_price_usd": price,
        "price_change_24h_pct": change_24h,
        "market_cap_usd": round(market_cap, 2),
        "market_cap_formatted": _format_large_number(market_cap),
        "circulating_supply": coin.get("circulating_supply"),
        "circulating_supply_formatted": _format_supply(coin.get("circulating_supply")),
        "max_supply": coin.get("max_supply"),
        "max_supply_formatted": _format_supply(coin.get("max_supply")),
        "volume_24h_usd": coin.get("volume_24h_usd", 0),
        "volume_24h_formatted": _format_large_number(coin.get("volume_24h_usd", 0)),

        # Investment thesis
        "investment_thesis": thesis,

        # Risk label
        "risk_label": _risk_label(coin, change_24h),

        # Tags
        "tags": _build_tags(coin),
    }


def _risk_label(coin: dict, change_24h: float) -> str:
    if coin["category"] == "Stablecoin":
        return "Very Low"
    volatility = abs(change_24h)
    if coin["market_cap_usd"] >= 100_000_000_000 and volatility < 5:
        return "Low"
    if coin["market_cap_usd"] >= 10_000_000_000:
        return "Medium"
    if coin["market_cap_usd"] >= 1_000_000_000:
        return "High"
    return "Very High"


def _build_tags(coin: dict) -> list[str]:
    tags = [coin["category"]]
    if coin["mineable"]:
        tags.append("Mineable")
    if coin["max_supply"]:
        tags.append("Fixed Supply")
    else:
        tags.append("Inflationary")
    if coin["launch_year"] <= 2017:
        tags.append("OG Coin")
    if "Privacy" in coin["category"]:
        tags.append("Anonymous")
    if "DeFi" in coin["category"]:
        tags.append("Yield Farming")
    return tags


def list_all_prospectuses(
    category: str | None = None,
    use_live_prices: bool = False,
) -> list[dict]:
    """
    Return prospectus summaries for all coins (or a filtered subset).

    Parameters
    ----------
    category        : filter by category (e.g. "DeFi", "Layer 1")
    use_live_prices : fetch live prices from CoinGecko
    """
    symbols = [
        sym for sym, data in CRYPTO_DATABASE.items()
        if category is None or data["category"].lower() == category.lower()
    ]
    return [
        get_coin_prospectus(sym, use_live_price=use_live_prices)
        for sym in symbols
    ]


def prospectus_text(symbol: str, use_live_price: bool = False) -> str:
    """
    Return a human-readable prospectus page for *symbol*.
    """
    p = get_coin_prospectus(symbol, use_live_price=use_live_price)
    change_sign = "+" if p["price_change_24h_pct"] >= 0 else ""
    lines = [
        f"{'=' * 60}",
        f"  {p['name']} ({p['symbol']}) — Crypto Prospectus",
        f"{'=' * 60}",
        f"  Category   : {p['category']}",
        f"  Algorithm  : {p['algorithm']}",
        f"  Mineable   : {'Yes' if p['mineable'] else 'No'}",
        f"  Launch     : {p['launch_year']}",
        f"  Website    : {p['website']}",
        "",
        f"  Current Price  : ${p['current_price_usd']:,.6f}",
        f"  24h Change     : {change_sign}{p['price_change_24h_pct']:.2f}%",
        f"  Market Cap     : {p['market_cap_formatted']}",
        f"  24h Volume     : {p['volume_24h_formatted']}",
        f"  Circulating    : {p['circulating_supply_formatted']}",
        f"  Max Supply     : {p['max_supply_formatted']}",
        f"  Risk Level     : {p['risk_label']}",
        "",
        "  Description",
        "  -----------",
        f"  {p['description']}",
        "",
        "  Investment Thesis",
        "  -----------------",
    ]
    for point in p["investment_thesis"]:
        lines.append(f"  • {point}")
    lines += [
        "",
        f"  Tags: {', '.join(p['tags'])}",
        f"{'=' * 60}",
    ]
    return "\n".join(lines)
