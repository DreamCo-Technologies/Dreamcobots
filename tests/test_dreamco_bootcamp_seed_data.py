import json
import os
import tempfile
import unittest
import sys
from unittest.mock import patch
from pathlib import Path

from tools.build_dreamco_bootcamp_seed_data import build_candidate, build_dataset_card, load_jsonl, main as build_main
from buddy.datasets.hub import DatasetHub, DatasetPolicyError
from buddy.datasets.training_jobs import create_training_job
from buddy.datasets.ingestion_worker import create_ingestion_job, execute_ingestion_job


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
        self.assertIn("\n", rows[0]["text"])
        card = build_dataset_card(manifest, "candidate.jsonl")
        self.assertFalse(card["training_approved"])
        self.assertEqual(card["rights_status"], "PENDING_HUMAN_REVIEW")
        self.assertEqual(card["license_url_status"], "INTERNAL_POLICY_REFERENCE_NOT_A_PUBLIC_LICENSE")
        self.assertEqual(card["license"], "DREAMCO_INTERNAL_OWNED")
        self.assertEqual(card["source"], "dreamco_authored")
        self.assertEqual(card["source_id"], "dreamco.bootcamp.core.v1")
        self.assertFalse(card["ai_training_allowed"])
        self.assertFalse(card["content_rights_verified"])
        self.assertFalse(card["owner_assignment_verified"])
        self.assertFalse(card["contributor_rights_verified"])
        self.assertEqual(card["owner_approval_id"], "")
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
            self.assertEqual(first_manifest["example_count"], 14)
            hashes.add(first_manifest["candidate_sha256"])
        self.assertEqual(len(hashes), 65)

    def test_rejects_duplicate_prompt_response_content(self):
        data = examples()
        data[1]["prompt"] = data[0]["prompt"]
        data[1]["response"] = data[0]["response"]
        with self.assertRaisesRegex(ValueError, "duplicate prompt/response"):
            build_candidate(data, 4, registry())

    def test_pending_seed_candidate_cannot_be_ingested_or_trained(self):
        with tempfile.TemporaryDirectory() as temp:
            rows, manifest = build_candidate(examples(), 4, registry())
            card = build_dataset_card(manifest, "candidate.jsonl")
            hub = DatasetHub(Path(temp) / "hub")
            hub.register(card)
            with self.assertRaisesRegex(DatasetPolicyError, "not approved for training"):
                create_training_job(hub, manifest["dataset_id"], 4, "example/model", "a" * 40)
            candidate = Path(temp) / "candidate.jsonl"
            candidate.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(DatasetPolicyError, "File ingestion is disabled"):
                hub.register(card, source_file=candidate)

    def test_reviewed_seed_candidate_ingests_with_matching_split_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            rows, manifest = build_candidate(examples(), 4, registry())
            candidate = Path(temp) / "candidate.jsonl"
            candidate.write_text(
                "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )
            card = build_dataset_card(manifest, str(candidate))
            card.update({
                "rights_status": "VERIFIED",
                "rights_evidence": "owner-review-fixture-001",
                "training_approved": True,
                "ai_training_allowed": True,
                "content_rights_verified": True,
                "owner_assignment_verified": True,
                "contributor_rights_verified": True,
                "owner_approval_id": "OWNER-APPROVAL-FIXTURE-001",
                "privacy_review": "PASSED",
            })
            hub = DatasetHub(Path(temp) / "hub")
            job = create_ingestion_job(card, candidate, "INGESTION-APPROVAL-FIXTURE", Path(temp) / "jobs")
            with patch.dict(os.environ, {"DREAMCO_ALLOW_DATASET_INGESTION": "1"}, clear=True):
                result = execute_ingestion_job(job["manifest_path"], "INGESTION-APPROVAL-FIXTURE", hub=hub)
            self.assertEqual(result["status"], "INGESTED_PENDING_BENCHMARK")
            self.assertEqual(result["split_manifest"], manifest["split_manifest"])
            self.assertEqual(result["rows_validated"], len(rows))
            self.assertFalse(result["training_started"])

    def test_jsonl_loader_rejects_invalid_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "examples.jsonl"
            path.write_text('{"valid": true}\n[]\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "must be an object"):
                load_jsonl(path)


if __name__ == "__main__":
    unittest.main()
