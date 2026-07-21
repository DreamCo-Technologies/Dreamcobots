"""
Multi-Channel Marketing Bot

Automates outreach across SMS, Email, AI Voice, and social media platforms
(TikTok, YouTube, Instagram). Uses AI to optimise ad spend based on
predicted ROI segments.

Architecture
------------
  Campaign → Channels → Audience Segments → AI Scoring → Send/Schedule

Revenue hook (standard DreamCo format):
    {
        "revenue": estimated attributed revenue,
        "leads_generated": contacts reached,
        "conversion_rate": estimated rate,
        "action": description of campaign action,
    }
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CampaignChannel(Enum):
    SMS = "sms"
    EMAIL = "email"
    AI_VOICE = "ai_voice"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    PAID_ADS = "paid_ads"


class CampaignStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class AudienceSegment:
    segment_id: str
    name: str
    size: int
    predicted_roi: float  # 0–1 score
    channel_affinity: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "segment_id": self.segment_id,
            "name": self.name,
            "size": self.size,
            "predicted_roi": round(self.predicted_roi, 4),
            "channel_affinity": self.channel_affinity,
        }


@dataclass
class Campaign:
    campaign_id: str
    name: str
    channels: List[CampaignChannel]
    message_template: str
    audience_size: int = 0
    status: CampaignStatus = CampaignStatus.DRAFT
    sends: int = 0
    conversions: int = 0
    attributed_revenue: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    launched_at: Optional[str] = None

    @property
    def conversion_rate(self) -> float:
        if self.sends == 0:
            return 0.0
        return round(self.conversions / self.sends, 4)

    def to_dict(self) -> dict:
        return {
            "campaign_id": self.campaign_id,
            "name": self.name,
            "channels": [c.value for c in self.channels],
            "status": self.status.value,
            "audience_size": self.audience_size,
            "sends": self.sends,
            "conversions": self.conversions,
            "conversion_rate": self.conversion_rate,
            "attributed_revenue": round(self.attributed_revenue, 2),
            "created_at": self.created_at,
            "launched_at": self.launched_at,
        }


# ---------------------------------------------------------------------------
# MultiChannelMarketing
# ---------------------------------------------------------------------------


class MultiChannelMarketing:
    """
    Orchestrates multi-channel marketing campaigns for DreamCo.

    Supports SMS, Email, AI Voice (Twilio), TikTok, YouTube, Instagram,
    and Paid Ads.  An AI scoring layer ranks audience segments by
    predicted ROI before sending.

    Usage
    -----
    mcm = MultiChannelMarketing()
    campaign = mcm.create_campaign(
        name="Spring Real Estate Push",
        channels=[CampaignChannel.SMS, CampaignChannel.EMAIL],
        message_template="Cash offer available for your property!",
    )
    mcm.add_segment(campaign.campaign_id, "Chicago Sellers", size=500, predicted_roi=0.12)
    mcm.launch_campaign(campaign.campaign_id)
    output = mcm.get_revenue_output(campaign.campaign_id)
    """

    # Average revenue per conversion per channel (USD) — tunable
    CHANNEL_REVENUE_MAP: Dict[str, float] = {
        "sms": 50.0,
        "email": 30.0,
        "ai_voice": 80.0,
        "tiktok": 20.0,
        "youtube": 25.0,
        "instagram": 20.0,
        "paid_ads": 60.0,
    }

    def __init__(self) -> None:
        self._campaigns: Dict[str, Campaign] = {}
        self._segments: Dict[str, List[AudienceSegment]] = {}  # campaign_id → segments

    # ------------------------------------------------------------------
    # Campaign management
    # ------------------------------------------------------------------

    def create_campaign(
        self,
        name: str,
        channels: List[CampaignChannel],
        message_template: str,
    ) -> Campaign:
        """Create and register a new marketing campaign."""
        campaign_id = f"camp_{uuid.uuid4().hex[:8]}"
        campaign = Campaign(
            campaign_id=campaign_id,
            name=name,
            channels=channels,
            message_template=message_template,
        )
        self._campaigns[campaign_id] = campaign
        self._segments[campaign_id] = []
        return campaign

    def add_segment(
        self,
        campaign_id: str,
        name: str,
        size: int,
        predicted_roi: float,
        channel_affinity: Optional[List[str]] = None,
    ) -> AudienceSegment:
        """Add an audience segment to a campaign."""
        campaign = self._get_campaign(campaign_id)
        segment = AudienceSegment(
            segment_id=f"seg_{uuid.uuid4().hex[:8]}",
            name=name,
            size=size,
            predicted_roi=predicted_roi,
            channel_affinity=channel_affinity or [],
        )
        self._segments[campaign_id].append(segment)
        campaign.audience_size += size
        return segment

    def launch_campaign(self, campaign_id: str) -> dict:
        """
        Score segments by predicted ROI, then simulate campaign sends
        across all registered channels.
        """
        campaign = self._get_campaign(campaign_id)
        if campaign.status == CampaignStatus.ACTIVE:
            return {"error": "Campaign already active"}

        # AI scoring: rank segments by predicted ROI
        segments = sorted(
            self._segments.get(campaign_id, []),
            key=lambda s: s.predicted_roi,
            reverse=True,
        )

        total_sends = 0
        total_conversions = 0
        total_revenue = 0.0

        for segment in segments:
            for channel in campaign.channels:
                sends = segment.size
                conv_rate = min(segment.predicted_roi * 0.8, 0.5)  # AI-adjusted rate
                conversions = int(sends * conv_rate)
                revenue_per_conv = self.CHANNEL_REVENUE_MAP.get(channel.value, 30.0)
                revenue = conversions * revenue_per_conv

                total_sends += sends
                total_conversions += conversions
                total_revenue += revenue

        campaign.sends = total_sends
        campaign.conversions = total_conversions
        campaign.attributed_revenue = round(total_revenue, 2)
        campaign.status = CampaignStatus.ACTIVE
        campaign.launched_at = datetime.now(timezone.utc).isoformat()

        return campaign.to_dict()

    def pause_campaign(self, campaign_id: str) -> dict:
        campaign = self._get_campaign(campaign_id)
        campaign.status = CampaignStatus.PAUSED
        return {"campaign_id": campaign_id, "status": campaign.status.value}

    def complete_campaign(self, campaign_id: str) -> dict:
        campaign = self._get_campaign(campaign_id)
        campaign.status = CampaignStatus.COMPLETED
        return {"campaign_id": campaign_id, "status": campaign.status.value}

    # ------------------------------------------------------------------
    # Revenue output (standard DreamCo format)
    # ------------------------------------------------------------------

    def get_revenue_output(self, campaign_id: str) -> dict:
        """Return a standard DreamCo revenue hook dict for this campaign."""
        campaign = self._get_campaign(campaign_id)
        return {
            "revenue": campaign.attributed_revenue,
            "leads_generated": campaign.sends,
            "conversion_rate": campaign.conversion_rate,
            "action": f"Multi-channel campaign '{campaign.name}' via "
                      f"{', '.join(c.value for c in campaign.channels)}",
        }

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def list_campaigns(self) -> List[dict]:
        return [c.to_dict() for c in self._campaigns.values()]

    def get_campaign(self, campaign_id: str) -> dict:
        return self._get_campaign(campaign_id).to_dict()

    def get_total_revenue(self) -> float:
        return round(
            sum(c.attributed_revenue for c in self._campaigns.values()), 2
        )

    def get_segments(self, campaign_id: str) -> List[dict]:
        return [s.to_dict() for s in self._segments.get(campaign_id, [])]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_campaign(self, campaign_id: str) -> Campaign:
        if campaign_id not in self._campaigns:
            raise KeyError(f"Campaign '{campaign_id}' not found.")
        return self._campaigns[campaign_id]
