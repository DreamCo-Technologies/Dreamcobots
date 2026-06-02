from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

@dataclass
class Principle:
    rule: str
    rationale: str
    detection_fn: Callable[[str], bool]
    remediation: str

@dataclass
class ConstitutionalScore:
    score: float
    violations: List[str]
    revised_output: str


class ConstitutionalAI:
    def __init__(self) -> None:
        self.principles = [
            Principle('harmlessness', 'Avoid harm and unsafe instructions.', lambda text: 'harm' in text.lower() or 'weapon' in text.lower(), 'Remove harmful content and offer safe alternative.'),
            Principle('honesty', 'Avoid fabricated certainty.', lambda text: 'guaranteed' in text.lower() and 'if' not in text.lower(), 'Qualify uncertainty and cite limits.'),
            Principle('helpfulness', 'Be actionable and clear.', lambda text: len(text.strip()) < 20, 'Expand answer with concrete steps.'),
        ]

    def evaluate(self, bot_output: str) -> ConstitutionalScore:
        violations: List[str] = []
        revised = bot_output
        for principle in self.principles:
            if principle.detection_fn(bot_output):
                violations.append(principle.rule)
                revised = self._revise(revised, principle)
        score = max(0.0, 1.0 - 0.3 * len(violations))
        return ConstitutionalScore(score=round(score, 2), violations=violations, revised_output=revised)

    def _revise(self, text: str, principle: Principle) -> str:
        if principle.rule == 'honesty':
            text = text.replace('guaranteed', 'likely')
        if principle.rule == 'harmlessness':
            text += ' Safe alternative: escalate to approved experts and follow policy.'
        if principle.rule == 'helpfulness':
            text += ' Add steps, risks, and expected outcome.'
        return text



def module_summary() -> dict:
    """Provide a compact runtime summary for orchestration tooling."""
    public_items = [name for name in globals() if not name.startswith('_')]
    return {
        'module': __name__,
        'public_items': sorted(public_items),
        'line_count': len(__doc__.splitlines()) if __doc__ else 0,
    }


def demo_payload() -> dict:
    """Return a deterministic payload useful for smoke-free integration wiring."""
    return {'module': __name__, 'status': 'ready'}
