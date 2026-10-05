"""Daily Buddy profile. It scans labels, not private accounts.

A profile is in Buddy's image only as a local summary. It is not a frontier
model, and it does not log into ChatGPT, GitHub, or Hugging Face.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from buddy.accounts.training_sources import EXPERTS, catalog
from buddy.learning.permissioned_views import PermissionError, grant, learn


def profile(note: str, allowed: bool, hf_model: str = "org/model") -> dict:
    if not allowed:
        raise PermissionError("a daily profile needs permission")
    sources = [{"source": name, "claim": f"{name} view of: {note}", "stance": "conflict" if name == "counterexample" else "agree"} for name in EXPERTS[:3]]
    report = learn("buddy-profile", sources, [grant("train", "buddy-profile", True)])
    data = catalog()
    report.update({"hf_model": hf_model, "weights_downloaded": False, "accounts_logged_in": False, "frontier_claim": False, "kinds": len(data["kinds"])})
    return report


def main() -> int:
    report = profile("daily scan", True)
    path = ROOT / "reports" / "BUDDY_DAILY_PROFILE.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"kinds": report["kinds"], "frontier_claim": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
