"""Dependency-free, forward-only tiny GPT-style decoder used by Buddy Bootcamp.

This is an educational reference model, not a production model. Parameters are
initialized deterministically and are never updated by this module.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Sequence


@dataclass(frozen=True)
class TinyGPTConfig:
    vocab_size: int = 256
    context_size: int = 8
    width: int = 8
    seed: int = 20261121
    ffn_multiplier: int = 2

    def validate(self) -> None:
        if self.vocab_size != 256:
            raise ValueError("ByteTokenizer requires vocab_size=256")
        if self.context_size < 2:
            raise ValueError("context_size must be at least 2")
        if self.width < 2:
            raise ValueError("width must be at least 2")
        if self.ffn_multiplier < 1:
            raise ValueError("ffn_multiplier must be at least 1")


class ByteTokenizer:
    """UTF-8 byte tokenizer with a fixed 256-token vocabulary."""

    vocab_size = 256
    name = "utf8-byte-v1"

    def encode(self, text: str) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        return list(text.encode("utf-8"))

    def decode(self, token_ids: Sequence[int]) -> str:
        values = _validate_token_ids(token_ids, self.vocab_size)
        return bytes(values).decode("utf-8")

    def fingerprint(self) -> str:
        return hashlib.sha256(b"dreamco:utf8-byte-v1:vocab=256").hexdigest()


def _validate_token_ids(token_ids: Sequence[int], vocab_size: int) -> list[int]:
    values = list(token_ids)
    if any(type(value) is not int or value < 0 or value >= vocab_size for value in values):
        raise ValueError(f"token IDs must be integers in [0, {vocab_size - 1}]")
    return values


def _seeded_value(seed: int, tensor_name: str, index: int, scale: float) -> float:
    digest = hashlib.sha256(f"{seed}:{tensor_name}:{index}".encode("utf-8")).digest()
    unit = int.from_bytes(digest[:8], "big") / float((1 << 64) - 1)
    return (2.0 * unit - 1.0) * scale


def _matrix(seed: int, name: str, rows: int, columns: int, scale: float) -> list[list[float]]:
    return [
        [_seeded_value(seed, name, row * columns + column, scale) for column in range(columns)]
        for row in range(rows)
    ]


def _linear(vector: Sequence[float], matrix: Sequence[Sequence[float]]) -> list[float]:
    if not matrix or len(vector) != len(matrix):
        raise ValueError("linear input width does not match matrix rows")
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("linear matrix must be rectangular")
    return [sum(vector[row] * matrix[row][column] for row in range(len(vector))) for column in range(columns)]


def _softmax(values: Sequence[float]) -> list[float]:
    maximum = max(values)
    exponentials = [math.exp(value - maximum) for value in values]
    denominator = sum(exponentials)
    return [value / denominator for value in exponentials]


def _layer_norm(values: Sequence[float]) -> list[float]:
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    scale = math.sqrt(variance + 1e-5)
    return [(value - mean) / scale for value in values]


class TinyGPT:
    """One-block causal self-attention decoder with a byte-level language head."""

    def __init__(self, config: TinyGPTConfig | None = None):
        self.config = config or TinyGPTConfig()
        self.config.validate()
        cfg = self.config
        hidden = cfg.width * cfg.ffn_multiplier
        self.token_embeddings = _matrix(cfg.seed, "token_embeddings", cfg.vocab_size, cfg.width, 0.04)
        self.position_embeddings = _matrix(cfg.seed, "position_embeddings", cfg.context_size, cfg.width, 0.04)
        self.wq = _matrix(cfg.seed, "wq", cfg.width, cfg.width, 0.08)
        self.wk = _matrix(cfg.seed, "wk", cfg.width, cfg.width, 0.08)
        self.wv = _matrix(cfg.seed, "wv", cfg.width, cfg.width, 0.08)
        self.wo = _matrix(cfg.seed, "wo", cfg.width, cfg.width, 0.08)
        self.w1 = _matrix(cfg.seed, "w1", cfg.width, hidden, 0.08)
        self.b1 = [0.0] * hidden
        self.w2 = _matrix(cfg.seed, "w2", hidden, cfg.width, 0.08)
        self.b2 = [0.0] * cfg.width
        self.lm_head = _matrix(cfg.seed, "lm_head", cfg.width, cfg.vocab_size, 0.08)
        self.lm_bias = [0.0] * cfg.vocab_size

    @property
    def parameter_count(self) -> int:
        matrices = (
            self.token_embeddings, self.position_embeddings, self.wq, self.wk,
            self.wv, self.wo, self.w1, self.w2, self.lm_head,
        )
        return sum(len(row) for matrix in matrices for row in matrix) + len(self.b1) + len(self.b2) + len(self.lm_bias)

    def fingerprint(self) -> str:
        payload = {
            "config": asdict(self.config),
            "token_embeddings": self.token_embeddings,
            "position_embeddings": self.position_embeddings,
            "wq": self.wq, "wk": self.wk, "wv": self.wv, "wo": self.wo,
            "w1": self.w1, "b1": self.b1, "w2": self.w2, "b2": self.b2,
            "lm_head": self.lm_head, "lm_bias": self.lm_bias,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def forward(self, input_ids: Sequence[int]) -> list[list[float]]:
        tokens = _validate_token_ids(input_ids, self.config.vocab_size)
        if not tokens:
            raise ValueError("input_ids must contain at least one token")
        if len(tokens) > self.config.context_size:
            raise ValueError("input sequence exceeds configured context_size")

        cfg = self.config
        embedded = [
            [self.token_embeddings[token][dim] + self.position_embeddings[position][dim] for dim in range(cfg.width)]
            for position, token in enumerate(tokens)
        ]
        queries = [_linear(row, self.wq) for row in embedded]
        keys = [_linear(row, self.wk) for row in embedded]
        values = [_linear(row, self.wv) for row in embedded]
        scale = math.sqrt(cfg.width)
        outputs: list[list[float]] = []

        for position, residual in enumerate(embedded):
            # The prefix is the only visible key/value range: future tokens cannot leak.
            scores = [
                sum(queries[position][dim] * keys[past][dim] for dim in range(cfg.width)) / scale
                for past in range(position + 1)
            ]
            attention = _softmax(scores)
            context = [
                sum(attention[past] * values[past][dim] for past in range(position + 1))
                for dim in range(cfg.width)
            ]
            attended = _linear(context, self.wo)
            hidden = _layer_norm([residual[dim] + attended[dim] for dim in range(cfg.width)])
            expanded = _linear(hidden, self.w1)
            activated = [max(0.0, expanded[index] + self.b1[index]) for index in range(len(self.b1))]
            projected = _linear(activated, self.w2)
            hidden = _layer_norm([hidden[dim] + projected[dim] + self.b2[dim] for dim in range(cfg.width)])
            logits = _linear(hidden, self.lm_head)
            outputs.append([logits[index] + self.lm_bias[index] for index in range(cfg.vocab_size)])
        return outputs


def sequence_cross_entropy(model: TinyGPT, token_ids: Sequence[int]) -> float:
    """Measure next-byte cross entropy without changing model parameters."""
    tokens = _validate_token_ids(token_ids, model.config.vocab_size)
    if len(tokens) < 2:
        raise ValueError("at least two tokens are required to score next-token loss")
    logits = model.forward(tokens[:-1])
    losses = []
    for row, target in zip(logits, tokens[1:]):
        maximum = max(row)
        log_partition = maximum + math.log(sum(math.exp(value - maximum) for value in row))
        losses.append(log_partition - row[target])
    return sum(losses) / len(losses)
