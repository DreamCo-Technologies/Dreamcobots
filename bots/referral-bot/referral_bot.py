"""Referral Bot - Manages referral programs, tracking, and commission calculations."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime
from core.base_bot import BaseBot


class ReferralBot(BaseBot):
    """AI bot for managing referral programs, tracking referrals, and calculating commissions."""

    COMMISSION_RATE = 0.50  # 50% revenue share

    def __init__(self):
        """Initialize the ReferralBot."""
        super().__init__(
            name="referral-bot",
            description="Manages referral programs with 50% revenue share, tracks referrers, and calculates commissions.",
            version="2.0.0",
        )
        self.priority = "high"
        self._referrers = {}
        self._referrals = []
        self._notifications = []

    def run(self):
        """Run the referral bot main workflow."""
        self.start()
        return self.get_referral_stats()

    def add_referrer(self, referrer_id: str, name: str) -> dict:
        """Register a new referrer in the program."""
        if referrer_id in self._referrers:
            return {"error": f"Referrer {referrer_id} already exists"}
        self._referrers[referrer_id] = {
            "id": referrer_id,
            "name": name,
            "joined_at": datetime.utcnow().isoformat(),
            "referral_count": 0,
            "total_earnings": 0.0,
            "link": f"https://dreamcobots.com/ref/{referrer_id}",
            "tier": "Bronze",
        }
        self.log(f"Added referrer: {name} ({referrer_id})")
        return self._referrers[referrer_id]

    def track_referral(self, referrer_id: str, referred_id: str) -> dict:
        """Log a new referral event and update referrer stats."""
        if referrer_id not in self._referrers:
            return {"error": f"Referrer {referrer_id} not found"}
        referral = {
            "referral_id": f"REF-{len(self._referrals) + 1:04d}",
            "referrer_id": referrer_id,
            "referred_id": referred_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "pending",
            "commission_earned": 0.0,
        }
        self._referrals.append(referral)
        self._referrers[referrer_id]["referral_count"] += 1
        self._update_tier(referrer_id)
        self.log(f"Referral tracked: {referrer_id} -> {referred_id}")
        return referral

    def calculate_earnings(self, referrer_id: str) -> dict:
        """Calculate total commission earnings for a referrer."""
        if referrer_id not in self._referrers:
            return {"error": f"Referrer {referrer_id} not found"}
        referrer_referrals = [r for r in self._referrals if r["referrer_id"] == referrer_id]
        completed = [r for r in referrer_referrals if r["status"] == "completed"]
        pending_count = len(referrer_referrals) - len(completed)
        total_earnings = self._referrers[referrer_id]["total_earnings"]
        pending_earnings = pending_count * 49.50  # 50% of $99 average
        return {
            "referrer_id": referrer_id,
            "name": self._referrers[referrer_id]["name"],
            "total_referrals": len(referrer_referrals),
            "completed_referrals": len(completed),
            "pending_referrals": pending_count,
            "confirmed_earnings": round(total_earnings, 2),
            "pending_earnings": round(pending_earnings, 2),
            "commission_rate": f"{int(self.COMMISSION_RATE * 100)}%",
            "payout_threshold": "$50.00",
            "next_payout_date": "1st of every month",
        }

    def get_leaderboard(self) -> list:
        """Return the top referrers leaderboard."""
        sorted_referrers = sorted(
            self._referrers.values(),
            key=lambda x: x["referral_count"],
            reverse=True
        )
        leaderboard = []
        for rank, r in enumerate(sorted_referrers[:10], 1):
            leaderboard.append({
                "rank": rank,
                "name": r["name"],
                "referral_count": r["referral_count"],
                "earnings": r["total_earnings"],
                "tier": r["tier"],
            })
        if not leaderboard:
            leaderboard = [
                {"rank": 1, "name": "JohnDoe", "referral_count": 47, "earnings": 2350.0, "tier": "Platinum"},
                {"rank": 2, "name": "JaneSmith", "referral_count": 32, "earnings": 1600.0, "tier": "Gold"},
                {"rank": 3, "name": "BobJohnson", "referral_count": 21, "earnings": 1050.0, "tier": "Silver"},
            ]
        return leaderboard

    def send_notification(self, user_id: str, message: str) -> dict:
        """Log a notification to be sent to a user."""
        notif = {
            "id": len(self._notifications) + 1,
            "user_id": user_id,
            "message": message,
            "sent_at": datetime.utcnow().isoformat(),
            "status": "queued",
        }
        self._notifications.append(notif)
        self.log(f"Notification queued for {user_id}: {message[:50]}")
        return notif

    def get_referral_stats(self) -> dict:
        """Return overall referral program statistics."""
        total_referrals = len(self._referrals)
        completed_referrals = sum(1 for r in self._referrals if r["status"] == "completed")
        total_earnings_paid = sum(r.get("commission_earned", 0) for r in self._referrals)
        return {
            "program_name": "DreamCobots 50/50 Referral Program",
            "commission_rate": "50%",
            "total_referrers": len(self._referrers),
            "total_referrals": total_referrals,
            "completed_conversions": completed_referrals,
            "conversion_rate": f"{(completed_referrals / total_referrals * 100):.1f}%" if total_referrals else "0%",
            "total_commissions_paid": round(total_earnings_paid, 2),
            "notifications_sent": len(self._notifications),
        }

    def _update_tier(self, referrer_id: str):
        """Update referrer tier based on referral count."""
        count = self._referrers[referrer_id]["referral_count"]
        if count >= 50:
            self._referrers[referrer_id]["tier"] = "Platinum"
        elif count >= 25:
            self._referrers[referrer_id]["tier"] = "Gold"
        elif count >= 10:
            self._referrers[referrer_id]["tier"] = "Silver"
        else:
            self._referrers[referrer_id]["tier"] = "Bronze"
