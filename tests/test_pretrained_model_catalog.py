import unittest
from tools.validate_pretrained_model_catalog import validate

class PretrainedModelCatalogTests(unittest.TestCase):
    def base(self):
        return {"schema":"dreamco.pretrained_model_marketplace.v1",
                "policy":{"parameter_count_limit":None,"source_data_included":False},
                "models":[]}

    def test_empty_catalog_is_valid_and_unbounded(self):
        self.assertEqual(validate(self.base()), [])

    def test_sale_listing_requires_full_evidence(self):
        c=self.base()
        c["models"]=[{"model_id":"test-1","parameter_count":45_000_000,"status":"approved_for_sale"}]
        errors=validate(c)
        self.assertTrue(any("sale listing missing" in e for e in errors))

    def test_unbounded_parameter_policy_is_enforced(self):
        c=self.base()
        c["policy"]["parameter_count_limit"]=45_000_000
        self.assertTrue(any("must remain null" in e for e in validate(c)))

    def test_source_data_never_included(self):
        c=self.base()
        c["policy"]["source_data_included"]=True
        self.assertTrue(any("source datasets must never" in e for e in validate(c)))

    def test_duplicate_model_ids_rejected(self):
        c=self.base()
        c["models"]=[{"model_id":"same","parameter_count":1},{"model_id":"same","parameter_count":2}]
        self.assertTrue(any("unique" in e for e in validate(c)))

if __name__ == "__main__":
    unittest.main()
