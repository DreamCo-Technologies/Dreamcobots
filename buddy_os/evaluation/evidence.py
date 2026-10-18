"""Evidence assessment, transfer, calibration, distillation and promotion gates.

Scores describe a pinned suite and exact system configuration, never general AGI.
Validation cannot prove absence of unknown proprietary pretraining contamination.
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from statistics import mean

from .review import POLICY, digest, finite

HASH = re.compile(r"^[a-f0-9]{64}$")
COMPONENTS = {"model", "policy", "router", "retrieval"}


def contamination(evaluation, training):
    """Compare supplied corpora only; normalized exact and near duplicates fail."""
    normalize = lambda s: " ".join(re.findall(r"\w+", s.casefold()))
    collisions = []
    for item in evaluation:
        for trained in training:
            exact_hash = bool(item.get("hash") and item.get("hash") == trained.get("hash"))
            same_family = bool(item.get("family") and item.get("family") == trained.get("family"))
            a, b = normalize(item.get("text", "")), normalize(trained.get("text", ""))
            near = bool(a and b and SequenceMatcher(None, a, b).ratio() >= 0.85)
            if exact_hash or same_family or near:
                collisions.append({"eval_id": item.get("id"), "training_id": trained.get("id"), "reason": "hash/family/near-duplicate"})
    return {"passed": not collisions, "collisions": collisions, "scope": "supplied training corpus only; unknown pretraining exposure is not ruled out"}


def calibration(samples, bins=10):
    if not samples:
        return {"status": "untested", "count": 0, "brier": None, "ece": None, "coverage": None, "selective_accuracy": None, "abstention_error": None}
    for row in samples:
        if not finite(row.get("confidence"), 0, 1) or any(type(row.get(k)) is not bool for k in ("correct", "abstained", "should_abstain")):
            raise ValueError("Calibration requires probabilities and observed binary outcomes")
    if type(bins) is not int or not 1 <= bins <= 100:
        raise ValueError("Invalid bin count")
    groups = defaultdict(list)
    for row in samples:
        groups[min(bins - 1, int(row["confidence"] * bins))].append(row)
    n = len(samples)
    answered = [r for r in samples if not r["abstained"]]
    return {"status": "measured", "count": n,
            "brier": mean((r["confidence"] - int(r["correct"])) ** 2 for r in samples),
            "ece": sum(len(g) / n * abs(mean(r["confidence"] for r in g) - mean(r["correct"] for r in g)) for g in groups.values()),
            "coverage": len(answered) / n,
            "selective_accuracy": mean(r["correct"] for r in answered) if answered else None,
            "abstention_error": mean(r["abstained"] != r["should_abstain"] for r in samples)}


def help_required(confidence, *, evidence_present, supported, high_impact=False):
    return (not finite(confidence, 0, 1) or confidence < 0.8 or evidence_present is not True
            or supported is not True or high_impact is True)


def assess(run):
    errors = []
    required = {"id", "schema", "capability", "subject", "components", "suite_id", "suite_version", "suite_hash", "dataset_hash", "grader_version", "seed", "hardware", "runtime", "timestamp", "license_review", "contamination", "cases", "expected_cases", "baseline_id", "baseline_hash", "simulated", "config_hash", "artifacts", "training_corpus_hash", "calibration", "red_team"}
    if not isinstance(run, dict):
        return {"status": "untested", "errors": ["run must be an object"], "eligible": False}
    errors += [f"missing {k}" for k in sorted(required - set(run))]
    if run.get("schema") != "dreamco.general_intelligence_run.v1":
        errors.append("wrong schema")
    if run.get("capability") not in {c["id"] for c in POLICY["capabilities"]}:
        errors.append("unknown capability")
    for key in ("suite_hash", "dataset_hash", "config_hash", "baseline_hash", "training_corpus_hash"):
        if not isinstance(run.get(key), str) or not HASH.fullmatch(run[key]):
            errors.append(f"invalid {key}")
    for key in ("id", "subject", "suite_id", "suite_version", "grader_version", "hardware", "runtime", "baseline_id"):
        if not isinstance(run.get(key), str) or not run[key].strip():
            errors.append(f"missing reproducibility field {key}")
    if type(run.get("seed")) is not int:
        errors.append("seed must be an integer")
    components = run.get("components", {})
    if not isinstance(components, dict) or set(components) != COMPONENTS or not all(isinstance(v, str) and v.strip() for v in components.values()):
        errors.append("exact model/policy/router/retrieval revisions required")
    try:
        stamp = datetime.fromisoformat(run.get("timestamp", "").replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp > datetime.now(timezone.utc):
            errors.append("timestamp is timezone-free or in the future")
    except (ValueError, TypeError):
        errors.append("invalid timestamp")
    if run.get("simulated") is not False:
        errors.append("simulated or unspecified execution")
    rights = run.get("license_review", {})
    if not isinstance(rights, dict) or rights.get("allowed") is not True or not rights.get("reviewer") or not rights.get("source"):
        errors.append("dataset license review required")
    scan = run.get("contamination", {})
    if not isinstance(scan, dict) or scan.get("passed") is not True or scan.get("collisions") != [] or not scan.get("scope"):
        errors.append("contamination scan missing or failed")
    artifacts = run.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts or any(not isinstance(a, dict) or not HASH.fullmatch(str(a.get("sha256", ""))) or not a.get("path") for a in artifacts):
        errors.append("content-addressed runtime artifacts required")
    cases = run.get("cases", [])
    if not isinstance(cases, list):
        cases = []
        errors.append("cases must be a list")
    expected = run.get("expected_cases", [])
    if not isinstance(expected, list) or not expected or any(not isinstance(i, str) for i in expected) or len(expected) != len(set(expected)):
        errors.append("unique preregistered case ids required")
        expected = []
    if any(not isinstance(c, dict) for c in cases):
        errors.append("invalid case")
        cases = []
    counts = defaultdict(set)
    seen = set()
    for index, case in enumerate(cases):
        prefix = f"case {index}"
        identity = (case.get("id"), case.get("repetition"))
        if not isinstance(identity[0], str) or type(identity[1]) is not int:
            errors.append(f"{prefix}: invalid identity")
            continue
        if identity in seen:
            errors.append(f"{prefix}: duplicate repetition")
        seen.add(identity)
        counts[identity[0]].add(identity[1])
        if case.get("split") not in {"holdout", "transfer"} or case.get("withheld_from_training") is not True or not case.get("family"):
            errors.append(f"{prefix}: held-out task family required")
        if not HASH.fullmatch(str(case.get("fixture_hash", ""))) or not HASH.fullmatch(str(case.get("response_hash", ""))):
            errors.append(f"{prefix}: fixture/response hashes missing")
        for metric in ("quality", "safety", "factuality"):
            if not finite(case.get(metric), 0, 1):
                errors.append(f"{prefix}: invalid {metric}")
        for metric in ("cost_usd", "latency_ms", "runtime_ms"):
            if not finite(case.get(metric)):
                errors.append(f"{prefix}: invalid {metric}")
        if type(case.get("human_interventions")) is not int or case["human_interventions"] < 0 or type(case.get("external_assistance")) is not bool:
            errors.append(f"{prefix}: assistance/intervention log missing")
    if set(counts) != set(expected) or len(counts) < POLICY["minimum_independent_tasks"]:
        errors.append("missing preregistered task coverage")
    if any(len(v) < POLICY["minimum_repetitions"] for v in counts.values()):
        errors.append("insufficient independent repetitions")
    if not any(c.get("split") == "transfer" and c.get("cross_domain") is True for c in cases):
        errors.append("cross-domain transfer evidence required")
    if len({c.get("family") for c in cases if isinstance(c.get("family"), str)}) < POLICY["minimum_independent_tasks"]:
        errors.append("insufficient independent task families")
    try:
        cal = calibration(run.get("calibration", []))
        if cal["status"] == "untested" or cal["ece"] > POLICY["maximum_calibration_error"] or cal["abstention_error"] > POLICY["maximum_abstention_error"]:
            errors.append("calibration/abstention gate not passed")
    except (ValueError, TypeError, KeyError):
        cal = calibration([])
        errors.append("invalid calibration samples")
    red = run.get("red_team", {})
    if not isinstance(red, dict) or any(red.get(k) is not True for k in POLICY["red_team"]):
        errors.append("red-team coverage incomplete or failed")
    measurable = [c for c in cases if all(finite(c.get(k), 0, 1) for k in ("quality", "safety", "factuality"))]
    metrics = {k: mean(c[k] for c in measurable) if measurable else None for k in ("quality", "safety", "factuality")}
    if measurable and any(c["quality"] < POLICY["pass_threshold"] or c["safety"] != 1 or c["factuality"] < POLICY["pass_threshold"] for c in measurable):
        errors.append("quality, factuality or safety regression")
    if any(c.get("external_assistance") is True or c.get("human_interventions", 0) != 0 for c in cases):
        errors.append("assisted results require separate reporting; independent capability unproven")
    metrics["human_intervention_rate"] = mean(c.get("human_interventions", 0) > 0 for c in cases) if cases else None
    return {"status": "partial" if cases else "untested", "eligible": not errors,
            "errors": sorted(set(errors)), "metrics": metrics, "calibration": cal,
            "truth": "Bundle validation is not independent artifact verification or an AGI claim."}


def verify_artifacts(run, root):
    """Reject traversal, symlinks outside evidence root, absent/mismatched artifacts."""
    import hashlib
    root = root.resolve()
    artifacts = run.get("artifacts", [])
    if not artifacts:
        return False
    for artifact in artifacts:
        try:
            path = (root / artifact["path"]).resolve()
            path.relative_to(root)
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
                return False
        except (ValueError, KeyError, TypeError, OSError):
            return False
    return True


def promotion(champion, challenger):
    """Advisory only. A fresh model_promotion action is still mandatory."""
    a, b = assess(champion), assess(challenger)
    keys = ("suite_id", "suite_version", "suite_hash", "dataset_hash", "grader_version", "seed", "hardware", "runtime", "expected_cases")
    comparable = all(champion.get(k) == challenger.get(k) for k in keys)
    baseline_matches = challenger.get("baseline_id") == champion.get("id") and challenger.get("baseline_hash") == digest(champion)
    approved_for_review = a["eligible"] and b["eligible"] and comparable and baseline_matches
    deltas = {k: b["metrics"][k] - a["metrics"][k] if a.get("metrics", {}).get(k) is not None and b.get("metrics", {}).get(k) is not None else None for k in ("quality", "safety", "factuality")}
    regression_free = all(v is not None and v >= 0 for v in deltas.values())
    if approved_for_review:
        old = {(c["id"], c["repetition"]): c for c in champion["cases"]}
        regression_free &= all((c["id"], c["repetition"]) in old and all(c[k] >= old[(c["id"], c["repetition"])][k] for k in deltas) for c in challenger["cases"])
    return {"status": "human_review_required" if approved_for_review and regression_free else "rejected",
            "promoted": False, "deltas": deltas, "comparable": comparable,
            "rollback_components": champion.get("components"), "candidate_components": challenger.get("components"),
            "reason": "Matched baselines, per-task regressions, artifact verification and one-action human approval are required."}


def distill(run):
    assessment = assess(run)
    return {"source_run": run.get("id"), "source_hash": digest(run), "provenance": run.get("artifacts", []),
            "status": "lesson_draft_requires_review", "outcome": "passed_gates" if assessment["eligible"] else "failed_or_incomplete",
            "beginner": f"This {run.get('capability', 'unclassified')} evaluation contains {len(run.get('cases', []))} measured or attempted cases. Its current status is {assessment['status']}; this does not establish general intelligence.",
            "intermediate": f"Observed quality: {assessment.get('metrics', {}).get('quality')}. Compare exact component revisions, fixture hashes and failed checks before proposing a training change.",
            "expert": f"The evidence validator found {len(assessment['errors'])} blocking conditions. Analyze family leakage and per-task regression before changing router, retrieval or model weights.",
            "failure_analysis": assessment["errors"],
            "exercise": "Create a new training-only example in a different task family.",
            "quiz": "Which evidence would falsify this lesson? Which action needs approval?",
            "misconception": "A passing example or multi-model orchestration proves general intelligence.",
            "training_candidate": {"eligible": False, "reason": "Evaluation and holdout examples never enter training; review rights and use disjoint families."},
            "benchmark_update": {"status": "proposed", "reason": "Review gaps and version the next suite without rewriting this baseline."}}


def claim_gate(text, evidence_hash, store, action_id):
    """Even marketing signoff cannot turn absent evidence into an AGI proof."""
    if not isinstance(text, str) or not HASH.fullmatch(str(evidence_hash)):
        return False
    try:
        review = store.get(action_id)
        store.audit()
    except (ValueError, AttributeError):
        return False
    action = review.get("action", {})
    return (review.get("status") == "approved" and (review.get("expires") or 0) > __import__("time").time()
            and action.get("action_class") == "marketing_claim" and action.get("parameters") == {"claim_text": text, "evidence_hash": evidence_hash}
            and review.get("hash") == digest(action) and bool(review.get("reviewer")))


def debate_assessment(rounds):
    roles = {r.get("role") for r in rounds}
    complete = {"proposer", "critic", "reviewer"} <= roles and all(r.get("model_version") and r.get("evidence") and r.get("independent_first_pass") is True for r in rounds)
    return {"status": "human_review_required" if complete else "incomplete", "rounds": rounds,
            "weights_changed": False, "unresolved_objections": [o for r in rounds for o in r.get("objections", [])],
            "truth": "Multi-model orchestration is not training or modification of proprietary weights."}
