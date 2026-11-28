"""Train or extend a tokenizer using only signed, commercially cleared train records."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
try:
    from .guardrails import iter_authorized_records, verify_signed_manifest
except ImportError:
    from guardrails import iter_authorized_records, verify_signed_manifest

SPECIAL_TOKENS = ["<|pad|>", "<|bos|>", "<|eos|>", "<|unk|>", "<|system|>", "<|user|>",
                  "<|assistant|>", "<|tool_call|>", "<|division_id|>", "<|sandbox_stdout|>",
                  "<|teach_back|>", "<|rubric_pass|>"]

def corpus(manifest):
    for row in iter_authorized_records(manifest, splits={"train"}):
        fields = [row.get("title", ""), row.get("core_concepts", ""),
                  row.get("worked_examples", ""), row.get("content", "")]
        objectives = row.get("learning_objectives", [])
        if isinstance(objectives, list):
            fields.extend(str(value) for value in objectives)
        yield "\n\n".join(str(value) for value in fields if value)
        for message in row.get("messages", []):
            if message.get("role") in {"assistant", "tool"} and message.get("content"):
                yield str(message["content"])

def main():
    parser = argparse.ArgumentParser(description="DreamCo signed-data tokenizer trainer")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["scratch", "extend"], default="scratch")
    parser.add_argument("--vocab-size", type=int, default=16384)
    parser.add_argument("--base-model")
    parser.add_argument("--base-revision")
    args = parser.parse_args()
    if args.vocab_size < 256:
        raise ValueError("vocab-size must be at least 256")
    manifest = verify_signed_manifest(args.manifest, args.signature, args.public_key)
    args.output.mkdir(parents=True, exist_ok=True)

    if args.mode == "scratch":
        from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
        from transformers import PreTrainedTokenizerFast
        tokenizer = Tokenizer(models.BPE(unk_token="<|unk|>"))
        tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        tokenizer.decoder = decoders.ByteLevel()
        trainer = trainers.BpeTrainer(
            vocab_size=args.vocab_size, min_frequency=2, special_tokens=SPECIAL_TOKENS,
            initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
        )
        tokenizer.train_from_iterator(corpus(manifest), trainer=trainer)
        hf_tokenizer = PreTrainedTokenizerFast(
            tokenizer_object=tokenizer, unk_token="<|unk|>", pad_token="<|pad|>",
            bos_token="<|bos|>", eos_token="<|eos|>",
            additional_special_tokens=SPECIAL_TOKENS[4:],
        )
    else:
        if not args.base_model or not isinstance(args.base_revision, str) or not re.fullmatch(r"[0-9a-f]{40}", args.base_revision):
            raise PermissionError("tokenizer extension requires a base model and exact reviewed 40-character commit SHA")
        from transformers import AutoTokenizer
        hf_tokenizer = AutoTokenizer.from_pretrained(
            args.base_model, revision=args.base_revision, trust_remote_code=False, use_fast=True,
        )
        if not hf_tokenizer.is_fast or not hasattr(hf_tokenizer, "train_new_from_iterator"):
            raise ValueError("base tokenizer must be a fast tokenizer supporting train_new_from_iterator")
        if args.vocab_size <= len(hf_tokenizer):
            raise ValueError("extended vocab-size must exceed the base tokenizer vocabulary")
        hf_tokenizer = hf_tokenizer.train_new_from_iterator(corpus(manifest), vocab_size=args.vocab_size)
        hf_tokenizer.add_special_tokens({
            "additional_special_tokens": [
                token for token in SPECIAL_TOKENS
                if token not in {hf_tokenizer.pad_token, hf_tokenizer.bos_token,
                                 hf_tokenizer.eos_token, hf_tokenizer.unk_token}
            ]
        })
        if hf_tokenizer.pad_token is None:
            hf_tokenizer.add_special_tokens({"pad_token": "<|pad|>"})

    hf_tokenizer.save_pretrained(args.output)
    metadata = {
        "schema": "dreamco.foundry.tokenizer_artifact.v1", "mode": args.mode,
        "vocab_size": len(hf_tokenizer),
        "base_model": args.base_model if args.mode == "extend" else None,
        "base_revision": args.base_revision if args.mode == "extend" else None,
        "source_manifest_sha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        "training_splits": ["train"], "excluded_splits": ["validation", "holdout"],
        "policy_decisions": sorted({item["policy_decision_id"] for item in manifest["datasets"]}),
        "special_tokens": SPECIAL_TOKENS,
    }
    (args.output / "foundry-tokenizer-manifest.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8",
    )

if __name__ == "__main__":
    main()
