"""
DreamCo Job Titles Bot — Main Entry Point

Composes all Job Titles sub-systems into a single tier-aware platform:

  • Job Titles Database  — 100+ job titles across 25+ industries
  • Job Bot Generator    — create and manage job-specific automation bots
  • Autonomous Trainer   — train humans & AI (face/object recognition, valuation)
  • Cost Justification   — explain costs autonomously and present payment options

Architecture:
    DreamCoBots
    │
    ├── buddybot
    │
    ├── job_titles_bot
    │     ├── job_titles_database
    │     ├── job_bot_generator
    │     ├── autonomous_trainer
    │     └── cost_justification
    │
    └── (other bots)

Usage
-----
    from bots.job_titles_bot import JobTitlesBot, Tier

    bot = JobTitlesBot(tier=Tier.PRO)
    results = bot.search_jobs("data analyst")
    for job in results:
        print(job.title, job.industry)

    # Generate a dedicated bot for any job
    job_bot = bot.generate_bot("Accountant")
    print(job_bot.chat("What can you do?"))

    # Valuate an item
    result = bot.valuate_item("1955 double-die penny", condition="excellent")
    print(result.estimated_value_usd)

    # Get cost justification
    report = bot.justify_cost("PRO upgrade", monthly_usd=49.0, savings_usd=200.0)
    print(bot.format_cost_report(report))
"""

from __future__ import annotations

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.job_titles_bot.tiers import Tier, get_bot_tier_info, get_tier_config, get_upgrade_path
from bots.job_titles_bot.job_titles_database import JobTitle, JobTitlesDatabase
from bots.job_titles_bot.job_bot_generator import GeneratedJobBot, JobBotGenerator
from bots.job_titles_bot.autonomous_trainer import (
    AutonomousTrainer,
    FaceRecord,
    ObjectRecord,
    ValuationResult,
    TrainingSession,
)
from bots.job_titles_bot.cost_justification import (
    CostJustificationEngine,
    CostItem,
    CostJustification,
)


class JobTitlesBotError(Exception):
    """Base error for JobTitlesBot."""


class JobTitlesBotTierError(JobTitlesBotError):
    """Raised when a feature is gated behind a higher tier."""


# Free-tier browse limit
_FREE_BROWSE_LIMIT = 50


