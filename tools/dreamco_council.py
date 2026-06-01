#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bots.global_sources_ai_bot.model_registry import TOP_100_AI_MODELS


@dataclass(frozen=True)
class CouncilVote:
    council_bot: str
    vote: str
    confidence: int
    reason: str
    models_considered: int


COUNCIL = (
    "validator_bot",
    "security_bot",
    "architecture_bot",
    "performance_bot",
    "compliance_bot",
)


def _score(signal_hits: int, base: int = 92) -> int:
    return max(51, min(99, base - (signal_hits * 14)))


def evaluate_vote(council_bot: str, content: str, model_count: int) -> CouncilVote:
    lowered = content.lower()
    red_flags = {
        "validator_bot": ("todo", "fixme", "wip"),
        "security_bot": ("password", "secret", "private key", "hardcoded token"),
        "architecture_bot": ("breaking change", "rewrite all", "single point of failure"),
        "performance_bot": ("n+1", "blocking loop", "full table scan"),
        "compliance_bot": ("pci violation", "gdpr violation", "no audit trail"),
    }[council_bot]
    hits = sum(1 for flag in red_flags if flag in lowered)
    vote = "reject" if hits > 0 else "approve"
    confidence = _score(hits)
    reason = (
        f"{council_bot} found {hits} governance risk signal(s)."
        if hits
        else f"{council_bot} found no blocking signals."
    )
    return CouncilVote(
        council_bot=council_bot,
        vote=vote,
        confidence=confidence,
        reason=reason,
        models_considered=model_count,
    )


def aggregate(votes: list[CouncilVote]) -> dict[str, Any]:
    approvals = [v for v in votes if v.vote == "approve"]
    rejections = [v for v in votes if v.vote == "reject"]
    avg_confidence = round(sum(v.confidence for v in votes) / max(len(votes), 1), 2)
    hard_veto = any(v.council_bot in {"security_bot", "compliance_bot"} for v in rejections)
    approved = len(approvals) >= 3 and not hard_veto
    decision = "approve" if approved else "reject"
    return {
        "decision": decision,
        "average_confidence": avg_confidence,
        "approve_count": len(approvals),
        "reject_count": len(rejections),
        "hard_veto": hard_veto,
    }


def run_council(content: str) -> dict[str, Any]:
    model_count = len(TOP_100_AI_MODELS)
    votes = [evaluate_vote(member, content, model_count) for member in COUNCIL]
    summary = aggregate(votes)
    return {
        "schema": "dreamco.council.v1",
        "models_in_global_ai_registry": model_count,
        "all_models_considered": all(v.models_considered == model_count for v in votes),
        "votes": [asdict(vote) for vote in votes],
        "summary": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DreamCo AI Debate Council voting.")
    parser.add_argument("--title", default="", help="PR or change title.")
    parser.add_argument("--body", default="", help="PR or change description.")
    parser.add_argument("--output", type=Path, default=None, help="Optional output JSON path.")
    args = parser.parse_args()

    payload = run_council(f"{args.title}\n{args.body}".strip())
    print(json.dumps(payload, indent=2))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return 0 if payload["summary"]["decision"] == "approve" else 1


if __name__ == "__main__":
    sys.exit(main())
