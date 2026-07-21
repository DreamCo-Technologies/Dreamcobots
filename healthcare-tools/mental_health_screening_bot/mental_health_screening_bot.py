# GLOBAL AI SOURCES FLOW
"""Mental Health Screening Bot - evidence-based mental health screening tool."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS


PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself",
    "Trouble concentrating on things",
    "Moving or speaking slowly (or being fidgety/restless)",
    "Thoughts of being better off dead or hurting yourself",
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless it is hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid as if something awful might happen",
]

CRISIS_RESOURCES = [
    "National Suicide Prevention Lifeline: 988",
    "Crisis Text Line: Text HOME to 741741",
    "SAMHSA Helpline: 1-800-662-4357",
]


class MentalHealthScreeningBot:
    """
    Evidence-based mental health screening using PHQ-9 and GAD-7 instruments.

    DISCLAIMER: This tool is for informational purposes only and does not
    constitute medical advice, diagnosis, or treatment.
    """

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])

    def run_phq2(self, responses: list) -> dict:
        """Run PHQ-2 screening. responses: list of 2 ints (0-3)."""
        if len(responses) < 2:
            raise ValueError("PHQ-2 requires exactly 2 responses (0-3 each).")
        score = sum(int(r) for r in responses[:2])
        return {
            "instrument": "PHQ-2",
            "score": score,
            "positive_screen": score >= 3,
            "recommendation": "Follow up with PHQ-9" if score >= 3 else "Low risk; monitor if symptoms persist.",
            "disclaimer": "Not a clinical diagnosis. Consult a healthcare professional.",
        }

    def run_phq9(self, responses: list) -> dict:
        """Run PHQ-9 screening. responses: list of 9 ints (0-3). Pro+ only."""
        if self.tier == "free":
            raise PermissionError("PHQ-9 screening requires Pro tier or higher.")
        if len(responses) < 9:
            raise ValueError("PHQ-9 requires exactly 9 responses (0-3 each).")
        score = sum(int(r) for r in responses[:9])
        if score <= 4:
            severity = "Minimal"
            action = "No action needed; monitor."
        elif score <= 9:
            severity = "Mild"
            action = "Watchful waiting; repeat PHQ-9 at follow-up."
        elif score <= 14:
            severity = "Moderate"
            action = "Treatment plan, counseling, follow-up."
        elif score <= 19:
            severity = "Moderately Severe"
            action = "Active treatment with medication and/or psychotherapy."
        else:
            severity = "Severe"
            action = "Immediate initiation of pharmacotherapy and psychotherapy."
        result = {
            "instrument": "PHQ-9",
            "score": score,
            "severity": severity,
            "action": action,
            "crisis_resources": CRISIS_RESOURCES if score >= 20 or responses[8] > 0 else [],
            "disclaimer": "Not a clinical diagnosis. Consult a licensed healthcare professional.",
        }
        return result

    def run_gad7(self, responses: list) -> dict:
        """Run GAD-7 anxiety screening. responses: list of 7 ints (0-3). Pro+ only."""
        if self.tier == "free":
            raise PermissionError("GAD-7 screening requires Pro tier or higher.")
        if len(responses) < 7:
            raise ValueError("GAD-7 requires exactly 7 responses (0-3 each).")
        score = sum(int(r) for r in responses[:7])
        if score <= 4:
            severity = "Minimal Anxiety"
        elif score <= 9:
            severity = "Mild Anxiety"
        elif score <= 14:
            severity = "Moderate Anxiety"
        else:
            severity = "Severe Anxiety"
        return {
            "instrument": "GAD-7",
            "score": score,
            "severity": severity,
            "further_evaluation_recommended": score >= 10,
            "disclaimer": "Not a clinical diagnosis. Consult a licensed healthcare professional.",
        }

    def get_questions(self, instrument: str) -> list:
        """Return questions for a given instrument."""
        if instrument == "PHQ-9":
            return PHQ9_QUESTIONS
        if instrument == "GAD-7":
            return GAD7_QUESTIONS
        if instrument == "PHQ-2":
            return PHQ9_QUESTIONS[:2]
        raise ValueError(f"Unknown instrument: {instrument}")
