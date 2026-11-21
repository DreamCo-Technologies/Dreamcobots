"""Small, CPU-only GPT-style reference model for deterministic baseline checks.

This module performs inference/evaluation only. It deliberately has no optimizer,
training loop, checkpoint writer, network access, or model-download path.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(frozen=True)
class TinyGPTConfig:
    vocab_size: int = 256
    block_size: int = 32
    n_layer: int = 2
    n_head: int = 2
    n_embd: int = 32
    dropout: float = 0.0

    def validate(self) -> None:
        if self.vocab_size != 256:
            raise ValueError("The first baseline uses a 256-value byte vocabulary")
        if self.block_size < 2:
            raise ValueError("block_size must be at least 2")
        if self.n_layer < 1 or self.n_head < 1 or self.n_embd < 1:
            raise ValueError("layer, head, and embedding dimensions must be positive")
        if self.n_embd % self.n_head:
            raise ValueError("n_embd must be divisible by n_head")
        if not 0.0 <= self.dropout < 1.0:
            raise ValueError("dropout must be in [0, 1)")


class ByteTokenizer:
    """UTF-8 byte tokenizer: IDs are exactly the byte values 0..255."""

    vocab_size = 256

    def encode(self, text: str) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return list(text.encode("utf-8"))

    def decode(self, token_ids: list[int]) -> str:
        values = []
        for token_id in token_ids:
            if not isinstance(token_id, int) or not 0 <= token_id <= 255:
                raise ValueError("byte token IDs must be integers in [0, 255]")
            values.append(token_id)
        return bytes(values).decode("utf-8", errors="strict")


class CausalSelfAttention(nn.Module):
    def __init__(self, config: TinyGPTConfig) -> None:
        super().__init__()
        self.n_head = config.n_head
        self.head_dim = config.n_embd // config.n_head
        self.qkv = nn.Linear(config.n_embd, 3 * config.n_embd, bias=False)
        self.projection = nn.Linear(config.n_embd, config.n_embd, bias=False)
        self.dropout = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, sequence, width = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)

        def split_heads(value: torch.Tensor) -> torch.Tensor:
            return value.view(batch, sequence, self.n_head, self.head_dim).transpose(1, 2)

        q, k, v = split_heads(q), split_heads(k), split_heads(v)
        scores = (q @ k.transpose(-2, -1)) * (self.head_dim ** -0.5)
        future_mask = torch.triu(
            torch.ones(sequence, sequence, dtype=torch.bool, device=x.device),
            diagonal=1,
        )
        scores = scores.masked_fill(future_mask, torch.finfo(scores.dtype).min)
        weights = self.dropout(F.softmax(scores, dim=-1))
        attended = weights @ v
        attended = attended.transpose(1, 2).contiguous().view(batch, sequence, width)
        return self.dropout(self.projection(attended))


class TransformerBlock(nn.Module):
    def __init__(self, config: TinyGPTConfig) -> None:
        super().__init__()
        self.norm_attention = nn.LayerNorm(config.n_embd)
        self.attention = CausalSelfAttention(config)
        self.norm_mlp = nn.LayerNorm(config.n_embd)
        self.mlp = nn.Sequential(
            nn.Linear(config.n_embd, 4 * config.n_embd),
            nn.GELU(),
            nn.Linear(4 * config.n_embd, config.n_embd),
            nn.Dropout(config.dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attention(self.norm_attention(x))
        return x + self.mlp(self.norm_mlp(x))


class TinyGPT(nn.Module):
    """Decoder-only causal transformer with learned positional embeddings."""

    def __init__(self, config: TinyGPTConfig | None = None) -> None:
        super().__init__()
        self.config = config or TinyGPTConfig()
        self.config.validate()
        self.token_embedding = nn.Embedding(self.config.vocab_size, self.config.n_embd)
        self.position_embedding = nn.Embedding(self.config.block_size, self.config.n_embd)
        self.blocks = nn.ModuleList(
            TransformerBlock(self.config) for _ in range(self.config.n_layer)
        )
        self.final_norm = nn.LayerNorm(self.config.n_embd)
        self.lm_head = nn.Linear(self.config.n_embd, self.config.vocab_size, bias=False)
        self.lm_head.weight = self.token_embedding.weight

    def forward(
        self,
        input_ids: torch.Tensor,
        targets: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        if input_ids.ndim != 2:
            raise ValueError("input_ids must have shape [batch, sequence]")
        if input_ids.dtype != torch.long:
            raise ValueError("input_ids must use torch.long token IDs")
        batch, sequence = input_ids.shape
        if sequence < 1 or sequence > self.config.block_size:
            raise ValueError("sequence length is outside the configured context window")
        if targets is not None and targets.shape != input_ids.shape:
            raise ValueError("targets must have the same shape as input_ids")

        positions = torch.arange(sequence, device=input_ids.device)
        x = self.token_embedding(input_ids) + self.position_embedding(positions)[None, :, :]
        for block in self.blocks:
            x = block(x)
        logits = self.lm_head(self.final_norm(x))
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.reshape(batch * sequence, self.config.vocab_size),
                targets.reshape(batch * sequence),
            )
        return logits, loss


def make_synthetic_batch(
    batch_size: int = 2,
    block_size: int = 32,
    seed: int = 42,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Create deterministic random byte IDs for evaluation only."""
    if batch_size < 1 or block_size < 2:
        raise ValueError("batch_size must be positive and block_size at least 2")
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    tokens = torch.randint(
        low=0,
        high=256,
        size=(batch_size, block_size + 1),
        generator=generator,
        dtype=torch.long,
        device="cpu",
    )
    return tokens[:, :-1], tokens[:, 1:]


