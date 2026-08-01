import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";

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
  assert.equal(index.summary.indexed_bot_profiles, 1051);
  assert.equal(index.summary.searchable_capability_terms, 8408);
  assert.equal(index.summary.indexed_divisions, 45);
  assert.equal(index.summary.indexed_models, 200);
  assert.equal(index.summary.indexed_providers, 200);
  assert.equal(index.summary.web_results_claimed, 0);

  const indexedBots = new Set(index.documents.filter((item) => item.type === "bot").map((item) => item.id.slice(4)));
  assert.equal(indexedBots.size, 1051);
  for (const bot of fleet.bots) assert.ok(indexedBots.has(bot.identity.slug), `missing search record for ${bot.identity.slug}`);
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
  assert.equal(externalReferences.length, 400);
  assert.ok(externalReferences.every((item) => item.status === "reference_catalog_not_connection"));
  assert.ok(externalReferences.every((item) => item.evidence_level === "reference_catalog"));
});

test("web search URLs encode one visible query", () => {
  assert.equal(
    buildDreamSearchWebUrl("https://duckduckgo.com/?q={query}", "grants & contracts"),
    "https://duckduckgo.com/?q=grants%20%26%20contracts",
  );
  assert.throws(() => buildDreamSearchWebUrl("https://example.com/?q={query}", ""), /required/);
});
