"""Regression tests for Buddy Flash training data integrity and tiny CPU forward pass.

Run: python -m unittest discover -s tests -p test_buddy_flash_smoke.py
"""
import json
import tempfile
import unittest
from pathlib import Path

from tools.buddy_flash_train import TinyBuddy, encoded, load_records


def record(source, split, prompt="Question?", completion="Answer"):
    return {
        "prompt": prompt, "completion": completion, "domain": "research",
        "source_id": source, "split": split, "provenance": "synthetic original",
        "license": "owner_created", "consent": True,
    }


def read_rows(rows):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "rows.jsonl"
        p.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
        return load_records(p)


class FlashSmokeTests(unittest.TestCase):
    def test_valid_splits(self):
        self.assertEqual(len(read_rows([record("a", "train"), record("b", "holdout", "Other?", "Yes")])), 2)

    def test_source_leakage_rejected(self):
        with self.assertRaises(ValueError):
            read_rows([record("same", "train"), record("same", "holdout", "Other?", "Yes")])

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            read_rows([record("a", "train"), record("b", "holdout")])

    def test_missing_consent_rejected(self):
        with self.assertRaises(ValueError):
            read_rows([record("a", "train", "A?", "A"), dict(record("b", "holdout", "B?", "B"), consent=False)])

    def test_unapproved_license_rejected(self):
        with self.assertRaises(ValueError):
            read_rows([record("a", "train", "A?", "A"), dict(record("b", "holdout", "B?", "B"), license="unknown")])

    def test_context_overflow_rejected(self):
        with self.assertRaises(ValueError):
            encoded(record("a", "train", "x" * 200), 64)

    def test_forward_shape(self):
        import torch
        model = TinyBuddy(width=16, layers=1, heads=4, context=64)
        logits = model(torch.tensor([[1, 4, 5]], dtype=torch.long))
        self.assertEqual(tuple(logits.shape), (1, 3, 259))


if __name__ == "__main__":
    unittest.main()
