import hashlib,json,unittest
from buddy.datasets.postgres_training_queue import PostgresTrainingQueue,TrainingQueueError

def training_job():
 return {"schema":"dreamco.model_training_job.v1","job_id":"train-0123456789abcdef",
  "masterbot_id":1,"compute_approval_id":"compute-approval-001","execution_status":"NOT_EXECUTED"}

class FakeCursor:
 def __init__(self): self.last_query="";self.last_params=();self.executed=[];self.next_row=None
 def __enter__(self): return self
 def __exit__(self,*_args): return False
 def execute(self,query,params=None):
  self.last_query=query;self.last_params=params or ();self.executed.append((query,params))
  self.next_row=None
  if "INSERT INTO" in query and "training_jobs" in query and "RETURNING job_id,manifest_sha256,status" in query:
   self.next_row=(self.last_params[0],self.last_params[4],"QUEUED")
  elif "WITH candidate AS" in query:
   job=training_job();digest=hashlib.sha256(json.dumps(job,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
   self.next_row=(job["job_id"],job,digest,job["compute_approval_id"],1,3,"2099-01-01T00:00:00Z")
  elif "RETURNING status,attempts,max_attempts" in query:
   self.next_row=("DEAD_LETTER",3,3)
  elif "RETURNING job_id" in query:
   self.next_row=("train-0123456789abcdef",)
 def fetchone(self): return self.next_row

class FakeConnection:
 def __init__(self): self.cursor_obj=FakeCursor()
 def __enter__(self): return self
 def __exit__(self,*_args): return False
 def cursor(self): return self.cursor_obj

class PostgresTrainingQueueTests(unittest.TestCase):
 def setUp(self):
  self.connection=FakeConnection()
  self.queue=PostgresTrainingQueue(dsn="postgresql://fake",connect=lambda *_a,**_k:self.connection)
 def test_enqueue_requires_matching_approval_and_idempotency(self):
  job=training_job()
  with self.assertRaisesRegex(TrainingQueueError,"approval_reference"):
   self.queue.enqueue(1,job,approval_ref="wrong-approval",idempotency_key="idempotency-001")
  result=self.queue.enqueue(1,job,approval_ref="compute-approval-001",idempotency_key="idempotency-001")
  self.assertEqual(result["status"],"QUEUED")
  sql="\n".join(q for q,_p in self.connection.cursor_obj.executed)
  self.assertIn("ON CONFLICT (idempotency_key) DO NOTHING",sql)
  self.assertIn("dreamco_division_001",sql)
 def test_lease_uses_skip_locked_and_returns_hash_verified_manifest(self):
  leased=self.queue.lease_next(1,"worker-gpu-01",lease_seconds=300)
  self.assertEqual(leased["job_id"],"train-0123456789abcdef")
  self.assertEqual(leased["manifest"]["masterbot_id"],1)
  sql="\n".join(q for q,_p in self.connection.cursor_obj.executed)
  self.assertIn("FOR UPDATE SKIP LOCKED",sql)
  lease_events=[
   params for query,params in self.connection.cursor_obj.executed
   if "INSERT INTO" in query and "queue_events" in query and params
  ]
  self.assertTrue(any(params[3]=="JOB_LEASED" for params in lease_events))
 def test_heartbeat_and_complete_require_active_lease_and_training_evidence(self):
  self.assertTrue(self.queue.heartbeat(1,"train-0123456789abcdef","worker-01",300))
  with self.assertRaisesRegex(TrainingQueueError,"result_v2"):
   self.queue.complete(1,"train-0123456789abcdef","worker-01",{"schema":"wrong"})
  result={"schema":"dreamco.model_training_result.v2","job_id":"train-0123456789abcdef",
   "masterbot_id":1,"weights_trained":True,"artifact_hashes":{
    "weights_directory_sha256":"a"*64,"checkpoints_directory_sha256":"b"*64,
    "tokenizer_directory_sha256":"c"*64}}
  completed=self.queue.complete(1,"train-0123456789abcdef","worker-01",result)
  self.assertEqual(completed["status"],"COMPLETED")
  self.assertEqual(len(completed["result_sha256"]),64)
 def test_failures_transition_to_dead_letter_after_max_attempts(self):
  result=self.queue.fail(1,"train-0123456789abcdef","worker-01","OutOfMemoryError")
  self.assertEqual(result["status"],"DEAD_LETTER")
  self.assertEqual(result["attempts"],3)
 def test_invalid_worker_and_lease_duration_are_rejected(self):
  with self.assertRaisesRegex(TrainingQueueError,"worker_id"):
   self.queue.lease_next(1,"x")
  with self.assertRaisesRegex(TrainingQueueError,"lease_seconds"):
   self.queue.lease_next(1,"worker-01",lease_seconds=1)

if __name__=="__main__": unittest.main()
