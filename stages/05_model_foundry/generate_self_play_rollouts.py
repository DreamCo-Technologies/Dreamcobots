"""Generate raw, quarantined self-play rollouts from signed TRAIN-only tasks.

No output is automatically certified for DPO/SFT/GRPO. Generated code is
executed only in a rootless, network-isolated Docker sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path


try:
    from .guardrails import iter_authorized_records, sha256_file, verify_signed_manifest
except ImportError:
    from guardrails import iter_authorized_records, sha256_file, verify_signed_manifest

GRADER_VERSION = "dreamco-rootless-pytest-v1"


def python_block(response: str) -> str:
    blocks = re.findall(r"```python\s*(.*?)```", response, flags=re.I | re.S)
    if len(blocks) != 1 or not blocks[0].strip():
        raise ValueError("response must contain exactly one non-empty fenced python block")
    code = blocks[0].strip() + "\n"
    if len(code.encode("utf-8")) > 128_000:
        raise ValueError("candidate code exceeds 128 KB")
    return code


def validate_tests(test_suite: str) -> None:
    if not isinstance(test_suite, str) or not test_suite.strip() or len(test_suite.encode("utf-8")) > 128_000:
        raise ValueError("an owner-authored test suite under 128 KB is required")
    if "placeholder" in test_suite.lower():
        raise ValueError("placeholder tests are prohibited")
    if not re.search(r"(^|\n)\s*(?:from\s+solution\s+import|import\s+solution)", test_suite):
        raise ValueError("tests must import the generated solution module")
    if not re.search(r"(^|\n)\s*def\s+test_", test_suite):
        raise ValueError("tests must define at least one pytest test")


def require_rootless_docker() -> None:
    if not shutil.which("docker"):
        raise RuntimeError("Docker unavailable; refusing unsafe host execution")
    info = subprocess.run(
        ["docker", "info", "--format", "{{json .SecurityOptions}}"],
        capture_output=True, text=True, timeout=8, check=False,
    )
    if info.returncode or "rootless" not in info.stdout.lower():
        raise PermissionError("a rootless Docker daemon is mandatory")


def grade(code: str, tests: str, image: str, timeout: int) -> tuple[str, str]:
    validate_tests(tests)
    require_rootless_docker()
    with tempfile.TemporaryDirectory(prefix="dreamco-rollout-") as tmp:
        root = Path(tmp).resolve()
        (root / "solution.py").write_text(code, encoding="utf-8")
        (root / "test_solution.py").write_text(tests, encoding="utf-8")
        root.chmod(0o755)
        (root / "solution.py").chmod(0o644)
        (root / "test_solution.py").chmod(0o644)
        container_name = "dreamco-rollout-" + uuid.uuid4().hex[:16]
        command = [
            "docker", "run", "--rm", "--name", container_name, "--network=none", "--read-only",
            "--cap-drop=ALL", "--security-opt=no-new-privileges",
            "--pids-limit=64", "--memory=256m", "--memory-swap=256m",
            "--cpus=0.5", "--user=65532:65532",
            "--tmpfs", "/tmp:rw,nosuid,nodev,size=32m",
            "-v", f"{root}:/work:ro", "-w", "/tmp", image,
            "sh", "-lc",
            "cp -R /work /tmp/work && cd /tmp/work && PYTHONDONTWRITEBYTECODE=1 pytest -q",
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", container_name], capture_output=True, text=True, timeout=5, check=False)
            subprocess.run(["docker", "rm", "-f", container_name], capture_output=True, text=True, timeout=5, check=False)
            return "LAB_FAILED", "SANDBOX_TIMEOUT"
        if result.returncode == 0:
            return "LAB_PASSED", "SANDBOX_PASS"
        detail = (result.stdout + "\n" + result.stderr)[-500:]
        return "LAB_FAILED", "SANDBOX_FAIL: " + detail


def main() -> None:
    p = argparse.ArgumentParser(description="Generate train-only DreamCo sandbox rollouts")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--signature", type=Path, required=True)
    p.add_argument("--public-key", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--tokenizer", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--image", default="dreamco-verifier:local")
    p.add_argument("--num-rollouts", type=int, default=4)
    p.add_argument("--max-tasks", type=int, default=25)
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("--timeout", type=int, default=10)
    a = p.parse_args()
    if not 2 <= a.num_rollouts <= 8 or not 1 <= a.max_tasks <= 100:
        raise ValueError("rollouts must be 2..8 and max-tasks 1..100")
    if not 1 <= a.max_new_tokens <= 1024 or not 1 <= a.timeout <= 10:
        raise ValueError("max-new-tokens must be 1..1024 and timeout 1..10")
    if not a.checkpoint.is_dir() or not a.tokenizer.is_dir():
        raise FileNotFoundError("local checkpoint and tokenizer directories are required")

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    manifest = verify_signed_manifest(a.manifest, a.signature, a.public_key)
    task_rows = iter_authorized_records(
        manifest, categories={"verified_trajectories"}, splits={"train"}
    )
    tokenizer = AutoTokenizer.from_pretrained(a.tokenizer, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        a.checkpoint, local_files_only=True, trust_remote_code=False, use_safetensors=True
    )
    if torch.cuda.is_available():
        model.to("cuda")
    model.eval()

    records = []
    grpo_groups, dpo_candidates, sft_candidates = [], [], []
    for task in task_rows:
        if len({row["task_id"] for row in records}) >= a.max_tasks:
            break
        task_id = str(task.get("task_id") or task.get("id") or "")
        prompt, tests = task.get("prompt"), task.get("test_suite")
        if not task_id or not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("each authorized task requires a stable ID and prompt")
        validate_tests(tests)
        formatted = f"<|user|>\n{prompt}<|eos|>\n<|assistant|>\n"
        inputs = tokenizer(formatted, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            generated = model.generate(
                **inputs, do_sample=True, temperature=0.8, top_p=0.95,
                num_return_sequences=a.num_rollouts, max_new_tokens=a.max_new_tokens,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        start = inputs["input_ids"].shape[1]
        task_rollouts = []
        for index, sequence in enumerate(generated):
            response = tokenizer.decode(sequence[start:], skip_special_tokens=True).strip()
            candidate_id = hashlib.sha256(
                f"{task_id}:{index}:{response}".encode("utf-8")
            ).hexdigest()[:24]
            try:
                code = python_block(response)
                status, log = grade(code, tests, a.image, a.timeout)
            except (ValueError, RuntimeError, PermissionError) as exc:
                status, log = "NOT_GRADED", f"{type(exc).__name__}: {exc}"
            test_sha = hashlib.sha256(tests.encode("utf-8")).hexdigest()
            rubric = json.dumps(task.get("rubric_keywords", []), sort_keys=True)
            rubric_sha = hashlib.sha256(rubric.encode("utf-8")).hexdigest()
            evidence = {
                "task_id": task_id, "candidate_id": candidate_id, "sandbox_status": status,
                "sandbox_log": log, "test_suite_sha256": test_sha, "rubric_sha256": rubric_sha,
                "grader_version": GRADER_VERSION,
            }
            evidence_sha = hashlib.sha256(
                json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            row = {
                **evidence, "prompt": prompt, "response": response,
                "sandbox_run_id": str(uuid.uuid4()),
                "grader_attestation_sha256": evidence_sha,
                "grader_attestation_type": "unsigned_local_evidence_fingerprint",
                "teach_back_status": "NOT_VERIFIED",
                "eligible_for_training": False,
                "source_dataset_id": task.get("_dataset_id"),
                "source_policy_decision_id": task.get("_policy_decision_id"),
                "source_license_tier": task.get("_license_tier"),
                "review_required": True,
            }
            records.append(row)
            task_rollouts.append(row)
        scored_rollouts = [row for row in task_rollouts if row["sandbox_status"] in {"LAB_PASSED", "LAB_FAILED"}]
        if len({row["sandbox_status"] for row in scored_rollouts}) > 1:
            grpo_groups.append({
                "task_id": task_id, "prompt": prompt,
                "rollouts": [{"candidate_id": row["candidate_id"],
                              "response": row["response"],
                              "reward": 1.0 if row["sandbox_status"] == "LAB_PASSED" else 0.0,
                              "sandbox_status": row["sandbox_status"]}
                             for row in scored_rollouts],
                "eligible_for_training": False, "review_required": True,
            })
        passed = [row for row in task_rollouts if row["sandbox_status"] == "LAB_PASSED"]
        failed = [row for row in task_rollouts if row["sandbox_status"] == "LAB_FAILED"]
        if passed and failed:
            dpo_candidates.append({
                "task_id": task_id, "prompt": prompt,
                "chosen": passed[0]["response"], "rejected": failed[0]["response"],
                "chosen_status": "LAB_PASSED", "teach_back_verified": False,
                "rejected_status": "LAB_FAILED", "eligible_for_training": False,
                "review_required": True,
            })
        for row in passed:
            sft_candidates.append({
                "task_id": task_id,
                "messages": [{"role": "user", "content": prompt},
                             {"role": "assistant", "content": row["response"]}],
                "lab_status": "LAB_PASSED", "teach_back_verified": False,
                "eligible_for_training": False, "review_required": True,
            })

    if not records:
        raise ValueError("no authorized train-split self-play tasks were found")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in records),
        encoding="utf-8",
    )
    sidecars = {
        "grpo_candidates.jsonl": grpo_groups,
        "dpo_candidates.jsonl": dpo_candidates,
        "sft_candidates.jsonl": sft_candidates,
    }
    for filename, rows in sidecars.items():
        (a.output.parent / filename).write_text(
            "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
    summary = {
        "schema": "dreamco.foundry.raw_self_play.v1",
        "source_manifest_sha256": sha256_file(a.manifest),
        "checkpoint_sha256": hashlib.sha256(
            b"".join(sorted(path.read_bytes() for path in a.checkpoint.glob("*.safetensors")))
        ).hexdigest(),
        "records": len(records),
        "grpo_candidate_groups": len(grpo_groups),
        "dpo_candidate_pairs": len(dpo_candidates),
        "sft_candidate_traces": len(sft_candidates),
        "split": "train_only",
        "holdout_read": False,
        "training_approval": False,
        "teach_back_auto_verified": False,
        "output_sha256": sha256_file(a.output),
        "sidecar_sha256": {name: sha256_file(a.output.parent / name) for name in sidecars},
    }
    a.output.with_suffix(".manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
