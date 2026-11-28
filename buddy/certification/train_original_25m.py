"""Buddy Original: offline 25M+ parameter causal language model training.

Requires separately installed torch; no teacher API, dataset download, or spending.
Supply a rights-cleared UTF-8 text file. Outputs are local, not Git-tracked.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

def train(data_path: str, output_dir: str, steps: int = 100, *, context: int = 128, seed: int = 42):
    if steps < 1 or steps > 100000 or context < 16 or context > 2048:
        raise ValueError("unsafe training configuration")
    import torch
    from torch import nn
    torch.manual_seed(seed)
    raw = Path(data_path).read_bytes()
    if len(raw) < context * 4:
        raise ValueError("insufficient licensed training data")
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    # Byte-level tokenization is a transparent baseline, not a competitive tokenizer.
    vocab, dim, layers, heads = 256, 512, 8, 8
    class Model(nn.Module):
        def __init__(self):
            super().__init__()
            self.token = nn.Embedding(vocab, dim)
            self.position = nn.Embedding(context, dim)
            block = nn.TransformerEncoderLayer(dim, heads, dim_feedforward=2048,
                                                dropout=0.0, batch_first=True, norm_first=True)
            self.blocks = nn.TransformerEncoder(block, layers, enable_nested_tensor=False)
            self.norm = nn.LayerNorm(dim)
            self.head = nn.Linear(dim, vocab, bias=False)
        def forward(self, x):
            positions = torch.arange(x.shape[1], device=x.device)
            h = self.token(x) + self.position(positions)
            mask = torch.ones((x.shape[1], x.shape[1]), device=x.device, dtype=torch.bool).triu(1)
            return self.head(self.norm(self.blocks(h, mask=mask)))
    model = Model().to(device)
    count = sum(p.numel() for p in model.parameters())
    if count < 25_000_000:
        raise RuntimeError(f"model has only {count} parameters")
    tokens = torch.tensor(list(raw), dtype=torch.long)
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
    losses = []
    model.train()
    for step in range(steps):
        starts = torch.randint(0, len(tokens) - context - 1, (2,))
        x = torch.stack([tokens[i:i+context] for i in starts]).to(device)
        y = torch.stack([tokens[i+1:i+context+1] for i in starts]).to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        loss = nn.functional.cross_entropy(logits.reshape(-1, vocab), y.reshape(-1))
        if not torch.isfinite(loss):
            raise RuntimeError("nonfinite training loss")
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(round(float(loss.detach().cpu()), 5))
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    torch.save(model.cpu().state_dict(), target / "buddy-original-25m-state.pt")
    report = {"parameters": count, "steps": steps, "context": context,
              "seed": seed, "loss_first": losses[0], "loss_last": losses[-1],
              "teacher": "none", "distilled": False,
              "evaluation_status": "unverified", "production_ready": False}
    (target / "training-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--licensed-data", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--context", type=int, default=128)
    args = parser.parse_args()
    print(json.dumps(train(args.licensed_data, args.output_dir, args.steps, context=args.context), indent=2))

if __name__ == "__main__":
    main()
