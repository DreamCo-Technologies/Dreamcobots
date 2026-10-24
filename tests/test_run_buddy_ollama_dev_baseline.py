"""Fake local-server contract tests. No model, network, or GPU is used."""
import json
import unittest

from tools.run_buddy_ollama_dev_baseline import BaselineError, loopback_endpoint, run_baseline
from tools.score_buddy_dev_fixtures import PINNED

D = "a" * 64


def catalog():
    return {"schema": "dreamco.buddy_model_benchmarks.v1",
            "suites": [{"id": k, **v} for k, v in PINNED.items()]}


class FakeTransport:
    def __init__(self, *, digest=D, wrong=None):
        self.calls = []
        self.digest = digest
        self.wrong = wrong

    def __call__(self, base, route, payload, timeout):
        self.calls.append((base, route, payload, timeout))
        if route == "/api/tags":
            return {"models": [{"name": "buddy:local", "digest": self.digest}]}
        assert route == "/api/generate"
        prompt = payload["prompt"]
        key = next(k for k, v in PINNED.items() if v["prompt_fixture"] == prompt)
        response = {"instruction_following": "READY", "arithmetic_reasoning": "42",
                    "structured_output": '{"result":42,"confidence":0.5}',
                    "tool_selection": "weather_read_only"}[key]
        if self.wrong == key:
            response = "wrong"
        return {"done": True, "response": response, "eval_count": 12, "eval_duration": 1000000000}


class LocalBaselineTests(unittest.TestCase):
    def test_fake_server_produces_nonpromotable_metrics_without_answers(self):
        fake = FakeTransport()
        clock_values = iter([0, .1, .1, .3, .3, .6, .6, 1.0])
        result = run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(),
                              transport=fake, clock=lambda: next(clock_values))
        self.assertEqual(result["actual_model_api_calls"], 4)
        self.assertEqual(result["passed_public_dev_fixtures"], 4)
        self.assertEqual(result["latency_ms_p95"], 400)
        self.assertEqual(result["server_reported_tokens_per_second_mean"], 12)
        self.assertEqual(result["independent_holdout_receipts"], 0)
        self.assertFalse(result["eligible_for_model_promotion"])
        self.assertFalse(result["model_quality_independently_verified"])
        self.assertNotIn("weather_read_only", json.dumps(result))
        self.assertNotIn("READY", json.dumps(result))
        self.assertEqual(len(fake.calls), 5)

    def test_wrong_answer_not_credited(self):
        result = run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(),
                              transport=FakeTransport(wrong="arithmetic_reasoning"),
                              clock=iter([0, .1, .1, .2, .2, .3, .3, .4]).__next__)
        self.assertEqual(result["passed_public_dev_fixtures"], 3)

    def test_model_digest_mismatch_prevents_generate(self):
        fake = FakeTransport(digest="b" * 64)
        with self.assertRaisesRegex(BaselineError, "digest mismatch"):
            run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), transport=fake)
        self.assertEqual(len(fake.calls), 1)

    def test_invalid_catalog_prevents_network(self):
        fake = FakeTransport()
        bad = catalog()
        bad["suites"][0]["prompt_fixture"] = "changed"
        with self.assertRaisesRegex(ValueError, "fixture changed"):
            run_baseline(model="buddy:local", expected_digest=D, catalog=bad, transport=fake)
        self.assertEqual(fake.calls, [])

    def test_only_loopback_no_redirect_or_credentials(self):
        for url in ("http://example.com:11434", "https://127.0.0.1:11434",
                    "http://localhost:11434", "http://user:pw@127.0.0.1:11434",
                    "http://127.0.0.1:11434@evil.com", "http://127.0.0.1:11434/evil",
                    "http://127.0.0.1:11434?foo=bar", "http://127.0.0.1:0"):
            with self.subTest(url=url), self.assertRaises(BaselineError):
                loopback_endpoint(url)
        self.assertEqual(loopback_endpoint("http://127.0.0.1:11434/"), "http://127.0.0.1:11434")

    def test_incomplete_response_blocks_without_output(self):
        class Incomplete(FakeTransport):
            def __call__(self, base, route, payload, timeout):
                d = super().__call__(base, route, payload, timeout)
                if route == "/api/generate":
                    d["done"] = False
                return d
        with self.assertRaisesRegex(BaselineError, "incomplete"):
            run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), transport=Incomplete())

    def test_timeout_and_model_name_are_bounded(self):
        for timeout in (0, 61, float("nan"), True):
            with self.subTest(timeout=timeout), self.assertRaises(BaselineError):
                run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), timeout_seconds=timeout)
        with self.assertRaisesRegex(BaselineError, "invalid installed model"):
            run_baseline(model="../evil", expected_digest=D, catalog=catalog())

    def test_workflow_registers_test_and_code(self):
        from pathlib import Path
        wf = (Path(__file__).resolve().parents[1] / ".github/workflows/buddy-teacher-coverage-audit.yml").read_text()
        self.assertIn('      - "tools/run_buddy_ollama_dev_baseline.py"', wf)
        self.assertIn('      - "tests/test_run_buddy_ollama_dev_baseline.py"', wf)
        self.assertIn('tests.test_run_buddy_ollama_dev_baseline', wf)


if __name__ == "__main__":
    unittest.main()
