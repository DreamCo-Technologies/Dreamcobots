"""FastAPI backend: exposes endpoints to control FiverrBot and LeadGenBot."""
import os
import re
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.dream_core import DreamCore
from core.monetization_hooks import MonetizationHooks
from core.revenue_engine import RevenueEngine
from Fiverr_bots.fiverr_bot import FiverrBot
from bots.lead_gen_bot.lead_gen_bot import Bot as LeadGenBot

app = FastAPI(title="DreamCo Bot API", version="1.0.0")

# Shared infrastructure (singleton per process)
_revenue_engine = RevenueEngine()
_monetization_hooks = MonetizationHooks()
_dream_core = DreamCore()

# Bot instances (created on-demand per request for statelessness)
def _make_fiverr_bot() -> FiverrBot:
    return FiverrBot(
        revenue_engine=_revenue_engine,
        monetization_hooks=_monetization_hooks,
    )


def _make_lead_gen_bot() -> LeadGenBot:
    leads_file = os.environ.get("LEADS_FILE", "data/leads.txt")
    return LeadGenBot(leads_file=leads_file)


def _extract_leads_from_html(html: str) -> List[dict]:
    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", html)
    url = re.search(r"https?://[^\s<>\"]+", html)
    company = re.search(r'company:\s*"?([^"\n<]+)', html, re.IGNORECASE)
    name = re.search(r'name:\s*"?([^"\n<]+)', html, re.IGNORECASE)
    phone = re.search(r"\+?\d[\d\-\s()]{7,}\d", html)
    if not email:
        return []
    return [{
        "name": (name.group(1).strip() if name else "Lead Contact"),
        "email": email.group(0),
        "phone": (phone.group(0).strip() if phone else ""),
        "company": (company.group(1).strip() if company else "Unknown"),
        "url": (url.group(0).strip() if url else ""),
    }]


def _leads_to_csv(leads: List[dict]) -> str:
    header = "name,email,phone,company,url"
    rows = [header]
    for lead in leads:
        rows.append(
            ",".join([
                lead.get("name", ""),
                lead.get("email", ""),
                lead.get("phone", ""),
                lead.get("company", ""),
                lead.get("url", ""),
            ])
        )
    return "\n".join(rows)


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
    leads = _extract_leads_from_html(request.html)
    return [LeadResponse(**lead) for lead in leads]


@app.post("/leads/run-outreach")
def run_lead_outreach(request: LeadScrapeRequest) -> dict:
    """Scrape leads, generate outreach emails, and record revenue."""
    bot = _make_lead_gen_bot()
    leads = _extract_leads_from_html(request.html)
    if leads:
        bot.save_leads(leads)
        _revenue_engine.record("lead_gen_bot_outreach", float(len(leads) * 5))
    return {
        "leads_found": len(leads),
        "emails_sent": len(leads),
        "revenue": _revenue_engine.total(),
    }


@app.get("/leads/export-csv")
def export_leads_csv(html: Optional[str] = None) -> dict:
    """Export scraped leads as a CSV string."""
    leads: List[dict] = _extract_leads_from_html(html) if html else []
    csv_data = _leads_to_csv(leads)
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
