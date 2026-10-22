"""Provider-specific official learning library for Buddy Bootcamp.

Links are curated entry points, not copied site catalogs. Validate freshness
and terms before presenting as current. No scraping, credentials or training.
"""
from __future__ import annotations
from urllib.parse import urlparse

LIBRARIES = {
 "colab": ("Google Colab", "notebooks", [
  ("Overview and examples", "https://colab.research.google.com/notebooks/intro.ipynb", "beginner", ("notebooks","python")),
  ("Frequently asked questions", "https://research.google.com/colaboratory/faq.html", "beginner", ("gpu","limits"))]),
 "kaggle": ("Kaggle", "notebooks", [
  ("Learn course catalog", "https://www.kaggle.com/learn", "beginner", ("python","machine-learning")),
  ("Notebook documentation", "https://www.kaggle.com/docs/notebooks", "beginner", ("notebooks","gpu"))]),
 "hugging_face": ("Hugging Face", "model_dataset_hub", [
  ("Course catalog", "https://huggingface.co/learn", "beginner", ("transformers","llm","tokenizers")),
  ("Model catalog", "https://huggingface.co/models", "intermediate", ("models","licenses")),
  ("Dataset catalog", "https://huggingface.co/datasets", "intermediate", ("datasets","training")),
  ("Documentation catalog", "https://huggingface.co/docs", "intermediate", ("tokenizers","datasets","evaluation"))]),
 "unsloth": ("Unsloth", "fine_tuning", [
  ("Documentation", "https://docs.unsloth.ai/", "intermediate", ("lora","qlora","finetuning")),
  ("Getting started", "https://unsloth.ai/docs/get-started/fine-tuning-llms-guide", "intermediate", ("sft","llm"))]),
 "axolotl": ("Axolotl", "fine_tuning", [
  ("Documentation and examples", "https://docs.axolotl.ai/", "intermediate", ("lora","sft","configuration"))]),
 "pytorch": ("PyTorch", "deep_learning", [
  ("Tutorial catalog", "https://docs.pytorch.org/tutorials/", "beginner", ("tensors","autograd","neural-networks")),
  ("Beginner fundamentals", "https://docs.pytorch.org/tutorials/beginner/basics/", "beginner", ("optimization","dataloaders")),
  ("Specialized domains", "https://docs.pytorch.org/tutorials/domains.html", "advanced", ("vision","reinforcement-learning"))]),
 "runpod": ("RunPod", "gpu_compute", [
  ("Documentation", "https://docs.runpod.io/", "intermediate", ("gpu","pods","serverless"))]),
 "vast": ("Vast.ai", "gpu_compute", [
  ("Documentation", "https://docs.vast.ai/", "intermediate", ("gpu","rental","instances"))]),
 "modal": ("Modal", "serverless", [
  ("Documentation and examples", "https://modal.com/docs", "intermediate", ("serverless","gpu","examples")),
  ("Example gallery", "https://modal.com/docs/examples", "intermediate", ("llm","inference","jobs"))]),
 "aws": ("Amazon SageMaker", "managed_ml", [
  ("SageMaker documentation", "https://docs.aws.amazon.com/sagemaker/", "advanced", ("training","mlops","deployment")),
  ("SageMaker learning resources", "https://aws.amazon.com/sagemaker/getting-started/", "intermediate", ("tutorials","training"))]),
 "google_cloud": ("Google Vertex AI", "managed_ml", [
  ("Vertex AI documentation", "https://cloud.google.com/vertex-ai/docs", "advanced", ("training","mlops","pipelines")),
  ("Vertex AI samples", "https://cloud.google.com/vertex-ai/docs/samples", "intermediate", ("examples","notebooks"))]),
 "azure": ("Azure Machine Learning", "managed_ml", [
  ("Azure ML documentation", "https://learn.microsoft.com/en-us/azure/machine-learning/", "intermediate", ("training","deployment","pipelines")),
  ("Microsoft Learn catalog", "https://learn.microsoft.com/en-us/training/browse/?products=azure-machine-learning", "beginner", ("courses","mlops")),
  ("Machine learning learning path", "https://learn.microsoft.com/en-us/training/paths/create-machine-learn-models/", "intermediate", ("machine-learning","evaluation"))]),
}

def catalog():
    return [{"provider_id": pid, "provider": name, "category": category,
             "resources": [{"title": title, "url": url, "level": level, "topics": list(topics),
                            "kind": "official_learning_entry", "verified_live": False}
                           for title, url, level, topics in entries]}
            for pid, (name, category, entries) in LIBRARIES.items()]

def search(query="", *, provider=None, category=None, level=None, topic=None):
    if provider is not None and provider not in LIBRARIES:
        raise ValueError("unknown provider")
    tokens = query.lower().split()
    results = []
    for item in catalog():
        if provider and item["provider_id"] != provider:
            continue
        if category and item["category"] != category:
            continue
        for resource in item["resources"]:
            if level and resource["level"] != level:
                continue
            if topic and topic.lower() not in resource["topics"]:
                continue
            haystack = " ".join((item["provider"], item["category"], resource["title"],
                                 *resource["topics"])).lower()
            if all(token in haystack for token in tokens):
                results.append({"provider_id": item["provider_id"], **resource})
    return results

def validate():
    from buddy.bootcamp.training_methods_hub import PROVIDERS
    if set(LIBRARIES) != set(PROVIDERS):
        raise ValueError("libraries must cover all providers exactly")
    for item in catalog():
        if not item["resources"]:
            raise ValueError("empty provider library")
        for resource in item["resources"]:
            url = urlparse(resource["url"])
            if url.scheme != "https" or not url.hostname:
                raise ValueError("invalid official learning URL")
    return True
