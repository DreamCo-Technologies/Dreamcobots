#!/usr/bin/env tsx
/** Generate DreamSearch's evidence-labeled local index from repository sources. */

import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import { AI_PROVIDERS } from "../shared/ai-ecosystem.ts";
import { MODEL_BENCHMARK_TARGETS } from "../shared/model-benchmark-targets.ts";
import type { DreamSearchConfig, DreamSearchDocument } from "../shared/dreamco-search.ts";
import { normalizeSearchText } from "../shared/dreamco-search.ts";
import { buildFleetCatalog } from "./generate_bot_fleet_catalog.ts";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CONFIG_PATH = join(ROOT, "config", "dreamco-search-engine.json");
const GENERATED_PATH = join(ROOT, "config", "generated", "dreamco_search_index.json");
const WEBSITE_PATH = join(ROOT, "website", "data", "dreamco-search-index.js");
const SYSTEM_MAP_PATH = join(ROOT, "website", "data", "repository-system-map.json");
const PLATFORM_PATH = join(ROOT, "config", "generated", "buddy_platform_expansion.json");
const REPORT_PATH = join(ROOT, "reports", "DREAMCO_SEARCH_INDEX.md");
const WEBSITE_DIR = join(ROOT, "website");

type PlatformExpansion = {
  implemented_capabilities: Array<{ id: string; name: string; status: string; evidence: string }>;
  revolutionary_ideas: Array<{ id: string; idea: string; theme: string; status: string; kind: string }>;
  companion_ideas: Array<{ id: string; idea: string; theme: string; status: string; kind: string }>;
};

type RepositorySystemMap = {
  systems: Array<{ label: string; detail: string; source: string; status: string }>;
  libraries: Array<{ id: string; name: string; description: string; count: number }>;
  divisions: Array<{ id: string; name: string; mission: string; registered_bots: number }>;
};

const PAGE_DESCRIPTIONS: Record<string, string> = {
  "buddy.html": "Talk with Buddy, route work to DreamCo specialists, and prepare governed task plans.",
  "search.html": "Search DreamCo bots, capabilities, models, providers, divisions, systems, libraries, and public tools.",
  "bots.html": "Browse the complete Buddy specialist fleet and open evidence-backed bot prospectuses.",
  "models.html": "Compare the DreamCo model reference catalog and prepare governed benchmark plans.",
  "platform.html": "Inspect implemented capability contracts and clearly labeled roadmap ideas.",
  "system-map.html": "Review repository systems, libraries, divisions, and honest readiness evidence.",
  "studio.html": "Plan and test consent-first voice, image, music, movie, course, game, and simulation projects.",
  "test-center.html": "Prepare repository test plans and inspect fleet capability certification evidence.",
  "government.html": "Find and organize official government resources without automating applications or eligibility decisions.",
  "connections.html": "Plan least-privilege connections to approved apps, APIs, webhooks, devices, and data sources.",
  "data-control.html": "Manage local memory preferences, data rights plans, consent evidence, and owner-created data packages.",
};

const PAGE_KEYWORDS: Record<string, string[]> = {
  "buddy.html": ["task", "chat", "specialist", "plan", "discover", "help me figure it out"],
  "search.html": ["search", "find", "discover", "catalog", "capability", "specialist"],
  "studio.html": ["build a game", "make a movie", "movie", "film", "video", "storyboard", "production", "game", "simulation", "voice", "image", "music", "course", "character"],
  "government.html": ["find grants and contracts", "grant", "contract", "procurement", "federal", "state", "local", "official resource"],
  "test-center.html": ["debug my repository", "test", "debug", "failure", "repository", "quality", "capability certification"],
  "models.html": ["compare AI models", "compare", "benchmark", "AI model", "LLM", "provider", "free model", "paid model"],
  "calculator.html": ["real estate ROI", "ROI", "estimate", "cost", "revenue", "real estate", "deal", "finance"],
  "connections.html": ["API", "webhook", "integration", "authentication", "database", "server", "app connection"],
  "bots.html": ["bot", "specialist", "prospectus", "capability", "fleet", "test bot"],
};

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(path, "utf8")) as T;
}

function unique(values: Array<string | undefined>): string[] {
  return [...new Set(values.map((value) => String(value || "").trim()).filter(Boolean))];
}

function slug(value: string): string {
  return normalizeSearchText(value).replace(/\s+/g, "-") || "item";
}

function pageTitle(html: string, filename: string): string {
  const match = html.match(/<title>([^<]+)<\/title>/i);
  return match?.[1]?.replace(/\s*[|\-]\s*DreamCo.*$/i, "").trim()
    || filename.replace(/\.html$/i, "").replace(/-/g, " ");
}

