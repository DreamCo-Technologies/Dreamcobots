"""Conservative training readiness gate; no paid compute or training launched."""
import re


def evaluate_training(spec):
    required = (
        "dataset_id", "dataset_sha256", "license", "model_id", "model_revision",
        "train_split_sha256", "holdout_split_sha256", "compute_profile", "max_cost_usd",
    )
    missing = [key for key in required if spec.get(key) is None or spec.get(key) == ""]
    for key in ("dataset_sha256", "train_split_sha256", "holdout_split_sha256"):
        value = spec.get(key)
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
            missing.append(f"valid_{key}")
    if spec.get("train_split_sha256") == spec.get("holdout_split_sha256"):
        missing.append("independent_holdout_split")
    if spec.get("max_cost_usd") != 0:
        missing.append("zero_cost_budget")
    if spec.get("compute_profile") not in {"local_cpu", "local_mps", "local_cpu_or_mps"}:
        missing.append("approved_local_compute_profile")
    if spec.get("owner_approved") is not True:
        missing.append("owner_approval")
    if spec.get("dataset_authorized") is not True:
        missing.append("dataset_authorization")
    if spec.get("training_execution_approved") is not True:
        missing.append("explicit_training_execution_approval")
    revision = str(spec.get("model_revision", "")).strip().lower()
    if revision in {"latest", "main", "master", "head", "default"}:
        missing.append("pinned_model_revision")
    return {
        "ready_for_review": not missing,
        "missing": sorted(set(missing)),
        "training_started": False,
        "compute_allocated": False,
        "paid_compute_allowed": False,
        "note": "Approval and valid specs do not execute training; the isolated trainer must revalidate data hashes and the zero-cost local compute profile.",
    }
