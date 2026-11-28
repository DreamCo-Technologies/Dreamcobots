"""Opt-in causal pretraining, supervised fine-tuning and DPO weight training.

No data is downloaded. Every run verifies an Ed25519-signed dataset manifest,
checks every dataset hash and deterministic split, and requires an explicit
weight-update authorization reference before optimizer steps can begin.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

try:
    from .guardrails import assert_training_split, iter_authorized_records, verify_signed_manifest, verify_signed_shard_manifest
except ImportError:  # direct script invocation from this directory
    from guardrails import assert_training_split, iter_authorized_records, verify_signed_manifest, verify_signed_shard_manifest


def load_recipe(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        recipe = json.loads(text)
    else:
        import yaml
        recipe = yaml.safe_load(text)
    if not isinstance(recipe, dict) or recipe.get("schema") != "dreamco.foundry.recipe.v1":
        raise ValueError("unsupported or missing DreamCo Foundry recipe schema")
    if not recipe.get("artifact_dir"):
        raise ValueError("recipe must declare artifact_dir")
    return recipe


def validated_preferences(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Only use verified lab-pass/teach-back responses against lab-failed responses."""
    result = []
    for row in records:
        if not all(isinstance(row.get(key), str) and row[key].strip()
                   for key in ("prompt", "chosen", "rejected")):
            continue
        chosen_ok = (
            row.get("chosen_status") == "LAB_PASSED"
            and row.get("teach_back_verified") is True
        )
        rejected_ok = row.get("rejected_status") == "LAB_FAILED"
        if chosen_ok and rejected_ok:
            result.append({
                "prompt": row["prompt"],
                "chosen": row["chosen"],
                "rejected": row["rejected"],
            })
    return result


def sft_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in records:
        messages = row.get("messages")
        if not isinstance(messages, list) or not messages:
            continue
        if not any(
            isinstance(message, dict)
            and message.get("role") in {"assistant", "tool"}
            and isinstance(message.get("content"), str)
            and message["content"].strip()
            for message in messages
        ):
            continue
        rows.append({"messages": messages})
    return rows


def _load_runtime():
    try:
        import torch
        from torch.utils.data import Dataset
        from transformers import (
            AutoModelForCausalLM, AutoTokenizer, LlamaConfig, LlamaForCausalLM,
            Trainer, TrainingArguments,
        )
    except ImportError as exc:
        raise RuntimeError(
            "Install stages/05_model_foundry/requirements-foundry.txt to execute training"
        ) from exc
    return torch, Dataset, AutoModelForCausalLM, AutoTokenizer, LlamaConfig, LlamaForCausalLM, Trainer, TrainingArguments


