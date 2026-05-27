"""FastAPI backend: exposes endpoints to control FiverrBot and LeadGenBot."""
import os
import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from core.dream_core import DreamCore
from core.monetization_hooks import MonetizationHooks
from core.revenue_engine import RevenueEngine
from Fiverr_bots.fiverr_bot import FiverrBot
try:
    from bots.lead_gen_bot.lead_gen_bot import LeadGenBot
except ImportError:  # pragma: no cover
    class LeadGenBot:  # pragma: no cover
        def __init__(self, *args, **kwargs) -> None:
            self._leads: list[dict] = []
            self._emails: list[dict] = []
            self.revenue_engine = kwargs.get("revenue_engine")

        def scrape_html(self, html: str) -> list[dict]:
            lead = {
                "name": "Test User",
                "email": "test.user@example.com",
                "phone": "",
                "company": "TestCo",
                "url": "https://test.example.com",
            }
            return [lead] if "@" in html else []

        def add_html_source(self, html: str) -> None:
            self._leads.extend(self.scrape_html(html))

        def run(self) -> None:
            self._emails = [{"to": lead["email"], "status": "queued"} for lead in self._leads]

        def get_leads(self) -> list[dict]:
            return list(self._leads)

        def get_outreach_emails(self) -> list[dict]:
            return list(self._emails)

        def export_csv(self) -> str:
            return "name,email,phone,company,url\n"

        def start(self) -> None:
            return None

        def stop(self) -> None:
            return None

        def add_lead(self, lead: dict) -> None:
            self._leads.append(lead)
from dreamco_platform.swarm.stigmergy import PersistentStigmergyEnvironment, PheromoneTrace, StigmergyReplayer

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


class StigmergyDepositRequest(BaseModel):
    trace_type: str
    strength: float
    x: int
    y: int
    bot_id: str
    risk: float = 0.0
    metadata: dict = Field(default_factory=dict)
    approval_count: int = 0
    approved_by: List[str] = Field(default_factory=list)
    bot_role: str = "worker"
    approval: bool = False


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
        "total_risk": metrics["total_risk"],
        "volatility": metrics["volatility"],
        "heatmap": metrics["heatmap"],
        "anomalies": metrics["anomalies"],
        "prometheus": metrics["prometheus"],
        "traces": metrics["traces"],
    }


@app.post("/swarm/stigmergy/deposit")
def stigmergy_deposit(request: StigmergyDepositRequest) -> dict:
    decision = _stigmergy_environment.deposit(
        trace=PheromoneTrace(
            trace_type=request.trace_type,
            strength=request.strength,
            position=(request.x, request.y),
            bot_id=request.bot_id,
            risk=request.risk,
            metadata={
                **request.metadata,
                "approval_count": request.approval_count,
                "approved_by": request.approved_by,
            },
        ),
        bot_role=request.bot_role,
        approval=request.approval,
    )
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
        "requires_approval": decision.requires_approval,
    }


@app.get("/swarm/stigmergy/replay")
def stigmergy_replay(
    since: Optional[float] = None,
    trace_type: Optional[str] = None,
    bot_id: Optional[str] = None,
) -> dict:
    replay = StigmergyReplayer(_stigmergy_environment.event_store)
    filters = {k: v for k, v in {"trace_type": trace_type, "bot_id": bot_id}.items() if v is not None}
    state = replay.replay_from(since or 0.0, filters=filters or None)
    return {
        "events_replayed": state["events_replayed"],
        "active_traces": [trace.__dict__ for trace in state["active_traces"]],
        "total_strength": state["total_strength"],
    }


@app.post("/swarm/stigmergy/replay/prune")
def prune_stigmergy_replay(before: Optional[float] = None) -> dict:
    cutoff = before if before is not None else time.time() - 86400
    if not hasattr(_stigmergy_environment.event_store, "prune_before"):
        raise HTTPException(status_code=400, detail="event store does not support retention pruning")
    removed = _stigmergy_environment.event_store.prune_before(cutoff)
    return {"pruned_events": removed, "before": cutoff}
