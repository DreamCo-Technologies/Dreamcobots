#!/usr/bin/env python3
"""Tiny from-scratch Buddy byte-language-model experiment; no downloads or paid calls.

Requires locally installed PyTorch. Research/smoke only: does not load external
checkpoints, make production changes, or demonstrate general model competence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from collections import Counter
from pathlib import Path

import torch
from torch import nn
import torch.nn.functional as F

PAD, BOS, EOS = 0, 1, 2
VOCAB = 259


def load_records(path: Path):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError("No training records")
    groups, pairs, counts = {}, set(), Counter()
    for row in rows:
        required = ("prompt", "completion", "domain", "source_id", "split", "provenance", "license", "consent")
        if any(k not in row for k in required):
            raise ValueError("Missing provenance or training fields")
        if row["license"] not in ("owner_created", "CC0-1.0", "MIT") or row["consent"] is not True:
            raise ValueError("Unapproved declared rights or missing consent; source claims require independent review")
        if row["split"] not in ("train", "holdout"):
            raise ValueError("Split must be train or holdout")
        if not all(isinstance(row[k], str) and row[k].strip() for k in ("prompt", "completion", "domain", "source_id", "provenance")):
            raise ValueError("Empty or invalid record fields")
        group = row["source_id"]
        if group in groups and groups[group] != row["split"]:
            raise ValueError("Source leakage across splits")
        groups[group] = row["split"]
        pair = (row["prompt"].strip(), row["completion"].strip())
        if pair in pairs:
            raise ValueError("Duplicate example")
        pairs.add(pair)
        counts[row["split"]] += 1
    if not counts["train"] or not counts["holdout"]:
        raise ValueError("Both train and holdout are required")
    return rows


def encoded(row, context):
    prefix = ("Task: " + row["prompt"] + "\nAnswer: ").encode("utf-8")
    answer = row["completion"].encode("utf-8")
    tokens = [BOS] + [b + 3 for b in prefix + answer] + [EOS]
    if len(tokens) > context:
        raise ValueError("Record exceeds context; never silently truncate")
    start = 1 + len(prefix)
    inp = tokens[:-1]
    labels = [-100] * (start - 1) + tokens[start:]
    return inp, labels


class TinyBuddy(nn.Module):
    def __init__(self, width=48, layers=2, heads=4, context=192):
        super().__init__()
        self.context = context
        self.embed = nn.Embedding(VOCAB, width)
        self.position = nn.Embedding(context, width)
        layer = nn.TransformerEncoderLayer(width, heads, dim_feedforward=width * 4, dropout=0.0, batch_first=True, norm_first=True)
        self.blocks = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(width)
        self.output = nn.Linear(width, VOCAB, bias=False)
        self.output.weight = self.embed.weight

    def forward(self, tokens):
        n = tokens.shape[1]
        if n > self.context:
            raise ValueError("Context exceeded")
        pos = torch.arange(n, device=tokens.device)
        x = self.embed(tokens) + self.position(pos)[None, :, :]
        causal = torch.ones((n, n), device=tokens.device, dtype=torch.bool).triu(1)
        return self.output(self.norm(self.blocks(x, mask=causal)))


def batch(rows, context, device):
    examples = [encoded(r, context) for r in rows]
    max_len = max(len(x) for x, _ in examples)
    xs, ys = [], []
    for x, y in examples:
        xs.append(x + [PAD] * (max_len - len(x)))
        ys.append(y + [-100] * (max_len - len(y)))
    return torch.tensor(xs, device=device), torch.tensor(ys, device=device)


@torch.no_grad()
def loss_on(model, rows, context, device):
    model.eval()
    values = []
    for row in rows:
        x, y = batch([row], context, device)
        logits = model(x)
        values.append(F.cross_entropy(logits.reshape(-1, VOCAB), y.reshape(-1), ignore_index=-100).item())
    return sum(values) / len(values)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--steps", type=int, default=5)
    p.add_argument("--context", type=int, default=192)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--device", choices=("cpu", "cuda", "mps"), default="cpu")
    args = p.parse_args()
    if not 1 <= args.steps <= 1000 or not 64 <= args.context <= 1024:
        p.error("Invalid step/context bounds")
    if args.device == "cuda" and not torch.cuda.is_available():
        p.error("CUDA unavailable")
    if args.device == "mps" and not torch.backends.mps.is_available():
        p.error("MPS unavailable")
    torch.set_num_threads(min(torch.get_num_threads(), 2))
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    device = torch.device(args.device)
    rows = load_records(args.data)
    train = [r for r in rows if r["split"] == "train"]
    holdout = [r for r in rows if r["split"] == "holdout"]
    for row in rows:
        encoded(row, args.context)
    model = TinyBuddy(context=args.context).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
    before = loss_on(model, holdout, args.context, device)
    start = time.monotonic()
    for _ in range(args.steps):
        model.train()
        sampled = random.sample(train, min(4, len(train)))
        x, y = batch(sampled, args.context, device)
        logits = model(x)
        loss = F.cross_entropy(logits.reshape(-1, VOCAB), y.reshape(-1), ignore_index=-100)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
    after = loss_on(model, holdout, args.context, device)
    args.out.mkdir(parents=True, exist_ok=True)
    checkpoint = args.out / "buddy-flash-smoke.pt"
    torch.save({"state_dict": model.cpu().state_dict(), "architecture": {"width": 48, "layers": 2, "heads": 4, "context": args.context}, "tokenizer": "utf8_bytes_plus_3"}, checkpoint)
    digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    report = {
        "status": "trained_smoke_only_not_production",
        "seed": args.seed, "steps": args.steps, "device": args.device,
        "parameters": sum(p.numel() for p in model.parameters()),
        "train_records": len(train), "holdout_records": len(holdout),
        "train_domains": dict(Counter(r["domain"] for r in train)),
        "holdout_domains": dict(Counter(r["domain"] for r in holdout)),
        "holdout_cross_entropy_before": before,
        "holdout_cross_entropy_after": after,
        "seconds": round(time.monotonic() - start, 3),
        "dataset_sha256": hashlib.sha256(args.data.read_bytes()).hexdigest(),
        "checkpoint_sha256": digest,
        "limitations": "Tiny synthetic fixture; loss is not accuracy or domain mastery. No inference serving or deployment.",
    }
    (args.out / "receipt.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
