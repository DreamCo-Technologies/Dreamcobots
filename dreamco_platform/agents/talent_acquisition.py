"""Autonomous talent acquisition bot."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence
import re


@dataclass
class TalentProfile:
    skills: List[str]
    experience_years: float
    culture_fit_score: float
    salary_expectation: float


class TalentAcquisition:
    KNOWN_SKILLS = {"python", "sql", "ml", "sales", "design", "leadership", "product", "aws"}

    def screen(self, resume_text: str) -> TalentProfile:
        lower = resume_text.lower()
        skills = sorted(skill for skill in self.KNOWN_SKILLS if skill in lower)
        years = [int(match) for match in re.findall(r"(\d+)\+? years", lower)]
        experience = float(max(years) if years else len(skills))
        culture = 0.5 + 0.05 * sum(word in lower for word in ["mentor", "collaborative", "ownership", "mission"])
        salary_match = re.search(r"\$(\d{2,3})(?:,?000)?", resume_text)
        salary = float(salary_match.group(1)) * 1000 if salary_match else 90000.0 + 5000 * experience
        return TalentProfile(skills, experience, min(1.0, culture), salary)

    def score_candidate(self, job_description: str, profile: TalentProfile) -> float:
        jd = job_description.lower()
        matched_skills = sum(skill in jd for skill in profile.skills)
        demand_years = max([int(value) for value in re.findall(r"(\d+)\+? years", jd)] or [1])
        experience_fit = min(1.0, profile.experience_years / demand_years)
        salary_fit = 1.0 if "salary" not in jd else max(0.0, 1.0 - profile.salary_expectation / 300000.0)
        return round((matched_skills * 0.4 + experience_fit * 0.4 + profile.culture_fit_score * 0.1 + salary_fit * 0.1), 3)

    def generate_interview_questions(self, role: str, profile: TalentProfile) -> List[str]:
        role_lower = role.lower()
        prompts = [f"Describe a project where you used {skill} in a {role} context." for skill in profile.skills[:3]]
        if "engineer" in role_lower:
            prompts.append("How do you trade off delivery speed against reliability in production systems?")
        if "manager" in role_lower:
            prompts.append("How do you coach underperforming team members while preserving accountability?")
        prompts.append("Which work environment best supports your culture fit and long-term performance?")
        return prompts
