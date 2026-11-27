import json
import tempfile
import unittest
from pathlib import Path
from scripts.dreamco_model_foundry import MODEL_BLUEPRINTS, build_catalog, build_buyer_foundry_kit, load_divisions
from scripts.train_my_agent import preflight

class ModelFoundryCommercialKitTests(unittest.TestCase):
 def test_catalog_has_195_unique_untrained_skus(self):
  c=build_catalog(); self.assertEqual(c["canonical_division_count"],65); self.assertEqual(c["tier_count"],3); self.assertEqual(c["kit_count"],195)
  skus=[x["sku"] for x in c["kits"]]; self.assertEqual(len(set(skus)),195)
  self.assertTrue(all(x["weights_included"] is False for x in c["kits"]))
  self.assertTrue(all(x["weights_status"]=="UNTRAINED_BLUEPRINT_READY_FOR_TRAINING" for x in c["kits"]))
 def test_canonical_divisions_and_tiers(self):
  self.assertEqual(len(load_divisions()),65); self.assertEqual(set(MODEL_BLUEPRINTS),{"45m-edge","350m-workstation","1b-sovereign"})
 def test_buyer_kit_manifest_and_seal(self):
  with tempfile.TemporaryDirectory() as tmp:
   kit=build_buyer_foundry_kit("45m-edge",load_divisions()[0],Path(tmp)); m=json.loads((kit/"BUYER_MANIFEST.json").read_text())
   self.assertFalse(m["weights_included"]); self.assertEqual(m["weights_status"],"UNTRAINED_BLUEPRINT_READY_FOR_TRAINING"); self.assertEqual(len(m["kit_seal_sha256"]),64)
 def test_launcher_fails_closed_without_rights_or_backend(self):
  with tempfile.TemporaryDirectory() as tmp:
   kit=build_buyer_foundry_kit("45m-edge",load_divisions()[0],Path(tmp)); r=preflight(kit,True)
   self.assertEqual(r["status"],"BLOCKED"); self.assertFalse(r["training_started"]); self.assertFalse(r["paid_compute_requested"]); self.assertTrue(r["blockers"])
if __name__=="__main__": unittest.main()
