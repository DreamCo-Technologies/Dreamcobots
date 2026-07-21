"""Tests for bots/multi_channel_marketing/multi_channel_marketing.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.multi_channel_marketing.multi_channel_marketing import (
    MultiChannelMarketing,
    Campaign,
    CampaignChannel,
    CampaignStatus,
    AudienceSegment,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_campaign(mcm=None, channels=None):
    mcm = mcm or MultiChannelMarketing()
    channels = channels or [CampaignChannel.SMS, CampaignChannel.EMAIL]
    campaign = mcm.create_campaign("Test Campaign", channels, "Hello {name}!")
    return mcm, campaign


# ---------------------------------------------------------------------------
# create_campaign
# ---------------------------------------------------------------------------

class TestCreateCampaign:
    def test_returns_campaign(self):
        mcm, campaign = _make_campaign()
        assert isinstance(campaign, Campaign)

    def test_campaign_id_assigned(self):
        mcm, campaign = _make_campaign()
        assert campaign.campaign_id.startswith("camp_")

    def test_status_draft(self):
        mcm, campaign = _make_campaign()
        assert campaign.status == CampaignStatus.DRAFT

    def test_channels_stored(self):
        mcm, campaign = _make_campaign(channels=[CampaignChannel.TIKTOK])
        assert CampaignChannel.TIKTOK in campaign.channels

    def test_list_campaigns(self):
        mcm = MultiChannelMarketing()
        mcm.create_campaign("A", [CampaignChannel.SMS], "msg1")
        mcm.create_campaign("B", [CampaignChannel.EMAIL], "msg2")
        assert len(mcm.list_campaigns()) == 2


# ---------------------------------------------------------------------------
# add_segment
# ---------------------------------------------------------------------------

class TestAddSegment:
    def test_returns_audience_segment(self):
        mcm, campaign = _make_campaign()
        seg = mcm.add_segment(campaign.campaign_id, "Chicago", 500, predicted_roi=0.12)
        assert isinstance(seg, AudienceSegment)

    def test_audience_size_updated(self):
        mcm, campaign = _make_campaign()
        mcm.add_segment(campaign.campaign_id, "Chicago", 300, 0.1)
        mcm.add_segment(campaign.campaign_id, "Atlanta", 200, 0.08)
        assert campaign.audience_size == 500

    def test_segment_id_assigned(self):
        mcm, campaign = _make_campaign()
        seg = mcm.add_segment(campaign.campaign_id, "Test", 100, 0.1)
        assert seg.segment_id.startswith("seg_")

    def test_invalid_campaign_raises(self):
        mcm = MultiChannelMarketing()
        with pytest.raises(KeyError):
            mcm.add_segment("invalid_id", "Seg", 100, 0.1)


# ---------------------------------------------------------------------------
# launch_campaign
# ---------------------------------------------------------------------------

class TestLaunchCampaign:
    def test_campaign_status_active_after_launch(self):
        mcm, campaign = _make_campaign()
        mcm.add_segment(campaign.campaign_id, "Chicago", 500, 0.15)
        result = mcm.launch_campaign(campaign.campaign_id)
        assert campaign.status == CampaignStatus.ACTIVE

    def test_sends_greater_than_zero_with_segment(self):
        mcm, campaign = _make_campaign()
        mcm.add_segment(campaign.campaign_id, "Chicago", 500, 0.15)
        mcm.launch_campaign(campaign.campaign_id)
        assert campaign.sends > 0

    def test_attributed_revenue_positive(self):
        mcm, campaign = _make_campaign()
        mcm.add_segment(campaign.campaign_id, "Chicago", 200, 0.2)
        mcm.launch_campaign(campaign.campaign_id)
        assert campaign.attributed_revenue > 0

    def test_launch_twice_returns_error(self):
        mcm, campaign = _make_campaign()
        mcm.add_segment(campaign.campaign_id, "Seg", 100, 0.1)
        mcm.launch_campaign(campaign.campaign_id)
        result = mcm.launch_campaign(campaign.campaign_id)
        assert "error" in result

    def test_no_segments_gives_zero_sends(self):
        mcm, campaign = _make_campaign()
        mcm.launch_campaign(campaign.campaign_id)
        assert campaign.sends == 0


# ---------------------------------------------------------------------------
# get_revenue_output
# ---------------------------------------------------------------------------

class TestGetRevenueOutput:
    def test_revenue_output_keys(self):
        mcm, campaign = _make_campaign()
        mcm.add_segment(campaign.campaign_id, "Seg", 200, 0.15)
        mcm.launch_campaign(campaign.campaign_id)
        output = mcm.get_revenue_output(campaign.campaign_id)
        for key in ("revenue", "leads_generated", "conversion_rate", "action"):
            assert key in output

    def test_revenue_matches_attributed(self):
        mcm, campaign = _make_campaign()
        mcm.add_segment(campaign.campaign_id, "Seg", 200, 0.15)
        mcm.launch_campaign(campaign.campaign_id)
        output = mcm.get_revenue_output(campaign.campaign_id)
        assert output["revenue"] == pytest.approx(campaign.attributed_revenue)


# ---------------------------------------------------------------------------
# pause / complete
# ---------------------------------------------------------------------------

class TestPauseComplete:
    def test_pause_campaign(self):
        mcm, campaign = _make_campaign()
        mcm.pause_campaign(campaign.campaign_id)
        assert campaign.status == CampaignStatus.PAUSED

    def test_complete_campaign(self):
        mcm, campaign = _make_campaign()
        mcm.complete_campaign(campaign.campaign_id)
        assert campaign.status == CampaignStatus.COMPLETED


# ---------------------------------------------------------------------------
# get_total_revenue
# ---------------------------------------------------------------------------

class TestGetTotalRevenue:
    def test_total_revenue_sums_campaigns(self):
        mcm = MultiChannelMarketing()
        c1 = mcm.create_campaign("C1", [CampaignChannel.SMS], "msg")
        c2 = mcm.create_campaign("C2", [CampaignChannel.EMAIL], "msg")
        mcm.add_segment(c1.campaign_id, "S1", 100, 0.2)
        mcm.add_segment(c2.campaign_id, "S2", 50, 0.1)
        mcm.launch_campaign(c1.campaign_id)
        mcm.launch_campaign(c2.campaign_id)
        total = mcm.get_total_revenue()
        assert total == pytest.approx(c1.attributed_revenue + c2.attributed_revenue)
