"""Persistent, content-addressed dataset registry with rights and quality gates.

The hub stores only local files explicitly submitted by an operator. Discovery
metadata never authorizes ingestion or training. SQLite and content-addressed
objects provide durable local storage; production shared storage is an adapter.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HOME = Path(os.environ.get("DREAMCO_DATASET_HOME", ROOT / ".dreamco" / "dataset-hub"))
ALLOWED_PLANES = {"dreamco_owned_training", "licensed_training", "user_contributed_opt_in_training", "evaluation_only_holdout", "public_reference_and_retrieval"}
TRAINING_PLANES = {"dreamco_owned_training", "licensed_training", "user_contributed_opt_in_training"}
PII_PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "us_phone": re.compile(r"(?<!\d)(?:\+1[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\d)"),
    "ssn": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
}

class DatasetPolicyError(ValueError):
    """A dataset violates a required provenance, rights, or training gate."""

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _quality(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    rows = 0
    duplicates = 0
    empty_rows = 0
    pii_hits = {name: 0 for name in PII_PATTERNS}
    seen: set[str] = set()
    if suffix == ".jsonl":
        iterator = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        for row in iterator:
            if not isinstance(row, (dict, list, str, int, float, bool)):
                raise DatasetPolicyError("Unsupported JSONL row type")
            normalized = json.dumps(row, sort_keys=True, ensure_ascii=False)
            rows += 1
            if not normalized.strip() or normalized in seen: duplicates += 1
            if not normalized.strip(): empty_rows += 1
            seen.add(normalized)
            for kind, pattern in PII_PATTERNS.items():
                pii_hits[kind] += len(pattern.findall(normalized))
    elif suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise DatasetPolicyError("CSV requires a header row")
            for row in reader:
                normalized = json.dumps(row, sort_keys=True, ensure_ascii=False)
                rows += 1
                if normalized in seen: duplicates += 1
                if not any(str(v or "").strip() for v in row.values()): empty_rows += 1
                seen.add(normalized)
                for kind, pattern in PII_PATTERNS.items():
                    pii_hits[kind] += len(pattern.findall(normalized))
    else:
        raise DatasetPolicyError("Only CSV and JSONL are supported by the first ingestion adapter")
    return {
        "format": suffix.lstrip("."), "row_count": rows, "duplicate_rows": duplicates,
        "empty_rows": empty_rows, "pii_pattern_hits": pii_hits,
        "pii_review_required": any(pii_hits.values()),
        "duplicate_rate": round(duplicates / rows, 6) if rows else 0.0,
        "quality_status": "REVIEW_REQUIRED" if not rows or duplicates or any(pii_hits.values()) else "STRUCTURE_CHECKS_PASSED",
        "limitations": ["Pattern scan is not a complete privacy classifier", "Schema semantics and label correctness require domain review"]
    }

class DatasetHub:
    def __init__(self, home: str | Path | None = None):
        self.home = Path(home) if home else DEFAULT_HOME
        self.objects = self.home / "objects"
        self.cards = self.home / "cards"
        self.db_path = self.home / "catalog.sqlite3"
        self.objects.mkdir(parents=True, exist_ok=True)
        self.cards.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS datasets (
                dataset_id TEXT NOT NULL, version INTEGER NOT NULL, name TEXT NOT NULL,
                owner TEXT NOT NULL, license TEXT NOT NULL, license_url TEXT NOT NULL,
                source_url TEXT NOT NULL, data_plane TEXT NOT NULL, rights_status TEXT NOT NULL,
                training_approved INTEGER NOT NULL, holdout INTEGER NOT NULL,
                content_sha256 TEXT, object_path TEXT, card_path TEXT NOT NULL,
                quality_json TEXT, created_at TEXT NOT NULL,
                PRIMARY KEY(dataset_id, version))""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_dataset_sha ON datasets(content_sha256)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_dataset_name ON datasets(name)")
            db.execute("""CREATE TABLE IF NOT EXISTS research_tasks (
                task_id TEXT PRIMARY KEY, problem TEXT NOT NULL, status TEXT NOT NULL,
                payload_json TEXT NOT NULL, created_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS external_candidates (
                candidate_key TEXT NOT NULL, masterbot_id INTEGER NOT NULL,
                source TEXT NOT NULL, source_id TEXT NOT NULL, url TEXT NOT NULL,
                name TEXT, license TEXT, rights_status TEXT NOT NULL,
                metadata_json TEXT NOT NULL, query TEXT NOT NULL,
                first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL,
                PRIMARY KEY(candidate_key, masterbot_id))""")
            db.execute("CREATE INDEX IF NOT EXISTS idx_external_candidate_source ON external_candidates(source, source_id)")

    def _connect(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    def register(self, card: dict[str, Any], source_file: str | Path | None = None) -> dict[str, Any]:
        required = ("name", "owner", "license", "license_url", "source_url", "data_plane", "rights_status")
        missing = [key for key in required if not str(card.get(key, "")).strip()]
        if missing:
            raise DatasetPolicyError("Missing dataset card fields: " + ", ".join(missing))
        from urllib.parse import urlparse
        for field in ("license_url", "source_url"):
            parsed = urlparse(str(card[field]))
            if parsed.scheme != "https" or not parsed.netloc:
                raise DatasetPolicyError(f"{field} must be an HTTPS URL")
        plane = str(card["data_plane"])
        if plane not in ALLOWED_PLANES:
            raise DatasetPolicyError("Unknown data plane")
        if card.get("holdout") and plane != "evaluation_only_holdout":
            raise DatasetPolicyError("Holdout datasets must use evaluation_only_holdout")
        approved = card.get("training_approved") is True
        if approved and (plane not in TRAINING_PLANES or card["rights_status"] != "VERIFIED"):
            raise DatasetPolicyError("Training requires verified rights and a training-eligible data plane")
        if approved and not str(card.get("rights_evidence", "")).strip():
            raise DatasetPolicyError("Training approval requires a rights-evidence reference")
        if approved:
            registry = json.loads((ROOT / "config/masterbot-75-registry.json").read_text(encoding="utf-8"))
            valid_ids = {int(item["id"]) for item in registry.get("divisions", [])}
            primary = card.get("primary_masterbot_id")
            collaborators = card.get("collaborating_masterbot_ids", [])
            if primary not in valid_ids or any(int(item) not in valid_ids for item in collaborators):
                raise DatasetPolicyError("Training datasets require a canonical primary MasterBot owner and valid collaborators")
            splits = card.get("split_manifest") or {}
            import re as _re
            for split_name in ("train_sha256", "validation_sha256", "test_sha256"):
                if not _re.fullmatch(r"[0-9a-f]{64}", str(splits.get(split_name, ""))):
                    raise DatasetPolicyError("Training approval requires pinned train, validation, and isolated test split hashes")
        content_hash = None
        object_path = None
        quality = None
        if source_file is not None:
            if not approved:
                raise DatasetPolicyError("File ingestion is disabled until an operator explicitly verifies rights and approves training")
            source = Path(source_file).expanduser().resolve()
            if not source.is_file():
                raise DatasetPolicyError("Source file does not exist")
            quality = _quality(source)
            content_hash = sha256_file(source)
            suffix = source.suffix.lower()
            if quality["row_count"] == 0 or quality["pii_review_required"] or quality["duplicate_rate"] > float(card.get("max_duplicate_rate", 0.01)):
                raise DatasetPolicyError("Quality gate failed; source was not added to the approved object store")
            target = self.objects / f"{content_hash}{suffix}"
            if not target.exists():
                temp = target.with_suffix(target.suffix + ".tmp")
                shutil.copyfile(source, temp)
                temp.replace(target)
            object_path = str(target.relative_to(self.home))
        dataset_id = str(card.get("dataset_id") or "dset-" + uuid.uuid4().hex[:16])
        if not re.fullmatch(r"[A-Za-z0-9._-]{3,100}", dataset_id):
            raise DatasetPolicyError("Dataset ID contains unsupported path characters")
        with self._connect() as db:
            prior = db.execute("SELECT MAX(version) AS v FROM datasets WHERE dataset_id=?", (dataset_id,)).fetchone()
            version = int(prior["v"] or 0) + 1
            card_doc = {
                **card, "dataset_id": dataset_id, "version": version,
                "content_sha256": content_hash, "object_path": object_path,
                "quality": quality, "created_at": utcnow(),
                "training_status": "APPROVED_PENDING_TRAINING" if approved else "NOT_APPROVED",
            }
            card_path = self.cards / f"{dataset_id}.v{version}.json"
            card_path.write_text(json.dumps(card_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            db.execute("""INSERT INTO datasets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                dataset_id, version, str(card["name"]), str(card["owner"]), str(card["license"]),
                str(card["license_url"]), str(card["source_url"]), plane, str(card["rights_status"]),
                int(approved), int(bool(card.get("holdout"))), content_hash, object_path,
                str(card_path.relative_to(self.home)), json.dumps(quality), card_doc["created_at"]))
        return card_doc

    def search(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        terms = [x for x in re.findall(r"[a-z0-9_-]+", query.lower()) if len(x) > 1]
        with self._connect() as db:
            rows = db.execute("SELECT * FROM datasets ORDER BY created_at DESC LIMIT 500").fetchall()
        found = []
        for row in rows:
            haystack = " ".join((row["name"], row["owner"], row["license"], row["source_url"], row["data_plane"])).lower()
            score = sum(1 for term in terms if term in haystack)
            if score or not terms:
                found.append({"dataset_id": row["dataset_id"], "version": row["version"], "name": row["name"], "owner": row["owner"], "license": row["license"], "source_url": row["source_url"], "data_plane": row["data_plane"], "rights_status": row["rights_status"], "training_approved": bool(row["training_approved"]), "holdout": bool(row["holdout"]), "content_sha256": row["content_sha256"], "score": score, "card_path": row["card_path"]})
        return sorted(found, key=lambda x: (x["score"], x["training_approved"]), reverse=True)[:max(1, min(limit, 100))]

    def get(self, dataset_id: str, version: int | None = None) -> dict[str, Any] | None:
        with self._connect() as db:
            if version is None:
                row = db.execute("SELECT * FROM datasets WHERE dataset_id=? ORDER BY version DESC LIMIT 1", (dataset_id,)).fetchone()
            else:
                row = db.execute("SELECT * FROM datasets WHERE dataset_id=? AND version=?", (dataset_id, version)).fetchone()
        if row is None:
            return None
        return json.loads((self.home / row["card_path"]).read_text(encoding="utf-8"))

    def record_external_candidate(self, candidate: dict[str, Any], masterbot_id: int, query: str) -> str:
        from urllib.parse import urlparse
        registry = json.loads((ROOT / "config/masterbot-75-registry.json").read_text(encoding="utf-8"))
        valid_masterbots = {int(item["id"]) for item in registry.get("divisions", [])}
        if int(masterbot_id) not in valid_masterbots:
            raise DatasetPolicyError("External candidates must route to a canonical MasterBot ID")
        source = str(candidate.get("source", "")).strip()
        source_id = str(candidate.get("id", "")).strip()
        url = str(candidate.get("url", "")).strip()
        parsed = urlparse(url)
        if not source or not source_id or parsed.scheme != "https" or not parsed.netloc:
            raise DatasetPolicyError("External candidates require a source ID and HTTPS URL")
        key = hashlib.sha256(f"{source}:{source_id}".encode("utf-8")).hexdigest()
        now = utcnow()
        safe = {k: v for k, v in candidate.items() if k not in {"content", "token", "authorization"}}
        with self._connect() as db:
            db.execute("""INSERT INTO external_candidates
                (candidate_key,masterbot_id,source,source_id,url,name,license,rights_status,metadata_json,query,first_seen_at,last_seen_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(candidate_key,masterbot_id) DO UPDATE SET
                name=excluded.name,license=excluded.license,rights_status=excluded.rights_status,
                metadata_json=excluded.metadata_json,query=excluded.query,last_seen_at=excluded.last_seen_at""",
                (key,int(masterbot_id),source,source_id,url,str(candidate.get("name") or candidate.get("id") or ""),
                 str(candidate.get("license") or ""),str(candidate.get("rights_status") or "UNVERIFIED"),
                 json.dumps(safe,ensure_ascii=False),str(query),now,now))
        return key

    def external_candidates(self, masterbot_id: int | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as db:
            if masterbot_id is None:
                rows = db.execute("SELECT * FROM external_candidates ORDER BY last_seen_at DESC LIMIT ?",
                    (max(1,min(limit,500)),)).fetchall()
            else:
                rows = db.execute("SELECT * FROM external_candidates WHERE masterbot_id=? ORDER BY last_seen_at DESC LIMIT ?",
                    (int(masterbot_id),max(1,min(limit,500)))).fetchall()
        return [{**dict(row),"metadata":json.loads(row["metadata_json"])} for row in rows]

    def enqueue_research_task(self, payload: dict[str, Any]) -> str:
        task_id = "research-" + uuid.uuid4().hex[:16]
        created = utcnow()
        with self._connect() as db:
            db.execute("INSERT INTO research_tasks VALUES (?,?,?,?,?)",
                (task_id, str(payload.get("problem", "")), "OPEN", json.dumps(payload, ensure_ascii=False), created))
        return task_id

    def research_tasks(self, status: str = "OPEN", limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM research_tasks WHERE status=? ORDER BY created_at DESC LIMIT ?",
                (status, max(1, min(limit, 200)))).fetchall()
        return [{"task_id": row["task_id"], "problem": row["problem"], "status": row["status"],
            "created_at": row["created_at"], "route": json.loads(row["payload_json"])} for row in rows]

    def _external_candidate_count(self) -> int:
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM external_candidates").fetchone()[0])

    def stats(self) -> dict[str, Any]:
        with self._connect() as db:
            rows = db.execute("SELECT COUNT(*) AS versions, COUNT(DISTINCT dataset_id) AS datasets, SUM(training_approved) AS approved, SUM(holdout) AS holdouts FROM datasets").fetchone()
            tasks = db.execute("SELECT COUNT(*) AS pending FROM research_tasks WHERE status='OPEN'").fetchone()
        return {"dataset_versions": rows["versions"], "datasets": rows["datasets"], "training_approved_versions": rows["approved"] or 0, "holdout_versions": rows["holdouts"] or 0, "pending_research_tasks": tasks["pending"], "external_discovery_routes": self._external_candidate_count(), "storage": str(self.home)}
