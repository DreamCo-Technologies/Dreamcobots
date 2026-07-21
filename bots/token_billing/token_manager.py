"""
Token manager for the DreamCobots billing system.

Manages token credit balances for each user account.  Token credits are
separate from the daily free allowance granted by the subscription tier;
purchased credits never expire and are consumed before the daily allowance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


class InsufficientTokensError(Exception):
    """Raised when a deduction exceeds the available token balance."""


@dataclass
class TokenLedgerEntry:
    """A single entry in a user's token ledger.

    Attributes
    ----------
    timestamp : datetime
        When the entry was recorded.
    delta : int
        Positive for credits, negative for debits.
    description : str
        Human-readable reason for the transaction.
    balance_after : int
        Running balance after this entry.
    """

    timestamp: datetime
    delta: int
    description: str
    balance_after: int


@dataclass
class TokenAccount:
    """Token balance and ledger for a single user.

    Attributes
    ----------
    user_id : str
        Unique user identifier.
    purchased_tokens : int
        Non-expiring credits purchased by the user.
    daily_tokens_used : int
        Free daily tokens consumed today.
    last_daily_reset : date
        The date of the last daily token reset.
    ledger : list[TokenLedgerEntry]
        Full transaction history.
    """

    user_id: str
    purchased_tokens: int = 0
    daily_tokens_used: int = 0
    last_daily_reset: date = field(default_factory=date.today)
    ledger: list = field(default_factory=list)

    def reset_daily_if_needed(self, daily_allowance: int, today: Optional[date] = None) -> None:
        """Reset the daily token counter if the date has changed."""
        today = today or date.today()
        if self.last_daily_reset < today:
            self.daily_tokens_used = 0
            self.last_daily_reset = today

    def available_tokens(self, daily_allowance: int, today: Optional[date] = None) -> int:
        """Return total available tokens (purchased + remaining daily allowance).

        Parameters
        ----------
        daily_allowance : int
            The tier's daily free token allowance (use a large number for
            unlimited tiers and cap externally if needed).
        today : date, optional
            Override for testing.
        """
        self.reset_daily_if_needed(daily_allowance, today)
        remaining_daily = max(0, daily_allowance - self.daily_tokens_used)
        return self.purchased_tokens + remaining_daily


class TokenManager:
    """Manages token balances across all user accounts.

    Parameters
    ----------
    unlimited_daily_sentinel : int
        Sentinel value used as the daily_allowance for unlimited-tier users.
        Defaults to ``10_000_000`` (10 million tokens/day).
    """

    UNLIMITED_SENTINEL: int = 10_000_000

    def __init__(self) -> None:
        self._accounts: dict[str, TokenAccount] = {}

    # ------------------------------------------------------------------
    # Account lifecycle
    # ------------------------------------------------------------------

    def create_account(self, user_id: str) -> TokenAccount:
        """Create a token account for *user_id* if it does not already exist."""
        if user_id not in self._accounts:
            self._accounts[user_id] = TokenAccount(user_id=user_id)
        return self._accounts[user_id]

    def get_account(self, user_id: str) -> TokenAccount:
        """Return the account for *user_id*.

        Raises
        ------
        KeyError
            If no account exists for *user_id*.
        """
        if user_id not in self._accounts:
            raise KeyError(f"No token account found for user '{user_id}'.")
        return self._accounts[user_id]

    # ------------------------------------------------------------------
    # Credits
    # ------------------------------------------------------------------

    def add_tokens(self, user_id: str, amount: int, description: str = "Token purchase") -> int:
        """Add purchased (non-expiring) *amount* tokens to *user_id*.

        Parameters
        ----------
        user_id : str
            Target user.
        amount : int
            Number of tokens to add (must be positive).
        description : str
            Ledger description.

        Returns
        -------
        int
            New purchased token balance.
        """
        if amount <= 0:
            raise ValueError(f"Token amount must be positive; got {amount}.")
        account = self.get_account(user_id)
        account.purchased_tokens += amount
        account.ledger.append(
            TokenLedgerEntry(
                timestamp=datetime.utcnow(),
                delta=amount,
                description=description,
                balance_after=account.purchased_tokens,
            )
        )
        return account.purchased_tokens

    # ------------------------------------------------------------------
    # Debits
    # ------------------------------------------------------------------

    def deduct_tokens(
        self,
        user_id: str,
        cost: int,
        daily_allowance: int,
        description: str = "AI model usage",
        today: Optional[date] = None,
    ) -> int:
        """Deduct *cost* tokens from *user_id*.

        Purchased credits are consumed first; daily allowance is drawn on only
        after purchased credits are exhausted.

        Parameters
        ----------
        user_id : str
            Target user.
        cost : int
            Number of tokens to deduct (must be positive).
        daily_allowance : int
            The tier's daily free token allowance.
        description : str
            Ledger description.
        today : date, optional
            Override for testing.

        Returns
        -------
        int
            Remaining purchased token balance.

        Raises
        ------
        InsufficientTokensError
            If *cost* exceeds the total available tokens.
        """
        if cost <= 0:
            raise ValueError(f"Deduction cost must be positive; got {cost}.")
        account = self.get_account(user_id)
        account.reset_daily_if_needed(daily_allowance, today)
        available = account.available_tokens(daily_allowance, today)
        if cost > available:
            raise InsufficientTokensError(
                f"User '{user_id}' has {available} tokens available but {cost} were requested."
            )
        # Consume purchased credits first
        if account.purchased_tokens >= cost:
            account.purchased_tokens -= cost
        else:
            remainder = cost - account.purchased_tokens
            account.purchased_tokens = 0
            account.daily_tokens_used += remainder

        account.ledger.append(
            TokenLedgerEntry(
                timestamp=datetime.utcnow(),
                delta=-cost,
                description=description,
                balance_after=account.purchased_tokens,
            )
        )
        return account.purchased_tokens

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_balance(self, user_id: str, daily_allowance: int) -> dict:
        """Return a balance summary for *user_id*.

        Returns
        -------
        dict
            Keys: ``purchased_tokens``, ``daily_tokens_remaining``,
            ``total_available``.
        """
        account = self.get_account(user_id)
        account.reset_daily_if_needed(daily_allowance)
        remaining_daily = max(0, daily_allowance - account.daily_tokens_used)
        return {
            "user_id": user_id,
            "purchased_tokens": account.purchased_tokens,
            "daily_tokens_remaining": remaining_daily,
            "total_available": account.purchased_tokens + remaining_daily,
        }

    def get_ledger(self, user_id: str) -> list:
        """Return the full transaction ledger for *user_id*."""
        return list(self.get_account(user_id).ledger)
