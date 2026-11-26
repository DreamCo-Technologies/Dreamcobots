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

    def test_critical_area_map_does_not_overclaim_missing_production_evidence(self):
        import json
        from tools.build_production_readiness_evidence_manifest import MAP, ROOT
        evidence_map = json.loads(MAP.read_text(encoding="utf-8"))
        names = {name for items in evidence_map["areas"].values() for item in items for name in item.get("check_names", [])}
        runs = [{"id": index + 1, "name": name, "head_sha": "a" * 40, "status": "completed", "conclusion": "success"} for index, name in enumerate(sorted(names))]
        manifest = build_manifest(evidence_map, "a" * 40, runs, ROOT)
        contract = json.loads((ROOT / "config/production-readiness-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest["areas"]), {area["id"] for area in contract["areas"]})
        self.assertEqual(manifest["areas"]["buddy_orchestration"]["status"], "VERIFIED")
        for area in ("benchmark_framework", "security", "deployment", "observability"):
            self.assertEqual(manifest["areas"][area]["status"], "PARTIAL", area)
            self.assertTrue(manifest["areas"][area]["resolution_errors"], area)
        for area in ("capability_genome", "model_research", "teacher_model", "experiment_engine", "ablation", "distillation", "free_first", "resource_optimization", "regression", "actions", "daily_scan", "source_ingestion", "superbot", "cost_accounting"):
            self.assertEqual(manifest["areas"][area]["status"], "UNVERIFIED", area)

if __name__ == '__main__': unittest.main()
