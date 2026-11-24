import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from buddy.datasets.hub import DatasetHub
from buddy.datasets.ingestion_worker import DatasetIngestionError,create_ingestion_job,execute_ingestion_job

def sample_card():
 return {"dataset_id":"fixture.dataset","name":"Fixture","owner":"DreamCo","license":"CC-BY-4.0",
 "license_url":"https://example.org/license","source_url":"https://example.org/dataset","source":"huggingface",
 "source_id":"dreamco/fixture","rights_status":"VERIFIED","rights_evidence":"rights-review-1",
 "data_plane":"licensed_training","training_approved":True,"primary_masterbot_id":1,
 "ai_training_allowed":True,"content_rights_verified":True,"privacy_review":"PASSED","max_duplicate_rate":0.01}

def write_jsonl(path):
 rows=[{"masterbot_id":1,"split":"train","text":"unique training example A"},
 {"masterbot_id":1,"split":"validation","text":"unique validation example B"},
 {"masterbot_id":1,"split":"test","text":"unique heldout example C"}]
 path.write_text("".join(json.dumps(x)+"\n" for x in rows),encoding="utf-8")

class FakeObjectStore:
 def __init__(self): self.uploads=[]
 def upload_file(self,path,key,masterbot_id,approval,digest,kind):
  self.uploads.append((path,key,masterbot_id,approval,digest,kind))
  return {"status":"UPLOADED","bucket":"dreamco-test","key":key,"sha256":digest,"version_id":"version-1"}

class FakePostgresCatalog:
 def __init__(self): self.manifests=[]
 def register(self,masterbot_id,manifest):
  self.manifests.append((masterbot_id,manifest))
  return {"status":"PERSISTED","schema":f"dreamco_division_{masterbot_id:03d}",
   "dataset_id":manifest["dataset_id"],"version":manifest["version"]}

class DatasetIngestionWorkerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.source=self.root/"dataset.jsonl";write_jsonl(self.source)
  self.hub=DatasetHub(self.root/"hub")
  self.job=create_ingestion_job(sample_card(),self.source,"approve-1",self.root/"jobs")
 def tearDown(self): self.temp.cleanup()
 def test_requires_matching_approval_and_opt_in(self):
  with patch.dict(os.environ,{},clear=True):
   with self.assertRaisesRegex(DatasetIngestionError,"approval_id_mismatch"):
    execute_ingestion_job(self.job["manifest_path"],"wrong",hub=self.hub)
   with self.assertRaisesRegex(DatasetIngestionError,"ALLOW_DATASET_INGESTION"):
    execute_ingestion_job(self.job["manifest_path"],"approve-1",hub=self.hub)
 def test_ingests_verified_dataset_and_pins_splits(self):
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DATASET_INGESTION":"1"},clear=True):
   result=execute_ingestion_job(self.job["manifest_path"],"approve-1",hub=self.hub)
  self.assertEqual(result["status"],"INGESTED_PENDING_BENCHMARK")
  self.assertEqual(result["rows_validated"],3)
  self.assertEqual(set(result["split_manifest"]),{"train_sha256","validation_sha256","test_sha256"})
  self.assertFalse(result["training_started"])
  self.assertEqual(self.hub.get("fixture.dataset")["content_sha256"],result["content_sha256"])
 def test_persists_object_and_manifest_to_approved_external_services(self):
  store=FakeObjectStore();postgres=FakePostgresCatalog()
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DATASET_INGESTION":"1"},clear=True):
   result=execute_ingestion_job(self.job["manifest_path"],"approve-1",hub=self.hub,
    object_store=store,postgres_catalog=postgres)
  self.assertEqual(result["status"],"INGESTED_PENDING_BENCHMARK")
  self.assertEqual(result["object_store"]["status"],"UPLOADED")
  self.assertEqual(result["postgres_catalog"]["status"],"PERSISTED")
  manifest=postgres.manifests[0][1]
  self.assertTrue(manifest["object_path"].startswith("dreamco/masterbot-001/datasets/"))
  self.assertTrue(store.uploads[0][0].is_file())
  self.assertEqual(manifest["local_object_path"],self.hub.get("fixture.dataset")["object_path"])
  self.assertFalse(result["training_started"])
 def test_postgres_catalog_cannot_be_used_without_object_storage(self):
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DATASET_INGESTION":"1"},clear=True):
   with self.assertRaisesRegex(DatasetIngestionError,"requires_approved_object_store"):
    execute_ingestion_job(self.job["manifest_path"],"approve-1",hub=self.hub,
     postgres_catalog=FakePostgresCatalog())
 def test_rejects_unverified_rights(self):
  card=sample_card();card["ai_training_allowed"]=False
  job=create_ingestion_job(card,self.source,"approve-2",self.root/"jobs")
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DATASET_INGESTION":"1"},clear=True):
   with self.assertRaisesRegex(DatasetIngestionError,"rights_or_privacy"):
    execute_ingestion_job(job["manifest_path"],"approve-2",hub=self.hub)
 def test_rejects_wrong_division(self):
  rows=[{"masterbot_id":2,"split":"train","text":"a"},{"masterbot_id":2,"split":"validation","text":"b"},{"masterbot_id":2,"split":"test","text":"c"}]
  self.source.write_text("".join(json.dumps(x)+"\n" for x in rows))
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DATASET_INGESTION":"1"},clear=True):
   with self.assertRaisesRegex(DatasetIngestionError,"target MasterBot"):
    execute_ingestion_job(self.job["manifest_path"],"approve-1",hub=self.hub)
 def test_idempotent_same_content(self):
  with patch.dict(os.environ,{"DREAMCO_ALLOW_DATASET_INGESTION":"1"},clear=True):
   first=execute_ingestion_job(self.job["manifest_path"],"approve-1",hub=self.hub)
   second=execute_ingestion_job(self.job["manifest_path"],"approve-1",hub=self.hub)
  self.assertEqual(first["status"],"INGESTED_PENDING_BENCHMARK")
  self.assertEqual(second["status"],"ALREADY_INGESTED")
  self.assertEqual(first["dataset_version"],second["dataset_version"])

if __name__=="__main__": unittest.main()
