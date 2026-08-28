#!/usr/bin/env python3
"""Convert workflow observations into stable failure fingerprints and repair queues."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

RULES = [
    ("workflow", r"yaml|workflow|action|runner|checkout|permission|workflow syntax"),
    ("dependency", r"npm|pip|package|dependency|lockfile|ebadengine|module not found"),
    ("test", r"test|pytest|jest|assert|coverage|regression"),
    ("security", r"security|secret|credential|vulnerability|sast|codeql"),
    ("benchmark", r"benchmark|evaluation|score|regression|accuracy|latency"),
    ("runtime", r"runtime|production|deploy|health|500|502|503|timeout|route"),
    ("review", r"pull request|\bpr\b|merge|conflict|review|stale"),
]

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[0-9a-f]{7,40}", "<sha>", text)
    text = re.sub(r"\d+", "<n>", text)
    return re.sub(r"\s+", " ", text).strip()

def classify(text: str) -> list[str]:
    value = normalize(text)
    hits = [name for name, pattern in RULES if re.search(pattern, value)]
    return hits or ["unknown"]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="artifacts/greenkeeper/root-cause.json")
    args = parser.parse_args()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    observations = raw if isinstance(raw, list) else raw.get("observations", raw.get("failures", []))
    records = []
    for observation in observations:
        text = observation if isinstance(observation, str) else json.dumps(observation, sort_keys=True)
        normalized = normalize(text)
        fingerprint = hashlib.sha256(normalized.encode()).hexdigest()[:16]
        categories = classify(text)
        records.append({
            "fingerprint": fingerprint,
            "categories": categories,
            "observation": observation,
            "root_cause_status": "unresolved",
            "repair_status": "queued",
            "evidence_required": ["failure_log", "affected_scope", "verification_result"],
        })
    result = {
        "schema": "dreamco.greenkeeper_root_cause.v1",
        "truth_rule": "unknown is never green",
        "deduplication": "sha256(normalized-observation)[:16]",
        "observations": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
