"""
Dashboard — unified tracking interface for the cryptocurrency management system.

Renders a console-based dashboard summarising portfolio, market overview,
mining stats, and recent transactions.

GLOBAL AI SOURCES FLOW: participates via crypto_bot.py pipeline.
"""

from __future__ import annotations

from typing import Optional

from bots.crypto_bot.portfolio import Portfolio
from bots.crypto_bot.price_feed import get_market_summary, get_price_change_24h
from bots.crypto_bot.crypto_database import CRYPTO_DATABASE


_SEPARATOR = "─" * 72
_DOUBLE_SEP = "═" * 72


def _pct_str(pct: float) -> str:
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def _usd(val: float) -> str:
    if abs(val) >= 1_000_000_000:
        return f"${val / 1_000_000_000:.2f}B"
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:.2f}M"
    if abs(val) >= 1_000:
        return f"${val:,.2f}"
    return f"${val:.4f}"


def render_portfolio(portfolio: Portfolio, use_live: bool = False) -> str:
    """
    Render the user's portfolio holdings as a formatted table.
    """
    summary = portfolio.summary(use_live_prices=use_live)
    lines = [
        _DOUBLE_SEP,
        "  DREAMCOBOTS — CRYPTO PORTFOLIO",
        _DOUBLE_SEP,
        f"  Cash Balance   : {_usd(summary['usd_balance'])}",
        f"  Portfolio Value: {_usd(summary['total_portfolio_value_usd'])}",
        f"  Market Value   : {_usd(summary['total_market_value_usd'])}",
        f"  Cost Basis     : {_usd(summary['total_cost_basis_usd'])}",
        f"  Unrealised P&L : {_usd(summary['total_unrealised_pnl_usd'])}",
        f"  Realised P&L   : {_usd(summary['total_realised_pnl_usd'])}",
        f"  Total P&L      : {_usd(summary['total_pnl_usd'])}",
        _SEPARATOR,
        f"  {'Symbol':<8} {'Amount':>18} {'Price USD':>14} {'Value USD':>14} {'P&L USD':>12}",
        _SEPARATOR,
    ]

    for h in summary["holdings"]:
        sym = h["symbol"]
        amount = h["total_amount"]
        price = h.get("current_price_usd", 0.0)
        value = h.get("market_value_usd", 0.0)
        pnl = h.get("total_pnl_usd", 0.0)
        lines.append(
            f"  {sym:<8} {amount:>18.6f} {_usd(price):>14} {_usd(value):>14} {_usd(pnl):>12}"
        )

    lines += [
        _SEPARATOR,
        f"  Holdings: {summary['num_holdings']}   Transactions: {summary['num_transactions']}",
        _DOUBLE_SEP,
    ]
    return "\n".join(lines)


def render_market_overview(symbols: Optional[list[str]] = None, use_live: bool = False) -> str:
    """
    Render a live market overview table for the given symbols.
    Default symbols cover the 12 coins shown in the UI mockup.
    """
    if symbols is None:
        symbols = [
            "BTC", "ETH", "SOL", "ADA", "DOT",
            "AVAX", "LINK", "MATIC", "LTC", "XRP",
            "DOGE", "TON",
        ]

    data = get_market_summary(symbols, use_live=use_live)
    lines = [
        _DOUBLE_SEP,
        "  MARKET OVERVIEW",
        _DOUBLE_SEP,
        f"  {'Symbol':<8} {'Name':<18} {'Price USD':>14} {'24h':>8} {'Market Cap':>14}",
        _SEPARATOR,
    ]

    for item in data:
        change = item["change_24h_pct"]
        pct = _pct_str(change)
        lines.append(
            f"  {item['symbol']:<8} {item['name']:<18} "
            f"{_usd(item['price_usd']):>14} {pct:>8} "
            f"{_usd(item['market_cap_usd']):>14}"
        )

    lines += [_DOUBLE_SEP]
    return "\n".join(lines)


def render_transactions(portfolio: Portfolio, limit: int = 10) -> str:
    """
    Render a table of the most recent transactions.
    """
    txs = portfolio.get_transactions(limit=limit)
    lines = [
        _DOUBLE_SEP,
        "  RECENT TRANSACTIONS",
        _DOUBLE_SEP,
        f"  {'ID':<10} {'Type':<10} {'Symbol':<8} {'Amount':>14} {'Price USD':>12} {'Total USD':>12}",
        _SEPARATOR,
    ]
    for t in txs:
        lines.append(
            f"  {t['tx_id']:<10} {t['tx_type']:<10} {t['symbol']:<8} "
            f"{t['amount']:>14.6f} {_usd(t['price_usd']):>12} {_usd(t['total_usd']):>12}"
        )
    if not txs:
        lines.append("  No transactions yet.")
    lines += [_DOUBLE_SEP]
    return "\n".join(lines)


def render_mining_stats(mining_results: list[dict]) -> str:
    """
    Render a mining leaderboard / stats table.

    Parameters
    ----------
    mining_results : list of dicts as returned by mining.simulate_mining()
                     or mining.mining_leaderboard()
    """
    lines = [
        _DOUBLE_SEP,
        "  MINING STATS",
        _DOUBLE_SEP,
        f"  {'Symbol':<8} {'Algorithm':<22} {'Hashrate':<14} {'Daily Coins':>12} {'Net Profit':>12}",
        _SEPARATOR,
    ]
    for r in mining_results:
        lines.append(
            f"  {r['symbol']:<8} {r['algorithm']:<22} {r['hashrate']:<14} "
            f"{r['coins_mined']:>12.6f} {_usd(r['net_profit_usd']):>12}"
        )
    if not mining_results:
        lines.append("  No mining sessions yet.")
    lines += [_DOUBLE_SEP]
    return "\n".join(lines)


def render_full_dashboard(
    portfolio: Portfolio,
    mining_results: Optional[list[dict]] = None,
    market_symbols: Optional[list[str]] = None,
    use_live: bool = False,
) -> str:
    """
    Render all dashboard sections as a single string.
    """
    sections = [
        render_portfolio(portfolio, use_live=use_live),
        "",
        render_market_overview(symbols=market_symbols, use_live=use_live),
        "",
        render_transactions(portfolio),
    ]
    if mining_results:
        sections += ["", render_mining_stats(mining_results)]

    return "\n".join(sections)
