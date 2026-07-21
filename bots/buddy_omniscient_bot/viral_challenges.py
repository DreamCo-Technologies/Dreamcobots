"""
Viral Challenges Engine — AI-Powered Viral Challenges, Gamification,
Reality Show, Social Competition, Charity Ambassadorship, Dream Your
Business, AI Social Creators, and Dynamic Learning for Buddy Omniscient.

Features:
  • AI-Powered Viral Challenges with shareable results (TikTok, Instagram)
  • Buddy Badges gamification system
  • Community leaderboards and social voting
  • "What Can Buddy Do?" Reality Show / Live-Streaming format
  • AI Charity Ambassadorship — donation systems, cause awareness
  • "Dream Your Business" Campaign — launch a business in hours
  • AI Social Creators — video ideas, automated edits, trendy scripts,
    meme generators
  • Dynamic Learning via Entertainment — chemistry games, stock simulators,
    multiplayer AI-assisted games

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
import copy

from framework import GlobalAISourcesFlow  # noqa: F401


# ===========================================================================
# Enums
# ===========================================================================

class ChallengeCategory(Enum):
    CAR_REPAIR = "car_repair"
    COOKING = "cooking"
    CREATIVE_ART = "creative_art"
    CODING = "coding"
    FITNESS = "fitness"
    EDUCATION = "education"
    BUSINESS = "business"
    GAMING = "gaming"
    MUSIC = "music"
    DIY_CRAFTS = "diy_crafts"
    CUSTOM = "custom"


class BadgeTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class SocialPlatform(Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    TWITCH = "twitch"
    FACEBOOK = "facebook"


class CharityCause(Enum):
    EDUCATION = "education"
    HUNGER_RELIEF = "hunger_relief"
    DISASTER_RELIEF = "disaster_relief"
    MENTAL_HEALTH = "mental_health"
    ENVIRONMENTAL = "environmental"
    TECH_ACCESS = "tech_access"
    VETERANS = "veterans"
    CUSTOM = "custom"


class ContentType(Enum):
    VIDEO_IDEA = "video_idea"
    SCRIPT = "script"
    MEME = "meme"
    REEL_IDEA = "reel_idea"
    TWEET = "tweet"
    TREND_ANALYSIS = "trend_analysis"


class LearningGameType(Enum):
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    STOCK_MARKET = "stock_market"
    HISTORY = "history"
    CODING = "coding"
    MATH = "math"
    MULTIPLAYER_AI = "multiplayer_ai"


# ===========================================================================
# Data classes
# ===========================================================================

@dataclass
class ViralChallenge:
    """Represents a single viral challenge."""

    challenge_id: str
    title: str
    category: ChallengeCategory
    description: str
    steps: List[str]
    difficulty: str
    share_hashtags: List[str]
    platforms: List[SocialPlatform]
    points: int
    badge_reward: Optional[str] = None
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "challenge_id": self.challenge_id,
            "title": self.title,
            "category": self.category.value,
            "description": self.description,
            "steps": self.steps,
            "difficulty": self.difficulty,
            "share_hashtags": self.share_hashtags,
            "platforms": [p.value for p in self.platforms],
            "points": self.points,
            "badge_reward": self.badge_reward,
            "active": self.active,
        }


@dataclass
class BuddyBadge:
    """Represents a Buddy Badge earned through challenges or skills."""

    badge_id: str
    name: str
    description: str
    tier: BadgeTier
    icon: str
    category: str
    points_required: int
    earned: bool = False
    share_url: str = ""

    def to_dict(self) -> dict:
        return {
            "badge_id": self.badge_id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.value,
            "icon": self.icon,
            "category": self.category,
            "points_required": self.points_required,
            "earned": self.earned,
            "share_url": self.share_url,
        }


@dataclass
class RealityShowEpisode:
    """Represents a Reality Show challenge episode."""

    episode_id: str
    title: str
    description: str
    participants: List[str]
    challenge_category: ChallengeCategory
    vote_count: int = 0
    live: bool = False
    platforms: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "title": self.title,
            "description": self.description,
            "participants": self.participants,
            "challenge_category": self.challenge_category.value,
            "vote_count": self.vote_count,
            "live": self.live,
            "platforms": self.platforms,
        }


@dataclass
class CharityInitiative:
    """Represents a charity initiative managed by Buddy."""

    initiative_id: str
    cause: CharityCause
    title: str
    description: str
    goal_amount: float
    raised_amount: float = 0.0
    active: bool = True
    awareness_posts: List[str] = field(default_factory=list)

    @property
    def progress_pct(self) -> float:
        if self.goal_amount <= 0:
            return 0.0
        return min(100.0, (self.raised_amount / self.goal_amount) * 100)

    def to_dict(self) -> dict:
        return {
            "initiative_id": self.initiative_id,
            "cause": self.cause.value,
            "title": self.title,
            "description": self.description,
            "goal_amount": self.goal_amount,
            "raised_amount": self.raised_amount,
            "progress_pct": round(self.progress_pct, 2),
            "active": self.active,
            "awareness_posts": self.awareness_posts,
        }


@dataclass
class BusinessPlan:
    """Represents a DreamYourBusiness plan."""

    plan_id: str
    business_name: str
    business_type: str
    owner_name: str
    steps_completed: List[str]
    marketing_content: List[str]
    estimated_launch_hours: float
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "business_name": self.business_name,
            "business_type": self.business_type,
            "owner_name": self.owner_name,
            "steps_completed": self.steps_completed,
            "marketing_content": self.marketing_content,
            "estimated_launch_hours": self.estimated_launch_hours,
            "active": self.active,
        }


@dataclass
class SocialContent:
    """AI-generated social media content for creators."""

    content_id: str
    content_type: ContentType
    platform: SocialPlatform
    title: str
    body: str
    hashtags: List[str]
    trend_score: float

    def to_dict(self) -> dict:
        return {
            "content_id": self.content_id,
            "content_type": self.content_type.value,
            "platform": self.platform.value,
            "title": self.title,
            "body": self.body,
            "hashtags": self.hashtags,
            "trend_score": self.trend_score,
        }


@dataclass
class LearningGame:
    """Represents a gamified learning experience."""

    game_id: str
    game_type: LearningGameType
    title: str
    description: str
    difficulty: str
    multiplayer: bool
    buddy_guidance: bool
    levels: int
    skills_taught: List[str]

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "game_type": self.game_type.value,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "multiplayer": self.multiplayer,
            "buddy_guidance": self.buddy_guidance,
            "levels": self.levels,
            "skills_taught": self.skills_taught,
        }


# ===========================================================================
# Seed data
# ===========================================================================

_PRESET_CHALLENGES: List[ViralChallenge] = [
    ViralChallenge(
        challenge_id="CH-001",
        title="Fix It Fast: Car Repair Challenge",
        category=ChallengeCategory.CAR_REPAIR,
        description=(
            "Use Buddy to diagnose and fix a common car issue. "
            "Record your session and share the result!"
        ),
        steps=[
            "Open the Buddy AR Repair overlay on your device.",
            "Point your camera at the engine bay.",
            "Follow Buddy's step-by-step repair instructions.",
            "Complete the repair and record a 60-second result video.",
            "Share on TikTok or Instagram with #BuddyFixIt.",
        ],
        difficulty="Intermediate",
        share_hashtags=["#BuddyFixIt", "#DreamCoAI", "#FixWithBuddy"],
        platforms=[SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM],
        points=500,
        badge_reward="Master Mechanic",
    ),
    ViralChallenge(
        challenge_id="CH-002",
        title="Chef Buddy: Cook & Share",
        category=ChallengeCategory.COOKING,
        description=(
            "Let Buddy guide you through cooking a dish from scratch "
            "using only what's in your kitchen. Post the result!"
        ),
        steps=[
            "Show Buddy your fridge and pantry via camera.",
            "Buddy generates a recipe from your available ingredients.",
            "Follow AR cooking overlays for each step.",
            "Plate the dish following Buddy's presentation tips.",
            "Post your creation with #BuddyChef.",
        ],
        difficulty="Beginner",
        share_hashtags=["#BuddyChef", "#DreamCoCooks", "#AIRecipe"],
        platforms=[SocialPlatform.INSTAGRAM, SocialPlatform.TIKTOK, SocialPlatform.YOUTUBE],
        points=300,
        badge_reward="AI Chef",
    ),
    ViralChallenge(
        challenge_id="CH-003",
        title="3D Art Creation Blitz",
        category=ChallengeCategory.CREATIVE_ART,
        description="Create a 3D art piece with Buddy's design guidance in under an hour.",
        steps=[
            "Tell Buddy your art concept or let Buddy suggest one.",
            "Use the AR creative design overlay for reference.",
            "Create the piece digitally or physically.",
            "Show Buddy for scoring and tips.",
            "Share your art with #BuddyArtist.",
        ],
        difficulty="Beginner",
        share_hashtags=["#BuddyArtist", "#DreamCoCreates", "#AIArt"],
        platforms=[SocialPlatform.INSTAGRAM, SocialPlatform.TIKTOK],
        points=400,
        badge_reward="AI Artist",
    ),
    ViralChallenge(
        challenge_id="CH-004",
        title="Business in a Day",
        category=ChallengeCategory.BUSINESS,
        description=(
            "Challenge: Use Buddy to plan, brand, and launch a micro-business "
            "concept in one day."
        ),
        steps=[
            "Tell Buddy your business idea.",
            "Buddy builds your business plan, name, and marketing in minutes.",
            "Set up your digital storefront with Buddy's guidance.",
            "Launch a social media post to announce your business.",
            "Share with #DreamCoLaunch.",
        ],
        difficulty="Advanced",
        share_hashtags=["#DreamCoLaunch", "#BusinessWithBuddy", "#AIEntrepreneur"],
        platforms=[
            SocialPlatform.INSTAGRAM,
            SocialPlatform.TIKTOK,
            SocialPlatform.TWITTER,
        ],
        points=800,
        badge_reward="Dream Entrepreneur",
    ),
    ViralChallenge(
        challenge_id="CH-005",
        title="Guitar Hero: AI Music Master",
        category=ChallengeCategory.MUSIC,
        description="Learn and perform a guitar solo with Buddy's real-time coaching.",
        steps=[
            "Choose a song from Buddy's music library.",
            "Follow Buddy's AR finger-placement overlays.",
            "Practice the solo with real-time feedback.",
            "Record your performance.",
            "Share with #BuddyRocks.",
        ],
        difficulty="Intermediate",
        share_hashtags=["#BuddyRocks", "#AIMusic", "#DreamCoSound"],
        platforms=[SocialPlatform.YOUTUBE, SocialPlatform.TIKTOK],
        points=600,
        badge_reward="Music Maestro",
    ),
]

_PRESET_BADGES: List[BuddyBadge] = [
    BuddyBadge(
        badge_id="BDG-001",
        name="AI Explorer",
        description="Completed your first Buddy challenge.",
        tier=BadgeTier.BRONZE,
        icon="🤖",
        category="general",
        points_required=100,
    ),
    BuddyBadge(
        badge_id="BDG-002",
        name="Master Mechanic",
        description="Fixed a vehicle with Buddy's AR guidance.",
        tier=BadgeTier.SILVER,
        icon="🔧",
        category="repair",
        points_required=500,
    ),
    BuddyBadge(
        badge_id="BDG-003",
        name="AI Chef",
        description="Cooked a full meal guided by Buddy.",
        tier=BadgeTier.SILVER,
        icon="👨‍🍳",
        category="cooking",
        points_required=300,
    ),
    BuddyBadge(
        badge_id="BDG-003B",
        name="AI Artist",
        description="Created a 3D art piece with Buddy's design guidance.",
        tier=BadgeTier.SILVER,
        icon="🎨",
        category="arts",
        points_required=400,
    ),
    BuddyBadge(
        badge_id="BDG-004",
        name="Dream Entrepreneur",
        description="Launched a business concept in under 24 hours with Buddy.",
        tier=BadgeTier.GOLD,
        icon="🚀",
        category="business",
        points_required=800,
    ),
    BuddyBadge(
        badge_id="BDG-005",
        name="Music Maestro",
        description="Performed a musical piece coached by Buddy.",
        tier=BadgeTier.GOLD,
        icon="🎸",
        category="music",
        points_required=600,
    ),
    BuddyBadge(
        badge_id="BDG-006",
        name="Charity Champion",
        description="Contributed to 3 or more Buddy charity initiatives.",
        tier=BadgeTier.PLATINUM,
        icon="💙",
        category="charity",
        points_required=1000,
    ),
    BuddyBadge(
        badge_id="BDG-007",
        name="Reality Star",
        description='Appeared in a "What Can Buddy Do?" live stream episode.',
        tier=BadgeTier.GOLD,
        icon="⭐",
        category="reality_show",
        points_required=750,
    ),
    BuddyBadge(
        badge_id="BDG-008",
        name="Viral Creator",
        description="Generated 10+ pieces of viral content using Buddy AI Social Creator.",
        tier=BadgeTier.PLATINUM,
        icon="📱",
        category="social",
        points_required=1200,
    ),
    BuddyBadge(
        badge_id="BDG-009",
        name="Knowledge Legend",
        description="Completed challenges across 5 different skill categories.",
        tier=BadgeTier.DIAMOND,
        icon="💎",
        category="knowledge",
        points_required=2500,
    ),
    BuddyBadge(
        badge_id="BDG-010",
        name="Buddy Grandmaster",
        description="Earned badges in every category and reached Legendary status.",
        tier=BadgeTier.LEGENDARY,
        icon="🏆",
        category="all",
        points_required=5000,
    ),
]

_PRESET_GAMES: List[LearningGame] = [
    LearningGame(
        game_id="GAME-001",
        game_type=LearningGameType.CHEMISTRY,
        title="Molecule Mixer",
        description="Combine elements in a virtual lab to discover reactions. Buddy explains the science!",
        difficulty="Beginner",
        multiplayer=False,
        buddy_guidance=True,
        levels=10,
        skills_taught=["Chemical bonding", "Periodic table", "Reaction types"],
    ),
    LearningGame(
        game_id="GAME-002",
        game_type=LearningGameType.STOCK_MARKET,
        title="Wall Street Simulator",
        description="Buy and sell virtual stocks in a simulated market with Buddy's investment guidance.",
        difficulty="Intermediate",
        multiplayer=True,
        buddy_guidance=True,
        levels=12,
        skills_taught=["Stock analysis", "Portfolio diversification", "Risk management"],
    ),
    LearningGame(
        game_id="GAME-003",
        game_type=LearningGameType.CODING,
        title="Bot Builder Arena",
        description="Compete to build the most efficient bot in a coding arena, with Buddy coaching.",
        difficulty="Advanced",
        multiplayer=True,
        buddy_guidance=True,
        levels=15,
        skills_taught=["Python basics", "Algorithm design", "Bot architecture"],
    ),
    LearningGame(
        game_id="GAME-004",
        game_type=LearningGameType.MULTIPLAYER_AI,
        title="DreamCo World Challenge",
        description=(
            "Multiplayer game where participants tackle real-world problems together "
            "while Buddy provides AI-powered insights and guidance."
        ),
        difficulty="Mixed",
        multiplayer=True,
        buddy_guidance=True,
        levels=20,
        skills_taught=["Collaboration", "Problem-solving", "AI application"],
    ),
]


# ===========================================================================
# Engine classes
# ===========================================================================

class ViralChallengesEngine:
    """
    Manages viral challenges, Buddy Badges, and user points.
    """

    def __init__(self, max_challenges: Optional[int] = 5) -> None:
        self._max_challenges = max_challenges
        self._challenges: Dict[str, ViralChallenge] = {
            c.challenge_id: c for c in _PRESET_CHALLENGES
        }
        self._badges: Dict[str, BuddyBadge] = {
            b.badge_id: copy.copy(b) for b in _PRESET_BADGES
        }
        self._user_points: int = 0
        self._earned_badges: List[str] = []

    def list_challenges(self, category: Optional[ChallengeCategory] = None) -> List[ViralChallenge]:
        challenges = [c for c in self._challenges.values() if c.active]
        if category:
            challenges = [c for c in challenges if c.category == category]
        if self._max_challenges is not None:
            challenges = challenges[: self._max_challenges]
        return challenges

    def get_challenge(self, challenge_id: str) -> Optional[ViralChallenge]:
        return self._challenges.get(challenge_id)

    def complete_challenge(self, challenge_id: str) -> dict:
        """Mark a challenge as completed, award points and badge."""
        challenge = self._challenges.get(challenge_id)
        if not challenge:
            return {"error": f"Challenge '{challenge_id}' not found."}
        self._user_points += challenge.points
        result: dict = {
            "challenge_id": challenge_id,
            "title": challenge.title,
            "points_earned": challenge.points,
            "total_points": self._user_points,
            "badge": None,
            "message": f"Challenge completed! You earned {challenge.points} points.",
        }
        if challenge.badge_reward:
            badge = self._award_badge_by_name(challenge.badge_reward)
            if badge:
                result["badge"] = badge.to_dict()
                result["message"] += f" Badge unlocked: {badge.icon} {badge.name}"
        return result

    def _award_badge_by_name(self, badge_name: str) -> Optional[BuddyBadge]:
        for badge in self._badges.values():
            if badge.name == badge_name and not badge.earned:
                badge.earned = True
                badge.share_url = (
                    f"https://dreamcobots.com/badges/{badge.badge_id}"
                )
                self._earned_badges.append(badge.badge_id)
                return badge
        return None

    def award_badge(self, badge_id: str) -> dict:
        """Directly award a badge by ID."""
        badge = self._badges.get(badge_id)
        if not badge:
            return {"error": f"Badge '{badge_id}' not found."}
        if badge.earned:
            return {"message": f"Badge '{badge.name}' already earned.", "badge": badge.to_dict()}
        badge.earned = True
        badge.share_url = f"https://dreamcobots.com/badges/{badge_id}"
        self._earned_badges.append(badge_id)
        return {"message": f"Badge unlocked: {badge.icon} {badge.name}!", "badge": badge.to_dict()}

    def get_user_points(self) -> int:
        return self._user_points

    def get_earned_badges(self) -> List[BuddyBadge]:
        return [self._badges[bid] for bid in self._earned_badges if bid in self._badges]

    def list_all_badges(self) -> List[BuddyBadge]:
        return list(self._badges.values())

    def get_leaderboard_entry(self, username: str) -> dict:
        return {
            "username": username,
            "points": self._user_points,
            "badges_earned": len(self._earned_badges),
            "rank": "Buddy Champion" if self._user_points >= 5000 else "Rising Star",
        }


class RealityShowEngine:
    """
    Manages "What Can Buddy Do?" Reality Show / Live-Stream Episodes.
    """

    def __init__(self) -> None:
        self._episodes: Dict[str, RealityShowEpisode] = {}

    def create_episode(
        self,
        title: str,
        description: str,
        challenge_category: ChallengeCategory,
        participants: List[str],
        platforms: Optional[List[str]] = None,
    ) -> RealityShowEpisode:
        episode_id = f"EP-{uuid.uuid4().hex[:6].upper()}"
        episode = RealityShowEpisode(
            episode_id=episode_id,
            title=title,
            description=description,
            participants=participants,
            challenge_category=challenge_category,
            platforms=platforms or ["TikTok", "YouTube", "Instagram"],
        )
        self._episodes[episode_id] = episode
        return episode

    def go_live(self, episode_id: str) -> dict:
        episode = self._episodes.get(episode_id)
        if not episode:
            return {"error": f"Episode '{episode_id}' not found."}
        episode.live = True
        return {
            "episode_id": episode_id,
            "status": "live",
            "message": f'🎬 Episode "{episode.title}" is NOW LIVE! Tune in and vote!',
            "platforms": episode.platforms,
        }

    def vote(self, episode_id: str, votes: int = 1) -> dict:
        episode = self._episodes.get(episode_id)
        if not episode:
            return {"error": f"Episode '{episode_id}' not found."}
        episode.vote_count += votes
        return {
            "episode_id": episode_id,
            "total_votes": episode.vote_count,
            "message": f"Vote recorded! Total votes: {episode.vote_count}",
        }

    def list_episodes(self, live_only: bool = False) -> List[RealityShowEpisode]:
        eps = list(self._episodes.values())
        if live_only:
            eps = [e for e in eps if e.live]
        return eps


class CharityAmbassadorEngine:
    """
    Manages Buddy charity initiatives.
    """

    def __init__(self) -> None:
        self._initiatives: Dict[str, CharityInitiative] = {}

    def create_initiative(
        self,
        cause: CharityCause,
        title: str,
        description: str,
        goal_amount: float,
    ) -> CharityInitiative:
        initiative_id = f"CHR-{uuid.uuid4().hex[:6].upper()}"
        initiative = CharityInitiative(
            initiative_id=initiative_id,
            cause=cause,
            title=title,
            description=description,
            goal_amount=goal_amount,
        )
        self._initiatives[initiative_id] = initiative
        return initiative

    def donate(self, initiative_id: str, amount: float) -> dict:
        initiative = self._initiatives.get(initiative_id)
        if not initiative:
            return {"error": f"Initiative '{initiative_id}' not found."}
        if not initiative.active:
            return {"error": f"Initiative '{initiative_id}' is no longer active."}
        initiative.raised_amount += amount
        return {
            "initiative_id": initiative_id,
            "amount_donated": amount,
            "total_raised": initiative.raised_amount,
            "goal": initiative.goal_amount,
            "progress_pct": initiative.progress_pct,
            "message": f"Thank you! ${amount:.2f} donated to {initiative.title}.",
        }

    def add_awareness_post(self, initiative_id: str, post_content: str) -> dict:
        initiative = self._initiatives.get(initiative_id)
        if not initiative:
            return {"error": f"Initiative '{initiative_id}' not found."}
        initiative.awareness_posts.append(post_content)
        return {
            "initiative_id": initiative_id,
            "post": post_content,
            "total_posts": len(initiative.awareness_posts),
            "message": "Awareness post added and ready to share!",
        }

    def list_initiatives(self, active_only: bool = False) -> List[CharityInitiative]:
        initiatives = list(self._initiatives.values())
        if active_only:
            initiatives = [i for i in initiatives if i.active]
        return initiatives


class DreamYourBusinessEngine:
    """
    Automates the "Dream Your Business" viral campaign.
    Buddy generates full business setup plans in hours.
    """

    def __init__(self) -> None:
        self._plans: Dict[str, BusinessPlan] = {}

    def create_business_plan(
        self,
        business_name: str,
        business_type: str,
        owner_name: str,
    ) -> BusinessPlan:
        plan_id = f"BIZ-{uuid.uuid4().hex[:6].upper()}"
        steps = [
            f"Business concept defined: {business_name} ({business_type})",
            "Market research completed by Buddy — target audience identified.",
            "Brand identity created: logo concept, color scheme, tagline.",
            "Social media accounts set up across all platforms.",
            "Initial marketing campaign drafted by Buddy.",
            "Digital storefront or landing page blueprint generated.",
            "Launch announcement content created and scheduled.",
        ]
        marketing = [
            f"Announcing {business_name} — {business_type} — powered by DreamCo AI!",
            f"Follow {business_name} to see how AI helped launch a business in hours.",
            f"Use #DreamCoLaunch to share your {business_name} journey.",
        ]
        plan = BusinessPlan(
            plan_id=plan_id,
            business_name=business_name,
            business_type=business_type,
            owner_name=owner_name,
            steps_completed=steps,
            marketing_content=marketing,
            estimated_launch_hours=4.0,
        )
        self._plans[plan_id] = plan
        return plan

    def get_plan(self, plan_id: str) -> Optional[BusinessPlan]:
        return self._plans.get(plan_id)

    def list_plans(self) -> List[BusinessPlan]:
        return list(self._plans.values())


class AISocialCreatorEngine:
    """
    AI copilot for content creators — generates viral content ideas,
    scripts, memes, and trend analyses for social platforms.
    """

    _TREND_TOPICS: List[str] = [
        "AI tools transforming daily life",
        "DIY car repair with AR assistance",
        "Launch a business in hours",
        "Buddy teaches guitar in real-time",
        "AI cooking guide from fridge contents",
        "Virtual stock market simulator",
        "Charity challenges with AI",
        "3D art created by AI",
        "What Can Buddy Do? — real-world test",
    ]

    def __init__(self) -> None:
        self._generated_content: List[SocialContent] = []

    def generate_content(
        self,
        content_type: ContentType,
        platform: SocialPlatform,
        topic: str = "",
    ) -> SocialContent:
        topic = topic or self._TREND_TOPICS[len(self._generated_content) % len(self._TREND_TOPICS)]
        bodies = {
            ContentType.VIDEO_IDEA: (
                f"Video Idea: '{topic}' — Show Buddy solving the challenge in 60 seconds, "
                "ending with a dramatic reveal. Perfect for short-form content!"
            ),
            ContentType.SCRIPT: (
                f"Hook: 'Did you know Buddy can {topic}?' "
                f"Main: Walk through how Buddy handles '{topic}' step by step with AR overlays. "
                "CTA: 'Try it yourself — link in bio!'"
            ),
            ContentType.MEME: (
                f"Top text: 'Other AI models when you ask about {topic}' / "
                f"Bottom text: 'Buddy: [Provides full AR guide instantly]'"
            ),
            ContentType.REEL_IDEA: (
                f"Reel: Fast-cut between 5 things Buddy can do related to '{topic}', "
                "ending with a badge unlock animation. Use trending audio."
            ),
            ContentType.TWEET: (
                f"Just asked Buddy about '{topic}' and it gave me a full AR walkthrough "
                f"in seconds. No other AI does this. 🤯 #DreamCoAI #BuddyBot"
            ),
            ContentType.TREND_ANALYSIS: (
                f"'{topic}' is trending on TikTok and Instagram. Buddy can help you "
                "create content around this trend instantly with AI-generated scripts "
                "and meme templates."
            ),
        }
        content = SocialContent(
            content_id=f"SC-{uuid.uuid4().hex[:6].upper()}",
            content_type=content_type,
            platform=platform,
            title=topic,
            body=bodies.get(content_type, f"AI-generated content for '{topic}'."),
            hashtags=[
                "#DreamCoAI", "#BuddyBot", "#AICreator",
                f"#{platform.value.capitalize()}Creator",
            ],
            trend_score=round(7.5 + (len(self._generated_content) % 3) * 0.5, 1),
        )
        self._generated_content.append(content)
        return content

    def list_generated_content(self) -> List[SocialContent]:
        return list(self._generated_content)

    def count_generated(self) -> int:
        return len(self._generated_content)


class DynamicLearningEngine:
    """
    Gamified learning experiences via entertainment.
    """

    def __init__(self) -> None:
        self._games: Dict[str, LearningGame] = {
            g.game_id: g for g in _PRESET_GAMES
        }
        self._active_sessions: Dict[str, dict] = {}

    def list_games(
        self,
        game_type: Optional[LearningGameType] = None,
        multiplayer_only: bool = False,
    ) -> List[LearningGame]:
        games = list(self._games.values())
        if game_type:
            games = [g for g in games if g.game_type == game_type]
        if multiplayer_only:
            games = [g for g in games if g.multiplayer]
        return games

    def start_game_session(
        self,
        game_id: str,
        player_name: str,
        teammates: Optional[List[str]] = None,
    ) -> dict:
        game = self._games.get(game_id)
        if not game:
            return {"error": f"Game '{game_id}' not found."}
        session_id = f"GS-{uuid.uuid4().hex[:6].upper()}"
        session = {
            "session_id": session_id,
            "game_id": game_id,
            "game_title": game.title,
            "player": player_name,
            "teammates": teammates or [],
            "current_level": 1,
            "buddy_guidance": game.buddy_guidance,
            "active": True,
        }
        self._active_sessions[session_id] = session
        return session

    def get_buddy_game_hint(self, session_id: str) -> dict:
        session = self._active_sessions.get(session_id)
        if not session:
            return {"error": f"Session '{session_id}' not found."}
        game = self._games.get(session["game_id"])
        return {
            "session_id": session_id,
            "hint": (
                f"Buddy says: For level {session['current_level']} of "
                f"'{game.title if game else session['game_id']}', "
                "focus on the pattern in the data before applying the concept. "
                "Remember, I can see your screen and guide you in real-time!"
            ),
            "buddy_guidance_active": True,
        }

    def count_games(self) -> int:
        return len(self._games)
