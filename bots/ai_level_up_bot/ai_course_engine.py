"""
AI Course Engine — 10-level AI University course structure for the DreamCo
AI Level-Up Bot.

Note: Courses carry DreamCo Professional Certificate branding, not official
US accreditation, to comply with legal requirements.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


@dataclass
class CourseModule:
    """A single module within a course level."""

    title: str
    description: str
    teaching_modes: List[str]
    duration_minutes: int
    token_cost: float = 0.0


@dataclass
class CourseLevel:
    """A level in the 10-level AI University."""

    level: int
    name: str
    focus: str
    modules: List[CourseModule]
    certification: str
    prerequisite_level: Optional[int] = None

    def total_duration_minutes(self) -> int:
        return sum(m.duration_minutes for m in self.modules)

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "name": self.name,
            "focus": self.focus,
            "modules": [
                {
                    "title": m.title,
                    "description": m.description,
                    "teaching_modes": m.teaching_modes,
                    "duration_minutes": m.duration_minutes,
                    "token_cost": m.token_cost,
                }
                for m in self.modules
            ],
            "certification": self.certification,
            "total_duration_minutes": self.total_duration_minutes(),
        }


# ---------------------------------------------------------------------------
# Teaching modes
# ---------------------------------------------------------------------------

MODE_VIDEO = "video"
MODE_SIMULATION = "simulation"
MODE_READING = "reading"
MODE_CODING_LAB = "coding_lab"

ALL_MODES = [MODE_VIDEO, MODE_SIMULATION, MODE_READING, MODE_CODING_LAB]

# ---------------------------------------------------------------------------
# Course levels data
# ---------------------------------------------------------------------------

_COURSE_LEVELS: List[CourseLevel] = [
    CourseLevel(
        level=1,
        name="AI Basics",
        focus="Foundational understanding of artificial intelligence",
        certification="DreamCo AI Foundations Certificate",
        prerequisite_level=None,
        modules=[
            CourseModule(
                title="What is AI?",
                description="History, definitions, and core concepts of artificial intelligence.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=30,
            ),
            CourseModule(
                title="Types of AI",
                description="Narrow AI, General AI, and Superintelligence explained.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=25,
            ),
            CourseModule(
                title="AI Ethics & Safety",
                description="Responsible AI use, bias, privacy, and societal impact.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=30,
            ),
            CourseModule(
                title="AI Tools Overview",
                description="Tour of today's most impactful AI tools and platforms.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=40,
                token_cost=0.5,
            ),
        ],
    ),
    CourseLevel(
        level=2,
        name="Prompt Engineering",
        focus="Crafting effective prompts for large language models",
        certification="DreamCo Prompt Engineering Certificate",
        prerequisite_level=1,
        modules=[
            CourseModule(
                title="Prompt Fundamentals",
                description="Role, context, instruction, and output format in prompts.",
                teaching_modes=[MODE_VIDEO, MODE_CODING_LAB],
                duration_minutes=35,
                token_cost=1.0,
            ),
            CourseModule(
                title="Advanced Prompt Patterns",
                description="Chain-of-thought, few-shot, and system prompts.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION, MODE_CODING_LAB],
                duration_minutes=45,
                token_cost=1.5,
            ),
            CourseModule(
                title="Multimodal Prompting",
                description="Prompting image, audio, and video generation models.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=40,
                token_cost=2.0,
            ),
            CourseModule(
                title="Prompt Optimisation",
                description="Iterative refinement and A/B testing of prompts.",
                teaching_modes=[MODE_CODING_LAB, MODE_SIMULATION],
                duration_minutes=50,
                token_cost=2.0,
            ),
        ],
    ),
    CourseLevel(
        level=3,
        name="AI Content Creation",
        focus="Using AI tools to produce high-quality content at scale",
        certification="DreamCo AI Content Creator Certificate",
        prerequisite_level=2,
        modules=[
            CourseModule(
                title="AI Writing & Copywriting",
                description="Blog posts, ad copy, and long-form content with AI.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=45,
                token_cost=2.0,
            ),
            CourseModule(
                title="AI Image & Video Creation",
                description="Generating and editing images and short videos.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=60,
                token_cost=3.0,
            ),
            CourseModule(
                title="AI Voice & Audio Production",
                description="Creating voiceovers, music, and podcasts with AI.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=50,
                token_cost=2.5,
            ),
            CourseModule(
                title="SEO & Distribution with AI",
                description="AI-driven keyword research and content distribution.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=40,
                token_cost=1.5,
            ),
        ],
    ),
    CourseLevel(
        level=4,
        name="AI Automation",
        focus="Automating business workflows with AI tools",
        certification="DreamCo AI Automation Certificate",
        prerequisite_level=3,
        modules=[
            CourseModule(
                title="Workflow Automation Fundamentals",
                description="Zapier, Make, and n8n for no-code automation.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION, MODE_CODING_LAB],
                duration_minutes=60,
                token_cost=3.0,
            ),
            CourseModule(
                title="AI in Customer Service",
                description="Chatbots, CRM automation, and support ticket routing.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=50,
                token_cost=2.5,
            ),
            CourseModule(
                title="Marketing Automation with AI",
                description="Email campaigns, social scheduling, and lead scoring.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION, MODE_CODING_LAB],
                duration_minutes=55,
                token_cost=3.0,
            ),
            CourseModule(
                title="Data Pipeline Automation",
                description="ETL workflows and AI-powered data processing.",
                teaching_modes=[MODE_CODING_LAB, MODE_READING],
                duration_minutes=65,
                token_cost=3.5,
            ),
        ],
    ),
    CourseLevel(
        level=5,
        name="AI Business Building",
        focus="Launching and scaling AI-powered ventures",
        certification="DreamCo AI Business Builder Certificate",
        prerequisite_level=4,
        modules=[
            CourseModule(
                title="AI Business Models",
                description="SaaS, API, marketplace, and service models for AI products.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=50,
                token_cost=2.5,
            ),
            CourseModule(
                title="Building an AI MVP",
                description="Rapid prototyping using no-code and low-code AI tools.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION, MODE_CODING_LAB],
                duration_minutes=70,
                token_cost=4.0,
            ),
            CourseModule(
                title="AI Monetisation Strategies",
                description="Pricing, subscriptions, tokens, and affiliate income.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=45,
                token_cost=2.0,
            ),
            CourseModule(
                title="AI Go-To-Market Strategy",
                description="Launch playbooks for AI products and services.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=55,
                token_cost=3.0,
            ),
        ],
    ),
    CourseLevel(
        level=6,
        name="AI Agent Development",
        focus="Building autonomous AI agents and multi-agent systems",
        certification="DreamCo AI Agent Developer Certificate",
        prerequisite_level=5,
        modules=[
            CourseModule(
                title="Introduction to AI Agents",
                description="Agent architectures, tools, and planning strategies.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=50,
                token_cost=3.0,
            ),
            CourseModule(
                title="Building Single Agents",
                description="Coding agents with LangChain, AutoGPT, and CrewAI.",
                teaching_modes=[MODE_CODING_LAB, MODE_SIMULATION],
                duration_minutes=80,
                token_cost=5.0,
            ),
            CourseModule(
                title="Multi-Agent Systems",
                description="Orchestrating collaborative agents for complex tasks.",
                teaching_modes=[MODE_CODING_LAB, MODE_SIMULATION],
                duration_minutes=90,
                token_cost=6.0,
            ),
            CourseModule(
                title="Agent Safety & Evaluation",
                description="Testing, monitoring, and securing AI agents.",
                teaching_modes=[MODE_VIDEO, MODE_CODING_LAB],
                duration_minutes=60,
                token_cost=4.0,
            ),
        ],
    ),
    CourseLevel(
        level=7,
        name="AI Infrastructure",
        focus="Hosting, scaling, and managing AI applications in production",
        certification="DreamCo AI Infrastructure Certificate",
        prerequisite_level=6,
        modules=[
            CourseModule(
                title="Cloud AI Platforms",
                description="AWS, GCP, and Azure AI services overview.",
                teaching_modes=[MODE_VIDEO, MODE_CODING_LAB],
                duration_minutes=70,
                token_cost=4.0,
            ),
            CourseModule(
                title="Model Serving & APIs",
                description="FastAPI, TorchServe, Triton, and serverless inference.",
                teaching_modes=[MODE_CODING_LAB, MODE_READING],
                duration_minutes=80,
                token_cost=5.0,
            ),
            CourseModule(
                title="Scalable AI Architecture",
                description="Microservices, queues, and auto-scaling for AI workloads.",
                teaching_modes=[MODE_VIDEO, MODE_CODING_LAB],
                duration_minutes=75,
                token_cost=5.0,
            ),
            CourseModule(
                title="MLOps & CI/CD for AI",
                description="Version control, experiment tracking, and model deployment.",
                teaching_modes=[MODE_CODING_LAB, MODE_READING],
                duration_minutes=85,
                token_cost=6.0,
            ),
        ],
    ),
    CourseLevel(
        level=8,
        name="AI Research",
        focus="Conducting AI experiments and optimising models",
        certification="DreamCo AI Research Certificate",
        prerequisite_level=7,
        modules=[
            CourseModule(
                title="Research Methodology in AI",
                description="Literature review, hypothesis formation, and benchmarking.",
                teaching_modes=[MODE_READING, MODE_VIDEO],
                duration_minutes=60,
                token_cost=3.0,
            ),
            CourseModule(
                title="Fine-Tuning & RLHF",
                description="Adapting pre-trained models to custom datasets.",
                teaching_modes=[MODE_CODING_LAB, MODE_SIMULATION],
                duration_minutes=100,
                token_cost=8.0,
            ),
            CourseModule(
                title="Evaluation Frameworks",
                description="MMLU, HumanEval, HELM, and custom evals.",
                teaching_modes=[MODE_CODING_LAB, MODE_READING],
                duration_minutes=70,
                token_cost=5.0,
            ),
            CourseModule(
                title="Emerging AI Architectures",
                description="Transformers, Mamba, mixture-of-experts, and beyond.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=80,
                token_cost=5.0,
            ),
        ],
    ),
    CourseLevel(
        level=9,
        name="AI Company Creation",
        focus="Turning AI prototypes into profitable enterprises",
        certification="DreamCo AI Founder Certificate",
        prerequisite_level=8,
        modules=[
            CourseModule(
                title="AI Company Strategy",
                description="Vision, positioning, and competitive moats for AI ventures.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=60,
                token_cost=3.0,
            ),
            CourseModule(
                title="Fundraising for AI Startups",
                description="VC landscape, pitch decks, and valuation for AI companies.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=70,
                token_cost=4.0,
            ),
            CourseModule(
                title="Building an AI Team",
                description="Roles, hiring, and org design for AI-first companies.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=55,
                token_cost=3.0,
            ),
            CourseModule(
                title="Scaling & Exit Strategies",
                description="Growth playbooks, M&A, and IPO preparation for AI firms.",
                teaching_modes=[MODE_VIDEO, MODE_SIMULATION],
                duration_minutes=65,
                token_cost=4.0,
            ),
        ],
    ),
    CourseLevel(
        level=10,
        name="AI Superintelligence Architecture",
        focus="Advanced architectures for multimodal and multi-agent AI systems",
        certification="DreamCo AI Master Certification",
        prerequisite_level=9,
        modules=[
            CourseModule(
                title="Advanced AI Architectures",
                description="Frontier model architectures and scaling laws.",
                teaching_modes=[MODE_VIDEO, MODE_READING, MODE_CODING_LAB],
                duration_minutes=120,
                token_cost=10.0,
            ),
            CourseModule(
                title="Multimodal AI Systems",
                description="Building systems that process text, image, audio, and video.",
                teaching_modes=[MODE_CODING_LAB, MODE_SIMULATION],
                duration_minutes=110,
                token_cost=10.0,
            ),
            CourseModule(
                title="AI Safety at Scale",
                description="Alignment research, interpretability, and red-teaming.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=90,
                token_cost=8.0,
            ),
            CourseModule(
                title="Future of AI & Society",
                description="Long-term AI trajectories, governance, and global impact.",
                teaching_modes=[MODE_VIDEO, MODE_READING],
                duration_minutes=75,
                token_cost=5.0,
            ),
        ],
    ),
]


class AICourseEngine:
    """Manages the 10-level DreamCo AI University course structure.

    Parameters
    ----------
    max_level : int
        Maximum level the current tier allows access to (1–10).
    """

    def __init__(self, max_level: int = 10) -> None:
        self._max_level = max(1, min(max_level, 10))
        self._levels: dict = {lvl.level: lvl for lvl in _COURSE_LEVELS}

    def get_level(self, level: int) -> Optional[CourseLevel]:
        """Return a course level if accessible, otherwise None."""
        if level not in self._levels:
            return None
        if level > self._max_level:
            return None
        return self._levels[level]

    def list_accessible_levels(self) -> List[CourseLevel]:
        """Return all levels accessible on the current tier."""
        return [self._levels[i] for i in range(1, self._max_level + 1)]

    def total_levels(self) -> int:
        """Return total number of levels in the engine (always 10)."""
        return len(self._levels)

    def get_certification(self, level: int) -> Optional[str]:
        """Return the certification name for a given level."""
        lvl = self._levels.get(level)
        return lvl.certification if lvl else None

    def list_all_teaching_modes(self) -> List[str]:
        """Return the list of all available teaching modes."""
        return list(ALL_MODES)
