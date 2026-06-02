from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

@dataclass
class Narrative:
    headline: str
    problem_statement: str
    solution: str
    evidence: str
    call_to_action: str

@dataclass
class NarrativeDoc:
    audience: str
    narrative: Narrative
    story_arc: str


class StrategicNarrative:
    def generate(self, company_data: Mapping[str, str], audience: str) -> NarrativeDoc:
        hero = company_data.get('company_name', 'DreamCo')
        problem = company_data.get('problem', 'fragmented software limits growth')
        solution = company_data.get('solution', 'an empire of interoperable bots')
        evidence = company_data.get('evidence', 'customers consolidate workflows and reduce response times')
        headline = self._headline(hero, audience)
        cta = self._cta(audience)
        narrative = Narrative(headline, f'{hero} confronts {problem}.', f'{hero} solves it with {solution}.', evidence, cta)
        return NarrativeDoc(audience=audience, narrative=narrative, story_arc='call to adventure → trials → transformation → proof → invitation')

    @staticmethod
    def _headline(hero: str, audience: str) -> str:
        mapping = {
            'investor': f'{hero} is compounding into an AI operating system.',
            'customer': f'{hero} removes operational drag with specialized bots.',
            'partner': f'{hero} expands your reach through capability exchange.',
            'employee': f'{hero} lets teams build with leverage and clarity.',
            'press': f'{hero} turns vertical AI into coordinated execution.',
        }
        return mapping.get(audience, f'{hero} is building category-defining AI infrastructure.')

    @staticmethod
    def _cta(audience: str) -> str:
        return {'investor': 'Back the scale curve.', 'customer': 'Start a pilot.', 'partner': 'Integrate capabilities.', 'employee': 'Join the mission.', 'press': 'Cover the transformation.'}.get(audience, 'Learn more.')



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
