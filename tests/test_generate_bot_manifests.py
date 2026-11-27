"""Tests for tools/generate_bot_manifests.py."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import generate_bot_manifests as gen  # noqa: E402


class GeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Tests must not regenerate tracked files: downstream prospectuses index
        # these outputs, so generation belongs in the explicit workflow step.
        cls.collection = gen.build()
        cls.by_slug = {b["slug"]: b for b in cls.collection["bots"]}

    def test_committed_file_is_current(self):
        self.assertEqual(
            gen.OUT.read_text(encoding="utf-8"),
            gen.render(self.collection),
        )
        self.assertEqual(
            gen.DIV_OUT.read_text(encoding="utf-8"),
            gen.render_divisions(self.collection),
        )

    def test_deterministic(self):
        self.assertEqual(gen.render(gen.build()), gen.render(self.collection))
        self.assertNotIn("generated_at", gen.render(self.collection))

    def test_covers_every_markdown_and_app_bot(self):
        md = {p.stem.lower() for p in (ROOT / "bots").glob("*.md")}
        app = set()
        for path in (ROOT / "App_bots").glob("*.json"):
            app |= {b["slug"] for b in json.loads(path.read_text())["bots"]}
        lanes = {lane["slug"] for lane in json.loads((ROOT / "config/bots/teammate-lanes.json").read_text())["lanes"]}
        self.assertEqual(set(self.by_slug), md | app | lanes)

    def test_teammate_lanes_route_to_canonical_owners_and_keep_shared_masterbots(self):
        lanes = [b for b in self.collection["bots"] if "teammate_lane" in b["flags"]]
        self.assertEqual(len(lanes), 112)
        self.assertTrue(all(b["source_division"] == "GrokTeammates" and b["division"] == "GrokTeammates" and b["engine"] != "unmapped" for b in lanes))
        self.assertTrue(all(b["primary_domain_owner"] in gen.load_route_metadata()["domain_names"] for b in lanes))
        self.assertTrue(all(b["shared_workforce_group"] == "GrokTeammates" for b in lanes))
        self.assertTrue(all(b["primary_masterbot_id"] in range(1, 46) for b in lanes))
        self.assertTrue(all(b["shared_teammate_masterbot_id"] in range(46, 66) for b in lanes))
        lanes_text = (ROOT / "config/bots/teammate-lanes.json").read_text()
        self.assertNotRegex(lanes_text, r'"(agent_?id|id|internal_id)"')

    def test_engine_fallbacks_are_flagged(self):
        for b in self.collection["bots"]:
            if "engine_fallback_workflow" in b["flags"]:
                self.assertEqual((b["engine"], b["engine_confidence"]), ("workflow", 0.0))
            if "engine_weak_signal" in b["flags"]:
                self.assertIn("engine_low_confidence", b["flags"])

    def test_run_policy_blocks_money_and_delete(self):
        self.assertEqual(self.by_slug["stripe-billing"]["run"], "blocked_money")
        self.assertEqual(self.by_slug["ach-processor"]["run"], "blocked_money")
        self.assertEqual(self.by_slug["ad-copy"]["run"], "allowed")
        self.assertEqual(gen.run_policy("purge old records", "workflow"), "blocked_destructive")
        self.assertEqual(gen.run_policy("anything", "unmapped"), "spec_only")
        for b in self.collection["bots"]:
            if b["engine"] == "unmapped":
                self.assertEqual(b["run"], "spec_only")

    def test_unmapped_bots_are_flagged_not_faked(self):
        # The production catalog currently maps every source profile. Keep the
        # unmapped contract covered with a synthetic no-signal profile rather
        # than requiring an intentionally broken production bot to exist.
        metadata = gen.load_route_metadata()
        entry = {
            "app": {
                "name": "No Signal Profile",
                "division": "CommandCore",
                "description": "Unclassified sample profile.",
                "capabilities": [],
            },
            "md": None,
            "lane": None,
            "flags": set(),
            "sources": ["synthetic:no-signal"],
        }
        bot = gen.build_manifest(
            "no-signal-profile",
            entry,
            {},
            set(metadata["division_names"]),
            metadata,
        )
        self.assertEqual(bot["engine"], "unmapped")
        self.assertIn("engine_unmapped", bot["flags"])
        self.assertEqual(bot["engine_confidence"], 0.0)
        self.assertEqual(bot["run"], "spec_only")

    def test_tier_boilerplate_not_counted_as_capability(self):
        bot = self.by_slug["ad-copy"]
        self.assertGreater(bot["tier_features_dropped"], 0)

    def test_ten_supplemental_domains_keep_proposed_owners_but_no_primary_owner(self):
        supplemental = [b for b in self.collection["bots"] if "supplemental_domain_unassigned_pending_owner_review" in b["flags"]]
        self.assertEqual(len(supplemental), 50)
        self.assertEqual(len({b["division"] for b in supplemental}), 10)
        for bot in supplemental:
            self.assertIsNone(bot["primary_domain_owner"])
            self.assertIsNone(bot["primary_masterbot_id"])
            self.assertIn(bot["proposed_domain_owner"], gen.load_route_metadata()["domain_names"])
            self.assertIn(bot["proposed_primary_masterbot_id"], range(1, 46))

    def test_threejs_markdown_specs_are_specialized_and_owned_by_dreamcodelab(self):
        bot = self.by_slug["threejs-core"]
        self.assertNotIn("md_only", bot["flags"])
        self.assertEqual(bot["source_division"], "Dream3D")
        self.assertEqual(bot["division"], "Dream3D")
        self.assertEqual(bot["primary_domain_owner"], "DreamCodeLab")
        self.assertEqual(bot["supplemental_portfolio"], "Dream3D")
        self.assertEqual(bot["specialist_capability_domain"], "interactive_web_3d_and_real_time_rendering")
        self.assertGreaterEqual(bot["caps"], 5)

    def test_seed_division_conflict_flagged(self):
        conflicts = [b for b in self.collection["bots"] if "division_conflict_seed" in b["flags"]]
        self.assertTrue(all(b["seed_division"] != b["source_division"] for b in conflicts))

    def test_live_action_bots_capped_at_plan_only(self):
        bot = self.by_slug["ach-processor"]
        self.assertTrue(bot["live"])
        self.assertEqual(bot["ceiling"], "plan_only")

    def test_engine_scoring_threshold(self):
        self.assertEqual(gen.pick_engine({"drafting": 1.0, "analysis": 0.5, "classification": 0, "workflow": 0}), ("unmapped", 0.0))
        self.assertEqual(gen.pick_engine({"drafting": 3.0, "analysis": 3.0, "classification": 0, "workflow": 0})[0], "analysis")

    def test_check_detects_drift(self):
        tmp = ROOT / "tmp" / "manifest-drift.json"
        tmp.parent.mkdir(exist_ok=True)
        tmp.write_text("{}\n")
        try:
            self.assertEqual(gen.main(["--check", "--out", str(tmp)]), 1)
        finally:
            tmp.unlink()

    def test_division_manifests_written_and_checked(self):
        text = gen.render_divisions(self.collection)
        committed = gen.DIV_OUT.read_text(encoding="utf-8")
        self.assertEqual(committed, text)
        divisions = {d["name"]: d for d in json.loads(text)["divisions"]}
        expected_divisions = set(gen.load_route_metadata()["division_names"])
        self.assertEqual(set(divisions), expected_divisions)
        self.assertEqual(len(divisions), 57)
        for name in expected_divisions:
            self.assertTrue(divisions[name]["smoke_bots"], name)
        charters = json.loads(gen.SUPPLEMENTAL_CHARTERS.read_text())
        for portfolio in charters["portfolios"]:
            name = portfolio["portfolio"]
            self.assertIn(f"App_bots/{name}.json", divisions[name]["sources"])
            if portfolio.get("classification") == "supplemental_domain_profile":
                self.assertIsNone(divisions[name]["primary_domain_owner"])
                self.assertEqual(divisions[name]["proposed_domain_owner"], portfolio["owner"])
            else:
                self.assertEqual(divisions[name]["primary_domain_owner"], portfolio["owner"])
        self.assertEqual(divisions["GrokTeammates"]["bots"], 112)
        seeds = gen.seed_division_counts()
        self.assertTrue(seeds)
        for name, count in seeds.items():
            if name in divisions:
                self.assertEqual(divisions[name]["seed_bots"], count)
                self.assertIn("server/seed-bots.ts", divisions[name]["sources"])


if __name__ == "__main__":
    unittest.main()
