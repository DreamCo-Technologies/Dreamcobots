"""Review model/chatbot resources and selected GitHub components before integration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from buddy.learning.resource_preflight import (ResourcePreflightError, clone_selected_github_components,
                                                review_ai_resource, review_github_repository)  # noqa: E402


def _write_report(report: dict, output: str | None) -> None:
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        path = Path(output).expanduser()
        if path.exists() or path.is_symlink():
            raise ResourcePreflightError("Output path already exists; reports are never overwritten.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ai = sub.add_parser("ai", help="Create provider-neutral intake checks for any model/chatbot/agent/tool")
    ai.add_argument("resource_id")
    ai.add_argument("resource_type", choices=["chatbot", "ai_model", "agent", "tool", "mcp_server", "workflow"])
    ai.add_argument("provider")
    ai.add_argument("source_url")
    ai.add_argument("--revision", default="")
    ai.add_argument("--license", default="")
    ai.add_argument("--terms-url", default="")
    ai.add_argument("--intended-action", action="append", default=[])
    ai.add_argument("--output")

    github = sub.add_parser("github", help="Inspect a public repository and selected files without cloning or execution")
    github.add_argument("source_url")
    github.add_argument("--revision", default="")
    github.add_argument("--select", action="append", default=[], help="Repository file or folder; repeat to choose more components")
    github.add_argument("--output")

    clone = sub.add_parser("clone-selected", help="Copy reviewed open-source components without installing or running them")
    clone.add_argument("review_report", type=Path)
    clone.add_argument("target", type=Path)
    clone.add_argument("--confirm-authorization", action="store_true", help="Confirm permission to use the selected repository components")
    clone.add_argument("--confirm-license-review", action="store_true", help="Confirm you reviewed the license and notices for this use")
    clone.add_argument("--customize", action="append", default=[], choices=["audience", "workflow", "interface", "accessibility", "privacy", "security", "integrations", "performance", "cost", "original_features"])
    clone.add_argument("--differentiator", required=True, help="Original DreamCo direction, at least 30 characters")

    args = parser.parse_args()
    try:
        if args.command == "ai":
            report = review_ai_resource(resource_id=args.resource_id, resource_type=args.resource_type,
                provider=args.provider, source_url=args.source_url, immutable_revision=args.revision,
                license_id=args.license, terms_url=args.terms_url, intended_actions=args.intended_action)
            _write_report(report, args.output)
        elif args.command == "github":
            report = review_github_repository(args.source_url, args.revision or "", selected_paths=args.select)
            _write_report(report, args.output)
        else:
            prior = json.loads(args.review_report.read_text(encoding="utf-8"))
            if prior.get("schema") != "dreamco.github_repository_preflight.v1":
                raise ResourcePreflightError("Provide a GitHub preflight report created by the review command.")
            source = prior.get("source", {})
            selected = prior.get("inventory", {}).get("selected_paths", [])
            fresh = review_github_repository(source.get("url", ""), source.get("commit_sha", ""), selected_paths=selected)
            if fresh.get("source", {}).get("commit_sha") != source.get("commit_sha"):
                raise ResourcePreflightError("The source commit changed; review it again before copying components.")
            report = clone_selected_github_components(fresh, args.target,
                user_authorized=args.confirm_authorization, license_reviewed=args.confirm_license_review,
                customizations=args.customize, differentiator=args.differentiator)
            _write_report(report, None)
    except (ResourcePreflightError, OSError, json.JSONDecodeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
