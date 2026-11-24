import unittest

from tools.build_live_revenue_readiness import canonical_bots


class LiveRevenueReadinessCoverageTests(unittest.TestCase):
    def test_readiness_uses_every_generated_bot_profile(self):
        rows = canonical_bots()
        self.assertEqual(len(rows), 1232)
        self.assertEqual(len({slug for slug, _division in rows}), len(rows))
        self.assertTrue(all(slug and division for slug, division in rows))

    def test_readiness_includes_markdown_and_other_non_app_bots(self):
        rows = canonical_bots()
        divisions = {division for _slug, division in rows}
        self.assertIn("DreamAffiliate", divisions)
        self.assertGreater(len(rows), 1051)


if __name__ == "__main__":
    unittest.main()
