"""Rights-scoped dataset study and evidence-backed Buddy research positions."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


SCOPES = {
    "private_study",
    "private_retrieval_for_this_user",
    "private_training_for_this_users_buddy",
    "shared_fleet_training",
    "publish_or_export",
    "commercial_redistribution",
}
STANCE = {"supports", "challenges", "context"}
SENSITIVE_COLUMN = re.compile(r"(^|_)(email|phone|mobile|ssn|social_security|password|token|secret|address|birthdate|date_of_birth|medical|diagnosis|health_record)(_|$)", re.I)
SAMPLE_RISK_PATTERNS = {
    "email_like_values": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "credential_like_values": re.compile(r"(?i)(?:api[_ -]?key|access[_ -]?token|secret[_ -]?key|password|token)\s*[:=]\s*[^\s,;]{6,}|\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,})\b"),
    "ssn_like_values": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "card_like_values": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "phone_like_values": re.compile(r"(?<!\w)(?:\+?\d[ .()/-]*){9,15}(?!\w)"),
    "active_content_markers": re.compile(r"(?i)<\s*script\b|javascript\s*:|\bonerror\s*=|<\s*iframe\b"),
    "instruction_injection_markers": re.compile(r"(?i)\b(ignore (?:all )?(?:previous|prior) instructions|reveal (?:the )?(?:system prompt|secrets)|developer message|system prompt)\b"),
}


class DataStudyError(ValueError):
    """Raised when rights evidence or research provenance is incomplete."""


def _fetch_hf_dataset_info(url: str, timeout_seconds: int = 10) -> dict[str, Any]:
    class HuggingFaceRedirectGuard(HTTPRedirectHandler):
        def redirect_request(self, request, file_pointer, code, message, headers, new_url):
            target = urlsplit(new_url)
            if target.scheme != "https" or target.hostname != "huggingface.co":
                raise DataStudyError("Hugging Face metadata redirect left the approved HTTPS host.")
            return super().redirect_request(request, file_pointer, code, message, headers, new_url)

    request = Request(url, headers={"Accept": "application/json", "User-Agent": "DreamCo-Buddy-Dataset-Study/1.0"})
    try:
        opener = build_opener(HuggingFaceRedirectGuard())
        with opener.open(request, timeout=timeout_seconds) as response:
            if urlsplit(response.geturl()).hostname != "huggingface.co":
                raise DataStudyError("Hugging Face metadata lookup redirected outside the approved host.")
            raw = response.read(2_000_001)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise DataStudyError(f"Hugging Face metadata lookup failed: {type(error).__name__}.") from error
    if len(raw) > 2_000_000:
        raise DataStudyError("Dataset metadata response exceeds the configured limit.")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise DataStudyError("Hugging Face returned invalid dataset metadata.") from error
    if not isinstance(payload, dict):
        raise DataStudyError("Hugging Face dataset metadata must be an object.")
    return payload


def discover_huggingface_dataset(repo_id: str, revision: str,
                                 fetch_json: Any = _fetch_hf_dataset_info) -> dict[str, Any]:
    """Fetch public HF metadata and freeze the returned SHA; never downloads dataset files."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}/[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", repo_id):
        raise DataStudyError("Use a Hugging Face dataset ID in namespace/name form.")
    if (not isinstance(revision, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,120}", revision)
            or ".." in revision.split("/")):
        raise DataStudyError("Use a valid Hugging Face dataset branch, tag, or commit reference.")
    url = f"https://huggingface.co/api/datasets/{quote(repo_id, safe='/')}/revision/{quote(revision, safe='/')}"
    payload = fetch_json(url)
    if payload.get("private") is True or payload.get("gated") not in (False, None):
        raise DataStudyError("Private or gated datasets need a separately reviewed access and permission flow.")
    resolved_sha = str(payload.get("sha", "")).lower()
    if not re.fullmatch(r"[a-f0-9]{40}", resolved_sha):
        raise DataStudyError("Hugging Face did not return a full immutable dataset commit SHA.")
    card_data = payload.get("cardData") if isinstance(payload.get("cardData"), dict) else {}
    siblings = payload.get("siblings", [])
    if not isinstance(siblings, list) or len(siblings) > 5_000:
        raise DataStudyError("Dataset file inventory is missing or exceeds the configured limit.")
    files = []
    for item in siblings:
        if not isinstance(item, dict):
            continue
        name = str(item.get("rfilename", ""))
        if not name or name.startswith("/") or ".." in Path(name).parts or "\\" in name:
            continue
        suffix = Path(name).suffix.lower()
        files.append({"path": name, "format": suffix.lstrip("."), "study_supported": suffix in {".csv", ".jsonl", ".ndjson"}})
    return {
        "schema": "dreamco.huggingface_dataset_discovery.v1",
        "source": {"repo_id": repo_id, "url": f"https://huggingface.co/datasets/{repo_id}", "requested_revision": revision, "revision": resolved_sha},
        "metadata": {
            "license_id": str(card_data.get("license", "unknown")),
            "license_review_status": "review_required",
            "description": str(payload.get("description", ""))[:1_000],
            "description_is_untrusted_external_content": True,
            "tags": [str(tag)[:100] for tag in payload.get("tags", [])[:100]] if isinstance(payload.get("tags", []), list) else [],
        },
        "files": files,
        "file_count": len(files),
        "data_downloaded": False,
        "training_authorized": False,
        "rights_review_required": True,
        "external_metadata_is_untrusted": True,
        "metadata_grants_no_permissions": True,
        "next_step": "Review this exact revision's dataset card, license, terms, provenance, and sensitive-data scope before granting private_study; obtain approved files separately for local CSV/JSONL analysis.",
    }


