import unittest

from tools.build_division_45m_model_blueprints import ARCHITECTURE, build, count_parameters


class DivisionModelBlueprintTests(unittest.TestCase):
    def test_reference_architecture_is_near_45_million_parameters(self):
        count = count_parameters(ARCHITECTURE)
        self.assertEqual(count, 45038208)
        self.assertLess(abs(count - 45000000), 100000)

    def test_builds_one_design_only_blueprint_for_each_division(self):
        registry = {"divisions": [{"id": i, "name": f"Division{i}"} for i in range(1, 66)]}
        result = build(registry, b'{"registry":"fixture"}')
        self.assertEqual(result["division_count"], 65)
        self.assertEqual(result["trained_model_count"], 0)
        self.assertEqual(result["actual_parameter_count"], 45038208)
        self.assertTrue(all(row["training_status"] == "design_only_not_trained" for row in result["blueprints"]))
        self.assertTrue(all(row["training_approved"] is False for row in result["blueprints"]))
        self.assertTrue(all(row["weights_sha256"] is None for row in result["blueprints"]))

    def test_rejects_incomplete_or_duplicate_registry(self):
        with self.assertRaises(ValueError):
            build({"divisions": [{"id": 1, "name": "OnlyOne"}]}, b"{}")
        duplicates = [{"id": i, "name": f"D{i}"} for i in range(1, 65)] + [{"id": 64, "name": "Duplicate"}]
        with self.assertRaises(ValueError):
            build({"divisions": duplicates}, b"{}")


if __name__ == "__main__":
    unittest.main()
