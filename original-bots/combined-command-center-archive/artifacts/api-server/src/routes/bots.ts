import { Router, type IRouter } from "express";
import { validateBotManifest, type BotManifest } from "@workspace/db/schema";
import { db, agentsTable, botRunsTable, botLearningsTable, type Agent } from "@workspace/db";
import { eq, sql } from "drizzle-orm";
import { logger } from "../lib/logger";
import {
  DREAMCOBOTS_REPO,
  GITHUB_ORG,
  ghFetch,
  ghFetchRaw,
} from "../lib/githubClient";
import { getStripeClient } from "../lib/stripeClient";
import { requireAuth } from "../middlewares/authMiddleware";
import { indexBots } from "../lib/botIndexer";

const router: IRouter = Router();

const BOT_CATEGORIES: Record<string, string> = {
  buddy_bot: "AI Companion",
  stripe_integration: "Payments",
  stripe_payment_bot: "Payments",
  stripe_key_rotation_bot: "Payments",
  token_billing: "Billing",
  stock_trading_bot: "Finance",
  real_estate_bot: "Real Estate",
  lead_gen_bot: "Lead Generation",
  social_media_bot: "Marketing",
  social_media_manager_bot: "Marketing",
  email_campaign_manager_bot: "Marketing",
  influencer_bot: "Marketing",
  shopify_automation_bot: "E-Commerce",
  saas_bot: "SaaS",
  software_bot: "Software",
  god_bot: "Core",
  god_mode_bot: "Core",
  space_ai_bot: "AI Research",
  quantum_ai_bot: "AI Research",
  quantum_decision_bot: "AI Research",
  smart_city_bot: "Infrastructure",
  legal_money_bot: "Legal",
  government_contract_grant_bot: "Government",
  wealth_system_bot: "Finance",
  stack_and_profit_bot: "Finance",
  voice_replicator_bot: "Media",
  sql_bot: "Data",
  selenium_job_application_bot: "Automation",
  health_wellness_bot: "Health",
  education_bot: "Education",
  dream_finance: "Finance",
};

const CATEGORY_CAPABILITIES: Record<string, string[]> = {
  "AI Companion": ["chat", "memory_recall", "emotion_detection", "intent_routing", "knowledge_lookup", "task_planning"],
  "AI Research": ["model_evaluation", "research_synthesis", "experiment_tracking", "data_ingestion", "reasoning"],
  "Automation": ["task_scheduling", "workflow_execution", "retries", "logging", "webhook_triggers"],
  "Billing": ["invoice_generation", "usage_metering", "subscription_lifecycle", "dunning", "stripe_sync"],
  "Core": ["bot_orchestration", "permission_management", "audit_logging", "event_bus", "system_health"],
  "Data": ["sql_query", "schema_introspection", "data_export", "etl_pipeline", "anomaly_detection"],
  "E-Commerce": ["product_sync", "order_fulfillment", "inventory_management", "shopify_api", "checkout_automation"],
  "Education": ["lesson_generation", "quiz_creation", "grading", "progress_tracking", "curriculum_sync"],
  "Finance": ["market_data_fetch", "portfolio_analysis", "risk_scoring", "trade_execution", "reporting"],
  "Government": ["grant_discovery", "contract_search", "compliance_check", "filing_automation", "deadline_alerts"],
  "Health": ["symptom_lookup", "appointment_scheduling", "telemetry_sync", "regimen_tracking", "alerts"],
  "Infrastructure": ["service_discovery", "load_balancing", "deployment_orchestration", "monitoring", "scaling"],
  "Lead Generation": ["lead_scraping", "enrichment", "lead_scoring", "outreach_sequencing", "crm_sync"],
  "Legal": ["contract_review", "clause_extraction", "compliance_search", "filing_automation", "citation_lookup"],
  "Marketing": ["content_generation", "campaign_scheduling", "audience_segmentation", "analytics", "social_publishing"],
  "Media": ["voice_synthesis", "transcription", "video_editing", "image_generation", "asset_management"],
  "Payments": ["charge_processing", "refunds", "webhook_handling", "key_rotation", "fraud_signals"],
  "Real Estate": ["mls_search", "valuation", "foreclosure_detection", "rental_cashflow", "lead_capture"],
  "SaaS": ["tenant_provisioning", "feature_flagging", "billing_sync", "usage_tracking", "support_routing"],
  "Sales": ["pipeline_management", "proposal_generation", "follow_up_sequencing", "deal_scoring", "crm_sync"],
  "Software": ["code_generation", "repo_scanning", "ci_orchestration", "dependency_audit", "release_automation"],
};