def _fetch_hf_viewer_json(url: str, timeout_seconds: int = 10) -> dict[str, Any]:
    """Read bounded JSON from the public HF Dataset Viewer; never fetch asset URLs."""
    class ViewerRedirectGuard(HTTPRedirectHandler):
        def redirect_request(self, request, file_pointer, code, message, headers, new_url):
            target = urlsplit(new_url)
            if target.scheme != "https" or target.hostname != "datasets-server.huggingface.co":
                raise DataStudyError("Dataset Viewer redirect left the approved HTTPS host.")
            return super().redirect_request(request, file_pointer, code, message, headers, new_url)

    if urlsplit(url).hostname != "datasets-server.huggingface.co" or urlsplit(url).scheme != "https":
        raise DataStudyError("Dataset Viewer requests must use its approved HTTPS host.")
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "DreamCo-Buddy-Dataset-Preview/1.0"})
    try:
        with build_opener(ViewerRedirectGuard()).open(request, timeout=timeout_seconds) as response:
            if urlsplit(response.geturl()).hostname != "datasets-server.huggingface.co":
                raise DataStudyError("Dataset Viewer lookup redirected outside the approved host.")
            raw = response.read(500_001)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise DataStudyError(f"Dataset Viewer preview failed: {type(error).__name__}.") from error
    if len(raw) > 500_000:
        raise DataStudyError("Dataset Viewer response exceeds the configured limit.")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise DataStudyError("Dataset Viewer returned invalid JSON.") from error
    if not isinstance(payload, dict):
        raise DataStudyError("Dataset Viewer response must be an object.")
    return payload


