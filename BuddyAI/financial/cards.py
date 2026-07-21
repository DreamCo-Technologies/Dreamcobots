# BuddyAI Card Processor
# Issues and processes virtual/physical card payments for clients enrolled in
# Buddy's financial system.

import secrets
import string
from typing import Dict, List, Optional

from .models import Account, Card, CardStatus, Transaction, TransactionType


def _generate_last_four() -> str:
    """Generate a random 4-digit string to represent card last-four digits."""
    return "".join(secrets.choice(string.digits) for _ in range(4))


class CardProcessor:
    """
    Manages card issuance and payment processing for BuddyAI clients.

    Security notes:
    - Full card PANs are never stored.  Only the last four digits are retained.
    - Card IDs are UUIDs; no sequential or guessable identifiers are used.
    - Spending limits are enforced on every payment attempt.
    """

    def __init__(self) -> None:
        self._cards: Dict[str, Card] = {}
        self._account_cards: Dict[str, List[str]] = {}  # account_id -> [card_id, ...]
        self._transactions: Dict[str, Transaction] = {}

    # ------------------------------------------------------------------
    # Card issuance
    # ------------------------------------------------------------------

    def issue_card(
        self,
        account: Account,
        cardholder_name: str,
        card_type: str = "virtual",
        spending_limit: float = 1000.0,
    ) -> Card:
        """
        Issue a new card for an account.

        Args:
            account: The Account to link the card to.
            cardholder_name: Full name of the cardholder.
            card_type: "virtual" or "physical".
            spending_limit: Maximum single-transaction spend allowed.

        Returns:
            The newly issued Card.

        Raises:
            ValueError: If card_type is invalid or spending_limit is not positive.
        """
        if card_type not in ("virtual", "physical"):
            raise ValueError("card_type must be 'virtual' or 'physical'.")
        if spending_limit <= 0:
            raise ValueError("spending_limit must be greater than zero.")

        card = Card(
            account_id=account.account_id,
            cardholder_name=cardholder_name,
            last_four=_generate_last_four(),
            card_type=card_type,
            spending_limit=spending_limit,
        )

        self._cards[card.card_id] = card
        self._account_cards.setdefault(account.account_id, []).append(card.card_id)
        return card

    def get_card(self, card_id: str) -> Optional[Card]:
        """Retrieve a card by its ID."""
        return self._cards.get(card_id)

    def list_cards_for_account(self, account_id: str) -> List[Card]:
        """Return all cards associated with a given account."""
        return [
            self._cards[cid]
            for cid in self._account_cards.get(account_id, [])
            if cid in self._cards
        ]

    def suspend_card(self, card_id: str) -> Card:
        """Suspend an active card."""
        card = self._get_card_or_raise(card_id)
        card.suspend()
        return card

    def activate_card(self, card_id: str) -> Card:
        """Re-activate a suspended card."""
        card = self._get_card_or_raise(card_id)
        card.activate()
        return card

    def cancel_card(self, card_id: str) -> Card:
        """Permanently cancel a card."""
        card = self._get_card_or_raise(card_id)
        card.cancel()
        return card

    # ------------------------------------------------------------------
    # Payment processing
    # ------------------------------------------------------------------

    def charge_card(
        self,
        card_id: str,
        payer_account: Account,
        payee_account: Account,
        amount: float,
        description: str = "",
    ) -> Transaction:
        """
        Charge a card for a payment.

        The amount is deducted from *payer_account* and credited to *payee_account*.

        Args:
            card_id: The card to charge.
            payer_account: Account funds are debited from.
            payee_account: Account funds are credited to.
            amount: Charge amount (must be positive and within the card's spending limit).
            description: Optional description for the transaction.

        Returns:
            The completed Transaction.

        Raises:
            ValueError: If the card is not active, the amount exceeds the spending limit,
                        or the payer has insufficient funds.
        """
        card = self._get_card_or_raise(card_id)

        if card.status != CardStatus.ACTIVE:
            raise ValueError(
                f"Card {card_id} is not active (status: {card.status.value})."
            )
        if amount <= 0:
            raise ValueError("Charge amount must be greater than zero.")
        if amount > card.spending_limit:
            raise ValueError(
                f"Charge amount ${amount:.2f} exceeds the card spending limit "
                f"of ${card.spending_limit:.2f}."
            )

        txn = Transaction(
            sender_id=payer_account.account_id,
            recipient_id=payee_account.account_id,
            amount=amount,
            transaction_type=TransactionType.PAYMENT,
            description=description or f"Card charge ****{card.last_four}",
        )

        try:
            payer_account.withdraw(amount)
            payee_account.deposit(amount)
            txn.complete()
        except ValueError:
            txn.fail()
            self._transactions[txn.transaction_id] = txn
            raise

        self._transactions[txn.transaction_id] = txn
        return txn

    # ------------------------------------------------------------------
    # Transaction history
    # ------------------------------------------------------------------

    def get_card_transactions(self, card_id: str) -> List[Transaction]:
        """
        Return all transactions processed through a given card.

        Note: transactions are linked by card ownership; a card must be in
        ``_cards`` and its account must match.
        """
        card = self._get_card_or_raise(card_id)
        return [
            txn
            for txn in self._transactions.values()
            if txn.sender_id == card.account_id
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_card_or_raise(self, card_id: str) -> Card:
        card = self._cards.get(card_id)
        if card is None:
            raise ValueError(f"Card {card_id} not found.")
        return card
