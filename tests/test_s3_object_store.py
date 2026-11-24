import hashlib,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from buddy.datasets.object_store import ObjectStoreError,S3ObjectStore,dataset_object_key,model_artifact_key

class MissingObject(Exception):
 def __init__(self): self.response={"Error":{"Code":"404"}}

class FakeS3:
 def __init__(self): self.objects={}
 def head_bucket(self,**_kwargs): return {}
 def get_bucket_versioning(self,**_kwargs): return {"Status":"Enabled"}
 def get_bucket_encryption(self,**_kwargs):
  return {"ServerSideEncryptionConfiguration":{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}}
 def head_object(self,Bucket,Key):
  if (Bucket,Key) not in self.objects: raise MissingObject()
  return self.objects[(Bucket,Key)]["head"]
 def upload_file(self,Filename,Bucket,Key,ExtraArgs):
  data=Path(Filename).read_bytes()
  self.objects[(Bucket,Key)]={"data":data,"head":{"Metadata":ExtraArgs["Metadata"],
   "ContentLength":len(data),"VersionId":"version-1"}}
 def download_file(self,Bucket,Key,Filename):
  Path(Filename).write_bytes(self.objects[(Bucket,Key)]["data"])

class S3ObjectStoreTests(unittest.TestCase):
 def test_object_keys_are_division_scoped_and_content_addressed(self):
  digest="a"*64
  self.assertEqual(dataset_object_key(1,"finance.data",2,digest),
   f"dreamco/masterbot-001/datasets/finance.data/v2/{digest}.jsonl")
  self.assertIn("/models/dreamfinance/v0.1.0/weights/",model_artifact_key(1,"dreamfinance","0.1.0","weights",digest,"adapter.safetensors"))
  with self.assertRaisesRegex(ObjectStoreError,"division_slug"):
   model_artifact_key(1,"../bad","0.1.0","weights",digest,"weights.bin")
 def test_upload_requires_explicit_write_opt_in(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"dataset.jsonl";path.write_text('{"text":"approved"}\n')
   digest=hashlib.sha256(path.read_bytes()).hexdigest()
   store=S3ObjectStore(bucket="dreamco-test",client=FakeS3())
   with patch.dict(os.environ,{},clear=True):
    with self.assertRaisesRegex(ObjectStoreError,"ALLOW_OBJECT_STORE_WRITES"):
     store.upload_file(path,dataset_object_key(1,"fixture.data",1,digest),1,"approval-1",digest,"dataset")
 def test_upload_and_download_verify_hash_and_bucket_controls(self):
  with tempfile.TemporaryDirectory() as tmp:
   source=Path(tmp)/"dataset.jsonl";source.write_text('{"text":"licensed data"}\n')
   digest=hashlib.sha256(source.read_bytes()).hexdigest()
   key=dataset_object_key(1,"fixture.data",1,digest)
   client=FakeS3();store=S3ObjectStore(bucket="dreamco-test",client=client)
   with patch.dict(os.environ,{"DREAMCO_ALLOW_OBJECT_STORE_WRITES":"1"},clear=True):
    uploaded=store.upload_file(source,key,1,"approval-1",digest,"dataset")
   target=Path(tmp)/"downloaded.jsonl"
   downloaded=store.download_file(key,1,"read-authorization-1",digest,target)
   self.assertEqual(uploaded["status"],"UPLOADED")
   self.assertEqual(downloaded["status"],"DOWNLOADED_VERIFIED")
   self.assertEqual(target.read_bytes(),source.read_bytes())
   self.assertFalse(uploaded["credentials_emitted"])
 def test_rejects_cross_division_key_and_unencrypted_bucket(self):
  store=S3ObjectStore(bucket="dreamco-test",client=FakeS3())
  with self.assertRaisesRegex(ObjectStoreError,"division_prefix"):
   store._validate_key("dreamco/masterbot-002/datasets/x",1)
  class Unencrypted(FakeS3):
   def get_bucket_encryption(self,**_kwargs): raise RuntimeError("no encryption")
  with tempfile.TemporaryDirectory() as tmp:
   source=Path(tmp)/"x";source.write_text("x");digest=hashlib.sha256(b"x").hexdigest()
   with patch.dict(os.environ,{"DREAMCO_ALLOW_OBJECT_STORE_WRITES":"1"},clear=True):
    with self.assertRaisesRegex(ObjectStoreError,"default_encryption"):
     S3ObjectStore(bucket="dreamco-test",client=Unencrypted()).upload_file(
      source,dataset_object_key(1,"fixture.data",1,digest),1,"approval-1",digest,"dataset")

if __name__=="__main__": unittest.main()
