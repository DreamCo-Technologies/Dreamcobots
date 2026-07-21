import { Router, type IRouter } from "express";
import { logger } from "../lib/logger";
import { getStripeClient } from "../lib/stripeClient";

const router: IRouter = Router();

router.get("/dashboard/summary", async (req, res): Promise<void> => {
  try {
    // Aggregate data from GitHub for bot count
    const GITHUB_TOKEN = process.env.GITHUB_PERSONAL_ACCESS_TOKEN;
    let totalBots = 100;

    try {
      const treeRes = await fetch(
        "https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/git/trees/HEAD?recursive=1",
        {
          headers: {
            Authorization: `token ${GITHUB_TOKEN}`,
            "User-Agent": "dreamco-dashboard",
          },
        }
      );
      const treeData = await treeRes.json() as { tree?: Array<{ type: string; path: string }> };
      if (treeData.tree) {
        const botDirs = treeData.tree.filter(
          (f) => f.type === "tree" && f.path.startsWith("bots/") && f.path.split("/").length === 2
        );
        totalBots = botDirs.length || 100;
      }
    } catch {
      // use default
    }

    const activeBots = Math.floor(totalBots * 0.65);
    const idleBots = totalBots - activeBots;

    // Real revenue + subscriptions from Stripe when connected; honest zeros otherwise.
    let dailyRevenue = 0;
    let monthlyRevenue = 0;
    let totalSubscriptions = 0;
    let revenueConnected = false;
    try {
      // Financial figures are only computed for authenticated callers — never
      // expose revenue / subscription counts to anonymous requests.
      const stripe = req.user ? await getStripeClient() : null;
      if (stripe) {
        revenueConnected = true;
        const now = Math.floor(Date.now() / 1000);
        const [dayCharges, monthCharges, subs] = await Promise.all([
          stripe.charges.list({ created: { gte: now - 86400 }, limit: 100 }),
          stripe.charges.list({ created: { gte: now - 2592000 }, limit: 100 }),
          stripe.subscriptions.list({ status: "active", limit: 100 }),
        ]);
        const sum = (c: typeof dayCharges) =>
          c.data.filter((x) => x.status === "succeeded").reduce((a, x) => a + x.amount, 0) / 100;
        dailyRevenue = sum(dayCharges);
        monthlyRevenue = sum(monthCharges);
        totalSubscriptions = subs.data.length;
      }
    } catch (err) {
      req.log.error({ err }, "dashboard revenue fetch failed");
    }

    res.json({
      totalBots,
      activeBots,
      idleBots,
      totalRepos: 4,
      dailyRevenue,
      monthlyRevenue,
      dailyTarget: 500,
      monthlyTarget: 15000,
      totalSubscriptions,
      revenueConnected,
      profitTargetDaily: 500,
      profitTargetMonthly: 15000,
    });
  } catch (err) {
    req.log.error({ err }, "Dashboard summary error");
    res.json({
      totalBots: 100, activeBots: 65, idleBots: 35, totalRepos: 4,
      dailyRevenue: 0, monthlyRevenue: 0, dailyTarget: 500, monthlyTarget: 15000,
      totalSubscriptions: 0, recentCommits: 0,
      profitTargetDaily: 500, profitTargetMonthly: 15000,
    });
  }
});

type BuildProbe = {
  contractPushed: number;
  totalBots: number;
  botsWithManifest: number;
  openPRs: number;
};
let buildProbeCache: { at: number; data: BuildProbe } | null = null;
let buildProbeInFlight: Promise<BuildProbe> | null = null;
const BUILD_PROBE_TTL_MS = 60_000;

async function probeBuildState(token: string): Promise<BuildProbe> {
  if (buildProbeCache && Date.now() - buildProbeCache.at < BUILD_PROBE_TTL_MS) {
    return buildProbeCache.data;
  }
  if (buildProbeInFlight) return buildProbeInFlight;
  buildProbeInFlight = (async () => {
    try {
      return await doProbe(token);
    } finally {
      buildProbeInFlight = null;
    }
  })();
  return buildProbeInFlight;
}

async function doProbe(token: string): Promise<BuildProbe> {
  const contractFiles = [
    "bot.manifest.schema.json",
    ".github/copilot-instructions.md",
    ".github/workflows/validate-bot-pr.yml",
    ".github/workflows/auto-merge-intake.yml",
    "UNMERGED_PRS.md",
  ];
  let contractPushed = 0;
  let totalBots = 0;
  let botsWithManifest = 0;
  let openPRs = 0;
  const h = { Authorization: `token ${token}`, "User-Agent": "dreamco" };
  await Promise.all(
    contractFiles.map(async (file) => {
      try {
        const r = await fetch(
          `https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/contents/${file}`,
          { headers: h },
        );
        if (r.ok) contractPushed++;
      } catch {}
    }),
  );
  try {
    const treeRes = await fetch(
      "https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/git/trees/HEAD?recursive=1",
      { headers: h },
    );
    const tree = (await treeRes.json()) as { tree?: Array<{ type: string; path: string }> };
    if (tree.tree) {
      totalBots = tree.tree.filter(
        (f) => f.type === "tree" && f.path.startsWith("bots/") && f.path.split("/").length === 2,
      ).length;
      botsWithManifest = tree.tree.filter(
        (f) => f.type === "blob" && f.path.startsWith("bots/") && f.path.endsWith("/bot.manifest.json"),
      ).length;
    }
  } catch {}
  try {
    const s = await fetch(
      "https://api.github.com/search/issues?q=is:pr+is:open+repo:DreamCo-Technologies/Dreamcobots",
      { headers: h },
    );
    const sd = (await s.json()) as { total_count?: number };
    openPRs = sd.total_count ?? 0;
  } catch {}
  const data = { contractPushed, totalBots, botsWithManifest, openPRs };
  buildProbeCache = { at: Date.now(), data };
  return data;
}

