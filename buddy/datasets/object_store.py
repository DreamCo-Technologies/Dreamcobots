"""Approval-gated, versioned S3-compatible object storage for datasets and model artifacts."""
from __future__ import annotations
import hashlib,os,re
from pathlib import Path
from typing import Any,Callable
from .migrate_division_lifecycle import schema_name

HASH=re.compile(r"^[0-9a-f]{64}$")
DATASET_ID=re.compile(r"^[A-Za-z0-9._-]{3,100}$")
MODEL_SLUG=re.compile(r"^[a-z0-9-]{2,80}$")

class ObjectStoreError(RuntimeError):
    """Object storage request failed a configuration, policy, or integrity check."""

def dataset_object_key(masterbot_id:int,dataset_id:str,version:int,sha256:str)->str:
    schema_name(masterbot_id)
    if not DATASET_ID.fullmatch(dataset_id): raise ObjectStoreError("dataset_id_invalid")
    if isinstance(version,bool) or not isinstance(version,int) or version<1: raise ObjectStoreError("dataset_version_invalid")
    if not HASH.fullmatch(sha256): raise ObjectStoreError("dataset_sha256_invalid")
    return f"dreamco/masterbot-{masterbot_id:03d}/datasets/{dataset_id}/v{version}/{sha256}.jsonl"

def model_artifact_key(masterbot_id:int,division_slug:str,model_version:str,artifact_type:str,
                       sha256:str,filename:str)->str:
    schema_name(masterbot_id)
    if not MODEL_SLUG.fullmatch(division_slug): raise ObjectStoreError("division_slug_invalid")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+",model_version): raise ObjectStoreError("model_version_invalid")
    if artifact_type not in {"weights","checkpoints","tokenizer","benchmark"}: raise ObjectStoreError("artifact_type_invalid")
    if not HASH.fullmatch(sha256): raise ObjectStoreError("artifact_sha256_invalid")
    name=Path(filename).name
    if name!=filename or name in {"",".",".."}: raise ObjectStoreError("artifact_filename_invalid")
    return f"dreamco/masterbot-{masterbot_id:03d}/models/{division_slug}/v{model_version}/{artifact_type}/{sha256}/{name}"

