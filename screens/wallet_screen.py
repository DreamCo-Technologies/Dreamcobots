"""
DreamCo — Wallet Screen

Manages a user's DreamCo wallet: deposit and withdraw USD, view DreamCoin
balance and staking, and browse full transaction history.

Fields
------
- USD balance available for deposit/withdrawal
- DreamCoin balance + staking status
- Deposit / Withdraw forms
- Transaction history table
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    DIVIDEND = "dividend"
    DREAMCOIN_EARNED = "dreamcoin_earned"
    DREAMCOIN_SPENT = "dreamcoin_spent"
    FEE = "fee"


@dataclass
class Transaction:
    """A single wallet transaction record."""
    tx_id: str
    tx_type: TransactionType
    amount_usd: float = 0.0
    dreamcoin_amount: float = 0.0
    description: str = ""
    hub_name: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def timestamp_str(self) -> str:
        return self.timestamp.strftime("%Y-%m-%d %H:%M")

    def amount_str(self) -> str:
        if self.amount_usd != 0:
            sign = "+" if self.amount_usd > 0 else ""
            return f"{sign}${self.amount_usd:,.2f}"
        if self.dreamcoin_amount != 0:
            sign = "+" if self.dreamcoin_amount > 0 else ""
            return f"{sign}{self.dreamcoin_amount:,.0f} DC"
        return "$0.00"


class WalletScreen:
    """
    Wallet Screen for the DreamCo platform.

    Displays a member's USD balance, DreamCoin holdings, deposit/withdraw
    controls, and a full transaction history.

    Usage
    -----
        screen = WalletScreen(
            user_id="alice",
            user_name="Alice Johnson",
            usd_balance=2500.0,
            dreamcoin_balance=450.0,
        )
        print(screen.render())
    """

    SCREEN_NAME = "Wallet"
    ROUTE = "/wallet"

    def __init__(
        self,
        user_id: str,
        user_name: str = "Member",
        usd_balance: float = 0.0,
        dreamcoin_balance: float = 0.0,
        dreamcoin_staked: float = 0.0,
    ) -> None:
        self.user_id = user_id
        self.user_name = user_name
        self.usd_balance = usd_balance
        self.dreamcoin_balance = dreamcoin_balance
        self.dreamcoin_staked = dreamcoin_staked
        self._transactions: list[Transaction] = []

    def add_transaction(self, tx: Transaction) -> None:
        self._transactions.append(tx)

    def transaction_count(self) -> int:
        return len(self._transactions)

    def total_deposited(self) -> float:
        return sum(
            t.amount_usd for t in self._transactions
            if t.tx_type == TransactionType.DEPOSIT
        )

    def total_withdrawn(self) -> float:
        return sum(
            t.amount_usd for t in self._transactions
            if t.tx_type == TransactionType.WITHDRAWAL
        )

    def total_dividends(self) -> float:
        return sum(
            t.amount_usd for t in self._transactions
            if t.tx_type == TransactionType.DIVIDEND
        )

    def render(self) -> str:
        """Return a plain-text demo rendering of the Wallet screen."""
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║              DREAMCO — WALLET                        ║",
            "╚══════════════════════════════════════════════════════╝",
            f"  {self.user_name}",
            "",
            "  ┌──────────────────────────────────────────────────┐",
            "  │  USD Balance                                      │",
            f"  │  ${self.usd_balance:,.2f}                                  │",
            "  ├──────────────────────────────────────────────────┤",
            "  │  DreamCoin                                        │",
            f"  │  Balance: {self.dreamcoin_balance:,.0f} DC  |  "
            f"Staked: {self.dreamcoin_staked:,.0f} DC        │",
            "  └──────────────────────────────────────────────────┘",
            "",
            "  SUMMARY",
            f"  Total Deposited:  ${self.total_deposited():,.2f}",
            f"  Total Withdrawn:  ${self.total_withdrawn():,.2f}",
            f"  Total Dividends:  ${self.total_dividends():,.2f}",
            "",
            "  [Deposit]  [Withdraw]  [Stake DreamCoin]  [Transfer]",
            "",
            "  TRANSACTION HISTORY",
            f"  {'Date':<18} {'Type':<20} {'Amount':>16} {'Hub/Note':<25}",
            "  " + "─" * 82,
        ]
        if not self._transactions:
            lines.append("  No transactions yet.")
        else:
            for tx in sorted(self._transactions, key=lambda t: t.timestamp, reverse=True)[:20]:
                lines.append(
                    f"  {tx.timestamp_str():<18} {tx.tx_type.value:<20} "
                    f"{tx.amount_str():>16}  {(tx.hub_name or tx.description)[:25]:<25}"
                )
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "usd_balance": round(self.usd_balance, 2),
            "dreamcoin_balance": self.dreamcoin_balance,
            "dreamcoin_staked": self.dreamcoin_staked,
            "total_deposited_usd": round(self.total_deposited(), 2),
            "total_withdrawn_usd": round(self.total_withdrawn(), 2),
            "total_dividends_usd": round(self.total_dividends(), 2),
            "transactions": [
                {
                    "tx_id": t.tx_id,
                    "type": t.tx_type.value,
                    "amount_usd": t.amount_usd,
                    "dreamcoin_amount": t.dreamcoin_amount,
                    "description": t.description,
                    "hub_name": t.hub_name,
                    "timestamp": t.timestamp_str(),
                }
                for t in sorted(self._transactions, key=lambda x: x.timestamp, reverse=True)
            ],
        }

    @classmethod
    def demo(cls) -> "WalletScreen":
        """Return a pre-populated demo instance."""
        from datetime import timedelta
        screen = cls(
            user_id="alice",
            user_name="Alice Johnson",
            usd_balance=2_547.50,
            dreamcoin_balance=450.0,
            dreamcoin_staked=200.0,
        )
        base = datetime(2025, 3, 15, 10, 0, tzinfo=timezone.utc)
        screen.add_transaction(Transaction(
            "tx-001", TransactionType.DEPOSIT,
            amount_usd=1_000.0, hub_name="Family Wealth Circle",
            timestamp=base,
        ))
        screen.add_transaction(Transaction(
            "tx-002", TransactionType.DIVIDEND,
            amount_usd=320.50, hub_name="Family Wealth Circle",
            timestamp=base + timedelta(days=7),
        ))
        screen.add_transaction(Transaction(
            "tx-003", TransactionType.DEPOSIT,
            amount_usd=500.0, hub_name="Tech Entrepreneurs Pool",
            timestamp=base + timedelta(days=10),
        ))
        screen.add_transaction(Transaction(
            "tx-004", TransactionType.DREAMCOIN_EARNED,
            dreamcoin_amount=150.0, description="Referral Bot reward",
            timestamp=base + timedelta(days=12),
        ))
        screen.add_transaction(Transaction(
            "tx-005", TransactionType.WITHDRAWAL,
            amount_usd=200.0, description="Personal withdrawal",
            timestamp=base + timedelta(days=15),
        ))
        return screen
