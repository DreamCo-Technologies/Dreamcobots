"""Offline 25M+ parameter Buddy model trainer with an explicit zero-cost authorization gate.

Requires separately installed torch and a user-supplied training split. No teacher
API, dataset download, hosted compute, or automatic CI invocation is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .training_gate import evaluate_training


def _authorized_training_input(data_path: str, authorization_path: str) -> tuple[bytes, dict]:
    data_file = Path(data_path)
    auth_file = Path(authorization_path)
    if not data_file.is_file() or not auth_file.is_file():
        raise PermissionError("training data and authorization manifest must both exist")
    raw = data_file.read_bytes()
    spec = json.loads(auth_file.read_text(encoding="utf-8"))
    gate = evaluate_training(spec)
    if not gate["ready_for_review"]:
        raise PermissionError("training readiness blocked: " + ", ".join(gate["missing"]))
    if spec.get("training_execution_approved") is not True:
        raise PermissionError("separate explicit training_execution_approved=true is required")
    if float(spec.get("max_cost_usd", -1)) != 0.0:
        raise PermissionError("this trainer only permits a zero-cost local compute budget")
    if spec.get("compute_profile") not in {"local_cpu", "local_mps", "local_cpu_or_mps"}:
        raise PermissionError("compute profile must be an approved local CPU/MPS profile")
    digest = hashlib.sha256(raw).hexdigest()
    if spec.get("train_split_sha256") != digest:
        raise PermissionError("training split SHA-256 does not match the supplied file")
    if spec.get("holdout_split_sha256") == digest:
        raise PermissionError("training and holdout splits must be independent")
    if len(str(spec.get("dataset_sha256", ""))) != 64:
        raise PermissionError("dataset SHA-256 must be a 64-character digest")
    return raw, spec


def train(
    data_path: str,
    output_dir: str,
    steps: int = 100,
    *,
    authorization_path: str,
    context: int = 128,
    seed: int = 42,
):
    if steps < 1 or steps > 100000 or context < 16 or context > 2048:
        raise ValueError("unsafe training configuration")
    # All rights, owner, holdout, explicit-run, and zero-cost checks happen
    # before importing the training framework or allocating compute.
    raw, authorization = _authorized_training_input(data_path, authorization_path)
    import torch
    from torch import nn

    torch.manual_seed(seed)
    has_mps = bool(torch.backends.mps.is_available())
    profile = authorization["compute_profile"]
    if profile == "local_mps" and not has_mps:
        raise PermissionError("approved MPS device is unavailable")
    device_name = "mps" if profile in {"local_mps", "local_cpu_or_mps"} and has_mps else "cpu"
    device = torch.device(device_name)
    # Byte-level tokenization is a transparent baseline, not a competitive tokenizer.
    vocab, dim, layers, heads = 256, 512, 8, 8

    class Model(nn.Module):
        def __init__(self):
            super().__init__()
            self.token = nn.Embedding(vocab, dim)
            self.position = nn.Embedding(context, dim)
            block = nn.TransformerEncoderLayer(
                dim, heads, dim_feedforward=2048, dropout=0.0,
                batch_first=True, norm_first=True,
            )
            self.blocks = nn.TransformerEncoder(block, layers, enable_nested_tensor=False)
            self.norm = nn.LayerNorm(dim)
            self.head = nn.Linear(dim, vocab, bias=False)

        def forward(self, x):
            positions = torch.arange(x.shape[1], device=x.device)
            hidden = self.token(x) + self.position(positions)
            mask = torch.ones(
                (x.shape[1], x.shape[1]), device=x.device, dtype=torch.bool
            ).triu(1)
            return self.head(self.norm(self.blocks(hidden, mask=mask)))

    model = Model().to(device)
    count = sum(parameter.numel() for parameter in model.parameters())
    if count < 25_000_000:
        raise RuntimeError(f"model has only {count} parameters")
    tokens = torch.tensor(list(raw), dtype=torch.long)
    if len(tokens) < context * 4:
        raise ValueError("insufficient training-split data")
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-4)
    losses = []
    model.train()
    for _step in range(steps):
        starts = torch.randint(0, len(tokens) - context - 1, (2,))
        x = torch.stack([tokens[index:index + context] for index in starts]).to(device)
        y = torch.stack([tokens[index + 1:index + context + 1] for index in starts]).to(device)
        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        loss = nn.functional.cross_entropy(logits.reshape(-1, vocab), y.reshape(-1))
        if not torch.isfinite(loss):
            raise RuntimeError("nonfinite training loss")
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        losses.append(round(float(loss.detach().cpu()), 5))

    target = Path(output_dir).resolve()
    target.mkdir(parents=True, exist_ok=True)
    torch.save(model.cpu().state_dict(), target / "buddy-original-25m-state.pt")
    report = {
        "parameters": count,
        "steps": steps,
        "context": context,
        "seed": seed,
        "loss_first": losses[0],
        "loss_last": losses[-1],
        "teacher": "none",
        "distilled": False,
        "dataset_id": authorization["dataset_id"],
        "dataset_sha256": authorization["dataset_sha256"],
        "train_split_sha256": authorization["train_split_sha256"],
        "holdout_split_sha256": authorization["holdout_split_sha256"],
        "license": authorization["license"],
        "compute_profile": authorization["compute_profile"],
        "actual_device": device_name,
        "max_cost_usd": 0,
        "authorization_sha256": hashlib.sha256(
            Path(authorization_path).read_bytes()
        ).hexdigest(),
        "evaluation_status": "unverified",
        "production_ready": False,
    }
    (target / "training-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--licensed-data", required=True)
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--context", type=int, default=128)
    args = parser.parse_args()
    print(json.dumps(train(
        args.licensed_data,
        args.output_dir,
        args.steps,
        authorization_path=args.authorization,
        context=args.context,
    ), indent=2))


if __name__ == "__main__":
    main()
