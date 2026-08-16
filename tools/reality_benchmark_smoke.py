"""Executable smoke tests for Buddy's reality-grounding contract.

These tests validate the benchmark *protocol* using deterministic fixtures.
They do not claim to measure a model's factuality; model scoring belongs to a
separate evaluator that supplies actual responses and evidence.
"""
from __future__ import annotations

import json
from pathlib import Path

SUITE = Path("config/reality_benchmark_suite.json")

REQUIRED_CATEGORIES = {
    "known_fact_retrieval",
    "unknown_fact_abstention",
    "false_premise_detection",
    "citation_entailment",
    "source_freshness",
    "real_vs_simulated_classification",
    "adversarial_hallucination_resistance",
}
REQUIRED_GATES = {
    "must_not_claim_unknown_as_verified",
    "must_label_simulation",
    "must_preserve_source_provenance",
    "high_risk_claims_require_verification",
    "regression_required_before_promotion",
}


def main() -> None:
    suite = json.loads(SUITE.read_text(encoding="utf-8"))
    categories = set(suite.get("test_categories", []))
    gates = suite.get("gates", {})

    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    if missing_categories:
        raise SystemExit(f"Missing required reality categories: {missing_categories}")

    missing_gates = sorted(g for g in REQUIRED_GATES if gates.get(g) is not True)
    if missing_gates:
        raise SystemExit(f"Missing required reality gates: {missing_gates}")

    scores = suite.get("scores", {})
    if not scores or any(value is not None for value in scores.values()):
        # Contract may eventually contain recorded results, but smoke validation
        # should never mistake configuration values for model evaluation.
        print("Reality suite contains recorded score fields; model results require evaluator evidence.")

    print("Reality benchmark protocol: PASS")
    print(f"Categories: {len(categories)}")
    print(f"Gates: {len(REQUIRED_GATES)}")


if __name__ == "__main__":
    main()
