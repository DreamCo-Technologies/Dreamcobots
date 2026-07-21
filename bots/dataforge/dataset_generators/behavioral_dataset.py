"""Behavioral/conversation dataset generator for DataForge AI."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import logging
import random
import uuid

logger = logging.getLogger(__name__)

CONV_TYPES = ["sales", "support", "negotiation"]
EMOTIONS = ["neutral", "frustrated", "happy", "confused", "angry", "satisfied"]
OUTCOMES = ["resolved", "escalated", "abandoned", "sale_made", "refund_issued", "no_resolution"]

SALES_TURNS = [
    ("agent", "Hello! How can I help you today?"),
    ("customer", "I'm interested in your premium package."),
    ("agent", "Great choice! Our premium package includes..."),
    ("customer", "What's the pricing?"),
    ("agent", "It's $499 per month with a 30-day free trial."),
    ("customer", "That sounds reasonable. Can I try it?"),
]
SUPPORT_TURNS = [
    ("agent", "Support team, how may I assist you?"),
    ("customer", "My order hasn't arrived yet."),
    ("agent", "I apologize for the delay. Let me check your order status."),
    ("customer", "It's been two weeks!"),
    ("agent", "I understand your frustration. I'll expedite this immediately."),
]
NEGOTIATION_TURNS = [
    ("customer", "I'd like a better price on this."),
    ("agent", "What budget are you working with?"),
    ("customer", "We were thinking around $10,000."),
    ("agent", "I can offer $12,000 with extended support."),
    ("customer", "How about $11,000?"),
    ("agent", "Let me check with my manager."),
]

TURN_POOLS = {"sales": SALES_TURNS, "support": SUPPORT_TURNS, "negotiation": NEGOTIATION_TURNS}


class BehavioralDatasetGenerator:
    """Generates synthetic customer conversation datasets for AI training."""

    def _build_turns(self, conv_type: str) -> list:
        """Build conversation turns with emotion labels.

        Args:
            conv_type: Type of conversation ('sales', 'support', 'negotiation').

        Returns:
            List of turn dicts with role, text, emotion, and confidence.
        """
        base_turns = TURN_POOLS.get(conv_type, SALES_TURNS)
        turns = []
        for role, text in base_turns:
            turns.append({
                "role": role,
                "text": text,
                "emotion": random.choice(EMOTIONS),
                "confidence": round(random.uniform(0.6, 1.0), 2),
            })
        return turns

    def generate(self, num_conversations: int = 100) -> list:
        """Generate synthetic conversation records.

        Args:
            num_conversations: Number of conversations to generate (default 100).

        Returns:
            List of conversation record dicts.
        """
        records = []
        for i in range(num_conversations):
            conv_type = random.choice(CONV_TYPES)
            record = {
                "id": str(uuid.uuid4()),
                "index": i,
                "type": conv_type,
                "turns": self._build_turns(conv_type),
                "outcome": random.choice(OUTCOMES),
                "duration_seconds": random.randint(30, 1800),
                "agent_id": f"AGENT_{random.randint(100, 999)}",
                "customer_id": f"CUST_{random.randint(10000, 99999)}",
                "synthetic": True,
                "license": "CC-BY-4.0",
            }
            records.append(record)
        logger.info("Generated %d behavioral conversation records.", num_conversations)
        return records
