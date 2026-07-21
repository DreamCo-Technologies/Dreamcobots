import { db, agentsTable } from "@workspace/db";
import { sql } from "drizzle-orm";
import { logger } from "./logger";
import { DREAMCOBOTS_REPO, GITHUB_ORG, ghFetch } from "./githubClient";

// Top-level folder -> human division label. Folders not listed fall back to a
// title-cased version of the folder name.
const DIVISION_BY_FOLDER: Record<string, string> = {
  bots: "Core Fleet",
  App_bots: "Apps",
  Occupational_bots: "Occupational",
  Business_bots: "Business",
  Fiverr_bots: "Freelance",
  Marketing_bots: "Marketing",
  Real_Estate_bots: "Real Estate",
  Government_Contract_bots: "Government",
  Side_Hustle_bots: "Side Hustle",
  DreamFinance: "Finance",
  BuddyAI: "AI Core",
  ConnectionsControl: "Integrations",
};

const CATEGORY_HINTS: Array<[RegExp, string]> = [
  [/stripe|payment|billing|invoice|checkout/, "Payments"],
  [/trad(e|ing)|stock|crypto|forex|fx|bond|wealth|finance|profit|loan|invest/, "Finance"],
  [/real_?estate|property|mls|foreclosure|rental|mortgage/, "Real Estate"],
  [/lead|sales|crm|outreach|prospect/, "Sales"],
  [/market|seo|social|ad_|advertis|campaign|content|influencer|email/, "Marketing"],
  [/legal|contract|compliance|grant|government/, "Legal"],
  [/health|medical|wellness|patient|clinic/, "Health"],
  [/edu|learn|lesson|tutor|course|student/, "Education"],
  [/shop|ecommerce|store|product|inventory|fulfil/, "E-Commerce"],
  [/saas|tenant|subscription/, "SaaS"],
  [/data|sql|etl|analytic|report|dashboard/, "Data"],
  [/voice|video|image|media|audio|transcri/, "Media"],
  [/quantum|space|research|model|reason/, "AI Research"],
  [/buddy|companion|assistant|chat/, "AI Companion"],
  [/god|core|orchestrat|control|framework/, "Core"],
  [/deploy|infra|monitor|scal|devops|server/, "Infrastructure"],
];

function deriveCategory(slug: string, folder: string): string {
  const hay = `${slug} ${folder}`.toLowerCase();
  for (const [re, cat] of CATEGORY_HINTS) {
    if (re.test(hay)) return cat;
  }
  return "Automation";
}

export interface IndexedBot {
  slug: string;
  name: string;
  description: string;
  repoPath: string;
  category: string;
  division: string;
}

export interface IndexResult {
  scanned: number;
  unique: number;
  inserted: number;
  updated: number;
  byDivision: Record<string, number>;
  byCategory: Record<string, number>;
  durationMs: number;
  truncated: boolean;
}

function titleCase(s: string): string {
  return s.replace(/[_-]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()).trim();
}

/** Scan the Dreamcobots repo tree and extract every `*_bot.py` as a bot row. */
export async function scanBots(): Promise<{ bots: IndexedBot[]; scanned: number; truncated: boolean }> {
  const data = await ghFetch<{
    tree?: Array<{ type: string; path: string }>;
    truncated?: boolean;
  }>(`/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/git/trees/main?recursive=1`);

  const tree = data.tree ?? [];
  const botFiles = tree.filter(
    (e) =>
      e.type === "blob" &&
      /_bot\.py$/.test(e.path) &&
      !/(^|\/)tests?\//.test(e.path) &&
      !/(^|\/)test_/.test(e.path),
  );

  const bySlug = new Map<string, IndexedBot>();
  for (const f of botFiles) {
    const parts = f.path.split("/");
    const file = parts[parts.length - 1]!;
    const folder = parts.length > 1 ? parts[0]! : "(root)";
    const slug = file.replace(/\.py$/, "").toLowerCase();
    if (bySlug.has(slug)) continue; // first occurrence wins
    const division = DIVISION_BY_FOLDER[folder] ?? titleCase(folder);
    const category = deriveCategory(slug, folder);
    bySlug.set(slug, {
      slug,
      name: titleCase(slug.replace(/_bot$/, "")) + " Bot",
      description: `${category} bot — ${titleCase(slug.replace(/_bot$/, ""))} (${division} division). Source: ${f.path}`,
      repoPath: f.path,
      category,
      division,
    });
  }

  return { bots: [...bySlug.values()], scanned: botFiles.length, truncated: Boolean(data.truncated) };
}

/**
 * Index the Dreamcobots fleet into the agents table.
 * Upserts by slug. Preserves existing telemetry (invocations, revenue, status,
 * heartbeat) on conflict — only refreshes name/description/repoPath/config.
 */
export async function indexBots(): Promise<IndexResult> {
  const start = Date.now();
  const { bots, scanned, truncated } = await scanBots();

  const byDivision: Record<string, number> = {};
  const byCategory: Record<string, number> = {};
  for (const b of bots) {
    byDivision[b.division] = (byDivision[b.division] ?? 0) + 1;
    byCategory[b.category] = (byCategory[b.category] ?? 0) + 1;
  }

  // Deterministic insert/update accounting: read existing slugs up front so the
  // metrics don't depend on timestamp resolution or clock skew.
  const existingRows = await db.select({ slug: agentsTable.slug }).from(agentsTable);
  const existing = new Set(existingRows.map((r) => r.slug.toLowerCase()));
  let inserted = 0;
  let updated = 0;
  for (const b of bots) {
    if (existing.has(b.slug.toLowerCase())) updated++;
    else inserted++;
  }

  const CHUNK = 50;
  for (let i = 0; i < bots.length; i += CHUNK) {
    const chunk = bots.slice(i, i + CHUNK);
    const rows = chunk.map((b) => ({
      slug: b.slug,
      name: b.name,
      description: b.description,
      tier: "FREE" as const,
      status: "idle" as const,
      repoPath: b.repoPath,
      runtimeConfig: { category: b.category, division: b.division, indexedFrom: "Dreamcobots" },
    }));
    await db
      .insert(agentsTable)
      .values(rows)
      .onConflictDoUpdate({
        target: agentsTable.slug,
        set: {
          name: sql`excluded.name`,
          description: sql`excluded.description`,
          repoPath: sql`excluded.repo_path`,
          runtimeConfig: sql`excluded.runtime_config`,
          updatedAt: new Date(),
        },
      });
  }

  const out: IndexResult = {
    scanned,
    unique: bots.length,
    inserted,
    updated,
    byDivision,
    byCategory,
    durationMs: Date.now() - start,
    truncated,
  };
  logger.info(out, "Dreamcobots fleet indexed");
  return out;
}
