import json
import tempfile
import unittest
from pathlib import Path
from buddy.certification.all_bot_goals import build

class AllBotGoalsTests(unittest.TestCase):
    def test_extracts_goals_without_certifying(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/"App_bots").mkdir()
            (root/"App_bots"/"Test.json").write_text(json.dumps({
                "division":"Test","bots":[{"slug":"alpha","displayName":"Alpha",
                "capabilities":["Debug code","Research sources"],
                "benchmarks":[{"label":"Pass rate","target":"90%"}],
                "learningPlan":["Read docs"]}]}))
            report=build(root)
            self.assertEqual(report["bots_scanned"],1)
            self.assertEqual(report["goals_scanned"],2)
            self.assertTrue(all(g["champion_model"] is None for g in report["goals"]))
            self.assertTrue(all(g["status"]=="declared_not_verified" for g in report["goals"]))
    def test_deduplicates_same_bot_slug(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/"App_bots").mkdir()
            payload={"division":"Test","bots":[{"slug":"a","capabilities":["One"]},
                                                {"slug":"a","capabilities":["One"]}]}
            (root/"App_bots"/"Test.json").write_text(json.dumps(payload))
            self.assertEqual(build(root)["goals_scanned"],1)

if __name__=="__main__":
    unittest.main()
