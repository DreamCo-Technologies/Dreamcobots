"""Validate grounded video-knowledge JSONL without inventing semantic truth."""
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUIRED = {"claim_id", "text", "evidence_refs", "source_refs", "confidence", "run_id", "schema_version"}

def validate(path: Path) -> int:
    errors = 0
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip(): continue
        try: row = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"line {n}: invalid JSON: {exc}"); errors += 1; continue
        missing = REQUIRED - row.keys()
        if missing:
            print(f"line {n}: missing {sorted(missing)}"); errors += 1
        if row.get("confidence") not in {"measured", "validated", "supported", "estimated", "unknown"}:
            print(f"line {n}: invalid confidence"); errors += 1
        if row.get("confidence") != "unknown" and not row.get("evidence_refs"):
            print(f"line {n}: non-unknown claim has no evidence"); errors += 1
    return errors

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    args = p.parse_args()
    raise SystemExit(1 if validate(args.manifest) else 0)
