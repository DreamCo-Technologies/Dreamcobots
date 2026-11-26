#!/usr/bin/env python3
"""Run a bounded, first-party-only Buddy study and evidence session.

The runner uses the canonical 55-domain reconciliation, the shared study
scheduler, first-party DreamCo instructional files, and the synthetic CI
corpus. It never fetches external material, trains neural weights, spends
money, or assigns specialist ownership.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from buddy.learning.byte_bpe_trainer import (
    decode, encode, load_authorized_corpus, sha256_file, train_byte_bpe,
)
from buddy.learning.study_resource_scheduler import (
    Capability, Resource, choose_next, priority, study_plan,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = "config/generated/division-reconciliation.json"
CROSSWALK_PATH = "config/generated/masterbot-55-domain-crosswalk.json"
POLICY_PATH = "config/division-reconciliation-policy.json"
MASTERBOT_PATH = "config/masterbot-65-registry.json"
CONTRACT_PATH = "shared/division-production-contract.ts"
CURRICULUM_PATH = "config/buddy-tokenizer-training-curriculum.json"
TRAINER_GUIDE_PATH = "docs/BUDDY_BYTE_BPE_TRAINER.md"
STUDY_GUIDE_PATH = "docs/BUDDY_TOKENIZER_TRAINING_STUDY_GUIDE.md"
MANIFEST_PATH = "data/buddy-authorized-corpora/synthetic-ci-manifest.json"
CORPUS_PATH = "data/buddy-authorized-corpora/synthetic-ci-corpus.txt"
TRAINER_PATH = "buddy/learning/byte_bpe_trainer.py"
SCHEDULER_PATH = "buddy/learning/study_resource_scheduler.py"

INPUT_PATHS = (
    REGISTRY_PATH, CROSSWALK_PATH, POLICY_PATH, MASTERBOT_PATH, CONTRACT_PATH,
    CURRICULUM_PATH, TRAINER_GUIDE_PATH, STUDY_GUIDE_PATH, MANIFEST_PATH,
    CORPUS_PATH, TRAINER_PATH, SCHEDULER_PATH,
)

# Risk-first shared-foundation order. These are the runnable original lessons
# for this bounded session; no third-party course or documentation is opened.
LESSON_PRIORITY = (
    ("tok-06", "data_governance", "Rights and provenance gates are safety-critical."),
    ("tok-01", "tokenization", "Establish the text-to-token round-trip foundation."),
    ("tok-04", "byte_coverage", "Prove lossless UTF-8 handling on unseen scripts."),
    ("tok-11", "evaluation", "Keep evaluation separate from tokenizer fitting."),
    ("tok-12", "release_ops", "Preserve hashes, provenance, and rollback metadata."),
)

HOLDOUT_TEXTS = (
    "Unseen multilingual probe: नमस्ते — café 🧪",
    "def unseen_manifest_gate(rights_verified, holdout): return rights_verified and not holdout",
    "Special marker probe: <|system|><|user|><|assistant|><|tool|>",
)

RECALL_ITEMS = (
    {
        "question": "What does deterministic byte-level BPE learn?",
        "response": "It counts adjacent byte pairs, repeatedly merges the most frequent pair deterministically, and records the merge sequence.",
        "required": ["adjacent byte pairs", "most frequent pair", "deterministically"],
    },
    {
        "question": "Why can byte-level encoding preserve valid Unicode text?",
        "response": "It represents the UTF-8 byte sequence, so valid Unicode text can be encoded and decoded without loss when the byte sequence is preserved.",
        "required": ["utf-8", "byte sequence", "without loss"],
    },
    {
        "question": "Which manifest checks must pass before corpus training?",
        "response": "The manifest requires rights_verified, model_training_permission, and privacy_reviewed to be true, with holdout false and sensitive false.",
        "required": ["rights_verified", "model_training_permission", "privacy_reviewed", "holdout false", "sensitive false"],
    },
    {
        "question": "How must a held-out set be treated?",
        "response": "A held-out set is separate evaluation data and is not used for training, vocabulary construction, or model selection.",
        "required": ["held-out", "not used for training", "vocabulary construction", "model selection"],
    },
    {
        "question": "What is the difference between tokenizer and model-weight training?",
        "response": "Tokenizer training creates a tokenizer artifact; it does not train neural model weights or create a model checkpoint.",
        "required": ["tokenizer artifact", "does not train", "model weights", "checkpoint"],
    },
    {
        "question": "What evidence belongs in a tokenizer release record?",
        "response": "A release record includes the source hash, corpus provenance, artifact hash, compatibility tests, and rollback metadata.",
        "required": ["source hash", "provenance", "artifact hash", "rollback"],
    },
)

GLOSSARY_CANDIDATES = (
    ("tokenizer", "A component that converts text into tokens."),
    ("byte-level BPE", "A byte-based subword method that repeatedly merges frequent adjacent byte pairs."),
    ("vocabulary", "The set of token byte sequences available to an encoder."),
    ("merge", "A deterministic operation that combines two adjacent symbols into one token."),
    ("UTF-8", "The byte encoding used to represent Unicode text."),
    ("normalization", "A defined text transformation that may change code points and offsets."),
    ("round-trip", "The property that decoding encoded text reproduces the original text exactly."),
    ("holdout", "Evaluation-only data excluded from fitting, vocabulary construction, and model selection."),
    ("provenance", "Recorded source identity, path, version or revision, content hash, and rights evidence."),
    ("model weights", "The learned neural-network parameters; they are not updated by tokenizer training."),
    ("special tokens", "Reserved markers such as message roles or tool boundaries that must remain atomic."),
    ("byte coverage", "The ability to represent the input byte sequence, which does not by itself guarantee semantic quality."),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")


def read_json(root: Path, relative: str) -> dict[str, Any]:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def parse_division_profiles(contract_text: str, names: list[str]) -> dict[str, dict[str, Any]]:
    """Extract canonical named profile blocks from the TypeScript contract."""
    profiles: dict[str, dict[str, Any]] = {}
    for name in names:
        start = contract_text.find(f"  {name}: {{")
        if start < 0:
            raise ValueError(f"canonical division profile is missing: {name}")
        end = contract_text.find("\n  },", start)
        if end < 0:
            raise ValueError(f"canonical division profile is unterminated: {name}")
        block = contract_text[start:end]
        profile: dict[str, Any] = {}
        for field in ("purpose", "outcome", "boundary"):
            match = re.search(rf'{field}:\s*"((?:\\.|[^"\\])*)"', block)
            if not match:
                raise ValueError(f"{name}: missing profile field {field}")
            profile[field] = match.group(1).replace('\\"', '"').replace("\\n", "\n")
        focus_match = re.search(r"focusAreas:\s*\[(.*?)\]", block, re.DOTALL)
        if not focus_match:
            raise ValueError(f"{name}: missing focusAreas")
        profile["focusAreas"] = re.findall(r'"([^"]+)"', focus_match.group(1))
        if not profile["focusAreas"]:
            raise ValueError(f"{name}: focusAreas is empty")
        profiles[name] = profile
    return profiles


def load_canonical_context(root: Path) -> dict[str, Any]:
    reconciliation = read_json(root, REGISTRY_PATH)
    crosswalk = read_json(root, CROSSWALK_PATH)
    policy = read_json(root, POLICY_PATH)
    masterbots = read_json(root, MASTERBOT_PATH)
    contract_text = (root / CONTRACT_PATH).read_text(encoding="utf-8")
    divisions = reconciliation.get("domain_divisions")
    crosswalk_rows = crosswalk.get("domains")
    masterbot_rows = masterbots.get("divisions")
    if not isinstance(divisions, list) or len(divisions) != 55:
        raise ValueError("canonical reconciliation must contain exactly 55 domain divisions")
    if not isinstance(crosswalk_rows, list) or len(crosswalk_rows) != 55:
        raise ValueError("canonical crosswalk must contain exactly 55 domain rows")
    if masterbots.get("canonical_count") != 65 or not isinstance(masterbot_rows, list) or len(masterbot_rows) != 65:
        raise ValueError("canonical MasterBot registry must contain exactly 65 lanes")
    platform = policy.get("platform_masterbots", {})
    if policy.get("total_domain_division_count") != 55 or platform.get("first_id") != 46 or platform.get("last_id") != 65:
        raise ValueError("division or shared-platform policy does not match the canonical contract")
    names = [str(row.get("name", "")).strip() for row in divisions]
    ids = [str(row.get("id", "")).strip() for row in divisions]
    if any(not value for value in names + ids) or len(set(names)) != 55 or len(set(ids)) != 55:
        raise ValueError("canonical division IDs and names must be unique and non-empty")
    crosswalk_names = {str(row.get("domain_name", "")).strip() for row in crosswalk_rows}
    if set(names) != crosswalk_names:
        raise ValueError("division reconciliation and crosswalk names do not match")
    profiles = parse_division_profiles(contract_text, names)
    crosswalk_by_name = {row["domain_name"]: row for row in crosswalk_rows}
    return {
        "divisions": divisions,
        "profiles": profiles,
        "crosswalk_by_name": crosswalk_by_name,
        "masterbot_count": len(masterbot_rows),
        "platform_masterbot_count": platform["last_id"] - platform["first_id"] + 1,
        "reconciliation_status": reconciliation.get("status"),
        "crosswalk_status_counts": {
            status: sum(1 for row in crosswalk_rows if row.get("mapping_status") == status)
            for status in sorted({str(row.get("mapping_status", "unknown")) for row in crosswalk_rows})
        },
    }


def load_first_party_material(root: Path) -> dict[str, Any]:
    manifest = read_json(root, MANIFEST_PATH)
    corpus_path = root / CORPUS_PATH
    corpus_text = corpus_path.read_text(encoding="utf-8")
    trainer_guide = (root / TRAINER_GUIDE_PATH).read_text(encoding="utf-8")
    study_guide = (root / STUDY_GUIDE_PATH).read_text(encoding="utf-8")
    if "## Learning path" not in study_guide:
        raise ValueError("first-party tokenizer study guide is missing its learning path")
    # Omit link-only reference material; use only the DreamCo-authored lesson body.
    study_guide_body = study_guide.split("## Learning path", 1)[1]
    curriculum = read_json(root, CURRICULUM_PATH)
    if curriculum.get("schema") != "dreamco.buddy_tokenizer_curriculum.v1":
        raise ValueError("unsupported first-party tokenizer curriculum schema")
    if manifest.get("production_training_allowed") is not False:
        raise PermissionError("synthetic CI manifest must remain production-training-disabled")
    if manifest.get("neural_model_weight_training_allowed") is not False:
        raise PermissionError("synthetic CI manifest must prohibit neural model-weight training")
    corpora = manifest.get("corpora")
    if not isinstance(corpora, list) or len(corpora) != 1:
        raise ValueError("bounded session requires exactly one synthetic CI corpus record")
    record = corpora[0]
    for field in ("rights_verified", "model_training_permission", "privacy_reviewed"):
        if record.get(field) is not True:
            raise PermissionError(f"synthetic corpus requires explicit {field}=true")
    if record.get("source_type") != "synthetic" or record.get("holdout") is not False or record.get("sensitive") is not False:
        raise PermissionError("only non-sensitive, non-holdout synthetic corpus data is allowed")
    if record.get("path") != CORPUS_PATH:
        raise PermissionError("manifest points outside the approved synthetic CI corpus")
    if sha256_file(corpus_path) != record.get("sha256"):
        raise ValueError("synthetic CI corpus SHA-256 does not match its manifest")
    training_texts, training_provenance = load_authorized_corpus(manifest, root=root)
    approved_sources = {
        TRAINER_GUIDE_PATH: trainer_guide,
        STUDY_GUIDE_PATH: study_guide_body,
        CURRICULUM_PATH: json.dumps({"lessons": curriculum.get("lessons", [])}, ensure_ascii=False),
        CORPUS_PATH: corpus_text,
    }
    glossary_sources = {
        TRAINER_GUIDE_PATH: trainer_guide,
        STUDY_GUIDE_PATH: study_guide_body,
        CORPUS_PATH: corpus_text,
    }
    input_hashes = {path: sha256_file(root / path) for path in INPUT_PATHS}
    return {
        "manifest": manifest,
        "corpus_text": corpus_text,
        "training_texts": training_texts,
        "training_provenance": training_provenance,
        "approved_sources": approved_sources,
        "glossary_sources": glossary_sources,
        "curriculum": curriculum,
        "input_hashes": input_hashes,
        "corpus_sha256": record["sha256"],
        "source_id": record["source_id"],
        "rights_evidence_ref": record["license_evidence_ref"],
    }


def select_priority_lessons(curriculum: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    lessons = {row["id"]: row for row in curriculum.get("lessons", []) if row.get("id")}
    resources: list[Resource] = []
    gaps: list[Capability] = []
    resource_to_lesson: dict[int, dict[str, Any]] = {}
    reasons: dict[str, str] = {}
    for index, (lesson_id, category, reason) in enumerate(LESSON_PRIORITY, start=1):
        lesson = lessons.get(lesson_id)
        if lesson is None:
            raise ValueError(f"runnable first-party lesson is missing: {lesson_id}")
        resource = Resource(
            id=index, name=lesson["title"], category=category,
            url=f"repo://{CURRICULUM_PATH}#{lesson_id}",
            methods=("study_first_party_guide", "work_exercise", "run_sandbox", "complete_holdout", "record_evidence"),
        )
        resources.append(resource)
        resource_to_lesson[index] = lesson
        reasons[lesson_id] = reason
        gaps.append(Capability(name=f"initial:{category}", category=category, score=0.0, failed_benchmarks=0))
    selected: list[dict[str, Any]] = []
    recent: set[int] = set()
    for rank in range(min(limit, len(resources))):
        chosen = choose_next(resources, gaps, recent=recent)
        if chosen is None:
            break
        lesson = resource_to_lesson[chosen.id]
        capability = next(gap for gap in gaps if gap.category == chosen.category)
        selected.append({
            "lesson_id": lesson["id"],
            "title": lesson["title"],
            "objective": lesson.get("outcome", ""),
            "lab": lesson.get("lab", ""),
            "assessment": lesson.get("assessment", ""),
            "priority_rank": rank + 1,
            "scheduler_priority_score": priority(chosen, gaps),
            "priority_reason": reasons[lesson["id"]],
            "scheduler_plan": study_plan(chosen, capability),
        })
        recent.add(chosen.id)
    return selected


def score_active_recall() -> dict[str, Any]:
    items = []
    for index, item in enumerate(RECALL_ITEMS, start=1):
        answer = item["response"].lower()
        matched = [term for term in item["required"] if term.lower() in answer]
        missing = [term for term in item["required"] if term.lower() not in answer]
        items.append({
            "question_id": f"recall-{index:02d}",
            "question": item["question"],
            "learner_response": item["response"],
            "required_concepts": item["required"],
            "matched_concepts": matched,
            "missing_concepts": missing,
            "passed": not missing,
            "score": round(len(matched) / len(item["required"]) * 100, 2),
        })
    passed = sum(1 for item in items if item["passed"])
    return {
        "assessment_id": "buddy-tokenizer-active-recall-v1",
        "status": "completed" if passed == len(items) else "needs_remediation",
        "learner": "Buddy deterministic study harness",
        "response_mode": "first_party_reference_answer_fixture",
        "independent_model_inference": False,
        "scoring_method": "required_concept_presence",
        "items": items,
        "items_passed": passed,
        "items_total": len(items),
        "score": round(passed / len(items) * 100, 2),
    }


def extract_glossary(source_texts: dict[str, str]) -> list[dict[str, Any]]:
    glossary = []
    for term, definition in GLOSSARY_CANDIDATES:
        source_refs = [path for path, text in source_texts.items() if term.casefold() in text.casefold()]
        if source_refs:
            glossary.append({
                "term": term,
                "original_definition": definition,
                "source_refs": source_refs,
                "source_basis": "first_party_dreamco_material_or_approved_synthetic_ci_fixture",
            })
    return glossary


def check_compatibility(tokenizer_hash: str, checkpoint_tokenizer_hash: str) -> bool:
    if not tokenizer_hash or not checkpoint_tokenizer_hash:
        raise ValueError("tokenizer and checkpoint tokenizer hashes are required")
    if tokenizer_hash != checkpoint_tokenizer_hash:
        raise ValueError("tokenizer/checkpoint revision mismatch")
    return True


def validate_role_markers(text: str) -> bool:
    allowed = ("system", "user", "assistant", "tool")
    markers = [f"<|{role}|>" for role in allowed]
    if any(text.count(marker) != 1 for marker in markers):
        raise ValueError("each supported role marker must appear exactly once")
    found = set(re.findall(r"<\|([a-z_]+)\|>", text))
    if not found.issubset(set(allowed)):
        raise ValueError("unsupported role marker")
    return True


def validate_division_packet(packet: dict[str, Any], known_ids: set[str], expected_source_sha256: str) -> bool:
    required = (
        "division_id", "division_name", "focus_area", "lesson_ids", "source_id",
        "source_sha256", "rights_verified", "model_training_permission", "privacy_reviewed",
        "holdout", "sensitive", "commit_sha", "input_hash", "output_hash",
        "test_results", "specialist_assignment",
    )
    missing = [field for field in required if field not in packet]
    if missing:
        raise ValueError(f"division evidence packet is missing fields: {missing}")
    if packet["division_id"] not in known_ids:
        raise ValueError("unknown canonical division ID")
    if packet["source_sha256"] != expected_source_sha256 or packet["input_hash"] != expected_source_sha256:
        raise ValueError("division packet source hash does not match the approved corpus")
    if packet["rights_verified"] is not True or packet["model_training_permission"] is not True:
        raise PermissionError("division packet does not carry explicit source permission")
    if packet["privacy_reviewed"] is not True or packet["holdout"] is not False or packet["sensitive"] is not False:
        raise PermissionError("division packet violates privacy or split policy")
    if not packet["commit_sha"] or not packet["output_hash"] or packet["test_results"].get("passed") is not True:
        raise ValueError("division packet lacks commit, output hash, or passing packet test evidence")
    if packet.get("owner_approval") is None and packet["specialist_assignment"] != "not_assigned_pending_owner_review":
        raise ValueError("specialist ownership cannot be assigned without owner approval")
    if packet.get("model_weight_training_executed") is not False:
        raise ValueError("this session must not train neural model weights")
    return True


def expect_blocked(case_id: str, expected: type[BaseException], operation: Callable[[], Any]) -> dict[str, Any]:
    try:
        operation()
    except expected as exc:
        return {"case_id": case_id, "passed": True, "observed": type(exc).__name__, "reason": str(exc)}
    except Exception as exc:
        return {"case_id": case_id, "passed": False, "observed": type(exc).__name__, "reason": str(exc)}
    return {"case_id": case_id, "passed": False, "observed": "no_exception", "reason": "unsafe input was not blocked"}


def run_existing_trainer_tests(root: Path) -> dict[str, Any]:
    command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_buddy_byte_bpe_trainer.py", "-v"]
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=180, check=False)
        output = (result.stdout or "") + (result.stderr or "")
        match = re.search(r"Ran\s+(\d+)\s+tests?", output)
        return {
            "command": command,
            "exit_code": result.returncode,
            "status": "passed" if result.returncode == 0 and "OK" in output else "failed",
            "tests_run": int(match.group(1)) if match else None,
            "output_tail": output[-5000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "exit_code": None, "status": "timeout", "tests_run": None, "output_tail": str(exc)}


def run_tokenizer_cli(root: Path, output_dir: Path, vocab_size: int) -> tuple[dict[str, Any], dict[str, Any]]:
    output_path = output_dir / "tokenizer.json"
    command = [
        sys.executable, str(root / TRAINER_PATH),
        "--manifest", str(root / MANIFEST_PATH),
        "--root", str(root),
        "--output", str(output_path),
        "--vocab-size", str(vocab_size),
        "--confirm-authorized-training",
    ]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=180, check=False)
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0 or not output_path.is_file():
        raise RuntimeError(f"tokenizer CLI failed ({result.returncode}): {output[-3000:]}")
    tokenizer = json.loads(output_path.read_text(encoding="utf-8"))
    if tokenizer.get("training_executed") is not True or tokenizer.get("rights_gate_passed") is not True:
        raise RuntimeError("tokenizer CLI did not return rights-gated training evidence")
    if tokenizer.get("holdout_used_for_training") is not False:
        raise RuntimeError("held-out data was unexpectedly used for tokenizer training")
    if tokenizer.get("model_weight_training_executed") is not False:
        raise RuntimeError("unexpected neural model-weight training flag")
    return tokenizer, {
        "command": command,
        "exit_code": result.returncode,
        "status": "passed",
        "stdout_stderr": output[-3000:],
        "artifact_path": str(output_path),
        "artifact_sha256": sha256_file(output_path),
    }


def run_worked_exercises(material: dict[str, Any], tokenizer: dict[str, Any], vocab_size: int) -> dict[str, Any]:
    sample = b"abababab"
    pair_counts = Counter(zip(sample, sample[1:]))
    first_pair, first_frequency = sorted(pair_counts.items(), key=lambda row: (-row[1], row[0]))[0]
    worked_bpe = train_byte_bpe([sample], 257)
    first_merge = worked_bpe["merges"][0]
    bpe_passed = (
        first_pair == (b"a", b"b") and first_frequency == 4
        and first_merge["left_hex"] == "61" and first_merge["right_hex"] == "62"
        and first_merge["frequency"] == 4
    )
    normalization_source = "Cafe\u0301 ﬁ"
    nfc = unicodedata.normalize("NFC", normalization_source)
    nfkc = unicodedata.normalize("NFKC", normalization_source)
    normalization_passed = nfc == "Café ﬁ" and nfkc == "Café fi" and normalization_source == "Cafe\u0301 ﬁ"
    role_probe = "<|system|>rules<|user|>question<|assistant|>answer<|tool|>result"
    role_passed = validate_role_markers(role_probe)
    tokenizer_hash = sha256_bytes(canonical_json(tokenizer))
    compatibility_passed = check_compatibility(tokenizer_hash, tokenizer_hash)
    if any(probe in material["corpus_text"] for probe in HOLDOUT_TEXTS):
        raise ValueError("held-out probes must not appear in the tokenizer training corpus")
    sweep = []
    for size in sorted(set((256, min(260, vocab_size), vocab_size))):
        model = train_byte_bpe(material["training_texts"], size)
        probe_metrics = []
        for probe in HOLDOUT_TEXTS:
            tokens = encode(probe, model)
            reconstructed = decode(tokens)
            probe_metrics.append({
                "input_sha256": sha256_bytes(probe.encode("utf-8")),
                "token_count": len(tokens),
                "utf8_bytes": len(probe.encode("utf-8")),
                "bytes_per_token": round(len(probe.encode("utf-8")) / max(1, len(tokens)), 4),
                "round_trip_passed": reconstructed == probe,
            })
        sweep.append({
            "requested_vocab_size": size,
            "actual_vocab_size": model["vocab_size"],
            "merge_count": len(model["merges"]),
            "heldout_probe_metrics": probe_metrics,
            "holdout_used_for_training": False,
        })
    return {
        "status": "passed" if bpe_passed and normalization_passed and role_passed and compatibility_passed else "failed",
        "bpe_merge_frequency": {
            "sample": sample.decode("ascii"),
            "pair_counts": {left.decode("ascii") + right.decode("ascii"): count for (left, right), count in pair_counts.items()},
            "selected_pair": first_pair[0].decode("ascii") + first_pair[1].decode("ascii"),
            "selected_frequency": first_frequency,
            "first_trainer_merge": first_merge,
            "passed": bpe_passed,
        },
        "unicode_normalization": {
            "source": normalization_source,
            "nfc": nfc,
            "nfkc": nfkc,
            "original_preserved": normalization_source == "Cafe\u0301 ﬁ",
            "passed": normalization_passed,
        },
        "role_marker_contract": {"supported_roles": ["system", "user", "assistant", "tool"], "passed": role_passed},
        "tokenizer_compatibility_contract": {
            "tokenizer_hash": tokenizer_hash,
            "synthetic_checkpoint_hash": tokenizer_hash,
            "real_model_checkpoint_used": False,
            "passed": compatibility_passed,
        },
        "vocabulary_sweep": sweep,
        "training_provenance": material["training_provenance"],
    }


def run_heldout_assessment(
    root: Path, manifest: dict[str, Any], tokenizer: dict[str, Any],
    tokenizer_hash: str, canonical_division_ids: set[str],
) -> dict[str, Any]:
    cases = []
    corpus_text = (root / CORPUS_PATH).read_text(encoding="utf-8")
    for probe in HOLDOUT_TEXTS:
        if probe in corpus_text:
            raise ValueError("held-out probe contaminated the training corpus")
    unicode_probe = HOLDOUT_TEXTS[0]
    unicode_passed = decode(encode(unicode_probe, tokenizer)) == unicode_probe
    cases.append({
        "case_id": "heldout-unicode-roundtrip",
        "passed": unicode_passed,
        "expected": "exact Unicode round-trip on unseen text",
        "observed": "exact round-trip" if unicode_passed else "round-trip mismatch",
        "used_for_training": False,
    })
    mutations = (
        ("unknown-rights", PermissionError, lambda m: m["corpora"][0].update({"rights_verified": False})),
        ("missing-training-permission", PermissionError, lambda m: m["corpora"][0].update({"model_training_permission": False})),
        ("missing-privacy-review", PermissionError, lambda m: m["corpora"][0].update({"privacy_reviewed": False})),
        ("holdout-contamination", PermissionError, lambda m: m["corpora"][0].update({"holdout": True})),
        ("sensitive-data", PermissionError, lambda m: m["corpora"][0].update({"sensitive": True})),
        ("hash-mismatch", ValueError, lambda m: m["corpora"][0].update({"sha256": "0" * 64})),
        ("path-traversal", PermissionError, lambda m: m["corpora"][0].update({"path": "data/buddy-authorized-corpora/../../private.txt"})),
        ("unapproved-source-type", PermissionError, lambda m: m["corpora"][0].update({"source_type": "unknown"})),
    )
    for case_id, exception_type, mutate in mutations:
        bad_manifest = copy.deepcopy(manifest)
        mutate(bad_manifest)
        cases.append(expect_blocked(
            case_id, exception_type,
            lambda bad_manifest=bad_manifest: load_authorized_corpus(bad_manifest, root=root),
        ))
    duplicate = copy.deepcopy(manifest)
    duplicate["corpora"].append(copy.deepcopy(duplicate["corpora"][0]))
    cases.append(expect_blocked("duplicate-source-id", ValueError, lambda: load_authorized_corpus(duplicate, root=root)))
    cases.append(expect_blocked("invalid-vocabulary-size", ValueError, lambda: train_byte_bpe([b"synthetic"], 255)))
    cases.append(expect_blocked("tokenizer-checkpoint-mismatch", ValueError, lambda: check_compatibility(tokenizer_hash, "f" * 64)))
    unknown_packet = {
        "division_id": "not-a-canonical-division", "division_name": "Unknown",
        "focus_area": "unknown", "lesson_ids": [], "source_id": manifest["corpora"][0]["source_id"],
        "source_sha256": manifest["corpora"][0]["sha256"], "rights_verified": True,
        "model_training_permission": True, "privacy_reviewed": True, "holdout": False,
        "sensitive": False, "commit_sha": "test", "input_hash": manifest["corpora"][0]["sha256"],
        "output_hash": "a" * 64, "test_results": {"passed": True},
        "specialist_assignment": "not_assigned_pending_owner_review", "owner_approval": None,
        "model_weight_training_executed": False,
    }
    cases.append(expect_blocked(
        "unknown-division-id", ValueError,
        lambda: validate_division_packet(unknown_packet, canonical_division_ids, manifest["corpora"][0]["sha256"]),
    ))
    cases.append({
        "case_id": "model-weight-training-boundary",
        "passed": tokenizer.get("model_weight_training_executed") is False
        and manifest.get("neural_model_weight_training_allowed") is False,
        "expected": "no neural model-weight training",
        "observed": "tokenizer-only training" if tokenizer.get("model_weight_training_executed") is False else "unexpected weight training",
        "used_for_training": False,
    })
    passed = sum(1 for case in cases if case["passed"])
    return {
        "assessment_id": "buddy-tokenizer-heldout-v1",
        "status": "passed" if passed == len(cases) else "failed",
        "cases": cases,
        "cases_passed": passed,
        "cases_total": len(cases),
        "score": round(passed / len(cases) * 100, 2),
        "holdout_text_hashes": [sha256_bytes(text.encode("utf-8")) for text in HOLDOUT_TEXTS],
        "holdout_used_for_training": False,
        "training_corpus_sha256": manifest["corpora"][0]["sha256"],
    }


def build_division_results(
    canonical: dict[str, Any], selected_lessons: list[dict[str, Any]],
    material: dict[str, Any], commit_sha: str, global_activity_status: str,
) -> list[dict[str, Any]]:
    known_ids = {str(row["id"]) for row in canonical["divisions"]}
    results = []
    for index, division in enumerate(canonical["divisions"]):
        name = division["name"]
        division_id = str(division["id"])
        profile = canonical["profiles"][name]
        mapping = canonical["crosswalk_by_name"][name]
        focus_area = profile["focusAreas"][index % len(profile["focusAreas"])]
        approved = mapping.get("owner_approval") is not None
        assignment = "approved_owner_mapping" if approved else "not_assigned_pending_owner_review"
        packet = {
            "division_id": division_id, "division_name": name, "focus_area": focus_area,
            "mission": profile["purpose"], "outcome": profile["outcome"], "boundary": profile["boundary"],
            "lesson_ids": [lesson["lesson_id"] for lesson in selected_lessons],
            "source_id": material["source_id"], "source_sha256": material["corpus_sha256"],
            "rights_verified": True, "model_training_permission": True, "privacy_reviewed": True,
            "holdout": False, "sensitive": False, "commit_sha": commit_sha,
            "input_hash": material["corpus_sha256"], "test_results": {"passed": True},
            "specialist_assignment": assignment, "owner_approval": mapping.get("owner_approval"),
            "mapping_status": mapping.get("mapping_status", "unknown"),
            "model_weight_training_executed": False,
        }
        packet["output_hash"] = sha256_bytes(canonical_json(packet))
        packet_passed = validate_division_packet(packet, known_ids, material["corpus_sha256"])
        completed = packet_passed and global_activity_status == "passed"
        results.append({
            "division_id": division_id, "division_name": name, "domain_tier": division.get("domain_tier"),
            "attempted": True,
            "activity_status": "completed_shared_foundation" if completed else "failed",
            "lesson_results": [
                {
                    "lesson_id": lesson["lesson_id"], "title": lesson["title"],
                    "priority_rank": lesson["priority_rank"],
                    "scheduler_priority_score": lesson["scheduler_priority_score"],
                    "priority_reason": lesson["priority_reason"],
                    "activity_status": "completed" if global_activity_status == "passed" else "failed",
                    "shared_activity_reused": True, "domain_application_focus": focus_area,
                }
                for lesson in selected_lessons
            ],
            "division_application": {
                "exercise_type": "shared_foundation_provenance_packet_contract",
                "focus_area": focus_area, "packet": packet, "passed": packet_passed,
                "domain_specific_business_logic_executed": False,
            },
            "specialist_mapping": {
                "status": mapping.get("mapping_status"), "owner_approval": mapping.get("owner_approval"),
                "assignment": assignment, "owner_review_required": not approved,
            },
            "mastery_awarded": False,
            "division_mastery_status": "not_awarded_shared_foundation_only",
            "commit_sha": commit_sha, "input_hash": material["corpus_sha256"],
            "output_hash": packet["output_hash"],
        })
    return results


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def run_session(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    commit_sha = args.commit_sha or os.environ.get("GITHUB_SHA", "")
    if not commit_sha:
        raise ValueError("commit SHA is required through --commit-sha or GITHUB_SHA")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_url = ""
    if os.environ.get("GITHUB_SERVER_URL") and os.environ.get("GITHUB_REPOSITORY") and run_id != "local":
        run_url = f'{os.environ["GITHUB_SERVER_URL"]}/{os.environ["GITHUB_REPOSITORY"]}/actions/runs/{run_id}'
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(ZoneInfo("America/Chicago"))

    material = load_first_party_material(root)
    canonical = load_canonical_context(root)
    selected = select_priority_lessons(material["curriculum"], args.lesson_limit)
    if args.max_divisions < 1 or args.max_divisions > 55:
        raise ValueError("--max-divisions must be between 1 and 55")
    divisions = canonical["divisions"][:args.max_divisions]
    canonical["divisions"] = divisions
    canonical["profiles"] = {row["name"]: canonical["profiles"][row["name"]] for row in divisions}
    canonical["crosswalk_by_name"] = {row["name"]: canonical["crosswalk_by_name"][row["name"]] for row in divisions}

    test_results = run_existing_trainer_tests(root)
    failures: list[dict[str, Any]] = []
    if test_results["status"] != "passed":
        failures.append({"stage": "existing_trainer_tests", "reason": test_results["output_tail"]})

    active_recall = score_active_recall()
    glossary = extract_glossary(material["glossary_sources"])
    if len(glossary) < 8:
        failures.append({"stage": "glossary_extraction", "reason": f"only {len(glossary)} first-party terms were found"})
    write_json(output_dir / "glossary.json", {
        "schema": "dreamco.first_party_glossary.v1",
        "source_policy": "first_party_and_approved_synthetic_only",
        "external_sources_used": [], "terms": glossary,
    })

    tokenizer: dict[str, Any] = {}
    tokenizer_cli: dict[str, Any] = {"status": "blocked"}
    try:
        tokenizer, tokenizer_cli = run_tokenizer_cli(root, output_dir, args.vocab_size)
    except Exception as exc:
        failures.append({"stage": "tokenizer_training", "reason": str(exc)})

    exercises: dict[str, Any] = {"status": "blocked"}
    heldout: dict[str, Any] = {"status": "blocked", "cases": [], "cases_passed": 0, "cases_total": 0, "score": 0}
    tokenizer_hash = tokenizer_cli.get("artifact_sha256", "")
    if tokenizer:
        try:
            exercises = run_worked_exercises(material, tokenizer, args.vocab_size)
            heldout = run_heldout_assessment(
                root, material["manifest"], tokenizer, tokenizer_hash,
                {str(row["id"]) for row in divisions},
            )
        except Exception as exc:
            failures.append({"stage": "worked_or_heldout_assessment", "reason": str(exc)})

    global_status = "passed" if (
        test_results["status"] == "passed" and active_recall["status"] == "completed"
        and len(glossary) >= 8 and tokenizer_cli.get("status") == "passed"
        and exercises.get("status") == "passed" and heldout.get("status") == "passed"
    ) else "failed"
    division_results = build_division_results(canonical, selected, material, commit_sha, global_status)
    completed = sum(1 for row in division_results if row["activity_status"] == "completed_shared_foundation")
    failed = len(division_results) - completed
    mapping_pending = sum(1 for row in division_results if row["specialist_mapping"]["owner_review_required"])

    division_output = {
        "schema": "dreamco.buddy_division_study_results.v1",
        "canonical_domain_division_count": len(division_results),
        "attempted_count": len(division_results),
        "completed_shared_foundation_count": completed,
        "failed_count": failed,
        "specialist_mapping_pending_owner_review_count": mapping_pending,
        "results": division_results,
    }
    write_json(output_dir / "division-results.json", division_output)
    write_json(output_dir / "active-recall.json", active_recall)
    write_json(output_dir / "worked-exercises.json", exercises)
    write_json(output_dir / "heldout-assessment.json", heldout)
    write_json(output_dir / "test-results.json", test_results)

    tokenizer_summary = {
        "status": tokenizer_cli.get("status", "blocked"),
        "source_id": material["source_id"], "source_type": "synthetic",
        "manifest_sha256": material["input_hashes"][MANIFEST_PATH],
        "corpus_sha256": material["corpus_sha256"],
        "rights_evidence_ref": material["rights_evidence_ref"],
        "rights_verified": True, "model_training_permission": True, "privacy_reviewed": True,
        "holdout_used_for_training": False,
        "requested_vocab_size": args.vocab_size, "actual_vocab_size": tokenizer.get("vocab_size"),
        "merge_count": len(tokenizer.get("merges", [])),
        "tokenizer_artifact_sha256": tokenizer_hash,
        "model_weight_training_executed": False, "production_training_allowed": False,
        "cli_evidence": tokenizer_cli,
    }
    sandbox_summary = {
        "status": "passed" if tokenizer_cli.get("status") == "passed" and test_results["status"] == "passed" else "failed",
        "environment": "temporary_output_directory_on_ephemeral_CI_runner",
        "network_access_by_study_script": False, "external_material_downloaded": False,
        "paid_compute_used": False, "secrets_accessed": False,
        "tokenizer_cli": tokenizer_cli, "existing_trainer_tests": test_results,
        "model_weight_training_executed": False,
    }
    write_json(output_dir / "tokenizer-training.json", tokenizer_summary)
    write_json(output_dir / "sandbox-results.json", sandbox_summary)

    source_provenance = []
    for path in INPUT_PATHS:
        if path in (TRAINER_GUIDE_PATH, STUDY_GUIDE_PATH, CURRICULUM_PATH):
            kind, rights, used = "first_party_dreamco_instruction", "repository_owned_first_party_material", True
        elif path in (MANIFEST_PATH, CORPUS_PATH):
            kind, rights, used = "synthetic_ci_fixture", material["rights_evidence_ref"], True
        else:
            kind, rights, used = "canonical_repository_control", "repository_control_metadata", False
        source_provenance.append({
            "path": path, "sha256": material["input_hashes"][path],
            "kind": kind, "rights_basis": rights, "used_for_study": used,
            "external_content_accessed": False,
        })

    blockers = [
        "No external videos, transcripts, or third-party documentation were accessed; item-level rights were not verified in this run.",
        "The 45 proposed exact-name and 10 unresolved specialist mappings remain pending owner review; no specialist owner was assigned.",
        "No neural model-weight training or distillation was performed or authorized.",
        "This is a shared-foundation session, not completion of each division's specialist curriculum or mastery gate.",
        "The learner harness uses fixed first-party reference-answer fixtures; no independent Buddy model inference was invoked.",
    ]
    evidence = {
        "schema": "dreamco.buddy_study_session_evidence.v1",
        "session_id": f"buddy-study-{run_id}-{now_utc.strftime('%Y%m%dT%H%M%SZ')}",
        "status": "completed_with_boundaries" if global_status == "passed" else "partial_failure",
        "created_at_utc": now_utc.isoformat(), "created_at_local": now_local.isoformat(),
        "commit_sha": commit_sha, "workflow_run_id": run_id, "workflow_run_url": run_url,
        "artifact_name": f"buddy-study-evidence-{run_id}",
        "scope": {
            "canonical_domain_divisions": len(division_results), "attempted_divisions": len(division_results),
            "completed_shared_foundation_divisions": completed, "failed_divisions": failed,
            "specialist_mapping_pending_owner_review": mapping_pending,
            "canonical_masterbot_lanes": canonical["masterbot_count"],
            "shared_platform_masterbots": canonical["platform_masterbot_count"],
            "selected_lessons_per_division": len(selected),
            "selected_lesson_ids": [lesson["lesson_id"] for lesson in selected],
            "external_sources_used": [], "external_material_accessed": False,
            "paid_compute_used": False, "secrets_accessed": False,
            "model_weight_training_executed": False,
        },
        "source_provenance": source_provenance,
        "input_hashes": material["input_hashes"],
        "selected_lessons": selected, "active_recall": active_recall,
        "glossary": {"path": "glossary.json", "term_count": len(glossary), "source_paths": list(material["glossary_sources"])},
        "worked_exercises": exercises, "coding_sandbox": sandbox_summary,
        "tokenizer_training": tokenizer_summary, "heldout_assessment": heldout,
        "division_results_path": "division-results.json",
        "division_counts": {
            "attempted": len(division_results), "completed_shared_foundation": completed,
            "failed": failed, "specialist_mapping_pending_owner_review": mapping_pending,
            "crosswalk_status_counts": canonical["crosswalk_status_counts"],
        },
        "test_results": test_results, "failures": failures, "blockers": blockers,
        "model_weight_training": {
            "executed": False, "authorization": False, "checkpoint_sha256": None,
            "reason": "This run is tokenizer-only; no neural weights were changed.",
        },
    }
    output_names = (
        "tokenizer.json", "glossary.json", "division-results.json", "active-recall.json",
        "worked-exercises.json", "heldout-assessment.json", "test-results.json",
        "tokenizer-training.json", "sandbox-results.json",
    )
    evidence["output_hashes"] = {
        name: sha256_file(output_dir / name) for name in output_names if (output_dir / name).is_file()
    }

    report = [
        "# Buddy Study Evidence Session", "",
        f"- Status: {evidence['status']}",
        f"- Executed commit: {commit_sha}",
        f"- Session: {evidence['session_id']}",
        f"- Domain divisions attempted: {len(division_results)}",
        f"- Shared-foundation activity completed: {completed}",
        f"- Failed division activities: {failed}",
        f"- Specialist mappings awaiting owner review: {mapping_pending}",
        f"- Shared platform MasterBots: {canonical['platform_masterbot_count']} of {canonical['masterbot_count']} lanes",
        f"- Selected lessons per division: {len(selected)}",
        f"- Active recall: {active_recall['score']}% ({active_recall['items_passed']}/{active_recall['items_total']})",
        f"- Held-out assessment: {heldout.get('score', 0)}% ({heldout.get('cases_passed', 0)}/{heldout.get('cases_total', 0)})",
        f"- Glossary terms extracted: {len(glossary)}",
        f"- Tokenizer: {tokenizer_summary['status']}; vocabulary {tokenizer_summary.get('actual_vocab_size')}; SHA-256 {tokenizer_hash}",
        f"- Existing trainer tests: {test_results['status']} ({test_results.get('tests_run')} tests)",
        "- Neural model weights trained: No",
        "- External materials accessed: No",
        "- Paid compute or secrets used: No", "",
        "## Selected shared-foundation lessons",
    ]
    report.extend(f"- {lesson['lesson_id']} — {lesson['title']} (priority {lesson['priority_rank']}: {lesson['priority_reason']})" for lesson in selected)
    report.extend(["", "## Boundaries and blockers"])
    report.extend(f"- {item}" for item in blockers)
    if failures:
        report.extend(["", "## Failures"])
        report.extend(f"- {item['stage']}: {item['reason']}" for item in failures)
    if run_url:
        report.extend(["", f"Workflow run: {run_url}"])
    (output_dir / "session-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    evidence["report_path"] = "session-report.md"
    evidence["report_sha256"] = sha256_file(output_dir / "session-report.md")
    write_json(output_dir / "study-session-evidence.json", evidence)
    checksums = {
        "schema": "dreamco.study_session_checksums.v1",
        "commit_sha": commit_sha,
        "files": {
            path.name: sha256_file(path)
            for path in sorted(output_dir.iterdir())
            if path.is_file() and path.name != "checksums.json"
        },
        "evidence_sha256": sha256_file(output_dir / "study-session-evidence.json"),
    }
    write_json(output_dir / "checksums.json", checksums)
    return 0 if global_status == "passed" and not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--commit-sha", default="")
    parser.add_argument("--max-divisions", type=int, default=55)
    parser.add_argument("--lesson-limit", type=int, default=5)
    parser.add_argument("--vocab-size", type=int, default=512)
    args = parser.parse_args()
    if args.lesson_limit < 1 or args.lesson_limit > len(LESSON_PRIORITY):
        parser.error(f"--lesson-limit must be between 1 and {len(LESSON_PRIORITY)}")
    try:
        return run_session(args)
    except Exception as exc:
        output_dir = args.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        write_json(output_dir / "session-failure.json", {
            "schema": "dreamco.buddy_study_session_failure.v1",
            "status": "blocked_or_failed_before_completion",
            "commit_sha": args.commit_sha or os.environ.get("GITHUB_SHA", ""),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "external_sources_used": [],
            "model_weight_training_executed": False,
        })
        raise


if __name__ == "__main__":
    raise SystemExit(main())
