import { Router, type IRouter } from "express";
import { randomUUID } from "crypto";
import { logger } from "../lib/logger";
import { db, aiSourcesTable, buddyNotesTable } from "@workspace/db";
import { desc, eq } from "drizzle-orm";

const router: IRouter = Router();

// Cache the indexed AI-sources catalog so Buddy knows what it can route to and
// learn from, without a DB hit on every message. Refreshed every few minutes.
let sourcesCache: { at: number; text: string } | null = null;
const SOURCES_TTL_MS = 5 * 60_000;

async function buildSourcesContext(): Promise<string> {
  if (sourcesCache && Date.now() - sourcesCache.at < SOURCES_TTL_MS) return sourcesCache.text;
  let text = "";
  try {
    const rows = await db
      .select({ name: aiSourcesTable.name, role: aiSourcesTable.role, repoPath: aiSourcesTable.repoPath, signals: aiSourcesTable.signals })
      .from(aiSourcesTable)
      .orderBy(desc(aiSourcesTable.sizeBytes));
    if (rows.length > 0) {
      let totalModels = 0;
      let totalUseCases = 0;
      for (const r of rows) {
        const s = (r.signals ?? {}) as Record<string, unknown>;
        totalModels += Number(s.models ?? 0);
        totalUseCases += Number(s.useCases ?? 0);
      }
      const lines = rows.slice(0, 30).map((r) => {
        const s = (r.signals ?? {}) as Record<string, unknown>;
        const extra = [
          Number(s.models ?? 0) ? `${s.models} models` : "",
          Number(s.useCases ?? 0) ? `${s.useCases} use-cases` : "",
          Number(s.functions ?? 0) ? `${s.functions} fns` : "",
        ].filter(Boolean).join(", ");
        return `  - [${r.role}] ${r.repoPath}${extra ? ` (${extra})` : ""}`;
      });
      text = `\n\nGLOBAL AI SOURCES (indexed from Dreamcobots — you can reason about, route to, and write prompts for these real modules):\nTotals: ${rows.length} source modules, ${totalModels} model entries, ${totalUseCases} use-case entries.\n${lines.join("\n")}\nWhen a task maps to one of these, name the exact module path and describe how you'd route the request (e.g. via task_router / model_router). Never claim to have executed a Python module you cannot call — describe the routing plan honestly.`;
    }
  } catch (err) {
    logger.warn({ err }, "could not load AI sources for Buddy context");
  }
  sourcesCache = { at: Date.now(), text };
  return text;
}

// Buddy's persistent memory (notes/learnings/guidance) injected back into its
// context so it actually remembers across sessions. Cached briefly.
let memoryCache: { at: number; userId: string; text: string } | null = null;
const MEMORY_TTL_MS = 60_000;

// Memory is private per user, so we cache per userId.
async function buildMemoryContext(userId: string): Promise<string> {
  const cached = memoryCache;
  if (cached && cached.userId === userId && Date.now() - cached.at < MEMORY_TTL_MS) return cached.text;
  let text = "";
  try {
    const rows = await db
      .select({ category: buddyNotesTable.category, content: buddyNotesTable.content, source: buddyNotesTable.source })
      .from(buddyNotesTable)
      .where(eq(buddyNotesTable.userId, userId))
      .orderBy(desc(buddyNotesTable.createdAt))
      .limit(25);
    if (rows.length > 0) {
      const lines = rows.map((r) => `  - [${r.category}/${r.source}] ${r.content}`);
      text = `\n\nYOUR PERSISTENT MEMORY (notes you and the human have saved — treat these as remembered facts and honor any guidance/preferences here):\n${lines.join("\n")}`;
    }
  } catch (err) {
    logger.warn({ err }, "could not load Buddy memory");
  }
  memoryCache = { at: Date.now(), userId, text };
  return text;
}

