import unittest

from tools.build_dreamco_training_examples import build


def event(n, owner=41):
    return {
        "event_id": f"event-{n}",
        "source_url": f"https://github.com/DreamCo-Technologies/Dreamcobots/commit/{n:040d}",
        "evidence_type": "verified_test",
        "verified": True,
        "human_reviewed": True,
        "training_allowed": True,
        "rights_status": "VERIFIED",
        "contains_secrets": False,
        "contains_personal_data": False,
        "third_party_content_included": False,
        "primary_masterbot_id": owner,
        "task": f"Implement capability number {n} with dependency-aware routing",
        "verified_lesson": "The verified implementation validates inputs, records evidence, and retests the capability.",
        "acceptance_criteria": ["the route is deterministic", "the evidence is reproducible"],
        "test_evidence": ["unit test passed", "held-out regression passed"],
    }


class DreamCoOriginalTrainingExamplesTests(unittest.TestCase):
    def test_verified_work_becomes_original_split_examples(self):
        result = build([event(1), event(2), event(3)])
        self.assertEqual(len(result["rows"]), 3)
        self.assertEqual({row["split"] for row in result["rows"]}, {"train", "validation", "test"})
        self.assertFalse(result["training_approved"])
        self.assertFalse(result["weights_trained"])
        self.assertTrue(all(row["derivation"] == "original_synthesis_from_verified_DreamCo_work" for row in result["rows"]))
        self.assertEqual(set(result["split_manifest"]), {"train", "validation", "test", "all_rows_sha256"})
        self.assertTrue(all(len(row["example_id"]) == 64 for row in result["rows"]))

    def test_unverified_or_unlicensed_records_are_rejected(self):
        bad = event(1)
        bad["training_allowed"] = False
        result = build([event(2), event(3), event(4), bad])
        self.assertEqual(len(result["rows"]), 3)
        self.assertEqual(len(result["rejected_source_events"]), 1)

    def test_mixed_masterbot_ownership_is_rejected(self):
        with self.assertRaises(ValueError):
            build([event(1, 41), event(2, 42), event(3, 43)])

    def test_personal_data_is_rejected(self):
        bad = event(1)
        bad["task"] = "Send a message to person@example.com"
        with self.assertRaises(ValueError):
            build([bad, event(2), event(3)])

    def test_wrong_masterbot_is_rejected(self):
        with self.assertRaises(ValueError):
            build([event(1, 999), event(2), event(3)])

    def test_duplicate_event_ids_are_rejected(self):
        duplicate = event(1)
        duplicate["source_url"] = "https://github.com/DreamCo-Technologies/Dreamcobots/commit/other"
        with self.assertRaises(ValueError):
            build([event(1), duplicate, event(2), event(3)])

    def test_duplicate_content_is_rejected_even_with_different_ids(self):
        duplicate = event(2)
        duplicate["event_id"] = "event-duplicate"
        duplicate["source_url"] = "https://github.com/DreamCo-Technologies/Dreamcobots/commit/duplicate"
        with self.assertRaises(ValueError):
            build([event(1), event(2), duplicate, event(3)])

    def test_secret_patterns_are_rejected(self):
        bad = event(1)
        bad["verified_lesson"] = "The implementation used token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 safely."
        with self.assertRaises(ValueError):
            build([bad, event(2), event(3)])

    def test_acceptance_criteria_must_be_an_array(self):
        bad = event(1)
        bad["acceptance_criteria"] = "not a list"
        with self.assertRaises(ValueError):
            build([bad, event(2), event(3)])

    def test_non_https_source_is_rejected(self):
        bad = event(1)
        bad["source_url"] = "http://github.com/example"
        with self.assertRaises(ValueError):
            build([bad, event(2), event(3)])


if __name__ == "__main__":
    unittest.main()
