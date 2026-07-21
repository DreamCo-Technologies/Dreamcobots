"""
ai_method_tags.py — AI method tagging module (metadata handling).

Enriches classified AI methods with structured metadata tags that can
be persisted, queried, and used to drive the learning pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class MethodTag:
    """A single metadata tag attached to an AI method."""

    name: str
    category: str
    description: Optional[str] = None
    aliases: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Built-in tag catalogue
# ---------------------------------------------------------------------------

_BUILTIN_TAGS: List[MethodTag] = [
    MethodTag("supervised_learning", "learning_paradigm", "Training with labelled data.", ["SL"]),
    MethodTag("unsupervised_learning", "learning_paradigm", "Training without labels.", ["UL"]),
    MethodTag("reinforcement_learning", "learning_paradigm", "Agent learns via reward signals.", ["RL"]),
    MethodTag("self_supervised_learning", "learning_paradigm", "Labels derived from the data itself.", ["SSL"]),
    MethodTag("transfer_learning", "learning_paradigm", "Reusing models pre-trained on related tasks.", ["TL"]),
    MethodTag("neural_network", "architecture", "Multi-layer perceptron or deep network."),
    MethodTag("transformer", "architecture", "Attention-based sequence model.", ["attention", "bert", "gpt"]),
    MethodTag("convolutional", "architecture", "Convolutional neural network.", ["CNN"]),
    MethodTag("recurrent", "architecture", "Recurrent or LSTM network.", ["RNN", "LSTM", "GRU"]),
    MethodTag("generative_adversarial", "architecture", "GAN-based model.", ["GAN"]),
    MethodTag("diffusion_model", "architecture", "Score-based generative model.", ["DDPM"]),
    MethodTag("nlp", "domain", "Natural language processing."),
    MethodTag("computer_vision", "domain", "Image or video understanding."),
    MethodTag("robotics", "domain", "Physical robot control and perception."),
    MethodTag("time_series", "domain", "Sequential or temporal data."),
    MethodTag("tabular", "domain", "Structured tabular data."),
]


class AIMethodTagger:
    """
    Assigns metadata tags to AI methods based on text analysis.

    Parameters
    ----------
    custom_tags : list[MethodTag] | None
        Extra tags to add to the built-in catalogue.
    """

    def __init__(self, custom_tags: Optional[List[MethodTag]] = None):
        self._tags: Dict[str, MethodTag] = {}
        for tag in _BUILTIN_TAGS:
            self._register(tag)
        for tag in (custom_tags or []):
            self._register(tag)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def tag(self, text: str) -> List[MethodTag]:
        """
        Return all tags whose name or aliases appear in *text*.

        Parameters
        ----------
        text : str
            Free-text description to analyse.

        Returns
        -------
        list[MethodTag]
        """
        lower = text.lower()
        matched: List[MethodTag] = []
        seen: Set[str] = set()
        for tag in self._tags.values():
            if tag.name in seen:
                continue
            terms = [tag.name.replace("_", " ")] + [a.lower() for a in tag.aliases]
            if any(term in lower for term in terms):
                matched.append(tag)
                seen.add(tag.name)
        return matched

    def tag_batch(self, texts: List[str]) -> List[List[MethodTag]]:
        """Tag a list of text snippets."""
        return [self.tag(t) for t in texts]

    def add_tag(self, tag: MethodTag) -> None:
        """Register a new custom tag."""
        self._register(tag)

    def list_tags(self, category: Optional[str] = None) -> List[MethodTag]:
        """Return all registered tags, optionally filtered by *category*."""
        tags = list(self._tags.values())
        if category is not None:
            tags = [t for t in tags if t.category == category]
        return tags

    def get_tag(self, name: str) -> Optional[MethodTag]:
        """Look up a tag by name."""
        return self._tags.get(name)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _register(self, tag: MethodTag) -> None:
        """Add *tag* to the internal catalogue."""
        self._tags[tag.name] = tag
