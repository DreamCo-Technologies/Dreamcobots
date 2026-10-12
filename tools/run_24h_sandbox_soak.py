#!/usr/bin/env python3
"""Persist hash-linked hourly inventory receipts. These do not prove runtime uptime."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "config/generated/user-money-map.json"
OUT = ROOT / "config/generated/sandbox-24h-tick.json"
HISTORY = ROOT / "config/generated/sandbox-24h-history.json"
REPORT = ROOT / "reports/SANDBOX_24H.md"


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def append_receipt(history: list, bots: list, commit: str, run_id: str, now: datetime) -> tuple[list, dict]:
    import re
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("immutable repository commit required")
    if not bots or any(not isinstance(row, dict) or not row.get("slug") or not row.get("grok_slug") for row in bots):
        raise ValueError("nonempty fleet and complete routing identities required")
    ids = [row["slug"] for row in bots]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate fleet identities")
    if not isinstance(run_id, str) or not run_id.strip() or now.tzinfo is None:
        raise ValueError("run identity and timezone required")
    previous = ""
    stamps = []
    seen = set()
    for receipt in history:
        body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
        if receipt.get("previous_sha256") != previous or receipt.get("receipt_sha256") != digest(body):
            raise ValueError("receipt history integrity failure")
        if receipt["run_id"] in seen:
            raise ValueError("duplicate historical run identity")
        seen.add(receipt["run_id"])
        stamp = datetime.fromisoformat(receipt["generated_at"])
        if stamp.tzinfo is None or (stamps and stamp <= stamps[-1]):
            raise ValueError("nonmonotonic receipt history")
        stamps.append(stamp)
        previous = receipt["receipt_sha256"]
    if run_id in seen or (stamps and now <= stamps[-1]):
        raise ValueError("duplicate run or nonmonotonic timestamp")
    fleet_digest = digest({"bots": sorted(bots, key=lambda row: row["slug"])})
    receipt = {"schema": "dreamco.sandbox_inventory_receipt.v2", "generated_at": now.isoformat(),
               "run_id": run_id, "repo_commit": commit, "fleet_sha256": fleet_digest,
               "sampled_bots": sorted(ids), "fleet_count": len(ids), "previous_sha256": previous,
               "model_executed": False, "runtime_verified": False, "production_ready": False,
               "status": "inventory_checked", "charges_attempted": 0}
    receipt["receipt_sha256"] = digest(receipt)
    history = history + [receipt]
    # Restart coverage at any source change or gap; do not combine different fleets/commits.
    window = [receipt]
    for older in reversed(history[:-1]):
        gap = datetime.fromisoformat(window[0]["generated_at"]) - datetime.fromisoformat(older["generated_at"])
        if older["repo_commit"] != commit or older["fleet_sha256"] != fleet_digest or not 0 < gap.total_seconds() <= 5400:
            break
        window.insert(0, older)
    span = (now - datetime.fromisoformat(window[0]["generated_at"])).total_seconds()
    summary = {"receipts": len(history), "fleet_count": len(ids), "coverage_seconds": span,
               "inventory_24h_covered": span >= 86400 and len(window) >= 25,
               "runtime_24h_verified": False, "production_ready": False,
               "latency_ms": None, "failure_rate": None,
               "reason": "Inventory receipts only; no runtime probe or model executed"}
    return history, summary


def main() -> int:
    data = json.loads(MAP.read_text())
    history = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    now = datetime.now(timezone.utc)
    run_id = os.environ.get("GITHUB_RUN_ID", "local-" + now.isoformat()) + ":" + os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    history, summary = append_receipt(history, data.get("bots", []), commit, run_id, now)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(history, indent=2) + "\n")
    OUT.write_text(json.dumps({**history[-1], "coverage": summary}, indent=2) + "\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("# Sandbox inventory receipts\n\nRuntime 24h verification: **UNKNOWN**\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
