#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from foundry.weight_balancer import assign_tokens, mix_routes, RouteSpec, simulate  # noqa: E402
from tools.run_weight_balancer import main  # noqa: E402


class WeightBalancerTest(unittest.TestCase):
    def test_capacity_prevents_collapse_to_one_expert(self):
        affinities = [[1.0, 0.1], [1.0, 0.1], [1.0, 0.2], [0.2, 1.0]]
        result = assign_tokens(affinities, top_k=1, capacity_factor=1.0)
        self.assertEqual(result["experts"], 2)
        self.assertLess(max(result["load"]), 4)

    def test_route_mix_prefers_us_when_quality_holds(self):
        mix = mix_routes(
            [
                RouteSpec("grok", 0.95, 1.0, True),
                RouteSpec("other", 0.71, 0.5, False),
            ],
            quality_floor=0.7,
        )
        self.assertGreater(mix["us_share"], 0.4)

    def test_no_route_below_the_quality_floor_is_selected(self):
        for routes in ([], [RouteSpec("low", 0.1, 0.01, True)]):
            result = mix_routes(routes, quality_floor=0.7)
            self.assertEqual(result["mix"], [])
            self.assertEqual(result["us_share"], 0)

    def test_preference_changes_odds_without_changing_quality(self):
        routes = [RouteSpec("owned", 0.8, 1, True), RouteSpec("other", 0.8, 1, False)]
        neutral = mix_routes(routes, 0.7, us_preference=1)
        preferred = mix_routes(routes, 0.7)
        self.assertEqual(neutral["us_share"], 0.5)
        self.assertAlmostEqual(preferred["mix"][0]["weight"] / preferred["mix"][1]["weight"], 1.25)
        self.assertTrue(all(row["quality"] == 0.8 for row in preferred["mix"]))

    def test_report_writes(self):
        self.assertTrue(simulate()["balance"]["experts"] >= 8)
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
