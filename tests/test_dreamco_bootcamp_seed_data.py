import json
import tempfile
import unittest
import sys
from unittest.mock import patch
from pathlib import Path

from tools.build_dreamco_bootcamp_seed_data import build_candidate, build_dataset_card, load_jsonl
from buddy.datasets.hub import DatasetHub, DatasetPolicyError, main as build_main


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
        self.assertEqual(manifest["data_plane"], "candidate_pending_ownership_and_rights_review")
        self.assertFalse(manifest["training_approved"])
        self.assertFalse(manifest["training_started"])
        self.assertEqual(len(manifest["candidate_sha256"]), 64)
        self.assertIn("\n", rows[0]["text"])
        card = build_dataset_card(manifest, "candidate.jsonl")
        self.assertFalse(card["training_approved"])
        self.assertEqual(card["rights_status"], "PENDING_HUMAN_REVIEW")
        self.assertEqual(card["primary_masterbot_id"], 4)

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

    def test_rejects_holdout_scope_and_incomplete_source_provenance(self):
        data = examples()
        data[0]["target_scope"] = "evaluation_only_holdout"
        with self.assertRaisesRegex(ValueError, "target scopes"):
            build_candidate(data, 4, registry())
        data = examples()
        del data[0]["source"]["source_version"]
        with self.assertRaisesRegex(ValueError, "complete source provenance"):
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

    def test_cli_writes_parseable_manifest_and_card_json(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "candidate.jsonl"
            manifest = root / "manifest.json"
            card = root / "card.json"
            with patch("sys.argv", ["builder", "--masterbot-id", "1", "--out", str(output),
                                   "--manifest-out", str(manifest), "--card-out", str(card)]):
                self.assertEqual(build_main(), 0)
            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
            card_data = json.loads(card.read_text(encoding="utf-8"))
            self.assertFalse(manifest_data["training_started"])
            self.assertFalse(card_data["training_approved"])
            self.assertTrue(manifest.read_bytes().endswith(bytes([10])))
            self.assertTrue(card.read_bytes().endswith(bytes([10])))

    def test_candidate_generation_is_reproducible_and_covers_all_65_lanes(self):
        data = examples()
        hashes = set()
        for masterbot_id in range(1, 66):
            first_rows, first_manifest = build_candidate(data, masterbot_id, registry())
            second_rows, second_manifest = build_candidate(data, masterbot_id, registry())
            self.assertEqual(first_manifest["candidate_sha256"], second_manifest["candidate_sha256"])
            self.assertEqual(first_rows, second_rows)
            self.assertEqual(first_manifest["primary_masterbot_id"], masterbot_id)
            hashes.add(first_manifest["candidate_sha256"])
        self.assertEqual(len(hashes), 65)

    def test_rejects_duplicate_prompt_response_content(self):
        data = examples()
        data[1]["prompt"] = data[0]["prompt"]
        data[1]["response"] = data[0]["response"]
        with self.assertRaisesRegex(ValueError, "duplicate prompt/response"):
            build_candidate(data, 4, registry())

    def test_pending_card_registers_metadata_without_ingesting_training_data(self):
        rows, manifest = build_candidate(examples(), 4, registry())
        card = build_dataset_card(manifest, "candidate.jsonl")
        with tempfile.TemporaryDirectory() as temp:
            hub = DatasetHub(home=temp)
            registered = hub.register(card)
            self.assertEqual(registered["training_status"], "NOT_APPROVED")
            self.assertFalse(registered["training_approved"])
            self.assertIsNone(registered["object_path"])
            self.assertIsNone(registered["content_sha256"])
            self.assertEqual(list((Path(temp) / "objects").iterdir()), [])

    def test_pending_card_cannot_ingest_candidate_file(self):
        rows, manifest = build_candidate(examples(), 4, registry())
        card = build_dataset_card(manifest, "candidate.jsonl")
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "candidate.jsonl"
            source.write_text("".join(json.dumps(row) + "\\n" for row in rows), encoding="utf-8")
            hub = DatasetHub(home=Path(temp) / "hub")
            with self.assertRaisesRegex(DatasetPolicyError, "disabled until an operator"):
                hub.register(card, source_file=source)
            self.assertEqual(list((Path(temp) / "hub" / "objects").iterdir()), [])

    def test_jsonl_loader_rejects_invalid_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "examples.jsonl"
            path.write_text('{"valid": true}\n[]\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be an object"):
                load_jsonl(path)


if __name__ == "__main__":
    unittest.main()
