# BuddyAI Earnings Distributor
# Implements the 50/50 earnings split between Buddy and its clients.
#
# Distribution rules:
#   - Autonomous mode: Buddy keeps 50 %, client receives 50 %.
#   - Compute-share mode: client receives 50 % of profits from their
#     computer usage while Buddy (operator) retains the other 50 %.

from typing import Dict, List, Tuple

from .models import Account, Earning, Transaction, TransactionType


# The split ratio applied to all earnings in both modes.
BUDDY_SHARE_RATIO = 0.50
CLIENT_SHARE_RATIO = 0.50


class EarningsDistributor:
    """
    Distributes earnings between Buddy's account and a client's account
    according to the configured 50/50 split.
    """

    def __init__(self, buddy_account: Account) -> None:
        """
        Args:
            buddy_account: The central Buddy account that receives its 50 % share.
        """
        self.buddy_account = buddy_account
        self._earnings: Dict[str, Earning] = {}
        self._distribution_transactions: Dict[str, List[Transaction]] = {}

    # ------------------------------------------------------------------
    # Core distribution
    # ------------------------------------------------------------------

    def distribute(
        self,
        client_account: Account,
        gross_amount: float,
        source: str = "autonomous_task",
        description: str = "",
    ) -> Tuple[Earning, Transaction, Transaction]:
        """
        Split a gross earning 50/50 between Buddy and the client.

        Args:
            client_account: The client's Account that receives its share.
            gross_amount: Total amount to be distributed.
            source: Short label for what generated the earning
                    (e.g. "autonomous_task", "compute_share").
            description: Optional free-text description.

        Returns:
            A tuple of (Earning record, Buddy's Transaction, Client's Transaction).

        Raises:
            ValueError: If gross_amount is not positive.
        """
        if gross_amount <= 0:
            raise ValueError("Gross amount must be greater than zero.")

        buddy_share = round(gross_amount * BUDDY_SHARE_RATIO, 2)
        client_share = round(gross_amount * CLIENT_SHARE_RATIO, 2)

        earning = Earning(
            source=source,
            gross_amount=gross_amount,
            buddy_share=buddy_share,
            client_share=client_share,
            description=description,
        )

        # Credit each account
        self.buddy_account.deposit(buddy_share)
        client_account.deposit(client_share)

        # Record distribution transactions
        buddy_txn = Transaction(
            sender_id="system",
            recipient_id=self.buddy_account.account_id,
            amount=buddy_share,
            transaction_type=TransactionType.EARNING,
            description=f"Buddy 50% share – {source}",
        )
        buddy_txn.complete()

        client_txn = Transaction(
            sender_id="system",
            recipient_id=client_account.account_id,
            amount=client_share,
            transaction_type=TransactionType.EARNING,
            description=f"Client 50% share – {source}",
        )
        client_txn.complete()

        self._earnings[earning.earning_id] = earning
        self._distribution_transactions.setdefault(earning.earning_id, []).extend(
            [buddy_txn, client_txn]
        )

        return earning, buddy_txn, client_txn

    # ------------------------------------------------------------------
    # Compute-share mode (client provides compute, Buddy operates it)
    # ------------------------------------------------------------------

    def distribute_compute_share(
        self,
        client_account: Account,
        compute_profit: float,
        description: str = "",
    ) -> Tuple[Earning, Transaction, Transaction]:
        """
        Distribute profits generated from a client's computer usage.

        The client receives 50 % of the compute profit; Buddy retains 50 %.

        Args:
            client_account: The client account contributing compute resources.
            compute_profit: Total profit generated from compute usage.
            description: Optional description.

        Returns:
            A tuple of (Earning record, Buddy's Transaction, Client's Transaction).
        """
        return self.distribute(
            client_account=client_account,
            gross_amount=compute_profit,
            source="compute_share",
            description=description or "Compute-share earnings distribution",
        )

    # ------------------------------------------------------------------
    # Reporting helpers
    # ------------------------------------------------------------------

    def get_earning(self, earning_id: str) -> Earning:
        """Return a single earning record by ID."""
        earning = self._earnings.get(earning_id)
        if earning is None:
            raise ValueError(f"Earning {earning_id} not found.")
        return earning

    def list_earnings(self) -> List[Earning]:
        """Return all recorded earnings."""
        return list(self._earnings.values())

    def total_buddy_earnings(self) -> float:
        """Return cumulative Buddy share across all earnings."""
        return round(sum(e.buddy_share for e in self._earnings.values()), 2)

    def total_client_earnings(self, client_account_id: str) -> float:
        """Return cumulative client share for a specific client account."""
        total = 0.0
        for earning_id, txns in self._distribution_transactions.items():
            for txn in txns:
                if txn.recipient_id == client_account_id:
                    total += txn.amount
        return round(total, 2)
