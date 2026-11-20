"""Explicitly authorized, read-only SQL dataset snapshots.

Every query requires a caller-provided authorization reference and an exact
SHA-256 allowlist hash. Credentials are read from environment variables only.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any

class DatabaseSourceError(ValueError):
    pass

def query_hash(sql: str, params: tuple = ()) -> str:
    normalized = " ".join(sql.split())
    payload = json.dumps({"sql": normalized, "params": params}, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def _validate(sql: str, params: tuple, authorization_ref: str, approved_query_sha256: str, limit: int) -> str:
    normalized = " ".join((sql or "").strip().split())
    if not authorization_ref.strip():
        raise DatabaseSourceError("An authorization reference is required")
    if not re.match(r"^(SELECT|WITH)\b", normalized, re.I):
        raise DatabaseSourceError("Only SELECT or read-only WITH queries are permitted")
    if ";" in normalized or re.search(r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|VACUUM|COPY|GRANT|REVOKE)\b", normalized, re.I):
        raise DatabaseSourceError("Multiple statements and write/administrative SQL are blocked")
    if not re.search(r"\bLIMIT\s+\d+\b", normalized, re.I):
        raise DatabaseSourceError("Queries must include an explicit LIMIT")
    found = re.search(r"\bLIMIT\s+(\d+)\b", normalized, re.I)
    if not found or int(found.group(1)) > max(1, min(limit, 1000)):
        raise DatabaseSourceError("Query LIMIT exceeds the configured row cap")
    if query_hash(normalized, params) != approved_query_sha256:
        raise DatabaseSourceError("Query hash is not in the caller's approved allowlist")
    return normalized

def snapshot_sqlite(db_path: str | Path, sql: str, params: tuple = (), *,
                    authorization_ref: str, approved_query_sha256: str,
                    output_path: str | Path, row_limit: int = 1000) -> dict[str, Any]:
    query = _validate(sql, params, authorization_ref, approved_query_sha256, row_limit)
    path = Path(db_path).resolve()
    if not path.is_file():
        raise DatabaseSourceError("SQLite source database not found")
    uri = path.as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        cursor = connection.execute(query, params)
        names = [column[0] for column in cursor.description or []]
        rows = cursor.fetchmany(row_limit)
    finally:
        connection.close()
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(zip(names, row)), ensure_ascii=False, default=str) + "\n")
    return {"rows_exported":len(rows),"columns":names,"authorization_ref":authorization_ref,
            "query_sha256":query_hash(query, params),"source_kind":"sqlite_read_only","output":str(out),
            "credentials_stored":False,"query_only":True}

def snapshot_postgres(sql: str, params: tuple = (), *, authorization_ref: str,
                      approved_query_sha256: str, output_path: str | Path,
                      row_limit: int = 1000) -> dict[str, Any]:
    query = _validate(sql, authorization_ref, approved_query_sha256, row_limit)
    dsn = os.environ.get("DREAMCO_POSTGRES_DSN")
    if not dsn:
        raise DatabaseSourceError("DREAMCO_POSTGRES_DSN is not configured")
    try:
        import psycopg
    except ImportError as exc:
        raise DatabaseSourceError("Install the optional psycopg package to enable PostgreSQL snapshots") from exc
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute(query, params)
            names = [column.name for column in cursor.description or []]
            rows = cursor.fetchmany(row_limit)
    with out.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(zip(names, row)), ensure_ascii=False, default=str) + "\n")
    return {"rows_exported":len(rows),"columns":names,"authorization_ref":authorization_ref,
            "query_sha256":query_hash(query),"source_kind":"postgres_read_only",
            "output":str(out),"credentials_stored":False,"query_only":True}
