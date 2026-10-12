import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.proposal_registry import REGISTRY, append, bootstrap, fingerprint, propose, validate


class ProposalRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text())

    def seeds(self, name='Example Evidence Review Assistant'):
        return [{'name': name, 'purpose': 'Organize permitted evidence for review.', 'division': 'Evidence Operations'}]

    def test_baseline_is_reproducible_from_source(self):
        sources = json.loads(REGISTRY.with_name('source-excerpts.json').read_text())
        recovered = bootstrap(sources)
        self.assertEqual(self.registry['systems'][:2200], recovered['systems'])
        self.assertEqual(list(range(1, 2201)), [s['id'] for s in recovered['systems']])
        self.assertEqual(220, len(recovered['divisions']))

    def test_missing_source_never_invented(self):
        for s in self.registry['systems']:
            if s['source_status'] == 'missing':
                self.assertIsNone(s['name'])
                self.assertIsNone(s['source'])
        self.assertEqual('Universal Task Intelligence Engine', self.registry['systems'][0]['name'])

    def test_preview_is_pure_and_idempotent(self):
        before = copy.deepcopy(self.registry)
        result, ids = propose(self.registry, self.seeds(), 'test-request')
        self.assertEqual([2201], ids)
        self.assertEqual(before, self.registry)
        again, again_ids = propose(result, self.seeds(), 'test-request')
        self.assertEqual(result, again)
        self.assertEqual(ids, again_ids)
        self.assertEqual('proposed', result['systems'][-1]['status'])

    def test_reused_request_with_new_content_rejected(self):
        result, _ = propose(self.registry, self.seeds(), 'test-request')
        with self.assertRaisesRegex(ValueError, 'different content'):
            propose(result, self.seeds('Different Name'), 'test-request')

    def test_duplicate_and_oversized_batches_rejected(self):
        for seeds in (self.seeds('UNIVERSAL TASK INTELLIGENCE ENGINE'), self.seeds()*2, self.seeds()*101, []):
            with self.assertRaises(ValueError):
                propose(self.registry, seeds, 'duplicate')

    def test_existing_fleet_identity_and_cosmetic_alias_are_not_new_bots(self):
        for name in ['3D Asset Manager', '3d-asset-mgr', '3D Asset Manager AI Bot']:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Existing bot'):
                propose(self.registry, self.seeds(name), 'reuse-existing')

    def test_execution_fields_rejected(self):
        seeds = self.seeds()
        seeds[0]['command'] = 'execute something'
        with self.assertRaises(ValueError):
            propose(self.registry, seeds, 'unsafe')

    def test_cosmetic_name_reordering_is_not_a_new_capability(self):
        with self.assertRaisesRegex(ValueError, 'Near-duplicate'):
            propose(self.registry, self.seeds('Application Business Connection Center Assistant'), 'same-job')

    def test_discovery_channel_is_recorded_without_calling_a_provider(self):
        seeds = self.seeds()
        seeds[0]['discovery_channel'] = 'job_role'
        updated, _ = propose(self.registry, seeds, 'job-role')
        self.assertEqual('job_role', updated['systems'][-1]['source']['discovery_channel'])

    def test_division_and_number_corruption_rejected(self):
        bad = copy.deepcopy(self.registry)
        bad['systems'][1]['id'] = 1
        with self.assertRaises(ValueError):
            validate(bad)
        result, _ = propose(self.registry, self.seeds(), 'first')
        seeds = self.seeds('Second Example')
        seeds[0]['division'] = 'Unrelated Division'
        with self.assertRaises(ValueError):
            propose(result, seeds, 'second')

    def test_atomic_write_stale_revision_and_existing_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'registry.json'
            raw = (json.dumps(self.registry) + '\n').encode()
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, 'Stale'):
                append(path, self.seeds(), 'first', 'wrong')
            self.assertEqual(raw, path.read_bytes())
            lock = path.with_suffix('.write-lock')
            lock.touch()
            with self.assertRaises(FileExistsError):
                append(path, self.seeds(), 'first', fingerprint(raw))
            lock.unlink()
            self.assertEqual([2201], append(path, self.seeds(), 'first', fingerprint(raw)))
            validate(json.loads(path.read_text()))
            self.assertFalse(lock.exists())
            self.assertEqual([path], list(Path(directory).iterdir()))


if __name__ == '__main__':
    unittest.main()
