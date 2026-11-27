import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from buddy.fleet_runtime.semantic_router import route_candidates,_catalog

class BuddySemanticRouterTests(unittest.TestCase):
 def test_catalog_preserves_canonical_business_and_legacy_sources(self):
  kinds={x["source_kind"] for x in _catalog()}
  self.assertEqual(kinds,{"canonical_fleet","commercial_business_microbot","legacy_original_bot_or_system"})
  self.assertEqual(sum(x["source_kind"]=="commercial_business_microbot" for x in _catalog()),55)
  self.assertEqual(sum(x["source_kind"]=="legacy_original_bot_or_system" for x in _catalog()),212)
 def test_business_specialist_routing_is_candidate_only(self):
  result=route_candidates("pricing elasticity margin optimization",top_k=5)
  self.assertTrue(result["candidates"])
  self.assertTrue(any(x["bot_id"]=="BUSINESS_BOT_06" for x in result["candidates"]))
  self.assertFalse(result["execution_started"])
  self.assertFalse(result["permissions_granted"])
  self.assertTrue(all(x["weights_loaded"] is False for x in result["candidates"]))
 def test_invalid_limits_rejected(self):
  with self.assertRaises(ValueError): route_candidates("pricing",0)
  with self.assertRaises(ValueError): route_candidates("x",11)
  with self.assertRaises(ValueError): route_candidates("x","5")
if __name__=="__main__": unittest.main()
