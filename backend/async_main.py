"""Async FastAPI backend mirroring the synchronous DreamCo API."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import List, Optional

try:
    import asyncpg
except ImportError:  # pragma: no cover - optional dependency at runtime
    asyncpg = None

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from core.dream_core import DreamCore
from core.monetization_hooks import MonetizationHooks
from core.revenue_engine import RevenueEngine
from Fiverr_bots.fiverr_bot import FiverrBot
from bots.lead_gen_bot.lead_gen_bot import LeadGenBot
from dreamco_platform.swarm.stigmergy import PersistentStigmergyEnvironment


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


_revenue_engine = RevenueEngine()
_monetization_hooks = MonetizationHooks()
_dream_core = DreamCore()
_stigmergy_environment = PersistentStigmergyEnvironment()


def _make_fiverr_bot() -> FiverrBot:
    return FiverrBot(revenue_engine=_revenue_engine, monetization_hooks=_monetization_hooks)


def _make_lead_gen_bot() -> LeadGenBot:
    return LeadGenBot(
        db_dsn=os.getenv("DATABASE_URL"),
        revenue_engine=_revenue_engine,
        monetization_hooks=_monetization_hooks,
        dream_core=_dream_core,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = None
    if asyncpg is not None and os.getenv("DATABASE_URL"):
        pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], min_size=1, max_size=5)
    app.state.db_pool = pool
    try:
        yield
    finally:
        if pool is not None:
            await pool.close()


app = FastAPI(title="DreamCo Bot API (Async)", version="1.0.0", lifespan=lifespan)


async def _record_request(pool, path: str) -> None:
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute("CREATE TABLE IF NOT EXISTS api_request_log(path TEXT, created_at TIMESTAMPTZ DEFAULT NOW())")
        await conn.execute("INSERT INTO api_request_log(path) VALUES($1)", path)


@app.get("/health")
async def health(request: Request) -> dict:
    await _record_request(request.app.state.db_pool, "/health")
    return {"status": "ok", "db_pool": request.app.state.db_pool is not None}


@app.post("/fiverr/generate-gig", response_model=GigResponse)
async def generate_gig(request: GigRequest, raw_request: Request) -> GigResponse:
    await _record_request(raw_request.app.state.db_pool, "/fiverr/generate-gig")
    bot = _make_fiverr_bot()

    def _run() -> dict:
        bot.add_gig(request.title, request.keywords, request.word_count)
        bot.run()
        completed = bot.get_completed_gigs()
        if not completed:
            raise RuntimeError("Gig generation failed.")
        return completed[0]

    gig = await asyncio.to_thread(_run)
    return GigResponse(**gig)


@app.post("/fiverr/run-batch")
async def run_fiverr_batch(gigs: List[GigRequest], raw_request: Request) -> dict:
    await _record_request(raw_request.app.state.db_pool, "/fiverr/run-batch")
    bot = _make_fiverr_bot()

    def _run() -> dict:
        for gig_req in gigs:
            bot.add_gig(gig_req.title, gig_req.keywords, gig_req.word_count)
        bot.run()
        return {"completed": len(bot.get_completed_gigs()), "revenue": bot.revenue_engine.total()}

    return await asyncio.to_thread(_run)


@app.post("/leads/scrape", response_model=List[LeadResponse])
async def scrape_leads(request: LeadScrapeRequest, raw_request: Request) -> List[LeadResponse]:
    await _record_request(raw_request.app.state.db_pool, "/leads/scrape")
    bot = _make_lead_gen_bot()
    leads = await asyncio.to_thread(bot.scrape_html, request.html)
    return [LeadResponse(**lead) for lead in leads]


@app.post("/leads/run-outreach")
async def run_lead_outreach(request: LeadScrapeRequest, raw_request: Request) -> dict:
    await _record_request(raw_request.app.state.db_pool, "/leads/run-outreach")
    bot = _make_lead_gen_bot()

    def _run() -> dict:
        bot.add_html_source(request.html)
        bot.run()
        return {
            "leads_found": len(bot.get_leads()),
            "emails_sent": len(bot.get_outreach_emails()),
            "revenue": bot.revenue_engine.total(),
        }

    return await asyncio.to_thread(_run)


@app.get("/leads/export-csv")
async def export_leads_csv(raw_request: Request, html: Optional[str] = None) -> dict:
    await _record_request(raw_request.app.state.db_pool, "/leads/export-csv")
    bot = _make_lead_gen_bot()

    def _run() -> str:
        if html:
            bot.add_html_source(html)
            bot.start()
            leads = bot.scrape_html(html)
            for lead in leads:
                bot.add_lead(lead)
            bot.stop()
        return bot.export_csv()

    csv_data = await asyncio.to_thread(_run)
    return {"csv": csv_data}


@app.get("/revenue", response_model=RevenueResponse)
async def get_revenue(raw_request: Request) -> RevenueResponse:
    await _record_request(raw_request.app.state.db_pool, "/revenue")
    return RevenueResponse(total_usd=_revenue_engine.total(), entries=_revenue_engine.report())


@app.get("/swarm/stigmergy/metrics")
async def stigmergy_metrics(raw_request: Request) -> dict:
    await _record_request(raw_request.app.state.db_pool, "/swarm/stigmergy/metrics")
    metrics = await asyncio.to_thread(_stigmergy_environment.metrics)
    if not metrics:
        raise HTTPException(status_code=500, detail="Unable to load stigmergy metrics")
    return {
        "active_trace_count": metrics["active_trace_count"],
        "total_strength": metrics["total_strength"],
        "heatmap": metrics["heatmap"],
        "prometheus": metrics["prometheus"],
        "traces": metrics["traces"],
    }
