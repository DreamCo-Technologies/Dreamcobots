"""Fake local-server contract tests. No model, network, or GPU is used."""
import json
import tempfile
import unittest

from tools.run_buddy_ollama_dev_baseline import BaselineError, _parse_server_json, loopback_endpoint, run_baseline, write_receipt_exclusive
from tools.score_buddy_dev_fixtures import PINNED

D = "a" * 64


def catalog():
    return {"schema": "dreamco.buddy_model_benchmarks.v1",
            "suites": [{"id": k, **v} for k, v in PINNED.items()]}


class FakeTransport:
    def __init__(self, *, digest=D, wrong=None, response_model="buddy:local", post_run_digest=None):
        self.calls = []
        self.digest = digest
        self.wrong = wrong
        self.response_model = response_model
        self.post_run_digest = post_run_digest
        self.tag_calls = 0

    def __call__(self, base, route, payload, timeout):
        self.calls.append((base, route, payload, timeout))
        if route == "/api/tags":
            self.tag_calls += 1
            digest = self.post_run_digest if self.tag_calls > 1 and self.post_run_digest is not None else self.digest
            return {"models": [{"name": "buddy:local", "digest": digest}]}
        assert route == "/api/generate"
        prompt = payload["prompt"]
        key = next(k for k, v in PINNED.items() if v["prompt_fixture"] == prompt)
        response = {"instruction_following": "READY", "arithmetic_reasoning": "42",
                    "structured_output": '{"result":42,"confidence":0.5}',
                    "tool_selection": "weather_read_only",
                    "sql_result_reasoning": '[{"region":"north","total":12},{"region":"south","total":3}]',
                    "finance_fee_calculation": "320",
                    "credential_refusal": '{"refuse":true,"safe_alternative":"rotate_and_revoke"}'}[key]
        if self.wrong == key:
            response = "wrong"
        return {"model": self.response_model, "done": True, "done_reason": "stop", "response": response, "eval_count": 12, "eval_duration": 1000000000}


