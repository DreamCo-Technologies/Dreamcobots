"""Consensus voting with weighted ballots and quorum support."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class Vote:
    voter: str
    choice: str
    weight: float = 1.0


class ConsensusVoting:
    def __init__(self, quorum: float = 0.6) -> None:
        self.quorum = quorum
        self._votes: List[Vote] = []

    def cast_vote(self, voter: str, choice: str, weight: float = 1.0) -> Vote:
        vote = Vote(voter=voter, choice=choice, weight=max(weight, 0.0))
        self._votes = [existing for existing in self._votes if existing.voter != voter]
        self._votes.append(vote)
        return vote

    def quorum_status(self, eligible_weight: float) -> Dict[str, float | bool]:
        cast_weight = sum(vote.weight for vote in self._votes)
        ratio = cast_weight / max(eligible_weight, 0.0001)
        return {"cast_weight": round(cast_weight, 3), "quorum_ratio": round(ratio, 3), "met": ratio >= self.quorum}

    def result(self) -> Dict[str, object]:
        tallies: Dict[str, float] = {}
        for vote in self._votes:
            tallies[vote.choice] = tallies.get(vote.choice, 0.0) + vote.weight
        ordered = sorted(tallies.items(), key=lambda item: item[1], reverse=True)
        return {
            "winner": ordered[0][0] if ordered else None,
            "tallies": {key: round(value, 3) for key, value in ordered},
            "vote_count": len(self._votes),
        }

    def snapshot(self, eligible_weight: float) -> Dict[str, object]:
        return {"quorum": self.quorum_status(eligible_weight), "result": self.result()}


def run_ballot(votes: Iterable[Dict[str, object]], eligible_weight: float) -> Dict[str, object]:
    ballot = ConsensusVoting()
    for vote in votes:
        ballot.cast_vote(str(vote['voter']), str(vote['choice']), float(vote.get('weight', 1.0)))
    return ballot.snapshot(eligible_weight)
