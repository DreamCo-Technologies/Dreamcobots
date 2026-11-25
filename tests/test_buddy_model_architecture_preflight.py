import json
from pathlib import Path

import pytest

from buddy.learning.model_architecture_preflight import (
    DecoderArchitecture,
    build_preflight,
    count_decoder_parameters,
)

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config/buddy-25m-cpu-architecture-profile.json"


def test_25m_profile_is_within_two_percent_without_starting_training():
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    report = build_preflight(profile)
    assert report["estimated_parameter_count"] == 24_943_360
    assert report["target_within_tolerance"] is True
    assert report["training_started"] is False
    assert report["weights_created"] is False
    assert report["paid_compute_authorized"] is False


def test_parameter_count_changes_when_output_embeddings_are_not_tied():
    tied = DecoderArchitecture(256, 256, 640, 5, 10, 2560, True, True)
    untied = DecoderArchitecture(256, 256, 640, 5, 10, 2560, False, True)
    assert count_decoder_parameters(untied) - count_decoder_parameters(tied) == 256 * 640


def test_invalid_attention_geometry_is_rejected():
    with pytest.raises(ValueError, match="divisible"):
        count_decoder_parameters(DecoderArchitecture(256, 128, 640, 5, 7, 2560))


def test_out_of_tolerance_profile_is_reported_not_silently_accepted():
    profile = {
        "profile_id": "too-small",
        "parameter_target": 25_000_000,
        "tolerance_fraction": 0.02,
        "vocab_size": 256,
        "context_size": 64,
        "width": 128,
        "layers": 2,
        "attention_heads": 4,
        "feed_forward_size": 512,
    }
    report = build_preflight(profile)
    assert report["status"] == "architecture_size_mismatch"
    assert report["target_within_tolerance"] is False
