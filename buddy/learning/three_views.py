"""Optional three-perspective answers.

A user can send one question. If multi_view is on, Buddy adds two contrasting
views of its own. Those added views are labeled generated, not live research.
"""

from __future__ import annotations

from buddy.learning.permissioned_views import learn


def answer(subject: str, question: str, grants: list[dict], multi_view: bool = False) -> dict:
    views = [{"source": "user", "claim": question, "stance": "agree"}]
    if multi_view:
        views.append({"source": "counterexample", "claim": f"The opposite of: {question}", "stance": "conflict"})
        views.append({"source": "measured", "claim": f"What would have to be measured before accepting: {question}", "stance": "agree"})
    if not multi_view or len({row["source"] for row in views}) < 3:
        return {"subject": subject, "question": question, "perspectives": views, "final": False, "multi_view": multi_view}
    report = learn(subject, views, grants)
    report["question"] = question
    report["perspectives"] = views
    report["generated_views"] = True
    report["live_research"] = False
    return report
