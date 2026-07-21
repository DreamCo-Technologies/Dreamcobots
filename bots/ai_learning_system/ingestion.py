"""
Data ingestion layer for the DreamCo Global AI Learning System.

Supports scraping and normalizing records from arXiv, GitHub, Kaggle, and AI Labs.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import datetime
import uuid

from .tiers import Tier, TierConfig, get_tier_config, FEATURE_SCRAPER
from framework import GlobalAISourcesFlow  # noqa: F401


class DataSourceType(Enum):
    ARXIV = "arxiv"
    GITHUB = "github"
    KAGGLE = "kaggle"
    AI_LAB = "ai_lab"


class ContentType(Enum):
    RESEARCH_PAPER = "research_paper"
    DATASET = "dataset"
    CODE_REPOSITORY = "code_repository"
    MODEL = "model"


@dataclass
class IngestedRecord:
    """A single normalised record retrieved from an external source.

    Attributes
    ----------
    id : str
        Unique record identifier (UUID4).
    source : DataSourceType
        Where the record was scraped from.
    content_type : ContentType
        Classification of the content.
    title : str
        Title of the paper/repo/dataset.
    url : str
        Canonical URL.
    tags : List[str]
        Normalised keyword tags.
    language : str
        Primary programming or spoken language.
    novelty_score : float
        Estimated novelty on a 0.0–1.0 scale.
    ingested_at : datetime.datetime
        UTC timestamp of ingestion.
    metadata : dict
        Source-specific extra fields.
    """

    id: str
    source: DataSourceType
    content_type: ContentType
    title: str
    url: str
    tags: List[str]
    language: str
    novelty_score: float
    ingested_at: datetime.datetime
    metadata: dict = field(default_factory=dict)


class IngestionTierError(Exception):
    """Raised when the current tier does not support the requested feature."""


class IngestionLimitError(Exception):
    """Raised when the monthly ingestion job quota has been exhausted."""


# ---------------------------------------------------------------------------
# Mock data templates used to generate realistic records
# ---------------------------------------------------------------------------

_MOCK_TEMPLATES = {
    DataSourceType.ARXIV: [
        ("Attention Is All You Need", "https://arxiv.org/abs/1706.03762",
         ["transformer", "attention", "nlp"], "English", ContentType.RESEARCH_PAPER),
        ("BERT: Pre-training of Deep Bidirectional Transformers", "https://arxiv.org/abs/1810.04805",
         ["bert", "nlp", "transfer_learning"], "English", ContentType.RESEARCH_PAPER),
        ("Deep Residual Learning for Image Recognition", "https://arxiv.org/abs/1512.03385",
         ["resnet", "computer_vision", "supervised_learning"], "English", ContentType.RESEARCH_PAPER),
        ("Generative Adversarial Networks", "https://arxiv.org/abs/1406.2661",
         ["gan", "unsupervised_learning", "generative"], "English", ContentType.RESEARCH_PAPER),
        ("Proximal Policy Optimization Algorithms", "https://arxiv.org/abs/1707.06347",
         ["reinforcement_learning", "ppo", "policy_gradient"], "English", ContentType.RESEARCH_PAPER),
        ("Self-Supervised Learning of Pretext-Invariant Representations", "https://arxiv.org/abs/1912.01991",
         ["self_supervised_learning", "representation_learning"], "English", ContentType.RESEARCH_PAPER),
        ("Federated Learning: Challenges, Methods, and Future Directions", "https://arxiv.org/abs/1908.07873",
         ["federated_learning", "privacy", "distributed"], "English", ContentType.RESEARCH_PAPER),
        ("Model-Agnostic Meta-Learning for Fast Adaptation", "https://arxiv.org/abs/1703.03400",
         ["meta_learning", "few_shot", "maml"], "English", ContentType.RESEARCH_PAPER),
        ("Semi-Supervised Learning with Deep Generative Models", "https://arxiv.org/abs/1406.5298",
         ["semi_supervised_learning", "vae", "generative"], "English", ContentType.RESEARCH_PAPER),
        ("An Image is Worth 16x16 Words: Transformers for Image Recognition", "https://arxiv.org/abs/2010.11929",
         ["vit", "transformer", "computer_vision"], "English", ContentType.RESEARCH_PAPER),
    ],
    DataSourceType.GITHUB: [
        ("pytorch/pytorch", "https://github.com/pytorch/pytorch",
         ["deep_learning", "framework", "supervised_learning"], "Python", ContentType.CODE_REPOSITORY),
        ("tensorflow/tensorflow", "https://github.com/tensorflow/tensorflow",
         ["deep_learning", "framework", "neural_network"], "Python", ContentType.CODE_REPOSITORY),
        ("openai/gym", "https://github.com/openai/gym",
         ["reinforcement_learning", "environment", "simulation"], "Python", ContentType.CODE_REPOSITORY),
        ("huggingface/transformers", "https://github.com/huggingface/transformers",
         ["transfer_learning", "nlp", "pre_trained_models"], "Python", ContentType.CODE_REPOSITORY),
        ("scikit-learn/scikit-learn", "https://github.com/scikit-learn/scikit-learn",
         ["supervised_learning", "unsupervised_learning", "ml_library"], "Python", ContentType.CODE_REPOSITORY),
        ("tensorflow/federated", "https://github.com/tensorflow/federated",
         ["federated_learning", "privacy", "distributed"], "Python", ContentType.CODE_REPOSITORY),
        ("google-research/meta-dataset", "https://github.com/google-research/meta-dataset",
         ["meta_learning", "few_shot", "dataset"], "Python", ContentType.CODE_REPOSITORY),
        ("facebookresearch/faiss", "https://github.com/facebookresearch/faiss",
         ["unsupervised_learning", "clustering", "similarity_search"], "C++", ContentType.CODE_REPOSITORY),
        ("openai/CLIP", "https://github.com/openai/CLIP",
         ["self_supervised_learning", "multimodal", "contrastive"], "Python", ContentType.CODE_REPOSITORY),
        ("google/jax", "https://github.com/google/jax",
         ["deep_learning", "autodiff", "accelerated_computing"], "Python", ContentType.CODE_REPOSITORY),
    ],
    DataSourceType.KAGGLE: [
        ("ImageNet Large Scale Visual Recognition Challenge", "https://www.kaggle.com/c/imagenet-object-localization-challenge",
         ["computer_vision", "supervised_learning", "classification"], "Python", ContentType.DATASET),
        ("NLP with Disaster Tweets", "https://www.kaggle.com/c/nlp-getting-started",
         ["nlp", "supervised_learning", "classification"], "Python", ContentType.DATASET),
        ("Google Brain - Ventilator Pressure Prediction", "https://www.kaggle.com/c/ventilator-pressure-prediction",
         ["time_series", "supervised_learning", "regression"], "Python", ContentType.DATASET),
        ("Tabular Playground Series", "https://www.kaggle.com/c/tabular-playground-series-jan-2021",
         ["tabular_data", "supervised_learning", "regression"], "Python", ContentType.DATASET),
        ("CommonLit Readability Prize", "https://www.kaggle.com/c/commonlitreadabilityprize",
         ["nlp", "semi_supervised_learning", "regression"], "Python", ContentType.DATASET),
        ("Shopee - Price Match Guarantee", "https://www.kaggle.com/c/shopee-product-matching",
         ["computer_vision", "nlp", "self_supervised_learning"], "Python", ContentType.DATASET),
        ("TensorFlow - Help Protect the Great Barrier Reef", "https://www.kaggle.com/c/tensorflow-great-barrier-reef",
         ["computer_vision", "supervised_learning", "object_detection"], "Python", ContentType.DATASET),
        ("Optiver Realized Volatility Prediction", "https://www.kaggle.com/c/optiver-realized-volatility-prediction",
         ["time_series", "supervised_learning", "finance"], "Python", ContentType.DATASET),
        ("Google Universal Image Embedding", "https://www.kaggle.com/c/google-universal-image-embedding",
         ["computer_vision", "transfer_learning", "embedding"], "Python", ContentType.DATASET),
        ("HuBMAP - Hacking the Human Vasculature", "https://www.kaggle.com/c/hubmap-hacking-the-human-vasculature",
         ["computer_vision", "supervised_learning", "segmentation"], "Python", ContentType.DATASET),
    ],
    DataSourceType.AI_LAB: [
        ("GPT-4 Technical Report", "https://openai.com/research/gpt-4",
         ["large_language_model", "supervised_learning", "rlhf"], "English", ContentType.MODEL),
        ("PaLM 2 Technical Report", "https://ai.google/discover/palm2",
         ["large_language_model", "transfer_learning", "multilingual"], "English", ContentType.MODEL),
        ("LLaMA: Open and Efficient Foundation Language Models", "https://ai.meta.com/research/publications/llama/",
         ["large_language_model", "self_supervised_learning", "efficient"], "English", ContentType.MODEL),
        ("Gemini: A Family of Highly Capable Multimodal Models", "https://deepmind.google/technologies/gemini/",
         ["multimodal", "self_supervised_learning", "reasoning"], "English", ContentType.MODEL),
        ("Claude: Constitutional AI", "https://www.anthropic.com/research/constitutional-ai",
         ["rlhf", "reinforcement_learning", "safety"], "English", ContentType.MODEL),
        ("Stable Diffusion: High-Resolution Image Synthesis", "https://stability.ai/research/stable-diffusion",
         ["generative", "diffusion_model", "unsupervised_learning"], "English", ContentType.MODEL),
        ("AlphaCode: Competitive Programming with LLMs", "https://deepmind.google/research/highlighted-research/alphacode/",
         ["code_generation", "supervised_learning", "transformer"], "English", ContentType.MODEL),
        ("Whisper: Robust Speech Recognition via Large-Scale Supervision", "https://openai.com/research/whisper",
         ["speech_recognition", "supervised_learning", "transformer"], "English", ContentType.MODEL),
        ("DALL-E 3: Improving Image Generation with Better Captions", "https://openai.com/research/dall-e-3",
         ["generative", "text_to_image", "self_supervised_learning"], "English", ContentType.MODEL),
        ("RT-2: Vision-Language-Action Models Transfer Web Knowledge", "https://robotics-transformer2.github.io/",
         ["robotics", "transfer_learning", "reinforcement_learning"], "English", ContentType.MODEL),
    ],
}

_LAB_NAMES = {
    DataSourceType.ARXIV: ["DeepMind", "OpenAI", "Google Brain", "Meta AI", "Stanford AI Lab"],
    DataSourceType.GITHUB: ["Meta AI", "Google", "Hugging Face", "OpenAI", "NVIDIA"],
    DataSourceType.KAGGLE: ["Kaggle Community", "Google Brain", "Shopee Research", "Optiver Labs", "TensorFlow Team"],
    DataSourceType.AI_LAB: ["OpenAI", "Google DeepMind", "Meta AI", "Anthropic", "Stability AI"],
}

_COUNTRIES = ["USA", "UK", "China", "Canada", "France", "Germany", "Japan", "South Korea"]

_NOVELTY_SCORES = {
    DataSourceType.ARXIV: (0.55, 0.95),
    DataSourceType.GITHUB: (0.40, 0.85),
    DataSourceType.KAGGLE: (0.30, 0.75),
    DataSourceType.AI_LAB: (0.65, 0.99),
}


def _make_novelty(source: DataSourceType, index: int) -> float:
    lo, hi = _NOVELTY_SCORES[source]
    step = (hi - lo) / 10
    return round(lo + (index % 10) * step, 3)


class DataIngestionLayer:
    """Scrapes and normalises records from external AI data sources.

    Parameters
    ----------
    tier : Tier
        The subscription tier controlling job limits.
    """

    def __init__(self, tier: Tier) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._job_count: int = 0
        self._records: List[IngestedRecord] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest(
        self,
        source: DataSourceType,
        query: str,
        max_results: int = 10,
    ) -> List[IngestedRecord]:
        """Scrape and normalise data from *source* matching *query*.

        Parameters
        ----------
        source : DataSourceType
            The data source to scrape.
        query : str
            Search query string (used for tag filtering simulation).
        max_results : int
            Maximum number of records to return (capped to available templates).

        Returns
        -------
        List[IngestedRecord]
            Normalised ingested records.

        Raises
        ------
        IngestionLimitError
            If the monthly job quota has been exhausted.
        """
        self._check_job_limit()
        self._job_count += 1

        templates = _MOCK_TEMPLATES[source]
        lab_names = _LAB_NAMES[source]
        count = min(max_results, len(templates))
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        new_records: List[IngestedRecord] = []
        query_lower = query.lower()

        for i, (title, url, tags, language, content_type) in enumerate(templates[:count]):
            normalised_tags = [t.lower().replace(" ", "_") for t in tags]
            # Boost novelty slightly when query term appears in title/tags
            base_novelty = _make_novelty(source, i)
            if any(query_lower in t for t in normalised_tags) or query_lower in title.lower():
                novelty = min(1.0, base_novelty + 0.05)
            else:
                novelty = base_novelty

            record = IngestedRecord(
                id=str(uuid.uuid4()),
                source=source,
                content_type=content_type,
                title=title,
                url=url,
                tags=normalised_tags,
                language=language,
                novelty_score=novelty,
                ingested_at=now,
                metadata={
                    "query": query,
                    "lab_name": lab_names[i % len(lab_names)],
                    "country": _COUNTRIES[i % len(_COUNTRIES)],
                    "rank": i + 1,
                },
            )
            new_records.append(record)
            self._records.append(record)

        return new_records

    def get_records(self) -> List[IngestedRecord]:
        """Return all ingested records (across all jobs)."""
        return list(self._records)

    def get_stats(self) -> dict:
        """Return a summary of ingestion activity."""
        source_counts: dict = {}
        for r in self._records:
            source_counts[r.source.value] = source_counts.get(r.source.value, 0) + 1
        return {
            "jobs_executed": self._job_count,
            "total_records": len(self._records),
            "jobs_remaining": self.jobs_remaining(),
            "records_by_source": source_counts,
        }

    def reset(self) -> None:
        """Reset job count and records (e.g. monthly billing cycle reset)."""
        self._job_count = 0
        self._records = []

    def jobs_remaining(self) -> Optional[int]:
        """Return jobs remaining this month, or None for unlimited tiers."""
        limit = self.config.ingestion_jobs_per_month
        if limit is None:
            return None
        return max(limit - self._job_count, 0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_job_limit(self) -> None:
        limit = self.config.ingestion_jobs_per_month
        if limit is not None and self._job_count >= limit:
            raise IngestionLimitError(
                f"Monthly ingestion job limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )
