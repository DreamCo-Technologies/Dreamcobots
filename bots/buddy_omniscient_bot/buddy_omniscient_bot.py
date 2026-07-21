"""
Buddy Omniscient Bot — DreamCo's Most Advanced AI Assistant.

Implements all viral, groundbreaking features for DreamCo's strategic roadmap:

  1. Personalized Reality Integration   — AR overlays & holographic Buddy bots
  2. AI-Powered Viral Challenges        — Shareable challenges, Buddy Badges
  3. Community-Built Skill Database     — Crowdsourcing hub for any skill
  4. Dream Your Business Campaign       — Launch a business in hours
  5. Dynamic Learning via Entertainment — Gamified learning, stock simulators
  6. Buddy Reality Show                 — "What Can Buddy Do?" live format
  7. AI Charity Ambassadorship          — Buddy-powered charity initiatives
  8. AI Social Creators                 — Viral content, memes, scripts, reels
  9. Expert Collaboration               — NASA engineers, artists, magnates
 10. Omniscient Knowledge Engine        — Buddy knows MORE than every AI model

Buddy OS runs on any smart device: phone, tablet, computer, smart TV,
gaming console, AR glasses, or VR headset.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.buddy_omniscient_bot import BuddyOmniscientBot, Tier

    buddy = BuddyOmniscientBot(tier=Tier.PRO, user_id="creator_42")

    # Start an AR repair session
    session = buddy.start_ar_overlay("car_repair", "smartphone")

    # Get a viral challenge
    challenges = buddy.list_viral_challenges()

    # Ask Buddy anything — he knows more than every other AI
    response = buddy.ask("How do I fix my alternator?")

    # Compare Buddy to ChatGPT
    result = buddy.compare_with_ai("ChatGPT (OpenAI)")
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401

from bots.buddy_omniscient_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_AR_VR,
    FEATURE_HOLOGRAPHIC,
    FEATURE_VIRAL_CHALLENGES,
    FEATURE_BUDDY_BADGES,
    FEATURE_SKILL_DATABASE,
    FEATURE_SKILL_UPLOAD,
    FEATURE_KNOWLEDGE_ENGINE,
    FEATURE_OMNISCIENT_MODE,
    FEATURE_SOCIAL_CREATORS,
    FEATURE_REALITY_SHOW,
    FEATURE_CHARITY_AMBASSADOR,
    FEATURE_DREAM_BUSINESS,
    FEATURE_EXPERT_COLLABORATION,
    FEATURE_DYNAMIC_LEARNING,
)
from bots.buddy_omniscient_bot.ar_vr_engine import (
    ARVREngine,
    AROverlaySession,
    HolographicSession,
    AROverlayType,
    HolographicMode,
    ProjectionDevice,
)
from bots.buddy_omniscient_bot.viral_challenges import (
    ViralChallengesEngine,
    RealityShowEngine,
    CharityAmbassadorEngine,
    DreamYourBusinessEngine,
    AISocialCreatorEngine,
    DynamicLearningEngine,
    ViralChallenge,
    BuddyBadge,
    ChallengeCategory,
    SocialPlatform,
    ContentType,
    CharityCause,
    LearningGameType,
)
from bots.buddy_omniscient_bot.skill_database import (
    SkillDatabase,
    CommunitySkill,
    ExpertProfile,
    SkillCategory,
    SkillDifficulty,
    ExpertField,
)
from bots.buddy_omniscient_bot.knowledge_engine import (
    KnowledgeEngine,
    KnowledgeDomain,
    CompetitorAI,
)

from typing import List, Optional


class BuddyOmniscientError(Exception):
    """Base exception for Buddy Omniscient Bot errors."""


class BuddyOmniscientTierError(BuddyOmniscientError):
    """Raised when a feature is not available on the current tier."""


class BuddyOmniscientBot:
    """
    Buddy Omniscient Bot — DreamCo's most advanced AI platform.

    Combines AR/VR guidance, viral challenges, community skills, expert
    knowledge, social content creation, charity ambassadorship, and
    an omniscient knowledge engine that surpasses every other AI model.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    user_id : str
        Identifier for the current user.
    """

    VERSION = "1.0.0"
    BOT_NAME = "Buddy Omniscient Bot"

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = "user") -> None:
        self.tier = tier
        self.user_id = user_id
        self.config: TierConfig = get_tier_config(tier)

        # Sub-systems
        self.ar_vr = ARVREngine(max_sessions=self.config.max_ar_sessions)
        self.challenges = ViralChallengesEngine(
            max_challenges=self.config.max_viral_challenges
        )
        self.reality_show = RealityShowEngine()
        self.charity = CharityAmbassadorEngine()
        self.dream_business = DreamYourBusinessEngine()
        self.social_creator = AISocialCreatorEngine()
        self.learning = DynamicLearningEngine()
        self.skills = SkillDatabase(max_uploads=self.config.max_skill_uploads)
        self.knowledge = KnowledgeEngine(max_domains=self.config.max_knowledge_domains)

    # ------------------------------------------------------------------
    # Framework compliance
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Return a status message confirming the bot is online."""
        return (
            f"{self.BOT_NAME} v{self.VERSION} Online "
            f"[{self.tier.value.upper()} tier] — "
            "Buddy knows everything. No other AI comes close."
        )

    # ------------------------------------------------------------------
    # Feature gate
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            raise BuddyOmniscientTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                "Upgrade to access it."
            )

    # ------------------------------------------------------------------
    # 1. AR/VR Personalized Reality Integration
    # ------------------------------------------------------------------

    def start_ar_overlay(
        self,
        overlay_type_str: str,
        device_str: str,
        context: str = "",
        voice_guidance: bool = False,
        hands_free_mode: bool = False,
    ) -> AROverlaySession:
        """Start an AR overlay session on a device.

        Parameters
        ----------
        overlay_type_str : str
            One of: repair_guide, furniture_placement, education, cooking_guide,
            business_planning, navigation, health_metrics, gaming,
            creative_design, custom.
        device_str : str
            One of: smartphone, tablet, smart_tv, computer, game_console,
            ar_glasses, vr_headset, holographic_display.
        """
        self._require_feature(FEATURE_AR_VR)
        try:
            overlay_type = AROverlayType(overlay_type_str)
        except ValueError:
            overlay_type = AROverlayType.CUSTOM
        try:
            device = ProjectionDevice(device_str)
        except ValueError:
            device = ProjectionDevice.SMARTPHONE
        return self.ar_vr.start_ar_overlay(
            overlay_type=overlay_type,
            device=device,
            context=context,
            voice_guidance=voice_guidance,
            hands_free_mode=hands_free_mode,
        )

    def project_holographic_buddy(
        self,
        device_str: str = "ar_glasses",
        mode_str: str = "life_sized",
        context: str = "",
    ) -> HolographicSession:
        """Project a life-sized holographic Buddy assistant."""
        self._require_feature(FEATURE_HOLOGRAPHIC)
        try:
            device = ProjectionDevice(device_str)
        except ValueError:
            device = ProjectionDevice.AR_GLASSES
        try:
            mode = HolographicMode(mode_str)
        except ValueError:
            mode = HolographicMode.LIFE_SIZED
        return self.ar_vr.project_holographic_buddy(
            device=device, mode=mode, context=context
        )

    def broadcast_ar_to_devices(
        self, session_id: str, device_strs: List[str]
    ) -> dict:
        """Broadcast an AR session to multiple devices simultaneously."""
        self._require_feature(FEATURE_AR_VR)
        devices = []
        for d in device_strs:
            try:
                devices.append(ProjectionDevice(d))
            except ValueError:
                devices.append(ProjectionDevice.SMARTPHONE)
        return self.ar_vr.broadcast_to_devices(session_id, devices)

    # ------------------------------------------------------------------
    # 2. Viral Challenges & Gamification
    # ------------------------------------------------------------------

    def list_viral_challenges(
        self, category_str: Optional[str] = None
    ) -> List[dict]:
        """List available viral challenges."""
        self._require_feature(FEATURE_VIRAL_CHALLENGES)
        category = None
        if category_str:
            try:
                category = ChallengeCategory(category_str)
            except ValueError:
                pass
        return [c.to_dict() for c in self.challenges.list_challenges(category)]

    def complete_viral_challenge(self, challenge_id: str) -> dict:
        """Complete a viral challenge and earn points and badges."""
        self._require_feature(FEATURE_VIRAL_CHALLENGES)
        return self.challenges.complete_challenge(challenge_id)

    def get_user_points(self) -> int:
        """Return the user's total accumulated points."""
        self._require_feature(FEATURE_VIRAL_CHALLENGES)
        return self.challenges.get_user_points()

    def get_earned_badges(self) -> List[dict]:
        """Return all badges earned by the user."""
        self._require_feature(FEATURE_BUDDY_BADGES)
        return [b.to_dict() for b in self.challenges.get_earned_badges()]

    def list_all_badges(self) -> List[dict]:
        """Return all available Buddy Badges."""
        self._require_feature(FEATURE_BUDDY_BADGES)
        return [b.to_dict() for b in self.challenges.list_all_badges()]

    # ------------------------------------------------------------------
    # 3. Community-Built Skill Database
    # ------------------------------------------------------------------

    def upload_skill(
        self,
        title: str,
        category_str: str,
        difficulty_str: str,
        description: str,
        steps: List[str],
        tags: Optional[List[str]] = None,
    ) -> dict:
        """Upload a new skill to the community database."""
        self._require_feature(FEATURE_SKILL_UPLOAD)
        try:
            category = SkillCategory(category_str)
        except ValueError:
            category = SkillCategory.CUSTOM
        try:
            difficulty = SkillDifficulty(difficulty_str)
        except ValueError:
            difficulty = SkillDifficulty.BEGINNER
        skill = self.skills.upload_skill(
            title=title,
            category=category,
            difficulty=difficulty,
            uploaded_by=self.user_id,
            description=description,
            steps=steps,
            tags=tags,
        )
        return skill.to_dict()

    def search_skills(
        self,
        query: str = "",
        category_str: Optional[str] = None,
        difficulty_str: Optional[str] = None,
    ) -> List[dict]:
        """Search the community skill database."""
        self._require_feature(FEATURE_SKILL_DATABASE)
        category = None
        if category_str:
            try:
                category = SkillCategory(category_str)
            except ValueError:
                pass
        difficulty = None
        if difficulty_str:
            try:
                difficulty = SkillDifficulty(difficulty_str)
            except ValueError:
                pass
        return [
            s.to_dict()
            for s in self.skills.search_skills(
                query=query, category=category, difficulty=difficulty
            )
        ]

    def rate_skill(self, skill_id: str, rating: float) -> dict:
        """Rate a skill in the community database."""
        self._require_feature(FEATURE_SKILL_DATABASE)
        return self.skills.rate_skill(skill_id, rating)

    def list_experts(self, field_str: Optional[str] = None) -> List[dict]:
        """List world-class experts who have trained Buddy."""
        self._require_feature(FEATURE_EXPERT_COLLABORATION)
        field = None
        if field_str:
            try:
                field = ExpertField(field_str)
            except ValueError:
                pass
        return [e.to_dict() for e in self.skills.list_experts(field)]

    def get_expert_skill_summary(self) -> dict:
        """Return a summary of skills contributed by all experts."""
        self._require_feature(FEATURE_EXPERT_COLLABORATION)
        return self.skills.get_expert_skill_summary()

    # ------------------------------------------------------------------
    # 4. Dream Your Business
    # ------------------------------------------------------------------

    def launch_business(
        self,
        business_name: str,
        business_type: str,
    ) -> dict:
        """Generate a complete business launch plan in hours."""
        self._require_feature(FEATURE_DREAM_BUSINESS)
        plan = self.dream_business.create_business_plan(
            business_name=business_name,
            business_type=business_type,
            owner_name=self.user_id,
        )
        return plan.to_dict()

    def list_business_plans(self) -> List[dict]:
        """List all created business plans."""
        self._require_feature(FEATURE_DREAM_BUSINESS)
        return [p.to_dict() for p in self.dream_business.list_plans()]

    # ------------------------------------------------------------------
    # 5. Dynamic Learning via Entertainment
    # ------------------------------------------------------------------

    def list_learning_games(
        self,
        game_type_str: Optional[str] = None,
        multiplayer_only: bool = False,
    ) -> List[dict]:
        """List available learning games."""
        self._require_feature(FEATURE_DYNAMIC_LEARNING)
        game_type = None
        if game_type_str:
            try:
                game_type = LearningGameType(game_type_str)
            except ValueError:
                pass
        return [
            g.to_dict()
            for g in self.learning.list_games(
                game_type=game_type, multiplayer_only=multiplayer_only
            )
        ]

    def start_learning_game(
        self,
        game_id: str,
        teammates: Optional[List[str]] = None,
    ) -> dict:
        """Start a learning game session."""
        self._require_feature(FEATURE_DYNAMIC_LEARNING)
        return self.learning.start_game_session(
            game_id=game_id,
            player_name=self.user_id,
            teammates=teammates,
        )

    def get_game_hint(self, session_id: str) -> dict:
        """Get Buddy's guidance hint for a learning game session."""
        self._require_feature(FEATURE_DYNAMIC_LEARNING)
        return self.learning.get_buddy_game_hint(session_id)

    # ------------------------------------------------------------------
    # 6. Buddy Reality Show
    # ------------------------------------------------------------------

    def create_reality_show_episode(
        self,
        title: str,
        description: str,
        challenge_category_str: str,
        participants: List[str],
        platforms: Optional[List[str]] = None,
    ) -> dict:
        """Create a new 'What Can Buddy Do?' reality show episode."""
        self._require_feature(FEATURE_REALITY_SHOW)
        try:
            category = ChallengeCategory(challenge_category_str)
        except ValueError:
            category = ChallengeCategory.CUSTOM
        episode = self.reality_show.create_episode(
            title=title,
            description=description,
            challenge_category=category,
            participants=participants,
            platforms=platforms,
        )
        return episode.to_dict()

    def go_live_reality_show(self, episode_id: str) -> dict:
        """Start a reality show episode live."""
        self._require_feature(FEATURE_REALITY_SHOW)
        return self.reality_show.go_live(episode_id)

    def vote_reality_show(self, episode_id: str, votes: int = 1) -> dict:
        """Cast votes for a live reality show episode."""
        self._require_feature(FEATURE_REALITY_SHOW)
        return self.reality_show.vote(episode_id, votes)

    # ------------------------------------------------------------------
    # 7. AI Charity Ambassadorship
    # ------------------------------------------------------------------

    def create_charity_initiative(
        self,
        cause_str: str,
        title: str,
        description: str,
        goal_amount: float,
    ) -> dict:
        """Create a new Buddy charity initiative."""
        self._require_feature(FEATURE_CHARITY_AMBASSADOR)
        try:
            cause = CharityCause(cause_str)
        except ValueError:
            cause = CharityCause.CUSTOM
        initiative = self.charity.create_initiative(
            cause=cause, title=title, description=description, goal_amount=goal_amount
        )
        return initiative.to_dict()

    def donate_to_charity(self, initiative_id: str, amount: float) -> dict:
        """Donate to a charity initiative."""
        self._require_feature(FEATURE_CHARITY_AMBASSADOR)
        return self.charity.donate(initiative_id, amount)

    def list_charity_initiatives(self, active_only: bool = False) -> List[dict]:
        """List all charity initiatives."""
        self._require_feature(FEATURE_CHARITY_AMBASSADOR)
        return [i.to_dict() for i in self.charity.list_initiatives(active_only)]

    # ------------------------------------------------------------------
    # 8. AI Social Creators
    # ------------------------------------------------------------------

    def generate_social_content(
        self,
        content_type_str: str,
        platform_str: str,
        topic: str = "",
    ) -> dict:
        """Generate viral social media content."""
        self._require_feature(FEATURE_SOCIAL_CREATORS)
        try:
            content_type = ContentType(content_type_str)
        except ValueError:
            content_type = ContentType.VIDEO_IDEA
        try:
            platform = SocialPlatform(platform_str)
        except ValueError:
            platform = SocialPlatform.TIKTOK
        content = self.social_creator.generate_content(
            content_type=content_type, platform=platform, topic=topic
        )
        return content.to_dict()

    def list_generated_content(self) -> List[dict]:
        """List all AI-generated social content."""
        self._require_feature(FEATURE_SOCIAL_CREATORS)
        return [c.to_dict() for c in self.social_creator.list_generated_content()]

    # ------------------------------------------------------------------
    # 9 & 10. Omniscient Knowledge Engine
    # ------------------------------------------------------------------

    def ask(self, topic: str, domain_str: Optional[str] = None) -> dict:
        """Ask Buddy anything — he knows more than every other AI model."""
        self._require_feature(FEATURE_KNOWLEDGE_ENGINE)
        domain = None
        if domain_str:
            try:
                domain = KnowledgeDomain(domain_str)
            except ValueError:
                pass
        return self.knowledge.query(topic, domain)

    def compare_with_ai(self, competitor_str: str) -> dict:
        """Compare Buddy's capabilities against a specific AI competitor."""
        self._require_feature(FEATURE_OMNISCIENT_MODE)
        try:
            competitor = CompetitorAI(competitor_str)
        except ValueError:
            return {
                "error": f"Competitor '{competitor_str}' not recognized.",
                "available": [c.value for c in CompetitorAI],
            }
        return self.knowledge.compare_with_competitor(competitor)

    def compare_with_all_ais(self) -> dict:
        """Compare Buddy against all major AI competitors."""
        self._require_feature(FEATURE_OMNISCIENT_MODE)
        return self.knowledge.compare_with_all_competitors()

    def get_superiority_summary(self) -> dict:
        """Return a summary of why Buddy surpasses all other AI models."""
        self._require_feature(FEATURE_KNOWLEDGE_ENGINE)
        return self.knowledge.get_buddy_superiority_summary()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> dict:
        """Return a unified dashboard of Buddy Omniscient Bot status."""
        return {
            "bot": self.BOT_NAME,
            "version": self.VERSION,
            "tier": self.tier.value,
            "user_id": self.user_id,
            "ar_sessions_active": self.ar_vr.count_active_ar_sessions(),
            "holographic_sessions_active": self.ar_vr.count_active_holographic_sessions(),
            "total_points": self.challenges.get_user_points(),
            "badges_earned": len(self.challenges.get_earned_badges()),
            "community_skills": self.skills.count_skills(),
            "expert_trainers": self.skills.count_experts(),
            "business_plans": len(self.dream_business.list_plans()),
            "charity_initiatives": len(self.charity.list_initiatives()),
            "social_content_generated": self.social_creator.count_generated(),
            "knowledge_entries": self.knowledge.count_entries(),
            "knowledge_queries": self.knowledge.count_queries(),
            "features": self.config.features,
        }

    def describe_tier(self) -> dict:
        """Return details about the current subscription tier."""
        cfg = self.config
        upgrade = get_upgrade_path(self.tier)
        return {
            "tier": cfg.tier.value,
            "name": cfg.name,
            "price_usd_monthly": cfg.price_usd_monthly,
            "max_ar_sessions": cfg.max_ar_sessions,
            "max_viral_challenges": cfg.max_viral_challenges,
            "max_skill_uploads": cfg.max_skill_uploads,
            "max_knowledge_domains": cfg.max_knowledge_domains,
            "features": cfg.features,
            "support_level": cfg.support_level,
            "upgrade_available": upgrade is not None,
            "upgrade_to": upgrade.name if upgrade else None,
            "upgrade_price": upgrade.price_usd_monthly if upgrade else None,
        }

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Handle a natural-language message and return a response dict.
        Makes BuddyOmniscientBot compatible with the BuddyAI orchestrator.
        """
        msg = message.lower().strip()

        if any(k in msg for k in ("dashboard", "status", "overview")):
            return {
                "response": "buddy_omniscient",
                "message": "Here is your Buddy Omniscient dashboard.",
                "data": self.dashboard(),
            }

        if any(k in msg for k in ("challenge", "viral", "tiktok", "instagram")):
            return {
                "response": "buddy_omniscient",
                "message": "Here are today's viral challenges!",
                "data": {"challenges": self.list_viral_challenges()},
            }

        if any(k in msg for k in ("badge", "points", "gamif")):
            return {
                "response": "buddy_omniscient",
                "message": f"You have {self.challenges.get_user_points()} points.",
                "data": {"badges": self.get_earned_badges() if self.config.has_feature(FEATURE_BUDDY_BADGES) else []},
            }

        if any(k in msg for k in ("augmented reality", "hologram", "ar overlay", "ar glasses", "vr headset", "virtual reality")):
            return {
                "response": "buddy_omniscient",
                "message": (
                    "Buddy can project AR overlays or appear as a holographic "
                    "assistant on any device — phone, tablet, TV, console, or AR glasses."
                ),
                "data": {
                    "supported_devices": self.ar_vr.get_supported_devices(),
                    "active_ar_sessions": self.ar_vr.count_active_ar_sessions(),
                },
            }

        if any(k in msg for k in ("skill", "learn", "teach", "community")):
            featured = [s.to_dict() for s in self.skills.list_featured_skills()]
            return {
                "response": "buddy_omniscient",
                "message": "Here are the featured community skills!",
                "data": {"featured_skills": featured},
            }

        if any(k in msg for k in ("business", "launch", "entrepreneur", "startup")):
            return {
                "response": "buddy_omniscient",
                "message": (
                    "Buddy can help you launch a business in hours! "
                    "Tell me your business idea and I'll handle the rest."
                ),
                "data": {"feature": "dream_your_business", "tier_required": "pro"},
            }

        if any(k in msg for k in ("charity", "donate", "cause", "ambassador")):
            initiatives = [i.to_dict() for i in self.charity.list_initiatives(active_only=True)]
            return {
                "response": "buddy_omniscient",
                "message": "Buddy is your AI Charity Ambassador!",
                "data": {"active_initiatives": initiatives},
            }

        if any(k in msg for k in ("chatgpt", "gemini", "claude", "copilot", "compare", "better")):
            if self.config.has_feature(FEATURE_OMNISCIENT_MODE):
                return {
                    "response": "buddy_omniscient",
                    "message": "Buddy outperforms every AI model. Here's the proof.",
                    "data": self.knowledge.compare_with_all_competitors(),
                }
            return {
                "response": "buddy_omniscient",
                "message": (
                    "Buddy surpasses all other AI models in AR guidance, "
                    "multi-device support, community skills, and more. "
                    "Upgrade to Pro for a detailed comparison."
                ),
                "data": {},
            }

        if any(k in msg for k in ("expert", "nasa", "doctor", "scientist", "trained by")):
            if self.config.has_feature(FEATURE_EXPERT_COLLABORATION):
                return {
                    "response": "buddy_omniscient",
                    "message": "Buddy is trained by the world's greatest minds!",
                    "data": {"experts": [e.to_dict() for e in self.skills.list_experts()]},
                }
            return {
                "response": "buddy_omniscient",
                "message": "Buddy is trained by NASA engineers, Grammy winners, and Fortune 500 leaders. Upgrade to Pro for full expert details.",
                "data": {},
            }

        if any(k in msg for k in ("game", "play", "chemistry", "stock", "multiplayer")):
            return {
                "response": "buddy_omniscient",
                "message": "Buddy turns learning into an epic game!",
                "data": {"games": self.list_learning_games()},
            }

        if any(k in msg for k in ("tier", "upgrade", "plan", "pricing")):
            return {
                "response": "buddy_omniscient",
                "message": "Here are the Buddy Omniscient subscription details.",
                "data": self.describe_tier(),
            }

        # Default: omniscient knowledge query
        result = self.knowledge.query(msg)
        return {
            "response": "buddy_omniscient",
            "message": (
                result.get("entry", {}).get("summary", "Buddy is here to help.")
                if result.get("found")
                else result.get("message", "Buddy is here to help with anything!")
            ),
            "data": result,
        }

    # ------------------------------------------------------------------
    # BuddyAI registration helper
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance) -> None:
        """Register this bot with the BuddyAI orchestrator."""
        buddy_bot_instance.register_bot("buddy_omniscient", self)