def preview_huggingface_dataset(discovery: dict[str, Any], config: str, split: str,
                                fetch_json: Any = _fetch_hf_viewer_json) -> dict[str, Any]:
    """Run a no-full-download preflight and schema preview for one public config/split.

    The Viewer API does not pin a preview request to the repository commit. The returned
    report states this limitation and never treats preview success as download approval.
    Raw sample values are inspected only as untrusted input and are not retained.
    """
    if discovery.get("schema") != "dreamco.huggingface_dataset_discovery.v1":
        raise DataStudyError("Run Hugging Face metadata discovery before requesting a preview.")
    repo_id = discovery.get("source", {}).get("repo_id", "")
    revision = discovery.get("source", {}).get("revision", "")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}/[A-Za-z0-9][A-Za-z0-9_.-]{0,95}", repo_id):
        raise DataStudyError("Discovery report has an invalid dataset ID.")
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise DataStudyError("Discovery report is not pinned to an immutable commit.")
    if not isinstance(config, str) or not config or len(config) > 200 or not isinstance(split, str) or not split or len(split) > 200:
        raise DataStudyError("Choose a valid dataset config and split from the preview list.")
    base = "https://datasets-server.huggingface.co"
    split_query = urlencode({"dataset": repo_id})
    split_data = fetch_json(f"{base}/splits?{split_query}")
    listed = split_data.get("splits", [])
    if not isinstance(listed, list) or len(listed) > 20_000:
        raise DataStudyError("Dataset Viewer returned an invalid or oversized split list.")
    if not any(item.get("config") == config and item.get("split") == split for item in listed if isinstance(item, dict)):
        raise DataStudyError("The selected config and split were not listed by the Dataset Viewer.")
    query = urlencode({"dataset": repo_id, "config": config, "split": split})
    sample = fetch_json(f"{base}/first-rows?{query}")
    features = sample.get("features", [])
    rows = sample.get("rows", [])
    if not isinstance(features, list) or len(features) > 300 or not isinstance(rows, list) or len(rows) > 100:
        raise DataStudyError("Dataset Viewer returned an invalid sample schema.")
    if any(not isinstance(item, dict) or not item.get("name") for item in features):
        raise DataStudyError("Dataset Viewer returned a malformed feature schema.")
    field_names = [str(item.get("name", ""))[:200] for item in features]
    if len(set(field_names)) != len(field_names):
        raise DataStudyError("Dataset Viewer returned duplicate field names.")
    sensitive_names = [name for name in field_names if SENSITIVE_COLUMN.search(name.lower().replace(" ", "_"))]
    # Inspect up to 100 untrusted rows in memory. Keep only aggregate findings.
    sample_rows = rows
    structure_issues = []
    sample_values = 0
    missing_values = 0
    duplicates = 0
    seen_rows: set[str] = set()
    observed_types: dict[str, set[str]] = {name: set() for name in field_names}
    risk_matches = {name: 0 for name in SAMPLE_RISK_PATTERNS}
    non_scalar_cells = 0
    for item in sample_rows:
        row = item.get("row", {}) if isinstance(item, dict) else None
        if not isinstance(row, dict) or set(map(str, row.keys())) != set(field_names):
            structure_issues.append("sample_rows_have_inconsistent_schema")
            break
        canonical = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if digest in seen_rows:
            duplicates += 1
        seen_rows.add(digest)
        for name in field_names:
            value = row.get(name)
            if value is None or value == "":
                missing_values += 1
                continue
            sample_values += 1
            if isinstance(value, bool):
                observed_types[name].add("boolean")
            elif isinstance(value, (int, float)):
                observed_types[name].add("numeric")
            elif isinstance(value, str):
                observed_types[name].add("text")
                for risk_name, pattern in SAMPLE_RISK_PATTERNS.items():
                    if pattern.search(value):
                        risk_matches[risk_name] += 1
            else:
                observed_types[name].add("structured")
                non_scalar_cells += 1
    scripts = [item["path"] for item in discovery.get("files", [])
               if Path(str(item.get("path", ""))).suffix.lower() in {".py", ".ipynb", ".sh"}]
    file_paths = [str(item.get("path", "")) for item in discovery.get("files", []) if isinstance(item, dict)]
    allowed_extensions = {".csv", ".jsonl", ".ndjson"}
    unsupported_files = [name for name in file_paths if Path(name).suffix.lower() not in allowed_extensions]
    empty_fields = [name for name, kinds in observed_types.items() if not kinds and sample_rows]
    mixed_type_fields = [name for name, kinds in observed_types.items() if len(kinds) > 1]
    risk_indicators = [name for name, count in risk_matches.items() if count]
    if non_scalar_cells:
        risk_indicators.append("structured_or_binary_sample_cells_need_format_specific_review")
    if duplicates:
        risk_indicators.append("duplicate_rows_in_preview")
    if missing_values:
        risk_indicators.append("missing_values_in_preview")
    if mixed_type_fields:
        risk_indicators.append("mixed_value_types_in_preview")
    if empty_fields:
        risk_indicators.append("all_empty_fields_in_preview")
    checks = {
        "immutable_source_revision_recorded": True,
        "preview_source_revision_pinned": False,
        "public_dataset_metadata_discovered": True,
        "license_and_terms_reviewed": discovery.get("metadata", {}).get("license_review_status") == "reviewed",
        "selected_config_and_split_verified": True,
        "sample_schema_consistent": not structure_issues,
        "sensitive_or_credential_like_fields_detected": bool(sensitive_names),
        "dataset_scripts_present": bool(scripts),
        "supported_local_tabular_files_available": any(file.get("study_supported") for file in discovery.get("files", [])),
        "unsupported_file_types_present": bool(unsupported_files),
        "sample_values_screened_for_common_risk_patterns": True,
        "sample_content_reviewed_by_user": False,
        "rights_to_download_confirmed": False,
    }
    blockers = []
    if sensitive_names:
        blockers.append("sensitive_or_credential_like_field_names_need_review")
    if scripts:
        blockers.append("dataset_contains_scripts_that_must_not_be_executed")
    if not checks["supported_local_tabular_files_available"]:
        blockers.append("no_supported_csv_or_jsonl_files_in_discovery")
    return {
        "schema": "dreamco.huggingface_dataset_preflight.v1",
        "source": {"repo_id": repo_id, "revision": revision, "preview_endpoint": "https://datasets-server.huggingface.co", "preview_is_commit_pinned": False},
        "selection": {"config": config, "split": split},
        "sample": {"rows_returned": len(sample_rows), "field_count": len(field_names), "fields": [
            {"name": name, "type": str(features[index].get("type", "unknown"))[:200] if index < len(features) and isinstance(features[index], dict) else "unknown"}
            for index, name in enumerate(field_names)
        ], "missing_values": missing_values, "duplicate_rows": duplicates,
            "mixed_type_fields": mixed_type_fields, "all_empty_fields": empty_fields,
            "raw_rows_retained": False, "raw_values_retained": False},
        "checks": checks,
        "sensitive_field_names": sensitive_names,
        "sample_risk_indicators": risk_indicators,
        "sample_risk_match_counts": risk_matches,
        "script_files": scripts,
        "unsupported_file_types": unsupported_files,
        "structure_issues": structure_issues,
        "blockers": blockers,
        "download_authorized": False,
        "training_authorized": False,
        "code_executed": False,
        "dataset_downloaded": False,
        "model_weights_changed": False,
        "assurance": "No scan can prove a dataset safe for all users, environments, or purposes. This report records bounded checks and findings; human rights, security, privacy, and task-specific review remain necessary.",
        "next_step": "Review the sample and exact commit locally; confirm the license, dataset terms, provenance, and download rights. Then use a separate explicit download approval and verify downloaded file hashes before local testing. Preview availability is not a safety or rights guarantee.",
    }


def study_local_tabular_dataset(path: Path, use_record: dict[str, Any], *, max_rows: int = 100_000,
                                max_bytes: int = 20_000_000) -> dict[str, Any]:
    """Profile local CSV/JSONL safely; never executes dataset content or returns raw cell values."""
    source = path.expanduser()
    if source.is_symlink() or not source.is_file():
        raise DataStudyError("Choose a regular local dataset file, not a symlink or directory.")
    resolved = source.resolve(strict=True)
    size = resolved.stat().st_size
    if size <= 0 or size > max_bytes:
        raise DataStudyError("Dataset must be between 1 byte and the configured size limit.")
    if use_record.get("decision") != "approved_for_selected_scopes" or "private_study" not in use_record.get("requested_scopes", []):
        raise DataStudyError("An approved private_study use record is required before reading the dataset.")
    digest = hashlib.sha256()
    with resolved.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    actual_digest = digest.hexdigest()
    if actual_digest != use_record.get("dataset_sha256", "").lower():
        raise DataStudyError("The local file hash does not match the rights-reviewed dataset record.")

    field_stats: dict[str, dict[str, Any]] = {}
    row_count = 0
    duplicate_count = 0
    row_hashes: set[str] = set()

    def consume(row: Any) -> None:
        nonlocal row_count, duplicate_count
        if not isinstance(row, dict):
            raise DataStudyError("Each tabular record must be a JSON object or CSV row.")
        if not field_stats:
            if not row or len(row) > 300:
                raise DataStudyError("Dataset must have between 1 and 300 fields.")
            if any(SENSITIVE_COLUMN.search(str(key).lower().replace(" ", "_")) for key in row):
                raise DataStudyError("Sensitive or credential-like column names require a separately approved analysis policy.")
            for key in row:
                field_stats[str(key)] = {"present": 0, "missing": 0, "types": Counter(), "distinct_hmacs": set()}
        if set(map(str, row.keys())) != set(field_stats):
            raise DataStudyError("Rows must have a consistent field schema.")
        canonical = json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        row_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if row_hash in row_hashes:
            duplicate_count += 1
        else:
            row_hashes.add(row_hash)
        row_count += 1
        for key, value in row.items():
            name = str(key)
            stat = field_stats[name]
            if value is None or (isinstance(value, str) and not value.strip()):
                stat["missing"] += 1
                continue
            stat["present"] += 1
            if isinstance(value, bool):
                kind = "boolean"
            elif isinstance(value, (int, float)):
                kind = "numeric"
            elif isinstance(value, str):
                try:
                    float(value)
                    kind = "numeric_text"
                except ValueError:
                    kind = "text"
            else:
                kind = "structured"
            stat["types"][kind] += 1
            fingerprint = hashlib.sha256(value if isinstance(value, bytes) else str(value).encode("utf-8")).hexdigest()
            if len(stat["distinct_hmacs"]) < 10_000:
                stat["distinct_hmacs"].add(fingerprint)
        if row_count > max_rows:
            raise DataStudyError("Dataset exceeds the configured row limit.")

    try:
        if resolved.suffix.lower() == ".csv":
            with resolved.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream, strict=True)
                if not reader.fieldnames or len(reader.fieldnames) > 300:
                    raise DataStudyError("CSV header is missing or has too many fields.")
                for row in reader:
                    consume(row)
        elif resolved.suffix.lower() in {".jsonl", ".ndjson"}:
            with resolved.open("r", encoding="utf-8") as stream:
                for line in stream:
                    if line.strip():
                        consume(json.loads(line))
        else:
            raise DataStudyError("Only CSV and JSONL are supported; executable and pickle-based formats are rejected.")
    except (UnicodeError, csv.Error, json.JSONDecodeError) as error:
        raise DataStudyError("Dataset is malformed or not valid UTF-8 text.") from error
    if not row_count:
        raise DataStudyError("Dataset contains no data rows.")
    final_digest = hashlib.sha256()
    with resolved.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            final_digest.update(chunk)
    if final_digest.hexdigest() != actual_digest:
        raise DataStudyError("Dataset changed during analysis; discard this result and retry.")
    quality_flags = []
    if row_count < 30:
        quality_flags.append("small_sample_for_generalization")
    missing_ratios = [values["missing"] / row_count for values in field_stats.values()]
    if any(value > 0 for value in missing_ratios):
        quality_flags.append("missing_values_present")
    if duplicate_count:
        quality_flags.append("duplicate_rows_present")
    return {
        "schema": "dreamco.local_dataset_study.v1",
        "dataset_sha256": actual_digest,
        "format": resolved.suffix.lower().lstrip("."),
        "size_bytes": size,
        "row_count": row_count,
        "field_count": len(field_stats),
        "duplicate_rows": duplicate_count,
        "quality_flags": quality_flags,
        "fields": {
            name: {
                "present": values["present"],
                "missing": values["missing"],
                "missing_ratio": round(values["missing"] / row_count, 4),
                "observed_types": dict(values["types"]),
                "distinct_values_lower_bound": len(values["distinct_hmacs"]),
            }
            for name, values in sorted(field_stats.items())
        },
        "raw_rows_in_report": False,
        "raw_values_in_report": False,
        "code_executed": False,
        "network_used": False,
        "model_weights_changed": False,
        "sensitive_columns_detected": False,
    }


def position_on_dataset_study(study: dict[str, Any], use_record: dict[str, Any]) -> dict[str, Any]:
    """Create a cautious Buddy position from safe aggregate study results, not raw examples."""
    if study.get("schema") != "dreamco.local_dataset_study.v1":
        raise DataStudyError("A completed local dataset study is required.")
    if use_record.get("decision") != "approved_for_selected_scopes" or "private_study" not in use_record.get("requested_scopes", []):
        raise DataStudyError("An approved private_study use record is required.")
    if study.get("dataset_sha256") != use_record.get("dataset_sha256"):
        raise DataStudyError("Study and rights record must refer to the same dataset digest.")
    flags = list(study.get("quality_flags", []))
    if flags:
        assessment = "Buddy's provisional view is to review this dataset before relying on it: " + ", ".join(flags) + "."
    else:
        assessment = "Buddy's provisional view is that this dataset passes basic structural checks; representativeness and task-specific value still need evaluation."
    assessment += " One dataset profile is not enough to establish a general conclusion or authorize model training."
    return {
        "schema": "dreamco.buddy_research_position.v1",
        "topic": "local dataset quality",
        "position_type": "evidence_based_hypothesis",
        "buddy_position": assessment,
        "status": "provisional",
        "confidence": 0.25 if flags else 0.35,
        "confidence_basis": {"independent_dataset_count": 1, "metrics": ["row_count", "missingness", "duplicate_rows", "field_types"], "quality_flags": flags},
        "source_evidence": [{
            "source_id": "dataset:" + study["dataset_sha256"][:20],
            "source_family": use_record["source"]["family"],
            "source_url": use_record["source"]["url"],
            "revision_or_retrieved_at": study["dataset_sha256"],
            "evidence_sha256": study["dataset_sha256"],
            "study_schema": study["schema"],
            "stance": "context",
            "rights_status": "reviewed",
        }],
        "limitations": ["This position covers basic structure only, not dataset semantics or representativeness.", "The view is provisional and should be compared with independent sources and task benchmarks.", "No raw dataset rows or values are included."],
        "needs_human_review": True,
        "model_weights_changed": False,
    }