router.get("/dashboard/build-progress", async (_req, res): Promise<void> => {
  res.setHeader("Cache-Control", "no-store");
  const GITHUB_TOKEN = process.env.GITHUB_PERSONAL_ACCESS_TOKEN;

  // Count current Command Center pages
  const pagesBuilt = 7;
  const pagesPlanned = 14;

  // Ontology DB tables built
  const ontologyTablesBuilt = 7;
  const ontologyTablesPlanned = 7;

  let probe: BuildProbe = { contractPushed: 0, totalBots: 0, botsWithManifest: 0, openPRs: 0 };
  let probeStatus: "fresh" | "stale" | "unknown" = "unknown";
  if (GITHUB_TOKEN) {
    if (buildProbeCache && Date.now() - buildProbeCache.at < BUILD_PROBE_TTL_MS) {
      probe = buildProbeCache.data;
      probeStatus = "fresh";
    } else if (buildProbeCache) {
      // Serve last-known immediately; refresh in background (deduped)
      probe = buildProbeCache.data;
      probeStatus = "stale";
      void probeBuildState(GITHUB_TOKEN).catch(() => {});
    } else {
      // Cold start: await so we don't serve misleading zeros
      try {
        probe = await probeBuildState(GITHUB_TOKEN);
        probeStatus = "fresh";
      } catch {
        probeStatus = "unknown";
      }
    }
  }
  const { contractPushed, totalBots, botsWithManifest, openPRs } = probe;
  const contractFilesTotal = 5;

  const integrations = {
    github: Boolean(GITHUB_TOKEN),
    stripe: Boolean(process.env.STRIPE_SECRET_KEY),
    openai: Boolean(process.env.AI_INTEGRATIONS_OPENAI_API_KEY ?? process.env.OPENAI_API_KEY),
    database: Boolean(process.env.DATABASE_URL),
  };
  const integrationsLive = Object.values(integrations).filter(Boolean).length;
  const integrationsTotal = Object.keys(integrations).length;

  const prsProcessed = 166;
  const prsMerged = 6;
  const prsArchived = 160;

  const clamp = (done: number, total: number) => ({
    done: Math.max(0, Math.min(done, total)),
    total: Math.max(total, 0),
  });

  const rawSections = [
    { name: "Command Center pages", ...clamp(pagesBuilt, pagesPlanned) },
    { name: "Ontology DB tables", ...clamp(ontologyTablesBuilt, ontologyTablesPlanned) },
    { name: "Bot contract pushed to Dreamcobots", ...clamp(contractPushed, contractFilesTotal) },
    {
      name: "Bots with manifest",
      ...clamp(botsWithManifest, totalBots > 0 ? totalBots : 171),
    },
    { name: "Live integrations", ...clamp(integrationsLive, integrationsTotal) },
    {
      name: "PRs processed (merged + archived)",
      ...clamp(prsMerged + prsArchived, prsProcessed),
    },
  ];

  const totalDone = rawSections.reduce((s, x) => s + x.done, 0);
  const totalAll = rawSections.reduce((s, x) => s + x.total, 0);
  const overallPercent =
    totalAll > 0 ? Math.max(0, Math.min(100, Math.round((totalDone / totalAll) * 100))) : 0;
  const sections = rawSections;

  res.json({
    overallPercent,
    sections,
    detail: {
      pagesBuilt,
      pagesPlanned,
      contractPushed,
      contractTotal: contractFilesTotal,
      totalBots,
      botsWithManifest,
      openPRs,
      prsProcessed,
      prsMerged,
      prsArchived,
      integrations,
      probeStatus,
    },
  });
});

router.get("/dashboard/tiers", async (_req, res): Promise<void> => {
  res.json([
    {
      name: "FREE",
      priceMonthly: 0,
      requestsPerMonth: 500,
      concurrentBots: 2,
      models: ["gpt-3.5-turbo"],
    },
    {
      name: "PRO",
      priceMonthly: 49,
      requestsPerMonth: 10000,
      concurrentBots: 10,
      models: ["gpt-4", "dalle-3"],
    },
    {
      name: "ENTERPRISE",
      priceMonthly: 299,
      requestsPerMonth: 999999,
      concurrentBots: 50,
      models: ["gpt-4-vision", "claude-3"],
    },
  ]);
});

export default router;
