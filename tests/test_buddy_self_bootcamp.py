import unittest
from tools.build_buddy_self_bootcamp import build, division_names

class SelfBootcampTests(unittest.TestCase):
    def test_parser_requires_exactly_55_complete_division_profiles(self):
        source="\\n".join(
            f"  Division{i}: {{\\n    purpose: 'purpose',\\n    focusAreas: [],\\n    serves: [],\\n    outcome: 'outcome',\\n    boundary: 'boundary',\\n  }}"
            for i in range(55)
        )
        self.assertEqual(len(division_names(source)),55)
        with self.assertRaises(ValueError):
            division_names(source.replace("  Division54:", "  Missing54:").replace("    boundary: 'boundary',", "    boundary: 'boundary',", 1))

    def test_builds_all_division_paths_and_preserves_truth_boundary(self):
        names=[f"Division{i}" for i in range(55)]
        workforce={"training_paths":[{"id":"sales"}]}
        government={"official_sources":[{"id":"onet"}]}
        result=build(names,{"subject_terms":["audio","vision"]},{"inventory":{"occupations":2,"task_statements":8}},
          {"counts":{"discovered":12,"guide_authoring_eligible":1,"rights_pending":11}},workforce,government)
        self.assertEqual(result["coverage"]["domain_divisions"],55)
        self.assertEqual(len(result["divisions"]),55)
        self.assertEqual(result["coverage"]["onet_task_statements"],8)
        self.assertIn("not proof",result["truth_boundary"])
        self.assertTrue(result["buddy_bootcamp_builder_loop"]["steps"])

if __name__=="__main__": unittest.main()
