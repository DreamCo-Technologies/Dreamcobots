"""Patent monitoring and novelty scoring utilities."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set
import re


@dataclass
class PatentFiling:
    filing_id: str
    title: str
    abstract: str
    assignee: str
    cited_terms: Set[str] = field(default_factory=set)


class PatentMonitor:
    STOPWORDS = {"the", "and", "for", "with", "from", "into", "that", "this", "using"}

    def keywords(self, text: str) -> Set[str]:
        return {token for token in re.findall(r"[a-zA-Z]{4,}", text.lower()) if token not in self.STOPWORDS}

    def enrich(self, filing: PatentFiling) -> PatentFiling:
        combined = f"{filing.title} {filing.abstract}"
        filing.cited_terms = self.keywords(combined)
        return filing

    def overlap_score(self, left: PatentFiling, right: PatentFiling) -> float:
        left_terms = left.cited_terms or self.keywords(left.title + " " + left.abstract)
        right_terms = right.cited_terms or self.keywords(right.title + " " + right.abstract)
        union = left_terms | right_terms
        return round(len(left_terms & right_terms) / max(len(union), 1), 3)

    def novelty_report(self, candidate: PatentFiling, corpus: Iterable[PatentFiling]) -> Dict[str, object]:
        candidate = self.enrich(candidate)
        scored = []
        for filing in corpus:
            filing = self.enrich(filing)
            score = self.overlap_score(candidate, filing)
            scored.append({"filing_id": filing.filing_id, "assignee": filing.assignee, "overlap": score})
        scored.sort(key=lambda item: item["overlap"], reverse=True)
        novelty = round(1.0 - (scored[0]["overlap"] if scored else 0.0), 3)
        return {
            "candidate": candidate.filing_id,
            "novelty": novelty,
            "closest_matches": scored[:5],
        }

    def assignee_landscape(self, corpus: Iterable[PatentFiling]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for filing in corpus:
            counts[filing.assignee] = counts.get(filing.assignee, 0) + 1
        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def compare_candidates(candidates: Iterable[PatentFiling], corpus: Iterable[PatentFiling]) -> List[Dict[str, object]]:
    monitor = PatentMonitor()
    reference = list(corpus)
    return [monitor.novelty_report(candidate, reference) for candidate in candidates]
