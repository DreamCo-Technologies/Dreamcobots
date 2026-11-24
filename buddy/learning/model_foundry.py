"""Rights-gated, reproducible CPU language-model training for DreamCo.

The trainer initializes weights randomly. It never downloads datasets or models.
Only manifest-approved local files with verified SHA-256 hashes are eligible.
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any

SCHEMA = "dreamco.authorized_training_datasets.v1"
DIVISION_COUNT = 65
DEFAULT_CONFIG = {
    "family": "decoder_only_transformer",
    "vocabulary": "byte_level_256_plus_special",
    "sequence_length": 64,
    "hidden_size": 128,
    "layers": 2,
    "attention_heads": 4,
    "feed_forward_size": 512,
    "weight_initialization": "random",
    "objective": "next_token_cross_entropy",
}
STRATEGIES = (
    "domain_adaptive_pretraining",
    "code_and_tool_sequence_modeling",
    "instruction_response_modeling",
    "classification_and_extraction",
    "retrieval_and_grounded_generation",
    "time_series_and_forecasting",
    "multimodal_representation_research",
    "simulation_and_planning",
    "safety_and_policy_modeling",
    "scientific_reasoning",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(manifest: dict[str, Any], data_root: Path) -> list[dict[str, Any]]:
    if manifest.get("schema") != SCHEMA:
        raise ValueError(f"manifest schema must be {SCHEMA}")
    entries = manifest.get("datasets")
    if not isinstance(entries, list):
        raise ValueError("datasets must be a list")
    approved: list[dict[str, Any]] = []
    seen: set[str] = set()
    root = data_root.resolve()
    for item in entries:
        dataset_id = str(item.get("dataset_id", "")).strip()
        if not dataset_id or dataset_id in seen:
            raise ValueError("dataset_id values must be non-empty and unique")
        seen.add(dataset_id)
        permissions = item.get("permissions") or {}
        required = (
            item.get("rights_status") == "APPROVED",
            bool(item.get("owner") and item.get("owner_attestation_ref")),
            bool(item.get("license_id") and item.get("license_evidence_ref")),
            permissions.get("training") is True,
            permissions.get("commercial_model_use") is True,
            permissions.get("derivative_models") is True,
            bool(item.get("approved_division_ids")),
        )
        if not all(required):
            continue
        relative = Path(str(item.get("local_path", "")))
        candidate = (root / relative).resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"{dataset_id}: local_path escapes data root")
        if not candidate.is_file():
            continue
        expected = str(item.get("sha256", "")).lower()
        if len(expected) != 64 or sha256_file(candidate) != expected:
            raise ValueError(f"{dataset_id}: missing or mismatched SHA-256")
        divisions = item["approved_division_ids"]
        if not isinstance(divisions, list) or any(
            not isinstance(value, int) or value < 1 or value > DIVISION_COUNT
            for value in divisions
        ):
            raise ValueError(f"{dataset_id}: invalid approved_division_ids")
        approved.append({**item, "_resolved_path": str(candidate)})
    return approved


def build_parallel_plan(registry: dict[str, Any], approved: list[dict[str, Any]]) -> dict[str, Any]:
    divisions = registry.get("divisions", [])
    ids = [row.get("id") for row in divisions]
    if len(divisions) != DIVISION_COUNT or sorted(ids) != list(range(1, DIVISION_COUNT + 1)):
        raise ValueError("canonical registry must contain unique division IDs 1 through 65")
    include = []
    blocked = []
    for division in sorted(divisions, key=lambda row: row["id"]):
        division_id = division["id"]
        candidates = [
            dataset for dataset in approved
            if division_id in dataset.get("approved_division_ids", [])
        ]
        if not candidates:
            blocked.append({"division_id": division_id, "division_name": division["name"],
                            "status": "blocked_no_authorized_dataset"})
            continue
        dataset = candidates[0]
        include.append({
            "division_id": division_id,
            "division_name": division["name"],
            "dataset_id": dataset["dataset_id"],
            "dataset_path": dataset["_resolved_path"],
            "dataset_sha256": dataset["sha256"],
            "strategy": STRATEGIES[(division_id - 1) % len(STRATEGIES)],
            "seed": 20261124 + division_id,
        })
    return {
        "schema": "dreamco.parallel_division_training_plan.v1",
        "division_count": DIVISION_COUNT,
        "eligible_divisions": len(include),
        "blocked_divisions": len(blocked),
        "max_parallel_recommended": 4,
        "include": include,
        "blocked": blocked,
        "truth_boundary": "A queued job is not a trained model; only checkpoint and evaluation evidence proves training.",
    }


def train_from_scratch(dataset_path: Path, output_path: Path, *, dataset_id: str,
                       division_id: int, strategy: str, seed: int, steps: int = 100) -> dict[str, Any]:
    """Train a small byte-level decoder-only model using PyTorch and local approved text."""
    try:
        import torch
        from torch import nn
    except ImportError as exc:
        raise RuntimeError("PyTorch is required; install the optional training dependencies") from exc

    raw = dataset_path.read_bytes()
    if len(raw) < 1024:
        raise ValueError("authorized dataset must contain at least 1024 bytes for isolated splits")
    if steps < 1 or steps > 10000:
        raise ValueError("steps must be between 1 and 10000")
    random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device("cpu")
    data = torch.tensor(list(raw), dtype=torch.long, device=device)
    train_end = int(len(data) * 0.8)
    validation_end = int(len(data) * 0.9)
    train_data = data[:train_end]
    val_data = data[train_end:validation_end]
    holdout_data = data[validation_end:]
    if min(len(train_data), len(val_data), len(holdout_data)) < 65:
        raise ValueError("dataset is too small for independent train/validation/holdout splits")

    class TinyDecoder(nn.Module):
        def __init__(self):
            super().__init__()
            self.token = nn.Embedding(256, 128)
            self.position = nn.Embedding(64, 128)
            layer = nn.TransformerEncoderLayer(
                d_model=128, nhead=4, dim_feedforward=512, batch_first=True,
                norm_first=True, activation="gelu"
            )
            self.blocks = nn.TransformerEncoder(layer, num_layers=2)
            self.norm = nn.LayerNorm(128)
            self.head = nn.Linear(128, 256, bias=False)
            self.head.weight = self.token.weight

        def forward(self, x):
            length = x.size(1)
            positions = torch.arange(length, device=x.device)
            hidden = self.token(x) + self.position(positions)
            mask = torch.triu(torch.ones(length, length, device=x.device), diagonal=1).bool()
            hidden = self.blocks(hidden, mask=mask)
            return self.head(self.norm(hidden))

    model = TinyDecoder().to(device)  # fresh random initialization; no imported base weights
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    generator = torch.Generator(device="cpu").manual_seed(seed)

    def batch(source):
        starts = torch.randint(0, max(1, len(source) - 65), (8,), generator=generator)
        x = torch.stack([source[int(i):int(i) + 64] for i in starts])
        y = torch.stack([source[int(i) + 1:int(i) + 65] for i in starts])
        return x, y

    model.train()
    for _ in range(steps):
        x, y = batch(train_data)
        logits = model(x)
        loss = nn.functional.cross_entropy(logits.reshape(-1, 256), y.reshape(-1))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

    model.eval()
    with torch.no_grad():
        x, y = batch(val_data)
        validation_loss = float(nn.functional.cross_entropy(
            model(x).reshape(-1, 256), y.reshape(-1)
        ).item())
        x, y = batch(holdout_data)
        holdout_loss = float(nn.functional.cross_entropy(
            model(x).reshape(-1, 256), y.reshape(-1)
        ).item())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "schema": "dreamco.model_checkpoint.v1",
        "model_id": f"buddy-division-{division_id:02d}-scratch",
        "division_id": division_id,
        "dataset_id": dataset_id,
        "training_strategy": strategy,
        "dataset_sha256": sha256_file(dataset_path),
        "architecture": DEFAULT_CONFIG,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "initialization": "random",
        "optimizer": "AdamW",
        "learning_rate": 3e-4,
        "seed": seed,
        "steps": steps,
        "train_bytes": len(train_data),
        "validation_bytes": len(val_data),
        "holdout_bytes": len(holdout_data),
        "holdout_used_for_training": False,
        "validation_loss": validation_loss,
        "holdout_loss": holdout_loss,
        "training_status": "trained_experimental_checkpoint_not_certified",
        "weights_sha256": None,
    }
    torch.save({"model_state_dict": model.state_dict(), "metadata": metadata}, output_path)
    metadata["weights_sha256"] = sha256_file(output_path)
    metadata_path = output_path.with_suffix(output_path.suffix + ".json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata
