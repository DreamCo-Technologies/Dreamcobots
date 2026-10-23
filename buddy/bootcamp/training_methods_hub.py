"""Read-only AI training method and compute catalog for Buddy.

Entries are discovery hints, not claims of live accounts, free GPU entitlement,
license approval, installed software, or successful training.
"""
from dataclasses import dataclass

METHODS = {
    "rag": ("retrieval", "index authorized documents; no weight updates"),
    "prompting": ("inference", "instructions and examples; no weight updates"),
    "sft": ("weights", "supervised fine-tuning on licensed examples"),
    "lora": ("adapter_weights", "parameter-efficient fine-tuning"),
    "qlora": ("adapter_weights", "quantized parameter-efficient fine-tuning"),
    "dpo": ("weights", "preference optimization using paired examples"),
    "grpo": ("weights", "reinforcement optimization with verifiable rewards"),
    "distillation": ("weights", "student training on permitted teacher outputs"),
    "continued_pretraining": ("weights", "next-token prediction on licensed corpus"),
    "tokenizer_training": ("tokenizer", "vocabulary and subword segmentation training"),
    "embedding_training": ("weights", "representation and retrieval training"),
    "reward_modeling": ("weights", "learn preference or process reward signals"),
    "full_finetuning": ("weights", "update all supported model parameters"),
    "evaluation": ("none", "measure without training"),
}
PROVIDERS = {
    "local_cpu": ("free_existing_hardware", "local", None),
    "local_gpu": ("existing_hardware", "local", None),
    "colab": ("free_limited_or_paid", "hosted", "https://research.google.com/colaboratory/faq.html"),
    "kaggle": ("free_limited", "hosted", "https://www.kaggle.com/docs/notebooks"),
    "hugging_face": ("free_tools_or_paid_compute", "hosted", "https://huggingface.co/docs"),
    "unsloth": ("free_software_compute_separate", "framework", "https://unsloth.ai/docs"),
    "axolotl": ("free_software_compute_separate", "framework", "https://docs.axolotl.ai/"),
    "pytorch": ("free_software_compute_separate", "framework", "https://pytorch.org/"),
    "runpod": ("paid_variable", "hosted", "https://www.runpod.io/"),
    "vast": ("paid_variable", "hosted", "https://vast.ai/"),
    "modal": ("paid_variable", "hosted", "https://modal.com/"),
    "aws": ("paid_variable", "hosted", "https://aws.amazon.com/sagemaker/"),
    "google_cloud": ("paid_variable", "hosted", "https://cloud.google.com/vertex-ai"),
    "azure": ("paid_variable", "hosted", "https://azure.microsoft.com/en-us/products/machine-learning"),
}

@dataclass(frozen=True)
class TrainingRequest:
    method: str
    budget_usd: float
    rights_verified: bool
    owner_approved: bool
    model_license_verified: bool = False

def propose(request: TrainingRequest):
    if request.method not in METHODS:
        raise ValueError("unknown training method")
    if isinstance(request.budget_usd, bool) or not isinstance(request.budget_usd, (int, float)) or not 0 <= request.budget_usd < float("inf"):
        raise ValueError("invalid budget")
    kind, description = METHODS[request.method]
    requires_rights = kind in {"weights", "adapter_weights", "tokenizer"}
    permitted = (not requires_rights or
                 (request.rights_verified and request.model_license_verified and request.owner_approved))
    options = [{"id": name, "cost_class": cost, "kind": mode, "documentation": url,
                "availability_verified": False, "price_verified": False}
               for name, (cost, mode, url) in PROVIDERS.items()
               if request.budget_usd > 0 or cost.startswith("free") or cost.startswith("existing")]
    return {"method": request.method, "mechanism": kind, "description": description,
            "eligible_for_review": permitted, "providers": options,
            "training_started": False, "approval_required": True,
            "next_step": "Verify hardware, pricing, provider terms, dataset rights, model license, and independent benchmarks"}
