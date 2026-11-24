"""Fail-closed S3-compatible storage health and backup/restore evidence.

This adapter inspects existing buckets only. It never creates buckets, changes
bucket policies, or uploads user datasets. Live canaries require an explicit
opt-in and write only tiny generated objects beneath the health-check prefix.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

class ObjectStoreError(RuntimeError):
    """Object storage is not configured or a required check failed."""

BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
PREFIX_RE = re.compile(r"^[A-Za-z0-9/_-]{1,120}$")
ENCRYPTION_ALGORITHMS = {"AES256", "aws:kms", "aws:kms:dsse"}


def _valid_bucket_name(value: str) -> bool:
    if not BUCKET_RE.fullmatch(value) or ".." in value:
        return False
    labels = value.split(".")
    if any(not label or label.startswith("-") or label.endswith("-") for label in labels):
        return False
    if len(labels) == 4 and all(label.isdigit() for label in labels):
        return False
    return True


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _client_from_env() -> Any:
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise ObjectStoreError("install_boto3_to_use_s3_object_storage") from exc

    endpoint = os.environ.get("DREAMCO_OBJECT_STORE_ENDPOINT_URL", "").strip()
    if endpoint:
        parsed = urlsplit(endpoint)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ObjectStoreError("object_store_endpoint_must_be_trusted_https_url")
    return boto3.client(
        "s3",
        region_name=os.environ.get("DREAMCO_OBJECT_STORE_REGION", "us-east-1"),
        endpoint_url=endpoint or None,
        config=Config(s3={"addressing_style": "path"}),
    )


def _classification(bucket: str, client: Any) -> dict[str, Any]:
    try:
        versioning = client.get_bucket_versioning(Bucket=bucket)
    except Exception as exc:
        raise ObjectStoreError("bucket_versioning_inspection_failed") from None

    try:
        encryption = client.get_bucket_encryption(Bucket=bucket)
    except Exception as exc:
        code = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if code in {
            "ServerSideEncryptionConfigurationNotFoundError",
            "NoSuchServerSideEncryptionConfiguration",
        }:
            encryption = {}
        else:
            raise ObjectStoreError("bucket_encryption_inspection_failed") from None

    try:
        public = client.get_public_access_block(Bucket=bucket)
    except Exception as exc:
        code = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if code in {"NoSuchPublicAccessBlockConfiguration", "NoSuchPublicAccessBlock"}:
            public = {}
        else:
            raise ObjectStoreError("bucket_public_access_inspection_failed") from None

    try:
        lifecycle = client.get_bucket_lifecycle_configuration(Bucket=bucket)
    except Exception as exc:
        code = getattr(exc, "response", {}).get("Error", {}).get("Code")
        if code in {"NoSuchLifecycleConfiguration", "NoSuchLifecycle"}:
            lifecycle = {}
        else:
            raise ObjectStoreError("bucket_lifecycle_inspection_failed") from None

    algorithms = []
    for rule in encryption.get("ServerSideEncryptionConfiguration", {}).get("Rules", []):
        default = rule.get("ApplyServerSideEncryptionByDefault") or {}
        algorithms.append(default.get("SSEAlgorithm"))

    block = public.get("PublicAccessBlockConfiguration") or {}
    public_access_blocked = all(
        block.get(key) is True
        for key in (
            "BlockPublicAcls",
            "IgnorePublicAcls",
            "BlockPublicPolicy",
            "RestrictPublicBuckets",
        )
    )

    retention_days = []
    for rule in lifecycle.get("Rules", []):
        expiration = rule.get("Expiration") or {}
        noncurrent = rule.get("NoncurrentVersionExpiration") or {}
        days = expiration.get("Days") or noncurrent.get("NoncurrentDays")
        if isinstance(days, int) and not isinstance(days, bool) and days > 0:
            retention_days.append(days)

    return {
        "versioning_enabled": versioning.get("Status") == "Enabled",
        "encryption_at_rest": bool(algorithms)
        and all(value in ENCRYPTION_ALGORITHMS for value in algorithms),
        "encryption_algorithms": algorithms,
        "public_access_blocked": public_access_blocked,
        "retention_days": min(retention_days) if retention_days else None,
    }


def _read_body(response: dict[str, Any]) -> bytes:
    body = response["Body"]
    try:
        return body.read()
    finally:
        close = getattr(body, "close", None)
        if callable(close):
            close()


def _verify_object_encryption(client: Any, bucket: str, key: str) -> dict[str, Any]:
    head = client.head_object(Bucket=bucket, Key=key)
    algorithm = head.get("ServerSideEncryption")
    if algorithm not in ENCRYPTION_ALGORITHMS:
        raise ObjectStoreError("canary_object_encryption_not_verified")
    return head


def run_object_store_healthcheck(
    *,
    client: Any = None,
    allow_canary: bool = False,
    primary_bucket: str | None = None,
    backup_bucket: str | None = None,
    prefix: str | None = None,
) -> dict[str, Any]:
    """Inspect two buckets; optionally prove a generated cross-bucket restore."""
    primary_value = primary_bucket if primary_bucket is not None else os.environ.get("DREAMCO_OBJECT_STORE_BUCKET", "")
    backup_value = backup_bucket if backup_bucket is not None else os.environ.get("DREAMCO_OBJECT_STORE_BACKUP_BUCKET", "")
    prefix_value = (
        prefix if prefix is not None
        else os.environ.get("DREAMCO_OBJECT_STORE_HEALTHCHECK_PREFIX", "dreamco/healthchecks")
    )
    if not all(isinstance(value, str) for value in (primary_value, backup_value, prefix_value)):
        raise ObjectStoreError("bucket_names_and_prefix_must_be_strings")
    primary = primary_value.strip()
    backup = backup_value.strip()
    key_prefix = prefix_value.strip()

    if not _valid_bucket_name(primary) or not _valid_bucket_name(backup) or primary == backup:
        raise ObjectStoreError("distinct_valid_primary_and_backup_buckets_are_required")
    if not PREFIX_RE.fullmatch(key_prefix):
        raise ObjectStoreError("object_store_healthcheck_prefix_is_invalid")
    if not isinstance(allow_canary, bool):
        raise ObjectStoreError("allow_canary_must_be_boolean")

    if client is None:
        client = _client_from_env()

    primary_config = _classification(primary, client)
    backup_config = _classification(backup, client)
    required = ("versioning_enabled", "encryption_at_rest", "public_access_blocked")
    security_ok = all(primary_config[key] and backup_config[key] for key in required)
    retention = backup_config["retention_days"]

    base = {
        "schema": "dreamco.object_store_health_evidence.v1",
        "observed_at": _now(),
        "primary_bucket": primary,
        "backup_bucket": backup,
        "primary": primary_config,
        "backup": backup_config,
        "retention_days": retention,
        "encryption_at_rest": bool(
            primary_config["encryption_at_rest"] and backup_config["encryption_at_rest"]
        ),
        "versioning_enabled": bool(
            primary_config["versioning_enabled"] and backup_config["versioning_enabled"]
        ),
        "public_access_blocked": bool(
            primary_config["public_access_blocked"] and backup_config["public_access_blocked"]
        ),
        "credentials_emitted": False,
        "canary_payload_contains_secrets": False,
    }

    if not security_ok or not isinstance(retention, int) or isinstance(retention, bool) or retention <= 0:
        return {
            **base,
            "status": "BLOCKED",
            "backup_restore_test": "NOT_RUN",
            "blocker": "bucket_security_or_backup_retention_configuration_incomplete",
        }

    canary_enabled = allow_canary or os.environ.get("DREAMCO_ALLOW_OBJECT_STORE_CANARY") == "1"
    if not canary_enabled:
        return {
            **base,
            "status": "CONFIGURED_NOT_VALIDATED",
            "backup_restore_test": "NOT_RUN",
            "blocker": "explicit_canary_opt_in_required",
        }

    run_id = uuid.uuid4().hex
    primary_key = f"{key_prefix}/primary/{run_id}.json"
    backup_key = f"{key_prefix}/backup/{run_id}.json"
    restore_key = f"{key_prefix}/restore/{run_id}.json"
    payload = json.dumps(
        {"schema": "dreamco.object_store_canary.v1", "run_id": run_id, "created_at": _now()},
        separators=(",", ":"),
    ).encode("utf-8")

    try:
        primary_put = client.put_object(Bucket=primary, Key=primary_key, Body=payload)
        primary_version = primary_put.get("VersionId")
        if not primary_version:
            raise ObjectStoreError("primary_canary_version_id_missing")
        primary_head = _verify_object_encryption(client, primary, primary_key)
        if _read_body(client.get_object(Bucket=primary, Key=primary_key)) != payload:
            raise ObjectStoreError("primary_canary_readback_mismatch")

        source = {"Bucket": primary, "Key": primary_key, "VersionId": primary_version}
        backup_put = client.copy_object(Bucket=backup, Key=backup_key, CopySource=source)
        backup_version = backup_put.get("VersionId")
        if not backup_version:
            raise ObjectStoreError("backup_canary_version_id_missing")
        backup_head = _verify_object_encryption(client, backup, backup_key)
        if _read_body(client.get_object(Bucket=backup, Key=backup_key, VersionId=backup_version)) != payload:
            raise ObjectStoreError("backup_canary_readback_mismatch")

        restore_source = {"Bucket": backup, "Key": backup_key, "VersionId": backup_version}
        restore_put = client.copy_object(Bucket=primary, Key=restore_key, CopySource=restore_source)
        restore_version = restore_put.get("VersionId")
        if not restore_version:
            raise ObjectStoreError("restore_canary_version_id_missing")
        restore_head = _verify_object_encryption(client, primary, restore_key)
        if _read_body(client.get_object(Bucket=primary, Key=restore_key, VersionId=restore_version)) != payload:
            raise ObjectStoreError("restore_canary_readback_mismatch")
    except ObjectStoreError:
        raise
    except Exception as exc:
        raise ObjectStoreError(f"object_store_canary_failed_{type(exc).__name__}") from None

    return {
        **base,
        "status": "HEALTHY",
        "backup_restore_test": "PASS",
        "primary_canary_key": primary_key,
        "backup_canary_key": backup_key,
        "restore_canary_key": restore_key,
        "primary_version_id": primary_version,
        "backup_version_id": backup_version,
        "restore_version_id": restore_version,
        "primary_object_encryption": primary_head.get("ServerSideEncryption"),
        "backup_object_encryption": backup_head.get("ServerSideEncryption"),
        "restore_object_encryption": restore_head.get("ServerSideEncryption"),
        "note": (
            "Generated cross-bucket canary copy and restore passed. This is not a full "
            "disaster-recovery exercise or proof of cross-account/cross-region resilience."
        ),
    }


def run_division_object_store_healthcheck(masterbot_id: int, **kwargs: Any) -> dict[str, Any]:
    """Run the same isolated canary under a canonical division key prefix."""
    if isinstance(masterbot_id, bool) or not isinstance(masterbot_id, int) or not 1 <= masterbot_id <= 65:
        raise ObjectStoreError("masterbot_id_must_be_between_1_and_65")
    prefix = kwargs.pop("prefix", None) or os.environ.get(
        "DREAMCO_OBJECT_STORE_HEALTHCHECK_PREFIX", "dreamco/healthchecks"
    )
    evidence = run_object_store_healthcheck(
        prefix=f"{prefix}/divisions/{masterbot_id:03d}", **kwargs
    )
    evidence["masterbot_id"] = masterbot_id
    return evidence
