import unittest
from buddy.resources.division_resource_router import plan_resource_route

class DivisionResourceRouterTests(unittest.TestCase):
 def test_private_data_never_routes_to_external_provider(self):
  result=plan_resource_route(1,"coding","customer_private",True,True,["openai"])
  self.assertEqual(result["eligible_external_connectors"],[])
  self.assertTrue(result["sensitive_data"])
  self.assertEqual(result["execution_status"],"PLAN_ONLY_NO_PROVIDER_CALL_MADE")
 def test_external_provider_requires_consent_paid_approval_and_implementation(self):
  result=plan_resource_route(1,"reasoning","public",True,True,["openai","anthropic","xai"])
  self.assertEqual(result["eligible_external_connectors"],["openai"])
  self.assertEqual(result["execution_status"],"PLAN_ONLY_NO_PROVIDER_CALL_MADE")
 def test_local_candidate_is_selected_only_when_caller_confirms_availability(self):
  baseline=plan_resource_route(4,"coding","public")
  self.assertEqual(baseline["local_candidate_models"],[])
  candidate=baseline["catalog_candidate_models"][0]
  selected=plan_resource_route(4,"coding","public",available_local_model_ids=[candidate])
  self.assertEqual(selected["local_candidate_models"],[candidate])
  self.assertEqual(selected["eligible_external_connectors"],[])
 def test_unknown_data_classification_fails_closed(self):
  result=plan_resource_route(4,"coding","unclassified",True,True,["openai"])
  self.assertTrue(result["sensitive_data"])
  self.assertEqual(result["eligible_external_connectors"],[])
 def test_mapped_and_unassigned_domain_routes_resolve_without_guessing_owners(self):
  mapped=plan_resource_route(None,"instruction",domain_id="dreamfinance")
  self.assertEqual(mapped["route_type"],"linked_to_masterbot_resource_bundle")
  self.assertEqual(mapped["division_id"],1)
  self.assertEqual(mapped["resource_bundle_id"],"division-resource-001")
  standalone=plan_resource_route(None,"instruction",domain_id="dreamaffiliate")
  self.assertEqual(standalone["route_type"],"standalone_domain_resource_bundle")
  self.assertIsNone(standalone["division_id"])
  self.assertEqual(standalone["resource_bundle_id"],"domain-resource-dreamaffiliate")
 def test_unknown_domain_is_rejected(self):
  with self.assertRaises(KeyError):
   plan_resource_route(None,"instruction",domain_id="madeupdomain")
 def test_unknown_division_is_rejected(self):
  with self.assertRaises(KeyError):
   plan_resource_route(999,"coding")
if __name__=="__main__":unittest.main()