def _file_sha256(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()

class S3ObjectStore:
    def __init__(self,bucket:str|None=None,region:str|None=None,endpoint_url:str|None=None,
                 client:Any|None=None):
        self.bucket=bucket or os.environ.get("DREAMCO_OBJECT_STORE_BUCKET","")
        self.region=region or os.environ.get("DREAMCO_OBJECT_STORE_REGION","us-east-1")
        self.endpoint_url=endpoint_url or os.environ.get("DREAMCO_OBJECT_STORE_ENDPOINT_URL")
        if not self.bucket: raise ObjectStoreError("DREAMCO_OBJECT_STORE_BUCKET_required")
        if self.endpoint_url and not self.endpoint_url.startswith("https://"):
            raise ObjectStoreError("object_store_endpoint_must_use_https")
        if client is None:
            try: import boto3
            except ImportError as exc: raise ObjectStoreError("install_boto3_for_s3_object_storage") from exc
            client=boto3.client("s3",region_name=self.region,endpoint_url=self.endpoint_url)
        self.client=client

    def _validate_key(self,key:str,masterbot_id:int)->None:
        prefix=f"dreamco/masterbot-{masterbot_id:03d}/"
        segments=key.split("/") if isinstance(key,str) else []
        if not isinstance(key,str) or not key.startswith(prefix) or any(part in {"",".",".."} for part in segments) or key.startswith("/"):
            raise ObjectStoreError("object_key_must_be_inside_the_requested_division_prefix")

    def _validate_bucket_controls(self)->None:
        self.client.head_bucket(Bucket=self.bucket)
        versioning=self.client.get_bucket_versioning(Bucket=self.bucket)
        if versioning.get("Status")!="Enabled":
            raise ObjectStoreError("bucket_versioning_must_be_enabled")
        try: encryption=self.client.get_bucket_encryption(Bucket=self.bucket)
        except Exception as exc: raise ObjectStoreError("bucket_default_encryption_must_be_configured") from None
        rules=encryption.get("ServerSideEncryptionConfiguration",{}).get("Rules",[])
        algorithms={x.get("ApplyServerSideEncryptionByDefault",{}).get("SSEAlgorithm") for x in rules}
        if not algorithms.intersection({"AES256","aws:kms"}):
            raise ObjectStoreError("bucket_default_encryption_must_be_aes256_or_kms")

    @staticmethod
    def _is_not_found(exc:Exception)->bool:
        response=getattr(exc,"response",{})
        code=str(response.get("Error",{}).get("Code",""))
        return code in {"404","NoSuchKey","NotFound"}

    def upload_file(self,local_path:str|Path,key:str,masterbot_id:int,approval_ref:str,
                    expected_sha256:str,object_type:str)->dict[str,Any]:
        if os.environ.get("DREAMCO_ALLOW_OBJECT_STORE_WRITES")!="1":
            raise ObjectStoreError("set_DREAMCO_ALLOW_OBJECT_STORE_WRITES=1_for_explicit_upload")
        schema_name(masterbot_id)
        if not approval_ref.strip(): raise ObjectStoreError("object_upload_approval_ref_required")
        if not HASH.fullmatch(expected_sha256): raise ObjectStoreError("expected_sha256_invalid")
        if object_type not in {"dataset","model_weights","model_checkpoint","tokenizer","benchmark_evidence"}:
            raise ObjectStoreError("object_type_invalid")
        self._validate_key(key,masterbot_id)
        path=Path(local_path).resolve()
        if not path.is_file(): raise ObjectStoreError("local_object_file_missing")
        actual=_file_sha256(path)
        if actual!=expected_sha256: raise ObjectStoreError("local_object_sha256_mismatch")
        self._validate_bucket_controls()
        try:
            existing=self.client.head_object(Bucket=self.bucket,Key=key)
        except Exception as exc:
            if not self._is_not_found(exc): raise ObjectStoreError(f"object_head_failed:{type(exc).__name__}") from None
            existing=None
        if existing is not None:
            metadata=existing.get("Metadata",{})
            if metadata.get("sha256")!=actual or int(existing.get("ContentLength",-1))!=path.stat().st_size:
                raise ObjectStoreError("immutable_object_key_conflict")
            return {"status":"ALREADY_PRESENT","bucket":self.bucket,"key":key,
                "sha256":actual,"bytes":path.stat().st_size,"version_id":existing.get("VersionId"),
                "approval_ref":approval_ref,"credentials_emitted":False}
        try:
            self.client.upload_file(str(path),self.bucket,key,ExtraArgs={"Metadata":{
                "sha256":actual,"masterbot_id":str(masterbot_id),"object_type":object_type,
                "approval_ref":approval_ref}})
            stored=self.client.head_object(Bucket=self.bucket,Key=key)
        except Exception as exc:
            raise ObjectStoreError(f"object_upload_failed:{type(exc).__name__}") from None
        if stored.get("Metadata",{}).get("sha256")!=actual or int(stored.get("ContentLength",-1))!=path.stat().st_size:
            raise ObjectStoreError("uploaded_object_integrity_verification_failed")
        return {"status":"UPLOADED","bucket":self.bucket,"key":key,"sha256":actual,
            "bytes":path.stat().st_size,"version_id":stored.get("VersionId"),
            "approval_ref":approval_ref,"credentials_emitted":False}

    def download_file(self,key:str,masterbot_id:int,authorization_ref:str,
                      expected_sha256:str,destination:str|Path)->dict[str,Any]:
        schema_name(masterbot_id)
        if not authorization_ref.strip(): raise ObjectStoreError("object_read_authorization_ref_required")
        if not HASH.fullmatch(expected_sha256): raise ObjectStoreError("expected_sha256_invalid")
        self._validate_key(key,masterbot_id)
        self._validate_bucket_controls()
        try:
            metadata=self.client.head_object(Bucket=self.bucket,Key=key)
            if metadata.get("Metadata",{}).get("sha256")!=expected_sha256:
                raise ObjectStoreError("remote_object_metadata_hash_mismatch")
            target=Path(destination);target.parent.mkdir(parents=True,exist_ok=True)
            self.client.download_file(self.bucket,key,str(target))
        except ObjectStoreError: raise
        except Exception as exc: raise ObjectStoreError(f"object_download_failed:{type(exc).__name__}") from None
        actual=_file_sha256(target)
        if actual!=expected_sha256:
            target.unlink(missing_ok=True)
            raise ObjectStoreError("downloaded_object_sha256_mismatch")
        return {"status":"DOWNLOADED_VERIFIED","bucket":self.bucket,"key":key,
            "sha256":actual,"bytes":target.stat().st_size,"authorization_ref":authorization_ref,
            "credentials_emitted":False}
