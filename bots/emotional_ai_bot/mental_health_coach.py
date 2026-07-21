"""Mental Health Coach — mental health support, productivity coaching, and emotional care."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="MentalHealthCoach")

STRATEGIES: dict = {
    "joy": [
        "Share your positive feelings with someone you trust.",
        "Journal about what brought you joy today.",
        "Use this energy to help others around you.",
        "Celebrate the moment mindfully.",
    ],
    "sadness": [
        "Allow yourself to feel the emotion without judgment.",
        "Reach out to a supportive friend or family member.",
        "Practice gentle self-compassion exercises.",
        "Engage in light physical activity like a short walk.",
        "Try box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s.",
    ],
    "anger": [
        "Pause and take 10 slow, deep breaths before responding.",
        "Use progressive muscle relaxation to release tension.",
        "Write down your feelings in a private journal.",
        "Remove yourself from the triggering situation temporarily.",
        "Channel energy into physical exercise.",
    ],
    "fear": [
        "Ground yourself using the 5-4-3-2-1 sensory technique.",
        "Challenge catastrophic thinking with realistic alternatives.",
        "Practice slow diaphragmatic breathing.",
        "Break overwhelming fears into small, manageable steps.",
        "Seek information to reduce uncertainty where possible.",
    ],
    "surprise": [
        "Give yourself time to process before reacting.",
        "Write down your thoughts to create clarity.",
        "Talk through the unexpected event with a trusted person.",
    ],
    "disgust": [
        "Distance yourself from the source of disgust if possible.",
        "Reframe the situation from a different perspective.",
        "Engage in a cleansing or refreshing activity.",
    ],
    "trust": [
        "Nurture your relationships through open communication.",
        "Reflect on the foundations of trust in your key relationships.",
        "Express gratitude to those you trust.",
    ],
    "anticipation": [
        "Channel anticipation into productive preparation.",
        "Break your goal into actionable steps.",
        "Practice mindfulness to stay present while looking forward.",
        "Create a vision board or written plan.",
    ],
}

FOCUS_AREAS = [
    "time_management",
    "motivation",
    "stress_reduction",
    "goal_setting",
    "habit_formation",
    "work_life_balance",
]


class MentalHealthCoachError(Exception):
    """Raised when a MentalHealthCoach feature is unavailable on the current tier."""


class MentalHealthCoach:
    """Tier-aware mental health support and wellness coaching.

    Note: This bot provides educational and supportive content only and is NOT
    a substitute for professional medical or psychiatric diagnosis or treatment.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._progress_store: dict = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def assess_mental_state(self, user_id: str, responses: list) -> dict:
        """Return a supportive mental state assessment (PRO/ENTERPRISE).

        DISCLAIMER: This is not a medical diagnosis. For clinical support please
        consult a qualified mental health professional.
        """
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise MentalHealthCoachError(
                f"Mental state assessment requires PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        if not isinstance(responses, list):
            raise ValueError("responses must be a list")
        positive = sum(1 for r in responses if isinstance(r, str) and
                       any(w in r.lower() for w in ["good", "great", "happy", "well", "fine", "okay"]))
        negative = sum(1 for r in responses if isinstance(r, str) and
                       any(w in r.lower() for w in ["bad", "sad", "tired", "anxious", "stressed", "worried"]))
        total = len(responses) if responses else 1
        wellness_score = round(max(0.0, min(1.0, (positive - negative * 0.5) / total + 0.5)), 2)
        if wellness_score >= 0.7:
            state = "positive"
            recommendation = "Keep up your healthy habits and celebrate your wins."
        elif wellness_score >= 0.4:
            state = "neutral"
            recommendation = "Consider adding self-care practices to your daily routine."
        else:
            state = "needs_attention"
            recommendation = "We recommend speaking with a mental health professional for personalized support."
        return {
            "user_id": user_id,
            "wellness_score": wellness_score,
            "state": state,
            "recommendation": recommendation,
            "disclaimer": "This assessment is for educational purposes only and is NOT a medical diagnosis.",
            "tier": self.tier.value,
        }

    def provide_coping_strategy(self, emotion: str, intensity: float) -> dict:
        """Return coping strategies for the given emotion and intensity level."""
        emotion = emotion.lower()
        if emotion not in STRATEGIES:
            emotion = "sadness"
        all_strategies = STRATEGIES[emotion]
        if self.tier == Tier.FREE:
            selected = all_strategies[:2]
        elif self.tier == Tier.PRO:
            count = 3 if intensity < 0.5 else 4
            selected = all_strategies[:count]
        else:
            selected = all_strategies
        urgency = "high" if intensity >= 0.8 else "moderate" if intensity >= 0.5 else "low"
        return {
            "emotion": emotion,
            "intensity": intensity,
            "urgency": urgency,
            "strategies": selected,
            "professional_help_recommended": intensity >= 0.9,
            "tier": self.tier.value,
        }

    def create_wellness_plan(self, user_id: str, goals: list) -> dict:
        """Create a personalized wellness plan (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise MentalHealthCoachError(
                f"Wellness plan creation requires PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        if not isinstance(goals, list):
            raise ValueError("goals must be a list")
        plan_items = []
        for goal in goals[:5]:
            plan_items.append({
                "goal": goal,
                "action": f"Break '{goal}' into 3 small weekly milestones.",
                "frequency": "daily check-in",
                "support_resource": "Journaling and mindfulness practices",
            })
        return {
            "user_id": user_id,
            "goals": goals,
            "plan": plan_items,
            "duration_weeks": 8,
            "check_in_frequency": "weekly",
            "disclaimer": "This plan is for personal wellness support, not medical treatment.",
            "tier": self.tier.value,
        }

    def track_progress(self, user_id: str, check_in_data: dict) -> dict:
        """Track wellness progress for a user (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise MentalHealthCoachError(
                f"Progress tracking requires PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        if user_id not in self._progress_store:
            self._progress_store[user_id] = []
        self._progress_store[user_id].append(check_in_data)
        history = self._progress_store[user_id]
        mood_scores = [e.get("mood_score", 5) for e in history]
        avg_mood = round(sum(mood_scores) / len(mood_scores), 2) if mood_scores else 5.0
        trend = "improving" if len(mood_scores) >= 2 and mood_scores[-1] >= mood_scores[0] else "needs_attention"
        return {
            "user_id": user_id,
            "check_ins_total": len(history),
            "average_mood_score": avg_mood,
            "trend": trend,
            "latest_check_in": check_in_data,
            "tier": self.tier.value,
        }


class ProductivityCoachError(Exception):
    """Raised when a ProductivityCoach feature is unavailable on the current tier."""


class ProductivityCoach:
    """Tier-aware productivity and life coaching."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_productivity(self, user_id: str, activity_data: dict) -> dict:
        """Analyze productivity from activity data (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise ProductivityCoachError(
                f"Productivity analysis requires PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        tasks_completed = activity_data.get("tasks_completed", 0)
        tasks_planned = activity_data.get("tasks_planned", 1)
        hours_worked = activity_data.get("hours_worked", 0)
        completion_rate = round(min(1.0, tasks_completed / max(tasks_planned, 1)), 2)
        efficiency = round(min(1.0, tasks_completed / max(hours_worked, 1) / 3), 2) if hours_worked else 0.0
        return {
            "user_id": user_id,
            "completion_rate": completion_rate,
            "efficiency_score": efficiency,
            "tasks_completed": tasks_completed,
            "tasks_planned": tasks_planned,
            "hours_worked": hours_worked,
            "productivity_level": "high" if completion_rate >= 0.75 else "moderate" if completion_rate >= 0.5 else "low",
            "tier": self.tier.value,
        }

    def create_coaching_session(self, user_id: str, focus_area: str) -> dict:
        """Create a structured coaching session plan (PRO/ENTERPRISE)."""
        if self.tier == Tier.FREE:
            upgrade = get_upgrade_path(self.tier)
            raise ProductivityCoachError(
                f"Coaching sessions require PRO or ENTERPRISE tier. Upgrade: {upgrade}"
            )
        if focus_area not in FOCUS_AREAS:
            focus_area = "motivation"
        session_templates = {
            "time_management": {
                "exercises": ["Time audit", "Priority matrix (Eisenhower)", "Time-blocking schedule"],
                "duration_min": 45,
                "homework": "Track every 30-minute block for one week.",
            },
            "motivation": {
                "exercises": ["Values clarification", "Why journaling", "Vision statement draft"],
                "duration_min": 30,
                "homework": "Write your top 3 motivators and display them visibly.",
            },
            "stress_reduction": {
                "exercises": ["Stress inventory", "4-7-8 breathing practice", "Boundary-setting role play"],
                "duration_min": 40,
                "homework": "Practice one relaxation technique daily for 7 days.",
            },
            "goal_setting": {
                "exercises": ["SMART goal framework", "Obstacle mapping", "Accountability partner setup"],
                "duration_min": 50,
                "homework": "Write 3 SMART goals and share with your accountability partner.",
            },
            "habit_formation": {
                "exercises": ["Habit stacking", "Cue-routine-reward loop design", "Habit tracker setup"],
                "duration_min": 35,
                "homework": "Implement one new habit using the stacking technique.",
            },
            "work_life_balance": {
                "exercises": ["Wheel of life assessment", "Boundary identification", "Recovery rituals"],
                "duration_min": 45,
                "homework": "Identify and schedule one non-work activity per day.",
            },
        }
        template = session_templates[focus_area]
        return {
            "user_id": user_id,
            "focus_area": focus_area,
            "session_plan": template,
            "session_number": 1,
            "follow_up": "Schedule next session in 7 days.",
            "tier": self.tier.value,
        }

    def generate_daily_affirmations(self, user_profile: dict) -> dict:
        """Generate personalized daily affirmations based on user profile."""
        mood = user_profile.get("current_mood", "neutral")
        goals = user_profile.get("goals", ["personal growth"])
        base_affirmations = [
            "I am capable of achieving my goals.",
            "I embrace challenges as opportunities to grow.",
            "My feelings are valid and I handle them with grace.",
            "I am worthy of love, success, and happiness.",
            "Each day I become a better version of myself.",
            "I have the power to create positive change.",
            "I am resilient and can navigate any storm.",
            "I trust the journey I am on.",
        ]
        mood_affirmations = {
            "sad": ["I give myself permission to heal at my own pace.", "This feeling is temporary."],
            "anxious": ["I am safe and in control.", "I breathe in calm and release tension."],
            "angry": ["I choose to respond thoughtfully rather than react.", "I release what I cannot control."],
            "happy": ["I radiate positivity and share it with others.", "I am grateful for this moment."],
        }
        affirmations = base_affirmations[:3]
        for key, extra in mood_affirmations.items():
            if key in mood.lower():
                affirmations += extra[:2]
                break
        if self.tier == Tier.FREE:
            affirmations = affirmations[:3]
        return {
            "affirmations": affirmations,
            "count": len(affirmations),
            "mood_based": mood,
            "goals_referenced": goals[:2],
            "tier": self.tier.value,
        }
