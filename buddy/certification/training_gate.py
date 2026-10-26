"""Conservative training readiness gate; no paid compute or training launched."""
def evaluate_training(spec):
    required = ("dataset_id", "dataset_sha256", "license", "model_id", "model_revision",
                "train_split_sha256", "holdout_split_sha256", "compute_profile", "max_cost_usd")
    missing = [k for k in required if not spec.get(k) and spec.get(k) != 0]
    if spec.get("train_split_sha256") == spec.get("holdout_split_sha256"):
        missing.append("independent_holdout_split")
    if spec.get("max_cost_usd", 0) < 0:
        missing.append("valid_budget")
    if spec.get("owner_approved") is not True:
        missing.append("owner_approval")
    if spec.get("dataset_authorized") is not True:
        missing.append("dataset_authorization")
    return {"ready_for_review": not missing, "missing": missing,
            "training_started": False, "compute_allocated": False,
            "note": "Approval and valid specs alone do not execute training; isolated trainer and resource quota enforcement still required."}
