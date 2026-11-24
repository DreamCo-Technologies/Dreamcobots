import io,unittest
from buddy.storage.object_store import ObjectStoreError,run_object_store_healthcheck,run_division_object_store_healthcheck

class FakeS3:
 def __init__(self,versioning=True,encryption=True,public=True,retention=30):
  self.versioning=versioning;self.encryption=encryption;self.public=public;self.retention=retention
  self.objects={};self.copies=[]
 def get_bucket_versioning(self,Bucket): return {"Status":"Enabled" if self.versioning else "Suspended"}
 def get_bucket_encryption(self,Bucket):
  if not self.encryption: return {"ServerSideEncryptionConfiguration":{"Rules":[]}}
  return {"ServerSideEncryptionConfiguration":{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}}
 def get_public_access_block(self,Bucket):
  value=self.public
  return {"PublicAccessBlockConfiguration":{k:value for k in ("BlockPublicAcls","IgnorePublicAcls","BlockPublicPolicy","RestrictPublicBuckets")}}
 def get_bucket_lifecycle_configuration(self,Bucket):
  return {"Rules":[{"Expiration":{"Days":self.retention}}]} if self.retention else {"Rules":[]}
 def put_object(self,Bucket,Key,Body):
  self.objects[(Bucket,Key)]=Body
  return {"VersionId":"v-primary"}
 def head_object(self,Bucket,Key): return {"ServerSideEncryption":"AES256"}
 def get_object(self,Bucket,Key): return {"Body":io.BytesIO(self.objects[(Bucket,Key)])}
 def copy_object(self,Bucket,Key,CopySource):
  source_bucket=CopySource["Bucket"];source_key=CopySource["Key"]
  self.objects[(Bucket,Key)]=self.objects[(source_bucket,source_key)]
  self.copies.append((source_bucket,source_key,Bucket,Key))
  return {"VersionId":"v-copy"}

class ObjectStoreTests(unittest.TestCase):
 def test_configuration_without_canary_is_not_reported_healthy(self):
  evidence=run_object_store_healthcheck(client=FakeS3(),primary_bucket="dreamco-primary",backup_bucket="dreamco-backup",allow_canary=False)
  self.assertEqual(evidence["status"],"CONFIGURED_NOT_VALIDATED")
  self.assertEqual(evidence["backup_restore_test"],"NOT_RUN")
 def test_canary_proves_cross_bucket_copy_and_restore(self):
  client=FakeS3()
  evidence=run_object_store_healthcheck(client=client,primary_bucket="dreamco-primary",backup_bucket="dreamco-backup",allow_canary=True)
  self.assertEqual(evidence["status"],"HEALTHY")
  self.assertEqual(evidence["backup_restore_test"],"PASS")
  self.assertTrue(evidence["encryption_at_rest"])
  self.assertTrue(evidence["versioning_enabled"])
  self.assertTrue(evidence["public_access_blocked"])
  self.assertEqual(len(client.copies),2)
  self.assertEqual(client.objects[("dreamco-primary",evidence["restore_canary_key"])],client.objects[("dreamco-backup",evidence["backup_canary_key"])])
  self.assertFalse(evidence["credentials_emitted"])
 def test_missing_versioning_or_encryption_or_public_block_fails_closed(self):
  for client in (FakeS3(versioning=False),FakeS3(encryption=False),FakeS3(public=False),FakeS3(retention=0)):
   evidence=run_object_store_healthcheck(client=client,primary_bucket="dreamco-primary",backup_bucket="dreamco-backup",allow_canary=True)
   self.assertEqual(evidence["status"],"BLOCKED")
   self.assertEqual(evidence["backup_restore_test"],"NOT_RUN")
 def test_division_healthcheck_uses_isolated_namespace(self):
  evidence=run_division_object_store_healthcheck(7,client=FakeS3(),primary_bucket="dreamco-primary",
    backup_bucket="dreamco-backup",allow_canary=True)
  self.assertEqual(evidence["masterbot_id"],7)
  self.assertIn("/divisions/007/",evidence["primary_canary_key"])
 def test_invalid_masterbot_id_is_rejected(self):
  with self.assertRaisesRegex(ObjectStoreError,"masterbot_id"):
   run_division_object_store_healthcheck(66,client=FakeS3(),primary_bucket="dreamco-primary",
     backup_bucket="dreamco-backup",allow_canary=True)
 def test_distinct_bucket_names_are_required(self):
  with self.assertRaisesRegex(ObjectStoreError,"distinct_valid"):
   run_object_store_healthcheck(client=FakeS3(),primary_bucket="dreamco-primary",backup_bucket="dreamco-primary",allow_canary=True)
 def test_invalid_prefix_is_rejected(self):
  with self.assertRaisesRegex(ObjectStoreError,"prefix_is_invalid"):
   run_object_store_healthcheck(client=FakeS3(),primary_bucket="dreamco-primary",backup_bucket="dreamco-backup",prefix="../escape",allow_canary=True)

if __name__=="__main__":unittest.main()
