"""Offline, evidence-first Buddy capability certification. Standard library only."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

STATES = ("planned", "implemented", "tested", "connected", "verified", "production")
DOMAINS = ("coding", "research", "learning", "models", "agents", "devices", "media", "business", "data", "security", "education", "deployment")
MAX_SECONDS = 60

def _digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def validate_manifest(data):
    if not isinstance(data, dict) or not isinstance(data.get("capabilities"), list):
        raise ValueError("capabilities list required")
    seen = set()
    for item in data["capabilities"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise ValueError("capability id required")
        if item["id"] in seen:
            raise ValueError("duplicate capability id")
        seen.add(item["id"])
        if item.get("domain") not in DOMAINS:
            raise ValueError("invalid domain")
        if item.get("target") not in STATES:
            raise ValueError("invalid target state")
        for key in ("description", "owner", "test_module"):
            if not isinstance(item.get(key), str):
                raise ValueError(key + " must be a string")
        if item.get("test_module") and not item["test_module"].startswith("tests.test_"):
            raise ValueError("test module must be under tests.test_*")
    return data

def run_suite(manifest, *, repo_root, execute=False, revision="unknown"):
    validate_manifest(manifest)
    root = Path(repo_root).resolve()
    results = []
    for item in manifest["capabilities"]:
        started = time.monotonic()
        module = item["test_module"]
        status, reason, receipt = "unverified", "No executable evidence collected", {}
        if execute and module:
            try:
                proc = subprocess.run([sys.executable, "-m", "unittest", module],
                                      cwd=root, capture_output=True, text=True,
                                      timeout=MAX_SECONDS, check=False)
                status = "tested" if proc.returncode == 0 else "failed"
                reason = "Local test passed; not independent mastery or production certification" if proc.returncode == 0 else "Local test failed"
                receipt = {"exit_code": proc.returncode,
                           "stdout_sha256": hashlib.sha256(proc.stdout.encode()).hexdigest(),
                           "stderr_sha256": hashlib.sha256(proc.stderr.encode()).hexdigest()}
            except subprocess.TimeoutExpired:
                status, reason = "failed", "Test timed out"
            except OSError:
                status, reason = "blocked", "Python test execution unavailable"
        elif module:
            reason = "Test declared but not executed"
        results.append({"id": item["id"], "domain": item["domain"], "owner": item["owner"],
                        "description": item["description"], "target": item["target"],
                        "observed": status, "reason": reason, "test_module": module,
                        "duration_ms": int((time.monotonic() - started) * 1000),
                        "receipt": receipt, "independently_verified": False,
                        "production_certified": False, "blockers": [
                            "Independent benchmark, live adapter, security and deployment evidence not provided"
                        ]})
    report = {"schema": "dreamco.capability_certification.v1",
              "generated_at": datetime.now(timezone.utc).isoformat(),
              "revision": revision, "mode": "local_test" if execute else "inventory_only",
              "source": "config/buddy/capability-certification-goals.json",
              "results": results, "summary": {
                  "total": len(results),
                  "locally_tested": sum(x["observed"] == "tested" for x in results),
                  "failed": sum(x["observed"] == "failed" for x in results),
                  "independently_verified": 0, "production_certified": 0}}
    report["report_sha256"] = _digest(report)
    return report

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="config/buddy/capability-certification-goals.json")
    parser.add_argument("--output", default="website/data/buddy-capability-certification.json")
    parser.add_argument("--execute", action="store_true", help="run explicitly listed local unittest modules")
    parser.add_argument("--revision", default="unknown")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    manifest = json.loads((root / args.manifest).read_text(encoding="utf-8"))
    report = run_suite(manifest, repo_root=root, execute=args.execute, revision=args.revision)
    output = (root / args.output).resolve()
    if not output.is_relative_to(root / "website" / "data"):
        parser.error("output must be within website/data")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    if report["summary"]["failed"]:
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
