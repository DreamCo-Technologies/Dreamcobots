"""S3-compatible object storage health and cross-bucket backup/restore evidence.

This adapter never creates buckets or changes bucket policies. Live canary
writes require an explicit environment opt-in and are confined to a generated
healthcheck prefix that should be covered by lifecycle retention.
"""
from __future__ import annotations
import io, json, os, re, uuid
from datetime import datetime, timezone
from typing import Any

class ObjectStoreError(RuntimeError):
    """Object storage is not configured or failed a required health check."""

BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
PREFIX_RE = re.compile(r"^[a-zA-Z0-9/_-]{1,120}$")

def _classification(bucket: str, client: Any) -> dict[str, Any]:
    versioning=client.get_bucket_versioning(Bucket=bucket)
    try:
        encryption=client.get_bucket_encryption(Bucket=bucket)
    except Exception as exc:
        code=getattr(exc,"response",{}).get("Error",{}).get("Code")
        if code in {"ServerSideEncryptionConfigurationNotFoundError","NoSuchServerSideEncryptionConfiguration"}:
            encryption={}
        else:
            raise ObjectStoreError("bucket_encryption_inspection_failed") from None
    try:
        public=client.get_public_access_block(Bucket=bucket)
    except Exception as exc:
        code=getattr(exc,"response",{}).get("Error",{}).get("Code")
        if code in {"NoSuchPublicAccessBlockConfiguration","NoSuchPublicAccessBlock"}:
            public={}
        else:
            raise ObjectStoreError("bucket_public_access_inspection_failed") from None
    try:
        lifecycle=client.get_bucket_lifecycle_configuration(Bucket=bucket)
    except Exception as exc:
        code=getattr(exc,"response",{}).get("Error",{}).get("Code")
        if code in {"NoSuchLifecycleConfiguration","NoSuchLifecycle"}:
            lifecycle={}
        else:
            raise ObjectStoreError("bucket_lifecycle_inspection_failed") from None
    rules=lifecycle.get("Rules",[])
    retention=[]
    for rule in rules:
        expiration=rule.get("Expiration") or {}
        noncurrent=rule.get("NoncurrentVersionExpiration") or {}
        days=expiration.get("Days") or noncurrent.get("NoncurrentDays")
        if isinstance(days,int) and days>0: retention.append(days)
    algorithms=[]
    for rule in encryption.get("ServerSideEncryptionConfiguration",{}).get("Rules",[]):
        default=rule.get("ApplyServerSideEncryptionByDefault") or {}
        algorithms.append(default.get("SSEAlgorithm"))
    config=public.get("PublicAccessBlockConfiguration") or {}
    public_blocked=all(config.get(k) is True for k in (
        "BlockPublicAcls","IgnorePublicAcls","BlockPublicPolicy","RestrictPublicBuckets"))
    return {
        "versioning_enabled":versioning.get("Status")=="Enabled",
        "encryption_at_rest":bool(algorithms) and all(x in {"AES256","aws:kms","aws:kms:dsse"} for x in algorithms),
        "encryption_algorithms":algorithms,
        "public_access_blocked":public_blocked,
        "retention_days":min(retention) if retention else None,
    }

def _client_from_env():
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise ObjectStoreError("install_boto3_to_use_s3_object_storage") from exc
    endpoint=os.environ.get("DREAMCO_OBJECT_STORE_ENDPOINT_URL","").strip() or None
    if endpoint and not endpoint.startswith("https://"):
        raise ObjectStoreError("object_store_endpoint_must_use_https")
    return boto3.client("s3",region_name=os.environ.get("DREAMCO_OBJECT_STORE_REGION","us-east-1"),
        endpoint_url=endpoint,config=Config(s3={"addressing_style":"path"}))

