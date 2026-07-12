from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class PromptVariant:
    template: str
    token_count: int
    avg_quality_score: float
    avg_cost_per_call: float


@dataclass
class OptimizedPrompt:
    template: str
    score: float
    supporting_examples: List[str]


class Optimizer:
    def run(self, base_prompt: str, test_cases: Iterable[dict]) -> OptimizedPrompt:
        candidates = self._generate_variants(base_prompt, list(test_cases))
        best = max(candidates, key=self._score)
        return OptimizedPrompt(
            best.template,
            round(self._score(best), 4),
            self._few_shot_examples(best.template),
        )

    def compare_variants(self, base_prompt: str, test_cases: Iterable[dict]) -> List[dict]:
        variants = self._generate_variants(base_prompt, list(test_cases))
        return [
            {
                "template": variant.template,
                "score": round(self._score(variant), 4),
                "tokens": variant.token_count,
                "quality": round(variant.avg_quality_score, 4),
            }
            for variant in variants
        ]

    def token_budget(self, prompt: str, budget: int = 250) -> bool:
        return len(prompt.split()) <= budget

    def _generate_variants(self, base_prompt: str, test_cases: List[dict]) -> List[PromptVariant]:
        examples = min(4, max(1, len(test_cases)))
        variants = []
        for instruction in ["Be concise.", "Reason step-by-step.", "Prefer examples before answers."]:
            template = f"{base_prompt}\n\n{instruction}\nExamples: {examples}"
            quality = 0.6 + 0.08 * examples + (0.07 if "step-by-step" in instruction else 0.04)
            tokens = len(template.split())
            cost = tokens * 0.00002
            variants.append(PromptVariant(template, tokens, quality, cost))
        return variants

    def _score(self, variant: PromptVariant) -> float:
        speed_bonus = max(0.0, 1 - variant.token_count / 250)
        return variant.avg_quality_score * 0.65 + speed_bonus * 0.2 - variant.avg_cost_per_call * 40

    def _few_shot_examples(self, template: str) -> List[str]:
        if "step-by-step" in template:
            return ["Input: analyze churn -> Output: identify drivers, quantify impact, recommend action"]
        return ["Input: summarize market -> Output: concise summary with three takeaways"]
