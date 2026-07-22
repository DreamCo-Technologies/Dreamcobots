#!/usr/bin/env python3
"""Generate Buddy Creative Studio registry and readiness report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dreamco_platform.creative import BuddyCreativeStudio, ProjectType


OUT_JSON = ROOT / "config" / "generated" / "buddy_multimodal_studio.json"
OUT_MD = ROOT / "reports" / "BUDDY_MULTIMODAL_STUDIO.md"


def build_registry() -> dict:
    return {
        "schema": "dreamco.buddy_multimodal_studio.v1",
        "name": "Buddy Creative Studio",
        "status": "production_packet_local_prototype_and_local_adapter_ready",
        "project_types": [
            {
                "id": project_type.value,
                "native_routes": [
                    *BuddyCreativeStudio.TYPE_ROUTES[project_type],
                    *BuddyCreativeStudio.COMMON_ROUTES,
                    *(
                        [{"bot": "adaptive-learning", "role": "learning objectives and difficulty tuning"}]
                        if project_type in {
                            ProjectType.SCHOOL_SIMULATION,
                            ProjectType.PARENT_LEARNING_VIDEO,
                            ProjectType.COLLEGE_COURSE,
                        }
                        else []
                    ),
                ],
            }
            for project_type in ProjectType
        ],
        "shared_routes": BuddyCreativeStudio.COMMON_ROUTES,
        "capabilities": [
            "plan games from prototypes through milestone-gated epic productions",
            "play-test supported owner-authorized games through sandbox adapters",
            "build curriculum-aligned school simulations",
            "build parent and family learning videos",
            "build music video treatments and production packets",
            "build sourced biographies and autobiographies",
            "build truthful commercial production packets",
            "build college courses with modules, labs, assessments, and rubrics",
            "build original feature-film production packets and delivery plans",
            "build rights-aware artist-development and original music production packets",
            "build editable logo concepts, brand systems, and clearance plans",
            "capture adult user voice and image locally",
            "enforce voice and likeness consent",
            "prepare local or optional model rendering",
            "run installed local voice and image engines without cloud credentials",
            "generate captions, lesson checks, and accessibility tests",
            "generate portable project code and production manifests",
        ],
        "media_truth_states": [
            "not_requested",
            "consent_verified_pending_render",
            "media_engine_configuration_required",
            "rendered",
        ],
        "release_guardrails": [
            "self-owned adult voice and likeness only",
            "no voice or likeness cloning of minors",
            "synthetic-media label cannot be disabled",
            "raw biometric media stays local or in an encrypted owner vault",
            "consent can be revoked",
            "publishing requires owner approval",
            "outside models are optional",
        ],
        "website": "website/studio.html",
        "game_lab": "dreamco_platform/games/harness.py",
        "social_manager": "dreamco_platform/social/manager.py",
        "approval_notifications": "server/approval-notifications.ts",
        "local_media_renderer": "dreamco_platform/creative/local_renderer.py",
        "cli": ["buddy studio-refresh", "buddy studio-report", "buddy open-studio"],
    }


def write_report(registry: dict) -> None:
    lines = [
        "# Buddy Multimodal Creative Studio",
        "",
        "Buddy now has one governed production path for games, school simulations, learning videos, music videos, biographies, commercials, college courses, feature films, artist development, and brand systems.",
        "",
        "## Production Tracks",
        "",
    ]
    lines.extend(f"- `{item['id']}`" for item in registry["project_types"])
    lines.extend(
        [
            "",
            "## Honest Media Readiness",
            "",
            "The studio never calls a voice or likeness asset rendered until a configured engine returns an asset reference. Capture, consent, and local previews work independently of a paid service.",
            "",
            "## Guardrails",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in registry["release_guardrails"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = build_registry()
    if args.check:
        if not OUT_JSON.exists() or not OUT_MD.exists():
            raise SystemExit("Studio outputs are missing. Run without --check first.")
        current = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        if current != registry:
            raise SystemExit("Studio registry is stale. Regenerate it.")
        print(json.dumps({"ok": True, "project_types": len(current["project_types"])}, indent=2))
        return 0
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(registry)
    print(json.dumps({"ok": True, "output": str(OUT_JSON.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
