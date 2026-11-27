"""Exact parameter-count preflight for Buddy's CPU-first decoder architectures.

This module estimates architecture size only. It never imports PyTorch, allocates
model weights, reads training data, launches training, or authorizes compute.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DecoderArchitecture:
    vocab_size: int
    context_size: int
    width: int
    layers: int
    attention_heads: int
    feed_forward_size: int
    tied_embeddings: bool = True
    bias: bool = True


def count_decoder_parameters(config: DecoderArchitecture) -> int:
    """Count parameters for the matching TransformerEncoderLayer decoder.

    Assumes PyTorch-style MultiheadAttention (combined Q/K/V projection),
    two affine LayerNorms per encoder layer, one final affine LayerNorm,
    token and learned positional embeddings, and an optional tied output head.
    """
    values = asdict(config)
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0
           for key, value in values.items() if key not in {"tied_embeddings", "bias"}):
        raise ValueError("all architecture dimensions must be positive integers")
    if config.width % config.attention_heads:
        raise ValueError("width must be divisible by attention_heads")
    if not isinstance(config.tied_embeddings, bool) or not isinstance(config.bias, bool):
        raise ValueError("tied_embeddings and bias must be booleans")

    embeddings = config.vocab_size * config.width + config.context_size * config.width
    if not config.tied_embeddings:
        embeddings += config.vocab_size * config.width

    # MHA: 4*d^2 weights; FFN: 2*d*f weights.
    weights_per_layer = 4 * config.width**2 + 2 * config.width * config.feed_forward_size
    if config.bias:
        # MHA QKV/out, FFN in/out, and two affine LayerNorms.
        weights_per_layer += 5 * config.width + config.feed_forward_size + 4 * config.width
    final_norm = 2 * config.width
    return embeddings + config.layers * weights_per_layer + final_norm


def build_preflight(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate a profile and return a reproducible plan-only parameter report."""
    architecture = DecoderArchitecture(
        vocab_size=profile["vocab_size"],
        context_size=profile["context_size"],
        width=profile["width"],
        layers=profile["layers"],
        attention_heads=profile["attention_heads"],
        feed_forward_size=profile["feed_forward_size"],
        tied_embeddings=profile.get("tied_embeddings", True),
        bias=profile.get("bias", True),
    )
    actual = count_decoder_parameters(architecture)
    target = profile["parameter_target"]
    tolerance = profile.get("tolerance_fraction", 0.02)
    if not isinstance(target, int) or isinstance(target, bool) or target <= 0:
        raise ValueError("parameter_target must be a positive integer")
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or not 0 <= tolerance <= 0.25:
        raise ValueError("tolerance_fraction must be between 0 and 0.25")
    delta = abs(actual - target) / target
    return {
        "schema": "dreamco.model_architecture_preflight.v1",
        "profile_id": profile.get("profile_id", "unnamed"),
        "architecture": asdict(architecture),
        "parameter_target": target,
        "estimated_parameter_count": actual,
        "relative_target_error": round(delta, 8),
        "target_within_tolerance": delta <= tolerance,
        "tolerance_fraction": tolerance,
        "status": "architecture_size_pass" if delta <= tolerance else "architecture_size_mismatch",
        "training_started": False,
        "weights_created": False,
        "paid_compute_authorized": False,
        "truth_boundary": "A parameter-count preflight is not a trained model, checkpoint, benchmark result, or training authorization.",
    }
