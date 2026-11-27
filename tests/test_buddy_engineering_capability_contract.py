import unittest
from tools.validate_buddy_engineering_capabilities import validate

class BuddyEngineeringCapabilityContractTests(unittest.TestCase):
    def test_all_four_capabilities_are_defined(self):
        result = validate()
        self.assertTrue(result["valid"])
        self.assertEqual(set(result["capabilities"]), {
            "vibe_coding", "reverse_engineering", "model_distillation", "model_weight_training",
            "physical_product_design", "hardware_software_prototyping", "three_dimensional_invention", "startup_creation"
        })

    def test_contract_does_not_claim_runtime_is_operational(self):
        self.assertFalse(validate()["operational_claim"])

if __name__ == "__main__":
    unittest.main()
