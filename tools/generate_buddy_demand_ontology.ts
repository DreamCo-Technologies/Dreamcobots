import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  DEMAND_CATALOG_IDS,
  DEMAND_REASONS,
  DEMAND_RESEARCH_SOURCES,
} from "../shared/ai-demand-ontology";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const generatedPath = resolve(root, "config", "generated", "buddy_demand_ontology.json");
const publicPath = resolve(root, "website", "data", "buddy-demand-ontology.js");

function buildCatalog() {
  const catalogs = DEMAND_CATALOG_IDS.map((id) => {
    const reasons = DEMAND_REASONS.filter((reason) => reason.catalogId === id);
    return {
      id,
      label: id === "ai_usage" ? "Why people use AI" : id === "downloaded_apps" ? "Why people use downloaded apps" : "Why people pay online",
      reasonCount: reasons.length,
      categories: [...new Set(reasons.map((reason) => reason.category))],
      researchSourceIds: DEMAND_RESEARCH_SOURCES.filter((source) =>
        (source.catalogs as readonly string[]).includes(id),
      ).map((source) => source.id),
    };
  });
  return {
    schema: "dreamco.buddy_demand_ontology.v1",
    reviewedOn: "2026-08-10",
    policy: {
      everyCatalogContainsExactly100Reasons: true,
      reasonRankIsEditorialCoverageOrderNotMarketShare: true,
      researchSourcesAreMarketAnchorsNotProofOfEachIndividualRank: true,
      everyReasonMapsToTaskCategoryAndCapabilities: true,
      eachMatchReturns20UserSelectableModelOptions: true,
      modelChoiceNeverAuthorizesProviderUseOrPayment: true,
    },
    summary: {
      catalogs: catalogs.length,
      reasons: DEMAND_REASONS.length,
      categories: new Set(DEMAND_REASONS.map((reason) => reason.category)).size,
      taskCategories: new Set(DEMAND_REASONS.map((reason) => reason.taskCategory)).size,
      modelOptionsPerReason: 20,
      researchSources: DEMAND_RESEARCH_SOURCES.length,
    },
    catalogs,
    researchSources: DEMAND_RESEARCH_SOURCES,
    reasons: DEMAND_REASONS,
  };
}

const catalog = buildCatalog();
const json = `${JSON.stringify(catalog, null, 2)}\n`;
const script = `window.BUDDY_DEMAND_ONTOLOGY = ${JSON.stringify(catalog)};\n`;
const checkOnly = process.argv.includes("--check");

if (checkOnly) {
  if (readFileSync(generatedPath, "utf8") !== json) throw new Error(`Generated file is stale: ${generatedPath}`);
  if (readFileSync(publicPath, "utf8") !== script) throw new Error(`Generated file is stale: ${publicPath}`);
} else {
  writeFileSync(generatedPath, json);
  writeFileSync(publicPath, script);
}

console.log(JSON.stringify(catalog.summary));