const CATEGORY_TO_DIVISION: Record<string, string> = {
  "Real Estate": "DreamRealEstate",
  "Lead Generation": "DreamSalesPro",
  Marketing: "DreamSalesPro",
  Sales: "DreamSalesPro",
  Finance: "DreamFinance",
  Payments: "DreamFinance",
  Billing: "DreamFinance",
  "AI Research": "DreamAI",
  "AI Companion": "DreamAI",
  Core: "DreamAI",
  Media: "DreamMedia",
  SaaS: "DreamSoft",
  Software: "DreamSoft",
  Infrastructure: "DreamSoft",
  Data: "DreamSoft",
  Automation: "DreamOps",
  Government: "DreamGov",
  Legal: "DreamGov",
  Health: "DreamGov",
  Education: "DreamGov",
  "E-Commerce": "DreamSalesPro",
};

type BotRow = {
  name: string;
  displayName: string | null;
  repoPath: string;
  status: "active" | "idle" | "error" | "unknown";
  tier: "FREE" | "PRO" | "ENTERPRISE";
  category: string;
  division: string | null;
  capabilities: string[];
  entrypoint: string | null;
  revenueModel: string | null;
  owner: string | null;
  description: string;
  lastHeartbeat: string | null;
  pendingPRs: number;
  revenue: number;
  lastUpdate: string | null;
  source: "manifest" | "heuristic" | "fallback";
};

type Telemetry = {
  agents: Map<string, Agent>;
  revenue: Map<string, number>;
  pendingPRs: Map<string, number>;
};

async function fetchBotFolderNames(): Promise<string[]> {
  try {
    const data = await ghFetch<{ tree?: Array<{ type: string; path: string }> }>(
      `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/git/trees/HEAD?recursive=1`,
    );
    if (!data.tree) return [];
    return data.tree
      .filter(
        (f) =>
          f.type === "tree" &&
          f.path.startsWith("bots/") &&
          f.path.split("/").length === 2,
      )
      .map((f) => f.path.replace("bots/", ""));
  } catch (err) {
    logger.warn({ err }, "fetchBotFolderNames failed");
    return [];
  }
}

async function fetchManifest(folder: string): Promise<BotManifest | null> {
  const raw = await ghFetchRaw(
    `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/contents/bots/${folder}/bot.manifest.json`,
  );
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    const result = validateBotManifest(parsed);
    if (!result.ok) {
      logger.info({ folder, errors: result.errors }, "manifest invalid");
      return null;
    }
    return result.manifest;
  } catch (err) {
    logger.info({ folder, err }, "manifest unparseable");
    return null;
  }
}

function heuristicCategory(name: string): string {
  const key = name.toLowerCase();
  return BOT_CATEGORIES[key] ?? "Automation";
}

async function fetchAgentsMap(): Promise<Map<string, Agent>> {
  try {
    const rows = await db.select().from(agentsTable);
    return new Map(rows.map((r) => [r.slug.toLowerCase(), r]));
  } catch (err) {
    logger.warn({ err }, "fetchAgentsMap failed");
    return new Map();
  }
}