def create_data_use_record(
    *, owner_user_id: str, buddy_instance_id: str, dataset_sha256: str,
    source_url: str, source_family: str, license_id: str,
    user_created: bool, rights_reviewed: bool, terms_checked: bool,
    requested_scopes: list[str], consent_scopes: list[str] = (),
    license_scopes: list[str] = (),
    consent_receipt_id: str = "", consent_revoked: bool = False,
    training_allowed_by_license: bool = False,
) -> dict[str, Any]:
    """Return a rights decision. User uploads remain theirs; scopes grant access, not ownership."""
    if not owner_user_id.strip() or not buddy_instance_id.strip():
        raise DataStudyError("User and Buddy workspace IDs are required.")
    if not re.fullmatch(r"[a-fA-F0-9]{64}", dataset_sha256):
        raise DataStudyError("A SHA-256 digest is required for the dataset version.")
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise DataStudyError("Use a credential-free HTTPS source reference.")
    if not source_family.strip() or not license_id.strip():
        raise DataStudyError("Record the dataset source family and license identifier.")
    requested = set(requested_scopes)
    consent = set(consent_scopes)
    license_permissions = set(license_scopes)
    if not requested <= SCOPES or not consent <= SCOPES or not license_permissions <= SCOPES:
        raise DataStudyError("A requested use scope is not supported.")
    reasons = []
    if not rights_reviewed or not terms_checked:
        reasons.append("source_rights_and_terms_review_required")
    if user_created and (not consent_receipt_id.strip() or consent_revoked):
        reasons.append("active_user_scope_consent_receipt_required")
    authorized_scopes = consent if user_created else license_permissions
    if requested - authorized_scopes:
        reasons.append("requested_scopes_exceed_explicit_consent" if user_created else "requested_scopes_exceed_verified_license")
    if consent_revoked:
        reasons.append("consent_revoked_future_use_blocked")
    training_scopes = {"private_training_for_this_users_buddy", "shared_fleet_training"}
    if requested & training_scopes and not training_allowed_by_license:
        reasons.append("training_not_allowed_or_not_verified_by_license")
    if "shared_fleet_training" in requested and not user_created and not training_allowed_by_license:
        reasons.append("external_data_not_cleared_for_shared_training")
    blocked = bool(reasons)
    return {
        "schema": "dreamco.dataset_use_record.v1",
        "dataset_sha256": dataset_sha256.lower(),
        "source": {"url": source_url, "family": source_family, "license": license_id, "rights_reviewed": rights_reviewed, "terms_checked": terms_checked},
        "user_workspace": {"owner_user_id": owner_user_id, "buddy_instance_id": buddy_instance_id, "isolated": True},
        "ownership": {
            "user_created_data_owner": owner_user_id if user_created else None,
            "third_party_rights_preserved": True,
            "ownership_transferred_to_dreamco": False,
            "buddy_access_is_scoped_permission": True,
            "shared_fleet_access": "shared_fleet_training" in requested and not blocked,
        },
        "requested_scopes": sorted(requested),
        "consent_receipt_id": consent_receipt_id if user_created else None,
        "decision": "approved_for_selected_scopes" if not blocked else "blocked",
        "reasons": reasons,
        "raw_dataset_copied_to_report": False,
        "raw_rows_logged": False,
        "automatic_weight_training": False,
    }


