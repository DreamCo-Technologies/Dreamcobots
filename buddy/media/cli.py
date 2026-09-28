"""Usage: python -m buddy.media.cli <command> ...  (run from the repo root)"""
from __future__ import annotations

import argparse
import json

from .core import BuddyMedia


def main(argv=None):
    p = argparse.ArgumentParser(prog="buddy-media")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("consent-add")
    c.add_argument("reference"); c.add_argument("--kind", choices=["voice", "image"], required=True)
    c.add_argument("--subject", required=True); c.add_argument("--granted-by", required=True)
    c.add_argument("--attestation", required=True, help="Sentence stating the subject consented")
    c.add_argument("--scope", default="personal"); c.add_argument("--ttl-days", type=int)

    r = sub.add_parser("consent-revoke"); r.add_argument("consent_id")

    v = sub.add_parser("voice")
    v.add_argument("text"); v.add_argument("--ref", required=True)
    v.add_argument("--purpose", default="personal"); v.add_argument("--out")

    i = sub.add_parser("image")
    i.add_argument("prompt"); i.add_argument("--ref", required=True)
    i.add_argument("--mode", choices=["style", "face"], default="style")
    i.add_argument("--purpose", default="personal"); i.add_argument("--seed", type=int); i.add_argument("--out")

    ver = sub.add_parser("verify"); ver.add_argument("path")
    sub.add_parser("status")

    a = p.parse_args(argv)
    m = BuddyMedia()
    try:
        if a.cmd == "consent-add":
            rec = m.register_consent(a.reference, a.subject, a.kind, a.granted_by, a.attestation,
                                     scope=a.scope.split(","), ttl_days=a.ttl_days)
            print(rec.consent_id)
        elif a.cmd == "consent-revoke":
            print("revoked" if m.consents.revoke(a.consent_id) else "not found")
        elif a.cmd == "voice":
            print(m.clone_voice(a.text, a.ref, purpose=a.purpose, out=a.out).path)
        elif a.cmd == "image":
            print(m.clone_image(a.prompt, a.ref, purpose=a.purpose, mode=a.mode, seed=a.seed, out=a.out).path)
        elif a.cmd == "verify":
            print(json.dumps(m.verify(a.path), indent=2))
        elif a.cmd == "status":
            print(json.dumps(m.status(), indent=2))
    finally:
        m.close()


if __name__ == "__main__":
    main()
