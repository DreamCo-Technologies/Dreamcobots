import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

import {
  buildDreamSearchWebUrl,
  expandSearchQuery,
  rankDreamSearchDocuments,
  type DreamSearchConfig,
  type DreamSearchDocument,
} from "../shared/dreamco-search.ts";

const searchConfig = JSON.parse(readFileSync("config/dreamco-search-engine.json", "utf8")) as DreamSearchConfig;
const index = JSON.parse(readFileSync("config/generated/dreamco_search_index.json", "utf8")) as {
  summary: Record<string, any>;
  documents: DreamSearchDocument[];
};
const fleet = JSON.parse(readFileSync("config/generated/bots.catalog.json", "utf8"));

test("DreamSearch indexes the complete routed fleet and reference catalogs", () => {
  assert.equal(index.summary.indexed_bot_profiles, 1101);
  assert.equal(index.summary.canonical_indexed_bot_profiles, 1051);
  assert.equal(index.summary.supplemental_indexed_bot_profiles, 50);
  assert.equal(index.summary.searchable_capability_terms, 8460);
  assert.equal(index.summary.canonical_searchable_capability_terms, 8408);
  assert.equal(index.summary.supplemental_searchable_capability_terms, 52);
  assert.equal(index.summary.indexed_divisions, 55);
  assert.equal(index.summary.canonical_indexed_divisions, 45);
  assert.equal(index.summary.supplemental_indexed_divisions, 10);
  assert.equal(index.summary.production_ready_bot_profiles, 0);
  assert.equal(index.summary.indexed_models, 500);
  assert.ok(index.summary.indexed_organizations >= 280);
  assert.equal(index.summary.indexed_providers, 200);
  assert.equal(index.summary.web_results_claimed, 0);

  const indexedBots = new Set(index.documents.filter((item) => item.type === "bot").map((item) => item.id.slice(4)));
  assert.equal(indexedBots.size, 1101);
  for (const bot of [...fleet.bots, ...fleet.supplemental_bots]) {
    const record = index.documents.find((item) => item.id === `bot:${bot.identity.slug}`);
    assert.ok(record, `missing search record for ${bot.identity.slug}`);
    const capabilities = bot.capability_search.split(" | ");
    assert.equal(capabilities.length, bot.capability_count);
    for (const capability of capabilities) assert.ok(record.keywords.includes(capability), `${bot.identity.slug}: ${capability}`);
  }
});

test("supplemental division documents are usable search results with source evidence and planning boundaries", () => {
  const divisions = index.documents.filter((item) => item.type === "division");
  assert.equal(divisions.length, 55);
  assert.equal(new Set(divisions.map((item) => item.division)).size, 55);
  for (const division of fleet.supplemental_divisions) {
    const record = divisions.find((item) => item.division === division.name);
    assert.ok(record, `missing division document: ${division.name}`);
    assert.equal(record.evidence, division.source);
    assert.equal(record.status, "production_evidence_required");
    assert.equal(record.url, `bots.html?q=${encodeURIComponent(division.name)}`);
    assert.ok(rankDreamSearchDocuments(index.documents, division.name, searchConfig, { type: "division" }).some((result) => result.document.id === record.id));
  }
  for (const bot of fleet.supplemental_bots) {
    const record = index.documents.find((item) => item.id === `bot:${bot.identity.slug}`)!;
    assert.equal(record.status, "routed_shared_sandbox_planning");
    assert.equal(record.evidence_level, "repository_catalog");
    assert.equal(record.evidence, bot.evidence.catalog_source);
    assert.ok(rankDreamSearchDocuments(index.documents, bot.identity.slug, searchConfig, { type: "bot" }).some((result) => result.document.id === record.id));
  }
});

test("published browser search data exactly matches the canonical search index", () => {
  const context = { window: {} as Record<string, unknown> };
  vm.runInNewContext(readFileSync("website/data/dreamco-search-index.js", "utf8"), context);
  assert.deepEqual(JSON.parse(JSON.stringify(context.window.DREAMCO_SEARCH_DATA)), index);
});

test("DreamSearch expands DreamCo task language and ranks implemented evidence above roadmap ideas", () => {
  const expanded = expandSearchQuery("make a movie", searchConfig);
  assert.ok(expanded.includes("film"));
  assert.ok(expanded.includes("storyboard"));

  const results = rankDreamSearchDocuments(index.documents, "build a game", searchConfig, { limit: 25 });
  assert.ok(results.length > 0);
  assert.ok(results.some((result) => result.document.type === "bot"));
  assert.notEqual(results[0].document.evidence_level, "roadmap");
  assert.ok(results[0].matched_terms.some((term) => ["game", "gaming", "simulation"].includes(term)));
});

test("DreamSearch returns exact bot records deterministically with evidence", () => {
  const bot = index.documents.find((item) => item.type === "bot");
  assert.ok(bot);
  const first = rankDreamSearchDocuments(index.documents, bot!.title, searchConfig, { limit: 5 });
  const second = rankDreamSearchDocuments(index.documents, bot!.title, searchConfig, { limit: 5 });
  assert.equal(first[0].document.id, bot!.id);
  assert.deepEqual(first.map((item) => item.document.id), second.map((item) => item.document.id));
  assert.ok(first[0].document.evidence.startsWith("App_bots/"));
});

test("DreamSearch routes common DreamCo outcomes to usable public tools", () => {
  const expectedPages = new Map([
    ["build a game", "studio.html"],
    ["make a movie", "studio.html"],
    ["find grants and contracts", "government.html"],
    ["debug my repository", "test-center.html"],
    ["compare AI models", "models.html"],
  ]);
  for (const [query, url] of expectedPages) {
    const result = rankDreamSearchDocuments(index.documents, query, searchConfig, { limit: 1 });
    assert.equal(result[0]?.document.url, url, query);
  }
});

test("DreamSearch labels model and provider entries as reference-only", () => {
  const externalReferences = index.documents.filter((item) => item.type === "model" || item.type === "provider");
  assert.equal(externalReferences.length, index.summary.indexed_models + index.summary.indexed_providers);
  assert.ok(externalReferences.every((item) => item.status === "reference_catalog_not_connection"));
  assert.ok(externalReferences.every((item) => item.evidence_level === "reference_catalog"));
});

test("DreamSearch indexes Alliance members without claiming capability or connection", () => {
  const organizations = index.documents.filter((item) => item.type === "organization");
  assert.ok(organizations.length >= 280);
  const alliance = organizations.filter((item) => item.category === "AI Alliance member");
  assert.ok(alliance.length >= 190);
  assert.ok(alliance.every((item) => item.evidence_level === "official_directory_membership"));
  assert.ok(alliance.every((item) => item.status.includes("required")));
});

test("web search URLs encode one visible query", () => {
  assert.equal(
    buildDreamSearchWebUrl("https://duckduckgo.com/?q={query}", "grants & contracts"),
    "https://duckduckgo.com/?q=grants%20%26%20contracts",
  );
  assert.throws(() => buildDreamSearchWebUrl("https://example.com/?q={query}", ""), /required/);
});