def _load_model(recipe: dict[str, Any], tokenizer, checkpoint: Path | None = None):
    torch, _, AutoModelForCausalLM, _, LlamaConfig, LlamaForCausalLM, _, _ = _load_runtime()
    if checkpoint and (checkpoint / "adapter_config.json").exists():
        base = recipe.get("base_model", {})
        model_id, revision = base.get("id"), base.get("revision")
        if not model_id or not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise PermissionError("loading a LoRA checkpoint requires the pinned base model revision")
        if base.get("license_review_status") != "APPROVED" or not str(base.get("license_evidence_id", "")).strip():
            raise PermissionError("loading an open-weight adapter requires approved model license evidence")
        base_model = AutoModelForCausalLM.from_pretrained(
            model_id, revision=revision, trust_remote_code=False,
            use_safetensors=True, torch_dtype="auto",
        )
        from peft import PeftModel
        model = PeftModel.from_pretrained(base_model, checkpoint, is_trainable=True)
    elif checkpoint:
        model = AutoModelForCausalLM.from_pretrained(
            checkpoint, trust_remote_code=False, use_safetensors=True
        )
    elif recipe.get("mode") == "scratch":
        arch = recipe.get("architecture", {})
        config = LlamaConfig(
            vocab_size=len(tokenizer),
            hidden_size=int(arch.get("hidden_size", 512)),
            intermediate_size=int(arch.get("intermediate_size", 1376)),
            num_hidden_layers=int(arch.get("layers", 8)),
            num_attention_heads=int(arch.get("attention_heads", 8)),
            max_position_embeddings=int(recipe.get("packing", {}).get("sequence_length", 1024)),
            tie_word_embeddings=True,
            bos_token_id=tokenizer.bos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
        model = LlamaForCausalLM(config)
        target = int(arch.get("parameters_target", 45_000_000))
        actual = sum(parameter.numel() for parameter in model.parameters())
        if abs(actual - target) / target > 0.20:
            raise ValueError(
                f"scratch architecture has {actual:,} parameters; target is {target:,} (20% tolerance)"
            )
    else:
        base = recipe.get("base_model", {})
        model_id = base.get("id")
        revision = base.get("revision")
        if not model_id or not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise PermissionError("open-weight base model requires an exact 40-character reviewed commit SHA")
        if base.get("license_review_status") != "APPROVED" or not str(base.get("license_evidence_id", "")).strip():
            raise PermissionError("open-weight training requires owner-approved model license evidence")
        model = AutoModelForCausalLM.from_pretrained(
            model_id, revision=revision, trust_remote_code=False,
            use_safetensors=True, torch_dtype="auto",
        )
        if len(tokenizer) != model.get_input_embeddings().weight.shape[0]:
            model.resize_token_embeddings(len(tokenizer), mean_resizing=True)
    return model


class _PackedDataset:
    def __new__(cls, shard_paths: list[Path], sequence_length: int):
        torch, Dataset, *_ = _load_runtime()
        import numpy as np

        class DatasetImpl(Dataset):
            def __init__(self):
                self.sequence_length = sequence_length
                self.maps = [np.memmap(path, dtype=np.uint32, mode="r") for path in shard_paths]
                self.lengths = [len(item) // sequence_length for item in self.maps]
                self.total = sum(self.lengths)
                if not self.total:
                    raise ValueError("no complete packed training sequences were found")

            def __len__(self):
                return self.total

            def __getitem__(self, index):
                for array, count in zip(self.maps, self.lengths):
                    if index < count:
                        start = index * self.sequence_length
                        ids = torch.tensor(array[start:start + self.sequence_length].astype("int64"))
                        return {"input_ids": ids, "labels": ids.clone(), "attention_mask": torch.ones_like(ids)}
                    index -= count
                raise IndexError(index)
        return DatasetImpl()


def _sft_dataset(rows, tokenizer, max_length: int):
    torch, Dataset, *_ = _load_runtime()
    items = []
    role_tokens = {
        "system": "<|system|>", "user": "<|user|>",
        "assistant": "<|assistant|>", "tool": "<|tool_call|>",
    }
    for row in rows:
        input_ids, labels = [], []
        for message in row["messages"]:
            role = message.get("role")
            if role not in role_tokens:
                continue
            marker = tokenizer.encode(role_tokens[role], add_special_tokens=False)
            body = tokenizer.encode(str(message.get("content", "")), add_special_tokens=False)
            segment = marker + body
            if tokenizer.eos_token_id is not None:
                segment.append(tokenizer.eos_token_id)
            input_ids.extend(segment)
            labels.extend(segment if role in {"assistant", "tool"} else [-100] * len(segment))
        input_ids, labels = input_ids[:max_length], labels[:max_length]
        if any(value != -100 for value in labels):
            items.append((input_ids, labels))
    if not items:
        raise ValueError("no SFT examples contain assistant/tool targets after loss masking")

    class DatasetImpl(Dataset):
        def __len__(self):
            return len(items)

        def __getitem__(self, index):
            ids, target = items[index]
            tensor = torch.tensor(ids, dtype=torch.long)
            return {
                "input_ids": tensor,
                "labels": torch.tensor(target, dtype=torch.long),
                "attention_mask": torch.ones_like(tensor),
            }
    return DatasetImpl()


def _collate(batch, tokenizer):
    import torch
    pad_id = tokenizer.pad_token_id
    if pad_id is None:
        pad_id = tokenizer.eos_token_id
    width = max(item["input_ids"].shape[0] for item in batch)
    ids, labels, masks = [], [], []
    for item in batch:
        n = width - item["input_ids"].shape[0]
        ids.append(torch.nn.functional.pad(item["input_ids"], (0, n), value=pad_id))
        labels.append(torch.nn.functional.pad(item["labels"], (0, n), value=-100))
        masks.append(torch.nn.functional.pad(item["attention_mask"], (0, n), value=0))
    return {
        "input_ids": torch.stack(ids),
        "labels": torch.stack(labels),
        "attention_mask": torch.stack(masks),
    }


def _training_args(output: Path, stage_cfg: dict[str, Any], recipe: dict[str, Any], *, eval_enabled=False):
    _, _, _, _, _, _, _, TrainingArguments = _load_runtime()
    return TrainingArguments(
        output_dir=str(output),
        num_train_epochs=float(stage_cfg.get("epochs", 1)),
        per_device_train_batch_size=int(stage_cfg.get("batch_size", 1)),
        gradient_accumulation_steps=int(stage_cfg.get("grad_accum_steps", 1)),
        learning_rate=float(stage_cfg.get("learning_rate", 1e-4)),
        warmup_ratio=float(stage_cfg.get("warmup_ratio", 0.03)),
        weight_decay=float(stage_cfg.get("weight_decay", 0.01)),
        logging_steps=10,
        save_strategy="epoch",
        eval_strategy="epoch" if eval_enabled else "no",
        report_to="none",
        seed=int(recipe.get("seed", 42)),
        remove_unused_columns=False,
        save_safetensors=True,
    )


def execute_stage(stage: str, recipe: dict[str, Any], manifest: dict[str, Any],
                  tokenizer_path: Path, shard_dir: Path | None, checkpoint: Path | None,
                  output: Path) -> Path:
    torch, _, AutoModelForCausalLM, AutoTokenizer, _, _, Trainer, _ = _load_runtime()
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, trust_remote_code=False)
    model = _load_model(recipe, tokenizer, checkpoint)
    adapter = recipe.get("architecture", {}).get("adapter")
    if adapter == "lora" and stage in {"pretrain", "sft", "dpo"} and not hasattr(model, "peft_config"):
        try:
            from peft import LoraConfig, get_peft_model
        except ImportError as exc:
            raise RuntimeError("LoRA recipe requires peft") from exc
        model = get_peft_model(model, LoraConfig(
            r=int(recipe["architecture"].get("rank", 16)),
            lora_alpha=int(recipe["architecture"].get("alpha", 32)),
            lora_dropout=float(recipe["architecture"].get("dropout", 0.05)),
            bias="none", task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        ))

    output.mkdir(parents=True, exist_ok=True)
    if stage == "pretrain":
        if shard_dir is None:
            raise ValueError("pretrain requires --token-shards pointing to pack_tokens.py output")
        shard_paths = sorted(shard_dir.glob("train-*.bin"))
        if not shard_paths:
            raise ValueError("no train-*.bin shards found")
        dataset = _PackedDataset(shard_paths, int(recipe["packing"]["sequence_length"]))
        validation_paths = sorted(shard_dir.glob("validation-*.bin"))
        validation_dataset = (
            _PackedDataset(validation_paths, int(recipe["packing"]["sequence_length"]))
            if validation_paths else None
        )
        cfg = recipe.get("pretrain", {})
        trainer = Trainer(
            model=model, args=_training_args(output, cfg, recipe, eval_enabled=validation_dataset is not None),
            train_dataset=dataset, eval_dataset=validation_dataset,
            data_collator=lambda batch: _collate(batch, tokenizer),
        )
    elif stage == "sft":
        records = list(iter_authorized_records(manifest, categories={"verified_trajectories"}, splits={"train"}))
        rows = sft_rows(records)
        dataset = _sft_dataset(rows, tokenizer, int(recipe.get("sft", {}).get("max_seq_length", 2048)))
        cfg = recipe.get("sft", {})
        trainer = Trainer(
            model=model, args=_training_args(output, cfg, recipe),
            train_dataset=dataset, data_collator=lambda batch: _collate(batch, tokenizer),
        )
    else:
        records = list(iter_authorized_records(manifest, categories={"verified_preferences"}, splits={"train"}))
        pairs = validated_preferences(records)
        if not pairs:
            raise ValueError("DPO requires chosen LAB_PASSED + TEACH_BACK_VERIFIED and rejected LAB_FAILED pairs")
        try:
            from datasets import Dataset as HFDataset
            from trl import DPOConfig, DPOTrainer
        except ImportError as exc:
            raise RuntimeError("DPO stage requires datasets and trl") from exc
        cfg = recipe.get("dpo", {})
        args = DPOConfig(
            output_dir=str(output),
            num_train_epochs=float(cfg.get("epochs", 1)),
            per_device_train_batch_size=int(cfg.get("batch_size", 1)),
            gradient_accumulation_steps=int(cfg.get("grad_accum_steps", 1)),
            learning_rate=float(cfg.get("learning_rate", 5e-6)),
            beta=float(cfg.get("beta", 0.1)),
            logging_steps=10, save_strategy="epoch", report_to="none",
            seed=int(recipe.get("seed", 42)),
        )
        trainer = DPOTrainer(
            model=model, args=args, train_dataset=HFDataset.from_list(pairs),
            processing_class=tokenizer,
        )
    trainer.train()
    trainer.save_model(str(output))
    tokenizer.save_pretrained(output)
    summary = {
        "schema": "dreamco.foundry.checkpoint.v1",
        "stage": stage,
        "checkpoint_dir": str(output),
        "checkpoint_sha256": hashlib.sha256(
            b"".join(sorted(path.read_bytes() for path in output.glob("*.safetensors")))
        ).hexdigest() if list(output.glob("*.safetensors")) else None,
        "source_manifest_sha256": hashlib.sha256(
            json.dumps(manifest, sort_keys=True, default=str).encode()
        ).hexdigest(),
        "training_split": "train",
        "holdout_used_for_training": False,
        "weight_updates_started": True,
    }
    (output / "checkpoint_manifest.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description="DreamCo opt-in PT/CPT, SFT and DPO weight trainer")
    parser.add_argument("--stage", choices=["pretrain", "sft", "dpo", "all"], required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--token-shards", type=Path)
    parser.add_argument("--shard-manifest", type=Path)
    parser.add_argument("--shard-signature", type=Path)
    parser.add_argument("--input-checkpoint", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--execute", action="store_true", help="actually run optimizer steps")
    parser.add_argument("--authorize-weight-updates", action="store_true")
    parser.add_argument("--authorization-reference")
    args = parser.parse_args()

    recipe = load_recipe(args.recipe)
    manifest = verify_signed_manifest(args.manifest, args.signature, args.public_key)
    stages = ["pretrain", "sft", "dpo"] if args.stage == "all" else [args.stage]
    categories = {
        "pretrain": {"study_guides", "verified_trajectories", "general_replay"},
        "sft": {"verified_trajectories"},
        "dpo": {"verified_preferences"},
    }
    counts = {
        stage: sum(1 for _ in iter_authorized_records(manifest, categories=categories[stage], splits={"train"}))
        for stage in stages
    }
    if any(counts[stage] == 0 for stage in stages):
        raise ValueError(f"no signed, authorized train records for requested stages: {counts}")
    if "pretrain" in stages:
        if not args.shard_manifest or not args.shard_signature or not args.token_shards:
            raise PermissionError("pretraining requires a policy-signed shard manifest and --token-shards directory")
        shard_payload = verify_signed_shard_manifest(
            args.shard_manifest, args.shard_signature, args.manifest, args.signature, args.public_key
        )
        if args.token_shards.resolve() != args.shard_manifest.parent.resolve():
            raise PermissionError("--token-shards must be the directory containing the verified signed shard manifest")
        if not shard_payload.get("train"):
            raise ValueError("signed shard manifest has no train shard")

    if not args.execute:
        summary = {
            "schema": "dreamco.foundry.training_preflight.v1",
            "stages": stages, "authorized_train_records": counts,
            "excluded_splits": ["validation", "holdout"],
            "weight_updates_started": False,
            "next_step": "Review the signed dataset and recipe, then pass --execute, --authorize-weight-updates and an approval reference.",
        }
        print(json.dumps(summary, sort_keys=True))
        return
    if not args.authorize_weight_updates or not args.authorization_reference:
        raise PermissionError("optimizer steps require --authorize-weight-updates and --authorization-reference")
    if not args.authorization_reference.strip():
        raise PermissionError("authorization reference must be non-empty")

    active = args.input_checkpoint
    if stages[0] in {"sft", "dpo"} and active is None:
        previous = "pretrain" if stages[0] == "sft" else "sft"
        candidate = Path(recipe["artifact_dir"]) / "checkpoints" / previous
        if candidate.exists():
            active = candidate
        else:
            raise ValueError(f"{stages[0]} requires --input-checkpoint or an existing {previous} checkpoint")
    for stage in stages:
        if args.output and len(stages) > 1:
            target = args.output / stage
        else:
            target = args.output or (Path(recipe["artifact_dir"]) / "checkpoints" / stage)
        active = execute_stage(stage, recipe, manifest, args.tokenizer, args.token_shards, active, target)
    print(json.dumps({"stages_completed": stages, "final_checkpoint": str(active)}, sort_keys=True))


if __name__ == "__main__":
    main()
