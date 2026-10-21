"""Offline regression checks for benchmark-source discovery; not mastery evidence."""
import ast
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import build_parallel_benchmark_gap_registry as registry

class RegistryIntegrityTests(unittest.TestCase):
    def run_registry(self, artifacts):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            gen=root/'config/generated'
            gen.mkdir(parents=True)
            for name,doc in artifacts.items():
                (gen/name).write_text(json.dumps(doc))
            with (patch.object(registry,'ROOT',root),
                  patch.object(registry,'GEN',gen),
                  patch.object(registry,'OUT',gen/'parallel-benchmark-gap-registry.json'),
                  patch.object(registry,'REPORT',root/'reports/PARALLEL_BENCHMARK_GAP_REGISTRY.md'),
                  contextlib.redirect_stdout(io.StringIO())):
                result=registry.main()
            return result,json.loads((gen/'parallel-benchmark-gap-registry.json').read_text())

    def test_module_compiles(self):
        ast.parse(Path(registry.__file__).read_text())

    def test_derived_metadata_is_excluded(self):
        result,data=self.run_registry({
            'benchmark-suite-gap-contracts.json':{'entries':[{'suite_id':'not-executable'}]},
            'buddy_benchmark_index.json':{'repositorySuites':[]},
            'buddy_model_benchmarks.json':{'suites':[{'id':'routing'}]},
            'system-speed-accuracy-benchmarks.json':{'speed':[]},
            'universal-capability-benchmark.json':{'cases':[{'case_id':'real'}]}})
        self.assertEqual(result,0)
        self.assertEqual(data['benchmark_source_count'],1)
        self.assertEqual(data['benchmark_case_count'],1)
        self.assertEqual(data['entries'][0]['case_id'],'real')

    def test_empty_real_suite_fails_closed(self):
        result,data=self.run_registry({'government-department-improvement-benchmarks.json':{'cases':[]}})
        self.assertEqual(result,2)
        self.assertFalse(data['registry_complete'])
        self.assertTrue(any('no executable benchmark cases' in e for e in data['source_errors']))

    def test_missing_sources_fails_closed(self):
        result,data=self.run_registry({})
        self.assertEqual(result,2)
        self.assertFalse(data['registry_complete'])
        self.assertTrue(any('no benchmark source artifacts' in e for e in data['source_errors']))

    def test_real_missing_definition_remains_visible(self):
        result,data=self.run_registry({'github-platform-parity-benchmark.json':{'capabilities':[]}})
        self.assertEqual(result,0)
        self.assertEqual(data['artifact_placeholder_count'],1)
        self.assertEqual(data['entries'][0]['status'],'needs_benchmark_definition')

    def test_malformed_cases_fail_closed(self):
        result,data=self.run_registry({'universal-capability-benchmark.json':{'cases':'invalid'}})
        self.assertEqual(result,2)
        self.assertFalse(data['registry_complete'])

    def test_duplicate_case_id_fails_closed(self):
        result,data=self.run_registry({'universal-capability-benchmark.json':{'cases':[{'case_id':'same'},{'case_id':'same'}]}})
        self.assertEqual(result,2)
        self.assertTrue(any('duplicate case identity' in e for e in data['source_errors']))

if __name__=='__main__':
    unittest.main()
