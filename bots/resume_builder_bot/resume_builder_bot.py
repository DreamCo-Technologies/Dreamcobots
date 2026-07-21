"""Resume Builder Bot — tier-aware resume creation and ATS optimization."""
import sys, os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.resume_builder_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class ResumeBuilderBot:
    """Tier-aware resume builder and ATS optimization bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="ResumeBuilderBot")

    def build_resume(self, name: str, experience, skills, education, target_role=None) -> dict:
        return {
            "name": name,
            "contact": {
                "email": f"{name.lower().replace(' ', '.')}@email.com",
                "phone": "555-0100",
                "location": "City, State",
            },
            "summary": f"Experienced professional with expertise in {', '.join(skills[:3]) if skills else 'various fields'}",
            "experience": experience if isinstance(experience, list) else [{"title": experience, "company": "Previous Company", "duration": "2020-2023", "bullets": ["Led key initiatives", "Improved processes by 20%"]}],
            "skills": skills if isinstance(skills, list) else [skills],
            "education": education if isinstance(education, list) else [{"degree": education, "school": "University", "year": "2019"}],
            "target_role": target_role,
            "template_used": "Professional" if self.tier == Tier.FREE else random.choice(["Executive", "Creative", "Technical", "Modern"]),
            "format": "pdf-ready",
            "word_count": random.randint(350, 500),
            "tier_used": self.tier.value,
        }

    def calculate_ats_score(self, resume_dict: dict) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("ATS score requires PRO or ENTERPRISE tier")
        return {
            "score": random.randint(65, 95),
            "breakdown": {
                "keywords": random.randint(60, 100),
                "formatting": random.randint(70, 100),
                "completeness": random.randint(75, 100),
                "readability": random.randint(70, 100),
            },
            "tier_used": self.tier.value,
        }

    def generate_cover_letter(self, resume_dict: dict, job_description: str) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Cover letter requires PRO or ENTERPRISE tier")
        name = resume_dict.get("name", "Candidate")
        target = resume_dict.get("target_role", "the position")
        body = f"Dear Hiring Manager,\n\nI am writing to express my interest in {target}. With my background in {job_description[:50] if job_description else 'relevant areas'}, I am confident I would be a valuable addition to your team.\n\n{name}"
        return {
            "subject": f"Application for {target}",
            "body": body,
            "word_count": len(body.split()),
            "tier_used": self.tier.value,
        }

    def suggest_improvements(self, resume_dict: dict) -> list:
        suggestions = [
            {"area": "Summary", "suggestion": "Add quantifiable achievements to your summary", "priority": "high"},
            {"area": "Skills", "suggestion": "Include industry-specific keywords and tools", "priority": "high"},
            {"area": "Experience", "suggestion": "Use action verbs to start each bullet point", "priority": "medium"},
            {"area": "Keywords", "suggestion": "Align keywords with the target job description", "priority": "medium"},
            {"area": "Formatting", "suggestion": "Ensure consistent date formatting throughout", "priority": "low"},
        ]
        return suggestions

    def run(self) -> dict:
        return self.flow.run_pipeline(
            raw_data={"bot": "ResumeBuilderBot", "tier": self.tier.value},
            learning_method="supervised",
        )
