"""Regression: generated work-platform backlog must contain real, consistent cases.

Synthetic fixtures test only the certification gate, not model capability or
production readiness. All paths are redirected to an isolated temporary folder.
"""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_full_system_certification as cert


class WorkPlatformBacklogCertificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        fixtures = {
            'verification': {'productionReady': True},
            'speed_accuracy': {'ok': True},
            'runtime_smoke': {'passed': True},
            'connections': {'connection_count': 1, 'all_declared_runtime_connections_verified': True},
            'repository_connections': {'ok': True},
            'code_trust': {'release_blockers': []},
            'bot_accounting': {'accounting_complete': True},
            'legacy_recovery': {'file_count': 1},
            'unified_bots': {'canonical_bot_count': 1051},
            'maximum_sandbox': {'worker_count': 1051, 'minimum_test_dimensions_per_applicable_case': 40},
            'sandbox_runtime': {'all_canonical_workers_have_runtime_evidence': True},
            'ontology': {'object_count': 1, 'link_count': 1},
            'work_benchmarks': {
                'status': 'generated', 'task_count': 1,
                'benchmark_case_count': 1, 'cases': [{'task_id': 'fixture-task'}],
            },
            'manufacturing': {'benchmark_case_count': 1},
            'universal_benchmark': {'case_count': 1},
            'business_benchmarks': {'case_count': 1},
            'creative_benchmarks': {'case_count': 1},
            'government_benchmarks': {'case_count': 1},
            'benchmark_gap_registry': {'benchmark_case_count': 1},
            'value_discovery': {'candidate_count': 1},
        }
        self.source_paths = {}
        for key, data in fixtures.items():
            path = root / f'{key}.json'
            path.write_text(json.dumps(data), encoding='utf-8')
            self.source_paths[key] = path
        program = root / 'program.json'
        program.write_text(json.dumps({'truth_rule': 'Synthetic certification fixture'}), encoding='utf-8')
        self.receipt = root / 'receipt.json'
        self.patches = [
            patch.object(cert, 'SOURCES', self.source_paths),
            patch.object(cert, 'PROGRAM', program),
            patch.object(cert, 'OUT', self.receipt),
            patch.object(cert, 'REPORT', root / 'report.md'),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def run_certification(self, evidence):
        self.source_paths['work_benchmarks'].write_text(json.dumps(evidence), encoding='utf-8')
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = cert.main()
        receipt = json.loads(self.receipt.read_text(encoding='utf-8'))
        return exit_code, receipt

    def test_missing_work_catalog_is_not_certified(self):
        code, doc = self.run_certification({'status': 'work_catalog_missing', 'task_count': 0,
                                            'benchmark_case_count': 0, 'cases': []})
        self.assertEqual(code, 1)
        self.assertFalse(doc['checks']['work_platform_benchmarks'])
        self.assertIn('work_platform_benchmarks', doc['release_blockers'])
        self.assertFalse(doc['fully_operational_and_connected_claim_allowed'])

    def test_empty_generated_backlog_is_not_certified(self):
        code, doc = self.run_certification({'status': 'generated', 'task_count': 1,
                                            'benchmark_case_count': 0, 'cases': []})
        self.assertEqual(code, 1)
        self.assertFalse(doc['checks']['work_platform_benchmarks'])

    def test_inconsistent_case_count_is_not_certified(self):
        code, doc = self.run_certification({'status': 'generated', 'task_count': 1,
                                            'benchmark_case_count': 2, 'cases': [{'task_id': 'fixture'}]})
        self.assertEqual(code, 1)
        self.assertFalse(doc['checks']['work_platform_benchmarks'])

    def test_boolean_case_count_is_not_certified(self):
        code, doc = self.run_certification({'status': 'generated', 'task_count': 1,
                                            'benchmark_case_count': True, 'cases': [{'task_id': 'fixture'}]})
        self.assertEqual(code, 1)
        self.assertFalse(doc['checks']['work_platform_benchmarks'])

    def test_generated_nonempty_consistent_backlog_satisfies_gate(self):
        code, doc = self.run_certification({'status': 'generated', 'task_count': 1,
                                            'benchmark_case_count': 1, 'cases': [{'task_id': 'fixture'}]})
        self.assertEqual(code, 0)
        self.assertTrue(doc['checks']['work_platform_benchmarks'])
        # This is a synthetic fixture: the test does not prove production readiness.


if __name__ == '__main__':
    unittest.main()