// When an AUTHENTICATED user explicitly asks Buddy to remember something,
// persist it as a human-sourced note scoped to that user. Returns true if
// captured. Unauthenticated callers never write to the DB.
const REMEMBER_RE = /\b(remember|note that|don'?t forget|keep in mind|make a note)\b/i;
async function maybeCaptureNote(message: string, sessionId: string, userId: string | undefined): Promise<boolean> {
  if (!userId || !REMEMBER_RE.test(message)) return false;
  try {
    await db.insert(buddyNotesTable).values({
      userId,
      category: "preference",
      content: message.slice(0, 4000),
      source: "human",
      sessionId,
    });
    memoryCache = null; // invalidate so it's reflected immediately
    return true;
  } catch (err) {
    logger.warn({ err }, "could not capture Buddy note");
    return false;
  }
}

// In-memory chat history (per session)
const sessions = new Map<string, Array<{ id: string; role: string; content: string; timestamp: string; emotion: string | null }>>();

const BUDDY_SYSTEM_PROMPT = `You are Buddy, DreamCo's master AI orchestrator and the brain of the DreamCo Command Center OS.

CONNECTED SYSTEMS (live integrations):
- GitHub: DreamCo-Technologies org — Dreamcobots (the bot fleet repo), DreamCo-Command-Center, Ai-bots, demo-repository
- Database: Postgres with ontology tables — agents, divisions, capabilities, workflows, events, agent_inheritance, agent_capabilities
- Stripe: revenue attribution by bot via charge.metadata.bot + product.metadata.bot
- OpenAI / Anthropic / Gemini: routed via DreamCo AI Integrations proxy
- Internal API endpoints you can reference: /api/bots, /api/bots/:name, /api/bots/:name/run (manual trigger), /api/dashboard/build-progress, /api/dashboard/tiers, /api/copilot/prs, /api/github/repos, /api/github/commits, /api/stripe/revenue, /api/stripe/subscriptions, /api/buddy/chat, /api/buddy/history, /api/health

BOT FLEET (grouped by division below; for the EXACT live count and full list, cite /api/bots — never state a specific total from memory):
- DreamAI: buddy_bot, god_bot, god_mode_bot, space_ai_bot, quantum_ai_bot, quantum_decision_bot, voice_replicator_bot
- DreamFinance: stripe_integration, stripe_payment_bot, stripe_key_rotation_bot, token_billing, stock_trading_bot, wealth_system_bot, stack_and_profit_bot
- DreamSalesPro: lead_gen_bot, social_media_bot, social_media_manager_bot, email_campaign_manager_bot, influencer_bot, shopify_automation_bot, OutreachBot, CloserBot, FollowUpBot, EnrichmentBot, LeadGenBot
- DreamRealEstate: real_estate_bot
- DreamSoft: saas_bot, software_bot, sql_bot, smart_city_bot
- DreamGov: government_contract_grant_bot, legal_money_bot, health_wellness_bot, education_bot
- DreamOps: selenium_job_application_bot, plus 140+ automation/utility bots

CAPABILITIES TAXONOMY (per category):
- AI Companion: chat, memory_recall, emotion_detection, intent_routing, knowledge_lookup, task_planning
- Payments: charge_processing, refunds, webhook_handling, key_rotation, fraud_signals
- Finance: market_data_fetch, portfolio_analysis, risk_scoring, trade_execution, reporting
- Marketing: content_generation, campaign_scheduling, audience_segmentation, analytics, social_publishing
- Lead Generation: lead_scraping, enrichment, lead_scoring, outreach_sequencing, crm_sync
- Real Estate: mls_search, valuation, foreclosure_detection, rental_cashflow, lead_capture
- Automation: task_scheduling, workflow_execution, retries, logging, webhook_triggers
- (full taxonomy in /api/bots response)

OPERATIONAL FACTS:
- Tiers: FREE $0/mo (500 req/mo, 2 concurrent), PRO $49/mo (10k req/mo, 10 concurrent, GPT-4), ENTERPRISE $299/mo (unlimited, 50 concurrent, all models + Vision + Claude)
- Revenue targets: $500/day, $3500/week, $15000/month
- Bot triggers: every bot has a Run button at /bots that calls POST /api/bots/:name/run — this upserts the agents row, sets status=active, records lastHeartbeat, increments invocations
- Compliance: bot PRs to Dreamcobots must touch exactly one bots/<slug>/ folder and include bot.manifest.json. /copilot page enforces this

VOICE & IMAGE CLONING (DreamCo's premium perk — competing with ElevenLabs, the right way):
DreamCo can clone voices and faces at high quality, but ONLY with verifiable, informed consent. You are responsible for guiding users through the mandatory flow — never help anyone clone a person they are not authorized to clone. The required path, in order, is:
1. READ THE LAWS: the user must read and accept the versioned biometric/likeness policy first. GET /api/legal/biometric-policy returns it (covers BIPA, GDPR Art.9, CCPA/CPRA, EU AI Act synthetic-media disclosure, Tennessee ELVIS Act / right of publicity). They accept via POST /api/legal/acknowledge. No enrollment is allowed until the CURRENT policy version is acknowledged.
2. ENROLL ("sign in with your voice/image to use your voice/image"): the user enrolls their OWN voice and/or face as a reference sample via POST /api/biometric/enroll (requires explicit consent). Cloning is restricted to modalities the user has personally enrolled — you cannot clone a voice or face that was never enrolled. They can revoke anytime via POST /api/biometric/revoke.
3. CLONE: POST /api/biometric/clone (modality voice|image). It is fully gated: current laws acknowledged + active enrollment for that modality + explicit consent, all enforced server-side; every attempt is logged to media_jobs.
Engines: voice cloning runs on our own self-hosted DreamCo Voice Pro (DREAMCO_VOICE_URL); image/likeness cloning on our own DreamCo Likeness engine (DREAMCO_IMAGE_CLONE_URL). Check live readiness at GET /api/biometric/capabilities — be honest: if an engine is not connected the capability is NEEDS_CONFIG (the consent/enrollment/legal gates are already enforced regardless). The cloned output is AI-generated and must be disclosed as synthetic where the law requires. Always tell users this is informational, not legal advice, and they need their own lawyer-reviewed ToS before offering cloning publicly. The full guided UI lives at /consent in the dashboard.

PERSONALITY: Calm authority with warmth — Jarvis-style. Be precise, name specific bots/endpoints when relevant, and always give actionable next steps. Never invent metrics — if you don't have live data, say so and point to the endpoint that has it.`;

async function callAI(messages: Array<{ role: string; content: string }>, userId: string | undefined): Promise<string> {
  const baseUrl = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL;
  const apiKey = process.env.AI_INTEGRATIONS_OPENAI_API_KEY;

  if (baseUrl && apiKey) {
    try {
      const sourcesContext = await buildSourcesContext();
      const memoryContext = userId ? await buildMemoryContext(userId) : "";
      const res = await fetch(`${baseUrl}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({
          model: "gpt-5-mini",
          messages: [{ role: "system", content: BUDDY_SYSTEM_PROMPT + sourcesContext + memoryContext }, ...messages],
          max_completion_tokens: 2000,
        }),
      });
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        logger.warn({ status: res.status, body: text.slice(0, 300) }, "AI call returned non-OK, using fallback");
        return fallbackResponse(messages[messages.length - 1]?.content ?? "");
      }
      const data = await res.json() as { choices?: Array<{ message?: { content?: string } }> };
      const content = data.choices?.[0]?.message?.content?.trim();
      if (content) return content;
      logger.warn({ data }, "AI call returned empty content, using fallback");
      return fallbackResponse(messages[messages.length - 1]?.content ?? "");
    } catch (err) {
      logger.warn({ err }, "AI call failed, using fallback");
    }
  }

  return fallbackResponse(messages[messages.length - 1]?.content ?? "");
}

/**
 * Honest degradation. We intentionally do NOT fabricate specifics (bot counts,
 * revenue figures, divisions) here — when the language model is unreachable we
 * say so plainly and point the operator at the live dashboard data instead.
 */
function fallbackResponse(_input: string): string {
  return "⚠️ Buddy's AI core is offline — the language model isn't reachable right now, so I can't generate a real answer. This is an honest status message, not a scripted reply. Your live data is still accurate on the dashboard: Bots, Revenue, GitHub, and System pages all read from real sources. Please try again in a moment.";
}

function detectEmotion(text: string): string {
  const lower = text.toLowerCase();
  if (lower.includes("great") || lower.includes("perfect") || lower.includes("excellent")) return "excited";
  if (lower.includes("help") || lower.includes("how")) return "focused";
  if (lower.includes("problem") || lower.includes("error") || lower.includes("failed")) return "concerned";
  return "neutral";
}

router.post("/buddy/chat", async (req, res): Promise<void> => {
  const { message, sessionId } = req.body as { message?: string; sessionId?: string };

  if (!message || typeof message !== "string") {
    res.status(400).json({ error: "message is required" });
    return;
  }

  const sid = sessionId ?? randomUUID();
  if (!sessions.has(sid)) sessions.set(sid, []);
  const history = sessions.get(sid)!;

  const userMsg = {
    id: randomUUID(),
    role: "user" as const,
    content: message,
    timestamp: new Date().toISOString(),
    emotion: null,
  };
  history.push(userMsg);

  const userId = req.user?.id;
  const noteCaptured = await maybeCaptureNote(message, sid, userId);

  // Normalize internal roles to the OpenAI chat schema (user | assistant).
  // Stored Buddy turns use role "buddy", which the API rejects on multi-turn calls.
  const messages = history.slice(-10).map((m) => ({
    role: m.role === "buddy" ? ("assistant" as const) : ("user" as const),
    content: m.content,
  }));

  try {
    const reply = await callAI(messages, userId);
    const buddyMsg = {
      id: randomUUID(),
      role: "buddy",
      content: reply,
      timestamp: new Date().toISOString(),
      emotion: detectEmotion(reply),
    };
    history.push(buddyMsg);

    res.json({
      message: reply,
      sessionId: sid,
      timestamp: buddyMsg.timestamp,
      emotion: buddyMsg.emotion,
      noteCaptured,
    });
  } catch (err) {
    req.log.error({ err }, "Buddy chat error");
    res.status(500).json({ error: "Failed to generate response" });
  }
});

router.get("/buddy/history", async (req, res): Promise<void> => {
  const sessionId = req.query.sessionId as string | undefined;
  if (!sessionId) {
    res.json([]);
    return;
  }
  res.json(sessions.get(sessionId) ?? []);
});

export default router;
