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
 def test_unknown_division_is_rejected(self):
  with self.assertRaises(KeyError):
   plan_resource_route(999,"coding")
if __name__=="__main__":unittest.main()
