"""Searchable, user-facing resource taxonomy for Buddy Bootcamp.

All 12 named resources are catalog entries, not verified account connections.
"""
from __future__ import annotations

from buddy.bootcamp.training_methods_hub import PROVIDERS

CATEGORIES = {
    "free_gpu_notebooks": {"title": "Free & Limited GPU Notebooks", "resources": ("colab", "kaggle"), "level": "beginner", "topics": ("python", "notebooks", "gpu", "experiments")},
    "model_dataset_hub": {"title": "Models, Datasets & Community", "resources": ("hugging_face",), "level": "beginner", "topics": ("models", "datasets", "tokenizers", "evaluation")},
    "fine_tuning_frameworks": {"title": "Efficient Fine-Tuning Frameworks", "resources": ("unsloth", "axolotl"), "level": "intermediate", "topics": ("lora", "qlora", "sft", "dpo", "training")},
    "deep_learning_frameworks": {"title": "Neural Network Development", "resources": ("pytorch",), "level": "intermediate", "topics": ("tensors", "autograd", "token_prediction", "weights")},
    "gpu_marketplaces": {"title": "Paid GPU Rental & Marketplaces", "resources": ("runpod", "vast"), "level": "intermediate", "topics": ("gpu", "pricing", "compute", "deployment")},
    "serverless_gpu": {"title": "Serverless GPU Workloads", "resources": ("modal",), "level": "intermediate", "topics": ("gpu", "serverless", "jobs")},
    "managed_cloud_ml": {"title": "Managed Cloud AI Training", "resources": ("aws", "google_cloud", "azure"), "level": "advanced", "topics": ("mlops", "training", "monitoring", "deployment")},
}
STUDY_PATHS = {
    "first_model_experiment": ("free_gpu_notebooks", "model_dataset_hub", "deep_learning_frameworks"),
    "fine_tune_open_model": ("model_dataset_hub", "fine_tuning_frameworks", "free_gpu_notebooks", "gpu_marketplaces"),
    "learn_token_prediction": ("deep_learning_frameworks", "model_dataset_hub", "free_gpu_notebooks"),
    "train_vocabulary": ("model_dataset_hub", "deep_learning_frameworks", "free_gpu_notebooks"),
    "scale_paid_training": ("gpu_marketplaces", "serverless_gpu", "managed_cloud_ml"),
    "enterprise_mlops": ("managed_cloud_ml", "model_dataset_hub", "deep_learning_frameworks"),
}

def validate_taxonomy():
    expected = set(PROVIDERS)
    found = [item for cat in CATEGORIES.values() for item in cat["resources"]]
    if set(found) != expected or len(found) != len(expected):
        raise ValueError("category coverage must be unique and complete")
    if any(category not in CATEGORIES for path in STUDY_PATHS.values() for category in path):
        raise ValueError("study path points to unknown category")
    return True

def search_resources(query="", *, category=None, cost=None, level=None):
    validate_taxonomy()
    if category is not None and category not in CATEGORIES:
        raise ValueError("unknown category")
    if cost not in (None, "free", "paid"):
        raise ValueError("cost must be free or paid")
    tokens = query.lower().strip().split()
    rows = []
    for key, group in CATEGORIES.items():
        if category is not None and category != key:
            continue
        if level is not None and level != group["level"]:
            continue
        for provider in group["resources"]:
            price, mode, docs = PROVIDERS[provider]
            if cost == "free" and not (price.startswith("free") or price.startswith("existing")):
                continue
            if cost == "paid" and not ("paid" in price or price == "existing_hardware"):
                continue
            searchable = " ".join((provider, key, group["title"], *group["topics"])).lower()
            if not all(token in searchable for token in tokens):
                continue
            rows.append({"id": provider, "category": key, "category_title": group["title"],
                         "level": group["level"], "topics": list(group["topics"]),
                         "cost_class": price, "kind": mode, "documentation": docs,
                         "account_connected": False, "availability_verified": False})
    return rows

def bootcamp_path(path_id):
    validate_taxonomy()
    if path_id not in STUDY_PATHS:
        raise ValueError("unknown study path")
    return {"schema": "dreamco.bootcamp.resource_path.v1", "id": path_id,
            "categories": [{"id": key, "title": CATEGORIES[key]["title"],
                            "resources": list(CATEGORIES[key]["resources"]),
                            "topics": list(CATEGORIES[key]["topics"])}
                           for key in STUDY_PATHS[path_id]],
            "steps": ["Learn the concepts", "Review provider documentation",
                      "Verify current account limits and licenses",
                      "Practice on authorized public or owned data",
                      "Compare cost and measured results",
                      "Complete a reproducible assessment"],
            "training_started": False, "requires_user_selection": True}
