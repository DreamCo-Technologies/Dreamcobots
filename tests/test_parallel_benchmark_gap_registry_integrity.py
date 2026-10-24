"""Fail-closed coverage tests for the shared parallel benchmark gap registry."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools import build_parallel_benchmark_gap_registry as registry


class ParallelBenchmarkGapRegistryIntegrityTests(unittest.TestCase):
    def _run_fixture(self, document):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "config" / "generated"
            generated.mkdir(parents=True)
            source = generated / "example-benchmark.json"
            source.write_text(json.dumps(document), encoding="utf-8")
            output = generated / "parallel-benchmark-gap-registry.json"
            report = root / "reports" / "PARALLEL_BENCHMARK_GAP_REGISTRY.md"
            with patch.multiple(
                registry, ROOT=root, GEN=generated, OUT=output, REPORT=report
            ), redirect_stdout(StringIO()):
                exit_code = registry.main()
            return exit_code, json.loads(output.read_text()), source.read_text()

    def test_missing_case_collection_stays_visible_but_blocks_completeness(self):
        document = {"schema": "fixture.benchmark.v1", "description": "not executable"}
        exit_code, output, unchanged_source = self._run_fixture(document)
        self.assertEqual(exit_code, 2)
        self.assertFalse(output["registry_complete"])
        self.assertEqual(output["artifact_placeholder_count"], 1)
        self.assertEqual(output["defined_case_count"], 0)
        self.assertEqual(output["benchmark_case_count"], 1)
        self.assertEqual(output["entries"][0]["status"], "needs_benchmark_definition")
        self.assertIn("no executable benchmark case collection", output["source_errors"][0])
        self.assertEqual(json.loads(unchanged_source), document)

    def test_executable_case_collection_can_complete_inventory_not_mastery(self):
        exit_code, output, _ = self._run_fixture(
            {"cases": [{"id": "fixture-case", "domain": "sandbox"}]}
        )
        self.assertEqual(exit_code, 0)
        self.assertTrue(output["registry_complete"])
        self.assertEqual(output["artifact_placeholder_count"], 0)
        self.assertEqual(output["defined_case_count"], 1)
        self.assertEqual(output["entries"][0]["status"], "needs_runtime_baseline")
        self.assertIn("not evidence that the gap is closed", output["truth_boundary"])

    def test_empty_executable_collection_remains_blocked(self):
        exit_code, output, _ = self._run_fixture({"cases": []})
        self.assertEqual(exit_code, 2)
        self.assertFalse(output["registry_complete"])
        self.assertEqual(output["benchmark_case_count"], 0)
        self.assertEqual(output["artifact_placeholder_count"], 0)
        self.assertTrue(output["source_errors"])


if __name__ == "__main__":
    unittest.main()
