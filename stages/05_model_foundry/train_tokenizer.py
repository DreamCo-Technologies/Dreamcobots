"""Train a BPE tokenizer only from signed, commercially cleared train records."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .guardrails import iter_authorized_records, verify_signed_manifest

SPECIAL_TOKENS = ["<|pad|>", "<|bos|>", "<|eos|>", "<|unk|>", "<|system|>",
                  "<|user|>", "<|assistant|>", "<|tool_call|>", "<|division_id|>",
                  "<|sandbox_stdout|>", "<|teach_back|>", "<|rubric_pass|>"]

def corpus(manifest):
    for row in iter_authorized_records(manifest, splits={"train"}):
        fields = [row.get("title", ""), row.get("core_concepts", ""),
                  row.get("worked_examples", ""), row.get("content", "")]
        objectives = row.get("learning_objectives", [])
        if isinstance(objectives, list):
            fields.extend(str(x) for x in objectives)
        yield "\n\n".join(str(x) for x in fields if x)
        for msg in row.get("messages", []):
            if msg.get("role") in {"assistant", "tool"} and msg.get("content"):
                yield str(msg["content"])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--signature",type=Path,required=True)
    ap.add_argument("--public-key",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--vocab-size",type=int,default=16384)
    a=ap.parse_args()
    if a.vocab_size < 256: raise ValueError("vocab-size must be at least 256")
    manifest=verify_signed_manifest(a.manifest,a.signature,a.public_key)
    try:
        from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
        from transformers import PreTrainedTokenizerFast
    except ImportError as exc:
        raise RuntimeError("Install tokenizers and transformers to train a tokenizer") from exc
    tok=Tokenizer(models.BPE(unk_token="<|unk|>"))
    tok.pre_tokenizer=pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder=decoders.ByteLevel()
    trainer=trainers.BpeTrainer(vocab_size=a.vocab_size,min_frequency=2,
        special_tokens=SPECIAL_TOKENS,initial_alphabet=pre_tokenizers.ByteLevel.alphabet())
    tok.train_from_iterator(corpus(manifest),trainer=trainer)
    a.output.mkdir(parents=True,exist_ok=True)
    hf=PreTrainedTokenizerFast(tokenizer_object=tok,unk_token="<|unk|>",pad_token="<|pad|>",
        bos_token="<|bos|>",eos_token="<|eos|>",additional_special_tokens=SPECIAL_TOKENS[4:-1]+[SPECIAL_TOKENS[-1]])
    hf.save_pretrained(a.output)
    meta={"schema":"dreamco.foundry.tokenizer_artifact.v1","vocab_size":len(hf),
          "source_manifest_sha256":__import__("hashlib").sha256(a.manifest.read_bytes()).hexdigest(),
          "training_splits":["train"],"excluded_splits":["validation","holdout"],
          "policy_decisions":sorted({d["policy_decision_id"] for d in manifest["datasets"]})}
    (a.output/"foundry-tokenizer-manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
if __name__=="__main__": main()
