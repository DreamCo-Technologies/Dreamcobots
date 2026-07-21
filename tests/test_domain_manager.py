"""
Tests for bots/business_launch_pad/domain_manager.py — DomainManager.
"""

import pytest
from bots.business_launch_pad.domain_manager import (
    DomainManager,
    DomainManagerError,
    PortfolioDomain,
    PortfolioDomainStatus,
    _estimate_value,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mgr() -> DomainManager:
    return DomainManager()


UID = "usr_abc123"


def _reg(mgr, name="example.com", uid=UID, cost=12.99):
    return mgr.register(name, user_id=uid, registration_cost_usd=cost)


# ===========================================================================
# _estimate_value
# ===========================================================================

class TestEstimateValue:
    def test_positive(self):
        assert _estimate_value("dreamco.com", 12.99) > 0

    def test_com_higher_than_org(self):
        val_com = _estimate_value("dreamco.com", 12.99)
        val_org = _estimate_value("dreamco.org", 12.99)
        assert val_com > val_org

    def test_short_name_higher(self):
        short = _estimate_value("ab.com", 12.99)
        long = _estimate_value("averylongdomainname.com", 12.99)
        assert short > long

    def test_ai_tld_premium(self):
        val_ai = _estimate_value("dream.ai", 89.0)
        val_net = _estimate_value("dream.net", 12.99)
        # .ai multiplier (2.0) × base should exceed .net (0.9)
        assert val_ai > val_net


# ===========================================================================
# register
# ===========================================================================

class TestRegister:
    def test_returns_portfolio_domain(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        assert isinstance(dom, PortfolioDomain)

    def test_status_is_owned(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        assert dom.status == PortfolioDomainStatus.OWNED

    def test_name_normalised_lowercase(self):
        mgr = make_mgr()
        dom = mgr.register("EXAMPLE.COM", user_id=UID)
        assert dom.name == "example.com"

    def test_estimated_value_set(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        assert dom.estimated_value_usd > 0

    def test_domain_id_starts_with_dom(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        assert dom.domain_id.startswith("dom_")

    def test_blank_name_raises(self):
        mgr = make_mgr()
        with pytest.raises(DomainManagerError, match="empty"):
            mgr.register("", user_id=UID)

    def test_negative_cost_raises(self):
        mgr = make_mgr()
        with pytest.raises(DomainManagerError, match="non-negative"):
            mgr.register("ok.com", user_id=UID, registration_cost_usd=-1)

    def test_duplicate_raises(self):
        mgr = make_mgr()
        _reg(mgr, name="unique.io")
        with pytest.raises(DomainManagerError, match="already in the portfolio"):
            _reg(mgr, name="unique.io")

    def test_duplicate_allowed_after_sold(self):
        mgr = make_mgr()
        dom = _reg(mgr, name="resell.com")
        mgr.mark_for_sale(dom.domain_id, UID, ask_price_usd=999.0)
        mgr.close_sale(dom.domain_id, UID, sold_price_usd=999.0)
        # Same domain can now be re-registered
        dom2 = _reg(mgr, name="resell.com")
        assert dom2.domain_id != dom.domain_id

    def test_different_users_can_own_same_domain(self):
        mgr = make_mgr()
        d1 = mgr.register("shared.io", user_id="usr_a")
        d2 = mgr.register("shared.io", user_id="usr_b")
        assert d1.domain_id != d2.domain_id


# ===========================================================================
# list_portfolio
# ===========================================================================

class TestListPortfolio:
    def test_returns_all_owned(self):
        mgr = make_mgr()
        _reg(mgr, name="a.com")
        _reg(mgr, name="b.com")
        assert len(mgr.list_portfolio(UID)) == 2

    def test_filter_by_owned(self):
        mgr = make_mgr()
        dom = _reg(mgr, name="c.com")
        mgr.mark_for_sale(dom.domain_id, UID, 500)
        owned = mgr.list_portfolio(UID, status="owned")
        assert len(owned) == 0

    def test_filter_by_listed(self):
        mgr = make_mgr()
        dom = _reg(mgr, name="d.com")
        mgr.mark_for_sale(dom.domain_id, UID, 500)
        listed = mgr.list_portfolio(UID, status="listed")
        assert len(listed) == 1

    def test_filter_invalid_status_raises(self):
        mgr = make_mgr()
        with pytest.raises(DomainManagerError, match="Invalid status"):
            mgr.list_portfolio(UID, status="unknown")

    def test_other_user_excluded(self):
        mgr = make_mgr()
        mgr.register("e.com", user_id="usr_other")
        assert mgr.list_portfolio(UID) == []

    def test_sorted_newest_first(self):
        mgr = make_mgr()
        d1 = _reg(mgr, name="first.com")
        d2 = _reg(mgr, name="second.com")
        listing = mgr.list_portfolio(UID)
        assert listing[0].domain_id == d2.domain_id


# ===========================================================================
# get_domain
# ===========================================================================

class TestGetDomain:
    def test_returns_correct_domain(self):
        mgr = make_mgr()
        dom = _reg(mgr, name="getme.com")
        found = mgr.get_domain(dom.domain_id, UID)
        assert found.domain_id == dom.domain_id

    def test_wrong_user_raises_key_error(self):
        mgr = make_mgr()
        dom = mgr.register("mine.com", user_id="usr_owner")
        with pytest.raises(KeyError):
            mgr.get_domain(dom.domain_id, "usr_other")

    def test_nonexistent_raises_key_error(self):
        mgr = make_mgr()
        with pytest.raises(KeyError):
            mgr.get_domain("dom_xxxxxxxx", UID)


# ===========================================================================
# valuate
# ===========================================================================

class TestValuate:
    def test_updates_estimated_value(self):
        mgr = make_mgr()
        dom = _reg(mgr, name="revalue.ai")
        old = dom.estimated_value_usd
        dom.estimated_value_usd = 0.0  # manually zero it
        mgr.valuate(dom.domain_id, UID)
        assert mgr.get_domain(dom.domain_id, UID).estimated_value_usd > 0


# ===========================================================================
# mark_for_sale
# ===========================================================================

class TestMarkForSale:
    def test_status_becomes_listed(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        mgr.mark_for_sale(dom.domain_id, UID, 999.0)
        assert mgr.get_domain(dom.domain_id, UID).status == PortfolioDomainStatus.LISTED

    def test_ask_price_set(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        mgr.mark_for_sale(dom.domain_id, UID, 1234.56)
        assert mgr.get_domain(dom.domain_id, UID).ask_price_usd == 1234.56

    def test_zero_ask_price_raises(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        with pytest.raises(DomainManagerError, match="greater than zero"):
            mgr.mark_for_sale(dom.domain_id, UID, 0.0)

    def test_already_listed_raises(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        mgr.mark_for_sale(dom.domain_id, UID, 500.0)
        with pytest.raises(DomainManagerError, match="OWNED"):
            mgr.mark_for_sale(dom.domain_id, UID, 600.0)


# ===========================================================================
# close_sale
# ===========================================================================

class TestCloseSale:
    def test_status_becomes_sold(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        mgr.mark_for_sale(dom.domain_id, UID, 500.0)
        mgr.close_sale(dom.domain_id, UID, 450.0)
        assert mgr.get_domain(dom.domain_id, UID).status == PortfolioDomainStatus.SOLD

    def test_profit_calculated(self):
        mgr = make_mgr()
        dom = _reg(mgr, cost=12.99)
        mgr.mark_for_sale(dom.domain_id, UID, 500.0)
        mgr.close_sale(dom.domain_id, UID, 500.0)
        closed = mgr.get_domain(dom.domain_id, UID)
        assert closed.profit_usd == pytest.approx(500.0 - 12.99, abs=0.01)

    def test_zero_sold_price_raises(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        mgr.mark_for_sale(dom.domain_id, UID, 500.0)
        with pytest.raises(DomainManagerError, match="greater than zero"):
            mgr.close_sale(dom.domain_id, UID, 0.0)

    def test_not_listed_raises(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        with pytest.raises(DomainManagerError, match="LISTED"):
            mgr.close_sale(dom.domain_id, UID, 300.0)


# ===========================================================================
# flip_domain
# ===========================================================================

class TestFlipDomain:
    def test_status_is_flipped(self):
        mgr = make_mgr()
        dom = mgr.flip_domain("flipped.io", UID, buy_price_usd=30.0, sell_price_usd=2000.0)
        assert dom.status == PortfolioDomainStatus.FLIPPED

    def test_profit_calculated(self):
        mgr = make_mgr()
        dom = mgr.flip_domain("profit.com", UID, buy_price_usd=12.99, sell_price_usd=1500.0)
        assert dom.profit_usd == pytest.approx(1500.0 - 12.99, abs=0.01)

    def test_zero_sell_price_raises(self):
        mgr = make_mgr()
        with pytest.raises(DomainManagerError, match="greater than zero"):
            mgr.flip_domain("zero.com", UID, buy_price_usd=10.0, sell_price_usd=0.0)

    def test_sold_price_set(self):
        mgr = make_mgr()
        dom = mgr.flip_domain("sold.ai", UID, buy_price_usd=89.99, sell_price_usd=4000.0)
        assert dom.sold_price_usd == 4000.0


# ===========================================================================
# portfolio_summary
# ===========================================================================

class TestPortfolioSummary:
    def setup_method(self):
        self.mgr = make_mgr()
        # owned domain
        _reg(self.mgr, name="owned.com", cost=12.99)
        # listed domain
        dom2 = _reg(self.mgr, name="listed.io", cost=39.99)
        self.mgr.mark_for_sale(dom2.domain_id, UID, 4999.0)
        # sold domain
        dom3 = _reg(self.mgr, name="sold.co", cost=14.99)
        self.mgr.mark_for_sale(dom3.domain_id, UID, 1000.0)
        self.mgr.close_sale(dom3.domain_id, UID, 1000.0)
        # flipped domain
        self.mgr.flip_domain("flipped.net", UID, buy_price_usd=9.99, sell_price_usd=600.0)

    def test_total_domains(self):
        s = self.mgr.portfolio_summary(UID)
        assert s["total_domains"] == 4

    def test_counts_by_status(self):
        s = self.mgr.portfolio_summary(UID)
        assert s["owned"] == 1
        assert s["listed"] == 1
        assert s["sold"] == 1
        assert s["flipped"] == 1

    def test_total_invested(self):
        s = self.mgr.portfolio_summary(UID)
        assert s["total_invested_usd"] == pytest.approx(12.99 + 39.99 + 14.99 + 9.99, abs=0.01)

    def test_total_revenue(self):
        s = self.mgr.portfolio_summary(UID)
        assert s["total_revenue_usd"] == pytest.approx(1000.0 + 600.0, abs=0.01)

    def test_total_profit(self):
        s = self.mgr.portfolio_summary(UID)
        invested = 12.99 + 39.99 + 14.99 + 9.99
        revenue = 1000.0 + 600.0
        assert s["total_profit_usd"] == pytest.approx(revenue - invested, abs=0.01)

    def test_empty_user(self):
        s = self.mgr.portfolio_summary("usr_nobody")
        assert s["total_domains"] == 0
        assert s["total_profit_usd"] == 0.0


# ===========================================================================
# to_dict
# ===========================================================================

class TestPortfolioDomainToDict:
    def test_has_expected_keys(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        d = dom.to_dict()
        for key in ("domain_id", "name", "registrar", "registration_cost_usd",
                    "ask_price_usd", "status", "registered_at", "expiry_date",
                    "estimated_value_usd", "sold_price_usd", "profit_usd",
                    "user_id", "notes"):
            assert key in d

    def test_status_is_string(self):
        mgr = make_mgr()
        dom = _reg(mgr)
        d = dom.to_dict()
        assert isinstance(d["status"], str)
