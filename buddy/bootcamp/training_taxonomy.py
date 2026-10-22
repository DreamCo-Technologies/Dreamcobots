"""Searchable Buddy Bootcamp curriculum categories for AI training resources.

No external resource access, account connection, or training execution.
"""
from dataclasses import dataclass
from buddy.bootcamp.training_methods_hub import METHODS, PROVIDERS

CATEGORIES = {
    "foundations": ("prompting", "rag", "evaluation"),
    "tokenization_vocabulary": ("tokenizer_training", "continued_pretraining"),
    "model_weights": ("sft", "full_finetuning", "continued_pretraining"),
    "efficient_finetuning": ("lora", "qlora"),
    "preferences_reinforcement": ("dpo", "grpo", "reward_modeling"),
    "teacher_student": ("distillation",),
    "representations_search": ("embedding_training", "rag"),
    "testing_benchmarks": ("evaluation",),
}
PROVIDER_CATEGORIES = {
    "free_start": ("local_cpu", "colab", "kaggle", "hugging_face"),
    "open_source_frameworks": ("pytorch", "unsloth", "axolotl"),
    "local_hardware": ("local_cpu", "local_gpu"),
    "paid_gpu": ("runpod", "vast", "modal"),
    "managed_cloud": ("aws", "google_cloud", "azure"),
}
LEVELS = ("beginner", "intermediate", "advanced")
LESSON_STEPS = ("concept", "worked_example", "guided_practice", "sandbox_exercise",
                "independent_evaluation", "human_review")


@dataclass(frozen=True)
class BootcampQuery:
    text: str = ""
    category: str | None = None
    level: str = "beginner"
    free_only: bool = False


def search(query: BootcampQuery):
    if query.level not in LEVELS:
        raise ValueError("invalid learning level")
    if query.category and query.category not in CATEGORIES and query.category not in PROVIDER_CATEGORIES:
        raise ValueError("unknown category")
    needle = query.text.strip().lower()
    method_ids = set(CATEGORIES.get(query.category, METHODS))
    provider_ids = set(PROVIDER_CATEGORIES.get(query.category, PROVIDERS))
    methods = [{"id": key, "category": group, "mechanism": METHODS[key][0],
                "summary": METHODS[key][1], "level": query.level}
               for group, ids in CATEGORIES.items() for key in ids
               if key in method_ids and (not needle or needle in (key + " " + METHODS[key][1] + " " + group).lower())]
    providers = [{"id": key, "category": group, "cost_class": PROVIDERS[key][0],
                  "documentation": PROVIDERS[key][2], "live_access_verified": False}
                 for group, ids in PROVIDER_CATEGORIES.items() for key in ids
                 if key in provider_ids
                 and (not query.free_only or PROVIDERS[key][0].startswith(("free", "existing")))
                 and (not needle or needle in (key + " " + group + " " + PROVIDERS[key][0]).lower())]
    methods = list({m["id"]: m for m in methods}.values())
    providers = list({p["id"]: p for p in providers}.values())
    methods.sort(key=lambda x: x["id"])
    providers.sort(key=lambda x: x["id"])
    return {"schema": "dreamco.bootcamp.search.v1", "methods": methods,
            "providers": providers, "method_count": len(methods),
            "provider_count": len(providers), "training_started": False}


def lesson(method_id: str, level: str = "beginner"):
    if method_id not in METHODS or level not in LEVELS:
        raise ValueError("unsupported lesson")
    category = next(name for name, ids in CATEGORIES.items() if method_id in ids)
    return {"schema": "dreamco.bootcamp.lesson.v1", "method": method_id,
            "category": category, "level": level, "mechanism": METHODS[method_id][0],
            "learning_objective": METHODS[method_id][1], "steps": list(LESSON_STEPS),
            "assessment": {"requires_independent_evidence": True,
                           "passing_score": 0.8, "status": "not_attempted"},
            "training_executed": False}
