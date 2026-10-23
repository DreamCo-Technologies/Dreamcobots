"""Fail-closed public model prospectus: claims cannot certify mastery."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_500_model_prospectus_matrix as module


class ProspectusEvidenceTests(unittest.TestCase):
    def build(self, evidence):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'catalog.json').write_text(json.dumps({'models':[{'model_id':'m1','name':'M1','provider':'local'}]}))
            (root / 'suites.json').write_text(json.dumps({'suites':[{'benchmark_id':'s1'}]}))
            (root / 'evidence.json').write_text(json.dumps({'results': evidence}))
            out = root / 'matrix.json'
            with patch.object(module, 'CATALOG_CANDIDATES', [root / 'catalog.json']), \
                 patch.object(module, 'SUITE_CANDIDATES', [root / 'suites.json']), \
                 patch.object(module, 'EVIDENCE_CANDIDATES', [root / 'evidence.json']), \
                 patch.object(module, 'OUT', out):
                self.assertEqual(module.main(), 0)
            return json.loads(out.read_text())

    def test_empty_evidence_is_unverified(self):
        data = self.build([])
        self.assertEqual(data['verified_rows'], 0)
        self.assertEqual(data['unverified_rows'], 1)
        self.assertEqual(data['matrix'][0]['status'], 'unverified')

    def test_self_declared_pass_cannot_certify_model(self):
        data = self.build([{'model_id':'m1','benchmark_id':'s1','status':'passed',
                            'evidence_reference':'fake','execution_timestamp':'2026-10-23T00:00:00Z'}])
        self.assertEqual(data['verified_rows'], 0)
        self.assertEqual(data['unreviewed_pass_claims'], 1)
        row=data['matrix'][0]
        self.assertEqual(row['status'], 'needs_review')
        self.assertEqual(row['reported_status'], 'passed')
        self.assertIsNone(row['last_verified'])
        self.assertEqual(row['reported_timestamp'], '2026-10-23T00:00:00Z')

    def test_duplicate_conflicting_claims_not_last_writer_wins(self):
        data = self.build([{'model_id':'m1','benchmark_id':'s1','status':'failed'},
                           {'model_id':'m1','benchmark_id':'s1','status':'passed'}])
        self.assertEqual(data['verified_rows'], 0)
        self.assertEqual(data['matrix'][0]['status'], 'conflicting_evidence')

    def test_unrelated_model_claim_not_applied(self):
        data = self.build([{'model_id':'m2','benchmark_id':'s1','status':'passed'}])
        self.assertEqual(data['matrix'][0]['status'], 'unverified')

    def test_unknown_claim_preserved_without_promotion(self):
        data = self.build([{'model_id':'m1','benchmark_id':'s1','status':'something-else'}])
        self.assertEqual(data['matrix'][0]['reported_status'], 'something-else')
        self.assertEqual(data['matrix'][0]['status'], 'needs_review')


if __name__ == '__main__':
    unittest.main()
