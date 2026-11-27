from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import torch

from buddy.modeling.tiny_gpt import (
    ByteTokenizer,
    TinyGPT,
    TinyGPTConfig,
    run_baseline,
    write_baseline_report,
)


class TinyGPTBaselineTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(1234)

    def test_byte_tokenizer_round_trips_unicode(self):
        tokenizer = ByteTokenizer()
        text = "Buddy — café 🤖"
        self.assertEqual(tokenizer.decode(tokenizer.encode(text)), text)
        self.assertEqual(tokenizer.vocab_size, 256)

    def test_byte_tokenizer_rejects_out_of_range_ids(self):
        with self.assertRaises(ValueError):
            ByteTokenizer().decode([256])

    def test_config_rejects_incompatible_attention_dimensions(self):
        with self.assertRaises(ValueError):
            TinyGPTConfig(n_embd=30, n_head=4).validate()

    def test_model_returns_expected_logits_and_loss(self):
        config = TinyGPTConfig(block_size=8, n_layer=1, n_head=2, n_embd=16)
        model = TinyGPT(config).eval()
        input_ids = torch.randint(0, 256, (2, 8), dtype=torch.long)
        logits, loss = model(input_ids, input_ids)
        self.assertEqual(tuple(logits.shape), (2, 8, 256))
        self.assertTrue(torch.isfinite(loss))

    def test_future_tokens_do_not_change_prior_logits(self):
        config = TinyGPTConfig(block_size=8, n_layer=2, n_head=2, n_embd=16)
        torch.manual_seed(7)
        model = TinyGPT(config).eval()
        first = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]], dtype=torch.long)
        changed_future = torch.tensor([[1, 2, 3, 4, 90, 91, 92, 93]], dtype=torch.long)
        with torch.no_grad():
            logits_a, _ = model(first)
            logits_b, _ = model(changed_future)
        torch.testing.assert_close(logits_a[:, :4], logits_b[:, :4], rtol=0, atol=1e-6)

    def test_backward_produces_finite_gradients_without_updating_weights(self):
        config = TinyGPTConfig(block_size=8, n_layer=1, n_head=2, n_embd=16)
        model = TinyGPT(config)
        before = {name: value.detach().clone() for name, value in model.state_dict().items()}
        inputs = torch.randint(0, 256, (2, 8), dtype=torch.long)
        _, loss = model(inputs, inputs)
        loss.backward()
        self.assertTrue(all(
            parameter.grad is not None and torch.isfinite(parameter.grad).all()
            for parameter in model.parameters()
        ))
        for name, value in model.state_dict().items():
            torch.testing.assert_close(value, before[name], rtol=0, atol=0)

    def test_baseline_report_is_repeatable_and_never_trains(self):
        config = TinyGPTConfig(block_size=8, n_layer=1, n_head=2, n_embd=16)
        first = run_baseline(seed=99, config=config)
        second = run_baseline(seed=99, config=config)
        self.assertEqual(first["report_sha256"], second["report_sha256"])
        self.assertEqual(first["evaluation"]["initial_loss"], second["evaluation"]["initial_loss"])
        self.assertFalse(first["training_performed"])
        self.assertFalse(first["weights_updated"])
        self.assertFalse(first["checkpoint_written"])
        self.assertFalse(first["network_accessed"])
        self.assertFalse(first["paid_compute_used"])

    def test_report_writer_emits_json_only(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "baseline.json"
            report = write_baseline_report(
                output,
                seed=5,
                config=TinyGPTConfig(block_size=8, n_layer=1, n_head=2, n_embd=16),
            )
            stored = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(stored["report_sha256"], report["report_sha256"])
            self.assertFalse(list(Path(temp).glob("*.pt")))
            self.assertFalse(list(Path(temp).glob("*.safetensors")))


if __name__ == "__main__":
    unittest.main()