def _canonical_hash(payload: dict[str, Any]) -> str:
    # Wall-clock creation time is metadata, not part of deterministic identity.
    stable = {key: value for key, value in payload.items() if key != "created_at"}
    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_baseline(
    seed: int = 42,
    config: TinyGPTConfig | None = None,
    batch_size: int = 2,
) -> dict[str, Any]:
    """Measure a random-initialized baseline; never trains or writes weights."""
    config = config or TinyGPTConfig()
    config.validate()
    torch.manual_seed(seed)
    model = TinyGPT(config).to(device="cpu")
    model.eval()
    input_ids, targets = make_synthetic_batch(batch_size, config.block_size, seed)
    with torch.no_grad():
        logits, loss = model(input_ids, targets)
    payload: dict[str, Any] = {
        "schema": "dreamco.buddy.tiny_gpt_baseline.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model_id": "dreamco/buddy-tiny-gpt-baseline",
        "model_status": "UNTRAINED_RANDOM_INITIALIZATION",
        "model_lineage": {
            "parent_model_id": None,
            "dataset_card": "config/buddy-tiny-gpt-synthetic-data-card.json",
            "training_run_id": None,
        },
        "config": asdict(config),
        "seed": seed,
        "device": "cpu",
        "python_version": platform.python_version(),
        "torch_version": torch.__version__,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "evaluation": {
            "batch_size": batch_size,
            "sequence_length": config.block_size,
            "logits_shape": list(logits.shape),
            "initial_loss": float(loss.item()),
        },
        "data": {
            "dataset_id": "synthetic-byte-sequence-fixture",
            "generation": "seeded_pseudorandom_byte_ids",
            "external_data_used": False,
            "training_data_authorized": False,
            "purpose": "shape_and_initial_baseline_evaluation_only",
        },
        "training_performed": False,
        "weights_updated": False,
        "checkpoint_written": False,
        "network_accessed": False,
        "paid_compute_used": False,
        "promotion": "NOT_ELIGIBLE_NO_TRAINING_OR_HELDOUT_EVIDENCE",
    }
    payload["report_sha256"] = _canonical_hash(payload)
    return payload


def write_baseline_report(output_path: str | Path, **kwargs: Any) -> dict[str, Any]:
    """Write JSON evidence only; no model or optimizer state is serialized."""
    report = run_baseline(**kwargs)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
