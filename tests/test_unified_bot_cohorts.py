import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_maximum_sandbox_matrix as matrix
from tools import build_ontology_snapshot as ontology
from tools import build_runtime_sync_plan as sync
from tools.build_full_system_certification import unified_bot_system_complete
from tools.build_unified_bot_system import build_unified_system
from tools.audit_all_bots_categories_and_agents import audit_bot_accounting
from tools.audit_maximum_sandbox_runtime import build_runtime_audit

ROOT = Path(__file__).resolve().parents[1]


class UnifiedBotCohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unified = build_unified_system(ROOT, {})
        program = json.loads((ROOT / 'config/bot-accounting-placement-program.json').read_text())
        cls.accounting = audit_bot_accounting(ROOT, program, {})

    def test_real_source_identities_and_capabilities_preserved_in_separate_cohorts(self):
        self.assertEqual(self.unified['canonical_bot_count'], 1051)
        self.assertEqual(self.unified['supplemental_bot_count'], 50)
        self.assertEqual(self.unified['total_profile_count'], 1101)
        self.assertEqual(self.unified['total_accounted_worker_records'], 1101)
        for path in sorted((ROOT / 'App_bots').glob('*.json')):
            payload = json.loads(path.read_text())
            cohort = 'supplemental' if payload.get('growth') is True else 'canonical'
            rows = {row['slug']: row for row in self.unified[f'{cohort}_bots']}
            for original in payload['bots']:
                row = rows[original['slug']]
                self.assertEqual(row['capabilities'], original['capabilities'])
                self.assertEqual(row['display_name'], original['displayName'])
                self.assertEqual(row['category'], original['category'])
                self.assertEqual(row['source'], str(path.relative_to(ROOT)))
                if cohort == 'supplemental':
                    self.assertEqual(row['status'], 'supplemental_sandbox_only')
        self.assertTrue(unified_bot_system_complete(self.unified, self.accounting))

    def test_legacy_candidates_remain_separate_and_require_promotion(self):
        recovery = {'promotion_gate': ['runtime proof'], 'items': [
            {'state': 'recoverable_new_bot', 'path': 'old/example.md', 'candidate_slugs': ['old-unique']}
        ]}
        result = build_unified_system(ROOT, recovery)
        self.assertEqual(result['canonical_bot_count'], 1051)
        self.assertEqual(result['supplemental_bot_count'], 50)
        self.assertEqual(result['total_accounted_worker_records'], 1102)
        self.assertEqual(result['legacy_pending_candidate_count'], 1)
        self.assertFalse(result['legacy_candidates'][0]['canonical_counted'])
        self.assertEqual(result['legacy_candidates'][0]['promotion_gate'], ['runtime proof'])

    def test_inflated_canonical_inventory_does_not_certify(self):
        result = copy.deepcopy(self.unified)
        result['canonical_bots'] += result['supplemental_bots']
        result['canonical_bot_count'] = 1101
        self.assertFalse(unified_bot_system_complete(result, self.accounting))

    def test_missing_or_substituted_supplemental_profile_blocks_certification(self):
        for mutation in ('missing', 'substitute', 'duplicate'):
            with self.subTest(mutation=mutation):
                result = copy.deepcopy(self.unified)
                if mutation == 'missing':
                    result['supplemental_bots'].pop()
                elif mutation == 'substitute':
                    result['supplemental_bots'][0]['slug'] = 'invented'
                else:
                    result['supplemental_bots'][0] = result['supplemental_bots'][1]
                self.assertFalse(unified_bot_system_complete(result, self.accounting))

    def test_missing_counts_and_failed_accounting_do_not_certify(self):
        for field in ('supplemental_bot_count', 'total_profile_count'):
            result = copy.deepcopy(self.unified)
            result.pop(field)
            self.assertFalse(unified_bot_system_complete(result, self.accounting))
        accounting = dict(self.accounting, accounting_complete=False)
        self.assertFalse(unified_bot_system_complete(self.unified, accounting))

    def test_runtime_evidence_requires_matching_complete_contract_for_each_cohort(self):
        plan = self.generate(matrix)
        fleet = json.loads((ROOT / 'website/data/bot-fleet-e2e.json').read_text())
        result = build_runtime_audit(plan, {}, fleet)
        self.assertEqual(result['canonical_worker_count'], 1051)
        self.assertEqual(result['supplemental_worker_count'], 50)
        self.assertTrue(result['all_canonical_workers_have_runtime_evidence'])
        self.assertTrue(result['all_supplemental_workers_have_runtime_evidence'])
        supplemental_slug = self.unified['supplemental_bots'][0]['slug']
        for mutation in ('missing', 'partial', 'failed'):
            with self.subTest(mutation=mutation):
                changed = copy.deepcopy(fleet)
                profile = next(row for row in changed['profiles'] if row['slug'] == supplemental_slug)
                if mutation == 'missing':
                    changed['profiles'].remove(profile)
                elif mutation == 'partial':
                    profile['capabilityTestsPassed'] -= 1
                else:
                    profile['capabilityTestsFailed'] = 1
                result = build_runtime_audit(plan, {}, changed)
                self.assertTrue(result['all_canonical_workers_have_runtime_evidence'])
                self.assertFalse(result['all_supplemental_workers_have_runtime_evidence'])
                self.assertIn(supplemental_slug, result['supplemental_workers_missing_runtime_evidence'])
        fleet['summary']['allDeclaredCapabilitiesTested'] = False
        result = build_runtime_audit(plan, {}, fleet)
        self.assertFalse(result['all_canonical_workers_have_runtime_evidence'])
        self.assertFalse(result['all_supplemental_workers_have_runtime_evidence'])
        self.assertEqual(result['canonical_workers_with_pass_evidence'], 0)
        self.assertEqual(result['supplemental_workers_with_pass_evidence'], 0)

    def generate(self, module):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            unified = root / 'unified.json'
            unified.write_text(json.dumps(self.unified))
            empty = root / 'empty.json'
            empty.write_text('{}')
            out = root / 'result.json'
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(module, 'ROOT', root))
                stack.enter_context(patch.object(module, 'UNIFIED', unified))
                stack.enter_context(patch.object(module, 'OUT', out))
                for name in ('WORK', 'PUBLIC', 'TASKS', 'GAPS', 'CONN'):
                    if hasattr(module, name):
                        stack.enter_context(patch.object(module, name, empty))
                stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
                self.assertEqual(module.main(), 0)
            return json.loads(out.read_text())

    def test_runtime_sync_keeps_every_profile_with_supplemental_sandbox_boundary(self):
        result = self.generate(sync)
        self.assertEqual(result['worker_count'], 1101)
        self.assertEqual(result['worker_type_counts']['canonical_bot'], 1051)
        self.assertEqual(result['worker_type_counts']['supplemental_bot'], 50)
        expected = {row['slug'] for row in self.unified['supplemental_bots']}
        actual = {row['worker_id'] for row in result['workers'] if row['worker_type'] == 'supplemental_bot'}
        self.assertEqual(actual, expected)
        self.assertTrue(all(row['runtime_state'] == 'sandbox_only' for row in result['workers'] if row['worker_type'] == 'supplemental_bot'))

    def test_matrix_retains_every_supplemental_bot_and_required_overlays(self):
        result = self.generate(matrix)
        self.assertEqual(result['worker_count'], 1101)
        self.assertEqual(result['canonical_workers'], 1051)
        self.assertEqual(result['supplemental_workers'], 50)
        self.assertGreaterEqual(result['minimum_test_dimensions_per_applicable_case'], 40)
        self.assertEqual(len({row['worker_id'] for row in result['workers']}), 1101)

    def test_ontology_keeps_all_bots_divisions_and_capabilities_connected(self):
        result = self.generate(ontology)
        self.assertEqual(result['object_type_counts']['Bot'], 1101)
        self.assertEqual(result['object_type_counts']['Division'], 55)
        self.assertEqual(result['object_type_counts']['Capability'], 8460)
        objects = {row['id'] for row in result['objects']}
        for link in result['links']:
            self.assertIn(link['from'], objects)
            self.assertIn(link['to'], objects)


if __name__ == '__main__':
    unittest.main()
