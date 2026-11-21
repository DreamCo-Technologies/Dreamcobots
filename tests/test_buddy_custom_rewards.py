import unittest
from tools.buddy_custom_rewards import Ledger, Rules

class RewardsTests(unittest.TestCase):
    def test_awards_only_verified_and_deduplicates(self):
        ledger = Ledger(Rules("student"))
        with self.assertRaises(ValueError):
            ledger.award("x", passed=True, improved=False, verified=False)
        self.assertEqual(ledger.award("x", passed=True, improved=True, verified=True), 15)
        self.assertEqual(ledger.award("x", passed=True, improved=True, verified=True), 0)

    def test_cap_and_redemption(self):
        ledger = Ledger(Rules("student", points_per_pass=70, daily_cap=100, rewards={"Badge": 90}))
        self.assertEqual(ledger.award("a", passed=True, improved=False, verified=True, day="2026-10-21"), 70)
        self.assertEqual(ledger.award("b", passed=True, improved=False, verified=True, day="2026-10-21"), 30)
        self.assertEqual(ledger.redeem("c", "Badge"), 90)
        self.assertEqual(ledger.balance, 10)

    def test_no_negative_balance(self):
        ledger = Ledger(Rules("student"))
        with self.assertRaises(ValueError):
            ledger.redeem("r", "Study badge")

    def test_invalid_rules(self):
        with self.assertRaises(ValueError):
            Rules("student", points_per_pass=-5)
        with self.assertRaises(ValueError):
            Rules("student", rewards={"Cash": 0})

if __name__ == "__main__":
    unittest.main()
