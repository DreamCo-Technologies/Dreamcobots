# BuddyAI Financial Models
# Data models used throughout the autonomous financial system.
#
# NOTE: monetary amounts are currently represented as float for simplicity.
# For production deployments, replace float with decimal.Decimal to avoid
# floating-point rounding errors in financial accounting.

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TransactionType(Enum):
    TRANSFER = "transfer"
    PAYMENT = "payment"
    EARNING = "earning"
    REFUND = "refund"


class CardStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


@dataclass
class Account:
    """Represents a client or Buddy financial account."""

    owner_id: str
    owner_name: str
    balance: float = 0.0
    account_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_autonomous: bool = False  # True when the account belongs to Buddy in autonomous mode

    def deposit(self, amount: float) -> None:
        """Add funds to the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Deduct funds from the account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount

    def to_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "balance": self.balance,
            "is_autonomous": self.is_autonomous,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Transaction:
    """Records a single financial transaction."""

    sender_id: str
    recipient_id: str
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def complete(self) -> None:
        self.status = TransactionStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def fail(self) -> None:
        self.status = TransactionStatus.FAILED
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "amount": self.amount,
            "type": self.transaction_type.value,
            "status": self.status.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class Card:
    """Represents a virtual or physical payment card linked to a client account."""

    account_id: str
    cardholder_name: str
    card_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # Last 4 digits stored only; full PAN never persisted in plaintext
    last_four: str = "0000"
    card_type: str = "virtual"  # "virtual" or "physical"
    status: CardStatus = CardStatus.ACTIVE
    spending_limit: float = 1000.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def suspend(self) -> None:
        self.status = CardStatus.SUSPENDED

    def activate(self) -> None:
        self.status = CardStatus.ACTIVE

    def cancel(self) -> None:
        self.status = CardStatus.CANCELLED

    def to_dict(self) -> dict:
        return {
            "card_id": self.card_id,
            "account_id": self.account_id,
            "cardholder_name": self.cardholder_name,
            "last_four": self.last_four,
            "card_type": self.card_type,
            "status": self.status.value,
            "spending_limit": self.spending_limit,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Earning:
    """Tracks a single earning event and its 50/50 distribution."""

    source: str
    gross_amount: float
    buddy_share: float
    client_share: float
    earning_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "earning_id": self.earning_id,
            "source": self.source,
            "gross_amount": self.gross_amount,
            "buddy_share": self.buddy_share,
            "client_share": self.client_share,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }
