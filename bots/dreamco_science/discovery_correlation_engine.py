# GLOBAL AI SOURCES FLOW
"""Cross-field discovery correlation helpers for DreamCo science."""
import sys
import os
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
from bots.dreamco_science.dream_science_brain import DreamScienceBrain
from bots.dreamco_science.evidence_grading import EVIDENCE_RANK, grade_evidence


class DiscoveryCorrelationEngine:
    """Find notable cross-domain overlaps in the DreamScienceBrain store."""

    def __init__(self, brain: DreamScienceBrain | None = None):
        self.brain = brain or DreamScienceBrain()

    @staticmethod
    def _tokenize(*values: str) -> set[str]:
        tokens = set()
        for value in values:
            for token in str(value or '').lower().replace('-', ' ').split():
                token = token.strip('.,:;()[]{}')
                if len(token) > 3:
                    tokens.add(token)
        return tokens

    def correlate(self, domain_a, domain_b) -> list[dict]:
        discoveries_a = self.brain.get_discoveries(domain=domain_a)
        discoveries_b = self.brain.get_discoveries(domain=domain_b)
        correlations = []
        for left in discoveries_a:
            left_tokens = self._tokenize(left['title'], left['summary'])
            for right in discoveries_b:
                overlap = left_tokens & self._tokenize(right['title'], right['summary'])
                if overlap:
                    correlations.append({
                        'discovery_a': left,
                        'discovery_b': right,
                        'relationship': f"Shared signals: {', '.join(sorted(overlap)[:3])}",
                    })
        return correlations

    def find_hidden_relationships(self, query_term) -> list[dict]:
        term = str(query_term or '').lower()
        matches = []
        for discovery in self.brain.get_discoveries():
            haystack = f"{discovery['title']} {discovery['summary']} {discovery['domain']}".lower()
            if term and term in haystack:
                matches.append(discovery)
        insights = []
        for idx, discovery in enumerate(matches):
            for related in matches[idx + 1:]:
                if discovery['domain'] != related['domain']:
                    insights.append({
                        'query_term': query_term,
                        'domains': sorted([discovery['domain'], related['domain']]),
                        'discovery_a': discovery,
                        'discovery_b': related,
                        'insight': f"{query_term} appears in both {discovery['domain']} and {related['domain']}",
                    })
        return insights

    def generate_hypothesis(self, domain, context) -> dict:
        domain_findings = self.brain.get_discoveries(domain=domain)
        supporting = [d for d in domain_findings if EVIDENCE_RANK[grade_evidence(d['evidence_level'])] <= EVIDENCE_RANK[grade_evidence('strong_evidence')]]
        confidence = round(min(0.95, 0.35 + (0.15 * len(supporting))), 2)
        titles = ', '.join(d['title'] for d in supporting[:3]) or 'early-stage discovery patterns'
        return {
            'hypothesis': f"In {domain}, {context} may benefit from integrating insights from {titles}.",
            'domain': domain,
            'confidence': confidence,
            'rationale': f"Generated from {len(domain_findings)} stored discoveries with {len(supporting)} strong or proven signals.",
        }

    def scan_for_breakthroughs(self, domains=None) -> list[dict]:
        discoveries = self.brain.get_discoveries()
        if domains:
            allowed = set(domains)
            discoveries = [d for d in discoveries if d['domain'] in allowed]
        return [
            discovery for discovery in discoveries
            if EVIDENCE_RANK[grade_evidence(discovery['evidence_level'])] <= EVIDENCE_RANK[grade_evidence('strong_evidence')]
        ]
