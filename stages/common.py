"""Shared deterministic JSON and schema helpers with bounded path access."""
import argparse
import json
import hashlib
import os
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = Path(tempfile.gettempdir()).resolve()


def safe_stage_path(value):
    candidate = Path(value)
    candidate = (REPO_ROOT / candidate if not candidate.is_absolute() else candidate).resolve()
    allowed_roots = [REPO_ROOT]
    if not os.environ.get("GITHUB_ACTIONS") or os.environ.get("PYTEST_CURRENT_TEST"):
        allowed_roots.append(TEMP_ROOT)
    if not any(candidate == root or root in candidate.parents for root in allowed_roots):
        raise ValueError("Stage input/output path must remain inside the repository or an approved test temp directory.")
    return candidate


def read_json(path):
    source = safe_stage_path(path)
    if source.stat().st_size > 5 * 1024 * 1024:
        raise ValueError("Stage JSON input exceeds the 5 MiB safety limit.")
    return json.loads(source.read_text(encoding="utf-8"))


def write_json(path, value):
    target = safe_stage_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate(value, schema_name):
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("Install requirements-reverse-engineer.txt (jsonschema) for contract validation.") from exc
    schema = read_json(REPO_ROOT / "contracts" / schema_name)
    jsonschema.Draft202012Validator(schema).validate(value)


def parser(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    return p
