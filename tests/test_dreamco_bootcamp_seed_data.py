import json
import tempfile
import unittest
from pathlib import Path

from tools.build_dreamco_bootcamp_seed_data import build_candidate, load_jsonl


def registry():
    return {"divisions": [{"id": i, "name": f"Division{i}"} for i in range(1, 66)]}


def examples():
    result = []
    for index in range(13):
        result.append({
            "example_id": f"lesson-{index:02d}",
            "module_id": f"module-{index:02d}",
            "split": "train" if index < 9 else "validation" if index < 11 else "test",
            "prompt": f"Explain the verified engineering concept number {index} in detail.",
            "response": f"This original lesson explains concept {index}, its constraints, validation approach, and evidence requirements.",
            "rubric": ["Explains the concept correctly", "Identifies its validation requirements"],
            "tags": ["engineering", f"module-{index}"],
            "source": {"kind": "dreamco_original_authored_draft", "source_id": "test", "source_version": "1.0.0", "external_text_included": False},
            "authoring": {"status": "DRAFT_REQUIRES_HUMAN_REVIEW", "owner_claim": "PENDING_ASSIGNMENT_REVIEW", "training_permission": "NOT_GRANTED"},
            "target_scope": "shared_foundation_candidate",
        })
    return result


class BootcampSeedDataTests(unittest.TestCase):
    def test_builds_isolated_candidate_for_requested_masterbot(self):
        rows, manifest = build_candidate(examples(), 4, registry())
        self.assertEqual(len(rows), 13)
        self.assertTrue(all(row["masterbot_id"] == 4 for row in rows))
        self.assertEqual(manifest["split_counts"], {"train": 9, "validation": 2, "test": 2})
        self.assertEqual(manifest["rights_status"], "PENDING_HUMAN_REVIEW")
        self.assertFalse(manifest["training_approved"])
        self.assertFalse(manifest["training_started"])
        self.assertEqual(len(manifest["candidate_sha256"]), 64)

    def test_rejects_duplicate_ids_and_missing_splits(self):
        data = examples()
        data[1]["example_id"] = data[0]["example_id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            build_candidate(data, 4, registry())
        data = examples()
        data[-1]["split"] = "train"
        data[-2]["split"] = "train"
        with self.assertRaisesRegex(ValueError, "non-empty"):
            build_candidate(data, 4, registry())

    def test_rejects_unknown_masterbot_and_rights_claims(self):
        with self.assertRaisesRegex(ValueError, "canonical"):
            build_candidate(examples(), 66, registry())
        data = examples()
        data[0]["authoring"]["training_permission"] = "ALLOWED"
        with self.assertRaisesRegex(ValueError, "pending human review"):
            build_candidate(data, 4, registry())

    def test_rejects_pii_and_external_text(self):
        data = examples()
        data[0]["response"] += " Contact person@example.com."
        with self.assertRaisesRegex(ValueError, "PII or secret"):
            build_candidate(data, 4, registry())
        data = examples()
        data[0]["source"]["external_text_included"] = True
        with self.assertRaisesRegex(ValueError, "external text"):
            build_candidate(data, 4, registry())

    def test_jsonl_loader_rejects_invalid_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "examples.jsonl"
            path.write_text('{"valid": true}\n[]\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be an object"):
                load_jsonl(path)


if __name__ == "__main__":
    unittest.main()
