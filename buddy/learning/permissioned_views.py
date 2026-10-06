"""Permissioned multi-view learning, weight choice, and Buddy calls.

A final perspective is refused until several viewpoints are on record.
Weight download, training, text, voice, image, and peer calls each need
an explicit grant. Voice and image also need a consent hash for the
reference. Nothing is downloaded or transmitted by this module.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

ACTIONS = {"download_weights", "train", "text", "voice_call", "image_call", "peer_message"}
MIN_VIEWS = 3


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class PermissionError(RuntimeError):
    pass


def grant(action: str, subject: str, allowed: bool, consent_hash: str = "") -> dict:
    if action not in ACTIONS:
        raise PermissionError(f"unknown action: {action}")
    if action in {"voice_call", "image_call"} and allowed and len(consent_hash) < 8:
        raise PermissionError("voice and image need a consent hash for the reference")
    return {
        "action": action,
        "subject": subject,
        "allowed": allowed,
        "consent_hash": consent_hash,
        "granted_at": _now(),
    }


def require_grant(grants: list[dict], action: str, subject: str) -> dict:
    match = next((row for row in grants if row["action"] == action and row["subject"] == subject and row["allowed"]), None)
    if match is None:
        raise PermissionError(f"{action} is not permitted for {subject}")
    return match


def learn(subject: str, views: list[dict], grants: list[dict], download_weights: bool = False) -> dict:
    require_grant(grants, "train", subject)
    if len(views) < MIN_VIEWS:
        raise PermissionError(f"need at least {MIN_VIEWS} perspectives before a final view")
    sources = {row["source"] for row in views}
    if len(sources) < MIN_VIEWS:
        raise PermissionError("perspectives must come from different sources")
    if download_weights:
        require_grant(grants, "download_weights", subject)
    agreements = [row["claim"] for row in views if row.get("stance") == "agree"]
    conflicts = [row["claim"] for row in views if row.get("stance") == "conflict"]
    return {
        "subject": subject,
        "views": len(views),
        "sources": sorted(sources),
        "perception": agreements[0] if agreements else "No agreement. Keep the conflict visible.",
        "conflicts": conflicts,
        "weights_downloaded": False,
        "download_requested": download_weights,
        "final": True,
        "production_trained": False,
    }


def call(mode: str, sender: str, receiver: str, grants: list[dict], body: str) -> dict:
    action = {"text": "text", "voice": "voice_call", "image": "image_call"}[mode]
    require_grant(grants, action, sender)
    require_grant(grants, action, receiver)
    require_grant(grants, "peer_message", sender)
    return {
        "mode": mode,
        "sender": sender,
        "receiver": receiver,
        "body": body,
        "delivered": False,
        "sandbox": True,
        "answered_with": mode,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a permissioned multi-view sample")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args(argv)
    if not args.demo:
        parser.print_help()
        return 0
    grants = [
        grant("train", "buddy-a", True),
        grant("download_weights", "buddy-a", True),
        grant("text", "buddy-a", True),
        grant("text", "buddy-b", True),
        grant("peer_message", "buddy-a", True),
        grant("voice_call", "buddy-a", True, "a" * 16),
        grant("voice_call", "buddy-b", True, "b" * 16),
    ]
    learned = learn(
        "buddy-a",
        [
            {"source": "docs", "claim": "cite the source", "stance": "agree"},
            {"source": "benchmark", "claim": "cite the source", "stance": "agree"},
            {"source": "counterexample", "claim": "a single model is enough", "stance": "conflict"},
        ],
        grants,
        download_weights=True,
    )
    message = call("text", "buddy-a", "buddy-b", grants, learned["perception"])
    print(json.dumps({"learned": learned, "call": message}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
