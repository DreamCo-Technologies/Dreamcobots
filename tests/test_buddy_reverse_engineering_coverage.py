import unittest

from buddy.reverse_engineering_coverage import Feature, audit

def feature(**changes):
    defaults = dict(feature_id="demo", target_kind="web_app",
                    evidence_type="authorized_demo", evidence_ref="fixture-1",
                    rights_verified=True, state="observed", independent_test_ref="")
    defaults.update(changes)
    return Feature(**defaults)

class ReverseEngineeringCoverageTests(unittest.TestCase):
    def test_observation_is_not_verification(self):
        self.assertEqual(audit([feature()])["gaps"], 1)

    def test_verified_requires_independent_test(self):
        self.assertEqual(audit([feature(state="verified")])["verified"], 0)
        self.assertEqual(audit([feature(state="verified", independent_test_ref="ci:fixture-123")])["verified"], 1)

    def test_rights_gate_blocks(self):
        result = audit([feature(rights_verified=False, state="verified", independent_test_ref="ci:fixture-123")])
        self.assertEqual(result["blocked"], 1)
        self.assertEqual(result["verified"], 0)

    def test_duplicate_ids_fail(self):
        with self.assertRaises(ValueError):
            audit([feature(), feature()])

    def test_unknown_kind_fails(self):
        with self.assertRaises(ValueError):
            audit([feature(target_kind="unknown")])

    def test_empty_evidence_is_blocked(self):
        self.assertEqual(audit([feature(evidence_ref="")])["blocked"], 1)

    def test_counts(self):
        result = audit([feature(feature_id="a"),
                        feature(feature_id="b", rights_verified=False),
                        feature(feature_id="c", state="verified", independent_test_ref="ci:ok")])
        self.assertEqual((result["total"], result["verified"], result["blocked"], result["gaps"]),
                         (3, 1, 1, 1))

if __name__ == "__main__":
    unittest.main()