async function fetchStripeRevenueByBot(): Promise<Map<string, number>> {
  const revenue = new Map<string, number>();
  const stripe = await getStripeClient();
  if (!stripe) return revenue;
  try {
    const productToBot = new Map<string, string>();
    let startingAfter: string | undefined;
    for (let page = 0; page < 5; page++) {
      const products = await stripe.products.list({
        limit: 100,
        ...(startingAfter ? { starting_after: startingAfter } : {}),
      });
      for (const p of products.data) {
        const slug = p.metadata?.bot;
        if (slug) productToBot.set(p.id, slug.toLowerCase());
      }
      if (!products.has_more || products.data.length === 0) break;
      startingAfter = products.data[products.data.length - 1]!.id;
    }

    const charges = await stripe.charges.list({
      limit: 100,
      expand: ["data.invoice"],
    });
    for (const c of charges.data) {
      if (c.status !== "succeeded") continue;
      const amount = c.amount / 100;
      const directSlug = c.metadata?.bot?.toLowerCase();
      if (directSlug) {
        revenue.set(directSlug, (revenue.get(directSlug) ?? 0) + amount);
        continue;
      }
      const invoice = (c as unknown as { invoice?: unknown }).invoice as
        | { lines?: { data: Array<{ amount: number; price?: { product?: string } | null }> } }
        | string
        | null
        | undefined;
      if (invoice && typeof invoice === "object" && invoice.lines?.data) {
        for (const line of invoice.lines.data) {
          const productId = line.price?.product;
          if (!productId) continue;
          const slug = productToBot.get(productId);
          if (slug) {
            revenue.set(slug, (revenue.get(slug) ?? 0) + line.amount / 100);
          }
        }
      }
    }
  } catch (err) {
    logger.warn({ err }, "fetchStripeRevenueByBot failed");
  }
  return revenue;
}

