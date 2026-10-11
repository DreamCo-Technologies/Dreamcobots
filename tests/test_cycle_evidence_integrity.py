"""Adversarial regressions for Cycle 024–026; all data is synthetic."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from buddy.learning.continuous_learning_controller import LearningEvent, EventType, evaluate_event
from buddy.learning.registered_runner import process_events
from buddy.learning.benchmark_learning_adapter import benchmark_to_event
from buddy.learning.workflow_benchmark_readiness import build_events
from buddy.learning.mastery_decision import MasteryEvidence, eligible_for_mastery
from tools.buddy_source_selector import Source, rank_sources
from tools.run_24h_sandbox_soak import append_receipt
from tools.verify_frontier_evidence import assess
from benchmarks.buddy_benchmark_runner import evaluate_task

ROOT = Path(__file__).resolve().parents[1]


class LearningIntegrity(unittest.TestCase):
    def event(self):
        return dict(event_id='one', event_type='benchmark', capability='coding', success=True,
                    verified=True, regression_passed=True, safety_passed=True, external_assistance=False)

    def test_inventory_never_verifies_execution(self):
        rows = build_events({'workflows': ['job.yml'], 'benchmarks': ['benchmarks/america_gov/sandbox.py', 'benchmarks/resource_mastery/sandbox.py']})['events']
        self.assertTrue(all(row['verified'] is False for row in rows))
        self.assertEqual(sum(row['promote'] for row in process_events(rows)), 0)

    def test_asserted_flags_cannot_promote(self):
        self.assertFalse(process_events([self.event()])[0]['promote'])

    def test_all_flags_reject_non_booleans(self):
        for name in ('success', 'verified', 'regression_passed', 'safety_passed', 'external_assistance'):
            for value in ('false', 'true', 0, 1, None, [], {}):
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    process_events([{**self.event(), name: value}])

    def test_duplicate_ids_rejected_before_decisions(self):
        with self.assertRaises(ValueError): process_events([self.event(), self.event()])

    def test_controller_rejects_truthy_string(self):
        self.assertFalse(evaluate_event(LearningEvent('id', EventType.BENCHMARK, 'code', True, 'false', True, True)).learn)

    def test_adapter_rejects_truthy_string(self):
        for key in ('passed', 'verified', 'native_success', 'external_assistance'):
            with self.assertRaises(ValueError): benchmark_to_event({key: 'false'})

    def test_source_authorization_and_rights_default_closed(self):
        self.assertEqual(rank_sources([Source('s', 1, 1, 1, 1, 1, 1)]), [])
        self.assertEqual(rank_sources([Source('s', 1, 1, 1, 1, 1, 1, rights_ok=True, authorized='true')]), [])
        self.assertEqual(rank_sources([Source('s', 1, 1, 1, 1, 1, 1, rights_ok=True, authorized=True)]), [('s', 1.0)])

    def test_external_assistance_cannot_establish_native_mastery(self):
        self.assertFalse(eligible_for_mastery(MasteryEvidence(3, True, True, True, True)))
        self.assertFalse(eligible_for_mastery(MasteryEvidence(3, 'true', True, True, False)))
        self.assertTrue(eligible_for_mastery(MasteryEvidence(3, True, True, True, False)))

    def test_supplied_perfect_score_is_unmeasured(self):
        row = evaluate_task({'task_id': 'test', 'baseline_score': 1}, 1)
        self.assertFalse(row.passed)
        self.assertEqual(row.status, 'unmeasured')

    def test_benchmark_cli_exit_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory)/'task.json'; task.write_text('{"tasks":[]}')
            command = [sys.executable, str(ROOT/'benchmarks/buddy_benchmark_runner.py'), str(task)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(subprocess.run(command+['--diagnostic-only'], capture_output=True).returncode, 0)

    def test_division_name_handoff_and_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'scores.json'; target = Path(directory)/'queue.json'
            source.write_text(json.dumps({'divisionResults': [{'division': 'DreamFinance', 'score': 20, 'target': 90}]}))
            command = [sys.executable, str(ROOT/'tools/benchmark_gap_planner.py'), '--scores', str(source), '--out', str(target)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            row = next(r for r in json.loads(target.read_text())['queue'] if r['division'] == 1)
            self.assertEqual(row['action'], 'CLOSE_GAPS')
            source.write_text('{"results":[{"division":"unknown"}]}')
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertFalse(json.loads(target.read_text())['complete'])


class FrontierIntegrity(unittest.TestCase):
    def setUp(self):
        self.suite = {'suite_id': 'test', 'suite_hash': 'a'*64, 'minimum_repetitions': 3,
                      'score_threshold': .8, 'evidence_required': [],
                      'lanes': [{'training_tasks': ['train'], 'holdout_tasks': ['hidden']}]}
        rows = []
        for subject in ('buddy', 'reference'):
            for phase, task in (('baseline', 'train'), ('candidate', 'train'), ('holdout', 'hidden')):
                for repetition in range(3):
                    rows.append(dict(run_id=f'{subject}-{phase}-{repetition}', task_id=task,
                                     phase=phase, subject_id=subject, score=.2 if phase == 'baseline' else .9,
                                     repo_commit='b'*40, model_sha256='c'*64, dataset_sha256='d'*64,
                                     fixture_hash=hashlib.sha256(task.encode()).hexdigest(), grader_version='v1',
                                     exact_subject_version='sha256:'+'c'*64, timestamp='2026-10-08T00:00:00+00:00',
                                     latency_ms=10, cost_usd=0, simulated=False, external_assistance=False,
                                     safety_passed=True, regression_passed=True, holdout_unseen=True))
        self.bundle = dict(schema='dreamco.buddy.frontier_run_bundle.v1', claim_context='live_comparison',
                           suite_id='test', suite_hash='a'*64, runs=rows)

    def test_complete_synthetic_contract(self):
        self.assertTrue(assess(self.bundle, self.suite)['evidence_valid'])
        self.assertFalse(assess(self.bundle, self.suite)['claimable'])

    def test_duplicate_repetitions_fail(self):
        self.bundle['runs'][1] = copy.deepcopy(self.bundle['runs'][0])
        self.assertFalse(assess(self.bundle, self.suite)['claimable'])

    def test_invalid_telemetry_flags_hashes_and_holdout_fail(self):
        for field, value in [('latency_ms', -1), ('cost_usd', float('nan')), ('score', True),
                             ('simulated', 'false'), ('safety_passed', 'true'), ('repo_commit', 'main'),
                             ('model_sha256', 'latest'), ('timestamp', 'today'), ('holdout_unseen', False)]:
            with self.subTest(field=field):
                bundle = copy.deepcopy(self.bundle); bundle['runs'][6][field] = value
                self.assertFalse(assess(bundle, self.suite)['claimable'])

    def test_holdout_cannot_appear_in_training_phase(self):
        self.bundle['runs'][0]['task_id'] = 'hidden'
        self.assertFalse(assess(self.bundle, self.suite)['claimable'])

    def test_malformed_rows_fail_closed(self):
        self.bundle['runs'] = [None]
        self.assertFalse(assess(self.bundle, self.suite)['claimable'])


class SoakIntegrity(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 8, tzinfo=timezone.utc)
        self.bots = [{'slug': 'bot', 'grok_slug': 'grok-bot'}]

    def test_empty_fleet_fails(self):
        with self.assertRaises(ValueError): append_receipt([], [], 'a'*40, '1', self.now)

    def test_one_tick_cannot_prove_24h(self):
        history, status = append_receipt([], self.bots, 'a'*40, '1', self.now)
        self.assertFalse(status['inventory_24h_covered'])
        self.assertFalse(status['runtime_24h_verified'])
        with self.assertRaises(ValueError): append_receipt(history, self.bots, 'a'*40, '1', self.now+timedelta(hours=1))

    def test_24h_inventory_is_not_runtime_uptime(self):
        history = []
        for i in range(25): history, status = append_receipt(history, self.bots, 'a'*40, str(i), self.now+timedelta(hours=i))
        self.assertTrue(status['inventory_24h_covered'])
        self.assertFalse(status['runtime_24h_verified'])
        self.assertFalse(status['production_ready'])
        _, status = append_receipt(history, self.bots, 'b'*40, 'new', self.now+timedelta(hours=25))
        self.assertFalse(status['inventory_24h_covered'])

    def test_tampering_and_gaps(self):
        history, _ = append_receipt([], self.bots, 'a'*40, '1', self.now)
        _, status = append_receipt(history, self.bots, 'a'*40, '2', self.now+timedelta(hours=3))
        self.assertEqual(status['coverage_seconds'], 0)
        history[0]['fleet_count'] = 999
        with self.assertRaises(ValueError): append_receipt(history, self.bots, 'a'*40, '2', self.now+timedelta(hours=1))


if __name__ == '__main__': unittest.main()
