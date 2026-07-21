"""
DreamCo Money OS — Domain Manager Screen

FlutterFlow-style screen for managing the user's domain portfolio.
Displays owned, listed, and sold domains with buttons to:
    • Register a new domain   (POST /domains)
    • Search domains          (GET /domains?keyword=)
    • Valuate a domain        (GET /domains/valuate?name=)
    • Mark a domain for sale  (PUT /domains/<id>/sell  action=list)
    • Close a sale            (PUT /domains/<id>/sell  action=close)
    • Flip a domain           (POST /domains/flip)
    • View portfolio summary  (GET /domains/summary)
"""

from datetime import datetime


class DomainManagerScreen:
    """
    Domain portfolio management screen for the DreamCo Money OS.

    Fields
    ------
    user_id          : Authenticated user's ID.
    domains          : List of domain records from the portfolio.
    selected_status  : Active status filter (all/owned/listed/sold/flipped).
    portfolio_summary: Aggregate stats dict from GET /domains/summary.
    search_query     : Current domain search keyword.
    search_results   : Results from the most recent domain search.
    last_updated     : ISO timestamp.
    """

    SCREEN_NAME = "DomainManagerScreen"
    ROUTE = "/domains"

    STATUS_FILTERS = ["all", "owned", "listed", "sold", "flipped"]

    def __init__(
        self,
        user_id: str = "",
        domains: list = None,
        selected_status: str = "all",
        portfolio_summary: dict = None,
        search_query: str = "",
        search_results: list = None,
    ):
        self.user_id = user_id
        self.domains = domains or []
        self.selected_status = selected_status
        self.portfolio_summary = portfolio_summary or {}
        self.search_query = search_query
        self.search_results = search_results or []
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> dict:
        """Return the screen's UI data model for FlutterFlow rendering."""
        filtered = (
            [d for d in self.domains if d.get("status") == self.selected_status]
            if self.selected_status != "all"
            else self.domains
        )

        s = self.portfolio_summary
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "header": {
                    "title": "Domain Manager",
                    "subtitle": "Manage, sell, and flip your domain portfolio",
                },
                # ---- Portfolio summary card ----
                "portfolio_summary_card": {
                    "total_domains": s.get("total_domains", len(self.domains)),
                    "owned": s.get("owned", 0),
                    "listed": s.get("listed", 0),
                    "sold": s.get("sold", 0),
                    "flipped": s.get("flipped", 0),
                    "total_invested": f"${s.get('total_invested_usd', 0):,.2f}",
                    "total_revenue": f"${s.get('total_revenue_usd', 0):,.2f}",
                    "total_profit": f"${s.get('total_profit_usd', 0):,.2f}",
                    "portfolio_value": f"${s.get('portfolio_estimated_value_usd', 0):,.2f}",
                    "summary_button": {
                        "id": "btn_refresh_summary",
                        "label": "Refresh Summary",
                        "action": "GET /domains/summary",
                        "icon": "refresh",
                    },
                },
                # ---- Domain search ----
                "search_section": {
                    "search_bar": {
                        "placeholder": "Search domain keyword (e.g. dreamco)",
                        "value": self.search_query,
                        "action": "GET /domains?keyword=<query>",
                    },
                    "valuate_button": {
                        "id": "btn_valuate",
                        "label": "Valuate a Domain",
                        "action": "GET /domains/valuate?name=<domain>",
                        "icon": "attach_money",
                    },
                    "search_results": {
                        "count": len(self.search_results),
                        "items": [
                            {
                                "name": r.get("name"),
                                "available": r.get("available"),
                                "price_usd": r.get("price_usd"),
                                "estimated_value_usd": r.get("estimated_value_usd"),
                                "register_button": {
                                    "id": f"btn_register_{r.get('name', '').replace('.', '_')}",
                                    "label": "Register",
                                    "action": "POST /domains",
                                    "enabled": r.get("available", False),
                                    "color": "primary",
                                },
                            }
                            for r in self.search_results
                        ],
                    },
                },
                # ---- Action buttons ----
                "action_buttons": [
                    {
                        "id": "btn_register_domain",
                        "label": "Register New Domain",
                        "action": "POST /domains",
                        "icon": "add_circle",
                        "color": "primary",
                    },
                    {
                        "id": "btn_flip_domain",
                        "label": "Record a Flip",
                        "action": "POST /domains/flip",
                        "icon": "swap_horiz",
                        "color": "success",
                    },
                ],
                # ---- Status filter ----
                "filter_row": {
                    "options": self.STATUS_FILTERS,
                    "selected": self.selected_status,
                    "action": "GET /domains?status=<status>",
                },
                # ---- Domain list ----
                "domains_list": {
                    "count": len(filtered),
                    "items": [
                        {
                            "domain_id": d.get("domain_id"),
                            "name": d.get("name"),
                            "registrar": d.get("registrar"),
                            "status": d.get("status"),
                            "registration_cost_usd": d.get("registration_cost_usd"),
                            "ask_price_usd": d.get("ask_price_usd"),
                            "sold_price_usd": d.get("sold_price_usd"),
                            "profit_usd": d.get("profit_usd"),
                            "estimated_value_usd": d.get("estimated_value_usd"),
                            "expiry_date": d.get("expiry_date"),
                            "sell_button": {
                                "id": f"btn_sell_{d.get('domain_id')}",
                                "label": "List for Sale" if d.get("status") == "owned" else "Close Sale",
                                "action": f"PUT /domains/{d.get('domain_id')}/sell",
                                "color": "warning",
                                "enabled": d.get("status") in ("owned", "listed"),
                            },
                        }
                        for d in filtered
                    ],
                },
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        """Serialise all screen state to a plain dict."""
        return {
            "screen": self.SCREEN_NAME,
            "user_id": self.user_id,
            "domains": self.domains,
            "selected_status": self.selected_status,
            "portfolio_summary": self.portfolio_summary,
            "search_query": self.search_query,
            "search_results": self.search_results,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "DomainManagerScreen":
        """Return a pre-populated demo instance."""
        return cls(
            user_id="usr_demo0000000000",
            domains=[
                {
                    "domain_id": "dom_a1b2c3d4",
                    "name": "dreamco.io",
                    "registrar": "Namecheap",
                    "status": "owned",
                    "registration_cost_usd": 39.99,
                    "ask_price_usd": None,
                    "sold_price_usd": None,
                    "profit_usd": None,
                    "estimated_value_usd": 2499.99,
                    "expiry_date": "2026-03-15",
                },
                {
                    "domain_id": "dom_e5f6a7b8",
                    "name": "aibot.com",
                    "registrar": "GoDaddy",
                    "status": "listed",
                    "registration_cost_usd": 12.99,
                    "ask_price_usd": 4999.0,
                    "sold_price_usd": None,
                    "profit_usd": None,
                    "estimated_value_usd": 5800.0,
                    "expiry_date": "2025-11-01",
                },
                {
                    "domain_id": "dom_c9d0e1f2",
                    "name": "earnmore.ai",
                    "registrar": "Namecheap",
                    "status": "flipped",
                    "registration_cost_usd": 89.99,
                    "ask_price_usd": None,
                    "sold_price_usd": 3200.0,
                    "profit_usd": 3110.01,
                    "estimated_value_usd": 0.0,
                    "expiry_date": None,
                },
            ],
            selected_status="all",
            portfolio_summary={
                "total_domains": 3,
                "owned": 1,
                "listed": 1,
                "sold": 0,
                "flipped": 1,
                "total_invested_usd": 142.97,
                "total_revenue_usd": 3200.0,
                "total_profit_usd": 3057.03,
                "portfolio_estimated_value_usd": 8299.99,
            },
            search_query="",
            search_results=[],
        )
