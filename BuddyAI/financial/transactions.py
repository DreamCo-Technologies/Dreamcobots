# BuddyAI Transaction Processor
# Handles financial transfers between accounts, similar to Stripe, PayPal, and Chime.

from typing import Dict, List, Optional

from .models import Account, Transaction, TransactionStatus, TransactionType


class TransactionProcessor:
    """
    Core transaction engine for the BuddyAI financial system.

    Supports:
    - Peer-to-peer transfers between accounts
    - Payments for services
    - Refunds on completed transactions
    - Full transaction history per account
    """

    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {}
        self._transactions: Dict[str, Transaction] = {}

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    def register_account(self, account: Account) -> Account:
        """Register a new account with the processor."""
        if account.account_id in self._accounts:
            raise ValueError(f"Account {account.account_id} is already registered.")
        self._accounts[account.account_id] = account
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        """Retrieve an account by its ID."""
        return self._accounts.get(account_id)

    def list_accounts(self) -> List[Account]:
        """Return all registered accounts."""
        return list(self._accounts.values())

    # ------------------------------------------------------------------
    # Transaction processing
    # ------------------------------------------------------------------

    def transfer(
        self,
        sender_id: str,
        recipient_id: str,
        amount: float,
        description: str = "",
    ) -> Transaction:
        """
        Transfer funds from one account to another.

        Raises:
            ValueError: If either account is not found, the amount is invalid,
                        or the sender has insufficient funds.
        """
        sender = self._get_account_or_raise(sender_id)
        recipient = self._get_account_or_raise(recipient_id)

        if amount <= 0:
            raise ValueError("Transfer amount must be greater than zero.")

        txn = Transaction(
            sender_id=sender_id,
            recipient_id=recipient_id,
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
            description=description,
        )

        return self._execute_transfer(txn, sender, recipient)

    def process_payment(
        self,
        payer_id: str,
        payee_id: str,
        amount: float,
        description: str = "",
    ) -> Transaction:
        """
        Process a service payment from a payer to a payee.

        Works identically to a transfer but is recorded as a PAYMENT type.
        """
        payer = self._get_account_or_raise(payer_id)
        payee = self._get_account_or_raise(payee_id)

        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        txn = Transaction(
            sender_id=payer_id,
            recipient_id=payee_id,
            amount=amount,
            transaction_type=TransactionType.PAYMENT,
            description=description,
        )

        return self._execute_transfer(txn, payer, payee)

    def refund(self, transaction_id: str) -> Transaction:
        """
        Refund a previously completed transaction.

        Raises:
            ValueError: If the transaction is not found or is not in COMPLETED state.
        """
        original = self._transactions.get(transaction_id)
        if original is None:
            raise ValueError(f"Transaction {transaction_id} not found.")
        if original.status != TransactionStatus.COMPLETED:
            raise ValueError(
                f"Only completed transactions can be refunded. "
                f"Current status: {original.status.value}"
            )

        refund_txn = Transaction(
            sender_id=original.recipient_id,
            recipient_id=original.sender_id,
            amount=original.amount,
            transaction_type=TransactionType.REFUND,
            description=f"Refund for transaction {transaction_id}",
        )

        recipient = self._get_account_or_raise(original.sender_id)
        sender = self._get_account_or_raise(original.recipient_id)

        self._execute_transfer(refund_txn, sender, recipient)
        original.status = TransactionStatus.REFUNDED
        return refund_txn

    # ------------------------------------------------------------------
    # History & reporting
    # ------------------------------------------------------------------

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Retrieve a single transaction by its ID."""
        return self._transactions.get(transaction_id)

    def get_account_transactions(self, account_id: str) -> List[Transaction]:
        """Return all transactions where the given account is sender or recipient."""
        self._get_account_or_raise(account_id)
        return [
            txn
            for txn in self._transactions.values()
            if txn.sender_id == account_id or txn.recipient_id == account_id
        ]

    def get_account_balance(self, account_id: str) -> float:
        """Return the current balance for an account."""
        return self._get_account_or_raise(account_id).balance

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _execute_transfer(
        self, txn: Transaction, sender: "Account", recipient: "Account"
    ) -> Transaction:
        """Internal helper: attempt the debit/credit and record the transaction."""
        try:
            sender.withdraw(txn.amount)
            recipient.deposit(txn.amount)
            txn.complete()
        except ValueError:
            txn.fail()
            self._transactions[txn.transaction_id] = txn
            raise
        self._transactions[txn.transaction_id] = txn
        return txn

    def _get_account_or_raise(self, account_id: str) -> Account:
        account = self._accounts.get(account_id)
        if account is None:
            raise ValueError(f"Account {account_id} not found.")
        return account
