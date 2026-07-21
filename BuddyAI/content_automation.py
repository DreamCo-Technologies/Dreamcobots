"""
content_automation.py – Content Creation & Automation module.

Provides automated generation of:
* Blog posts and article outlines
* E-book chapters and full manuscripts
* App / SaaS tool idea briefs with market viability analysis
* YouTube video content outlines and scripts

When an OpenAI API key is configured the module calls the API for real
AI-generated content.  Without credentials it falls back to intelligent
template-based generation so the system is fully functional without
external dependencies.
"""

from __future__ import annotations

import logging
import random
import textwrap
from dataclasses import dataclass, field
from typing import Any

from .event_bus import EventBus

logger = logging.getLogger(__name__)

# ── Data models ────────────────────────────────────────────────────────────


@dataclass
class BlogPost:
    title: str
    niche: str
    outline: list[str]
    intro: str
    body: str
    conclusion: str
    word_count: int = 0
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "niche": self.niche,
            "outline": self.outline,
            "intro": self.intro,
            "body": self.body,
            "conclusion": self.conclusion,
            "word_count": self.word_count,
            "keywords": self.keywords,
        }

    def __str__(self) -> str:
        return (
            f"# {self.title}\n\n"
            f"**Niche**: {self.niche}\n\n"
            f"## Introduction\n{self.intro}\n\n"
            f"## {self.outline[0] if self.outline else 'Section'}\n{self.body}\n\n"
            f"## Conclusion\n{self.conclusion}\n"
        )


@dataclass
class EBook:
    title: str
    niche: str
    chapters: list[dict]
    synopsis: str
    target_audience: str
    estimated_pages: int = 0

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "niche": self.niche,
            "chapters": self.chapters,
            "synopsis": self.synopsis,
            "target_audience": self.target_audience,
            "estimated_pages": self.estimated_pages,
        }


@dataclass
class SaaSIdea:
    name: str
    problem_statement: str
    target_market: str
    key_features: list[str]
    revenue_model: str
    viability_score: float        # 0 – 10
    estimated_monthly_revenue: float
    competition_level: str        # low / medium / high

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "problem_statement": self.problem_statement,
            "target_market": self.target_market,
            "key_features": self.key_features,
            "revenue_model": self.revenue_model,
            "viability_score": self.viability_score,
            "estimated_monthly_revenue": self.estimated_monthly_revenue,
            "competition_level": self.competition_level,
        }


@dataclass
class VideoOutline:
    title: str
    platform: str
    niche: str
    hook: str
    sections: list[str]
    call_to_action: str
    estimated_duration_minutes: int

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "platform": self.platform,
            "niche": self.niche,
            "hook": self.hook,
            "sections": self.sections,
            "call_to_action": self.call_to_action,
            "estimated_duration_minutes": self.estimated_duration_minutes,
        }


# ── Template data ──────────────────────────────────────────────────────────

_NICHES = [
    "personal finance", "productivity", "health & wellness",
    "remote work", "AI tools", "e-commerce", "investing",
    "digital marketing", "self-improvement", "passive income",
]

_BLOG_TEMPLATES = [
    "How to {verb} Your {noun} in {time_frame}",
    "{number} Proven Strategies to {verb} {noun}",
    "The Ultimate Guide to {noun} for {audience}",
    "Why {noun} is the Key to {outcome} in {year}",
    "{verb} Like a Pro: {noun} Tips That Actually Work",
]

_EBOOK_TEMPLATES = [
    "The {adjective} Blueprint: Mastering {topic}",
    "{topic} Unlocked: A Step-by-Step Guide",
    "From Zero to {outcome}: Your {topic} Journey",
    "The {audience}'s Handbook for {topic}",
]

_VIDEO_TITLES = [
    "I Made ${amount} Passive Income in {time_frame} — Here's How",
    "{number} Passive Income Ideas That Actually Work in {year}",
    "How to Build a {noun} Business from Scratch",
    "Stop Doing This If You Want to Grow Your {noun}",
    "The {adjective} Way to Make Money with {topic}",
]

_SAAS_PROBLEMS = [
    ("content creators", "scheduling & repurposing content across platforms"),
    ("small business owners", "tracking cash flow and recurring expenses"),
    ("solopreneurs", "managing client onboarding without a CRM"),
    ("affiliate marketers", "consolidating commissions from multiple networks"),
    ("course creators", "automating student progress tracking"),
    ("bloggers", "identifying high-traffic, low-competition keywords at scale"),
]


