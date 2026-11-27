import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"config/masterbot-65-registry.json"
class All65LearningDivisionsTests(unittest.TestCase):
 def setUp(self): self.data=json.loads(REGISTRY.read_text(encoding="utf-8"))
 def test_all_65_canonical_divisions_are_learning_divisions(self):
  divisions=self.data["divisions"]
  self.assertEqual(len(divisions),65)
  self.assertTrue(all(d.get("is_learning_division") is True for d in divisions))
  self.assertTrue(all(d.get("learning_contract",{}).get("required") is True for d in divisions))
 def test_every_division_has_complete_learning_lifecycle(self):
  required={"learn","research","teach","build","practice","test","evaluate","remediate","certify","improve"}
  for d in self.data["divisions"]:
   with self.subTest(division=d["name"]):
    c=d["learning_contract"]
    self.assertTrue(required.issubset(set(c["capabilities"])))
    self.assertGreaterEqual(len(c["tracks"]),7)
    self.assertIn("holdout_results",c["evidence_required"])
    self.assertIn("unknown rights block",c["source_policy"])
 def test_shared_resource_categories_do_not_replace_divisions(self):
  p=self.data["learning_division_policy"]
  self.assertTrue(p["all_divisions_are_learning_divisions"])
  self.assertEqual(p["canonical_learning_division_count"],65)
  self.assertIn("not the DreamCo division structure",p["distinction"])
if __name__=="__main__": unittest.main()
