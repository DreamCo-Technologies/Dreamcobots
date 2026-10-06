"""Learn from user interactions, courses, and videos without one-source answers.

Every interaction is stored. A final perspective still needs other angles.
Course and video notes store the source and the lesson, not a copied transcript.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from buddy.learning.permissioned_views import PermissionError, learn


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class InteractionLedger:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def record(self, kind: str, subject: str, source: str, claim: str, stance: str = "agree") -> dict:
        if kind not in {"user", "course", "youtube", "model", "counterexample"}:
            raise PermissionError(f"unknown interaction kind: {kind}")
        if kind in {"course", "youtube"} and not source.startswith(("http://", "https://")):
            raise PermissionError("course and video sources need a url")
        row = {"kind": kind, "subject": subject, "source": source, "claim": claim, "stance": stance, "at": _now()}
        self.rows.append(row)
        return row

    def perspective(self, subject: str, grants: list[dict]) -> dict:
        views = [row for row in self.rows if row["subject"] == subject]
        kinds = {row["kind"] for row in views}
        if "user" in kinds and len(kinds) < 2:
            raise PermissionError("a user interaction needs another angle before a final perspective")
        report = learn(subject, views, grants)
        report["interaction_count"] = len(views)
        report["kinds"] = sorted(kinds)
        report["copied_media"] = False
        return report


def picker(catalog: dict) -> dict:
    weights = [
        {
            "type": row["type"],
            "task": row["task"],
            "pipeline_tag": row["pipeline_tag"],
            "example_weights": row["example"],
            "commercial_ok": row["commercial_ok"],
            "min_gb": row["min_gb"],
            "download": "user_opt_in",
        }
        for row in catalog["models"]
    ]
    return {"shown": len(weights), "weights": weights, "downloaded": False}


def main() -> int:
    print(json.dumps({"ledger": "ready", "copied_media": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