class JobTitlesBot:
    """
    Tier-aware bot for job title search, workforce automation, training,
    and autonomous cost justification.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE, PRO, or ENTERPRISE).
    token_balance : int
        Initial DreamCo token balance for the account.
    """

    def __init__(self, tier: Tier = Tier.FREE, token_balance: int = 0) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)

        self._db = JobTitlesDatabase()
        self._generator = JobBotGenerator()
        self._trainer = AutonomousTrainer()
        self._cost_engine = CostJustificationEngine(token_balance=token_balance)

    # ── Tier info ────────────────────────────────────────────────────────────

    def describe_tier(self) -> str:
        """Return a human-readable description of the current tier."""
        info = get_bot_tier_info(self.tier)
        lines = [
            f"Job Titles Bot — {info['name']} Tier",
            f"Price : ${info['price_usd_monthly']:.2f}/month",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  • {f}")
        return "\n".join(lines)

    def get_upgrade_path(self) -> dict:
        """Return the upgrade options for the current tier."""
        return get_upgrade_path(self.tier)

    # ── Job search ───────────────────────────────────────────────────────────

    def search_jobs(self, query: str) -> list[JobTitle]:
        """
        Search for job titles matching *query*.

        Free tier is limited to 50 results; PRO/ENTERPRISE are unlimited.
        """
        results = self._db.search(query)
        if self.tier == Tier.FREE:
            return results[:_FREE_BROWSE_LIMIT]
        return results

    def browse_industry(self, industry: str) -> list[JobTitle]:
        """Return all job titles in *industry*."""
        results = self._db.by_industry(industry)
        if self.tier == Tier.FREE:
            return results[:_FREE_BROWSE_LIMIT]
        return results

    def list_industries(self) -> list[str]:
        """Return all available industry names."""
        industries = self._db.industries()
        if self.tier == Tier.FREE:
            return industries[:3]
        return industries

    def database_stats(self) -> dict:
        """Return statistics about the job titles database."""
        return self._db.stats()

    def get_job(self, title: str) -> JobTitle | None:
        """Look up a specific job title (exact match, case-insensitive)."""
        return self._db.get(title)

    def list_automatable_jobs(self, level: str = "full") -> list[JobTitle]:
        """
        Return jobs that can be automated at *level* ('full', 'partial', 'assisted').
        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise JobTitlesBotTierError(
                "Automation filtering requires PRO or ENTERPRISE tier. "
                f"Upgrade: {get_upgrade_path(self.tier)}"
            )
        return self._db.automatable(level)

    def list_bot_replaceable(self) -> list[JobTitle]:
        """Return all jobs that can be fully replaced by a DreamCo bot."""
        if self.tier == Tier.FREE:
            raise JobTitlesBotTierError(
                "Bot-replaceable job list requires PRO or ENTERPRISE tier."
            )
        return self._db.bot_replaceable()

    # ── Bot generation ───────────────────────────────────────────────────────

    def generate_bot(self, job_title: str) -> GeneratedJobBot:
        """
        Generate (or retrieve) a dedicated automation bot for *job_title*.
        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise JobTitlesBotTierError(
                "Bot generation requires PRO or ENTERPRISE tier."
            )
        job = self._db.get(job_title)
        if job is None:
            raise JobTitlesBotError(f"Job title '{job_title}' not found in the database.")
        return self._generator.generate(job)

    def generate_all_bots(self) -> list[GeneratedJobBot]:
        """Generate bots for every job title in the database. ENTERPRISE only."""
        if self.tier != Tier.ENTERPRISE:
            raise JobTitlesBotTierError("generate_all_bots requires ENTERPRISE tier.")
        return self._generator.generate_all(self._db.all_titles())

    def propagate_buddy_upgrade(self, new_version: str, extra_capabilities: list[str] | None = None) -> int:
        """
        Propagate a Buddy Bot upgrade to ALL generated job bots.
        Returns the number of bots upgraded.
        ENTERPRISE only.
        """
        if self.tier != Tier.ENTERPRISE:
            raise JobTitlesBotTierError("Buddy Bot propagation requires ENTERPRISE tier.")
        count = self._generator.propagate_upgrade(new_version, extra_capabilities)
        self._trainer.upgrade_module(new_version)
        return count

    # ── Training ─────────────────────────────────────────────────────────────

    def train(self, trainee: str, skill: str, duration_seconds: int = 60) -> TrainingSession:
        """
        Run a training session for *trainee* on *skill*.
        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise JobTitlesBotTierError("Training requires PRO or ENTERPRISE tier.")
        return self._trainer.run_training_session(trainee, skill, duration_seconds)

    def register_face(self, label: str, raw_encoding: bytes) -> FaceRecord:
        """Register a face for recognition. ENTERPRISE only."""
        if self.tier != Tier.ENTERPRISE:
            raise JobTitlesBotTierError("Face recognition requires ENTERPRISE tier.")
        return self._trainer.register_face(label, raw_encoding)

    def identify_face(self, raw_encoding: bytes) -> FaceRecord | None:
        """Identify a face from raw encoding. ENTERPRISE only."""
        if self.tier != Tier.ENTERPRISE:
            raise JobTitlesBotTierError("Face identification requires ENTERPRISE tier.")
        return self._trainer.identify_face(raw_encoding)

    def register_object(
        self, category: str, description: str, visual_keywords: list[str], value_usd: float = 0.0
    ) -> ObjectRecord:
        """Register an object for recognition. ENTERPRISE only."""
        if self.tier != Tier.ENTERPRISE:
            raise JobTitlesBotTierError("Object registration requires ENTERPRISE tier.")
        return self._trainer.register_object(category, description, visual_keywords, value_usd)

    def recognize_object(self, description: str) -> list[ObjectRecord]:
        """Recognize an object from a text description. Requires PRO or ENTERPRISE."""
        if self.tier == Tier.FREE:
            raise JobTitlesBotTierError("Object recognition requires PRO or ENTERPRISE tier.")
        return self._trainer.recognize_object(description)

    def valuate_item(self, item_description: str, condition: str = "good") -> ValuationResult:
        """
        Estimate the market value of a physical item.
        Requires PRO or ENTERPRISE tier.
        """
        if self.tier == Tier.FREE:
            raise JobTitlesBotTierError("Item valuation requires PRO or ENTERPRISE tier.")
        return self._trainer.valuate_item(item_description, condition)

    def trainer_stats(self) -> dict:
        """Return trainer activity statistics. Requires PRO or ENTERPRISE."""
        if self.tier == Tier.FREE:
            raise JobTitlesBotTierError("Trainer stats require PRO or ENTERPRISE tier.")
        return self._trainer.stats()

    # ── Cost justification ───────────────────────────────────────────────────

    def justify_cost(
        self,
        feature_name: str,
        monthly_usd: float,
        savings_usd: float,
        line_items: list[CostItem] | None = None,
    ) -> CostJustification:
        """
        Build an autonomous cost justification report.

        Parameters
        ----------
        feature_name : str
            The feature or upgrade being considered.
        monthly_usd : float
            Monthly cost in USD.
        savings_usd : float
            Estimated monthly savings / revenue generated.
        line_items : list[CostItem] | None
            Optional detailed line-item breakdown.
        """
        return self._cost_engine.justify(feature_name, monthly_usd, savings_usd, line_items)

    def format_cost_report(self, justification: CostJustification) -> str:
        """Return a formatted text version of *justification*."""
        return self._cost_engine.format_report(justification)

    def add_tokens(self, amount: int) -> int:
        """Add tokens to the account balance."""
        return self._cost_engine.add_tokens(amount)

    def deduct_tokens(self, amount: int) -> dict:
        """Deduct tokens from the account balance."""
        return self._cost_engine.deduct_tokens(amount)

    @property
    def token_balance(self) -> int:
        """Current DreamCo token balance."""
        return self._cost_engine.token_balance

    # ── BuddyAI chat interface ───────────────────────────────────────────────

    def chat(self, message: str) -> dict:
        """
        Respond to a natural-language message.  Compatible with BuddyBot.

        Parameters
        ----------
        message : str
            User or orchestrator message.

        Returns
        -------
        dict
            Response payload.
        """
        msg = message.lower()

        if "tier" in msg or "upgrade" in msg or "plan" in msg:
            reply = self.describe_tier()
        elif "search" in msg or "find job" in msg or "look up" in msg:
            query = message.split(":")[-1].strip() if ":" in message else message
            results = self._db.search(query)[:5]
            reply = (
                f"Found {len(results)} job(s) matching '{query}': "
                + ", ".join(j.title for j in results)
            ) if results else f"No jobs found matching '{query}'."
        elif "valuate" in msg or "value" in msg or "worth" in msg or "antique" in msg or "coin" in msg:
            reply = (
                "Item valuation is available on PRO and ENTERPRISE tiers. "
                "Send: valuate_item('<description>', condition='good') or upgrade your plan."
            )
        elif "cost" in msg or "price" in msg or "pay" in msg:
            justification = self._cost_engine.justify(
                "Job Titles Bot PRO", 49.0, 200.0
            )
            reply = self._cost_engine.format_report(justification)
        elif "train" in msg:
            reply = (
                "Training is available on PRO and ENTERPRISE tiers. "
                "I can train humans and AI for any job role, face recognition, "
                "and item valuation."
            )
        elif "robot" in msg or "hire" in msg or "employee" in msg:
            reply = (
                "DreamCo provides bots for every known job title. "
                "Use search_jobs() to find a role and generate_bot() to deploy "
                "an automation bot. Human hiring is also available via our marketplace."
            )
        elif "stats" in msg or "database" in msg:
            stats = self._db.stats()
            reply = (
                f"Database: {stats['total_titles']} titles across {stats['industries']} industries. "
                f"{stats['fully_automatable']} fully automatable, "
                f"{stats['bot_replaceable']} bot-replaceable."
            )
        else:
            reply = (
                "Welcome to DreamCo Job Titles Bot! I can help you: "
                "search job titles, generate automation bots for any role, "
                "train humans/AI, valuate items (antiques, coins, currency), "
                "and justify costs autonomously. What would you like to do?"
            )

        return {
            "bot_name": "job_titles_bot",
            "tier": self.tier.value,
            "reply": reply,
        }

    def register_with_buddy(self, buddy_bot_instance) -> None:
        """Register this bot with a BuddyBot orchestrator instance."""
        buddy_bot_instance.register_bot("job_titles_bot", self)


__all__ = [
    "JobTitlesBot",
    "JobTitlesBotError",
    "JobTitlesBotTierError",
    "Tier",
]
