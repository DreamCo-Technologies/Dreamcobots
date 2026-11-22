"""Small, deterministic GPT-style reference baseline for Buddy Bootcamp."""
from .tiny_gpt import ByteTokenizer, TinyGPT, TinyGPTConfig, sequence_cross_entropy
from .data_pipeline import DataPreparationError, prepare_synthetic_splits

__all__ = [
    "ByteTokenizer",
    "TinyGPT",
    "TinyGPTConfig",
    "sequence_cross_entropy",
    "DataPreparationError",
    "prepare_synthetic_splits",
]
