from pathlib import Path
import tempfile
import unittest
from tools.build_production_readiness_evidence_manifest import build_manifest, SCHEMA

class ProductionReadinessEvidenceManifestTests(unittest.TestCase):
    def test_only_successful_checks_for_exact_revision_are_recorded(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'src').mkdir(); (root / 'src/router.py').write_text('router')
            mapping = {'schema':'dreamco.production_readiness_evidence_map.v1','areas':{'buddy_orchestration':[{'path':'src/router.py','check_names':['governed-local-tests']}]}}
            runs = [{'id':123,'name':'governed-local-tests','head_sha':'a'*40,'status':'completed','conclusion':'success'}]
            manifest = build_manifest(mapping,'a'*40,runs,root)
            self.assertEqual(manifest['schema'],SCHEMA); self.assertEqual(manifest['areas']['buddy_orchestration']['status'],'VERIFIED'); self.assertEqual(manifest['areas']['buddy_orchestration']['evidence'][0]['check_id'],'123')
    def test_failed_or_stale_checks_leave_area_unverified(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / 'router.py').write_text('router')
            mapping = {'schema':'dreamco.production_readiness_evidence_map.v1','areas':{'buddy_orchestration':[{'path':'router.py','check_names':['governed-local-tests']}]}}
            runs = [{'id':123,'name':'governed-local-tests','head_sha':'b'*40,'status':'completed','conclusion':'success'},{'id':124,'name':'governed-local-tests','head_sha':'a'*40,'status':'completed','conclusion':'failure'}]
            manifest = build_manifest(mapping,'a'*40,runs,root)
            self.assertEqual(manifest['areas']['buddy_orchestration']['status'],'UNVERIFIED'); self.assertEqual(manifest['areas']['buddy_orchestration']['evidence'],[])
    def test_missing_artifacts_and_unsafe_paths_are_not_certified(self):
        with tempfile.TemporaryDirectory() as temp:
            mapping = {'schema':'dreamco.production_readiness_evidence_map.v1','areas':{'security':[{'path':'../secret.txt','check_names':['trusted-code']},{'path':'missing.txt','check_names':['trusted-code']}]}}
            manifest = build_manifest(mapping,'a'*40,[],Path(temp))
            self.assertEqual(manifest['areas']['security']['status'],'UNVERIFIED'); self.assertEqual(len(manifest['areas']['security']['resolution_errors']),2)

if __name__ == '__main__': unittest.main()
