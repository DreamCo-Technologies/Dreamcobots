#!/usr/bin/env python3
"""Paid-training boot camp. It does not train a frontier model by itself."""
from __future__ import annotations

import json

TARGET = 1000
VIEWS = 10

REFUSED = (
    "copy gpt",
    "copy claude",
    "distill gpt",
    "distill claude",
    "gpt astra",
    "claude mythos",
    "mythos weights",
    "astra weights",
    "proprietary weights",
    "reproduce openai",
    "reproduce anthropic",
)


def mastery(resource_count: int, views_each: int, holdout_passed: bool) -> dict:
    reasons = []
    if resource_count < TARGET:
        reasons.append(f"{resource_count} of {TARGET} resources are in the catalogs")
    if views_each < VIEWS:
        reasons.append(f"{views_each} views is short of {VIEWS}")
    if not holdout_passed:
        reasons.append("no held-out exam has been passed")
    return {
        "mastered": not reasons,
        "resource_count": resource_count,
        "views_each": views_each,
        "holdout_passed": bool(holdout_passed),
        "blocking_reasons": reasons,
    }


def frontier(resource_count: int) -> dict:
    return {
        "gpt_or_claude_class_model_trained": False,
        "can_compete_today": False,
        "reason": (
            "No training run and no public score. "
            f"{resource_count} readings are not a model the size of GPT or Claude."
        ),
        "allowed_next_step": "Train an open model the customer has a license to run, then publish the score.",
    }


def review_paid_job(job: dict) -> dict:
    text = json.dumps(job).lower()
    for phrase in REFUSED:
        if phrase in text:
            return {
                "accepted": False,
                "trains_now": False,
                "reason": "This boot camp will not copy or distill another company's model.",
            }
    if job.get("customer_owns_data") is not True:
        return {"accepted": False, "trains_now": False, "reason": "The customer has to own the training data."}
    if job.get("held_out_test") is not True:
        return {"accepted": False, "trains_now": False, "reason": "Hold out a test the model does not study."}
    gate = mastery(int(job.get("resources_studied") or 0), int(job.get("views_each") or 0), False)
    return {
        "accepted": True,
        "trains_now": False,
        "mastery": gate,
        "frontier": frontier(int(job.get("resources_studied") or 0)),
        "reason": "Order accepted as a plan. Nothing is trained until the customer runs a licensed open model and records a score.",
    }


if __name__ == "__main__":
    assert mastery(600, 10, False)["mastered"] is False
    assert mastery(1000, 10, True)["mastered"] is True
    bad = review_paid_job({"goal": "distill Claude Mythos weights", "customer_owns_data": True, "held_out_test": True})
    assert bad["accepted"] is False
    good = review_paid_job({
        "goal": "fine-tune an open model on our support notes",
        "customer_owns_data": True,
        "held_out_test": True,
        "resources_studied": 600,
        "views_each": 10,
    })
    assert good["accepted"] is True and good["trains_now"] is False
    assert good["frontier"]["can_compete_today"] is False
    print("bootcamp gate ok")
