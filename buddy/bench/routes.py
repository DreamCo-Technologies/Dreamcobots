#!/usr/bin/env python3
"""Routes a user can choose. Choosing one does not run it."""
from __future__ import annotations

import json

METRICS = [
    ("exactness", "Exact match"), ("exactness", "Accuracy"), ("exactness", "Token accuracy"),
    ("exactness", "Precision"), ("exactness", "Recall"), ("exactness", "F1"),
    ("exactness", "Macro F1"), ("exactness", "Micro F1"), ("ranking", "ROC AUC"),
    ("ranking", "PR AUC"), ("ranking", "Mean reciprocal rank"), ("ranking", "nDCG"),
    ("calibration", "Expected calibration error"), ("calibration", "Brier score"),
    ("language", "Perplexity"), ("language", "Bits per byte"), ("language", "Cross entropy"),
    ("language", "BLEU"), ("language", "chrF"), ("language", "TER"), ("language", "METEOR"),
    ("language", "ROUGE-1"), ("language", "ROUGE-2"), ("language", "ROUGE-L"),
    ("language", "BERTScore"), ("language", "BLEURT"), ("language", "COMET"),
    ("exams", "MMLU accuracy"), ("exams", "MMLU-Pro"), ("exams", "GPQA"),
    ("exams", "GSM8K exact match"), ("exams", "MATH"), ("exams", "HellaSwag"),
    ("exams", "ARC"), ("exams", "Winogrande"), ("exams", "TruthfulQA"),
    ("exams", "IFEval"), ("exams", "BBH"), ("exams", "HumanEval pass@1"),
    ("exams", "HumanEval pass@k"), ("exams", "MBPP"), ("exams", "SWE-bench resolved"),
    ("exams", "MT-Bench"), ("exams", "Arena Elo"), ("speech", "Word error rate"),
    ("speech", "Character error rate"), ("speech", "MOS"), ("speech", "PESQ"), ("speech", "STOI"),
    ("vision", "FID"), ("vision", "Inception score"), ("vision", "CLIP score"),
    ("vision", "LPIPS"), ("vision", "PSNR"), ("vision", "SSIM"), ("vision", "NIQE"),
    ("vision", "mAP"), ("vision", "IoU"), ("vision", "AP50"),
    ("safety", "Refusal rate"), ("safety", "Toxicity rate"), ("safety", "Jailbreak rate"),
    ("safety", "Bias gap"), ("safety", "Hallucination rate"), ("safety", "Citation support"),
    ("cost", "Latency p50"), ("cost", "Latency p95"), ("cost", "Time to first token"),
    ("cost", "Tokens per second"), ("cost", "Peak memory GB"), ("cost", "Cost per 1k tokens"),
    ("robustness", "Paraphrase drop"), ("robustness", "Noise drop"), ("robustness", "Contamination flag"),
]

FRAMEWORKS = [
    ("python", "pytest"), ("python", "unittest"), ("python", "doctest"), ("python", "hypothesis"),
    ("python", "tox"), ("python", "nox"), ("python", "coverage.py"), ("python", "mutmut"),
    ("python", "bandit"), ("python", "ruff"), ("python", "mypy"), ("python", "behave"),
    ("python", "pytest-bdd"), ("javascript", "node:test"), ("javascript", "jest"),
    ("javascript", "vitest"), ("javascript", "mocha"), ("javascript", "jasmine"), ("javascript", "ava"),
    ("javascript", "playwright"), ("javascript", "cypress"), ("javascript", "selenium"),
    ("javascript", "puppeteer"), ("javascript", "webdriverio"), ("javascript", "testing-library"),
    ("javascript", "eslint"), ("javascript", "tsc"), ("javascript", "fast-check"),
    ("javascript", "c8"), ("javascript", "stryker"), ("browser", "axe-core"), ("browser", "pa11y"),
    ("browser", "lighthouse"), ("load", "k6"), ("load", "locust"), ("load", "artillery"),
    ("load", "vegeta"), ("contract", "pact"), ("contract", "schemathesis"),
    ("other", "junit"), ("other", "testng"), ("other", "cargo test"), ("other", "go test"),
    ("other", "gtest"), ("other", "catch2"), ("other", "rspec"), ("other", "phpunit"),
    ("other", "xunit"), ("other", "nunit"), ("other", "robot framework"), ("other", "appium"),
]


def routes() -> dict:
    metrics = [{"id": name.lower().replace(" ", "-").replace("@", ""), "family": family, "name": name, "ran": False} for family, name in METRICS]
    frameworks = [{"id": name.lower().replace(" ", "-").replace(":", ""), "family": family, "name": name, "ran": False} for family, name in FRAMEWORKS]
    ids = [row["id"] for row in metrics + frameworks]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Two routes share an id.")
    return {
        "metrics": metrics,
        "frameworks": frameworks,
        "choosing_runs_them": False,
        "live_scores": 0,
    }


if __name__ == "__main__":
    made = routes()
    assert len(made["metrics"]) >= 60 and len(made["frameworks"]) >= 40
    assert made["choosing_runs_them"] is False and made["live_scores"] == 0
    print(json.dumps({"metrics": len(made["metrics"]), "frameworks": len(made["frameworks"]), "ran": False}))
