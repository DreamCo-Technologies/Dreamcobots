from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping

@dataclass
class EthicsViolation:
    category: str
    description: str
    severity: str
    affected_users: int
    remediation: str

@dataclass
class EthicsReport:
    violations: List[EthicsViolation]
    demographic_parity: float
    equalized_odds_gap: float
    compliant: bool


class EthicsChecker:
    def audit(self, bot_outputs_sample: Iterable[Mapping[str, object]]) -> EthicsReport:
        violations: List[EthicsViolation] = []
        favorable = {'group_a': 0, 'group_b': 0}
        positives = {'group_a': 0, 'group_b': 0}
        true_positive = {'group_a': 0, 'group_b': 0}
        actual_positive = {'group_a': 0, 'group_b': 0}
        for sample in bot_outputs_sample:
            text = str(sample.get('output', '')).lower()
            group = str(sample.get('group', 'group_a'))
            decision = bool(sample.get('approved', False))
            actual = bool(sample.get('actual_positive', False))
            favorable[group] += int(decision)
            positives[group] += 1
            true_positive[group] += int(decision and actual)
            actual_positive[group] += int(actual)
            if 'guaranteed' in text or 'manipulate' in text:
                violations.append(EthicsViolation('manipulation', 'Potential coercive phrasing detected.', 'high', 1, 'Rewrite output and retrain prompt policy.'))
            if 'private data' in text:
                violations.append(EthicsViolation('privacy_violation', 'Sensitive data reference detected.', 'critical', 1, 'Redact output and trigger privacy review.'))
        rate_a = favorable['group_a'] / max(positives['group_a'], 1)
        rate_b = favorable['group_b'] / max(positives['group_b'], 1)
        tpr_a = true_positive['group_a'] / max(actual_positive['group_a'], 1)
        tpr_b = true_positive['group_b'] / max(actual_positive['group_b'], 1)
        return EthicsReport(violations=violations, demographic_parity=round(abs(rate_a - rate_b), 3), equalized_odds_gap=round(abs(tpr_a - tpr_b), 3), compliant=not violations and abs(rate_a-rate_b) < 0.1 and abs(tpr_a-tpr_b) < 0.1)



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
