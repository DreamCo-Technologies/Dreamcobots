"""
DreamCo Global Wealth System — UI Screens Package

Provides structured Python representations of every major screen in the
DreamCo platform UI. Each module defines a screen class that can render
its content as a plain-text demo or as a structured dict suitable for
consumption by a frontend framework.

Screens
-------
- HomeDashboardScreen   — total balance, earnings, bots, hub overview
- WealthHubScreen       — treasury, members, ownership, voting panel
- BotControlCenterScreen — bot toggle, earnings per bot, automation settings
- WalletScreen          — deposit/withdraw, DreamCoin balance, history
- GovernancePanelScreen — proposals, voting, results
- InvestmentDashboardScreen — asset allocation, gold/silver, ROI tracking
- ReferralSystemScreen  — invite links, earnings tracker, team growth tree
"""

from .home_dashboard import HomeDashboardScreen
from .wealth_hub_screen import WealthHubScreen
from .bot_control_center import BotControlCenterScreen
from .wallet_screen import WalletScreen
from .governance_panel import GovernancePanelScreen
from .investment_dashboard import InvestmentDashboardScreen
from .referral_system import ReferralSystemScreen

__all__ = [
    "HomeDashboardScreen",
    "WealthHubScreen",
    "BotControlCenterScreen",
    "WalletScreen",
    "GovernancePanelScreen",
    "InvestmentDashboardScreen",
    "ReferralSystemScreen",
]
