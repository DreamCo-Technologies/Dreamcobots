"""
Big Bro AI — Interactive Gamified Dashboard

Implements the full gamified experience as described in the Big Bro AI
Empire concept:

  • XP & Level progression
  • Achievement system (unlockable badges)
  • Bot Idea Manager (generate, rank, track)
  • Hustle Simulator (revenue/profit simulation)
  • Code Gladiator (challenge-based skill games)
  • Bot Speed Control
  • Real-time Big Bro motivational commentary
  • Progress bar rendering

Can be used standalone or composed within the BigBroAI platform.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------

def progress_bar(value: int, total: int = 100, width: int = 20) -> str:
    """Return an ASCII progress bar string.

    Example: ``[████████────────────]  40%``
    """
    value = max(0, min(value, total))
    filled = round((value / total) * width) if total > 0 else 0
    bar = "█" * filled + "─" * (width - filled)
    pct = round(value / total * 100) if total > 0 else 0
    return f"[{bar}] {pct:3d}%"


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

@dataclass
class Achievement:
    name: str
    description: str
    unlocked: bool = False
    unlocked_at: Optional[str] = None

    def unlock(self) -> bool:
        """Unlock this achievement. Returns True if newly unlocked."""
        if not self.unlocked:
            self.unlocked = True
            self.unlocked_at = datetime.now(timezone.utc).isoformat()
            return True
        return False


_DEFAULT_ACHIEVEMENTS = [
    ("First Hustle", "Run your first Hustle Simulator session."),
    ("Code Warrior", "Win your first Code Gladiator challenge."),
    ("Bot Creator", "Generate your first new bot idea."),
    ("Empire Builder", "Generate 10 or more bot ideas."),
    ("XP Machine", "Reach Level 5."),
    ("Speed Demon", "Set bot speed to Aggressive."),
    ("Big Bro Approved", "Earn 500 total XP."),
    ("Fleet Commander", "Have 10 or more bot ideas in your fleet."),
]


# ---------------------------------------------------------------------------
# Bot Idea
# ---------------------------------------------------------------------------

@dataclass
class BotIdea:
    name: str
    profit_per_day_usd: float
    usage_pct: float
    category: str = "general"
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Bot Speed
# ---------------------------------------------------------------------------

class BotSpeed(Enum):
    SLOW = "slow"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

    @property
    def xp_multiplier(self) -> float:
        return {"slow": 0.5, "moderate": 1.0, "aggressive": 1.5}[self.value]

    @property
    def profit_multiplier(self) -> float:
        return {"slow": 0.7, "moderate": 1.0, "aggressive": 1.3}[self.value]


# ---------------------------------------------------------------------------
# Interactive Dashboard
# ---------------------------------------------------------------------------

class InteractiveDashboard:
    """
    Big Bro AI Interactive Gamified Dashboard.

    Manages XP, level, achievements, bot ideas, hustle simulations,
    code gladiator challenges, and bot speed control.  Designed as a
    self-contained game loop that can render to any output stream.
    """

    # Pre-loaded bot ideas from the Big Bro empire concept
    STARTER_BOT_IDEAS = [
        BotIdea("AI Content Bot", 120.0, 50.0, "content"),
        BotIdea("Auto Reseller Bot", 240.0, 70.0, "ecommerce"),
        BotIdea("Lead Finder Bot", 180.0, 65.0, "marketing"),
    ]

    # Pool of ideas for random generation
    IDEA_POOL = [
        ("AI YouTube Script Bot", 150.0, "content"),
        ("Auto Meme Generator", 80.0, "content"),
        ("Affiliate Marketing Bot", 200.0, "marketing"),
        ("Stock News Analyzer Bot", 130.0, "finance"),
        ("Social Media Growth Bot", 110.0, "marketing"),
        ("Crypto Signal Bot", 300.0, "finance"),
        ("Email Outreach Bot", 90.0, "sales"),
        ("Freelance Bid Bot", 140.0, "sales"),
        ("SEO Keyword Bot", 170.0, "seo"),
        ("Drop-Shipping Bot", 260.0, "ecommerce"),
        ("Review Monitor Bot", 60.0, "analytics"),
        ("Invoice Generator Bot", 75.0, "finance"),
        ("Cold DM Bot", 95.0, "sales"),
        ("Podcast Transcriber Bot", 55.0, "content"),
        ("Ad Spy Bot", 120.0, "marketing"),
    ]

    BIG_BRO_MESSAGES = [
        "Stay sharp. Build smarter than everybody else.",
        "They might laugh today but they'll copy tomorrow.",
        "You're building an empire. Keep going.",
        "Short kings run tech empires too.",
        "Every bot you build is a 24/7 employee that never calls in sick.",
        "The grind is just the beginning. The system is the goal.",
        "Level up or get left behind. Simple as that.",
        "One bot today. Ten tomorrow. Empire next year.",
    ]

    def __init__(self) -> None:
        self.xp: int = 0
        self.level: int = 1
        self.bot_speed: BotSpeed = BotSpeed.MODERATE
        self._achievements: dict[str, Achievement] = {
            name: Achievement(name=name, description=desc)
            for name, desc in _DEFAULT_ACHIEVEMENTS
        }
        self.bot_ideas: list[BotIdea] = list(self.STARTER_BOT_IDEAS)
        self._hustle_history: list = []
        self._gladiator_history: list = []

    # ------------------------------------------------------------------
    # XP & Level
    # ------------------------------------------------------------------

    def add_xp(self, amount: int) -> dict:
        """Award XP and check for level-up."""
        scaled = max(1, round(amount * self.bot_speed.xp_multiplier))
        self.xp += scaled
        leveled_up = self._check_level()
        self._check_achievement_triggers()
        return {
            "xp_earned": scaled,
            "total_xp": self.xp,
            "level": self.level,
            "leveled_up": leveled_up,
            "xp_to_next_level": self._xp_to_next(),
        }

    def _check_level(self) -> bool:
        new_level = max(1, self.xp // 100 + 1)
        if new_level > self.level:
            self.level = new_level
            return True
        return False

    def _xp_to_next(self) -> int:
        return self.level * 100 - self.xp

    # ------------------------------------------------------------------
    # Achievements
    # ------------------------------------------------------------------

    def _check_achievement_triggers(self) -> None:
        if self.xp >= 500:
            self._unlock("Big Bro Approved")
        if self.level >= 5:
            self._unlock("XP Machine")
        if len(self.bot_ideas) >= 10:
            self._unlock("Fleet Commander")

    def _unlock(self, name: str) -> Optional[Achievement]:
        ach = self._achievements.get(name)
        if ach and ach.unlock():
            return ach
        return None

    def unlock_achievement(self, name: str) -> dict:
        """Manually unlock a named achievement."""
        ach = self._achievements.get(name)
        if not ach:
            return {"status": "not_found", "name": name}
        newly_unlocked = ach.unlock()
        return {
            "name": name,
            "unlocked": ach.unlocked,
            "newly_unlocked": newly_unlocked,
            "unlocked_at": ach.unlocked_at,
        }

    def get_achievements(self) -> list:
        """Return all achievements with their status."""
        return [
            {
                "name": a.name,
                "description": a.description,
                "unlocked": a.unlocked,
                "unlocked_at": a.unlocked_at,
                "icon": "🏆" if a.unlocked else "🔒",
            }
            for a in self._achievements.values()
        ]

    # ------------------------------------------------------------------
    # Hustle Simulator
    # ------------------------------------------------------------------

    def hustle_simulator(self) -> dict:
        """
        Simulate a business hustle session.

        Returns random revenue/profit figures influenced by bot speed.
        Awards XP and unlocks the 'First Hustle' achievement.
        """
        base_revenue = random.randint(100, 500)
        revenue = round(base_revenue * self.bot_speed.profit_multiplier)
        profit = round(revenue * 0.4)
        xp_result = self.add_xp(25)
        self._unlock("First Hustle")

        result = {
            "module": "Hustle Simulator",
            "revenue_usd": revenue,
            "profit_usd": profit,
            "profit_margin_pct": 40.0,
            "bot_speed": self.bot_speed.value,
            "xp_earned": xp_result["xp_earned"],
            "big_bro_says": self.big_bro_message(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._hustle_history.append(result)
        return result

    def get_hustle_history(self) -> list:
        return list(self._hustle_history)

    # ------------------------------------------------------------------
    # Code Gladiator
    # ------------------------------------------------------------------

    def code_gladiator_challenge(self) -> dict:
        """
        Generate a Code Gladiator challenge.

        Returns a challenge dict with the secret answer hidden.
        Call ``submit_gladiator_answer()`` with the challenge_id to submit.
        """
        secret = random.randint(0, 9)
        challenge_id = f"cg_{len(self._gladiator_history) + 1:04d}"
        challenge = {
            "challenge_id": challenge_id,
            "question": "Guess the number between 0 and 9 (inclusive).",
            "hint": "Big Bro picked a single digit. Trust your instincts.",
            "_secret": secret,
        }
        self._gladiator_history.append({"challenge_id": challenge_id, "secret": secret, "submitted": False})
        return {k: v for k, v in challenge.items() if not k.startswith("_")}

    def submit_gladiator_answer(self, challenge_id: str, guess: int) -> dict:
        """Submit an answer to a Code Gladiator challenge."""
        record = next((r for r in self._gladiator_history if r["challenge_id"] == challenge_id), None)
        if not record:
            return {"status": "not_found", "challenge_id": challenge_id}
        if record["submitted"]:
            return {"status": "already_submitted", "challenge_id": challenge_id}

        record["submitted"] = True
        correct = guess == record["secret"]
        record["correct"] = correct
        record["guess"] = guess

        if correct:
            xp_result = self.add_xp(40)
            self._unlock("Code Warrior")
            return {
                "result": "victory",
                "message": "🔥 Correct! You win the duel.",
                "xp_earned": xp_result["xp_earned"],
                "level": self.level,
                "big_bro_says": "Sharp mind. That's what separates empire builders from workers.",
            }
        else:
            self.add_xp(5)
            return {
                "result": "defeat",
                "message": f"❌ Wrong. The answer was {record['secret']}.",
                "xp_earned": 5,
                "level": self.level,
                "big_bro_says": "Failure is just data. Analyse and retry.",
            }

    # ------------------------------------------------------------------
    # Bot Idea Manager
    # ------------------------------------------------------------------

    def generate_bot_idea(self) -> dict:
        """
        Randomly generate a new bot idea and add it to the fleet.

        Awards XP and may unlock the 'Bot Creator' or 'Empire Builder' achievements.
        """
        name, base_profit, category = random.choice(self.IDEA_POOL)
        profit = round(base_profit * random.uniform(0.8, 1.5), 2)
        usage = round(random.uniform(20.0, 95.0), 1)
        idea = BotIdea(name=name, profit_per_day_usd=profit, usage_pct=usage, category=category)
        self.bot_ideas.append(idea)

        xp_result = self.add_xp(20)
        self._unlock("Bot Creator")
        if len(self.bot_ideas) >= 10:
            self._unlock("Empire Builder")

        return {
            "module": "Bot Idea Manager",
            "new_bot": {
                "name": idea.name,
                "profit_per_day_usd": idea.profit_per_day_usd,
                "usage_pct": idea.usage_pct,
                "category": idea.category,
            },
            "total_ideas": len(self.bot_ideas),
            "xp_earned": xp_result["xp_earned"],
            "big_bro_says": self.big_bro_message(),
        }

    def get_top_bots(self, n: int = 5, sort_by: str = "profit") -> list:
        """Return top N bot ideas sorted by profit or usage."""
        bots = list(self.bot_ideas)
        if sort_by == "usage":
            bots.sort(key=lambda b: b.usage_pct, reverse=True)
        else:
            bots.sort(key=lambda b: b.profit_per_day_usd, reverse=True)
        return [
            {
                "name": b.name,
                "profit_per_day_usd": b.profit_per_day_usd,
                "usage_pct": b.usage_pct,
                "category": b.category,
            }
            for b in bots[:n]
        ]

    # ------------------------------------------------------------------
    # Bot Speed Control
    # ------------------------------------------------------------------

    def set_bot_speed(self, speed: BotSpeed) -> dict:
        """Change the global bot operating speed."""
        self.bot_speed = speed
        if speed == BotSpeed.AGGRESSIVE:
            self._unlock("Speed Demon")
        return {
            "bot_speed": speed.value,
            "xp_multiplier": speed.xp_multiplier,
            "profit_multiplier": speed.profit_multiplier,
        }

    # ------------------------------------------------------------------
    # Big Bro commentary
    # ------------------------------------------------------------------

    def big_bro_message(self) -> str:
        """Return a random motivational message from Big Bro."""
        return random.choice(self.BIG_BRO_MESSAGES)

    # ------------------------------------------------------------------
    # Dashboard snapshot
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        """Return a full dashboard snapshot suitable for display."""
        xp_in_level = self.xp % 100
        return {
            "module": "Interactive Dashboard",
            "level": self.level,
            "total_xp": self.xp,
            "xp_in_level": xp_in_level,
            "progress_bar": progress_bar(xp_in_level, 100),
            "xp_to_next_level": self._xp_to_next(),
            "bot_speed": self.bot_speed.value,
            "bot_ideas_count": len(self.bot_ideas),
            "top_bots": self.get_top_bots(),
            "achievements": self.get_achievements(),
            "big_bro_says": self.big_bro_message(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def render(self) -> str:
        """Render the dashboard as a human-readable string."""
        snap = self.snapshot()
        lines = [
            "🤖 BIG BRO AI EMPIRE",
            "",
            f"Level: {snap['level']}",
            f"XP:    {snap['progress_bar']}",
            "",
            f"🤖 Big Bro says: {snap['big_bro_says']}",
            "",
            "🏆 Achievements",
        ]
        for ach in snap["achievements"]:
            lines.append(f"  {ach['icon']} {ach['name']}")
        lines += [
            "",
            "🤖 Top Bot Ideas",
        ]
        for bot in snap["top_bots"]:
            lines.append(f"  {bot['name']} | ${bot['profit_per_day_usd']}/day | {bot['usage_pct']}% usage")
        lines += [
            "",
            "⚙️  Bot Speed: " + snap["bot_speed"].upper(),
            "",
            "MENU",
            "1️⃣  Hustle Simulator",
            "2️⃣  Code Gladiator",
            "3️⃣  Generate Bot Idea",
            "4️⃣  Change Bot Speed",
        ]
        return "\n".join(lines)
