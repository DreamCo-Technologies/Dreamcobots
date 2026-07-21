"""Tests for UserMarketplace."""
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))


class TestUserMarketplace(unittest.TestCase):
    """Test cases for UserMarketplace."""

    def setUp(self):
        """Set up test fixtures."""
        from bots.dataforge.user_marketplace import UserMarketplace
        self.marketplace = UserMarketplace()

    def test_user_signup(self):
        """Test that user signup creates correct record."""
        user = self.marketplace.signup_user("u001", "Alice", "alice@example.com")
        self.assertEqual(user["user_id"], "u001")
        self.assertEqual(user["name"], "Alice")
        self.assertFalse(user["contributor"])

    def test_opt_in(self):
        """Test opt-in as contributor."""
        self.marketplace.signup_user("u002", "Bob", "bob@example.com")
        result = self.marketplace.opt_in_contributor("u002")
        self.assertTrue(result["contributor"])

    def test_revenue_share(self):
        """Test revenue share calculation is 70/30."""
        user_share, platform_share = self.marketplace.calculate_revenue_share(1000.0)
        self.assertAlmostEqual(user_share, 700.0)
        self.assertAlmostEqual(platform_share, 300.0)

    def test_dashboard(self):
        """Test that dashboard returns correct user data."""
        self.marketplace.signup_user("u003", "Carol", "carol@example.com")
        dash = self.marketplace.get_dashboard("u003")
        self.assertEqual(dash["user_id"], "u003")
        self.assertEqual(dash["submissions"], 0)

    def test_payout(self):
        """Test payout processing clears pending amount."""
        self.marketplace.signup_user("u004", "Dave", "dave@example.com")
        self.marketplace._payouts["u004"]["pending"] = 350.0
        result = self.marketplace.process_payout("u004")
        self.assertEqual(result["amount_paid"], 350.0)
        self.assertEqual(result["status"], "processed")


if __name__ == "__main__":
    unittest.main()
