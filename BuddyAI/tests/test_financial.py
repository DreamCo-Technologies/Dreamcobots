# Tests for BuddyAI financial system.

import pytest

from BuddyAI.financial.models import (
    Account,
    Card,
    CardStatus,
    Earning,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from BuddyAI.financial.transactions import TransactionProcessor
from BuddyAI.financial.earnings import EarningsDistributor, BUDDY_SHARE_RATIO, CLIENT_SHARE_RATIO
from BuddyAI.financial.cards import CardProcessor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_account(owner_id: str, name: str, balance: float = 0.0) -> Account:
    acc = Account(owner_id=owner_id, owner_name=name, balance=balance)
    return acc


# ---------------------------------------------------------------------------
# Account model tests
# ---------------------------------------------------------------------------

class TestAccount:
    def test_deposit_increases_balance(self):
        acc = make_account("u1", "Alice", 100.0)
        acc.deposit(50.0)
        assert acc.balance == 150.0

    def test_withdraw_decreases_balance(self):
        acc = make_account("u1", "Alice", 100.0)
        acc.withdraw(40.0)
        assert acc.balance == 60.0

    def test_withdraw_insufficient_funds_raises(self):
        acc = make_account("u1", "Alice", 10.0)
        with pytest.raises(ValueError, match="Insufficient funds"):
            acc.withdraw(50.0)

    def test_deposit_zero_raises(self):
        acc = make_account("u1", "Alice", 0.0)
        with pytest.raises(ValueError):
            acc.deposit(0.0)

    def test_withdraw_zero_raises(self):
        acc = make_account("u1", "Alice", 100.0)
        with pytest.raises(ValueError):
            acc.withdraw(0.0)

    def test_to_dict_contains_expected_keys(self):
        acc = make_account("u1", "Alice", 50.0)
        d = acc.to_dict()
        assert "account_id" in d
        assert d["owner_name"] == "Alice"
        assert d["balance"] == 50.0


# ---------------------------------------------------------------------------
# TransactionProcessor tests
# ---------------------------------------------------------------------------

class TestTransactionProcessor:
    def setup_method(self):
        self.processor = TransactionProcessor()
        self.alice = self.processor.register_account(make_account("u1", "Alice", 500.0))
        self.bob = self.processor.register_account(make_account("u2", "Bob", 200.0))

    def test_register_duplicate_raises(self):
        with pytest.raises(ValueError, match="already registered"):
            self.processor.register_account(self.alice)

    def test_transfer_updates_balances(self):
        self.processor.transfer(self.alice.account_id, self.bob.account_id, 100.0)
        assert self.alice.balance == 400.0
        assert self.bob.balance == 300.0

    def test_transfer_returns_completed_transaction(self):
        txn = self.processor.transfer(self.alice.account_id, self.bob.account_id, 50.0)
        assert txn.status == TransactionStatus.COMPLETED
        assert txn.transaction_type == TransactionType.TRANSFER
        assert txn.amount == 50.0

    def test_transfer_insufficient_funds_fails(self):
        with pytest.raises(ValueError, match="Insufficient funds"):
            self.processor.transfer(self.alice.account_id, self.bob.account_id, 999.0)
        # Alice's balance should be unchanged
        assert self.alice.balance == 500.0

    def test_transfer_zero_raises(self):
        with pytest.raises(ValueError):
            self.processor.transfer(self.alice.account_id, self.bob.account_id, 0.0)

    def test_transfer_unknown_sender_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.processor.transfer("unknown", self.bob.account_id, 10.0)

    def test_process_payment_records_correct_type(self):
        txn = self.processor.process_payment(self.alice.account_id, self.bob.account_id, 75.0)
        assert txn.transaction_type == TransactionType.PAYMENT
        assert txn.status == TransactionStatus.COMPLETED

    def test_refund_reverses_transfer(self):
        txn = self.processor.transfer(self.alice.account_id, self.bob.account_id, 100.0)
        self.processor.refund(txn.transaction_id)
        assert self.alice.balance == 500.0
        assert self.bob.balance == 200.0

    def test_refund_unknown_transaction_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.processor.refund("nonexistent-id")

    def test_refund_non_completed_raises(self):
        # Create a failed transaction by trying to overdraft (it gets recorded as FAILED)
        try:
            self.processor.transfer(self.alice.account_id, self.bob.account_id, 9999.0)
        except ValueError:
            pass
        txns = self.processor.get_account_transactions(self.alice.account_id)
        failed_txn = next(t for t in txns if t.status == TransactionStatus.FAILED)
        with pytest.raises(ValueError, match="Only completed"):
            self.processor.refund(failed_txn.transaction_id)

    def test_get_account_transactions(self):
        self.processor.transfer(self.alice.account_id, self.bob.account_id, 10.0)
        self.processor.transfer(self.alice.account_id, self.bob.account_id, 20.0)
        txns = self.processor.get_account_transactions(self.alice.account_id)
        assert len(txns) == 2

    def test_get_account_balance(self):
        assert self.processor.get_account_balance(self.alice.account_id) == 500.0


# ---------------------------------------------------------------------------
# EarningsDistributor tests
# ---------------------------------------------------------------------------

class TestEarningsDistributor:
    def setup_method(self):
        self.buddy_account = make_account("buddy", "Buddy", 0.0)
        self.client_account = make_account("c1", "ClientOne", 0.0)
        self.distributor = EarningsDistributor(buddy_account=self.buddy_account)

    def test_distribute_50_50_split(self):
        earning, buddy_txn, client_txn = self.distributor.distribute(
            self.client_account, gross_amount=200.0
        )
        assert earning.buddy_share == 100.0
        assert earning.client_share == 100.0
        assert self.buddy_account.balance == 100.0
        assert self.client_account.balance == 100.0

    def test_distribute_correct_ratios(self):
        gross = 300.0
        earning, _, _ = self.distributor.distribute(self.client_account, gross)
        assert earning.buddy_share == pytest.approx(gross * BUDDY_SHARE_RATIO)
        assert earning.client_share == pytest.approx(gross * CLIENT_SHARE_RATIO)

    def test_distribute_zero_raises(self):
        with pytest.raises(ValueError):
            self.distributor.distribute(self.client_account, 0.0)

    def test_distribute_negative_raises(self):
        with pytest.raises(ValueError):
            self.distributor.distribute(self.client_account, -50.0)

    def test_compute_share_distribution(self):
        earning, _, _ = self.distributor.distribute_compute_share(
            self.client_account, compute_profit=400.0
        )
        assert earning.source == "compute_share"
        assert earning.buddy_share == 200.0
        assert earning.client_share == 200.0

    def test_total_buddy_earnings(self):
        self.distributor.distribute(self.client_account, 100.0)
        self.distributor.distribute(self.client_account, 200.0)
        assert self.distributor.total_buddy_earnings() == 150.0  # 50% of 300

    def test_total_client_earnings(self):
        self.distributor.distribute(self.client_account, 100.0)
        self.distributor.distribute(self.client_account, 200.0)
        total = self.distributor.total_client_earnings(self.client_account.account_id)
        assert total == 150.0  # 50% of 300

    def test_list_earnings(self):
        self.distributor.distribute(self.client_account, 100.0)
        self.distributor.distribute(self.client_account, 50.0)
        assert len(self.distributor.list_earnings()) == 2

    def test_get_earning_not_found_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.distributor.get_earning("nonexistent-id")


# ---------------------------------------------------------------------------
# CardProcessor tests
# ---------------------------------------------------------------------------

class TestCardProcessor:
    def setup_method(self):
        self.processor = CardProcessor()
        self.payer = make_account("u1", "Alice", 500.0)
        self.payee = make_account("u2", "Merchant", 0.0)

    def test_issue_card_creates_card(self):
        card = self.processor.issue_card(self.payer, "Alice")
        assert card.account_id == self.payer.account_id
        assert card.status == CardStatus.ACTIVE
        assert len(card.last_four) == 4

    def test_issue_card_invalid_type_raises(self):
        with pytest.raises(ValueError, match="card_type"):
            self.processor.issue_card(self.payer, "Alice", card_type="debit")

    def test_issue_card_invalid_limit_raises(self):
        with pytest.raises(ValueError, match="spending_limit"):
            self.processor.issue_card(self.payer, "Alice", spending_limit=0.0)

    def test_suspend_and_activate_card(self):
        card = self.processor.issue_card(self.payer, "Alice")
        self.processor.suspend_card(card.card_id)
        assert card.status == CardStatus.SUSPENDED
        self.processor.activate_card(card.card_id)
        assert card.status == CardStatus.ACTIVE

    def test_cancel_card(self):
        card = self.processor.issue_card(self.payer, "Alice")
        self.processor.cancel_card(card.card_id)
        assert card.status == CardStatus.CANCELLED

    def test_charge_card_updates_balances(self):
        card = self.processor.issue_card(self.payer, "Alice", spending_limit=500.0)
        self.processor.charge_card(card.card_id, self.payer, self.payee, 100.0)
        assert self.payer.balance == 400.0
        assert self.payee.balance == 100.0

    def test_charge_card_over_limit_raises(self):
        card = self.processor.issue_card(self.payer, "Alice", spending_limit=50.0)
        with pytest.raises(ValueError, match="spending limit"):
            self.processor.charge_card(card.card_id, self.payer, self.payee, 100.0)

    def test_charge_suspended_card_raises(self):
        card = self.processor.issue_card(self.payer, "Alice")
        self.processor.suspend_card(card.card_id)
        with pytest.raises(ValueError, match="not active"):
            self.processor.charge_card(card.card_id, self.payer, self.payee, 10.0)

    def test_charge_insufficient_funds_fails(self):
        card = self.processor.issue_card(self.payer, "Alice", spending_limit=10000.0)
        with pytest.raises(ValueError, match="Insufficient funds"):
            self.processor.charge_card(card.card_id, self.payer, self.payee, 9999.0)

    def test_list_cards_for_account(self):
        self.processor.issue_card(self.payer, "Alice")
        self.processor.issue_card(self.payer, "Alice")
        cards = self.processor.list_cards_for_account(self.payer.account_id)
        assert len(cards) == 2

    def test_get_card_not_found_returns_none(self):
        assert self.processor.get_card("nonexistent") is None
