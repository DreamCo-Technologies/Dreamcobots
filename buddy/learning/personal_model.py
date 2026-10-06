"""Personal model intake. A user may train toward their own model.

Sources can be a link, a book citation, or a YouTube URL. The note is the
user's lesson, not a copied book or transcript. A final view still needs
three sources, and no weights are downloaded.
"""

from __future__ import annotations

from buddy.learning.permissioned_views import PermissionError, grant, learn


def add_source(kind: str, subject: str, source: str, claim: str) -> dict:
    if kind not in {"internet", "book", "youtube", "user"}:
        raise PermissionError(f"unknown source kind: {kind}")
    if kind in {"internet", "youtube"} and not source.startswith("https://"):
        raise PermissionError("internet and video sources need an https url")
    if kind == "book" and len(source) < 8:
        raise PermissionError("a book source needs a title and author")
    return {"kind": kind, "subject": subject, "source": source, "claim": claim, "stance": "agree", "copied": False}


def personal_model(subject: str, sources: list[dict], grants: list[dict]) -> dict:
    grant_row = next((row for row in grants if row["action"] == "train" and row["subject"] == subject and row["allowed"]), None)
    if grant_row is None:
        raise PermissionError("personal training needs a train grant")
    report = learn(subject, sources, grants)
    report["own_model"] = True
    report["weights_downloaded"] = False
    report["production_trained"] = False
    return report
