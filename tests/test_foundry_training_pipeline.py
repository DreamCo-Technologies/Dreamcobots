"""Offline tests for signed-data guardrails and train/validation/holdout isolation."""
import importlib.util
import importlib
import hashlib
import json
import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "stages" / "05_model_foundry" / "guardrails.py"
SPEC = importlib.util.spec_from_file_location("dreamco_foundry_guardrails", MODULE_PATH)
GUARDRAILS = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(GUARDRAILS)
sys.path.insert(0, str(MODULE_PATH.parent))
TRAIN_WEIGHTS_SPEC = importlib.util.spec_from_file_location(
    "dreamco_foundry_train_weights", MODULE_PATH.parent / "train_weights.py"
)
TRAIN_WEIGHTS = importlib.util.module_from_spec(TRAIN_WEIGHTS_SPEC)
assert TRAIN_WEIGHTS_SPEC and TRAIN_WEIGHTS_SPEC.loader
TRAIN_WEIGHTS_SPEC.loader.exec_module(TRAIN_WEIGHTS)
HOLDOUT_HELPERS = importlib.import_module("stages.05_model_foundry.holdout")
HOLDOUT_RUNNER = importlib.import_module("stages.05_model_foundry.run_holdout_eval")
HOLDOUT_GATE = importlib.import_module("stages.05_model_foundry.eval_holdout")
TOKENIZER_MODULE = importlib.import_module("stages.05_model_foundry.train_tokenizer")
PACKER_MODULE = importlib.import_module("stages.05_model_foundry.pack_tokens")
MERGE_MODULE = importlib.import_module("stages.05_model_foundry.merge_adapter")
SIGN_MANIFEST = importlib.import_module("stages.01_policy_gate.sign_training_manifest")
SIGN_SHARDS = importlib.import_module("stages.01_policy_gate.sign_token_shards")


