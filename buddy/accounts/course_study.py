"""Permissioned course study. A site is not fetched unless the user allows it."""

from __future__ import annotations

from buddy.learning.permissioned_views import PermissionError, grant, learn

SITES = ["codecademy", "khan academy", "freecodecamp", "mit opencourseware", "osha", "union training", "youtube"]


def study(site: str, note: str, allowed: bool) -> dict:
    if site not in SITES:
        raise PermissionError(f"unknown site: {site}")
    if not allowed:
        raise PermissionError("course study needs permission")
    grants = [grant("train", site, True)]
    views = [
        {"source": "user", "claim": note, "stance": "agree"},
        {"source": "course", "claim": f"The course claim for {site}", "stance": "agree"},
        {"source": "counterexample", "claim": f"What {site} does not prove", "stance": "conflict"},
    ]
    report = learn(site, views, grants)
    report["fetched"] = False
    report["copied"] = False
    return report
