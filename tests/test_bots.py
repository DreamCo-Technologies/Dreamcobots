"""
Tests for all Dreamcobots bots.

Conflict resolution notes:
- PR #10 tests were written for an older API.  This version has been updated
  to match the current bot implementations from PR #13 and PR #55/56.

Run:
    python -m pytest tests/test_bots.py
"""

import sys
import os
import unittest

# ---------------------------------------------------------------------------
# Path setup so bots can be imported without installation
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "bots", "government-contract-grant-bot"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "bots", "referral-bot"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "bots", "hustle-bot"))
sys.path.insert(0, os.path.join(_REPO_ROOT, "bots", "ai-models-integration"))

from government_contract_grant_bot import GovernmentContractGrantBot
from referral_bot import ReferralBot
from hustle_bot import HustleBot


# ===========================================================================
# Government Contract & Grant Bot
# ===========================================================================

class TestGovernmentContractGrantBot(unittest.TestCase):

    def setUp(self):
        self.bot = GovernmentContractGrantBot()

    def test_start_does_not_raise(self):
        self.bot.start()  # should not raise

    def test_search_contracts_returns_dict(self):
        result = self.bot.search_contracts(query="technology")
        self.assertIsInstance(result, dict)

    def test_check_grant_eligibility_returns_dict(self):
        result = self.bot.check_grant_eligibility({"name": "Test Org", "employees": 10})
        self.assertIsInstance(result, dict)

    def test_run_returns_dict(self):
        result = self.bot.run()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_process_contracts_does_not_raise(self):
        self.bot.process_contracts()  # should not raise

    def test_process_grants_does_not_raise(self):
        self.bot.process_grants()  # should not raise


# ===========================================================================
# Referral Bot
# ===========================================================================

class TestReferralBot(unittest.TestCase):

    def setUp(self):
        self.bot = ReferralBot()

    def test_run_returns_stats(self):
        result = self.bot.run()
        self.assertIsNotNone(result)

    def test_add_referrer_creates_entry(self):
        result = self.bot.add_referrer("user1", "Alice")
        self.assertEqual(result["id"], "user1")
        self.assertEqual(result["name"], "Alice")

    def test_add_referrer_duplicate_returns_error(self):
        self.bot.add_referrer("user2", "Bob")
        result = self.bot.add_referrer("user2", "Bob")
        self.assertIn("error", result)

    def test_track_referral_logs_event(self):
        self.bot.add_referrer("ref1", "Referrer")
        result = self.bot.track_referral("ref1", "new_user")
        self.assertIsInstance(result, dict)

    def test_get_referral_stats_returns_dict(self):
        stats = self.bot.get_referral_stats()
        self.assertIsInstance(stats, dict)

    def test_calculate_earnings_returns_dict(self):
        self.bot.add_referrer("earn1", "Earner")
        result = self.bot.calculate_earnings("earn1")
        self.assertIsInstance(result, dict)

    def test_get_leaderboard_returns_list(self):
        result = self.bot.get_leaderboard()
        self.assertIsInstance(result, list)

    def test_commission_rate_constant(self):
        self.assertEqual(ReferralBot.COMMISSION_RATE, 0.50)


# ===========================================================================
# Hustle Bot
# ===========================================================================

class TestHustleBot(unittest.TestCase):

    def setUp(self):
        self.bot = HustleBot()

    def test_run_returns_summary(self):
        result = self.bot.run()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_set_goal_returns_goal_entry(self):
        result = self.bot.set_goal("Reach $5k MRR", 5000.0)
        self.assertIn("goal", result)
        self.assertEqual(result["target_revenue"], 5000.0)

    def test_track_progress_returns_dict(self):
        self.bot.set_goal("Test Goal", 1000.0)
        result = self.bot.track_progress()
        self.assertIsInstance(result, dict)

    def test_suggest_tasks_returns_list(self):
        result = self.bot.suggest_tasks()
        self.assertIsInstance(result, list)

    def test_log_milestone_returns_entry(self):
        result = self.bot.log_milestone("Hit $1k revenue")
        self.assertIsInstance(result, dict)

    def test_generate_daily_summary_returns_dict(self):
        result = self.bot.generate_daily_summary()
        self.assertIsInstance(result, dict)

    def test_optimize_revenue_streams_returns_dict(self):
        result = self.bot.optimize_revenue_streams()
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
