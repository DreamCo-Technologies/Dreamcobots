"""
Job Bot Generator — Creates and manages job-specific bot templates.

Each generated bot is a lightweight object that inherits the core
DreamCo automation pipeline and is pre-configured for a specific job role.
Bots expose a ``chat()`` method so they can be registered with BuddyBot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401
from bots.job_titles_bot.job_titles_database import JobTitle


# ---------------------------------------------------------------------------
# Generated bot data class
# ---------------------------------------------------------------------------

@dataclass
class GeneratedJobBot:
    """
    A lightweight bot object generated for a specific job role.

    Attributes
    ----------
    job_title : str
        The job title this bot is configured for.
    industry : str
        Industry category.
    capabilities : list[str]
        Actions this bot can perform autonomously.
    automation_level : str
        'full' | 'partial' | 'assisted'
    is_active : bool
        Whether the bot is currently deployed.
    version : str
        Bot template version (bumped on every Buddy Bot upgrade).
    """

    job_title: str
    industry: str
    capabilities: list[str]
    automation_level: str
    is_active: bool = True
    version: str = "1.0.0"
    metadata: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # BuddyAI-compatible interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Respond to a chat message as this job bot.

        Parameters
        ----------
        message : str
            Incoming text from a user or orchestrator.

        Returns
        -------
        dict
            Response payload including bot identity and reply text.
        """
        msg = message.lower()
        if "capabilities" in msg or "what can you do" in msg:
            reply = (
                f"I am the {self.job_title} bot. "
                f"I can: {', '.join(self.capabilities)}."
            )
        elif "status" in msg:
            reply = f"{self.job_title} bot is {'active' if self.is_active else 'inactive'} (v{self.version})."
        elif "automate" in msg or "replace" in msg:
            reply = (
                f"This role has {self.automation_level} automation coverage. "
                "DreamCo bots can handle the repetitive portions so humans focus on high-value work."
            )
        elif "upgrade" in msg:
            reply = f"Upgrade request received. Current version: {self.version}. Buddy Bot will propagate the latest features automatically."
        else:
            reply = (
                f"Hello! I am the DreamCo {self.job_title} bot for the {self.industry} industry. "
                f"Ask me about capabilities, automation, hiring, or upgrades."
            )
        return {
            "bot_name": f"job_bot_{self.job_title.lower().replace(' ', '_')}",
            "job_title": self.job_title,
            "industry": self.industry,
            "reply": reply,
            "version": self.version,
        }

    def describe(self) -> dict:
        """Return a full description dict for marketplace/UI display."""
        return {
            "job_title": self.job_title,
            "industry": self.industry,
            "capabilities": self.capabilities,
            "automation_level": self.automation_level,
            "is_active": self.is_active,
            "version": self.version,
            **self.metadata,
        }

    def upgrade(self, new_version: str, additional_capabilities: Optional[list[str]] = None) -> None:
        """
        Upgrade this bot to *new_version*, optionally adding capabilities.
        Called automatically by Buddy Bot when global features are improved.
        """
        self.version = new_version
        if additional_capabilities:
            for cap in additional_capabilities:
                if cap not in self.capabilities:
                    self.capabilities.append(cap)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class JobBotGenerator:
    """
    Factory that creates ``GeneratedJobBot`` instances from ``JobTitle`` entries.

    Usage
    -----
        from bots.job_titles_bot.job_bot_generator import JobBotGenerator
        from bots.job_titles_bot.job_titles_database import JobTitlesDatabase

        db  = JobTitlesDatabase()
        gen = JobBotGenerator()
        bot = gen.generate(db.get("Data Analyst"))
    """

    # Default template version applied to all freshly generated bots
    CURRENT_VERSION: str = "1.0.0"

    def __init__(self) -> None:
        self._registry: dict[str, GeneratedJobBot] = {}

    # ── Core generation ──────────────────────────────────────────────────────

    def generate(self, job: JobTitle) -> GeneratedJobBot:
        """
        Create a new bot for *job*.  Re-returns the cached instance if the
        same title has already been generated.
        """
        key = job.title.lower()
        if key in self._registry:
            return self._registry[key]

        capabilities = self._build_capabilities(job)
        bot = GeneratedJobBot(
            job_title=job.title,
            industry=job.industry,
            capabilities=capabilities,
            automation_level=job.automation_level,
            version=self.CURRENT_VERSION,
            metadata={
                "avg_salary_usd": job.avg_salary_usd,
                "required_skills": list(job.required_skills),
                "replaceable_by_bot": job.replaceable_by_bot,
            },
        )
        self._registry[key] = bot
        return bot

    def generate_all(self, jobs: list[JobTitle]) -> list[GeneratedJobBot]:
        """Generate bots for a list of job titles."""
        return [self.generate(j) for j in jobs]

    # ── Registry helpers ─────────────────────────────────────────────────────

    def get(self, title: str) -> Optional[GeneratedJobBot]:
        """Look up a previously generated bot by job title (case-insensitive)."""
        return self._registry.get(title.lower())

    def list_generated(self) -> list[str]:
        """Return sorted list of generated bot titles."""
        return sorted(self._registry.keys())

    def count(self) -> int:
        """Number of generated bots in the registry."""
        return len(self._registry)

    # ── Bulk upgrades ────────────────────────────────────────────────────────

    def propagate_upgrade(
        self,
        new_version: str,
        additional_capabilities: Optional[list[str]] = None,
    ) -> int:
        """
        Propagate a version upgrade across ALL registered bots.
        Called by Buddy Bot when global AI features are improved.

        Returns
        -------
        int
            Number of bots upgraded.
        """
        for bot in self._registry.values():
            bot.upgrade(new_version, additional_capabilities)
        return len(self._registry)

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _build_capabilities(job: JobTitle) -> list[str]:
        """
        Build an initial capability list from the job's responsibilities
        plus universal DreamCo bot capabilities.
        """
        capabilities = list(job.responsibilities)
        # Append universal DreamCo capabilities
        universal = [
            "autonomous task scheduling",
            "cost justification reporting",
            "token billing integration",
            "Buddy Bot upgrade propagation",
        ]
        for cap in universal:
            if cap not in capabilities:
                capabilities.append(cap)
        # Add automation-level-specific capabilities
        if job.automation_level == "full":
            capabilities.append("24/7 unmanned operation")
        elif job.automation_level == "partial":
            capabilities.append("human-in-the-loop handoff")
        else:  # assisted
            capabilities.append("AI recommendation engine")
        return capabilities


__all__ = ["GeneratedJobBot", "JobBotGenerator"]
