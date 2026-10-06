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
        cls.collection = gen.build()
        cls.by_slug = {b["slug"]: b for b in cls.collection["bots"]}

    def test_committed_file_is_current(self):
        self.assertEqual(gen.main(["--check"]), 0)

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

    def test_teammate_lanes_are_bots_with_engines(self):
        lanes = [b for b in self.collection["bots"] if "teammate_lane" in b["flags"]]
        self.assertEqual(len(lanes), 112)
        self.assertTrue(all(b["division"] == "GrokTeammates" and b["engine"] != "unmapped" for b in lanes))
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
        unmapped = [b for b in self.collection["bots"] if b["engine"] == "unmapped"]
        self.assertTrue(unmapped)
        for b in unmapped:
            self.assertIn("engine_unmapped", b["flags"])
            self.assertEqual(b["engine_confidence"], 0.0)

    def test_tier_boilerplate_not_counted_as_capability(self):
        bot = self.by_slug["ad-copy"]
        self.assertGreater(bot["tier_features_dropped"], 0)

    def test_md_only_bots_flagged(self):
        bot = self.by_slug["threejs-core"]
        self.assertIn("md_only", bot["flags"])
        self.assertIn("division_missing", bot["flags"])
        self.assertEqual(bot["division"], "UNASSIGNED")

    def test_seed_division_conflict_flagged(self):
        conflicts = [b for b in self.collection["bots"] if "division_conflict_seed" in b["flags"]]
        self.assertTrue(all(b["seed_division"] != b["division"] for b in conflicts))

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
        app = {json.loads(p.read_text())["division"] for p in gen.APP_BOTS.glob("*.json") if json.loads(p.read_text()).get("bots")}
        self.assertTrue(app <= set(divisions))
        for name in app:
            self.assertTrue(divisions[name]["smoke_bots"], name)
        seeds = gen.seed_division_counts()
        self.assertTrue(seeds)
        for name, count in seeds.items():
            if name in divisions:
                self.assertEqual(divisions[name]["seed_bots"], count)
                self.assertIn("server/seed-bots.ts", divisions[name]["sources"])


if __name__ == "__main__":
    unittest.main()
