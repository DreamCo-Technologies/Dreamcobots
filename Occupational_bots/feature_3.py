"""
Feature 3: Occupational Interview Preparation Bot
Functionality: Provides commonly asked interview questions, model answers, and
  tailored coaching tips organized by role, difficulty, and interview type.
Use Cases: Candidates preparing for upcoming interviews across various industries.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import GlobalAISourcesFlow  # noqa: F401 — GLOBAL AI SOURCES FLOW

# ---------------------------------------------------------------------------
# 30 example interview question records
# ---------------------------------------------------------------------------

EXAMPLES = [
    {"id": 1,  "question": "Tell me about yourself.",                              "type": "behavioral", "difficulty": "easy",   "role": "all",               "star_answer": "Start with your current role, highlight 2-3 key achievements, then explain why you're excited about this opportunity.", "follow_ups": ["What's your greatest strength?", "Where do you see yourself in 5 years?"]},
    {"id": 2,  "question": "Why do you want to work here?",                        "type": "motivational","difficulty": "easy",  "role": "all",               "star_answer": "Research the company's mission and recent achievements. Connect your personal values and career goals to their impact.", "follow_ups": ["What do you know about our products?"]},
    {"id": 3,  "question": "What is your greatest weakness?",                      "type": "behavioral", "difficulty": "medium", "role": "all",               "star_answer": "Choose a real weakness, describe steps you're taking to improve it, and show measurable progress.", "follow_ups": ["Can you give another example?"]},
    {"id": 4,  "question": "Describe a time you led a team under pressure.",       "type": "behavioral", "difficulty": "medium", "role": "management",        "star_answer": "Situation: Product launch delayed. Task: Coordinate 5-person team. Action: Daily standups, clear ownership. Result: Launched on time, 15% over target.", "follow_ups": ["How did you prioritize tasks?"]},
    {"id": 5,  "question": "Design a URL shortener like bit.ly.",                  "type": "technical",  "difficulty": "hard",   "role": "software_engineer", "star_answer": "Discuss hash function (MD5/Base62), database schema (short_code→URL), cache layer (Redis), load balancing, and 301 vs 302 redirects.", "follow_ups": ["How would you handle 1B requests/day?"]},
    {"id": 6,  "question": "Explain the difference between supervised and unsupervised learning.", "type": "technical", "difficulty": "medium", "role": "ml_engineer", "star_answer": "Supervised: labeled data, learn input→output mapping (classification, regression). Unsupervised: no labels, find patterns (clustering, dimensionality reduction).", "follow_ups": ["Give a real-world example of each."]},
    {"id": 7,  "question": "Walk me through a DCF analysis.",                      "type": "technical",  "difficulty": "hard",   "role": "financial_analyst", "star_answer": "Project free cash flows, select discount rate (WACC), calculate terminal value, discount all to present value, add non-operating assets.", "follow_ups": ["What are the key assumptions?"]},
    {"id": 8,  "question": "How do you prioritize features on a roadmap?",         "type": "behavioral", "difficulty": "medium", "role": "product_manager",   "star_answer": "Use a framework: RICE (Reach×Impact×Confidence/Effort) or MoSCoW. Balance customer value, business goals, and technical feasibility.", "follow_ups": ["How do you handle stakeholder conflicts?"]},
    {"id": 9,  "question": "How would you improve our conversion rate?",           "type": "case",       "difficulty": "hard",   "role": "marketing_manager", "star_answer": "Audit current funnel, identify drop-off points (Google Analytics), A/B test landing pages, optimize CTA copy, improve page speed.", "follow_ups": ["What metrics would you track?"]},
    {"id": 10, "question": "Tell me about a time you failed.",                     "type": "behavioral", "difficulty": "medium", "role": "all",               "star_answer": "Use STAR. Choose a real failure, own your mistake, explain what you learned, and describe how you applied that lesson.", "follow_ups": ["What would you do differently?"]},
    {"id": 11, "question": "What is Big O notation? Give examples.",               "type": "technical",  "difficulty": "medium", "role": "software_engineer", "star_answer": "Time/space complexity measure. O(1) constant, O(log n) binary search, O(n) linear scan, O(n log n) merge sort, O(n²) nested loops.", "follow_ups": ["What's the complexity of your last project?"]},
    {"id": 12, "question": "How do you handle a difficult team member?",           "type": "behavioral", "difficulty": "medium", "role": "management",        "star_answer": "1-on-1 conversation, understand their perspective, set clear expectations, document if escalation needed, involve HR if necessary.", "follow_ups": ["What if they don't improve?"]},
    {"id": 13, "question": "Explain REST vs GraphQL.",                             "type": "technical",  "difficulty": "medium", "role": "software_engineer", "star_answer": "REST: fixed endpoints, multiple requests, over/under fetching. GraphQL: single endpoint, query exactly what you need, typed schema.", "follow_ups": ["When would you use each?"]},
    {"id": 14, "question": "How do you analyze a new market opportunity?",         "type": "case",       "difficulty": "hard",   "role": "product_manager",   "star_answer": "TAM/SAM/SOM sizing, competitive landscape, customer research, regulatory environment, business model viability, go-to-market strategy.", "follow_ups": ["How would you validate assumptions?"]},
    {"id": 15, "question": "What's your approach to cold email outreach?",         "type": "behavioral", "difficulty": "medium", "role": "sales",             "star_answer": "Research prospect pain points, personalize subject line, lead with value not features, clear CTA, follow-up 3x, A/B test copy.", "follow_ups": ["What's your average open rate?"]},
    {"id": 16, "question": "Explain gradient descent.",                            "type": "technical",  "difficulty": "hard",   "role": "ml_engineer",       "star_answer": "Optimization algorithm to minimize loss function. Calculate gradient (∂L/∂w), update weights: w = w - η∇L. Variants: SGD, Adam, RMSProp.", "follow_ups": ["How do you choose learning rate?"]},
    {"id": 17, "question": "How do you build a customer success playbook?",        "type": "case",       "difficulty": "medium", "role": "customer_success",  "star_answer": "Map customer journey, define health score signals, create segment-specific playbooks (onboarding, QBR, at-risk, expansion), automate triggers.", "follow_ups": ["How do you measure success?"]},
    {"id": 18, "question": "Describe how you would debug a slow database query.",  "type": "technical",  "difficulty": "medium", "role": "software_engineer", "star_answer": "EXPLAIN ANALYZE, check missing indexes, look for N+1 queries, consider query rewriting, caching with Redis, or table partitioning.", "follow_ups": ["What profiling tools do you use?"]},
    {"id": 19, "question": "What metrics define success for a new product feature?","type": "behavioral", "difficulty": "medium", "role": "product_manager",  "star_answer": "Primary: adoption rate, retention impact. Secondary: NPS, support tickets, revenue attribution. Guardrail: performance regression, error rate.", "follow_ups": ["How long do you track a feature?"]},
    {"id": 20, "question": "How do you handle competing priorities?",              "type": "behavioral", "difficulty": "medium", "role": "all",               "star_answer": "Clarify urgency vs importance (Eisenhower matrix), communicate trade-offs to stakeholders, negotiate timelines, and communicate proactively.", "follow_ups": ["Give me a specific example."]},
    {"id": 21, "question": "Explain TCP vs UDP.",                                  "type": "technical",  "difficulty": "medium", "role": "software_engineer", "star_answer": "TCP: connection-oriented, reliable, ordered, slower (web, email). UDP: connectionless, fast, no guarantee (video streaming, gaming, DNS).", "follow_ups": ["Which would you use for a chat app?"]},
    {"id": 22, "question": "How do you retain at-risk customers?",                 "type": "case",       "difficulty": "hard",   "role": "customer_success",  "star_answer": "Detect signals early (usage drop, NPS dip, support tickets), proactive outreach, EBR, executive sponsor, personalized success plan.", "follow_ups": ["What's an acceptable churn rate for SaaS?"]},
    {"id": 23, "question": "What financial ratios do you use to evaluate a company?","type": "technical", "difficulty": "medium","role": "financial_analyst", "star_answer": "Profitability: ROE, EBITDA margin. Liquidity: current ratio, quick ratio. Leverage: D/E ratio. Efficiency: asset turnover. Valuation: P/E, EV/EBITDA.", "follow_ups": ["How do these differ by industry?"]},
    {"id": 24, "question": "How would you design a recommendation system?",        "type": "technical",  "difficulty": "hard",   "role": "ml_engineer",       "star_answer": "Content-based: item features similarity. Collaborative filtering: user behavior matrix. Hybrid: combine both. Considerations: cold start, scalability, freshness.", "follow_ups": ["How do you evaluate it?"]},
    {"id": 25, "question": "Describe a data-driven decision you made.",            "type": "behavioral", "difficulty": "medium", "role": "all",               "star_answer": "Identified declining retention, analyzed cohort data in SQL, discovered feature under-adoption, drove targeted campaign, improved retention by 18%.", "follow_ups": ["How did you present your findings?"]},
    {"id": 26, "question": "How would you scale a system to handle 10x traffic?",  "type": "technical",  "difficulty": "hard",   "role": "software_engineer", "star_answer": "Horizontal scaling, load balancing, database read replicas, CDN for static assets, caching (Redis/Memcached), async queues (Celery/RabbitMQ), autoscaling.", "follow_ups": ["What would you monitor?"]},
    {"id": 27, "question": "How do you negotiate a job offer?",                    "type": "behavioral", "difficulty": "medium", "role": "all",               "star_answer": "Research market data (Glassdoor, Levels.fyi), anchor high but realistically, negotiate total comp (base, equity, bonus), get it in writing.", "follow_ups": ["What if they say no to your counter?"]},
    {"id": 28, "question": "Describe your ideal work environment.",                "type": "motivational","difficulty": "easy",  "role": "all",               "star_answer": "Be authentic but align with the company culture. Mention: collaboration, ownership, feedback culture, growth opportunities. Research their values.", "follow_ups": ["How do you handle remote work?"]},
    {"id": 29, "question": "How do you stay current with industry trends?",        "type": "motivational","difficulty": "easy",  "role": "all",               "star_answer": "Specific: name 2-3 newsletters/podcasts/communities relevant to your role. Show genuine curiosity and how you apply new knowledge.", "follow_ups": ["What did you learn recently?"]},
    {"id": 30, "question": "Do you have any questions for us?",                    "type": "motivational","difficulty": "easy",  "role": "all",               "star_answer": "Always ask: 1) What does success look like in 90 days? 2) What's the biggest challenge the team faces? 3) How does the company support career growth?", "follow_ups": []},
]

TIERS = {
    "FREE":       {"price_usd": 0,   "max_questions": 10,  "mock_interview": False, "ai_coaching": False},
    "PRO":        {"price_usd": 19,  "max_questions": None,"mock_interview": True,  "ai_coaching": False},
    "ENTERPRISE": {"price_usd": 49,  "max_questions": None,"mock_interview": True,  "ai_coaching": True},
}


class InterviewPrepBot:
    """Prepares candidates for job interviews with questions, answers, and coaching.

    Competes with Pramp and interviewing.io by providing role-specific STAR
    answers, AI coaching feedback, and mock interview simulations.
    Monetization: $19/month PRO or $49/month ENTERPRISE subscription.
    """

    def __init__(self, tier: str = "FREE"):
        if tier not in TIERS:
            raise ValueError(f"Invalid tier '{tier}'. Choose from {list(TIERS)}")
        self.tier = tier
        self._config = TIERS[tier]
        self._flow = GlobalAISourcesFlow(bot_name="InterviewPrepBot")
        self._practice_log: list[dict] = []

    def _available_questions(self) -> list[dict]:
        limit = self._config["max_questions"]
        return EXAMPLES[:limit] if limit else EXAMPLES

    def get_questions_by_type(self, interview_type: str) -> list[dict]:
        """Return questions filtered by interview type: behavioral, technical, case, motivational."""
        valid = {"behavioral", "technical", "case", "motivational"}
        if interview_type not in valid:
            raise ValueError(f"Invalid type. Choose from {valid}")
        return [q for q in self._available_questions() if q["type"] == interview_type]

    def get_questions_by_role(self, role: str) -> list[dict]:
        """Return questions relevant to a specific role."""
        return [q for q in self._available_questions() if q["role"] in (role.lower(), "all")]

    def get_questions_by_difficulty(self, difficulty: str) -> list[dict]:
        """Return questions by difficulty: easy, medium, hard."""
        valid = {"easy", "medium", "hard"}
        if difficulty not in valid:
            raise ValueError(f"Invalid difficulty. Choose from {valid}")
        return [q for q in self._available_questions() if q["difficulty"] == difficulty]

    def get_question(self, question_id: int) -> dict:
        """Get a specific question with its full STAR answer."""
        question = next((q for q in EXAMPLES if q["id"] == question_id), None)
        if question is None:
            raise ValueError(f"Question ID {question_id} not found.")
        return dict(question)

    def get_star_answer(self, question_id: int) -> dict:
        """Get the STAR-method answer for a specific question."""
        question = self.get_question(question_id)
        return {
            "question": question["question"],
            "star_answer": question["star_answer"],
            "follow_ups": question["follow_ups"],
            "method": "STAR: Situation → Task → Action → Result",
        }

    def start_mock_interview(self, role: str, difficulty: str = "medium") -> list[dict]:
        """Generate a mock interview set for a specific role (PRO/ENTERPRISE)."""
        if not self._config["mock_interview"]:
            raise PermissionError(
                "Mock interview requires PRO or ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        all_q = self.get_questions_by_role(role)
        filtered = [q for q in all_q if q["difficulty"] == difficulty]
        return filtered[:5] if len(filtered) >= 5 else all_q[:5]

    def get_ai_coaching_feedback(self, question_id: int, user_answer: str) -> dict:
        """Get AI-powered feedback on a practice answer (ENTERPRISE only)."""
        if not self._config["ai_coaching"]:
            raise PermissionError(
                "AI coaching requires ENTERPRISE tier. "
                "Upgrade at dreamcobots.com/pricing"
            )
        question = self.get_question(question_id)
        feedback = {
            "question": question["question"],
            "your_answer_length": len(user_answer.split()),
            "feedback": [],
        }
        if len(user_answer.split()) < 50:
            feedback["feedback"].append("Your answer is too short. Aim for 2-3 minutes (150-200 words).")
        else:
            feedback["feedback"].append("Good length! Your answer is well-developed.")
        has_result = any(w in user_answer.lower() for w in ["result", "outcome", "%", "$", "increased", "reduced"])
        if not has_result:
            feedback["feedback"].append("Add a quantifiable result (%, $, time saved) to strengthen your answer.")
        else:
            feedback["feedback"].append("Great! You included a measurable result — this is exactly what interviewers want.")
        feedback["coaching_tips"] = question["follow_ups"]
        return feedback

    def log_practice(self, question_id: int, self_rating: int) -> dict:
        """Log a practice answer for progress tracking."""
        question = self.get_question(question_id)
        entry = {
            "question_id": question_id,
            "question": question["question"],
            "self_rating": self_rating,
            "session_count": len(self._practice_log) + 1,
        }
        self._practice_log.append(entry)
        return entry

    def get_prep_summary(self) -> dict:
        """Return interview preparation summary and statistics."""
        questions = self._available_questions()
        by_type: dict[str, int] = {}
        by_difficulty: dict[str, int] = {}
        for q in questions:
            by_type[q["type"]] = by_type.get(q["type"], 0) + 1
            by_difficulty[q["difficulty"]] = by_difficulty.get(q["difficulty"], 0) + 1
        return {
            "total_questions": len(questions),
            "by_type": by_type,
            "by_difficulty": by_difficulty,
            "practice_sessions": len(self._practice_log),
            "avg_self_rating": round(sum(p["self_rating"] for p in self._practice_log) / len(self._practice_log), 1) if self._practice_log else 0,
            "tier": self.tier,
        }

    def describe_tier(self) -> str:
        cfg = self._config
        limit = cfg["max_questions"] if cfg["max_questions"] else "all"
        lines = [
            f"=== InterviewPrepBot — {self.tier} Tier ===",
            f"  Monthly price    : ${cfg['price_usd']}/month",
            f"  Questions access : {limit}",
            f"  Mock interview   : {'enabled' if cfg['mock_interview'] else 'disabled'}",
            f"  AI coaching      : {'enabled' if cfg['ai_coaching'] else 'disabled (ENTERPRISE)'}",
        ]
        return "\n".join(lines)

    def run(self) -> dict:
        """Run the GLOBAL AI SOURCES FLOW pipeline."""
        result = self._flow.run_pipeline(
            raw_data={"domain": "interview_preparation", "questions_count": len(EXAMPLES)},
            learning_method="supervised",
        )
        return {"pipeline_complete": result.get("pipeline_complete"), "prep_summary": self.get_prep_summary()}


if __name__ == "__main__":
    bot = InterviewPrepBot(tier="PRO")
    behavioral = bot.get_questions_by_type("behavioral")
    print(f"Behavioral questions: {len(behavioral)}")
    se_questions = bot.get_questions_by_role("software_engineer")
    print(f"Software Engineer questions: {len(se_questions)}")
    mock = bot.start_mock_interview("software_engineer", "medium")
    print(f"\nMock interview set ({len(mock)} questions):")
    for q in mock:
        print(f"  🎯 [{q['difficulty']}] {q['question']}")
    star = bot.get_star_answer(5)
    print(f"\nSTAR Answer for Q5: {star['star_answer'][:100]}...")
    print(bot.describe_tier())

# ---------------------------------------------------------------------------
# Tier system additions for test compatibility
# ---------------------------------------------------------------------------
import random as _random_tier
from enum import Enum as _TierEnum


class Tier(_TierEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other.upper()
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()


_TIER_MONTHLY_PRICE = {"free": 0, "pro": 29, "enterprise": 99}


class InterviewPrepBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


_orig_interviewprep_bot_init = InterviewPrepBot.__init__


def _interviewprep_bot_new_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_interviewprep_bot_init(self, tier_val.upper())
    self.tier = Tier(tier_val)


InterviewPrepBot.__init__ = _interviewprep_bot_new_init
InterviewPrepBot.RESULT_LIMITS = {"free": 5, "pro": 25, "enterprise": 100}


def _interviewprep_bot_monthly_price(self):
    return _TIER_MONTHLY_PRICE[self.tier.value]


def _interviewprep_bot_get_tier_info(self):
    return {
        "tier": self.tier.value,
        "monthly_price_usd": self.monthly_price(),
        "result_limit": self.RESULT_LIMITS[self.tier.value],
    }


def _interviewprep_bot_enforce_tier(self, required_value):
    order = ["free", "pro", "enterprise"]
    if order.index(self.tier.value) < order.index(required_value):
        raise InterviewPrepBotTierError(
            f"{required_value.upper()} tier required. Current: {self.tier.value}"
        )


def _interviewprep_bot_list_items(self, limit=None):
    cap = limit if limit else self.RESULT_LIMITS[self.tier.value]
    return _random_tier.sample(EXAMPLES, min(cap, len(EXAMPLES)))


def _interviewprep_bot_analyze(self):
    self._enforce_tier("pro")
    return {"bot": "InterviewPrepBot", "tier": self.tier.value, "count": len(EXAMPLES)}


def _interviewprep_bot_export_report(self):
    self._enforce_tier("enterprise")
    return {"bot": "InterviewPrepBot", "tier": self.tier.value, "total_items": len(EXAMPLES), "items": EXAMPLES}


InterviewPrepBot.monthly_price = _interviewprep_bot_monthly_price
InterviewPrepBot.get_tier_info = _interviewprep_bot_get_tier_info
InterviewPrepBot._enforce_tier = _interviewprep_bot_enforce_tier
InterviewPrepBot.list_items = _interviewprep_bot_list_items
InterviewPrepBot.analyze = _interviewprep_bot_analyze
InterviewPrepBot.export_report = _interviewprep_bot_export_report

# ---------------------------------------------------------------------------
# InterviewPrepBot extended interface: chat, learning
# ---------------------------------------------------------------------------
import uuid as _uuid_ip


class _MockLearning:
    def __init__(self):
        self._weights = {}

    def get_response_weight(self, key: str) -> float:
        return self._weights.get(key, 1.0)

    def update_weight(self, key: str, delta: float = 0.1) -> None:
        self._weights[key] = self._weights.get(key, 1.0) + delta


_INTERVIEW_QUESTIONS = [
    "Tell me about a time you solved a difficult technical problem.",
    "How do you handle pressure and tight deadlines?",
    "What is your greatest professional achievement?",
    "Describe your approach to debugging complex software issues.",
    "How do you stay current with industry trends?",
]


def _interviewprepbot_full_init(self, tier=Tier.FREE):
    tier_val = tier.value if hasattr(tier, "value") else str(tier).lower()
    _orig_interviewprep_bot_init(self, tier_val.upper())
    self.tier = Tier(tier_val)
    if not hasattr(self, "bot_id"):
        self.bot_id = str(_uuid_ip.uuid4())
    self.name = "Interview Prep Bot"
    self.category = "occupational"
    self.domain = "interview_prep"
    self.learning = _MockLearning()
    self._question_index = 0
    self._feedback_counts = {"positive": 0, "negative": 0}


def _interviewprepbot_chat(self, user_input: str, user_id: str = "anonymous") -> str:
    q = user_input.lower()
    if any(w in q for w in ("great", "helpful", "good", "excellent", "amazing")):
        self.learning.update_weight("interview_prep", 0.2)
        self._feedback_counts["positive"] = self._feedback_counts.get("positive", 0) + 1
        return "Great! I'm glad the feedback was helpful. Let me share another interview question."
    if any(w in q for w in ("bad", "terrible", "wrong", "incorrect", "broken")):
        self._feedback_counts["negative"] = self._feedback_counts.get("negative", 0) + 1
        return "I'm sorry that wasn't helpful. Let me try a different approach."
    if any(w in q for w in ("question", "ask", "interview", "give me")):
        q_text = _INTERVIEW_QUESTIONS[self._question_index % len(_INTERVIEW_QUESTIONS)]
        self._question_index += 1
        return f"Interview question: {q_text}"
    return "I'm your Interview Prep Bot. Ask me for interview questions or practice scenarios."


InterviewPrepBot.__init__ = _interviewprepbot_full_init
InterviewPrepBot.chat = _interviewprepbot_chat
InterviewPrepBot.end_session = lambda self, user_id: None
