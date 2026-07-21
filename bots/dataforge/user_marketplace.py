"""User Marketplace: allows users to contribute and monetize their data."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

REVENUE_SPLIT_USER = 0.70
REVENUE_SPLIT_PLATFORM = 0.30


class UserMarketplace:
    """Marketplace for users to contribute data and earn revenue shares."""

    def __init__(self):
        """Initialize the UserMarketplace with empty user, contribution, and payout stores."""
        self._users: dict = {}
        self._contributions: dict = {}
        self._payouts: dict = {}

    def signup_user(self, user_id: str, name: str, email: str) -> dict:
        """Register a new user in the marketplace.

        Args:
            user_id: Unique identifier for the user.
            name: Full name of the user.
            email: Email address of the user.

        Returns:
            The user record dict.
        """
        self._users[user_id] = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "contributor": False,
            "consent_given": True,
            "joined_at": datetime.utcnow().isoformat(),
        }
        self._contributions[user_id] = []
        self._payouts[user_id] = {"total_earned": 0.0, "pending": 0.0, "paid": 0.0, "history": []}
        logger.info("User signed up: %s (%s)", name, user_id)
        return self._users[user_id]

    def opt_in_contributor(self, user_id: str) -> dict:
        """Opt a user in as a data contributor for revenue sharing.

        Args:
            user_id: The user to opt in.

        Returns:
            Dict with user_id and contributor status.

        Raises:
            ValueError: If user_id is not found.
        """
        if user_id not in self._users:
            raise ValueError(f"User {user_id} not found.")
        self._users[user_id]["contributor"] = True
        self._users[user_id]["opted_in_at"] = datetime.utcnow().isoformat()
        logger.info("User %s opted in as contributor.", user_id)
        return {"user_id": user_id, "contributor": True}

    def submit_data(self, user_id: str, data: dict) -> dict:
        """Accept a data submission from a contributing user.

        Args:
            user_id: The contributing user's identifier.
            data: The data dict to submit.

        Returns:
            The submission record dict.

        Raises:
            ValueError: If user_id is not found.
            PermissionError: If user has not opted in as contributor.
        """
        if user_id not in self._users:
            raise ValueError(f"User {user_id} not found.")
        if not self._users[user_id].get("contributor"):
            raise PermissionError(f"User {user_id} has not opted in as a contributor.")
        submission = {
            "submission_id": str(uuid.uuid4()),
            "user_id": user_id,
            "data": data,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "pending_review",
        }
        self._contributions[user_id].append(submission)
        logger.info("Data submitted by user %s, submission %s", user_id, submission["submission_id"])
        return submission

    def calculate_revenue_share(self, sale_amount: float) -> tuple:
        """Calculate user and platform revenue shares for a sale.

        Args:
            sale_amount: Total sale amount in USD.

        Returns:
            Tuple of (user_share, platform_share) as floats.
        """
        user_share = round(sale_amount * REVENUE_SPLIT_USER, 2)
        platform_share = round(sale_amount * REVENUE_SPLIT_PLATFORM, 2)
        logger.info("Revenue split: user=%.2f platform=%.2f", user_share, platform_share)
        return user_share, platform_share

    def get_dashboard(self, user_id: str) -> dict:
        """Get contribution and earnings dashboard for a user.

        Args:
            user_id: The user identifier.

        Returns:
            Dashboard dict with submissions count and earnings summary.

        Raises:
            ValueError: If user_id is not found.
        """
        if user_id not in self._users:
            raise ValueError(f"User {user_id} not found.")
        contributions = self._contributions.get(user_id, [])
        payouts = self._payouts.get(user_id, {})
        return {
            "user_id": user_id,
            "name": self._users[user_id]["name"],
            "contributor": self._users[user_id].get("contributor", False),
            "submissions": len(contributions),
            "total_earned": payouts.get("total_earned", 0.0),
            "pending_payout": payouts.get("pending", 0.0),
            "total_paid": payouts.get("paid", 0.0),
        }

    def process_payout(self, user_id: str) -> dict:
        """Process pending payout for a user.

        Args:
            user_id: The user to process payout for.

        Returns:
            Dict with user_id, amount_paid, and status.

        Raises:
            ValueError: If user_id is not found.
        """
        if user_id not in self._users:
            raise ValueError(f"User {user_id} not found.")
        payout = self._payouts[user_id]
        amount = payout["pending"]
        payout["paid"] += amount
        payout["pending"] = 0.0
        payout["history"].append({
            "amount": amount,
            "processed_at": datetime.utcnow().isoformat(),
        })
        logger.info("Payout processed for user %s: $%.2f", user_id, amount)
        return {"user_id": user_id, "amount_paid": amount, "status": "processed"}