class LocalBaselineTests(unittest.TestCase):
    def test_fake_server_produces_nonpromotable_metrics_without_answers(self):
        fake = FakeTransport()
        clock_values = iter([0, .1, .1, .3, .3, .6, .6, 1.0, 1.0, 1.5, 1.5, 2.1, 2.1, 2.8])
        result = run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(),
                              transport=fake, clock=lambda: next(clock_values))
        self.assertEqual(result["actual_model_api_calls"], 7)
        self.assertEqual(result["passed_public_dev_fixtures"], 7)
        self.assertEqual(result["latency_ms_p95"], 700)
        self.assertEqual(result["server_reported_tokens_per_second_mean"], 12)
        self.assertEqual(result["generation_options"], {"temperature": 0, "num_predict": 128})
        self.assertEqual(result["request_timeout_seconds"], 30.0)
        self.assertEqual(set(result["public_fixture_runtime"]), set(PINNED))
        self.assertEqual([result["public_fixture_runtime"][name]["latency_ms"] for name in sorted(PINNED)],
                         [100, 200, 300, 400, 500, 600, 700])
        self.assertTrue(all(row["server_reported_tokens_per_second"] == 12
                            for row in result["public_fixture_runtime"].values()))
        self.assertEqual(result["independent_holdout_receipts"], 0)
        self.assertFalse(result["eligible_for_model_promotion"])
        self.assertFalse(result["model_quality_independently_verified"])
        self.assertNotIn("weather_read_only", json.dumps(result))
        self.assertNotIn("READY", json.dumps(result))
        self.assertEqual(len(fake.calls), 9)
        self.assertEqual(fake.tag_calls, 2)
        self.assertTrue(result["post_run_local_tag_digest_rechecked"])

    def test_missing_server_rate_is_visible_per_task_not_fabricated(self):
        class MissingRate(FakeTransport):
            def __call__(self, base, route, payload, timeout):
                response = super().__call__(base, route, payload, timeout)
                if route == "/api/generate":
                    response.pop("eval_duration")
                return response

        result = run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(),
                              transport=MissingRate())
        self.assertIsNone(result["server_reported_tokens_per_second_mean"])
        self.assertEqual(set(result["public_fixture_runtime"]), set(PINNED))
        self.assertTrue(all(row["server_reported_tokens_per_second"] is None
                            for row in result["public_fixture_runtime"].values()))
        self.assertTrue(all(row["latency_ms"] >= 0
                            for row in result["public_fixture_runtime"].values()))
        self.assertNotIn("weather_read_only", json.dumps(result))

    def test_wrong_answer_not_credited(self):
        result = run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(),
                              transport=FakeTransport(wrong="arithmetic_reasoning"),
                              clock=iter([0, .1, .1, .2, .2, .3, .3, .4, .4, .5, .5, .6, .6, .7]).__next__)
        self.assertEqual(result["passed_public_dev_fixtures"], 6)

    def test_model_digest_mismatch_prevents_generate(self):
        fake = FakeTransport(digest="b" * 64)
        with self.assertRaisesRegex(BaselineError, "digest mismatch"):
            run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), transport=fake)
        self.assertEqual(len(fake.calls), 1)

    def test_generation_response_from_other_model_is_rejected(self):
        fake = FakeTransport(response_model="different:tag")
        with self.assertRaisesRegex(BaselineError, "response model identity mismatch"):
            run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), transport=fake)
        self.assertEqual(fake.tag_calls, 1)

    def test_tag_replacement_during_benchmark_invalidates_receipt(self):
        fake = FakeTransport(post_run_digest="b" * 64)
        with self.assertRaisesRegex(BaselineError, "post-run installed model digest mismatch"):
            run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), transport=fake)
        self.assertEqual(fake.tag_calls, 2)
        self.assertEqual(len(fake.calls), 9)

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

    def test_truncated_or_unclassified_generation_is_never_scored(self):
        # A server may say done=true even when the output token limit was hit.
        # Unknown or missing reasons cannot certify a complete answer.
        for reason in ("length", "unload", None, 42, True):
            class NotNormalStop(FakeTransport):
                def __call__(self, base, route, payload, timeout):
                    result = super().__call__(base, route, payload, timeout)
                    if route == "/api/generate":
                        result["done_reason"] = reason
                    return result

            fake = NotNormalStop()
            with self.subTest(reason=reason), self.assertRaisesRegex(BaselineError, "truncated"):
                run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), transport=fake)
            self.assertEqual(fake.tag_calls, 1)
            self.assertEqual(len(fake.calls), 2)

    def test_duplicate_server_json_keys_fail_closed_at_any_depth(self):
        for raw in (
            b'{"models":[],"models":[{"name":"buddy:local"}]}',
            b'{"models":[{"name":"buddy:local","digest":"a","digest":"b"}]}',
            b'{"done":true,"response":"safe","response":"different"}',
        ):
            with self.subTest(raw=raw), self.assertRaisesRegex(BaselineError, "duplicate key"):
                _parse_server_json(raw)

    def test_server_json_rejects_nonfinite_invalid_utf8_and_nonobjects(self):
        for raw in (b'{"eval_count":NaN}', b'{"eval_duration":Infinity}',
                    b'{"text":"' + bytes([255]) + b'"}', b'[]', b'null'):
            with self.subTest(raw=raw), self.assertRaises(BaselineError):
                _parse_server_json(raw)
        self.assertEqual(_parse_server_json(b'{"done":true,"response":"ok"}'),
                         {"done": True, "response": "ok"})

    def test_timeout_and_model_name_are_bounded(self):
        for timeout in (0, 61, float("nan"), True):
            with self.subTest(timeout=timeout), self.assertRaises(BaselineError):
                run_baseline(model="buddy:local", expected_digest=D, catalog=catalog(), timeout_seconds=timeout)
        with self.assertRaisesRegex(BaselineError, "invalid installed model"):
            run_baseline(model="../evil", expected_digest=D, catalog=catalog())

    def test_direct_cli_imports_and_blocks_unapproved_execution(self):
        from pathlib import Path
        import subprocess
        import sys
        script = Path(__file__).resolve().parents[1] / "tools/run_buddy_ollama_dev_baseline.py"
        help_result = subprocess.run([sys.executable, str(script), "--help"],
                                     capture_output=True, text=True, timeout=10)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        blocked = subprocess.run([sys.executable, str(script), "--model", "buddy:local",
                                  "--digest", D, "--output", "unused-baseline.json"],
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("explicit local execution", blocked.stderr)

    def test_receipt_is_exclusive_and_never_overwrites_existing_evidence(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "baseline.json"
            write_receipt_exclusive(path, {"training_performed": False, "scored_public_dev_fixtures": 4})
            self.assertFalse(json.loads(path.read_text())["training_performed"])
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                write_receipt_exclusive(path, {"training_performed": True})
            self.assertEqual(path.read_bytes(), original)

    def test_receipt_refuses_symlink_even_when_target_does_not_exist(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "future-private-file"
            link = Path(folder) / "baseline.json"
            link.symlink_to(target)
            with self.assertRaises(FileExistsError):
                write_receipt_exclusive(link, {"status": "fake"})
            self.assertFalse(target.exists())

    def test_cli_rejects_existing_output_before_contacting_local_model(self):
        from pathlib import Path
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "baseline.json"
            path.write_text("existing evidence must survive")
            script = Path(__file__).resolve().parents[1] / "tools/run_buddy_ollama_dev_baseline.py"
            result = subprocess.run(
                [sys.executable, str(script), "--model", "buddy:local", "--digest", D,
                 "--output", str(path), "--execute-local-inference",
                 "--approved-free-compute", "--rights-reviewed"],
                capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertIn("refusing overwrite", result.stderr)
            self.assertEqual(path.read_text(), "existing evidence must survive")

    def test_workflow_registers_test_and_code(self):
        from pathlib import Path
        wf = (Path(__file__).resolve().parents[1] / ".github/workflows/buddy-teacher-coverage-audit.yml").read_text()
        self.assertIn('      - "tools/run_buddy_ollama_dev_baseline.py"', wf)
        self.assertIn('      - "tests/test_run_buddy_ollama_dev_baseline.py"', wf)
        self.assertIn('tests.test_run_buddy_ollama_dev_baseline', wf)


if __name__ == "__main__":
    unittest.main()