def run_object_store_healthcheck(*,client:Any=None,allow_canary:bool=False,
                                 primary_bucket:str|None=None,backup_bucket:str|None=None,
                                 prefix:str|None=None)->dict[str,Any]:
    """Verify two buckets and perform an isolated write/read/backup/restore canary."""
    primary=primary_bucket or os.environ.get("DREAMCO_OBJECT_STORE_BUCKET","").strip()
    backup=backup_bucket or os.environ.get("DREAMCO_OBJECT_STORE_BACKUP_BUCKET","").strip()
    key_prefix=prefix or os.environ.get("DREAMCO_OBJECT_STORE_HEALTHCHECK_PREFIX","dreamco/healthchecks")
    if not BUCKET_RE.fullmatch(primary) or not BUCKET_RE.fullmatch(backup) or primary==backup:
        raise ObjectStoreError("distinct_valid_primary_and_backup_buckets_are_required")
    if not PREFIX_RE.fullmatch(key_prefix):
        raise ObjectStoreError("object_store_healthcheck_prefix_is_invalid")
    if client is None: client=_client_from_env()
    primary_cfg=_classification(primary,client)
    backup_cfg=_classification(backup,client)
    config_ok=all(primary_cfg[k] and backup_cfg[k] for k in (
        "versioning_enabled","encryption_at_rest","public_access_blocked"))
    retention=backup_cfg.get("retention_days")
    if not config_ok or not isinstance(retention,int) or retention<=0:
        return {"schema":"dreamco.object_store_health_evidence.v1","status":"BLOCKED",
            "observed_at":datetime.now(timezone.utc).isoformat(),"primary_bucket":primary,
            "backup_bucket":backup,"primary":primary_cfg,"backup":backup_cfg,
            "backup_restore_test":"NOT_RUN","retention_days":retention,
            "encryption_at_rest":bool(primary_cfg["encryption_at_rest"] and backup_cfg["encryption_at_rest"]),
            "versioning_enabled":bool(primary_cfg["versioning_enabled"] and backup_cfg["versioning_enabled"]),
            "public_access_blocked":bool(primary_cfg["public_access_blocked"] and backup_cfg["public_access_blocked"]),
            "credentials_emitted":False,"blocker":"bucket_security_or_retention_configuration_incomplete"}
    if not allow_canary and os.environ.get("DREAMCO_ALLOW_OBJECT_STORE_CANARY")!="1":
        return {"schema":"dreamco.object_store_health_evidence.v1","status":"CONFIGURED_NOT_VALIDATED",
            "observed_at":datetime.now(timezone.utc).isoformat(),"primary_bucket":primary,
            "backup_bucket":backup,"primary":primary_cfg,"backup":backup_cfg,
            "backup_restore_test":"NOT_RUN","retention_days":retention,
            "encryption_at_rest":True,"versioning_enabled":True,"public_access_blocked":True,
            "credentials_emitted":False,"blocker":"explicit_canary_opt_in_required"}
    run_id=uuid.uuid4().hex
    primary_key=f"{key_prefix}/primary/{run_id}.json"
    backup_key=f"{key_prefix}/backup/{run_id}.json"
    restore_key=f"{key_prefix}/restore/{run_id}.json"
    payload=json.dumps({"schema":"dreamco.object_store_canary.v1","run_id":run_id,
        "created_at":datetime.now(timezone.utc).isoformat()}).encode("utf-8")
    try:
        put=client.put_object(Bucket=primary,Key=primary_key,Body=payload)
        version_id=put.get("VersionId")
        if not version_id:
            raise ObjectStoreError("primary_object_version_id_missing")
        head=client.head_object(Bucket=primary,Key=primary_key)
        if head.get("ServerSideEncryption") not in {"AES256","aws:kms","aws:kms:dsse"}:
            raise ObjectStoreError("primary_canary_object_encryption_not_verified")
        read=client.get_object(Bucket=primary,Key=primary_key)
        if read["Body"].read()!=payload:
            raise ObjectStoreError("primary_canary_readback_mismatch")
        source={"Bucket":primary,"Key":primary_key}
        if version_id: source["VersionId"]=version_id
        backup_copy=client.copy_object(Bucket=backup,Key=backup_key,CopySource=source)
        if not backup_copy.get("VersionId"):
            raise ObjectStoreError("backup_object_version_id_missing")
        backup_head=client.head_object(Bucket=backup,Key=backup_key)
        if backup_head.get("ServerSideEncryption") not in {"AES256","aws:kms","aws:kms:dsse"}:
            raise ObjectStoreError("backup_canary_object_encryption_not_verified")
        backup_read=client.get_object(Bucket=backup,Key=backup_key)
        if backup_read["Body"].read()!=payload:
            raise ObjectStoreError("backup_copy_readback_mismatch")
        restore_copy=client.copy_object(Bucket=primary,Key=restore_key,
            CopySource={"Bucket":backup,"Key":backup_key})
        if not restore_copy.get("VersionId"):
            raise ObjectStoreError("restored_object_version_id_missing")
        restore_head=client.head_object(Bucket=primary,Key=restore_key)
        if restore_head.get("ServerSideEncryption") not in {"AES256","aws:kms","aws:kms:dsse"}:
            raise ObjectStoreError("restored_canary_object_encryption_not_verified")
        restored=client.get_object(Bucket=primary,Key=restore_key)
        if restored["Body"].read()!=payload:
            raise ObjectStoreError("restore_readback_mismatch")
    except ObjectStoreError:
        raise
    except Exception as exc:
        raise ObjectStoreError("object_store_canary_failed_"+type(exc).__name__) from None
    return {"schema":"dreamco.object_store_health_evidence.v1","status":"HEALTHY",
        "observed_at":datetime.now(timezone.utc).isoformat(),"primary_bucket":primary,
        "backup_bucket":backup,"primary":primary_cfg,"backup":backup_cfg,
        "primary_canary_key":primary_key,"backup_canary_key":backup_key,
        "restore_canary_key":restore_key,"primary_version_id":version_id,
        "backup_restore_test":"PASS","retention_days":retention,
        "encryption_at_rest":True,"versioning_enabled":True,"public_access_blocked":True,
        "credentials_emitted":False,"canary_payload_contains_secrets":False,
        "note":"A cross-bucket canary copy/restore passed. This is not a full disaster-recovery exercise or proof of cross-account/region resilience."}

