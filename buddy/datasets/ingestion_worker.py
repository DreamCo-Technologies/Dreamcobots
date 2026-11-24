"""Explicit, reproducible worker for rights-cleared local JSONL dataset ingestion."""
from __future__ import annotations
import hashlib,json,os,re,uuid
from datetime import datetime,timezone
from pathlib import Path
from typing import Any
from .hub import DatasetHub,DatasetPolicyError,sha256_file
from .license_policy import assess_training_candidate
from .object_store import dataset_object_key,ObjectStoreError

class DatasetIngestionError(RuntimeError):
    """An ingestion request failed a policy or provenance gate."""

def _load_jsonl(path:Path,masterbot_id:int)->tuple[list[dict],dict[str,str]]:
    rows=[]
    for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        try: row=json.loads(line)
        except json.JSONDecodeError as exc: raise DatasetIngestionError(f"invalid_jsonl_line_{number}") from exc
        if not isinstance(row,dict) or row.get("split") not in {"train","validation","test"}:
            raise DatasetIngestionError("every row must be an object with train/validation/test split")
        if row.get("masterbot_id")!=masterbot_id:
            raise DatasetIngestionError("each row must belong to the target MasterBot lane")
        if not (row.get("text") or (row.get("instruction") and row.get("output"))):
            raise DatasetIngestionError("each row requires text or instruction/output")
        rows.append(row)
    if not rows: raise DatasetIngestionError("dataset_file_is_empty")
    hashes={}
    for split in ("train","validation","test"):
        selected=[row for row in rows if row["split"]==split]
        if not selected: raise DatasetIngestionError(f"missing_{split}_split")
        canonical="".join(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n" for row in selected)
        hashes[f"{split}_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
    return rows,hashes

def create_ingestion_job(card:dict[str,Any],source_file:str|Path,approval_id:str,
                         output_dir:str|Path="artifacts/dataset-ingestion-jobs")->dict[str,Any]:
    if not approval_id.strip(): raise DatasetIngestionError("ingestion_approval_id_required")
    if not isinstance(card,dict): raise DatasetIngestionError("dataset_card_must_be_an_object")
    source=Path(source_file).expanduser().resolve()
    if not source.is_file(): raise DatasetIngestionError("staged_source_file_missing")
    payload={"schema":"dreamco.dataset_ingestion_job.v1","job_id":"ingest-"+uuid.uuid4().hex[:16],
      "created_at":datetime.now(timezone.utc).isoformat(),"ingestion_approval_id":approval_id,
      "source_file":str(source),"card":card,"execution_status":"NOT_EXECUTED",
      "network_download_performed":False,"training_started":False}
    root=Path(output_dir);root.mkdir(parents=True,exist_ok=True)
    path=root/(payload["job_id"]+".json")
    path.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    payload["manifest_path"]=str(path)
    return payload

def _persist_external(record:dict[str,Any],catalog:DatasetHub,masterbot_id:int,
                      approval_id:str,object_store:Any,postgres_catalog:Any)->dict[str,Any]:
    if postgres_catalog is not None and object_store is None:
        raise DatasetIngestionError("postgres_catalog_requires_approved_object_store")
    if object_store is None: return {}
    local_object=(catalog.home/record["object_path"]).resolve()
    key=dataset_object_key(masterbot_id,record["dataset_id"],int(record["version"]),record["content_sha256"])
    try:
        storage=object_store.upload_file(local_object,key,masterbot_id,approval_id,
            record["content_sha256"],"dataset")
    except ObjectStoreError as exc:
        raise DatasetIngestionError(f"object_store_persistence_failed_{type(exc).__name__}") from None
    postgres=None
    if postgres_catalog is not None:
        manifest={**record,"masterbot_id":masterbot_id,"primary_masterbot_id":masterbot_id,
            "local_object_path":record["object_path"],"object_path":key,
            "object_store_bucket":storage.get("bucket"),"object_store_version_id":storage.get("version_id"),
            "ingestion_approval_ref":approval_id}
        try: postgres=postgres_catalog.register(masterbot_id,manifest)
        except Exception as exc:
            raise DatasetIngestionError(f"postgres_catalog_persistence_failed_{type(exc).__name__}") from None
    return {"object_store":storage,"postgres_catalog":postgres,"object_store_key":key}

def execute_ingestion_job(job_path:str|Path,approval_id:str,*,hub:DatasetHub|None=None,
                          object_store:Any|None=None,postgres_catalog:Any|None=None,
                          max_bytes:int=512*1024*1024)->dict[str,Any]:
    job=json.loads(Path(job_path).read_text(encoding="utf-8"))
    if job.get("schema")!="dreamco.dataset_ingestion_job.v1" or job.get("execution_status")!="NOT_EXECUTED":
        raise DatasetIngestionError("invalid_or_already_executed_job")
    if not approval_id or approval_id!=job.get("ingestion_approval_id"):
        raise DatasetIngestionError("ingestion_approval_id_mismatch")
    if os.environ.get("DREAMCO_ALLOW_DATASET_INGESTION")!="1":
        raise DatasetIngestionError("set_DREAMCO_ALLOW_DATASET_INGESTION=1_for_explicit_ingestion")
    if postgres_catalog is not None and object_store is None:
        raise DatasetIngestionError("postgres_catalog_requires_approved_object_store")
    source=Path(job["source_file"]).resolve()
    if not source.is_file() or source.suffix.lower()!=".jsonl":
        raise DatasetIngestionError("only_staged_jsonl_files_are_supported")
    if source.stat().st_size>max_bytes: raise DatasetIngestionError("dataset_exceeds_configured_size_limit")
    card=dict(job.get("card") or {})
    try: masterbot_id=int(card["primary_masterbot_id"])
    except (KeyError,TypeError,ValueError) as exc: raise DatasetIngestionError("canonical_primary_masterbot_id_required") from exc
    rows,split_hashes=_load_jsonl(source,masterbot_id)
    if card.get("split_manifest") not in (None,{},split_hashes):
        raise DatasetIngestionError("provided_split_hashes_do_not_match_staged_file")
    card["split_manifest"]=split_hashes
    candidate={"source":card.get("source"),"id":card.get("source_id"),"url":card.get("source_url"),
      "license":card.get("license"),"ai_training_allowed":card.get("ai_training_allowed") is True,
      "content_rights_verified":card.get("content_rights_verified") is True,
      "privacy_review":card.get("privacy_review")}
    rights=assess_training_candidate(candidate)
    if rights["status"]!="PERMISSIVE_LICENSE_TRAINING_CANDIDATE_REQUIRES_DATA_QUALITY_AND_FINAL_REVIEW":
        raise DatasetIngestionError("dataset_rights_or_privacy_gate_failed")
    if card.get("rights_status")!="VERIFIED" or not str(card.get("rights_evidence","")).strip():
        raise DatasetIngestionError("final_rights_verification_evidence_required")
    if card.get("training_approved") is not True: raise DatasetIngestionError("explicit_training_approval_required")
    if card.get("data_plane") not in {"dreamco_owned_training","licensed_training","user_contributed_opt_in_training"}:
        raise DatasetIngestionError("training_data_plane_not_allowed")
    dataset_id=str(card.get("dataset_id") or "")
    if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}",dataset_id): raise DatasetIngestionError("explicit_valid_dataset_id_required")
    digest=sha256_file(source)
    catalog=hub or DatasetHub()
    previous=catalog.get(dataset_id)
    immutable_card_fields=("license","license_url","source_url","rights_status","rights_evidence",
        "training_approved","data_plane","primary_masterbot_id","privacy_review","split_manifest")
    same_metadata=bool(previous) and all(previous.get(key)==card.get(key) for key in immutable_card_fields)
    if previous and previous.get("content_sha256")==digest and same_metadata:
        external=_persist_external(previous,catalog,masterbot_id,approval_id,object_store,postgres_catalog)
        return {"schema":"dreamco.dataset_ingestion_evidence.v1",
          "status":"ALREADY_INGESTED_PERSISTED" if external else "ALREADY_INGESTED",
          "job_id":job["job_id"],"dataset_id":dataset_id,"dataset_version":previous["version"],
          "content_sha256":digest,"rows_validated":len(rows),"split_manifest":split_hashes,
          **external,"training_started":False,"network_download_performed":False,"credentials_emitted":False}
    try: record=catalog.register(card,source_file=source)
    except DatasetPolicyError as exc: raise DatasetIngestionError(f"dataset_hub_policy_rejected_{type(exc).__name__}") from None
    external=_persist_external(record,catalog,masterbot_id,approval_id,object_store,postgres_catalog)
    return {"schema":"dreamco.dataset_ingestion_evidence.v1","status":"INGESTED_PENDING_BENCHMARK",
      "job_id":job["job_id"],"dataset_id":record["dataset_id"],"dataset_version":record["version"],
      "content_sha256":record["content_sha256"],"manifest_path":f"cards/{record['dataset_id']}.v{record['version']}.json",
      "split_manifest":split_hashes,"rows_validated":len(rows),"quality":record.get("quality"),
      "rights_assessment":rights,**external,"training_started":False,"network_download_performed":False,
      "credentials_emitted":False,"next_gate":"run_baseline_and_domain_benchmarks_before_training"}
