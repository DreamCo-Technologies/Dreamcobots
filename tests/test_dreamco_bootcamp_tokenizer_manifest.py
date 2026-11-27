import json
import shutil
import tempfile
import unittest
from pathlib import Path

from buddy.learning.byte_bpe_trainer import train_from_manifest
from tools.build_dreamco_bootcamp_tokenizer_manifest import (
    AUTHORIZATION,
    MANIFEST,
    SOURCE,
    build_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


class DreamCoBootcampTokenizerManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in (SOURCE, AUTHORIZATION):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

    def tearDown(self):
        self.temp.cleanup()

    def test_builds_tokenizer_only_manifest_from_train_split(self):
        report = build_manifest(self.root)
        manifest_path = self.root / MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        corpus_path = self.root / manifest["corpora"][0]["path"]
        rows = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(report["status"], "TOKENIZER_ONLY_CORPUS_READY")
        source_rows = [
            json.loads(line)
            for line in (self.root / SOURCE).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        authorization = json.loads((self.root / AUTHORIZATION).read_text(encoding="utf-8"))
        self.assertTrue(all(row["authoring"]["status"] == "DRAFT_REQUIRES_HUMAN_REVIEW" for row in source_rows))
        self.assertTrue(all(row["authoring"]["training_permission"] == "NOT_GRANTED" for row in source_rows))
        self.assertEqual(authorization["scope"], "tokenizer_training_only")
        self.assertFalse(authorization["allow_model_weight_training"])
        self.assertFalse(authorization["allow_distillation"])
        self.assertEqual(report["source_split_counts"], {"train": 10, "validation": 2, "test": 2})
        self.assertEqual(report["training_rows_used"], 10)
        self.assertEqual(report["validation_rows_excluded"], 2)
        self.assertEqual(report["test_rows_excluded"], 2)
        self.assertTrue(all(row["split"] == "train" for row in rows))
        self.assertEqual(len(rows), 10)
        self.assertFalse(manifest["neural_model_weight_training_allowed"])
        self.assertFalse(manifest["production_training_allowed"])
        self.assertEqual(manifest["training_scope"], "tokenizer_only")
        self.assertEqual(manifest["corpora"][0]["source_type"], "first_party")

        tokenizer = train_from_manifest(manifest, root=self.root, vocab_size=512)
        self.assertTrue(tokenizer["training_executed"])
        self.assertTrue(tokenizer["rights_gate_passed"])
        self.assertFalse(tokenizer["model_weight_training_executed"])
        self.assertFalse(tokenizer["holdout_used_for_training"])
        self.assertEqual(tokenizer["training_provenance"][0]["source_type"], "first_party")

    def test_refuses_owner_authorization_for_model_weights_or_third_party_content(self):
        auth_path = self.root / AUTHORIZATION
        auth = json.loads(auth_path.read_text(encoding="utf-8"))
        auth["allow_model_weight_training"] = True
        auth_path.write_text(json.dumps(auth), encoding="utf-8")
        with self.assertRaisesRegex(PermissionError, "allow_model_weight_training"):
            build_manifest(self.root)

    def test_refuses_external_text_even_with_owner_tokenizer_authorization(self):
        source_path = self.root / SOURCE
        rows = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines()]
        rows[0]["source"]["external_text_included"] = True
        source_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(PermissionError, "external text"):
            build_manifest(self.root)


if __name__ == "__main__":
    unittest.main()
