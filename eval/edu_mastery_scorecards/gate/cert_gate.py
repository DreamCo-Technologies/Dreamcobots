#!/usr/bin/env python3
"""Completion-certificate gate for course mastery evidence cards.

Rule: no completion certificate without benches. A card may carry a
certificate / status 'certified' only when every required bench for the
claimed floor (and all lower floors) has real, passing, hashed evidence.
"""
import json, re, sys
from datetime import datetime

FLOORS = ["F0", "F1", "F2", "F3", "F4"]
SHA = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_TOP = ["card_id","course_id","course_title","track","version","learner","floors",
                "bench_results","provenance","floor_attained","status","certificate","regression_watch"]


def _ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def _bench_ok(b, spec):
    """Return list of reasons this bench result fails the floor spec (empty = ok)."""
    r = []
    bid = b.get("bench_id", "?")
    for k in ("run_id", "artifact_uri"):
        if not b.get(k):
            r.append(f"bench {bid}: missing {k}")
    if not SHA.match(str(b.get("artifact_sha256", ""))):
        r.append(f"bench {bid}: artifact_sha256 is not 64 lowercase hex chars")
    if not _ts(str(b.get("run_timestamp", ""))):
        r.append(f"bench {bid}: invalid run_timestamp")
    mx = b.get("max_score") or 0
    ratio = (b.get("score", 0) / mx) if mx else 0
    if ratio < spec["min_score"]:
        r.append(f"bench {bid}: score ratio {ratio:.2f} below floor min {spec['min_score']:.2f}")
    if spec.get("holdout_required"):
        if not b.get("holdout"):
            r.append(f"bench {bid}: floor requires a held-out bench")
        if not (b.get("leakage_check") or {}).get("passed"):
            r.append(f"bench {bid}: leakage check not passed")
    return r


def floor_status(card):
    """Return (highest_met_floor_or_None, {floor: [reasons]})."""
    benches = {b.get("bench_id"): b for b in card.get("bench_results", [])}
    floors = card.get("floors", {})
    highest, why = None, {}
    prev_latest = None
    for f in FLOORS:
        spec = floors.get(f)
        if spec is None:
            why[f] = ["floor not defined on card"]
            break
        reasons = []
        if not spec["required_benches"]:
            reasons.append("floor lists no required benches")
        latest = None
        for bid in spec["required_benches"]:
            b = benches.get(bid)
            if b is None:
                reasons.append(f"required bench {bid} has no result")
                continue
            reasons += _bench_ok(b, spec)
            t = _ts(str(b.get("run_timestamp", "")))
            if t and (latest is None or t > latest):
                latest = t
        gap = spec.get("min_days_since_prior_floor")
        if gap and not reasons:
            if prev_latest is None or latest is None or (latest - prev_latest).days < gap:
                reasons.append(f"retest must be >= {gap} days after prior floor evidence")
        if spec.get("independent_evaluator_required") and not reasons:
            issuer = (card.get("certificate") or {}).get("issued_by")
            for bid in spec["required_benches"]:
                if benches[bid].get("evaluator") in (None, "", issuer):
                    reasons.append(f"bench {bid}: evaluator must be independent of issuer")
        why[f] = reasons
        if reasons:
            break
        highest, prev_latest = f, latest
    return highest, why


def check_card(card):
    reasons = [f"missing field {k}" for k in REQUIRED_TOP if k not in card]
    if reasons:
        return False, reasons
    highest, why = floor_status(card)
    claimed = card.get("floor_attained")
    if claimed != highest:
        detail = "; ".join(why.get(claimed, [])) if claimed else ""
        reasons.append(f"floor_attained={claimed} but evidence supports {highest}" + (f" ({detail})" if detail else ""))
    cert = card.get("certificate")
    status = card.get("status")
    if status == "certified" and not cert:
        reasons.append("status is certified but no certificate object")
    if cert:
        if not card.get("bench_results"):
            reasons.append("certificate present with no bench results (no cert without benches)")
        cf = cert.get("floor")
        if highest is None or cf not in FLOORS or FLOORS.index(cf) > FLOORS.index(highest):
            reasons.append(f"certificate floor {cf} exceeds evidence-supported floor {highest}")
        ids = {b.get("bench_id") for b in card.get("bench_results", [])}
        if not cert.get("evidence_bench_ids"):
            reasons.append("certificate lists no evidence_bench_ids")
        for bid in cert.get("evidence_bench_ids", []):
            if bid not in ids:
                reasons.append(f"certificate evidence {bid} does not resolve to a bench result")
        if status not in ("certified", "revoked"):
            reasons.append(f"certificate present but status is {status}")
    for s in card["provenance"].get("sources", []):
        if not s.get("license") or not s.get("consent"):
            reasons.append(f"provenance source {s.get('uri')} lacks license or consent")
    return (not reasons), reasons


def main(argv):
    if len(argv) != 2:
        print("usage: cert_gate.py card.json"); return 2
    with open(argv[1]) as fh:
        card = json.load(fh)
    ok, reasons = check_card(card)
    print(("PASS " if ok else "FAIL ") + card.get("card_id", "?"))
    for r in reasons:
        print("  - " + r)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
