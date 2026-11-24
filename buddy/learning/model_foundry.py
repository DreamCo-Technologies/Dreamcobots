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
    "vocabulary": "byte_level_256",
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
    "simulation_and_planning",
    "safety_and_policy_modeling",
    "scientific_reasoning",
)

STRATEGY_PROFILES = {
    "domain_adaptive_pretraining": {"sequence_length": 64, "batch_size": 8, "learning_rate": 3e-4},
    "code_and_tool_sequence_modeling": {"sequence_length": 64, "batch_size": 4, "learning_rate": 2e-4},
    "instruction_response_modeling": {"sequence_length": 64, "batch_size": 8, "learning_rate": 2e-4},
    "classification_and_extraction": {"sequence_length": 32, "batch_size": 8, "learning_rate": 1.5e-4},
    "retrieval_and_grounded_generation": {"sequence_length": 64, "batch_size": 4, "learning_rate": 2e-4},
    "time_series_and_forecasting": {"sequence_length": 32, "batch_size": 8, "learning_rate": 1e-4},
    "simulation_and_planning": {"sequence_length": 64, "batch_size": 4, "learning_rate": 2e-4},
    "safety_and_policy_modeling": {"sequence_length": 64, "batch_size": 8, "learning_rate": 1e-4},
    "scientific_reasoning": {"sequence_length": 64, "batch_size": 4, "learning_rate": 1.5e-4},
}


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
            item.get("training_strategy") in STRATEGY_PROFILES,
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
            "strategy": dataset["training_strategy"],
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
                       division_id: int, strategy: str, seed: int, steps: int = 100,
                       resume_from: Path | None = None) -> dict[str, Any]:
    """Train a small byte-level decoder-only model using PyTorch and local approved text."""
    if strategy not in STRATEGY_PROFILES:
        raise ValueError(f"unsupported training strategy: {strategy}")
    profile = STRATEGY_PROFILES[strategy]
    sequence_length = profile["sequence_length"]
    batch_size = profile["batch_size"]
    learning_rate = profile["learning_rate"]
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
            self.position = nn.Embedding(sequence_length, 128)
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
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    resumed_steps = 0
    if resume_from is not None:
        saved = torch.load(resume_from, map_location=device)
        saved_meta = saved.get("metadata", {})
        if (saved_meta.get("dataset_id") != dataset_id or saved_meta.get("division_id") != division_id
                or saved_meta.get("dataset_sha256") != sha256_file(dataset_path)
                or saved_meta.get("training_strategy") != strategy):
            raise ValueError("resume checkpoint provenance does not match this training run")
        model.load_state_dict(saved["model_state_dict"])
        if "optimizer_state_dict" in saved:
            optimizer.load_state_dict(saved["optimizer_state_dict"])
        resumed_steps = int(saved_meta.get("total_steps", saved_meta.get("steps", 0)))
    torch.manual_seed(seed + resumed_steps)
    generator = torch.Generator(device="cpu").manual_seed(seed + resumed_steps)

    def batch(source):
        starts = torch.randint(0, max(1, len(source) - sequence_length - 1), (batch_size,), generator=generator)
        x = torch.stack([source[int(i):int(i) + sequence_length] for i in starts])
        y = torch.stack([source[int(i) + 1:int(i) + sequence_length + 1] for i in starts])
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
        "architecture": {**DEFAULT_CONFIG, "sequence_length": sequence_length},
        "tokenizer": {"type": "byte_level", "vocabulary_size": 256, "special_tokens": []},
        "tokenizer_sha256": None,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "initialization": "random",
        "optimizer": "AdamW",
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "training_profile": profile,
        "seed": seed,
        "steps": steps,
        "resumed_from_steps": resumed_steps,
        "total_steps": resumed_steps + steps,
        "train_bytes": len(train_data),
        "validation_bytes": len(val_data),
        "holdout_bytes": len(holdout_data),
        "holdout_used_for_training": False,
        "validation_loss": validation_loss,
        "holdout_loss": holdout_loss,
        "train_split_sha256": hashlib.sha256(bytes(train_data.tolist())).hexdigest(),
        "validation_split_sha256": hashlib.sha256(bytes(val_data.tolist())).hexdigest(),
        "holdout_split_sha256": hashlib.sha256(bytes(holdout_data.tolist())).hexdigest(),
        "training_code_revision": __import__("os").environ.get("GITHUB_SHA"),
        "torch_version": torch.__version__,
        "training_status": "trained_experimental_checkpoint_not_certified",
        "weights_sha256": None,
    }
    tokenizer_bytes = json.dumps(metadata["tokenizer"], sort_keys=True, separators=(",", ":")).encode("utf-8")
    tokenizer_path = output_path.with_suffix(output_path.suffix + ".tokenizer.json")
    tokenizer_path.write_bytes(tokenizer_bytes)
    metadata["tokenizer_sha256"] = hashlib.sha256(tokenizer_bytes).hexdigest()
    torch.save({"model_state_dict": model.state_dict(), "optimizer_state_dict": optimizer.state_dict(), "metadata": metadata}, output_path)
    metadata["weights_sha256"] = sha256_file(output_path)
    metadata_path = output_path.with_suffix(output_path.suffix + ".json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata
