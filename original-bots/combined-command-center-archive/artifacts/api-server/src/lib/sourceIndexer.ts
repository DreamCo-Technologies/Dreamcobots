import { db, aiSourcesTable } from "@workspace/db";
import { sql, notInArray } from "drizzle-orm";
import { logger } from "./logger";
import { DREAMCOBOTS_REPO, GITHUB_ORG, ghFetch, ghFetchRaw } from "./githubClient";

/**
 * Indexes the "global AI sources" — the AI-infrastructure Python modules in the
 * Dreamcobots repo (model registries, routers, the global-ai-sources flow,
 * capability registries, connectors, orchestrators). For each it stores the
 * module docstring and lightweight parsed signals so Buddy and the dashboard
 * have a live catalog of what the system can route to and learn from.
 */

// Path patterns that identify an AI-infrastructure module, with a role label.
// Order matters — first match wins.
const ROLE_RULES: Array<[RegExp, string]> = [
  [/model_registry|models\/registry|ai_models|model.*registry/i, "registry"],
  [/global_ai_sources_flow|global.*sources/i, "flow"],
  [/task_router|model_router|router_agent|bot_router|event_router/i, "router"],
  [/capability_registry|capabilities\/models|capabilit/i, "capability"],
  [/connector|api_registry|openai_connector|gemini_connector/i, "connector"],
  [/orchestrat/i, "orchestrator"],
  [/registry/i, "registry"],
  [/benchmark/i, "benchmark"],
];

// Only index files whose path matches one of these (keeps the catalog focused
// on real AI infrastructure rather than every bot's helper).
const INCLUDE = /(registry|router|orchestrat|global_ai_sources|global_sources|capabilit|connector|api_registry|benchmark|model_router|router_agent|model_registry)/i;
const EXCLUDE = /(^|\/)tests?\/|(^|\/)test_|__pycache__/i;

function classifyRole(path: string): string {
  for (const [re, role] of ROLE_RULES) if (re.test(path)) return role;
  return "module";
}

function titleFromPath(path: string): string {
  const file = path.split("/").pop() ?? path;
  return file.replace(/\.py$/, "").replace(/[_-]+/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function extractDocstring(src: string): string {
  const m = src.match(/^\s*(?:[rRbBuU]*)("""|''')([\s\S]*?)\1/);
  if (!m) return "";
  return m[2]!.trim().split("\n").slice(0, 6).join("\n").trim();
}

function parseSignals(src: string): Record<string, number | string[]> {
  const classes = [...src.matchAll(/^\s*class\s+([A-Za-z_]\w*)/gm)].map((m) => m[1]!);
  const functions = (src.match(/^\s*(?:async\s+)?def\s+\w+/gm) ?? []).length;
  const models = (src.match(/\bAIModel\s*\(/g) ?? []).length;
  const useCases = (src.match(/\bUseCase\s*\(/g) ?? []).length;
  const providers = [...new Set([...src.matchAll(/"(OpenAI|Anthropic|Google|Meta|Mistral|Cohere|xAI|DeepSeek|Stability|ElevenLabs|HuggingFace|Replicate)"/gi)].map((m) => m[1]!))];
  return {
    classes: classes.slice(0, 12),
    classCount: classes.length,
    functions,
    models,
    useCases,
    providers,
  };
}

export interface IndexedSource {
  key: string;
  name: string;
  role: string;
  summary: string;
  repoPath: string;
  sizeBytes: number;
  signals: Record<string, unknown>;
}

export interface SourceIndexResult {
  scanned: number;
  indexed: number;
  inserted: number;
  updated: number;
  pruned: number;
  byRole: Record<string, number>;
  totalModels: number;
  totalUseCases: number;
  durationMs: number;
}

async function fetchRaw(path: string): Promise<string> {
  const raw = await ghFetchRaw(`/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/contents/${path}`);
  if (raw == null) throw new Error(`could not fetch ${path}`);
  return raw;
}

export async function indexSources(limit = 40): Promise<SourceIndexResult> {
  const start = Date.now();
  const tree = await ghFetch<{ tree?: Array<{ type: string; path: string; size?: number }> }>(
    `/repos/${GITHUB_ORG}/${DREAMCOBOTS_REPO}/git/trees/main?recursive=1`,
  );
  const candidates = (tree.tree ?? []).filter(
    (e) => e.type === "blob" && e.path.endsWith(".py") && INCLUDE.test(e.path) && !EXCLUDE.test(e.path),
  );

  // Prioritize the high-value AI infrastructure modules so the catalog always
  // captures the registries/routers/flow first, and cap low-signal connectors
  // so a single bot's connector folder can't crowd out everything else.
  function priority(path: string): number {
    if (/global_sources_ai_bot\/model_registry|global_ai_sources_flow|global_sources_ai_bot/i.test(path)) return 100;
    const role = classifyRole(path);
    return { flow: 90, registry: 80, router: 70, capability: 60, orchestrator: 50, benchmark: 40, connector: 10, module: 20 }[role] ?? 20;
  }
  const ranked = [...candidates].sort((a, b) => priority(b.path) - priority(a.path));
  const CONNECTOR_CAP = 8;
  let connectors = 0;
  const sliced: typeof ranked = [];
  for (const e of ranked) {
    if (sliced.length >= limit) break;
    if (classifyRole(e.path) === "connector") {
      if (connectors >= CONNECTOR_CAP) continue;
      connectors++;
    }
    sliced.push(e);
  }
  const sources: IndexedSource[] = [];
  for (const f of sliced) {
    let src = "";
    try {
      src = await fetchRaw(f.path);
    } catch (err) {
      logger.warn({ err, path: f.path }, "source fetch failed, skipping");
      continue;
    }
    sources.push({
      key: f.path,
      name: titleFromPath(f.path),
      role: classifyRole(f.path),
      summary: extractDocstring(src) || `${titleFromPath(f.path)} (${f.path})`,
      repoPath: f.path,
      sizeBytes: f.size ?? src.length,
      signals: parseSignals(src),
    });
  }

  const byRole: Record<string, number> = {};
  let totalModels = 0;
  let totalUseCases = 0;
  for (const s of sources) {
    byRole[s.role] = (byRole[s.role] ?? 0) + 1;
    totalModels += Number((s.signals as any).models ?? 0);
    totalUseCases += Number((s.signals as any).useCases ?? 0);
  }

  const existingRows = await db.select({ key: aiSourcesTable.key }).from(aiSourcesTable);
  const existing = new Set(existingRows.map((r) => r.key));
  let inserted = 0;
  let updated = 0;
  for (const s of sources) (existing.has(s.key) ? updated++ : inserted++);

  const CHUNK = 25;
  for (let i = 0; i < sources.length; i += CHUNK) {
    const rows = sources.slice(i, i + CHUNK).map((s) => ({
      key: s.key,
      name: s.name,
      role: s.role,
      language: "python",
      summary: s.summary,
      repoPath: s.repoPath,
      sizeBytes: s.sizeBytes,
      signals: s.signals,
      indexedFrom: "Dreamcobots",
    }));
    await db
      .insert(aiSourcesTable)
      .values(rows)
      .onConflictDoUpdate({
        target: aiSourcesTable.key,
        set: {
          name: sql`excluded.name`,
          role: sql`excluded.role`,
          summary: sql`excluded.summary`,
          repoPath: sql`excluded.repo_path`,
          sizeBytes: sql`excluded.size_bytes`,
          signals: sql`excluded.signals`,
          updatedAt: new Date(),
        },
      });
  }

  // Reconcile: drop rows whose source file no longer exists / no longer matches
  // (files that disappear from the repo). We prune against the FULL candidate
  // set — not just this run's limited slice — so validly-indexed modules that
  // weren't re-fetched this run are preserved. Guarded so an empty/failed tree
  // fetch can never wipe the catalog.
  let pruned = 0;
  if (candidates.length > 0) {
    const candidateKeys = candidates.map((c) => c.path);
    const deleted = await db
      .delete(aiSourcesTable)
      .where(notInArray(aiSourcesTable.key, candidateKeys))
      .returning({ key: aiSourcesTable.key });
    pruned = deleted.length;
  }

  const out: SourceIndexResult = {
    scanned: candidates.length,
    indexed: sources.length,
    inserted,
    updated,
    pruned,
    byRole,
    totalModels,
    totalUseCases,
    durationMs: Date.now() - start,
  };
  logger.info(out, "Global AI sources indexed");
  return out;
}