class FoundryGuardrailTests(unittest.TestCase):
    def test_split_is_deterministic_and_disjoint(self):
        ids = [f"task-{i}" for i in range(10000)]
        buckets = [GUARDRAILS.split_bucket(value) for value in ids]
        self.assertEqual(buckets, [GUARDRAILS.split_bucket(value) for value in ids])
        self.assertTrue(all(GUARDRAILS.split_name(value) == "train" for value in ids if GUARDRAILS.split_bucket(value) < 90))
        self.assertTrue(all(GUARDRAILS.split_name(value) == "validation" for value in ids if 90 <= GUARDRAILS.split_bucket(value) < 95))
        self.assertTrue(all(GUARDRAILS.split_name(value) == "holdout" for value in ids if GUARDRAILS.split_bucket(value) >= 95))

    def test_unsigned_or_tampered_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = root / "records.jsonl"
            data.write_text('{"task_id":"t1","content":"safe"}\n', encoding="utf-8")
            manifest = {
                "schema": "dreamco.foundry.authorization.v1",
                "datasets": [{
                    "dataset_id": "d1",
                    "path": "records.jsonl",
                    "sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
                    "license_tier": "DREAMCO_ORIGINAL",
                    "commercial_use": True,
                    "policy_decision_id": "PD-1",
                    "category": "study_guides",
                }],
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            signature_path = root / "manifest.sig"
            signature_path.write_text("", encoding="ascii")
            public_key_path = root / "pub.pem"
            public_key_path.write_text("not-a-key", encoding="ascii")
            with self.assertRaises(Exception):
                GUARDRAILS.verify_signed_manifest(manifest_path, signature_path, public_key_path)

    def test_holdout_cannot_be_requested_with_training_splits(self):
        with self.assertRaises(PermissionError):
            list(GUARDRAILS.iter_authorized_records(
                {"datasets": []}, splits={"train", "holdout"}
            ))

    def test_dpo_accepts_only_lab_pass_teachback_against_lab_failure(self):
        evidence = {
            "sandbox_run_id": "run-good", "rejected_sandbox_run_id": "run-bad",
            "grader_version": "grader-v1", "test_suite_sha256": "a" * 64,
            "rubric_sha256": "b" * 64, "grader_attestation_sha256": "c" * 64,
            "rejected_grader_attestation_sha256": "d" * 64,
        }
        rows = [
            {"prompt": "p", "chosen": "good", "rejected": "bad",
             "chosen_status": "LAB_PASSED", "teach_back_verified": True,
             "rejected_status": "LAB_FAILED", **evidence},
            {"prompt": "p", "chosen": "unverified", "rejected": "bad",
             "chosen_status": "LAB_PASSED", "teach_back_verified": False,
             "rejected_status": "LAB_FAILED", **evidence},
            {"prompt": "p", "chosen": "no-attestation", "rejected": "bad",
             "chosen_status": "LAB_PASSED", "teach_back_verified": True,
             "rejected_status": "LAB_FAILED"},
        ]
        pairs = TRAIN_WEIGHTS.validated_preferences(rows)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["chosen"], "good")

    def test_open_weight_requires_exact_signed_license_evidence(self):
        approved = {
            "models": [{
                "model_id": "example/model",
                "revision": "a" * 40,
                "license_tier": "PERMISSIVE_COMMERCIAL",
                "commercial_use": True,
                "policy_decision_id": "POLICY-1",
                "license_evidence_id": "LICENSE-1",
                "approved_by": "Policy Owner",
            }]
        }
        result = GUARDRAILS.require_model_authorization(approved, "example/model", "a" * 40)
        self.assertEqual(result["license_evidence_id"], "LICENSE-1")
        with self.assertRaises(PermissionError):
            GUARDRAILS.require_model_authorization(approved, "example/model", "b" * 40)

    def test_holdout_helpers_use_same_fixed_split_as_guardrails(self):
        ids = [f"task-{i}" for i in range(1000)]
        self.assertEqual(
            [HOLDOUT_HELPERS.bucket(value) for value in ids],
            [GUARDRAILS.split_bucket(value) for value in ids],
        )
        with self.assertRaises(ValueError):
            HOLDOUT_HELPERS.split_tasks([{"task_id": "x"}], holdout_percent=20)

    def test_holdout_runner_uses_deterministic_text_normalization(self):
        self.assertEqual(HOLDOUT_RUNNER.normalized("Hello, WORLD!"), "hello world")
        self.assertEqual(HOLDOUT_RUNNER.normalized("  A   B  "), "a b")
        self.assertTrue(HOLDOUT_RUNNER.thresholds_pass(0.96, 1.0, 0.95, 1.0))
        self.assertFalse(HOLDOUT_RUNNER.thresholds_pass(0.94, 1.0, 0.95, 1.0))

    def test_holdout_gate_requires_exact_suite_and_config_evidence(self):
        report = {
            "schema": "dreamco.foundry.model_holdout_report.v1",
            "evaluation_split": "holdout",
            "holdout_access": "evaluation_only",
            "training_access": False,
            "source_manifest_sha256": "a" * 64,
            "benchmark_suite_sha256": "b" * 64,
            "evaluation_config_sha256": "c" * 64,
            "tokenizer_sha256": "e" * 64,
            "checkpoint_sha256": "d" * 64,
            "evaluated_task_ids": ["task-1"],
            "evaluated_count": 1,
            "pass_rate": 0.95,
            "safety_gate_pass_rate": 1.0,
        }
        HOLDOUT_GATE.validate_report(report, ["task-1"], "a" * 64, "b" * 64, "candidate")
        with self.assertRaises(ValueError):
            HOLDOUT_GATE.validate_report(report, ["task-2"], "a" * 64, "b" * 64, "candidate")

    def test_lora_holdout_report_binds_adapter_configuration(self):
        report = {
            "schema": "dreamco.foundry.model_holdout_report.v1",
            "evaluation_split": "holdout",
            "holdout_access": "evaluation_only",
            "training_access": False,
            "source_manifest_sha256": "a" * 64,
            "benchmark_suite_sha256": "b" * 64,
            "evaluation_config_sha256": "c" * 64,
            "tokenizer_sha256": "e" * 64,
            "checkpoint_sha256": "d" * 64,
            "base_model_id": "Qwen/Qwen2.5-Coder-1.5B",
            "base_model_revision": "a" * 40,
            "base_model_license_evidence_id": "QWEN-APACHE-2.0-REVISION",
            "evaluated_task_ids": ["task-1"],
            "evaluated_count": 1,
            "pass_rate": 0.95,
            "safety_gate_pass_rate": 1.0,
        }
        with self.assertRaises(ValueError):
            HOLDOUT_GATE.validate_report(report, ["task-1"], "a" * 64, "b" * 64, "candidate")
        report["adapter_config_sha256"] = "f" * 64
        HOLDOUT_GATE.validate_report(report, ["task-1"], "a" * 64, "b" * 64, "candidate")

    def test_tokenizer_corpus_excludes_holdout_benchmark_category(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            train_id = next(f"train-{i}" for i in range(10000) if GUARDRAILS.split_bucket(f"train-{i}") < 90)
            guide = root / "guide.jsonl"
            benchmark = root / "benchmark.jsonl"
            guide.write_text(json.dumps({"task_id": train_id, "title": "allowed guide"}) + "\\n", encoding="utf-8")
            benchmark.write_text(json.dumps({"task_id": train_id, "title": "holdout benchmark"}) + "\\n", encoding="utf-8")
            manifest = {"datasets": [
                {"_resolved_path": str(guide), "dataset_id": "g", "category": "study_guides",
                 "license_tier": "DREAMCO_ORIGINAL", "policy_decision_id": "P1"},
                {"_resolved_path": str(benchmark), "dataset_id": "h", "category": "holdout_benchmarks",
                 "license_tier": "DREAMCO_ORIGINAL", "policy_decision_id": "P1"},
            ]}
            corpus = list(TOKENIZER_MODULE.corpus(manifest))
            self.assertTrue(any("allowed guide" in item for item in corpus))
            self.assertFalse(any("holdout benchmark" in item for item in corpus))

    def test_packer_emits_signed_bin_and_index_metadata(self):
        try:
            import numpy  # noqa: F401
        except ImportError:
            self.skipTest("NumPy is installed by the Foundry CPU preflight workflow")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            entry = PACKER_MODULE._write_shard(list(range(16)), root, "train", 8)
            self.assertEqual(entry["tokens"], 16)
            self.assertEqual(entry["sequences"], 2)
            self.assertTrue((root / entry["file"]).is_file())
            self.assertTrue((root / entry["index_file"]).is_file())
            index = json.loads((root / entry["index_file"]).read_text(encoding="utf-8"))
            self.assertEqual(index["sequence_stride_tokens"], 8)
            self.assertEqual(index["sequence_count"], 2)
            self.assertEqual(
                entry["index_sha256"],
                hashlib.sha256((root / entry["index_file"]).read_bytes()).hexdigest(),
            )

    def test_packer_uses_reserved_tool_call_token(self):
        class DummyTokenizer:
            eos_token_id = 2
            seen = ""
            def encode(self, value, add_special_tokens=False):
                self.seen = value
                return [1, 2]
        tokenizer = DummyTokenizer()
        PACKER_MODULE._token_pool(
            [{"messages": [{"role": "tool", "content": "tool result"}]}], tokenizer
        )
        self.assertIn("<|tool_call|>", tokenizer.seen)
        self.assertNotIn("<|tool|>", tokenizer.seen)

    def test_policy_signers_bind_dataset_and_shard_bytes(self):
        from unittest.mock import patch
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError:
            self.skipTest("cryptography is installed by the foundry preflight workflow")
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PrivateFormat, NoEncryption, PublicFormat,
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            private = Ed25519PrivateKey.generate()
            private_path, public_path = root / "private.pem", root / "public.pem"
            private_path.write_bytes(private.private_bytes(
                Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
            ))
            public_path.write_bytes(private.public_key().public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
            ))
            task_id = next(f"signer-{i}" for i in range(10000)
                           if GUARDRAILS.split_bucket(f"signer-{i}") < 90)
            holdout_id = next(f"holdout-{i}" for i in range(10000)
                              if GUARDRAILS.split_bucket(f"holdout-{i}") >= 95)
            dataset = root / "study_guides.jsonl"
            holdout_dataset = root / "holdout.jsonl"
            dataset.write_text(json.dumps({"task_id": task_id, "title": "Guide"}) + "\\n", encoding="utf-8")
            holdout_dataset.write_text(json.dumps({
                "task_id": holdout_id, "prompt": "holdout prompt",
                "expected_answer": "holdout answer", "expected_safety": "ALLOW"
            }) + "\\n", encoding="utf-8")
            attestation = root / "owner-attestation.txt"
            attestation.write_text("DreamCo owns this original study guide.", encoding="utf-8")
            manifest = root / "manifest.json"
            signature = root / "manifest.sig"
            payload = {
                "schema": "dreamco.foundry.authorization.v1",
                "datasets": [{
                    "dataset_id": "guide-1", "path": dataset.name,
                    "sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
                    "license_tier": "DREAMCO_ORIGINAL", "commercial_use": True,
                    "category": "study_guides",
                    "owner_attestation_path": attestation.name,
                    "owner_attestation_sha256": hashlib.sha256(attestation.read_bytes()).hexdigest(),
                }, {
                    "dataset_id": "holdout-1", "path": holdout_dataset.name,
                    "sha256": hashlib.sha256(holdout_dataset.read_bytes()).hexdigest(),
                    "license_tier": "DREAMCO_ORIGINAL", "commercial_use": True,
                    "category": "holdout_benchmarks",
                    "owner_attestation_path": attestation.name,
                    "owner_attestation_sha256": hashlib.sha256(attestation.read_bytes()).hexdigest(),
                }],
                "models": [],
            }
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with patch("sys.argv", ["sign_training_manifest", "--manifest", str(manifest),
                    "--registry", str(ROOT / "contracts/license_policy.yaml"),
                    "--private-key", str(private_path), "--signature-output", str(signature),
                    "--approve-commercial-training", "--approved-by", "Unit Test Owner",
                    "--policy-decision-id", "TEST-POLICY-1"]):
                SIGN_MANIFEST.main()
            verified_all = GUARDRAILS.verify_signed_manifest(manifest, signature, public_path)
            self.assertEqual(verified_all["datasets"][0]["approved_by"], "Unit Test Owner")
            holdout_dataset.write_text(json.dumps({
                "task_id": holdout_id, "prompt": "tampered holdout",
                "expected_answer": "wrong", "expected_safety": "ALLOW"
            }) + "\\n", encoding="utf-8")
            verified = GUARDRAILS.verify_signed_manifest(
                manifest, signature, public_path, verify_dataset_hashes=False
            )
            train_rows = list(GUARDRAILS.iter_authorized_records(
                verified, categories={"study_guides"}, splits={"train"}
            ))
            self.assertEqual(len(train_rows), 1)
            with self.assertRaises(ValueError):
                list(GUARDRAILS.iter_authorized_records(
                    verified, categories={"holdout_benchmarks"}, splits={"holdout"}
                ))

            shard_dir = root / "shards"
            shard_dir.mkdir()
            shard = shard_dir / "train-00000.bin"
            shard.write_bytes(b"\\x00" * 32)
            shard_index = shard_dir / "train-00000.idx"
            index_payload = {
                "schema": "dreamco.foundry.token_shard_index.v1",
                "bin_file": shard.name, "dtype": "uint32",
                "sequence_length": 8, "sequence_count": 1, "token_count": 8,
                "offset_unit": "tokens", "first_token_offset": 0,
                "sequence_stride_tokens": 8,
            }
            shard_index.write_text(json.dumps(index_payload, sort_keys=True, separators=(",", ":")) + "\\n", encoding="utf-8")
            shard_manifest = shard_dir / "manifest.json"
            shard_signature = shard_dir / "manifest.sig"
            shard_payload = {
                "schema": "dreamco.foundry.token_shards.v1",
                "sequence_length": 8, "shard_size_tokens": 8, "dtype": "uint32",
                "source_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                "training_splits": ["train"], "validation_splits": [],
                "excluded_splits": ["holdout"],
                "mix_percent": {"study_guides": 60, "verified_trajectories": 25, "general_replay": 15},
                "train": {"file": shard.name, "tokens": 8, "sequences": 1,
                          "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
                          "index_file": shard_index.name,
                          "index_sha256": hashlib.sha256(shard_index.read_bytes()).hexdigest()},
                "validation": None,
            }
            shard_manifest.write_text(json.dumps(shard_payload), encoding="utf-8")
            with patch("sys.argv", ["sign_token_shards", "--shard-manifest", str(shard_manifest),
                    "--source-manifest", str(manifest), "--source-signature", str(signature),
                    "--public-key", str(public_path), "--private-key", str(private_path),
                    "--signature-output", str(shard_signature)]):
                SIGN_SHARDS.main()
            verified_shards = GUARDRAILS.verify_signed_shard_manifest(
                shard_manifest, shard_signature, manifest, signature, public_path
            )
            self.assertEqual(verified_shards["train"]["_resolved_path"], str(shard.resolve()))
            self.assertEqual(verified_shards["train"]["_resolved_index_path"], str(shard_index.resolve()))
            self.assertNotIn("_resolved_path", json.loads(shard_manifest.read_text())["train"])

    def test_signed_shard_payload_checks_sequence_geometry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shard = root / "train-00000.bin"
            shard.write_bytes(b"\\x00" * (8 * 4))
            shard_index = root / "train-00000.idx"
            index_payload = {
                "schema": "dreamco.foundry.token_shard_index.v1",
                "bin_file": shard.name, "dtype": "uint32",
                "sequence_length": 8, "sequence_count": 1, "token_count": 8,
                "offset_unit": "tokens", "first_token_offset": 0,
                "sequence_stride_tokens": 8,
            }
            shard_index.write_text(json.dumps(index_payload, sort_keys=True, separators=(",", ":")) + "\\n", encoding="utf-8")
            source = root / "source.json"
            source.write_text("{}", encoding="utf-8")
            payload = {
                "schema": "dreamco.foundry.token_shards.v1",
                "sequence_length": 8, "shard_size_tokens": 8, "dtype": "uint32",
                "training_splits": ["train"], "validation_splits": [],
                "excluded_splits": ["holdout"],
                "mix_percent": {"study_guides": 60, "verified_trajectories": 25, "general_replay": 15},
                "source_manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "train": {"file": shard.name, "tokens": 8, "sequences": 1,
                          "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
                          "index_file": shard_index.name,
                          "index_sha256": hashlib.sha256(shard_index.read_bytes()).hexdigest()},
                "validation": None,
            }
            validated = GUARDRAILS.validate_shard_payload(payload, root, source)
            self.assertEqual(validated["train"]["_resolved_path"], str(shard.resolve()))
            payload["train"]["tokens"] = 7
            with self.assertRaises(ValueError):
                GUARDRAILS.validate_shard_payload(payload, root, source)

    def test_signed_shard_manifest_validates_multiple_bin_idx_pairs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.json"
            source.write_text("{}", encoding="utf-8")
            entries = []
            for index_number in range(2):
                shard = root / f"train-{index_number:05d}.bin"
                shard.write_bytes(b"\\x00" * 32)
                index_path = root / f"train-{index_number:05d}.idx"
                index_payload = {
                    "schema": "dreamco.foundry.token_shard_index.v1",
                    "bin_file": shard.name, "dtype": "uint32",
                    "sequence_length": 8, "sequence_count": 1, "token_count": 8,
                    "offset_unit": "tokens", "first_token_offset": 0,
                    "sequence_stride_tokens": 8,
                }
                index_path.write_text(
                    json.dumps(index_payload, sort_keys=True, separators=(",", ":")) + "\\n",
                    encoding="utf-8",
                )
                entries.append({
                    "file": shard.name, "sha256": hashlib.sha256(shard.read_bytes()).hexdigest(),
                    "index_file": index_path.name,
                    "index_sha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
                    "tokens": 8, "sequences": 1,
                })
            payload = {
                "schema": "dreamco.foundry.token_shards.v1",
                "sequence_length": 8, "shard_size_tokens": 8, "dtype": "uint32",
                "training_splits": ["train"], "validation_splits": [],
                "excluded_splits": ["holdout"],
                "mix_percent": {"study_guides": 60, "verified_trajectories": 25, "general_replay": 15},
                "source_manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "train": entries, "validation": [],
            }
            validated = GUARDRAILS.validate_shard_payload(payload, root, source)
            self.assertEqual(len(validated["train"]), 2)
            self.assertTrue(all(item["_resolved_path"] for item in validated["train"]))
            self.assertTrue(all(item["_resolved_index_path"] for item in validated["train"]))

    def test_merge_adapter_digest_requires_safetensors(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            (folder / "adapter_model.safetensors").write_bytes(b"weights")
            self.assertEqual(
                MERGE_MODULE.safetensors_digest(folder),
                hashlib.sha256(b"weights").hexdigest(),
            )

    def test_scratch_model_parameter_target_is_enforced(self):
        TRAIN_WEIGHTS.validate_parameter_count(45_148_256, 45_148_864, tolerance=0.01)
        with self.assertRaises(ValueError):
            TRAIN_WEIGHTS.validate_parameter_count(40_000_000, 45_148_864, tolerance=0.01)

    def test_sft_rows_require_assistant_or_tool_targets(self):
        rows = [
            {"messages": [{"role": "user", "content": "question"}]},
            {"messages": [{"role": "assistant", "content": "verified answer"}]},
            {"messages": [{"role": "tool", "content": "tool result"}]},
        ]
        selected = TRAIN_WEIGHTS.sft_rows(rows)
        self.assertEqual(len(selected), 2)

    def test_self_play_pairs_only_use_verified_lab_and_teachback_preferences(self):
        path = ROOT / "stages" / "05_model_foundry" / "generate_self_play_pairs.py"
        spec = importlib.util.spec_from_file_location("dreamco_self_play_pairs", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {
            "task_id": "task-1", "prompt": "Solve this",
            "test_suite_sha256": "a" * 64, "rubric_sha256": "b" * 64,
            "grader_attestation_sha256": "c" * 64, "grader_version": "grader-v1",
        }
        rows = [
            {**common, "candidate_id": "good", "response": "correct",
             "sandbox_status": "LAB_PASSED", "teach_back_status": "TEACH_BACK_VERIFIED",
             "sandbox_run_id": "run-good"},
            {**common, "candidate_id": "bad", "response": "incorrect",
             "sandbox_status": "LAB_FAILED", "teach_back_status": "NOT_VERIFIED",
             "sandbox_run_id": "run-bad"},
            {**common, "candidate_id": "weak", "response": "unverified",
             "sandbox_status": "LAB_PASSED", "teach_back_status": "NOT_VERIFIED",
             "sandbox_run_id": "run-weak"},
        ]
        pairs, report = module.build_pairs(rows)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["chosen"], "correct")
        self.assertEqual(pairs[0]["rejected"], "incorrect")
        self.assertFalse(report["training_started"])

    def test_self_play_pairs_reject_mismatched_test_suite_revisions(self):
        path = ROOT / "stages" / "05_model_foundry" / "generate_self_play_pairs.py"
        spec = importlib.util.spec_from_file_location("dreamco_self_play_pairs_mismatch", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {"task_id":"task-1","grader_version":"v1","rubric_sha256":"b"*64,
                  "grader_attestation_sha256":"c"*64}
        rows = [
            {**common,"candidate_id":"a","response":"good","sandbox_status":"LAB_PASSED",
             "teach_back_status":"TEACH_BACK_VERIFIED","sandbox_run_id":"1","test_suite_sha256":"a"*64},
            {**common,"candidate_id":"b","response":"bad","sandbox_status":"LAB_FAILED",
             "teach_back_status":"NOT_VERIFIED","sandbox_run_id":"2","test_suite_sha256":"d"*64},
        ]
        pairs, _ = module.build_pairs(rows)
        self.assertEqual(pairs, [])

    def test_self_play_pairs_exclude_holdout_tasks(self):
        path = ROOT / "stages" / "05_model_foundry" / "generate_self_play_pairs.py"
        spec = importlib.util.spec_from_file_location("dreamco_self_play_holdout", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {"task_id":"t","grader_version":"v1","test_suite_sha256":"a"*64,
                  "rubric_sha256":"b"*64,"grader_attestation_sha256":"c"*64,"prompt":"p"}
        rows = [
            {**common,"candidate_id":"a","response":"good","sandbox_status":"LAB_PASSED",
             "teach_back_status":"TEACH_BACK_VERIFIED","sandbox_run_id":"1"},
            {**common,"candidate_id":"b","response":"bad","sandbox_status":"LAB_FAILED",
             "teach_back_status":"NOT_VERIFIED","sandbox_run_id":"2"},
        ]
        pairs, report = module.build_pairs(rows)
        self.assertEqual(pairs, [])
        self.assertEqual(report["excluded_non_train_records"], 2)

    def test_shared_cache_requires_explicit_public_redistribution(self):
        path = ROOT / "stages" / "05_model_foundry" / "cache_policy.py"
        module = importlib.import_module("stages.05_model_foundry.cache_policy")
        self.assertTrue(module.public_cache_allowed({"datasets":[
            {"cache_visibility":"public","redistribution_allowed":True}
        ]}))
        self.assertFalse(module.public_cache_allowed({"datasets":[
            {"cache_visibility":"private","redistribution_allowed":False}
        ]}))
        self.assertFalse(module.public_cache_allowed({"datasets":[]} ))
        self.assertFalse(module.public_cache_allowed({
            "datasets":[{"cache_visibility":"public","redistribution_allowed":True}],
            "models":[{"cache_visibility":"private","redistribution_allowed":False}],
        }))

    def test_self_play_pairs_require_same_prompt_for_all_candidates(self):
        path = ROOT / "stages" / "05_model_foundry" / "generate_self_play_pairs.py"
        spec = importlib.util.spec_from_file_location("dreamco_self_play_prompt_check", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {"task_id":"task-1","grader_version":"v1","test_suite_sha256":"a"*64,
                  "rubric_sha256":"b"*64,"grader_attestation_sha256":"c"*64}
        rows = [
            {**common,"candidate_id":"a","prompt":"prompt one","response":"good",
             "sandbox_status":"LAB_PASSED","teach_back_status":"TEACH_BACK_VERIFIED","sandbox_run_id":"1"},
            {**common,"candidate_id":"b","prompt":"prompt two","response":"bad",
             "sandbox_status":"LAB_FAILED","teach_back_status":"NOT_VERIFIED","sandbox_run_id":"2"},
        ]
        pairs, _ = module.build_pairs(rows)
        self.assertEqual(pairs, [])

    def test_holdout_promotion_validator_requires_exact_signed_task_coverage(self):
        evaluator = importlib.import_module("stages.05_model_foundry.eval_holdout")
        report = {
            "schema": "dreamco.foundry.model_holdout_report.v1",
            "holdout_access": "evaluation_only",
            "training_access": False,
            "evaluation_split": "holdout",
            "source_manifest_sha256": "a" * 64,
            "benchmark_suite_sha256": "b" * 64,
            "evaluation_config_sha256": "c" * 64,
            "checkpoint_sha256": "d" * 64,
            "evaluated_task_ids": ["task-a", "task-b"],
            "pass_rate": 0.95,
            "safety_gate_pass_rate": 1.0,
        }
        evaluator.validate_report(report, ["task-a", "task-b"], "a" * 64, "b" * 64, "candidate")
        with self.assertRaises(ValueError):
            evaluator.validate_report(report, ["task-a", "task-b", "task-c"], "a" * 64, "b" * 64, "candidate")

    def test_distilled_trace_cache_is_verified_deduplicated_and_cot_free(self):
        path = ROOT / "stages" / "05_model_foundry" / "cache_distilled_traces.py"
        spec = importlib.util.spec_from_file_location("dreamco_distilled_trace_cache", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        common = {
            "task_id":"task-1","division_id":"DIV-01","prompt":"Write a function",
            "final_response":"def answer(): return 42","tool_calls":[{"name":"python","arguments":{"code":"print(42)","api_key":"sk-12345678901234567890"}}],
            "explanation_summary":"The function returns the requested constant.",
            "sandbox_run_id":"run-1","sandbox_status":"LAB_PASSED",
            "teach_back_status":"TEACH_BACK_VERIFIED","grader_attestation_sha256":"a"*64,
            "rubric_sha256":"b"*64,"test_suite_sha256":"c"*64,
        }
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "distilled_traces.jsonl"
            first = module.append_verified_traces([common], output)
            second = module.append_verified_traces([common], output)
            rejected = module.append_verified_traces([{**common,"chain_of_thought":"private reasoning"}], output)
            self.assertEqual(first["appended"], 1)
            self.assertEqual(second["duplicates"], 1)
            self.assertEqual(rejected["rejected"], 1)
            stored = json.loads(output.read_text().strip())
            self.assertNotIn("chain_of_thought", stored)
            self.assertFalse(stored["training_authorized"])
            self.assertEqual(stored["tool_calls"][0]["arguments"]["api_key"], "[REDACTED_SECRET]")

    def test_token_packing_deduplicates_normalized_examples(self):
        class FakeTokenizer:
            eos_token_id = 99
            def encode(self, value, add_special_tokens=False):
                return [ord(char) for char in value]

        rows = [
            {"task_id": "a", "content": "  UNIQUE   lesson "},
            {"task_id": "b", "content": "unique lesson"},
            {"task_id": "c", "content": "A different lesson"},
        ]
        tokens = PACKER_MODULE._token_pool(rows, FakeTokenizer())
        expected = [ord(char) for char in "unique lesson"] + [99]
        expected += [ord(char) for char in "a different lesson"] + [99]
        self.assertEqual(tokens, expected)

    def test_token_packing_skips_empty_normalized_examples(self):
        class FakeTokenizer:
            eos_token_id = 99
            def encode(self, value, add_special_tokens=False):
                return [ord(char) for char in value]

        self.assertEqual(PACKER_MODULE._token_pool([{"content": "   "}], FakeTokenizer()), [])


    def test_reused_manifest_rechecks_dataset_hash_after_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            task_id = next(
                f"rehash-{i}" for i in range(10000)
                if GUARDRAILS.split_bucket(f"rehash-{i}") < 90
            )
            dataset = root / "records.jsonl"
            dataset.write_text(
                json.dumps({"task_id": task_id, "content": "original"}) + "\n",
                encoding="utf-8",
            )
            manifest = {
                "datasets": [{
                    "_resolved_path": str(dataset),
                    "dataset_id": "rehash-test",
                    "sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
                    "category": "study_guides",
                    "license_tier": "DREAMCO_ORIGINAL",
                    "policy_decision_id": "TEST-POLICY",
                }]
            }
            first = list(GUARDRAILS.iter_authorized_records(
                manifest, categories={"study_guides"}, splits={"train"}
            ))
            self.assertEqual(len(first), 1)
            dataset.write_text(
                json.dumps({"task_id": task_id, "content": "tampered"}) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "dataset SHA-256 mismatch"):
                list(GUARDRAILS.iter_authorized_records(
                    manifest, categories={"study_guides"}, splits={"train"}
                ))

if __name__ == "__main__":
    unittest.main()
