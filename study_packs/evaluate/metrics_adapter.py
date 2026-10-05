#!/usr/bin/env python3
"""Offline-first metric adapter for Buddy benches.

`compute(name, predictions, references)` uses Hugging Face `evaluate.load(name)`
only when HF_PACK_ALLOW_NETWORK=1 is set and `evaluate` is importable. Otherwise it
uses the pure-python fallbacks below, which follow the same definitions as the HF
metrics for exact_match, accuracy, f1 (binary) and pass@k (unbiased estimator from
the Codex paper, the same one HF `code_eval` uses). Every result says which backend
produced it so a scorecard never hides a fallback.
"""
from __future__ import annotations

import math
import os
import re
import string
from typing import Iterable, Sequence

NETWORK_FLAG = "HF_PACK_ALLOW_NETWORK"
FALLBACK_METRICS = ("exact_match", "accuracy", "f1", "pass_at_k")


def _normalize(text: str, ignore_case: bool, ignore_punctuation: bool) -> str:
    if ignore_case:
        text = text.lower()
    if ignore_punctuation:
        text = text.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", text).strip()


def exact_match(predictions: Sequence[str], references: Sequence[str],
                ignore_case: bool = False, ignore_punctuation: bool = False) -> float:
    _same_len(predictions, references)
    if not predictions:
        raise ValueError("empty predictions")
    hits = sum(_normalize(p, ignore_case, ignore_punctuation) == _normalize(r, ignore_case, ignore_punctuation)
               for p, r in zip(predictions, references))
    return hits / len(predictions)


def accuracy(predictions: Sequence, references: Sequence) -> float:
    _same_len(predictions, references)
    if not predictions:
        raise ValueError("empty predictions")
    return sum(p == r for p, r in zip(predictions, references)) / len(predictions)


def f1(predictions: Sequence[int], references: Sequence[int], pos_label: int = 1) -> float:
    _same_len(predictions, references)
    tp = sum(p == pos_label and r == pos_label for p, r in zip(predictions, references))
    fp = sum(p == pos_label and r != pos_label for p, r in zip(predictions, references))
    fn = sum(p != pos_label and r == pos_label for p, r in zip(predictions, references))
    if tp == 0:
        return 0.0
    precision, recall = tp / (tp + fp), tp / (tp + fn)
    return 2 * precision * recall / (precision + recall)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k for one problem: n samples, c correct."""
    if not 0 <= c <= n or k < 1 or k > n:
        raise ValueError("need 0 <= c <= n and 1 <= k <= n")
    if n - c < k:
        return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


def mean_pass_at_k(samples: Iterable[tuple[int, int]], k: int) -> float:
    rows = [pass_at_k(n, c, k) for n, c in samples]
    if not rows:
        raise ValueError("no problems")
    return sum(rows) / len(rows)


def _same_len(a: Sequence, b: Sequence) -> None:
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} predictions vs {len(b)} references")


def network_allowed() -> bool:
    return os.environ.get(NETWORK_FLAG) == "1"


def compute(name: str, predictions: Sequence, references: Sequence, **kwargs) -> dict:
    """Score with HF evaluate when allowed, else the local fallback."""
    if network_allowed():
        try:
            import evaluate  # type: ignore

            result = evaluate.load(name).compute(predictions=predictions, references=references, **kwargs)
            return {"metric": name, "backend": "hf_evaluate", "result": result}
        except Exception as exc:  # fall through, but say why
            reason = f"hf_evaluate failed: {exc.__class__.__name__}"
        else:
            reason = ""
    else:
        reason = f"{NETWORK_FLAG} not set"
    fallbacks = {"exact_match": exact_match, "accuracy": accuracy, "f1": f1}
    if name not in fallbacks:
        raise RuntimeError(f"no offline fallback for {name!r} ({reason}); set {NETWORK_FLAG}=1 with evaluate installed")
    value = fallbacks[name](predictions, references, **kwargs)
    return {"metric": name, "backend": "local_fallback", "reason": reason, "result": {name: value}}
