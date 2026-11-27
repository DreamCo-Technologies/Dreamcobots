import unittest
from tools.validate_buddy_connection_setup_guides import validate

class ConnectionSetupGuideTests(unittest.TestCase):
    def setUp(self):
        self.catalog={"schema":"dreamco.buddy.connection_setup_catalog.v1","connections":[{"id":"local","auth":"local_runtime","secret_ref":None},{"id":"api","auth":"api_key","secret_ref":"API_TOKEN"}]}
        base={
            "beginner_explanation":"Plain-language description.",
            "setup_steps":["step one","step two","step three","step four","step five"],
            "permission_review":{"credential_values_in_chat":False,"browser_storage_for_secrets":False},
            "credential_handling":{"required":False,"secret_reference":None},
            "cost_review":{"status":"verify_current_provider_pricing_before_enablement"},
            "local_or_low_cost_alternative":"A local alternative.",
            "health_check":{"status":"not_run_by_catalog","evidence_fields":["checked_at"]},
            "disconnect_and_recovery":["revoke","remove","record"],
            "official_setup_url":"https://example.org",
            "current_provider_terms_review":"required_before_enablement",
            "status":"guide_template_ready_live_connection_unverified"
        }
        self.guides={"schema":"dreamco.buddy.connection_setup_guides.v1","global_policy":{"no_password_or_raw_secret_collection_in_chat":True,"default_access":"read_only_or_mock"},"profiles":[dict(base,connection_id="local"),dict(base,connection_id="api",credential_handling={"required":True,"secret_reference":"API_TOKEN"})]}

    def test_one_guide_per_catalog_entry(self):
        self.assertEqual(validate(self.catalog,self.guides),[])

    def test_missing_connection_profile_is_detected(self):
        self.guides["profiles"].pop()
        self.assertTrue(any("catalog/profile mismatch" in error for error in validate(self.catalog,self.guides)))

    def test_unsafe_raw_secret_collection_is_rejected(self):
        self.guides["profiles"][0]["permission_review"]["credential_values_in_chat"]=True
        self.assertTrue(any("unsafe credential handling" in error for error in validate(self.catalog,self.guides)))

    def test_catalog_cannot_claim_health_check_or_live_connection(self):
        self.guides["profiles"][0]["health_check"]["status"]="passed"
        self.assertTrue(any("health check ran" in error for error in validate(self.catalog,self.guides)))

    def test_secret_required_profile_needs_reference(self):
        self.guides["profiles"][1]["credential_handling"]["secret_reference"]=None
        self.assertTrue(any("required secret reference missing" in error for error in validate(self.catalog,self.guides)))

if __name__=="__main__": unittest.main()