async function fetchPendingPRsByFolder(): Promise<Map<string, number>> {
  const counts = new Map<string, number>();
  try {
    const prs = await ghFetch<Array<{ number: number }>>(
      `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/pulls?state=open&per_page=100`,
    );
    const CONCURRENCY = 5;
    for (let i = 0; i < prs.length; i += CONCURRENCY) {
      const batch = prs.slice(i, i + CONCURRENCY);
      await Promise.all(
        batch.map(async (pr) => {
          try {
            const files = await ghFetch<Array<{ filename: string }>>(
              `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/pulls/${pr.number}/files?per_page=100`,
            );
            const folders = new Set<string>();
            for (const f of files) {
              const m = f.filename.match(/^bots\/([^/]+)\//);
              if (m && m[1]) folders.add(m[1].toLowerCase());
            }
            for (const folder of folders) {
              counts.set(folder, (counts.get(folder) ?? 0) + 1);
            }
          } catch (err) {
            logger.warn({ err, pr: pr.number }, "pr files fetch failed");
          }
        }),
      );
    }
  } catch (err) {
    logger.warn({ err }, "fetchPendingPRsByFolder failed");
  }
  return counts;
}

function applyTelemetry(
  row: BotRow,
  folder: string,
  manifestStatus: BotManifest["status"] | null,
  telemetry: Telemetry,
): BotRow {
  const key = folder.toLowerCase();
  const agent = telemetry.agents.get(key);

  let status: BotRow["status"];
  if (agent) {
    const s = agent.status;
    status =
      s === "active" || s === "idle" || s === "error" ? s : "unknown";
  } else if (manifestStatus === "active") {
    status = "active";
  } else if (manifestStatus === "paused") {
    status = "idle";
  } else {
    status = "unknown";
  }

  return {
    ...row,
    status,
    lastHeartbeat: agent?.lastHeartbeat ? agent.lastHeartbeat.toISOString() : null,
    revenue: telemetry.revenue.get(key) ?? 0,
    pendingPRs: telemetry.pendingPRs.get(key) ?? 0,
    lastUpdate: agent?.updatedAt ? agent.updatedAt.toISOString() : null,
  };
}

function buildFromManifest(folder: string, m: BotManifest): BotRow {
  return {
    name: m.name,
    displayName: m.displayName ?? null,
    repoPath: `bots/${folder}`,
    status: "unknown",
    tier: m.tier,
    category: m.category,
    division: m.division,
    capabilities: m.capabilities,
    entrypoint: `${m.entrypoint.runtime}: ${m.entrypoint.command}`,
    revenueModel: m.revenueModel?.type ?? null,
    owner: m.owner.team,
    description: m.description,
    lastHeartbeat: null,
    pendingPRs: 0,
    revenue: 0,
    lastUpdate: null,
    source: "manifest",
  };
}

function buildHeuristic(folder: string): BotRow {
  const category = heuristicCategory(folder);
  return {
    name: folder,
    displayName: null,
    repoPath: `bots/${folder}`,
    status: "unknown",
    tier: "FREE",
    category,
    division: CATEGORY_TO_DIVISION[category] ?? null,
    capabilities: CATEGORY_CAPABILITIES[category] ?? ["task_execution"],
    entrypoint: null,
    revenueModel: null,
    owner: null,
    description: `DreamCo ${category} bot — ${folder.replace(/_/g, " ")}`,
    lastHeartbeat: null,
    pendingPRs: 0,
    revenue: 0,
    lastUpdate: null,
    source: "heuristic",
  };
}

const FALLBACK_FOLDERS = [
  "buddy_bot",
  "stripe_integration",
  "stock_trading_bot",
  "lead_gen_bot",
  "social_media_bot",
  "shopify_automation_bot",
  "real_estate_bot",
  "wealth_system_bot",
  "sql_bot",
  "voice_replicator_bot",
  "space_ai_bot",
  "government_contract_grant_bot",
  "legal_money_bot",
  "saas_bot",
  "software_bot",
  "email_campaign_manager_bot",
  "token_billing",
  "stripe_payment_bot",
];

let botCache: BotRow[] | null = null;
let botCacheTime = 0;
const CACHE_TTL = 60_000;

async function buildAllBots(): Promise<BotRow[]> {
  const [folders, telemetry] = await Promise.all([
    fetchBotFolderNames(),
    (async (): Promise<Telemetry> => {
      const [agents, revenue, pendingPRs] = await Promise.all([
        fetchAgentsMap(),
        fetchStripeRevenueByBot(),
        fetchPendingPRsByFolder(),
      ]);
      return { agents, revenue, pendingPRs };
    })(),
  ]);

  if (folders.length === 0) {
    return FALLBACK_FOLDERS.map((f) => {
      const row = { ...buildHeuristic(f), source: "fallback" as const };
      return applyTelemetry(row, f, null, telemetry);
    });
  }

  // Normalized identity key so `foo` (folder) and `foo_bot` (indexed *_bot.py)
  // collapse to the same logical bot and are never double-counted.
  const normKey = (s: string): string => s.toLowerCase().replace(/_bot$/, "").replace(/[^a-z0-9]/g, "");

  const CONCURRENCY = 8;
  const results: BotRow[] = [];
  const seen = new Set<string>();
  for (let i = 0; i < folders.length; i += CONCURRENCY) {
    const batch = folders.slice(i, i + CONCURRENCY);
    const rows = await Promise.all(
      batch.map(async (folder) => {
        const manifest = await fetchManifest(folder);
        const base = manifest
          ? buildFromManifest(folder, manifest)
          : buildHeuristic(folder);
        return applyTelemetry(base, folder, manifest?.status ?? null, telemetry);
      }),
    );
    for (const r of rows) {
      results.push(r);
      seen.add(normKey(r.name));
    }
  }

  // Merge in the indexed fleet (agents seeded from the Dreamcobots repo scan)
  // that aren't already represented by a manifest/heuristic folder row.
  for (const agent of telemetry.agents.values()) {
    const key = agent.slug.toLowerCase();
    if (seen.has(normKey(agent.slug))) continue;
    const cfg = (agent.runtimeConfig ?? {}) as Record<string, unknown>;
    const category = typeof cfg.category === "string" ? cfg.category : heuristicCategory(agent.slug);
    const division =
      typeof cfg.division === "string"
        ? cfg.division
        : CATEGORY_TO_DIVISION[category] ?? null;
    const s = agent.status;
    const status: BotRow["status"] =
      s === "active" || s === "idle" || s === "error" ? s : "unknown";
    results.push({
      name: agent.slug,
      displayName: agent.name,
      repoPath: agent.repoPath ?? `bots/${agent.slug}`,
      status,
      tier: (agent.tier as BotRow["tier"]) ?? "FREE",
      category,
      division,
      capabilities: CATEGORY_CAPABILITIES[category] ?? ["task_execution"],
      entrypoint: null,
      revenueModel: null,
      owner: null,
      description: agent.description ?? `DreamCo ${category} bot — ${agent.slug.replace(/_/g, " ")}`,
      lastHeartbeat: agent.lastHeartbeat ? agent.lastHeartbeat.toISOString() : null,
      pendingPRs: telemetry.pendingPRs.get(key) ?? 0,
      revenue: telemetry.revenue.get(key) ?? agent.revenueGenerated ?? 0,
      lastUpdate: agent.updatedAt ? agent.updatedAt.toISOString() : null,
      source: "manifest",
    });
    seen.add(normKey(agent.slug));
  }

  return results;
}

router.get("/bots", async (req, res): Promise<void> => {
  const now = Date.now();
  if (botCache && now - botCacheTime < CACHE_TTL) {
    res.json(botCache);
    return;
  }
  const bots = await buildAllBots();
  botCache = bots;
  botCacheTime = now;
  const manifestCount = bots.filter((b) => b.source === "manifest").length;
  req.log.info(
    { count: bots.length, manifestCount },
    "Returning bots (manifest-aware)",
  );
  res.json(bots);
});

router.post("/bots/index", requireAuth, async (req, res): Promise<void> => {
  try {
    const result = await indexBots();
    botCache = null; // force /bots to reflect newly indexed agents
    req.log.info(result, "fleet index complete");
    res.json({ ok: true, ...result });
  } catch (err) {
    req.log.error({ err }, "fleet index failed");
    res.status(500).json({ error: "Indexing failed", detail: String(err) });
  }
});

router.post("/bots/:name/run", async (req, res): Promise<void> => {
  const rawName = Array.isArray(req.params.name) ? req.params.name[0] : req.params.name;
  const name = (rawName ?? "").toLowerCase();
  if (!name) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }
  const bots = botCache ?? (await buildAllBots());
  const bot = bots.find((b) => b.name.toLowerCase() === name);
  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }
  const now = new Date();
  try {
    const existing = await db
      .select()
      .from(agentsTable)
      .where(eq(agentsTable.slug, name))
      .limit(1);
    let row: Agent;
    if (existing.length === 0) {
      const inserted = await db
        .insert(agentsTable)
        .values({
          slug: name,
          name: bot.displayName ?? bot.name,
          description: bot.description,
          tier: bot.tier,
          status: "active",
          repoPath: bot.repoPath,
          lastHeartbeat: now,
          invocations: 1,
        })
        .returning();
      row = inserted[0]!;
    } else {
      const updated = await db
        .update(agentsTable)
        .set({
          status: "active",
          lastHeartbeat: now,
          invocations: sql`${agentsTable.invocations} + 1`,
        })
        .where(eq(agentsTable.slug, name))
        .returning();
      row = updated[0]!;
    }
    // Insert a bot_run row so we can observe activity + later attach earnings
    const runRow = await db
      .insert(botRunsTable)
      .values({
        botSlug: name,
        status: "succeeded",
        triggeredBy: "manual",
        input: (req.body as Record<string, unknown> | undefined) ?? {},
        output: { message: `Manual run for ${name}` },
        durationMs: 0,
        endedAt: now,
      })
      .returning();
    // Seed a learning row so the bot starts a memory trail
    await db.insert(botLearningsTable).values({
      botSlug: name,
      kind: "run_observation",
      prompt: `Manual invocation of ${row.slug}`,
      outcome: "succeeded",
      reward: 0.1,
      metadata: { runId: runRow[0]?.id },
    });
    // Invalidate the bot list cache so the next /bots reflects new status/heartbeat
    botCache = null;
    res.json({
      ok: true,
      name: row.slug,
      status: row.status,
      invocations: row.invocations,
      lastHeartbeat: (row.lastHeartbeat ?? now).toISOString(),
      message: `Run recorded for ${row.slug}`,
    });
  } catch (err) {
    req.log.warn({ err, name }, "run bot failed");
    res.status(500).json({ error: "Failed to record run" });
  }
});

router.get("/bots/:name", async (req, res): Promise<void> => {
  const rawName = Array.isArray(req.params.name) ? req.params.name[0] : req.params.name;
  const name = (rawName ?? "").toLowerCase();
  const bots = botCache ?? (await buildAllBots());
  const bot = bots.find((b) => b.name.toLowerCase() === name);
  if (!bot) {
    res.status(404).json({ error: "Bot not found" });
    return;
  }
  res.json(bot);
});

export default router;
