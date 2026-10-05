#!/usr/bin/env python3
"""Evidence ledger v0.1 gate: computes the only status an entry may hold.
Exit 1 if any entry claims more than its evidence supports (vanity green)."""
import json, re, sys
SHA = re.compile(r"^[0-9a-f]{40}$")
RANK = ["rejected","open","evidence_incomplete","evidence_complete","cert_pending","certified"]

def missing(e):
    m = []
    if not (e.get("git", {}).get("sha") and SHA.match(e["git"]["sha"])): m.append("missing_sha")
    ci = e.get("ci", {})
    if not (ci.get("conclusion") == "success" and ci.get("run_url") and ci.get("head_sha") == e.get("git", {}).get("sha")): m.append("missing_ci_on_sha")
    s = e.get("soak", {})
    if not (s.get("result") == "pass" and s.get("uri") and s.get("duration_ok")): m.append("missing_soak")
    r = e.get("runtime", {})
    if not (r.get("result") == "pass" and r.get("proof_uri")): m.append("missing_runtime")
    return m

def main(path):
    bad = 0
    for n, line in enumerate(open(path), 1):
        if not line.strip(): continue
        e = json.loads(line)
        gaps = missing(e)
        ceiling = "evidence_incomplete" if gaps else "certified"
        claimed = e.get("status")
        vanity = (claimed in ("evidence_complete","cert_pending","certified") and gaps) \
                 or (e["claim"].get("asserted_ready") and gaps) \
                 or (e["prc"].get("decision") == "certify" and gaps)
        flag = "VANITY" if vanity else "ok"
        bad += bool(vanity)
        print(f"{flag}\t{e['entry_id']}\tstatus={claimed}\tceiling={ceiling}\tgaps={','.join(gaps) or '-'}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evidence/ledger/ledger.jsonl")
