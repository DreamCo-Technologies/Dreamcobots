"""Offline, no-network regression checks for benchmark evidence workflow and converter."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/benchmark-evidence-loop.yml'
CONVERTER = ROOT / 'tools/convert_daily_division_benchmark.py'


def row(name='Division A', passed=2, total=2, score=100, status='pass'):
    return {'division': name, 'passed': passed, 'total': total, 'score': score, 'status': status}


def payload(rows):
    return {'schema': 'dreamco.daily_division_contract_benchmark.v2',
            'divisions': len(rows), 'divisionResults': rows}


class EvidenceWorkflowTests(unittest.TestCase):
    def test_runner_failure_is_not_suppressed(self):
        content = WORKFLOW.read_text()
        self.assertNotIn('|| true', content)
        self.assertIn('id: benchmark_run\n        continue-on-error: true', content)
        self.assertIn('node --import tsx tools/run_daily_division_benchmarks.ts', content)

    def test_failed_benchmark_keeps_valid_gap_measurements(self):
        content = WORKFLOW.read_text()
        self.assertIn("!cancelled() && steps.benchmark_run.outcome != 'skipped'", content)
        self.assertIn("!cancelled() && steps.convert.outcome == 'success'", content)
        self.assertIn('if: always()\n        with:\n          name: benchmark-evidence-', content)

    def test_final_gate_rejects_any_failed_or_skipped_stage(self):
        content = WORKFLOW.read_text()
        script = content.split('      - name: Enforce benchmark evidence gate\n', 1)[1].split('        run: |\n', 1)[1]
        commands = '\n'.join(line.strip() for line in script.splitlines()) + '\n'
        for key in ('BENCHMARK_OUTCOME', 'CONVERT_OUTCOME', 'PLAN_OUTCOME'):
            self.assertIn(f'test "${key}" = success', commands)
        for outcomes, expected in [(['success']*3, 0), (['failure','success','success'], 1),
                                   (['success','failure','skipped'], 1), (['success','success','failure'], 1),
                                   (['skipped','skipped','skipped'], 1)]:
            env = dict(os.environ)
            env.update(zip(('BENCHMARK_OUTCOME', 'CONVERT_OUTCOME', 'PLAN_OUTCOME'), outcomes))
            proc = subprocess.run(['bash', '-e', '-c', commands], env=env, capture_output=True)
            self.assertEqual(proc.returncode, expected, outcomes)


class ConverterTests(unittest.TestCase):
    def convert(self, value, success):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'input.json'
            target = Path(temp) / 'output.json'
            source.write_text(json.dumps(value))
            proc = subprocess.run([sys.executable, str(CONVERTER), '--input', str(source),
                                   '--output', str(target)], capture_output=True, text=True)
            self.assertEqual(proc.returncode == 0, success, proc.stderr)
            self.assertEqual(target.exists(), success)
            return json.loads(target.read_text()) if success else None

    def test_valid_pass_and_failure_are_preserved(self):
        out = self.convert(payload([row(), row('Division B', 1, 2, 50, 'needs_remediation')]), True)
        self.assertEqual([r['status'] for r in out['results']], ['pass', 'failed'])

    def test_empty_or_missing_is_not_passing_evidence(self):
        self.convert(payload([]), False)
        self.convert({'schema': 'dreamco.daily_division_contract_benchmark.v2'}, False)

    def test_duplicate_divisions_fail_closed(self):
        self.convert(payload([row(), row()]), False)

    def test_contradictory_status_fails_closed(self):
        self.convert(payload([row(passed=1, total=2, score=50, status='pass')]), False)

    def test_contradictory_counts_fail_closed(self):
        self.convert(payload([row(passed=1, total=2, score=100, status='needs_remediation')]), False)

    def test_nonfinite_and_boolean_scores_fail_closed(self):
        self.convert(payload([row(score=True)]), False)
        self.convert(payload([row(score=float('nan'))]), False)

    def test_declared_count_must_match(self):
        value = payload([row()]); value['divisions'] = 65
        self.convert(value, False)


if __name__ == '__main__':
    unittest.main()
