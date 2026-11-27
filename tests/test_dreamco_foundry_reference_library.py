import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"config/dreamco-institute-reference-library-100.json"
class FoundryReferenceLibraryTests(unittest.TestCase):
 def test_exactly_100_unique_references_across_ten_tracks(self):
  d=json.loads(CATALOG.read_text(encoding="utf-8")); r=d["resources"]
  self.assertEqual(d["source_count"],100); self.assertEqual(len(r),100)
  self.assertEqual(len({x["id"] for x in r}),100); self.assertEqual(len({x["official_reference"] for x in r}),100)
  self.assertEqual(len(d["categories"]),10)
 def test_unknown_rights_never_imply_training_permission(self):
  d=json.loads(CATALOG.read_text(encoding="utf-8")); self.assertTrue(d["policy"]["resources_are_not_automatically_training_datasets"])
  self.assertTrue(all(x["training_permission"]=="UNKNOWN_BLOCKED" for x in d["resources"]))
  self.assertTrue(all("training" in x["prohibited_until_approved"] for x in d["resources"]))
if __name__=="__main__": unittest.main()
