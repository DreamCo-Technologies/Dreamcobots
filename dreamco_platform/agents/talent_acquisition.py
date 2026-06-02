"""Candidate ranking and hiring funnel planning."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List


@dataclass
class Candidate:
    name: str
    skills: List[str]
    years_experience: float
    expected_salary: float
    location_overlap: float
    interview_score: float = 0.0
    notes: List[str] = field(default_factory=list)


class TalentAcquisitionAgent:
    def score_candidate(self, candidate: Candidate, required_skills: Iterable[str], budget: float) -> float:
        required = set(required_skills)
        skill_match = len(required & set(candidate.skills)) / max(len(required), 1)
        affordability = max(0.0, min(1.0, budget / max(candidate.expected_salary, 1.0)))
        experience = min(1.0, candidate.years_experience / 8)
        score = skill_match * 0.45 + affordability * 0.2 + experience * 0.15 + candidate.location_overlap * 0.1 + candidate.interview_score * 0.1
        return round(score, 3)

    def shortlist(self, candidates: Iterable[Candidate], required_skills: Iterable[str], budget: float, limit: int = 5) -> List[Dict[str, object]]:
        required_skills = list(required_skills)
        scored = []
        for candidate in candidates:
            score = self.score_candidate(candidate, required_skills, budget)
            missing = sorted(set(required_skills) - set(candidate.skills))
            scored.append({
                "name": candidate.name,
                "score": score,
                "expected_salary": candidate.expected_salary,
                "missing_skills": missing,
                "notes": list(candidate.notes),
            })
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]

    def compensation_band(self, candidates: Iterable[Candidate]) -> Dict[str, float]:
        salaries = [candidate.expected_salary for candidate in candidates]
        if not salaries:
            return {"low": 0.0, "mid": 0.0, "high": 0.0}
        salaries.sort()
        return {
            "low": round(salaries[0], 2),
            "mid": round(salaries[len(salaries) // 2], 2),
            "high": round(salaries[-1], 2),
        }

    def hiring_plan(self, pipeline_size: int, target_hires: int, conversion_rate: float) -> Dict[str, int]:
        expected_hires = round(pipeline_size * conversion_rate)
        additional = max(0, target_hires - expected_hires)
        return {
            "expected_hires": expected_hires,
            "additional_candidates_needed": additional,
            "recommended_pipeline": max(pipeline_size, int(target_hires / max(conversion_rate, 0.01))),
        }


def best_fit(candidates: Iterable[Candidate], required_skills: Iterable[str], budget: float) -> Dict[str, object] | None:
    ranked = TalentAcquisitionAgent().shortlist(candidates, required_skills, budget, limit=1)
    return ranked[0] if ranked else None
