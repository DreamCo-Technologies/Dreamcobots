"""Email Campaign Manager Bot — tier-aware email campaign creation and drip sequences."""
import sys, os
import random
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.email_campaign_manager_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


SUBSCRIBER_LIMITS = {Tier.FREE: 500, Tier.PRO: 10000, Tier.ENTERPRISE: None}
CAMPAIGN_LIMITS = {Tier.FREE: 2, Tier.PRO: 10, Tier.ENTERPRISE: None}


class EmailCampaignManagerBot:
    """Tier-aware email campaign manager bot."""

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self.flow = GlobalAISourcesFlow(bot_name="EmailCampaignManagerBot")
        self._subscribers = []
        self._campaigns = {}
        self._sequences = {}

    def add_subscriber(self, email: str, name: str, segment: str = "general") -> dict:
        limit = SUBSCRIBER_LIMITS[self.tier]
        if limit is not None and len(self._subscribers) >= limit:
            raise PermissionError(f"Subscriber limit ({limit}) reached for {self.tier.value} tier")
        sub = {
            "email": email,
            "name": name,
            "segment": segment,
            "subscribed_at": datetime.now().isoformat(),
            "status": "active",
        }
        self._subscribers.append(sub)
        return sub

    def create_campaign(self, name: str, subject: str, audience_segment: str, goal: str = "engagement") -> dict:
        limit = CAMPAIGN_LIMITS[self.tier]
        if limit is not None and len(self._campaigns) >= limit:
            raise PermissionError(f"Campaign limit ({limit}) reached for {self.tier.value} tier")
        campaign_id = f"camp_{len(self._campaigns)+1}"
        camp = {
            "campaign_id": campaign_id,
            "name": name,
            "subject": subject,
            "audience_segment": audience_segment,
            "goal": goal,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "tier_used": self.tier.value,
        }
        self._campaigns[campaign_id] = camp
        return camp

    def generate_email_content(self, campaign_dict: dict, tone: str = "professional") -> dict:
        subject = campaign_dict.get("subject", "Important Update")
        body = (
            f"Dear Subscriber,\n\nWe have an exciting update about {campaign_dict.get('name', 'our campaign')}. "
            f"This message is crafted with a {tone} tone to help you achieve {campaign_dict.get('goal', 'your goals')}."
            f"\n\nBest regards,\nThe Team"
        )
        word_count = len(body.split())
        return {
            "subject": subject,
            "preheader": f"Quick update: {subject[:50]}",
            "body_text": body,
            "body_html": f"<p>{body.replace(chr(10), '</p><p>')}</p>",
            "word_count": word_count,
            "estimated_read_time_min": round(word_count / 200, 1),
            "tier_used": self.tier.value,
        }

    def get_campaign_stats(self, campaign_id: str) -> dict:
        sent = random.randint(100, 5000)
        opens = random.randint(10, sent)
        clicks = random.randint(1, opens)
        return {
            "campaign_id": campaign_id,
            "sent": sent,
            "opens": opens,
            "clicks": clicks,
            "unsubscribes": random.randint(0, 10),
            "open_rate": round(opens / sent * 100, 2),
            "click_rate": round(clicks / sent * 100, 2),
            "tier_used": self.tier.value,
        }

    def create_drip_sequence(self, trigger: str, num_emails: int = 5) -> dict:
        if self.tier == Tier.FREE:
            raise PermissionError("Drip sequences require PRO or ENTERPRISE tier")
        seq_id = f"seq_{len(self._sequences)+1}"
        emails = [
            {
                "email_num": i + 1,
                "delay_days": i * 3,
                "subject": f"Email {i+1}: {trigger}",
                "type": random.choice(["welcome", "educational", "promotional", "follow_up"]),
            }
            for i in range(num_emails)
        ]
        seq = {
            "sequence_id": seq_id,
            "trigger": trigger,
            "num_emails": num_emails,
            "emails": emails,
            "status": "active",
            "tier_used": self.tier.value,
        }
        self._sequences[seq_id] = seq
        return seq

    def run(self) -> dict:
        return self.flow.run_pipeline(
            raw_data={"bot": "EmailCampaignManagerBot", "tier": self.tier.value, "subscribers": len(self._subscribers), "campaigns": len(self._campaigns)},
            learning_method="supervised",
        )
