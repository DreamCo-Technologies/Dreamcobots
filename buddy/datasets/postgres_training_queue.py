"""Durable, division-scoped PostgreSQL training queue with leases and DLQ."""
from __future__ import annotations
import hashlib,json,os,re,uuid
from typing import Any,Callable
from .migrate_division_lifecycle import schema_name

class TrainingQueueError(RuntimeError):
    """A queue operation was rejected or lost its lease."""

def _json(value:Any)->dict[str,Any]:
    if isinstance(value,dict): return value
    if isinstance(value,str): return json.loads(value)
    raise TrainingQueueError("database_returned_invalid_json_payload")

class PostgresTrainingQueue:
    def __init__(self,dsn:str|None=None,connect:Callable[...,Any]|None=None):
        self.dsn=dsn or os.environ.get("DREAMCO_POSTGRES_DSN") or os.environ.get("DATABASE_URL")
        if not self.dsn: raise TrainingQueueError("DREAMCO_POSTGRES_DSN_or_DATABASE_URL_required")
        if connect is None:
            try: import psycopg
            except ImportError as exc: raise TrainingQueueError("install_psycopg_for_training_queue") from exc
            connect=psycopg.connect
        self._connect=connect

    @staticmethod
    def _scope(cursor:Any,masterbot_id:int)->str:
        schema=schema_name(masterbot_id)
        cursor.execute("SELECT set_config('dreamco.masterbot_id',%s,true)",(str(masterbot_id),))
        return f'"{schema}"'

    def enqueue(self,masterbot_id:int,job:dict[str,Any],*,approval_ref:str,idempotency_key:str,max_attempts:int=3)->dict[str,Any]:
        schema_name(masterbot_id)
        if not isinstance(job,dict) or job.get("schema")!="dreamco.model_training_job.v1":
            raise TrainingQueueError("valid_model_training_job_manifest_required")
        if int(job.get("masterbot_id",-1))!=masterbot_id:
            raise TrainingQueueError("training_job_masterbot_id_mismatch")
        if not approval_ref.strip() or approval_ref!=job.get("compute_approval_id"):
            raise TrainingQueueError("compute_approval_reference_mismatch")
        if not re.fullmatch(r"[A-Za-z0-9._:-]{8,160}",idempotency_key):
            raise TrainingQueueError("idempotency_key_invalid")
        if isinstance(max_attempts,bool) or not isinstance(max_attempts,int) or not 1<=max_attempts<=20:
            raise TrainingQueueError("max_attempts_must_be_1_to_20")
        serialized=json.dumps(job,sort_keys=True,ensure_ascii=False)
        manifest_hash=hashlib.sha256(serialized.encode()).hexdigest()
        job_id=str(job.get("job_id") or "")
        if not re.fullmatch(r"train-[a-f0-9]{16}",job_id):
            raise TrainingQueueError("training_job_id_invalid")
        schema=f'"{schema_name(masterbot_id)}"'
        try:
            with self._connect(self.dsn,connect_timeout=5) as connection:
                with connection.cursor() as cursor:
                    self._scope(cursor,masterbot_id)
                    cursor.execute(f"""INSERT INTO {schema}.training_jobs
                      (job_id,masterbot_id,idempotency_key,status,manifest,manifest_sha256,approval_ref,max_attempts)
                      VALUES (%s,%s,%s,'QUEUED',%s::jsonb,%s,%s,%s)
                      ON CONFLICT (idempotency_key) DO NOTHING
                      RETURNING job_id,manifest_sha256,status""",
                      (job_id,masterbot_id,idempotency_key,serialized,manifest_hash,approval_ref,max_attempts))
                    row=cursor.fetchone()
                    if row is None:
                        cursor.execute(f"""SELECT job_id,manifest_sha256,status FROM {schema}.training_jobs
                            WHERE idempotency_key=%s""",(idempotency_key,))
                        row=cursor.fetchone()
                        if row is None or str(row[1]).strip()!=manifest_hash:
                            raise TrainingQueueError("idempotency_key_conflict_with_different_manifest")
                        return {"status":"ALREADY_QUEUED","job_id":str(row[0]),"manifest_sha256":manifest_hash}
                    cursor.execute(f"""INSERT INTO {schema}.queue_events
                      (event_id,masterbot_id,job_id,event_type,payload)
                      VALUES (%s,%s,%s,%s,%s::jsonb)""",
                      ("queue-"+uuid.uuid4().hex,masterbot_id,job_id,"JOB_ENQUEUED",
                       json.dumps({"approval_ref":approval_ref,"manifest_sha256":manifest_hash})))
        except TrainingQueueError: raise
        except Exception as exc: raise TrainingQueueError(f"training_queue_enqueue_failed:{type(exc).__name__}") from None
        return {"status":"QUEUED","job_id":job_id,"manifest_sha256":manifest_hash,"credentials_emitted":False}

    def lease_next(self,masterbot_id:int,worker_id:str,lease_seconds:int=900)->dict[str,Any]|None:
        schema_name(masterbot_id)
        if not re.fullmatch(r"[A-Za-z0-9._:-]{3,120}",worker_id): raise TrainingQueueError("worker_id_invalid")
        if isinstance(lease_seconds,bool) or not isinstance(lease_seconds,int) or not 30<=lease_seconds<=7200:
            raise TrainingQueueError("lease_seconds_must_be_30_to_7200")
        schema=f'"{schema_name(masterbot_id)}"'
        try:
            with self._connect(self.dsn,connect_timeout=5) as connection:
                with connection.cursor() as cursor:
                    self._scope(cursor,masterbot_id)
                    cursor.execute(f"""UPDATE {schema}.training_jobs SET status='DEAD_LETTER',
                        locked_by=NULL,lease_expires_at=NULL,updated_at=now(),
                        last_error_type=COALESCE(last_error_type,'lease_expired_max_attempts')
                        WHERE masterbot_id=%s AND status IN ('LEASED','RUNNING')
                        AND lease_expires_at<now() AND attempts>=max_attempts""",(masterbot_id,))
                    cursor.execute(f"""WITH candidate AS (
                        SELECT job_id FROM {schema}.training_jobs
                        WHERE masterbot_id=%s AND attempts<max_attempts AND available_at<=now()
                          AND (status='QUEUED' OR (status IN ('LEASED','RUNNING') AND lease_expires_at<now()))
                        ORDER BY available_at,created_at
                        FOR UPDATE SKIP LOCKED LIMIT 1)
                        UPDATE {schema}.training_jobs AS job SET status='LEASED',
                          attempts=job.attempts+1,locked_by=%s,
                          lease_expires_at=now()+make_interval(secs=>%s),updated_at=now()
                        FROM candidate WHERE job.job_id=candidate.job_id
                        RETURNING job.job_id,job.manifest,job.manifest_sha256,job.approval_ref,
                          job.attempts,job.max_attempts,job.lease_expires_at""",
                        (masterbot_id,worker_id,lease_seconds))
                    row=cursor.fetchone()
                    if row is None: return None
                    manifest=_json(row[1])
                    actual=hashlib.sha256(json.dumps(manifest,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                    if actual!=str(row[2]).strip(): raise TrainingQueueError("leased_job_manifest_hash_mismatch")
                    cursor.execute(f"""INSERT INTO {schema}.queue_events
                      (event_id,masterbot_id,job_id,event_type,payload)
                      VALUES (%s,%s,%s,%s,%s::jsonb)""",
                      ("queue-"+uuid.uuid4().hex,masterbot_id,str(row[0]),"JOB_LEASED",
                       json.dumps({"worker_id":worker_id,"attempt":int(row[4]),"lease_seconds":lease_seconds})))
                    return {"job_id":str(row[0]),"manifest":manifest,"manifest_sha256":actual,
                        "approval_ref":str(row[3]),"attempt":int(row[4]),"max_attempts":int(row[5]),
                        "lease_expires_at":str(row[6]),"worker_id":worker_id}
        except TrainingQueueError: raise
        except Exception as exc: raise TrainingQueueError(f"training_queue_lease_failed:{type(exc).__name__}") from None

    def heartbeat(self,masterbot_id:int,job_id:str,worker_id:str,lease_seconds:int=900)->bool:
        schema_name(masterbot_id)
        if not re.fullmatch(r"[A-Za-z0-9._:-]{3,120}",worker_id): raise TrainingQueueError("worker_id_invalid")
        if isinstance(lease_seconds,bool) or not isinstance(lease_seconds,int) or not 30<=lease_seconds<=7200:
            raise TrainingQueueError("lease_seconds_must_be_30_to_7200")
        schema=f'"{schema_name(masterbot_id)}"'
        with self._connect(self.dsn,connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                self._scope(cursor,masterbot_id)
                cursor.execute(f"""UPDATE {schema}.training_jobs SET lease_expires_at=now()+make_interval(secs=>%s),
                    updated_at=now() WHERE job_id=%s AND masterbot_id=%s AND locked_by=%s
                    AND status IN ('LEASED','RUNNING') AND lease_expires_at>now()
                    RETURNING job_id""",(lease_seconds,job_id,masterbot_id,worker_id))
                return cursor.fetchone() is not None

    def complete(self,masterbot_id:int,job_id:str,worker_id:str,result:dict[str,Any])->dict[str,Any]:
        schema=f'"{schema_name(masterbot_id)}"'
        if not isinstance(result,dict) or result.get("schema")!="dreamco.model_training_result.v2":
            raise TrainingQueueError("verified_training_result_v2_required")
        if result.get("job_id")!=job_id or result.get("masterbot_id")!=masterbot_id or result.get("weights_trained") is not True:
            raise TrainingQueueError("training_result_job_division_or_weight_evidence_invalid")
        hashes=result.get("artifact_hashes") or {}
        for key in ("weights_directory_sha256","checkpoints_directory_sha256","tokenizer_directory_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}",str(hashes.get(key,""))):
                raise TrainingQueueError(f"training_result_missing_{key}")
        serialized=json.dumps(result,sort_keys=True,ensure_ascii=False)
        digest=hashlib.sha256(serialized.encode()).hexdigest()
        with self._connect(self.dsn,connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                self._scope(cursor,masterbot_id)
                cursor.execute(f"""UPDATE {schema}.training_jobs SET status='COMPLETED',
                    result=%s::jsonb,result_sha256=%s,locked_by=NULL,lease_expires_at=NULL,updated_at=now()
                    WHERE job_id=%s AND masterbot_id=%s AND locked_by=%s
                    AND status IN ('LEASED','RUNNING') AND lease_expires_at>now()
                    RETURNING job_id""",(serialized,digest,job_id,masterbot_id,worker_id))
                if cursor.fetchone() is None: raise TrainingQueueError("training_job_lease_lost_before_completion")
                cursor.execute(f"""INSERT INTO {schema}.queue_events
                    (event_id,masterbot_id,job_id,event_type,payload)
                    VALUES (%s,%s,%s,%s,%s::jsonb)""",
                    ("queue-"+uuid.uuid4().hex,masterbot_id,job_id,"JOB_COMPLETED",
                     json.dumps({"result_sha256":digest})))
        return {"status":"COMPLETED","job_id":job_id,"result_sha256":digest}

    def fail(self,masterbot_id:int,job_id:str,worker_id:str,error_type:str)->dict[str,Any]:
        schema=f'"{schema_name(masterbot_id)}"'
        safe_error=re.sub(r"[^A-Za-z0-9_.-]","_",str(error_type))[:120] or "UnknownError"
        with self._connect(self.dsn,connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                self._scope(cursor,masterbot_id)
                cursor.execute(f"""UPDATE {schema}.training_jobs SET
                    status=CASE WHEN attempts>=max_attempts THEN 'DEAD_LETTER' ELSE 'QUEUED' END,
                    available_at=now()+make_interval(secs=>LEAST(3600,60*power(2,GREATEST(attempts-1,0)))),
                    locked_by=NULL,lease_expires_at=NULL,last_error_type=%s,updated_at=now()
                    WHERE job_id=%s AND masterbot_id=%s AND locked_by=%s
                    AND status IN ('LEASED','RUNNING') AND lease_expires_at>now()
                    RETURNING status,attempts,max_attempts""",(safe_error,job_id,masterbot_id,worker_id))
                row=cursor.fetchone()
                if row is None: raise TrainingQueueError("training_job_lease_lost_before_failure_update")
                status=str(row[0])
                cursor.execute(f"""INSERT INTO {schema}.queue_events
                    (event_id,masterbot_id,job_id,event_type,payload)
                    VALUES (%s,%s,%s,%s,%s::jsonb)""",
                    ("queue-"+uuid.uuid4().hex,masterbot_id,job_id,"JOB_"+status,
                     json.dumps({"error_type":safe_error,"attempts":int(row[1]),"max_attempts":int(row[2])})))
        return {"status":status,"job_id":job_id,"error_type":safe_error,
            "attempts":int(row[1]),"max_attempts":int(row[2])}
