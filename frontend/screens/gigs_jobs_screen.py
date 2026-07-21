"""
DreamCo Money OS — Gigs & Jobs Screen

FlutterFlow-style screen for discovering and managing Fiverr gigs and
job opportunities from multiple platforms.
"""

from datetime import datetime


class GigsJobsScreen:
    """
    Unified gigs and jobs feed from Fiverr, job boards, and freelance platforms.

    Fields
    ------
    fiverr_gigs      : Active / recommended Fiverr gig opportunities.
    job_listings     : Job listings from job boards (Indeed, LinkedIn, etc.).
    active_gigs      : User's currently live gigs.
    earnings_this_month : Gig + job earnings this month.
    filter_platform  : Active platform filter.
    filter_category  : Active category filter.
    sort_by          : 'earnings' | 'rating' | 'demand'.
    last_updated     : ISO timestamp.
    """

    SCREEN_NAME = "GigsJobsScreen"
    ROUTE = "/gigs-jobs"

    def __init__(
        self,
        fiverr_gigs: list = None,
        job_listings: list = None,
        active_gigs: list = None,
        earnings_this_month: float = 0.0,
        filter_platform: str = "all",
        filter_category: str = "all",
        sort_by: str = "earnings",
    ):
        self.fiverr_gigs = fiverr_gigs or []
        self.job_listings = job_listings or []
        self.active_gigs = active_gigs or []
        self.earnings_this_month = earnings_this_month
        self.filter_platform = filter_platform
        self.filter_category = filter_category
        self.sort_by = sort_by
        self.last_updated = datetime.utcnow().isoformat() + "Z"

    def render(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "route": self.ROUTE,
            "widgets": {
                "earnings_banner": {
                    "value": f"${self.earnings_this_month:,.2f}",
                    "label": "Earned This Month",
                    "color": "green",
                },
                "filter_row": {
                    "platform": self.filter_platform,
                    "category": self.filter_category,
                    "sort_by": self.sort_by,
                },
                "active_gigs_section": {
                    "title": "⚡ Your Active Gigs",
                    "count": len(self.active_gigs),
                    "items": self.active_gigs,
                },
                "fiverr_section": {
                    "title": "🎯 Fiverr Opportunities",
                    "count": len(self.fiverr_gigs),
                    "items": self.fiverr_gigs,
                },
                "jobs_section": {
                    "title": "💼 Job Listings",
                    "count": len(self.job_listings),
                    "items": self.job_listings,
                },
            },
            "last_updated": self.last_updated,
        }

    def to_dict(self) -> dict:
        return {
            "screen": self.SCREEN_NAME,
            "fiverr_gigs": self.fiverr_gigs,
            "job_listings": self.job_listings,
            "active_gigs": self.active_gigs,
            "earnings_this_month": self.earnings_this_month,
            "filter_platform": self.filter_platform,
            "filter_category": self.filter_category,
            "sort_by": self.sort_by,
            "last_updated": self.last_updated,
        }

    @classmethod
    def demo(cls) -> "GigsJobsScreen":
        return cls(
            fiverr_gigs=[
                {"gig_id": "GIG-001", "title": "I will build your Python automation bot",
                 "price": 150, "delivery_days": 3, "platform": "fiverr",
                 "category": "programming", "orders_completed": 47, "rating": 4.9},
                {"gig_id": "GIG-002", "title": "I will create a professional logo",
                 "price": 50, "delivery_days": 2, "platform": "fiverr",
                 "category": "design", "orders_completed": 123, "rating": 5.0},
            ],
            job_listings=[
                {"id": "JOB-001", "title": "Remote Python Developer", "company": "TechCorp",
                 "platform": "indeed", "salary": "$90,000 - $130,000", "location": "Remote"},
                {"id": "JOB-002", "title": "Data Analyst", "company": "DataCo",
                 "platform": "linkedin", "salary": "$75,000 - $95,000", "location": "Remote"},
            ],
            active_gigs=[
                {"gig_id": "GIG-001", "title": "Python automation bot", "status": "active",
                 "pending_orders": 3, "earnings_this_month": 450},
            ],
            earnings_this_month=847.30,
            filter_platform="fiverr",
            filter_category="programming",
        )
