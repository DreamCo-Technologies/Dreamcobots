"""FastAPI backend: exposes endpoints to control FiverrBot and LeadGenBot."""
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.dream_core import DreamCore
from core.monetization_hooks import MonetizationHooks
from core.revenue_engine import RevenueEngine
from Fiverr_bots.fiverr_bot import FiverrBot
from bots.lead_gen_bot.lead_gen_bot import LeadGenBot
from dreamco_platform.swarm.stigmergy import PersistentStigmergyEnvironment

app = FastAPI(title="DreamCo Bot API", version="1.0.0")

# Shared infrastructure (singleton per process)
_revenue_engine = RevenueEngine()
_monetization_hooks = MonetizationHooks()
_dream_core = DreamCore()
_stigmergy_environment = PersistentStigmergyEnvironment()

# Bot instances (created on-demand per request for statelessness)
def _make_fiverr_bot() -> FiverrBot:
    return FiverrBot(
        revenue_engine=_revenue_engine,
        monetization_hooks=_monetization_hooks,
    )


def _make_lead_gen_bot() -> LeadGenBot:
    db_dsn = os.environ.get("DATABASE_URL")
    return LeadGenBot(
        db_dsn=db_dsn,
        revenue_engine=_revenue_engine,
        monetization_hooks=_monetization_hooks,
        dream_core=_dream_core,
    )


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class GigRequest(BaseModel):
    title: str
    keywords: List[str]
    word_count: int = 500


class GigResponse(BaseModel):
    title: str
    keywords: List[str]
    content: str
    revenue: float


class LeadScrapeRequest(BaseModel):
    html: str


class LeadResponse(BaseModel):
    name: str
    email: str
    phone: str
    company: str
    url: str


class RevenueResponse(BaseModel):
    total_usd: float
    entries: List[dict]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# FiverrBot endpoints
# ---------------------------------------------------------------------------

@app.post("/fiverr/generate-gig", response_model=GigResponse)
def generate_gig(request: GigRequest) -> GigResponse:
    """Generate a single SEO content gig and return the result."""
    bot = _make_fiverr_bot()
    bot.add_gig(request.title, request.keywords, request.word_count)
    bot.run()
    completed = bot.get_completed_gigs()
    if not completed:
        raise HTTPException(status_code=500, detail="Gig generation failed.")
    gig = completed[0]
    return GigResponse(
        title=gig["title"],
        keywords=gig["keywords"],
        content=gig["content"],
        revenue=gig["revenue"],
    )


@app.post("/fiverr/run-batch")
def run_fiverr_batch(gigs: List[GigRequest]) -> dict:
    """Process a batch of SEO gigs."""
    bot = _make_fiverr_bot()
    for gig_req in gigs:
        bot.add_gig(gig_req.title, gig_req.keywords, gig_req.word_count)
    bot.run()
    return {
        "completed": len(bot.get_completed_gigs()),
        "revenue": bot.revenue_engine.total(),
    }


# ---------------------------------------------------------------------------
# LeadGenBot endpoints
# ---------------------------------------------------------------------------

@app.post("/leads/scrape", response_model=List[LeadResponse])
def scrape_leads(request: LeadScrapeRequest) -> List[LeadResponse]:
    """Scrape leads from a provided HTML snippet."""
    bot = _make_lead_gen_bot()
    leads = bot.scrape_html(request.html)
    return [LeadResponse(**lead) for lead in leads]


@app.post("/leads/run-outreach")
def run_lead_outreach(request: LeadScrapeRequest) -> dict:
    """Scrape leads, generate outreach emails, and record revenue."""
    bot = _make_lead_gen_bot()
    bot.add_html_source(request.html)
    bot.run()
    return {
        "leads_found": len(bot.get_leads()),
        "emails_sent": len(bot.get_outreach_emails()),
        "revenue": bot.revenue_engine.total(),
    }


@app.get("/leads/export-csv")
def export_leads_csv(html: Optional[str] = None) -> dict:
    """Export scraped leads as a CSV string."""
    bot = _make_lead_gen_bot()
    if html:
        bot.add_html_source(html)
        bot.start()
        leads = bot.scrape_html(html)
        for lead in leads:
            bot.add_lead(lead)
        bot.stop()
    csv_data = bot.export_csv()
    return {"csv": csv_data}


# ---------------------------------------------------------------------------
# Revenue endpoint
# ---------------------------------------------------------------------------

@app.get("/revenue", response_model=RevenueResponse)
def get_revenue() -> RevenueResponse:
    """Return aggregated revenue data."""
    return RevenueResponse(
        total_usd=_revenue_engine.total(),
        entries=_revenue_engine.report(),
    )


@app.get("/swarm/stigmergy/metrics")
def stigmergy_metrics() -> dict:
    """Return real-time stigmergy metrics and trace snapshots."""
    metrics = _stigmergy_environment.metrics()
    return {
        "active_trace_count": metrics["active_trace_count"],
        "total_strength": metrics["total_strength"],
        "heatmap": metrics["heatmap"],
        "prometheus": metrics["prometheus"],
        "traces": metrics["traces"],
    }
