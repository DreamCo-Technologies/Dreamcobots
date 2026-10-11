#!/usr/bin/env python3
"""Hard-fail frontier/sellable claim trust gates for Pages and API surfaces.

Four gates must be green before claimable shipping:
  1) provenance policy present and coherent
  2) allowlist / readiness never_claim_frontier_without_evidence
  3) sandbox soak tick evidence present and ok
  4) disclosure config present + assessment claimable:true

Default (deploy) mode: fail if vanity claim phrases appear in website/ while
gates are not all green. Strict mode (--require-all-gates): fail unless all
four are green regardless of copy.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISCLOSURE = ROOT / "config" / "buddy-frontier-claim-disclosure.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check_provenance(cfg: dict, errors: list[str]) -> bool:
    req = cfg["provenance_requirements"]
    path = ROOT / req["policy_path"]
    if not path.is_file():
        errors.append(f"provenance policy missing: {req['policy_path']}")
        return False
    policy = _load_json(path)
    if req.get("require_core_rule_present") and not policy.get("core_rule"):
        errors.append("provenance policy missing core_rule")
        return False
    classes = policy.get("ownership_classes") or []
    if req.get("block_unknown_do_not_publish_for_claims") and "unknown_do_not_publish" not in classes:
        errors.append("provenance policy missing unknown_do_not_publish ownership class")
        return False
    return True


def check_allowlist(cfg: dict, errors: list[str]) -> bool:
    req = cfg["allowlist_requirements"]
    gates_path = ROOT / req["readiness_gates_path"]
    contract_path = ROOT / req["model_contract_path"]
    ok = True
    if not gates_path.is_file():
        errors.append(f"readiness gates missing: {req['readiness_gates_path']}")
        ok = False
    else:
        gates = _load_json(gates_path)
        if req.get("require_never_claim_frontier_without_evidence") and not gates.get(
            "never_claim_frontier_without_evidence"
        ):
            errors.append("readiness gates must set never_claim_frontier_without_evidence=true")
            ok = False
        if not gates.get("gates"):
            errors.append("readiness gates list empty")
            ok = False
    if not contract_path.is_file():
        errors.append(f"model operating contract missing: {req['model_contract_path']}")
        ok = False
    return ok


def check_soak(cfg: dict, errors: list[str]) -> bool:
    req = cfg["soak_requirements"]
    tick_path = ROOT / req["tick_path"]
    report_path = ROOT / req["report_path"]
    ok = True
    if not tick_path.is_file():
        errors.append(f"sandbox soak tick missing: {req['tick_path']}")
        ok = False
    else:
        tick = _load_json(tick_path)
        if tick.get("status") != req.get("required_tick_status", "sandbox_tick_ok"):
            errors.append(
                f"sandbox soak tick status={tick.get('status')!r}, "
                f"need {req.get('required_tick_status')!r}"
            )
            ok = False
    if not report_path.is_file():
        errors.append(f"sandbox soak report missing: {req['report_path']}")
        ok = False
    return ok


def check_disclosure_and_claimable(cfg: dict, errors: list[str]) -> tuple[bool, bool]:
    """Return (disclosure_config_ok, claimable)."""
    fields = cfg.get("required_public_disclosure_fields") or []
    if len(fields) < 4:
        errors.append("disclosure config missing required_public_disclosure_fields")
        return False, False
    if not cfg.get("ship_rule"):
        errors.append("disclosure config missing ship_rule")
        return False, False
    assessment_path = ROOT / cfg["claimable_assessment_path"]
    if not assessment_path.is_file():
        errors.append(f"claim assessment missing: {cfg['claimable_assessment_path']}")
        return True, False
    assessment = _load_json(assessment_path)
    claimable = bool(assessment.get("claimable") is True and assessment.get("status") == "claimable")
    if not claimable:
        errors.append(
            "frontier claim not claimable: "
            f"claimable={assessment.get('claimable')!r} status={assessment.get('status')!r}"
        )
    return True, claimable


def find_vanity_hits(cfg: dict) -> list[str]:
    phrases = [p.lower() for p in cfg.get("vanity_claim_phrases") or []]
    roots = [ROOT / r for r in cfg.get("scan_roots") or ["website"]]
    suffixes = tuple(g.replace("*", "") for g in (cfg.get("scan_globs") or ["*.html", "*.js", "*.json", "*.md"]))
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if suffixes and not path.name.endswith(suffixes):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore").lower()
            except OSError:
                continue
            for phrase in phrases:
                if phrase and phrase in text:
                    rel = path.relative_to(ROOT).as_posix()
                    hits.append(f"{rel}: contains vanity phrase {phrase!r}")
    return hits


def evaluate(*, require_all_gates: bool) -> dict:
    errors: list[str] = []
    if not DISCLOSURE.is_file():
        return {
            "schema": "dreamco.buddy.frontier_claim_trust_result.v1",
            "all_gates_green": False,
            "claimable": False,
            "vanity_hits": [],
            "errors": [f"missing disclosure config: {DISCLOSURE.relative_to(ROOT)}"],
            "ok": False,
        }
    cfg = _load_json(DISCLOSURE)
    provenance_ok = check_provenance(cfg, errors)
    allowlist_ok = check_allowlist(cfg, errors)
    soak_ok = check_soak(cfg, errors)
    disclosure_ok, claimable = check_disclosure_and_claimable(cfg, errors)
    # claimable false always appends an error; for deploy mode we still track it
    all_gates_green = provenance_ok and allowlist_ok and soak_ok and disclosure_ok and claimable
    vanity_hits = find_vanity_hits(cfg)

    if require_all_gates:
        ok = all_gates_green
        if not ok and not errors:
            errors.append("require-all-gates: one or more trust gates red")
    else:
        # Deploy mode: allow Pages when no vanity claims ship while red.
        ok = True
        if vanity_hits and not all_gates_green:
            ok = False
            errors.append(
                "vanity frontier/sellable claim copy found on Pages while trust gates are red"
            )
            errors.extend(vanity_hits[:20])
        elif vanity_hits and all_gates_green:
            # phrases still discouraged even when claimable; allow if green
            pass

    return {
        "schema": "dreamco.buddy.frontier_claim_trust_result.v1",
        "mode": "require_all_gates" if require_all_gates else "deploy_block_vanity",
        "gates": {
            "provenance": provenance_ok,
            "allowlist": allowlist_ok,
            "sandbox_soak": soak_ok,
            "disclosure_config": disclosure_ok,
            "claimable": claimable,
        },
        "all_gates_green": all_gates_green,
        "claimable": claimable,
        "vanity_hit_count": len(vanity_hits),
        "vanity_hits": vanity_hits[:50],
        "errors": errors,
        "ok": ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-all-gates",
        action="store_true",
        help="Fail unless provenance, allowlist, soak, and claimable:true are all green",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON result path")
    args = parser.parse_args()
    result = evaluate(require_all_gates=args.require_all_gates)
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
