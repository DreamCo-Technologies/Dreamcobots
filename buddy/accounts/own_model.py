"""A user's own model profile.

Chatbots and social accounts are labels. Weights download only when the user
chooses it, and the owner study path never downloads them. More expert views
do not make this a frontier model.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.learning.permissioned_views import PermissionError, grant, learn

EXPERTS = ["official", "counterexample", "measured", "practitioner", "critic", "teacher", "security", "user"]
SOCIAL = ["x", "youtube", "instagram", "tiktok", "facebook", "linkedin", "discord", "reddit"]


def own_model(bots: list[str], social: dict[str, str], download_weights: bool, owner_study: bool) -> dict:
    if owner_study and download_weights:
        raise PermissionError("the owner study path does not download weights")
    unknown = [name for name in social if name not in SOCIAL]
    if unknown:
        raise PermissionError("unknown social account: " + ", ".join(unknown))
    views = [{"source": name, "claim": f"{name} view", "stance": "conflict" if name == "counterexample" else "agree"} for name in EXPERTS[:3]]
    report = learn("own-model", views, [grant("train", "own-model", True)])
    report.update({
        "bots": bots,
        "social": social,
        "download_weights": download_weights,
        "weights_downloaded": False,
        "owner_study": owner_study,
        "secrets_stored": False,
        "frontier_claim": False,
        "experts": EXPERTS,
    })
    return report


def build_plan(sections: int, duplicates: int) -> dict:
    return {
        "sections": sections,
        "duplicate_names": duplicates,
        "steps": ["keep the owner study path free of downloads", "store user bots and social labels", "add expert views to the profile", "do not delete duplicate files"],
        "frontier_claim": False,
        "deleted": False,
    }


def main() -> int:
    report = own_model(["buddy"], {"x": "handle"}, False, True)
    plan = build_plan(77, 119)
    (ROOT / "reports" / "OWN_MODEL_PROFILE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (ROOT / "reports" / "BUILD_PLAN.md").write_text("# Build plan\n\n" + "\n".join(f"- {step}" for step in plan["steps"]) + "\n\nNot a frontier claim. No files deleted.\n", encoding="utf-8")
    print(json.dumps({"experts": len(report["experts"]), "frontier_claim": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