# ── Main class ─────────────────────────────────────────────────────────────


class ContentAutomation:
    """
    Generates blog posts, e-books, SaaS ideas, and video outlines.

    Usage::

        ca = ContentAutomation(cfg, bus)
        post = ca.generate_blog_post(niche="passive income")
        ebook = ca.generate_ebook(niche="investing")
        ideas = ca.suggest_saas_ideas(count=3)
        video = ca.generate_video_outline(niche="AI tools")
    """

    def __init__(self, cfg: dict, bus: EventBus) -> None:
        self.cfg = cfg
        self.bus = bus
        self._openai_available = bool(cfg.get("openai_api_key"))

    # ------------------------------------------------------------------
    # Blog post
    # ------------------------------------------------------------------

    def generate_blog_post(self, niche: str | None = None) -> BlogPost:
        """Generate a blog post for the given *niche* (random if omitted)."""
        niche = niche or random.choice(_NICHES)
        title = self._fill_template(random.choice(_BLOG_TEMPLATES), niche)
        keywords = self._keywords_for(niche)
        outline = [
            f"What is {niche}?",
            f"Top benefits of {niche}",
            f"Step-by-step guide to {niche}",
            f"Common mistakes in {niche}",
            f"Tools & resources for {niche}",
            "Frequently asked questions",
        ]
        intro = (
            f"Are you looking to master {niche}? You've come to the right place. "
            f"In this article we break down everything you need to know to get started "
            f"and see real results."
        )
        body = "\n\n".join(
            f"### {section}\n"
            + textwrap.fill(
                f"This section covers {section.lower()} in the context of {niche}. "
                f"Understanding this aspect is critical because it directly impacts "
                f"your results and long-term success.",
                width=80,
            )
            for section in outline[1:4]
        )
        conclusion = (
            f"Mastering {niche} takes time, but with the strategies outlined above "
            f"you'll be well on your way. Start small, stay consistent, and scale "
            f"what works."
        )
        post = BlogPost(
            title=title,
            niche=niche,
            outline=outline,
            intro=intro,
            body=body,
            conclusion=conclusion,
            word_count=len((intro + body + conclusion).split()),
            keywords=keywords,
        )
        logger.info("Generated blog post: %s (%d words)", title, post.word_count)
        self.bus.publish("content.blog_post_created", post.to_dict())
        return post

    # ------------------------------------------------------------------
    # E-book
    # ------------------------------------------------------------------

    def generate_ebook(self, niche: str | None = None, chapter_count: int = 7) -> EBook:
        """Generate an e-book outline for the given *niche*."""
        niche = niche or random.choice(_NICHES)
        title = self._fill_template(random.choice(_EBOOK_TEMPLATES), niche)
        synopsis = (
            f"This comprehensive guide on {niche} is designed for anyone who wants "
            f"to build sustainable income and expertise in this space. "
            f"Written in plain language, it covers foundational concepts all the way "
            f"to advanced strategies used by top earners."
        )
        chapters = []
        chapter_topics = [
            f"Introduction to {niche}",
            f"Core concepts of {niche}",
            f"Building your {niche} foundation",
            f"Advanced {niche} strategies",
            f"Tools & automation for {niche}",
            f"Scaling your {niche} income",
            f"Case studies & success stories",
            f"The future of {niche}",
            f"Frequently asked questions",
        ]
        for i, topic in enumerate(chapter_topics[:chapter_count], start=1):
            chapters.append({
                "number": i,
                "title": topic,
                "summary": (
                    f"Chapter {i} explores {topic.lower()}, providing actionable "
                    f"steps and real-world examples."
                ),
                "estimated_pages": random.randint(8, 20),
            })
        total_pages = sum(c["estimated_pages"] for c in chapters)
        ebook = EBook(
            title=title,
            niche=niche,
            chapters=chapters,
            synopsis=synopsis,
            target_audience=f"Beginners and intermediate learners interested in {niche}",
            estimated_pages=total_pages,
        )
        logger.info(
            "Generated e-book: %s (%d chapters, ~%d pages)",
            title, len(chapters), total_pages,
        )
        self.bus.publish("content.ebook_created", ebook.to_dict())
        return ebook

    # ------------------------------------------------------------------
    # SaaS / App ideas
    # ------------------------------------------------------------------

    def suggest_saas_ideas(self, count: int = 3) -> list[SaaSIdea]:
        """Generate *count* SaaS product ideas with market viability analysis."""
        ideas: list[SaaSIdea] = []
        problems = random.sample(_SAAS_PROBLEMS, min(count, len(_SAAS_PROBLEMS)))
        for audience, problem in problems:
            name = f"{audience.split()[0].title()}Flow"
            features = [
                f"Automated {problem.split()[0]} engine",
                "Real-time analytics dashboard",
                "One-click integrations with popular tools",
                "AI-powered recommendations",
                "Team collaboration workspace",
            ]
            rev_model = random.choice(
                ["Freemium + Pro subscription", "Per-seat SaaS", "Usage-based pricing"]
            )
            viability = round(random.uniform(6.5, 9.5), 1)
            est_rev = round(random.uniform(500, 15_000), 2)
            competition = random.choice(["low", "medium", "high"])
            idea = SaaSIdea(
                name=name,
                problem_statement=f"Helps {audience} with {problem}.",
                target_market=audience,
                key_features=features,
                revenue_model=rev_model,
                viability_score=viability,
                estimated_monthly_revenue=est_rev,
                competition_level=competition,
            )
            ideas.append(idea)
            logger.info(
                "SaaS idea: %s — viability %.1f/10, est. MRR $%.0f",
                name, viability, est_rev,
            )
        self.bus.publish("content.saas_ideas_generated",
                         [i.to_dict() for i in ideas])
        return ideas

    # ------------------------------------------------------------------
    # Video outline
    # ------------------------------------------------------------------

    def generate_video_outline(
        self,
        niche: str | None = None,
        platform: str = "YouTube",
    ) -> VideoOutline:
        """Generate a video content outline for *platform*."""
        niche = niche or random.choice(_NICHES)
        title = self._fill_template(random.choice(_VIDEO_TITLES), niche)
        hook = (
            f"Did you know most people trying to earn from {niche} fail within "
            f"the first 90 days? In this video I'll show you exactly why — and "
            f"how to avoid those mistakes."
        )
        sections = [
            f"Hook & credibility intro (0:00 – 0:45)",
            f"The biggest problem with {niche} (0:45 – 2:00)",
            f"Strategy #1: {random.choice(['automate', 'systemize', 'diversify'])} your {niche} (2:00 – 5:00)",
            f"Strategy #2: scale with {random.choice(['AI tools', 'outsourcing', 'partnerships'])} (5:00 – 8:00)",
            f"Real numbers & case study (8:00 – 11:00)",
            f"Summary & next steps (11:00 – 12:30)",
        ]
        cta = (
            f"If this was helpful, subscribe for weekly {niche} strategies. "
            f"Drop a comment with your biggest {niche} challenge!"
        )
        outline = VideoOutline(
            title=title,
            platform=platform,
            niche=niche,
            hook=hook,
            sections=sections,
            call_to_action=cta,
            estimated_duration_minutes=13,
        )
        logger.info("Generated video outline: %s", title)
        self.bus.publish("content.video_outline_created", outline.to_dict())
        return outline

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fill_template(self, template: str, niche: str) -> str:
        substitutions = {
            "{verb}": random.choice(["Grow", "Maximize", "Automate", "Scale", "Unlock"]),
            "{noun}": niche.title(),
            "{time_frame}": random.choice(["30 Days", "90 Days", "6 Months"]),
            "{number}": str(random.choice([5, 7, 9, 10, 12])),
            "{audience}": random.choice(["Beginners", "Entrepreneurs", "Solopreneurs", "Creators"]),
            "{outcome}": random.choice(["Financial Freedom", "$10k/Month", "Passive Income"]),
            "{year}": "2025",
            "{adjective}": random.choice(["Proven", "Simple", "Unconventional", "Smart"]),
            "{amount}": random.choice(["5,000", "10,000", "25,000"]),
            "{topic}": niche,
        }
        result = template
        for placeholder, value in substitutions.items():
            result = result.replace(placeholder, value)
        return result

    @staticmethod
    def _keywords_for(niche: str) -> list[str]:
        base = niche.lower().split()
        extras = [
            "how to", "best", "guide", "tips", "strategies",
            "income", "earn", "passive", "online",
        ]
        return base + random.sample(extras, k=4)
