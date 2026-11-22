from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from buddy.gpt_baseline import ByteTokenizer, DataPreparationError, prepare_synthetic_splits
from tools.prepare_buddy_synthetic_splits import build_artifacts

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/buddy-gpt-day2-synthetic-data.json"
SOURCE = {
    "source_kind": "synthetic",
    "source_ref": "urn:dreamco:synthetic:test-fixture:v1",
    "rights_status": "SYNTHETIC_ONLY",
    "contains_personal_data": False,
}


def records(count: int = 12):
    return [
        {"id": f"example-{index:03d}", "text": f"Synthetic tokenizer example number {index}.", "provenance": dict(SOURCE)}
        for index in range(count)
    ]


class BuddyGPTDataPipelineTests(unittest.TestCase):
    def test_config_builds_reproducible_synthetic_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            first = build_artifacts(CONFIG, Path(temp) / "first", "test-commit")
            second = build_artifacts(CONFIG, Path(temp) / "second", "test-commit")
            self.assertEqual(first["split_hashes"], second["split_hashes"])
            self.assertEqual(first["split_ids"], second["split_ids"])
            self.assertEqual(first["split_counts"], {"train": 10, "validation": 1, "test": 1})
            for name in ("train", "validation", "test"):
                self.assertTrue((Path(temp) / "first" / f"{name}.jsonl").is_file())

    def test_deduplicates_before_splitting_and_prevents_content_leakage(self):
        rows = records()
        rows.append({"id": "duplicate-001", "text": rows[0]["text"], "provenance": dict(SOURCE)})
        result = prepare_synthetic_splits(rows, seed=7)
        manifest = result["manifest"]
        self.assertEqual(manifest["quality"]["input_rows"], 13)
        self.assertEqual(manifest["quality"]["unique_rows"], 12)
        self.assertEqual(manifest["quality"]["duplicate_rows_removed_before_split"], 1)
        content_sets = [{row["content_sha256"] for row in split} for split in result["splits"].values()]
        self.assertFalse(content_sets[0] & content_sets[1])
        self.assertFalse(content_sets[0] & content_sets[2])
        self.assertFalse(content_sets[1] & content_sets[2])

    def test_split_assignment_and_hashes_are_seed_deterministic(self):
        first = prepare_synthetic_splits(records(), seed=20261122)["manifest"]
        second = prepare_synthetic_splits(records(), seed=20261122)["manifest"]
        self.assertEqual(first["split_ids"], second["split_ids"])
        self.assertEqual(first["split_hashes"], second["split_hashes"])

    def test_unicode_nfc_dedup_and_utf8_byte_accounting(self):
        rows = records(4)
        rows[0]["text"] = "Cafe\u0301"
        rows[1]["text"] = "Caf\u00e9"
        result = prepare_synthetic_splits(rows, seed=11)
        manifest = result["manifest"]
        self.assertEqual(manifest["quality"]["unique_rows"], 3)
        tokenizer = ByteTokenizer()
        all_rows = [row for split in result["splits"].values() for row in split]
        self.assertTrue(all(tokenizer.decode(tokenizer.encode(row["text"])) == row["text"] for row in all_rows))
        self.assertEqual(manifest["tokenizer"]["token_count_total"], manifest["tokenizer"]["byte_count_total"])

    def test_external_source_is_rejected(self):
        row = records(3)
        row[0]["provenance"]["source_kind"] = "huggingface"
        with self.assertRaises(DataPreparationError):
            prepare_synthetic_splits(row, seed=1)

    def test_unknown_rights_are_rejected(self):
        row = records(3)
        row[0]["provenance"]["rights_status"] = "UNKNOWN"
        with self.assertRaises(DataPreparationError):
            prepare_synthetic_splits(row, seed=1)

    def test_personal_data_is_rejected(self):
        row = records(3)
        row[0]["provenance"]["contains_personal_data"] = True
        with self.assertRaises(DataPreparationError):
            prepare_synthetic_splits(row, seed=1)

    def test_duplicate_ids_and_empty_text_are_rejected(self):
        row = records(3)
        row[1]["id"] = row[0]["id"]
        with self.assertRaises(DataPreparationError):
            prepare_synthetic_splits(row, seed=1)
        row = records(3)
        row[0]["text"] = "  \n "
        with self.assertRaises(DataPreparationError):
            prepare_synthetic_splits(row, seed=1)

    def test_requires_three_unique_examples_and_valid_ratios(self):
        with self.assertRaises(DataPreparationError):
            prepare_synthetic_splits(records(2), seed=1)
        with self.assertRaises(DataPreparationError):
            prepare_synthetic_splits(records(3), seed=1, train_ratio=0.7, validation_ratio=0.2, test_ratio=0.2)

    def test_manifest_does_not_authorize_training_or_include_raw_text(self):
        result = prepare_synthetic_splits(records(), seed=9)
        manifest = result["manifest"]
        self.assertFalse(manifest["training_authorized"])
        self.assertEqual(manifest["training_execution"], "NOT_RUN")
        self.assertFalse(manifest["weights_updated"])
        self.assertFalse(manifest["checkpoint_created"])
        self.assertFalse(manifest["external_data_used"])
        serialized = json.dumps(manifest)
        self.assertNotIn("Synthetic tokenizer example", serialized)


if __name__ == "__main__":
    unittest.main()