function pageDescription(html: string, filename: string): string {
  const match = html.match(/<meta\s+name=["']description["']\s+content=["']([^"']+)["']/i)
    || html.match(/<meta\s+content=["']([^"']+)["']\s+name=["']description["']/i);
  return PAGE_DESCRIPTIONS[filename] || match?.[1]?.trim() || `Open the DreamCo ${pageTitle(html, filename)} page.`;
}

function document(input: DreamSearchDocument): DreamSearchDocument {
  const keywords = unique(input.keywords);
  return {
    ...input,
    keywords,
    search_text: normalizeSearchText([
      input.title,
      input.summary,
      input.category,
      input.division,
      input.status,
      input.evidence_level,
      ...keywords,
    ].join(" ")),
  };
}

export function buildDreamSearchIndex() {
  const config = readJson<DreamSearchConfig & Record<string, unknown>>(CONFIG_PATH);
  const platform = readJson<PlatformExpansion>(PLATFORM_PATH);
  const systemMap = readJson<RepositorySystemMap>(SYSTEM_MAP_PATH);
  const fleet = buildFleetCatalog();
  const documents: DreamSearchDocument[] = [];

  for (const bot of fleet.bots) {
    documents.push(document({
      id: `bot:${bot.identity.slug}`,
      type: "bot",
      title: `${bot.logo.emoji} ${bot.identity.display_name}`,
      summary: bot.prospectus.mission,
      url: `bots.html?prospectus=${encodeURIComponent(bot.identity.slug)}`,
      keywords: unique([
        bot.identity.slug,
        bot.identity.category,
        bot.identity.division,
        bot.identity.tier,
        "Buddy specialist",
        "ROI calculator",
        ...bot.capabilities.map((capability) => capability.name),
        ...bot.tools.map((tool) => String(tool.name || "")),
        ...bot.api_candidates.map((api) => api.name),
      ]),
      category: bot.identity.category,
      division: bot.identity.division || "",
      status: "routed_shared_runtime",
      evidence_level: "repository_catalog",
      evidence: bot.evidence.catalog_source,
    }));
  }

  for (const division of systemMap.divisions) {
    documents.push(document({
      id: `division:${division.id}`,
      type: "division",
      title: division.name,
      summary: division.mission,
      url: `divisions.html#${division.id}`,
      keywords: ["division", "specialists", "Buddy", `${division.registered_bots} bots`],
      category: "DreamCo division",
      division: division.name,
      status: "registered",
      evidence_level: "repository_catalog",
      evidence: "config/master_bot_registry.json",
    }));
  }

  for (const model of MODEL_BENCHMARK_TARGETS) {
    documents.push(document({
      id: `model:${model.id}`,
      type: "model",
      title: model.name,
      summary: model.bestFor,
      url: "models.html",
      keywords: unique([model.provider, model.category, model.tier, model.developerRegion, ...model.declaredCapabilities]),
      category: model.category,
      division: "DreamAIInfra",
      status: "reference_catalog_not_connection",
      evidence_level: "reference_catalog",
      evidence: model.discoveryTarget ? "shared/model-benchmark-targets.ts#official-discovery" : "shared/ai-models.ts",
    }));
  }

  for (const provider of AI_PROVIDERS) {
    documents.push(document({
      id: `provider:${provider.id}`,
      type: "provider",
      title: provider.name,
      summary: `${provider.coreSkill}. Best at: ${provider.bestAt}.`,
      url: "ecosystem.html",
      keywords: unique([
        provider.category,
        provider.freeVsPaid,
        provider.integrationStrategy,
        provider.agentSpecialization,
        ...provider.bundleFit,
      ]),
      category: provider.category,
      division: "DreamAIInfra",
      status: "reference_catalog_not_connection",
      evidence_level: "reference_catalog",
      evidence: "shared/ai-ecosystem.ts",
    }));
  }

  for (const capability of platform.implemented_capabilities) {
    documents.push(document({
      id: `capability:${capability.id}`,
      type: "capability",
      title: capability.name,
      summary: `DreamCo capability contract with status ${capability.status.replaceAll("_", " ")}.`,
      url: "platform.html",
      keywords: [capability.id, capability.status, "implemented capability", "Buddy tool"],
      category: "Platform capability",
      division: "CommandCore",
      status: capability.status,
      evidence_level: "implementation_evidence",
      evidence: capability.evidence,
    }));
  }

  for (const idea of [...platform.revolutionary_ideas, ...platform.companion_ideas]) {
    documents.push(document({
      id: `roadmap:${idea.id}`,
      type: "roadmap",
      title: idea.idea.replace(/\.$/, ""),
      summary: `${idea.theme.replace(/\b\w/g, (letter) => letter.toUpperCase())} concept. This remains a labeled roadmap idea, not an implemented capability.`,
      url: "platform.html",
      keywords: [idea.id, idea.kind, idea.theme, "roadmap idea"],
      category: idea.kind === "opt_in" ? "Companion roadmap" : "Innovation roadmap",
      division: "DreamDecision",
      status: idea.status,
      evidence_level: "roadmap",
      evidence: "config/generated/buddy_platform_expansion.json",
    }));
  }

  for (const system of systemMap.systems) {
    documents.push(document({
      id: `system:${slug(system.label)}`,
      type: "system",
      title: system.label,
      summary: system.detail,
      url: "system-map.html",
      keywords: [system.source, system.status, "repository system"],
      category: "Repository system",
      division: "CommandCore",
      status: system.status,
      evidence_level: "repository_evidence",
      evidence: system.source,
    }));
  }

  for (const library of systemMap.libraries) {
    documents.push(document({
      id: `library:${library.id}`,
      type: "library",
      title: library.name,
      summary: library.description,
      url: "system-map.html",
      keywords: [library.id, `${library.count} records`, "library", "catalog"],
      category: "DreamCo library",
      division: "DreamData",
      status: "generated",
      evidence_level: "repository_evidence",
      evidence: "website/data/repository-system-map.json",
    }));
  }

  for (const filename of readdirSync(WEBSITE_DIR).filter((name) => name.endsWith(".html")).sort()) {
    const html = readFileSync(join(WEBSITE_DIR, filename), "utf8");
    const title = pageTitle(html, filename);
    documents.push(document({
      id: `page:${filename}`,
      type: "page",
      title,
      summary: pageDescription(html, filename),
      url: filename,
      keywords: [
        filename.replace(/\.html$/, "").replace(/-/g, " "),
        "DreamCo page",
        "public tool",
        ...(PAGE_KEYWORDS[filename] || []),
      ],
      category: "Public page",
      division: "CommandCore",
      status: "public_static_page",
      evidence_level: "public_page",
      evidence: `website/${filename}`,
    }));
  }

  const duplicateIds = documents.filter((item, index) => documents.findIndex((candidate) => candidate.id === item.id) !== index);
  if (duplicateIds.length) throw new Error(`Duplicate search document IDs: ${unique(duplicateIds.map((item) => item.id)).join(", ")}`);

  const countsByType = Object.fromEntries(
    [...new Set(documents.map((item) => item.type))].sort().map((type) => [type, documents.filter((item) => item.type === type).length]),
  );
  const evidenceLevels = [...new Set(documents.map((item) => item.evidence_level))].sort();
  const divisions = [...new Set(documents.map((item) => item.division).filter(Boolean))].sort();

  return {
    schema: "dreamco.search_index.v1",
    engine: {
      name: String(config.name || "DreamSearch"),
      description: String(config.description || "DreamCo search"),
      query_policy: config.query_policy,
      ranking: config.ranking,
      result_policy: config.result_policy,
      web_search: config.web_search,
    },
    summary: {
      documents: documents.length,
      counts_by_type: countsByType,
      indexed_bot_profiles: fleet.summary.profiles,
      searchable_capability_terms: fleet.summary.declared_capability_slots,
      indexed_divisions: fleet.summary.divisions,
      indexed_models: MODEL_BENCHMARK_TARGETS.length,
      indexed_providers: AI_PROVIDERS.length,
      indexed_public_pages: countsByType.page || 0,
      web_results_claimed: 0,
    },
    filters: { divisions, evidence_levels: evidenceLevels },
    documents,
  };
}

function stableJson(value: unknown): string {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function report(index: ReturnType<typeof buildDreamSearchIndex>): string {
  const rows = Object.entries(index.summary.counts_by_type)
    .map(([type, count]) => `| ${type} | ${Number(count).toLocaleString()} |`);
  return [
    "# DreamSearch Index",
    "",
    "DreamSearch is a generated, local-first index. It does not claim live internet results or connected external providers.",
    "",
    "## Inventory",
    "",
    `- Search documents: ${index.summary.documents.toLocaleString()}`,
    `- Bot profiles: ${index.summary.indexed_bot_profiles.toLocaleString()}`,
    `- Searchable bot capability terms: ${index.summary.searchable_capability_terms.toLocaleString()}`,
    `- Divisions: ${index.summary.indexed_divisions.toLocaleString()}`,
    `- Model reference records: ${index.summary.indexed_models.toLocaleString()}`,
    `- Provider reference records: ${index.summary.indexed_providers.toLocaleString()}`,
    `- Public pages: ${index.summary.indexed_public_pages.toLocaleString()}`,
    `- Live web results claimed: ${index.summary.web_results_claimed}`,
    "",
    "| Result type | Count |",
    "| --- | ---: |",
    ...rows,
    "",
    "## Boundary",
    "",
    "Web mode creates user-initiated links to allowlisted search engines or a citation-first Buddy research prompt. It does not crawl, scrape, or transmit private repository content.",
    "",
  ].join("\n");
}

export function writeDreamSearchIndex({ check = false } = {}) {
  const index = buildDreamSearchIndex();
  const outputs = [
    [GENERATED_PATH, stableJson(index)],
    [WEBSITE_PATH, `window.DREAMCO_SEARCH_DATA=${JSON.stringify(index)};\n`],
    [REPORT_PATH, report(index)],
  ] as const;
  if (check) {
    for (const [path, expected] of outputs) {
      if (readFileSync(path, "utf8") !== expected) throw new Error(`${relative(ROOT, path)} is stale; regenerate DreamSearch`);
    }
  } else {
    mkdirSync(dirname(GENERATED_PATH), { recursive: true });
    mkdirSync(dirname(WEBSITE_PATH), { recursive: true });
    for (const [path, content] of outputs) writeFileSync(path, content, "utf8");
  }
  return index.summary;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  const summary = writeDreamSearchIndex({ check: process.argv.includes("--check") });
  console.log(JSON.stringify({ ok: true, ...summary }, null, 2));
}
