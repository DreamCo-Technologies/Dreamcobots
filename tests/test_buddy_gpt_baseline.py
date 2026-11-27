import json
import math
import tempfile
import unittest
from pathlib import Path

from buddy.gpt_baseline import ByteTokenizer, TinyGPT, TinyGPTConfig, sequence_cross_entropy
from tools.run_buddy_gpt_baseline import build_evidence, load_config

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/buddy-tiny-gpt-baseline.json"


class TinyGPTBaselineTests(unittest.TestCase):
    def test_utf8_byte_tokenizer_round_trips_unicode(self):
        tokenizer = ByteTokenizer()
        text = "Buddy GPT 🚀 — Wisconsin"
        self.assertEqual(tokenizer.decode(tokenizer.encode(text)), text)
        self.assertEqual(tokenizer.vocab_size, 256)

    def test_forward_shapes_and_finite_logits(self):
        model = TinyGPT(TinyGPTConfig(context_size=8, width=8, seed=7))
        logits = model.forward([97, 98, 99, 100])
        self.assertEqual(len(logits), 4)
        self.assertTrue(all(len(row) == 256 for row in logits))
        self.assertTrue(all(math.isfinite(value) for row in logits for value in row))
        self.assertGreater(model.parameter_count, 0)

    def test_future_tokens_do_not_change_past_logits(self):
        model = TinyGPT(TinyGPTConfig(context_size=8, width=8, seed=19))
        left = model.forward([10, 20, 30, 40])
        right = model.forward([10, 20, 99, 88])
        for position in (0, 1):
            for a, b in zip(left[position], right[position]):
                self.assertAlmostEqual(a, b, places=12)

    def test_initialization_is_deterministic_and_seed_sensitive(self):
        first = TinyGPT(TinyGPTConfig(seed=123))
        repeated = TinyGPT(TinyGPTConfig(seed=123))
        changed = TinyGPT(TinyGPTConfig(seed=124))
        self.assertEqual(first.fingerprint(), repeated.fingerprint())
        self.assertNotEqual(first.fingerprint(), changed.fingerprint())

    def test_sequence_loss_is_finite_and_does_not_update_weights(self):
        model = TinyGPT(TinyGPTConfig(seed=33))
        before = model.fingerprint()
        loss = sequence_cross_entropy(model, [97, 98, 97, 98, 97])
        self.assertTrue(math.isfinite(loss))
        self.assertGreater(loss, 0)
        self.assertEqual(model.fingerprint(), before)

    def test_report_is_synthetic_only_and_explicitly_untrained(self):
        report, card = build_evidence(CONFIG, commit_sha="test-commit")
        self.assertEqual(report["status"], "BASELINE_MEASURED_UNTRAINED")
        self.assertFalse(report["training"]["weights_trained"])
        self.assertEqual(report["training"]["weight_updates"], 0)
        self.assertFalse(report["training"]["checkpoint_created"])
        self.assertFalse(report["data_rights"]["external_data_used"])
        self.assertEqual(set(report["fixtures"]), {"train", "validation", "test"})
        self.assertTrue(all(row["used_for_training"] is False for row in report["fixtures"].values()))
        self.assertEqual(card["status"], "UNTRAINED_REFERENCE_IMPLEMENTATION")
        self.assertEqual(report["run"]["commit_sha"], "test-commit")

    def test_config_rejects_training_enablement_and_duplicate_splits(self):
        config = load_config(CONFIG)
        self.assertFalse(config["training_policy"]["enabled"])
        with tempfile.TemporaryDirectory() as temp:
            bad = dict(config)
            bad["training_policy"] = dict(config["training_policy"], enabled=True)
            path = Path(temp) / "bad.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)
            bad = dict(config)
            bad["synthetic_fixtures"] = dict(config["synthetic_fixtures"], test=config["synthetic_fixtures"]["validation"])
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)

    def test_invalid_context_and_token_ids_fail_closed(self):
        model = TinyGPT(TinyGPTConfig(context_size=4))
        with self.assertRaises(ValueError):
            model.forward([1, 2, 3, 4, 5])
        with self.assertRaises(ValueError):
            model.forward([256])
        with self.assertRaises(ValueError):
            sequence_cross_entropy(model, [1])


if __name__ == "__main__":
    unittest.main()
