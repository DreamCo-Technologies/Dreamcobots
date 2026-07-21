"""Tests for bots/buyer_network/buyer_network.py"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.buyer_network.buyer_network import BuyerNetwork, Buyer, Deal, DealStatus, AuctionBid


# ---------------------------------------------------------------------------
# Buyer registration
# ---------------------------------------------------------------------------

class TestRegisterBuyer:
    def setup_method(self):
        self.network = BuyerNetwork()

    def test_returns_buyer(self):
        buyer = self.network.register_buyer("Alice", "alice@ex.com", "+1555", ["Chicago"], 150_000)
        assert isinstance(buyer, Buyer)

    def test_buyer_id_assigned(self):
        buyer = self.network.register_buyer("Bob", "bob@ex.com", "+1556", ["Atlanta"], 100_000)
        assert buyer.buyer_id.startswith("buyer_")

    def test_buyer_active_by_default(self):
        buyer = self.network.register_buyer("Carol", "c@ex.com", "+1557", ["Dallas"], 200_000)
        assert buyer.active is True

    def test_deactivate_buyer(self):
        buyer = self.network.register_buyer("Dave", "d@ex.com", "+1558", ["Miami"], 80_000)
        result = self.network.deactivate_buyer(buyer.buyer_id)
        assert result is True
        assert not self.network._buyers[buyer.buyer_id].active

    def test_list_buyers_excludes_inactive(self):
        buyer = self.network.register_buyer("Eve", "e@ex.com", "+1559", ["Seattle"], 120_000)
        self.network.deactivate_buyer(buyer.buyer_id)
        buyers = self.network.list_buyers()
        assert all(b["active"] for b in buyers)


# ---------------------------------------------------------------------------
# Deal submission
# ---------------------------------------------------------------------------

class TestSubmitDeal:
    def setup_method(self):
        self.network = BuyerNetwork()

    def test_returns_deal(self):
        deal = self.network.submit_deal("123 Oak", "Chicago", 90_000, beds=3)
        assert isinstance(deal, Deal)

    def test_deal_id_assigned(self):
        deal = self.network.submit_deal("456 Elm", "Atlanta", 75_000, beds=2)
        assert deal.deal_id.startswith("deal_")

    def test_deal_status_available(self):
        deal = self.network.submit_deal("789 Pine", "Dallas", 60_000, beds=4)
        assert deal.status == DealStatus.AVAILABLE

    def test_get_deal_by_id(self):
        deal = self.network.submit_deal("Addr", "Chicago", 80_000, beds=3)
        fetched = self.network.get_deal(deal.deal_id)
        assert fetched["deal_id"] == deal.deal_id

    def test_get_nonexistent_deal_raises(self):
        with pytest.raises(KeyError):
            self.network.get_deal("deal_nonexistent")


# ---------------------------------------------------------------------------
# Buyer matching
# ---------------------------------------------------------------------------

class TestMatchBuyers:
    def setup_method(self):
        self.network = BuyerNetwork()
        self.network.register_buyer("Alice", "a@ex.com", "+1", ["Chicago"], 150_000, min_beds=2)
        self.network.register_buyer("Bob", "b@ex.com", "+2", ["Atlanta"], 80_000, min_beds=0)

    def test_matches_buyer_in_region(self):
        deal = self.network.submit_deal("123 Oak", "Chicago", 90_000, beds=3)
        matches = self.network.match_buyers(deal.deal_id)
        assert any(m["name"] == "Alice" for m in matches)

    def test_excludes_buyer_wrong_region(self):
        deal = self.network.submit_deal("456 Elm", "Chicago", 90_000, beds=3)
        matches = self.network.match_buyers(deal.deal_id)
        assert not any(m["name"] == "Bob" for m in matches)

    def test_excludes_buyer_price_too_high(self):
        deal = self.network.submit_deal("789 Pine", "Atlanta", 200_000, beds=2)
        matches = self.network.match_buyers(deal.deal_id)
        assert not any(m["name"] == "Bob" for m in matches)

    def test_excludes_buyer_insufficient_beds(self):
        deal = self.network.submit_deal("321 Maple", "Chicago", 100_000, beds=1)
        matches = self.network.match_buyers(deal.deal_id)
        # Alice requires min_beds=2 so should be excluded
        assert not any(m["name"] == "Alice" for m in matches)

    def test_matched_buyers_stored_on_deal(self):
        deal = self.network.submit_deal("Test", "Chicago", 100_000, beds=3)
        self.network.match_buyers(deal.deal_id)
        assert len(deal.matched_buyers) >= 1


# ---------------------------------------------------------------------------
# Auction
# ---------------------------------------------------------------------------

class TestAuction:
    def setup_method(self):
        self.network = BuyerNetwork()
        self.buyer = self.network.register_buyer("Alice", "a@ex.com", "+1", ["Chicago"], 200_000)
        self.deal = self.network.submit_deal("123 Main", "Chicago", 90_000, beds=3)

    def test_place_bid_returns_auction_bid(self):
        bid = self.network.place_bid(self.deal.deal_id, self.buyer.buyer_id, 6_000)
        assert isinstance(bid, AuctionBid)

    def test_place_bid_unavailable_deal_raises(self):
        self.network.run_auction(self.deal.deal_id)
        with pytest.raises(ValueError):
            self.network.place_bid(self.deal.deal_id, self.buyer.buyer_id, 7_000)

    def test_run_auction_selects_highest_bid(self):
        buyer2 = self.network.register_buyer("Bob", "b@ex.com", "+2", ["Chicago"], 200_000)
        self.network.place_bid(self.deal.deal_id, self.buyer.buyer_id, 5_000)
        self.network.place_bid(self.deal.deal_id, buyer2.buyer_id, 8_000)
        result = self.network.run_auction(self.deal.deal_id)
        assert result["winning_buyer_id"] == buyer2.buyer_id
        assert result["assignment_fee"] == pytest.approx(8_000)

    def test_run_auction_updates_deal_status(self):
        self.network.place_bid(self.deal.deal_id, self.buyer.buyer_id, 5_500)
        self.network.run_auction(self.deal.deal_id)
        assert self.deal.status == DealStatus.UNDER_CONTRACT

    def test_run_auction_no_buyers_returns_no_buyers(self):
        deal2 = self.network.submit_deal("456 Elm", "Timbuktu", 90_000, beds=3)
        result = self.network.run_auction(deal2.deal_id)
        assert result["status"] == "no_buyers"


# ---------------------------------------------------------------------------
# Revenue output
# ---------------------------------------------------------------------------

class TestRevenueOutput:
    def test_revenue_output_keys(self):
        network = BuyerNetwork()
        output = network.get_revenue_output()
        for key in ("revenue", "leads_generated", "conversion_rate", "action"):
            assert key in output

    def test_revenue_increases_after_closed_deal(self):
        network = BuyerNetwork()
        buyer = network.register_buyer("A", "a@ex.com", "+1", ["Chicago"], 200_000)
        deal = network.submit_deal("123 Main", "Chicago", 90_000, beds=3)
        network.place_bid(deal.deal_id, buyer.buyer_id, 7_000)
        network.run_auction(deal.deal_id)
        output = network.get_revenue_output()
        assert output["revenue"] == pytest.approx(7_000)


# ---------------------------------------------------------------------------
# Pipeline stats
# ---------------------------------------------------------------------------

class TestPipelineStats:
    def test_stats_keys(self):
        network = BuyerNetwork()
        stats = network.get_pipeline_stats()
        for key in ("total_deals", "available", "closed", "total_revenue", "active_buyers"):
            assert key in stats

    def test_region_filter(self):
        network = BuyerNetwork()
        network.submit_deal("A", "Chicago", 50_000, beds=2)
        network.submit_deal("B", "Atlanta", 60_000, beds=3)
        stats = network.get_pipeline_stats(region="Chicago")
        assert stats["total_deals"] == 1