def build_buddy_position(topic: str, evidence: list[dict[str, Any]], position: str) -> dict[str, Any]:
    """Record a revisable position from sourced claims, preserving disagreement and uncertainty."""
    clean_topic = " ".join(topic.split())
    clean_position = " ".join(position.split())
    if len(clean_topic) < 3 or len(clean_position) < 30:
        raise DataStudyError("Provide a topic and an original Buddy position of at least 30 characters.")
    seen: set[str] = set()
    rows = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        source_id = str(item.get("source_id", "")).strip()
        family = str(item.get("source_family", "")).strip()
        url = str(item.get("source_url", "")).strip()
        stance = str(item.get("stance", "context")).strip().lower()
        digest = str(item.get("evidence_sha256", "")).strip().lower()
        parsed = urlsplit(url)
        if (not source_id or source_id in seen or not family or parsed.scheme != "https" or not parsed.netloc
                or parsed.username or parsed.password or stance not in STANCE
                or not re.fullmatch(r"[a-f0-9]{64}", digest)):
            continue
        seen.add(source_id)
        rows.append({
            "source_id": source_id,
            "source_family": family,
            "source_url": url,
            "revision_or_retrieved_at": str(item.get("revision_or_retrieved_at", ""))[:120],
            "evidence_sha256": digest,
            "stance": stance,
            "quality_score": max(0.0, min(1.0, float(item.get("quality_score", 0)))),
            "rights_status": str(item.get("rights_status", "unreviewed")),
        })
    if not rows:
        raise DataStudyError("Add at least one valid, versioned source evidence record.")
    counts = Counter(row["stance"] for row in rows)
    distinct_families = len({row["source_family"] for row in rows})
    average_quality = sum(row["quality_score"] for row in rows) / len(rows)
    coverage = min(1.0, len(rows) / 5)
    agreement = max(counts.get("supports", 0), counts.get("challenges", 0), counts.get("context", 0)) / len(rows)
    confidence = round(coverage * average_quality * agreement, 3)
    mature = len(rows) >= 3 and distinct_families >= 2 and all(row["rights_status"] == "reviewed" for row in rows)
    return {
        "schema": "dreamco.buddy_research_position.v1",
        "topic": clean_topic,
        "position_type": "evidence_based_hypothesis",
        "buddy_position": clean_position,
        "status": "provisional" if not mature else "reviewable",
        "confidence": confidence,
        "confidence_basis": {"source_count": len(rows), "independent_source_families": distinct_families, "average_source_quality": round(average_quality, 3), "stance_counts": dict(counts)},
        "supporting_source_ids": [row["source_id"] for row in rows if row["stance"] == "supports"],
        "challenging_source_ids": [row["source_id"] for row in rows if row["stance"] == "challenges"],
        "source_evidence": rows,
        "limitations": ["This is a revisable synthesis, not a personal feeling or verified fact.", "Evidence sources and disagreements remain visible.", "Dataset rows and source passages are not copied into this position record."],
        "needs_human_review": True,
        "model_weights_changed": False,
    }
