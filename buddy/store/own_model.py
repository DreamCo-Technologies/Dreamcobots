#!/usr/bin/env python3
"""Sell a customer their own fine-tune. Never sell someone else's base weights."""
from __future__ import annotations

import json
import re

SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}/[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
REFUSED = (
    "copy gpt",
    "copy claude",
    "distill gpt",
    "distill claude",
    "proprietary weights",
    "closed weights",
    "gpt astra",
    "claude mythos",
)


def sell_own_model(base_id: str, source: str, license_lets_customer_keep: bool, customer_owns_data: bool) -> dict:
    text = f"{base_id} {source}".lower().replace("-", " ").replace("_", " ").replace("/", " ")
    for phrase in REFUSED:
        if phrase in text:
            return {"for_sale": False, "reason": "Closed frontier models are not yours to sell."}
    if source not in {"huggingface", "github"}:
        return {"for_sale": False, "reason": "The base has to be a public Hugging Face model or a public GitHub model."}
    if not SLUG.match((base_id or "").strip()):
        return {"for_sale": False, "reason": "Use a public id like organization/model-name."}
    if not license_lets_customer_keep or not customer_owns_data:
        return {
            "for_sale": False,
            "reason": "You can sell the customer's own fine-tune only when the base license allows it and the customer owns the training data.",
        }
    clean = base_id.strip()
    url = f"https://huggingface.co/{clean}" if source == "huggingface" else f"https://github.com/{clean}"
    return {
        "for_sale": True,
        "sells_base_weights": False,
        "trains_here": False,
        "what_customer_buys": "A plan, then a fine-tune they own after it is trained on data they own.",
        "what_customer_does_not_buy": "The starting weights. Those stay under the original open-weight license.",
        "base_url": url,
        "reason": "Offer accepted as a customer-owned model plan. The base model is not the product.",
    }


def sell_wrapper_until_ready(
    base_id: str,
    source: str,
    license_lets_customer_keep: bool,
    customer_owns_data: bool,
    task: str,
    customer_model_passed: bool,
) -> dict:
    """Sell a wrapper while their model is not ready. Stop when a hidden test passes."""
    base = sell_own_model(base_id, source, license_lets_customer_keep, customer_owns_data)
    if not base["for_sale"]:
        base["product"] = "none"
        return base
    if not (task or "").strip():
        return {"for_sale": False, "product": "none", "reason": "Name the task the wrapper is covering."}
    if customer_model_passed:
        return {
            "for_sale": True,
            "product": "customer_model",
            "wrapper_for_sale": False,
            "sells_base_weights": False,
            "trains_here": False,
            "task": task.strip(),
            "reason": "Their model passed the hidden test, so the wrapper is no longer the product. The base weights are still not yours to sell.",
        }
    return {
        "for_sale": True,
        "product": "wrapper",
        "wrapper_for_sale": True,
        "sells_base_weights": False,
        "trains_here": False,
        "task": task.strip(),
        "base_url": base["base_url"],
        "reason": "Sell the wrapper for this task. It uses an open base the license allows. Retire the wrapper after their own model passes a hidden test.",
    }


if __name__ == "__main__":
    closed = sell_own_model("org/distill-claude", "huggingface", True, True)
    assert closed["for_sale"] is False
    stolen = sell_own_model("org/model", "huggingface", False, True)
    assert stolen["for_sale"] is False
    good = sell_own_model("org/open-model", "huggingface", True, True)
    assert good["for_sale"] is True and good["sells_base_weights"] is False and good["trains_here"] is False
    github = sell_own_model("org/open-weights", "github", True, True)
    assert github["base_url"].startswith("https://github.com/")
    assert sell_own_model("org/model", "secret", True, True)["for_sale"] is False
    wrapper = sell_wrapper_until_ready("org/open-model", "huggingface", True, True, "answer support mail", False)
    ready = sell_wrapper_until_ready("org/open-model", "huggingface", True, True, "answer support mail", True)
    assert wrapper["product"] == "wrapper" and wrapper["sells_base_weights"] is False
    assert ready["product"] == "customer_model" and ready["wrapper_for_sale"] is False
    assert sell_wrapper_until_ready("org/open-model", "huggingface", True, True, "  ", False)["for_sale"] is False
    print(json.dumps(wrapper))
