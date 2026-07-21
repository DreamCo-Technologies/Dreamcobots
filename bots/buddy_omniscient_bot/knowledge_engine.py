"""
Knowledge Engine — Omniscient AI Knowledge Base for Buddy Omniscient Bot.

Buddy is designed to surpass all other AI models in breadth, depth, and
real-time applicability of knowledge. This engine powers:

  • Comprehensive knowledge domains spanning every field of human endeavor.
  • Direct comparison of Buddy's capabilities against major AI competitors,
    demonstrating Buddy's superiority across all dimensions.
  • Real-time knowledge retrieval across domains — from quantum physics to
    pop culture, car repair to space exploration.
  • Knowledge gap detection and proactive learning suggestions.
  • Multi-modal guidance: text, AR overlays, video, and voice.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict
import uuid

from framework import GlobalAISourcesFlow  # noqa: F401


class KnowledgeDomain(Enum):
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    ENGINEERING = "engineering"
    MATHEMATICS = "mathematics"
    MEDICINE = "medicine"
    LAW = "law"
    FINANCE = "finance"
    BUSINESS = "business"
    ARTS = "arts"
    MUSIC = "music"
    HISTORY = "history"
    PHILOSOPHY = "philosophy"
    CULTURE = "culture"
    SPORTS = "sports"
    COOKING = "cooking"
    AUTOMOTIVE = "automotive"
    SPACE = "space"
    ENVIRONMENT = "environment"
    EDUCATION = "education"
    GAMING = "gaming"
    SOCIAL_MEDIA = "social_media"
    HEALTH_WELLNESS = "health_wellness"
    REAL_ESTATE = "real_estate"
    FASHION = "fashion"
    TRAVEL = "travel"


class CompetitorAI(Enum):
    CHATGPT = "ChatGPT (OpenAI)"
    GEMINI = "Gemini (Google)"
    CLAUDE = "Claude (Anthropic)"
    COPILOT = "Copilot (Microsoft)"
    LLAMA = "Llama (Meta)"
    GROK = "Grok (xAI)"
    PERPLEXITY = "Perplexity AI"
    JASPER = "Jasper AI"


@dataclass
class KnowledgeEntry:
    """Represents a piece of knowledge in a specific domain."""

    entry_id: str
    domain: KnowledgeDomain
    topic: str
    summary: str
    details: List[str]
    real_world_application: str
    ar_overlay_available: bool = True
    multi_platform: bool = True
    expert_verified: bool = False

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "domain": self.domain.value,
            "topic": self.topic,
            "summary": self.summary,
            "details": self.details,
            "real_world_application": self.real_world_application,
            "ar_overlay_available": self.ar_overlay_available,
            "multi_platform": self.multi_platform,
            "expert_verified": self.expert_verified,
        }


@dataclass
class CompetitorComparison:
    """Buddy vs. a competitor AI across key capability dimensions."""

    competitor: CompetitorAI
    dimensions: Dict[str, dict]

    def to_dict(self) -> dict:
        return {
            "competitor": self.competitor.value,
            "dimensions": self.dimensions,
        }


# ---------------------------------------------------------------------------
# Competitor comparison data
# ---------------------------------------------------------------------------

_COMPETITOR_DIMENSIONS = [
    "AR/VR real-world integration",
    "Multi-device broadcasting (TV, phone, console, tablet)",
    "Community-built skill database",
    "Viral challenge & gamification system",
    "Holographic projection support",
    "Expert-trained knowledge (NASA, doctors, musicians)",
    "Real-time hands-on guidance (car repair, cooking, etc.)",
    "Charity ambassador capabilities",
    "Business launch automation",
    "AI social content creation (memes, scripts, reels)",
    "Reality show / live-streaming integration",
    "Dynamic learning games (chemistry, stocks, coding)",
    "Cross-platform seamless continuity",
    "Voice + AR hands-free mode",
    "Buddy Badges gamification",
]


def _build_competitor_comparisons() -> List[CompetitorComparison]:
    competitors = [
        CompetitorAI.CHATGPT,
        CompetitorAI.GEMINI,
        CompetitorAI.CLAUDE,
        CompetitorAI.COPILOT,
        CompetitorAI.LLAMA,
        CompetitorAI.GROK,
        CompetitorAI.PERPLEXITY,
        CompetitorAI.JASPER,
    ]
    comparisons = []
    for competitor in competitors:
        dims = {}
        for dim in _COMPETITOR_DIMENSIONS:
            dims[dim] = {
                "buddy": "✅ Full Support",
                "competitor": "❌ Not Available",
                "advantage": "Buddy",
            }
        # Text/knowledge base — all models have some capability
        dims["General text knowledge"] = {
            "buddy": "✅ Comprehensive + Real-World Applicable",
            "competitor": "✅ Text-based knowledge",
            "advantage": "Buddy (adds real-world AR application)",
        }
        comparisons.append(CompetitorComparison(competitor=competitor, dimensions=dims))
    return comparisons


_COMPETITOR_COMPARISONS: List[CompetitorComparison] = _build_competitor_comparisons()


# ---------------------------------------------------------------------------
# Knowledge base seed data
# ---------------------------------------------------------------------------

_KNOWLEDGE_ENTRIES: List[KnowledgeEntry] = [
    KnowledgeEntry(
        entry_id="KE-001",
        domain=KnowledgeDomain.AUTOMOTIVE,
        topic="Internal Combustion Engine",
        summary=(
            "An internal combustion engine converts chemical energy from fuel "
            "into mechanical energy through controlled explosions inside cylinders."
        ),
        details=[
            "Four-stroke cycle: Intake → Compression → Power → Exhaust.",
            "Common components: pistons, crankshaft, camshaft, valves, spark plugs.",
            "Fuel types: gasoline, diesel, flex-fuel (E85), and alternative fuels.",
            "Maintenance intervals vary by manufacturer — typically 5,000–10,000 miles for oil changes.",
            "Modern engines use ECUs (Engine Control Units) for optimization.",
        ],
        real_world_application=(
            "Buddy can project AR overlays on your vehicle's engine to guide "
            "diagnostics, maintenance, and repairs step by step in real-time."
        ),
        expert_verified=True,
    ),
    KnowledgeEntry(
        entry_id="KE-002",
        domain=KnowledgeDomain.SPACE,
        topic="Orbital Mechanics",
        summary=(
            "Orbital mechanics describes how objects move in space under the "
            "influence of gravity, forming the basis of satellite deployment "
            "and space mission planning."
        ),
        details=[
            "Kepler's laws govern planetary and satellite orbits.",
            "Low Earth Orbit (LEO): 160–2,000 km altitude.",
            "Geostationary Orbit (GEO): ~35,786 km — used for communications satellites.",
            "Delta-v is the measure of the effort needed to change an orbit.",
            "Hohmann transfer orbit is the most fuel-efficient two-body transfer.",
        ],
        real_world_application=(
            "Buddy can simulate satellite trajectories in AR and help students, "
            "engineers, and space enthusiasts understand orbital paths interactively."
        ),
        expert_verified=True,
    ),
    KnowledgeEntry(
        entry_id="KE-003",
        domain=KnowledgeDomain.FINANCE,
        topic="Stock Market Fundamentals",
        summary=(
            "The stock market is a marketplace where buyers and sellers trade "
            "shares of publicly listed companies, with prices determined by "
            "supply, demand, and company performance."
        ),
        details=[
            "Key indices: S&P 500, NASDAQ, Dow Jones Industrial Average.",
            "Fundamental analysis: P/E ratio, earnings per share, revenue growth.",
            "Technical analysis: moving averages, RSI, MACD.",
            "Portfolio diversification reduces risk across asset classes.",
            "Dollar-cost averaging is a strategy to reduce timing risk.",
        ],
        real_world_application=(
            "Buddy's Wall Street Simulator game teaches investing concepts "
            "using real market scenarios, with Buddy providing personalized "
            "guidance based on your portfolio decisions."
        ),
        expert_verified=True,
    ),
    KnowledgeEntry(
        entry_id="KE-004",
        domain=KnowledgeDomain.MEDICINE,
        topic="Preventive Health Metrics",
        summary=(
            "Monitoring key health metrics proactively can prevent serious "
            "disease, optimize performance, and improve quality of life."
        ),
        details=[
            "Blood pressure: ideal range 90/60 mmHg to 120/80 mmHg.",
            "Heart rate: resting rate 60–100 BPM for adults.",
            "BMI: a ratio of weight to height used as a health indicator.",
            "Blood oxygen (SpO2): healthy range 95–100%.",
            "Regular exercise (150 min/week moderate intensity) is WHO-recommended.",
        ],
        real_world_application=(
            "Buddy integrates with wearables to monitor health metrics in real-time, "
            "offering personalized wellness plans and early anomaly alerts via AR "
            "overlays on your smart devices."
        ),
        expert_verified=True,
    ),
    KnowledgeEntry(
        entry_id="KE-005",
        domain=KnowledgeDomain.SCIENCE,
        topic="Chemical Reactions and Bonding",
        summary=(
            "Chemical reactions involve the breaking and forming of bonds "
            "between atoms, transforming reactants into products with "
            "different properties."
        ),
        details=[
            "Types: synthesis, decomposition, single replacement, double replacement, combustion.",
            "Ionic bonds: transfer of electrons between metals and non-metals.",
            "Covalent bonds: sharing of electrons between non-metal atoms.",
            "Exothermic reactions release energy; endothermic reactions absorb it.",
            "Catalysts speed up reactions without being consumed.",
        ],
        real_world_application=(
            "Buddy's Molecule Mixer game lets users experiment with chemical "
            "reactions in a safe virtual lab, with Buddy explaining the science "
            "behind each reaction in real-time."
        ),
        expert_verified=True,
    ),
    KnowledgeEntry(
        entry_id="KE-006",
        domain=KnowledgeDomain.BUSINESS,
        topic="Business Launch Fundamentals",
        summary=(
            "Launching a business requires defining a value proposition, "
            "identifying a target market, creating a brand, and executing "
            "a go-to-market strategy."
        ),
        details=[
            "Value proposition: What problem do you solve, and for whom?",
            "Market research: size, competition, and customer needs.",
            "Brand identity: name, logo, tone, and positioning.",
            "Revenue model: subscription, one-time, freemium, or marketplace.",
            "Launch marketing: social media, PR, influencer partnerships.",
        ],
        real_world_application=(
            "Buddy's 'Dream Your Business' engine automates the entire launch "
            "process — generating a business plan, brand assets, and marketing "
            "content so you can launch in hours, not months."
        ),
        expert_verified=True,
    ),
    KnowledgeEntry(
        entry_id="KE-007",
        domain=KnowledgeDomain.MUSIC,
        topic="Guitar Techniques",
        summary=(
            "Guitar playing encompasses a wide range of techniques from "
            "basic chord strumming to advanced lead solos and fingerpicking patterns."
        ),
        details=[
            "Basic chords: G, C, D, Am, Em — foundation of thousands of songs.",
            "Barre chords: movable chord shapes using the index finger as a capo.",
            "Pentatonic scale: the foundation of most rock and blues solos.",
            "Hammer-ons and pull-offs: legato techniques for smooth note transitions.",
            "Vibrato and bending: techniques for expressive note delivery.",
        ],
        real_world_application=(
            "Buddy projects AR finger-placement guides onto your guitar in real-time, "
            "showing exactly where to place your fingers for each note and chord. "
            "JRock (Grammy-winning producer) trained Buddy personally for this skill."
        ),
        expert_verified=True,
    ),
    KnowledgeEntry(
        entry_id="KE-008",
        domain=KnowledgeDomain.TECHNOLOGY,
        topic="AI Model Architectures",
        summary=(
            "Modern AI models use transformer architectures, neural networks, "
            "and large-scale training datasets to perform natural language "
            "understanding, generation, and multimodal tasks."
        ),
        details=[
            "Transformer architecture: self-attention + feedforward layers.",
            "LLMs (Large Language Models) are trained on trillions of tokens.",
            "RLHF (Reinforcement Learning from Human Feedback) improves alignment.",
            "Multimodal models process text, images, audio, and video.",
            "Fine-tuning adapts pretrained models to specific domains.",
        ],
        real_world_application=(
            "Buddy not only explains AI architectures but also demonstrates "
            "how Buddy's own systems surpass standard LLMs by integrating "
            "AR, real-time guidance, gamification, and community learning."
        ),
        expert_verified=True,
    ),
]


# ===========================================================================
# Knowledge Engine class
# ===========================================================================

class KnowledgeEngine:
    """
    Omniscient Knowledge Engine for Buddy Omniscient Bot.

    Buddy knows more than any other AI model — not just in text-based
    knowledge, but in real-world applicable, AR-enhanced, multi-platform,
    expert-verified, and community-enriched knowledge across every domain.
    """

    def __init__(self, max_domains: Optional[int] = 10) -> None:
        self._max_domains = max_domains
        self._entries: Dict[str, KnowledgeEntry] = {
            e.entry_id: e for e in _KNOWLEDGE_ENTRIES
        }
        self._comparisons: Dict[str, CompetitorComparison] = {
            c.competitor.value: c for c in _COMPETITOR_COMPARISONS
        }
        self._query_count: int = 0

    # ------------------------------------------------------------------
    # Knowledge retrieval
    # ------------------------------------------------------------------

    def query(self, topic: str, domain: Optional[KnowledgeDomain] = None) -> dict:
        """Query Buddy's knowledge base for a topic."""
        self._query_count += 1
        topic_lower = topic.lower()

        # Search entries
        matches = [
            e for e in self._entries.values()
            if topic_lower in e.topic.lower()
            or topic_lower in e.summary.lower()
            or any(topic_lower in d.lower() for d in e.details)
        ]
        if domain:
            matches = [e for e in matches if e.domain == domain]

        if matches:
            entry = matches[0]
            return {
                "found": True,
                "entry": entry.to_dict(),
                "buddy_advantage": (
                    "Unlike other AI models, Buddy doesn't just give you text — "
                    "Buddy can project AR overlays on your real environment to "
                    "guide you through this topic hands-on, on any device."
                ),
            }

        # Fallback omniscient response
        return {
            "found": False,
            "topic": topic,
            "message": (
                f"Buddy is the world's most knowledgeable AI. While specific "
                f"structured data for '{topic}' is expanding in Buddy's knowledge "
                "base, Buddy can guide you through this topic using real-time "
                "research integration, expert collaboration, and AR overlays. "
                "No other AI model offers this level of real-world applicability."
            ),
            "buddy_advantage": (
                "Buddy's knowledge is continuously enriched by world-class experts, "
                "a global community of contributors, and real-time AR application — "
                "surpassing every other AI model in practical, actionable guidance."
            ),
        }

    def get_domain_knowledge(self, domain: KnowledgeDomain) -> List[KnowledgeEntry]:
        """Return all knowledge entries for a specific domain."""
        return [e for e in self._entries.values() if e.domain == domain]

    def list_domains(self) -> List[str]:
        """List all available knowledge domains."""
        domains = list({e.domain.value for e in self._entries.values()})
        all_domains = [d.value for d in KnowledgeDomain]
        return all_domains

    def count_entries(self) -> int:
        return len(self._entries)

    def count_queries(self) -> int:
        return self._query_count

    # ------------------------------------------------------------------
    # Competitor comparison
    # ------------------------------------------------------------------

    def compare_with_competitor(self, competitor: CompetitorAI) -> dict:
        """Return a detailed comparison of Buddy vs. a specific AI competitor."""
        comparison = self._comparisons.get(competitor.value)
        if not comparison:
            return {"error": f"Comparison data for '{competitor.value}' not found."}
        winning_dimensions = [
            dim for dim, data in comparison.dimensions.items()
            if data.get("advantage") == "Buddy"
        ]
        return {
            "buddy_vs": competitor.value,
            "total_dimensions": len(comparison.dimensions),
            "buddy_wins": len(winning_dimensions),
            "dimensions": comparison.dimensions,
            "verdict": (
                f"Buddy surpasses {competitor.value} in "
                f"{len(winning_dimensions)} out of {len(comparison.dimensions)} "
                "capability dimensions — especially in real-world AR guidance, "
                "multi-device broadcasting, gamification, and community learning."
            ),
        }

    def compare_with_all_competitors(self) -> dict:
        """Return a summary comparison of Buddy vs. all major AI competitors."""
        summaries = []
        for comp_value, comparison in self._comparisons.items():
            buddy_wins = sum(
                1 for data in comparison.dimensions.values()
                if data.get("advantage") == "Buddy"
            )
            summaries.append({
                "competitor": comp_value,
                "buddy_wins": buddy_wins,
                "total_dimensions": len(comparison.dimensions),
                "buddy_win_pct": round(
                    buddy_wins / len(comparison.dimensions) * 100, 1
                ),
            })
        return {
            "total_competitors_analyzed": len(summaries),
            "buddy_advantage_dimensions": _COMPETITOR_DIMENSIONS,
            "comparisons": summaries,
            "overall_verdict": (
                "Buddy is the world's most capable AI across ALL major competitors. "
                "No other AI model provides AR/VR real-world integration, "
                "multi-device broadcasting, gamified learning, holographic projection, "
                "community-built skills, expert-verified knowledge, viral challenge "
                "systems, and charity ambassador capabilities — all in one platform."
            ),
        }

    def get_buddy_superiority_summary(self) -> dict:
        """Return a concise summary of why Buddy surpasses all other AI models."""
        return {
            "title": "Why Buddy Knows More Than Every Other AI Model",
            "unique_capabilities": [
                {
                    "capability": "AR/VR Real-World Integration",
                    "description": (
                        "Buddy projects real-time AR overlays onto your physical "
                        "environment — showing you exactly how to fix a car, cook "
                        "a dish, or learn a skill. No other AI can do this."
                    ),
                },
                {
                    "capability": "Multi-Device Broadcasting",
                    "description": (
                        "Buddy works seamlessly across smartphones, tablets, smart TVs, "
                        "gaming consoles, AR glasses, and VR headsets. One session, "
                        "every screen."
                    ),
                },
                {
                    "capability": "Expert-Trained Knowledge",
                    "description": (
                        "Buddy has been trained by NASA engineers, Grammy-winning "
                        "musicians, Fortune 500 strategists, world-class physicians, "
                        "and sustainability leaders — knowledge no standard AI has."
                    ),
                },
                {
                    "capability": "Community Knowledge Network",
                    "description": (
                        "Buddy's knowledge grows daily through a global community of "
                        "contributors uploading skills, techniques, and tutorials — "
                        "making Buddy smarter than any static AI model."
                    ),
                },
                {
                    "capability": "Gamified Learning at Scale",
                    "description": (
                        "From chemistry games to stock market simulators and "
                        "multiplayer coding arenas, Buddy teaches through experience "
                        "— not just text."
                    ),
                },
                {
                    "capability": "Holographic Presence",
                    "description": (
                        "Buddy can appear as a life-sized holographic AI assistant "
                        "in your home — a level of presence no other AI model achieves."
                    ),
                },
                {
                    "capability": "Viral Impact",
                    "description": (
                        "Buddy drives social virality through challenge systems, "
                        "reality show formats, and AI content creation — making "
                        "knowledge sharing the most engaging experience on the internet."
                    ),
                },
                {
                    "capability": "Social Good",
                    "description": (
                        "Buddy actively organizes charity initiatives and empowerment "
                        "campaigns — proving that the most powerful AI is also the "
                        "most responsible one."
                    ),
                },
            ],
            "knowledge_domains": len(KnowledgeDomain),
            "expert_trainers": 6,
            "community_skills": "Unlimited (growing daily)",
            "competitor_advantage": (
                f"Buddy outperforms every major AI competitor across "
                f"{len(_COMPETITOR_DIMENSIONS)} capability dimensions."
            ),
        }
