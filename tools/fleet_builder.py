"""Fleet builder for systems larger than the current repo.

Stages are diagnose, fix, build, test, train, and deploy. Train and deploy
stay planned until a human passes --allow-train or --allow-deploy. A plan is
not a green run.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ("diagnose", "fix", "build", "test", "train", "deploy")
STYLES = ("python-bot", "typescript-bot", "study-pack", "media", "pages", "workflow")


def plan(style: str, name: str, allow_train: bool = False, allow_deploy: bool = False) -> dict:
    if style not in STYLES:
        raise ValueError(f"unknown style: {style}")
    stages = []
    for stage in STAGES:
        allowed = stage not in {"train", "deploy"} or (stage == "train" and allow_train) or (stage == "deploy" and allow_deploy)
        stages.append({
            "stage": stage,
            "style": style,
            "target": name,
            "status": "planned" if allowed else "blocked",
            "reason": "" if allowed else "needs an explicit allow flag and host evidence",
        })
    return {
        "name": name,
        "style": style,
        "stages": stages,
        "green": False,
        "weights_downloaded": False,
        "deployed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan a fix, build, test, train, and deploy run")
    parser.add_argument("--style", default="python-bot", choices=sorted(STYLES))
    parser.add_argument("--name", default="buddy")
    parser.add_argument("--allow-train", action="store_true")
    parser.add_argument("--allow-deploy", action="store_true")
    args = parser.parse_args(argv)
    report = plan(args.style, args.name, args.allow_train, args.allow_deploy)
    out = ROOT / "reports" / "fleet-builder-plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"name": report["name"], "style": report["style"], "green": report["green"], "blocked": [row["stage"] for row in report["stages"] if row["status"] == "blocked"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