def run_division_object_store_healthcheck(masterbot_id:int, **kwargs:Any)->dict[str,Any]:
    """Run the canary under the canonical division's isolated key prefix."""
    if isinstance(masterbot_id,bool) or not isinstance(masterbot_id,int) or not 1<=masterbot_id<=65:
        raise ObjectStoreError("masterbot_id_must_be_between_1_and_65")
    base=kwargs.pop("prefix",None) or os.environ.get("DREAMCO_OBJECT_STORE_HEALTHCHECK_PREFIX","dreamco/healthchecks")
    evidence=run_object_store_healthcheck(prefix=f"{base}/divisions/{masterbot_id:03d}",**kwargs)
    evidence["masterbot_id"]=masterbot_id
    return evidence

def upload_division_dataset(masterbot_id:int,dataset_id:str,dataset_version:int,source_file:str,
                            content_sha256:str,upload_approval_id:str,*,client:Any=None,
                            bucket:str|None=None,prefix:str="dreamco/datasets")->dict[str,Any]:
    """Upload one verified dataset object into its division-isolated S3 prefix."""
    import hashlib
    from pathlib import Path
    if isinstance(masterbot_id,bool) or not isinstance(masterbot_id,int) or not 1<=masterbot_id<=65:
        raise ObjectStoreError("masterbot_id_must_be_between_1_and_65")
    if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}",str(dataset_id)):
        raise ObjectStoreError("dataset_id_is_invalid")
    if isinstance(dataset_version,bool) or not isinstance(dataset_version,int) or dataset_version<1:
        raise ObjectStoreError("dataset_version_must_be_positive")
    if not re.fullmatch(r"[0-9a-f]{64}",str(content_sha256)):
        raise ObjectStoreError("content_sha256_must_be_lowercase_sha256")
    if not str(upload_approval_id).strip():
        raise ObjectStoreError("dataset_object_upload_approval_id_required")
    if os.environ.get("DREAMCO_ALLOW_DATASET_OBJECT_UPLOAD")!="1":
        raise ObjectStoreError("set_DREAMCO_ALLOW_DATASET_OBJECT_UPLOAD=1_for_explicit_upload")
    target_bucket=bucket or os.environ.get("DREAMCO_OBJECT_STORE_BUCKET","").strip()
    if not BUCKET_RE.fullmatch(target_bucket):
        raise ObjectStoreError("valid_primary_object_store_bucket_required")
    if not PREFIX_RE.fullmatch(prefix):
        raise ObjectStoreError("object_store_dataset_prefix_is_invalid")
    if client is None: client=_client_from_env()
    config=_classification(target_bucket,client)
    if not all(config[k] for k in ("versioning_enabled","encryption_at_rest","public_access_blocked")):
        raise ObjectStoreError("object_store_bucket_security_configuration_incomplete")
    source=Path(source_file).expanduser().resolve()
    if not source.is_file(): raise ObjectStoreError("dataset_source_file_missing")
    size=source.stat().st_size
    if size>512*1024*1024: raise ObjectStoreError("dataset_source_file_exceeds_512_mib")
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=content_sha256: raise ObjectStoreError("dataset_source_content_hash_mismatch")
    key=f"{prefix}/divisions/{masterbot_id:03d}/datasets/{dataset_id}/v{dataset_version}/{digest}.jsonl"
    metadata={"masterbot-id":str(masterbot_id),"dataset-id":dataset_id,
        "dataset-version":str(dataset_version),"content-sha256":digest,
        "upload-approval-ref":str(upload_approval_id)[:128]}
    try:
        with source.open("rb") as handle:
            put=client.put_object(Bucket=target_bucket,Key=key,Body=handle,
                Metadata=metadata)
        version_id=put.get("VersionId")
        if not version_id: raise ObjectStoreError("dataset_object_version_id_missing")
        head=client.head_object(Bucket=target_bucket,Key=key)
        if head.get("ContentLength")!=size or head.get("Metadata")!=metadata:
            raise ObjectStoreError("dataset_object_metadata_or_size_verification_failed")
        if head.get("ServerSideEncryption") not in {"AES256","aws:kms","aws:kms:dsse"}:
            raise ObjectStoreError("dataset_object_encryption_not_verified")
        body=client.get_object(Bucket=target_bucket,Key=key,VersionId=version_id)["Body"]
        verified=hashlib.sha256()
        while True:
            chunk=body.read(1024*1024)
            if not chunk: break
            verified.update(chunk)
        if verified.hexdigest()!=digest:
            raise ObjectStoreError("dataset_object_readback_hash_mismatch")
    except ObjectStoreError:
        raise
    except Exception as exc:
        raise ObjectStoreError("dataset_object_upload_failed_"+type(exc).__name__) from None
    return {"schema":"dreamco.division_dataset_object_evidence.v1","status":"PERSISTED",
        "masterbot_id":masterbot_id,"dataset_id":dataset_id,"dataset_version":dataset_version,
        "bucket":target_bucket,"object_key":key,"object_version_id":version_id,
        "content_sha256":digest,"bytes":size,"server_side_encryption":head["ServerSideEncryption"],
        "versioning_enabled":True,"public_access_blocked":True,
        "upload_approval_ref":str(upload_approval_id)[:128],"credentials_emitted":False}
