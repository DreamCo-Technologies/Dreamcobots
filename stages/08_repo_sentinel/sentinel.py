"""Repository Sentinel: AST integrity audit and policy-gated FreeCodeCamp metadata refresh."""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "stages/08_repo_sentinel/canonical_registry.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def catalog_freshness(ledger: Path, max_age_hours: float) -> dict[str, Any]:
    if not ledger.exists():
        return {"exists": False, "record_count": 0, "stale": True, "age_hours": None}
    latest = None
    count = 0
    for line_number, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid catalog ledger JSON at line {line_number}") from exc
        count += 1
        observed = record.get("observed_at")
        if observed:
            stamp = datetime.fromisoformat(str(observed).replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            latest = stamp if latest is None or stamp > latest else latest
    if latest is None:
        return {"exists": True, "record_count": count, "stale": True, "age_hours": None}
    age = max(0.0, (datetime.now(timezone.utc) - latest).total_seconds() / 3600)
    return {"exists": True, "record_count": count, "stale": age > max_age_hours,
            "age_hours": round(age, 3), "last_observed_at": latest.isoformat()}


def run_sentinel(*, sync_fcc: bool = False, apply_ast: bool = False,
                 backup_dir: Path | None = None) -> dict[str, Any]:
    config = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if config.get("schema") != "dreamco.sentinel_registry.v1":
        raise ValueError("unsupported Sentinel registry schema")
    ast_tool = _load_module("dreamco_ast_consolidator", ROOT / "stages/08_repo_sentinel/ast_consolidator.py")
    scan = ast_tool.scan_duplicate_symbols(ROOT, config.get("scan_roots", []))
    consolidation = ast_tool.consolidate_exact_duplicates(
        ROOT, scan["duplicates"], config.get("canonical_owners", {}),
        apply=apply_ast, backup_dir=backup_dir,
    )
    catalog_cfg = config["catalog"]
    ledger = ROOT / catalog_cfg["ledger_path"]
    freshness = catalog_freshness(ledger, float(catalog_cfg.get("max_age_hours", 24)))
    sync_report = None
    if sync_fcc and freshness["stale"]:
        sync_module = _load_module("dreamco_fcc_sync", ROOT / "stages/00_catalog_sync/sync_fcc_catalog.py")
        sync_report = sync_module.sync_fcc_catalog(
            ledger=ledger, policy_path=ROOT / catalog_cfg["policy_path"]
        )
        freshness = catalog_freshness(ledger, float(catalog_cfg.get("max_age_hours", 24)))
    return {
        "schema": "dreamco.repo_sentinel_report.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ast": {"symbols_scanned": scan["symbols_scanned"], "duplicates": scan["duplicates"],
                "parse_errors": scan["parse_errors"], "consolidation": consolidation,
                "apply_enabled": apply_ast},
        "freecodecamp_catalog": {"source_id": catalog_cfg["source_id"], "freshness": freshness,
                                 "sync_requested": sync_fcc, "sync_report": sync_report,
                                 "media_downloaded": False, "transcripts_fetched": False},
        "overall_status": "needs_review" if scan["parse_errors"] or scan["duplicates"] or any(
            row.get("status") in {"conflict", "canonical_symbol_missing", "canonical_file_missing", "unregistered_owner", "unsafe_canonical_path"}
            for row in consolidation
        ) or freshness["stale"] else "audit_passed",
        "automatic_rewrites_default": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sync-fcc", action="store_true", help="refresh the catalog only when stale")
    parser.add_argument("--apply-ast", action="store_true", help="shim AST-identical duplicates with a canonical owner")
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--report", type=Path, default=ROOT / "reports/repo-sentinel/sentinel_report.json")
    args = parser.parse_args()
    if args.apply_ast and args.backup_dir is None:
        parser.error("--apply-ast requires --backup-dir")
    report = run_sentinel(sync_fcc=args.sync_fcc, apply_ast=args.apply_ast, backup_dir=args.backup_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["overall_status"] == "audit_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
