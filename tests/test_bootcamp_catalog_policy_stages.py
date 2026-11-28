import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load_stage(name,relative):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

catalog=load_stage("bootcamp_catalog_sync","stages/00_catalog_sync/catalog_sync.py")
policy=load_stage("bootcamp_policy_gate","stages/01_policy_gate/policy_gate.py")

class CatalogPolicyTests(unittest.TestCase):
    def setUp(self):
        self.registry=policy.load_registry(ROOT/"contracts/license_policy.yaml")

    def test_youtube_metadata_does_not_authorize_transcripts_or_training(self):
        source={"source_url":"https://www.youtube.com/watch?v=abc","license_tag":"Creative Commons","license_record_verified":False}
        self.assertFalse(policy.evaluate_source(source,self.registry,"transcript_extraction")["allowed"])
        self.assertFalse(policy.evaluate_source(source,self.registry,"commercial_training")["allowed"])

    def test_unregistered_youtube_channel_is_not_cataloged(self):
        self.assertFalse(catalog.source_is_configured("unknown-channel","https://www.youtube.com/@random",policy.load_registry(ROOT/"contracts/license_policy.yaml")))

    def test_catalog_rejects_prefix_collision(self):
        registry=policy.load_registry(ROOT/"contracts/license_policy.yaml")
        self.assertFalse(catalog.source_is_configured("freecodecamp","https://www.youtube.com/@freecodecamp.evil",registry))

    def test_catalog_rejects_video_from_wrong_channel(self):
        with self.assertRaises(PermissionError):
            catalog.normalize_item({"id":"x","channel_id":"UC_NOT_THE_OFFICIAL_CHANNEL"},
                "https://www.youtube.com/@freecodecamp","freecodecamp","UC8butISFwT-Wl7EV0hUK0BQ")

    def test_registered_source_url_prefix_is_enforced(self):
        source={"source_id":"freecodecamp","source_url":"https://www.youtube.com/watch?v=unlisted",
                "license_tag":"CC-BY-4.0","license_record_verified":True}
        result=policy.evaluate_source(source,self.registry,"fact_extraction")
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"],"BLOCKED_SOURCE_URL_NOT_ALLOWLISTED")
        source["source_url"]="https://www.youtube.com/@freecodecamp.evil"
        result=policy.evaluate_source(source,self.registry,"fact_extraction")
        self.assertFalse(result["allowed"])

    def test_missing_item_license_snapshot_fails_closed(self):
        source={"source_id":"freecodecamp","source_url":"https://www.youtube.com/@freecodecamp",
                "license_tag":"CC-BY-4.0","license_record_verified":True}
        result=policy.evaluate_source(source,self.registry,"fact_extraction")
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"],"BLOCKED_MISSING_OR_UNVERIFIED_ITEM_LICENSE_EVIDENCE")

    def test_unknown_domain_fails_closed(self):
        source={"source_url":"https://unknown.example/item","license_tag":"MIT","license_record_verified":True}
        result=policy.evaluate_source(source,self.registry)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"],"BLOCKED_MISSING_VERIFIED_SOURCE_RECORD")

    def test_catalog_is_append_only_idempotent_and_records_updates(self):
        item={"id":"abc123","title":"Example","upload_date":"20261127","duration":42,"channel_id":"UC8butISFwT-Wl7EV0hUK0BQ"}
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/"source_catalog.jsonl"
            sources=[{"source_id":"freecodecamp","url":"https://www.youtube.com/@freecodecamp"}]
            first=catalog.sync_sources(sources,ledger,ROOT/"contracts/license_policy.yaml",lambda _: [item])
            self.assertEqual(first["new_or_updated_records"],1)
            original=ledger.read_text()
            second=catalog.sync_sources(sources,ledger,ROOT/"contracts/license_policy.yaml",lambda _: [item])
            self.assertEqual(second["new_or_updated_records"],0)
            self.assertEqual(ledger.read_text(),original)
            third=catalog.sync_sources(sources,ledger,ROOT/"contracts/license_policy.yaml",lambda _: [{**item,"duration":43}])
            self.assertEqual(third["new_or_updated_records"],1)
            rows=[json.loads(line) for line in ledger.read_text().splitlines()]
            self.assertEqual(len(rows),2)
            self.assertFalse(rows[0]["license_record_verified"])
            self.assertNotEqual(rows[0]["content_sha256"],rows[1]["content_sha256"])

    def test_hash_is_stable(self):
        self.assertEqual(catalog.canonical_hash({"video_id":"abc","duration":30}),catalog.canonical_hash({"duration":30,"video_id":"abc"}))

if __name__=="__main__":
    unittest.main()
