"""Regression coverage for fail-closed model routing with untrusted registry rows."""
import math
import unittest

from benchmarks.model_competition.route import connect_account, register, route


class ModelRouteIntegrityTests(unittest.TestCase):
    def test_existing_route_contract(self):
        models = [
            register("slow", "frontier", "code", 0.9, 0.2, "owner", False),
            register("fast", "open-source", "code", 0.9, 0.8, "user", True),
        ]
        accounts = [connect_account("frontier", True)]
        self.assertEqual(route("code", models, accounts=accounts)["model"], "fast")
        self.assertIsNone(route("code", [models[0]])["model"])
        self.assertFalse(accounts[0]["secret_stored"])
        self.assertFalse(route("code", models, accounts=accounts)["guessed"])
        self.assertEqual(route("code", models, free_only=True)["model"], "fast")
        self.assertIsNone(route("legal", models)["model"])

    def test_invalid_registered_scores_rejected(self):
        for score in (math.nan, math.inf, -math.inf, -1, 1.01, True, "0.9"):
            with self.subTest(score=score):
                with self.assertRaises(ValueError):
                    register("bad", "open-source", "code", score, 0.2, "owner", True)

    def test_malformed_or_out_of_range_rows_do_not_route(self):
        good = register("safe", "open-source", "code", 0.7, 0.5, "owner", True)
        bad = [
            {**good, "name": "invalid", "quality": math.nan},
            {**good, "name": "invalid", "quality": 1.5},
            {**good, "name": "invalid", "quality": "1"},
            {**good, "name": "invalid", "efficiency": math.inf},
            {**good, "name": "invalid", "quality": True},
            {**good, "name": "invalid", "source": "bogus"},
            {**good, "name": "invalid", "approved_by": "stranger"},
            {**good, "name": "invalid", "task": "other"},
            {"name": "broken"},
            None,
        ]
        self.assertEqual(route("code", bad + [good])["model"], "safe")
        self.assertIsNone(route("code", bad)["model"])

    def test_malformed_accounts_cannot_unlock_paid_route(self):
        paid = register("paid", "frontier", "code", 0.9, 0.4, "owner", False)
        for accounts in (
            [None],
            [{"connected": True, "paid": True}],
            [{"provider": "frontier", "connected": True, "paid": "yes"}],
        ):
            with self.subTest(accounts=accounts):
                self.assertIsNone(route("code", [paid], accounts=accounts)["model"])

    def test_paid_model_cannot_borrow_unrelated_provider_connection(self):
        paid = register("premium", "frontier", "code", 0.99, 0.9, "owner", False)
        forged = {**paid, "provider": "open-source"}
        accounts = [connect_account("open-source", True)]
        self.assertIsNone(route("code", [forged], accounts=accounts)["model"])

    def test_provider_mismatch_does_not_outscore_valid_free_model(self):
        paid = register("premium", "frontier", "code", 0.99, 0.9, "owner", False)
        forged = {**paid, "provider": "open-source"}
        free = register("free", "open-source", "code", 0.7, 0.6, "user", True)
        self.assertEqual(route("code", [forged, free], accounts=[connect_account("open-source", True)])["model"], "free")

    def test_legitimate_paid_provider_connection_still_routes(self):
        paid = register("premium", "frontier", "code", 0.99, 0.9, "owner", False)
        self.assertEqual(route("code", [paid], accounts=[connect_account("frontier", True)])["model"], "premium")



if __name__ == "__main__":
    unittest.main()
