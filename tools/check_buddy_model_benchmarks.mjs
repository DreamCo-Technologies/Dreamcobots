import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(resolve(root, "shared", "ai-models.ts"), "utf8");
const config = JSON.parse(readFileSync(resolve(root, "config", "buddy-model-benchmarks.json"), "utf8"));
const generatedText = readFileSync(resolve(root, "config", "generated", "buddy_model_benchmarks.json"), "utf8");
const publicScript = readFileSync(resolve(root, "website", "data", "buddy-model-benchmarks.js"), "utf8");
const catalog = JSON.parse(generatedText);

const sourceTargets = [...source.matchAll(/\{ id: (\d+), name: "((?:[^"\\]|\\.)*)"/g)].map((match) => ({
  id: Number(match[1]),
  name: JSON.parse(`"${match[2]}"`),
}));

if (sourceTargets.length !== 100) throw new Error(`Expected 100 curated source targets, found ${sourceTargets.length}`);
if (catalog.targets.length !== config.target_count) throw new Error(`Expected ${config.target_count} generated targets, found ${catalog.targets.length}`);
if (catalog.suites.length !== config.suites.length) throw new Error("Generated benchmark suites do not match the source config");
if (publicScript !== `window.BUDDY_MODEL_BENCHMARKS = ${JSON.stringify(catalog)};\n`) throw new Error("Public benchmark script is stale");

sourceTargets.forEach((sourceTarget, index) => {
  const target = catalog.targets[index];
  if (target.id !== sourceTarget.id || target.name !== sourceTarget.name) {
    throw new Error(`Benchmark target drift at position ${index + 1}`);
  }
  if (!target.catalogReady || !target.officialCatalog || !target.sourceConnection?.sourceLinked || !target.sourceConnection?.setupPathReady || target.liveEvidenceStatus !== "not_run" || target.liveScore !== null || target.promptLibrary.length < 4) {
    throw new Error(`Invalid evidence state for ${target.name}`);
  }
});

catalog.targets.slice(sourceTargets.length).forEach((target) => {
  if (!target.discoveryTarget || !target.officialCatalog || !target.sourceConnection?.sourceLinked || !target.sourceConnection?.setupPathReady || target.liveEvidenceStatus !== "discovery_required" || target.liveScore !== null) {
    throw new Error(`Invalid discovery evidence state for ${target.name}`);
  }
});

if (catalog.summary.sourceLinked !== 500 || catalog.summary.setupPathsReady !== 500 || catalog.summary.liveConnected !== 0) {
  throw new Error("Model source connection summary is invalid");
}

console.log(JSON.stringify(catalog.summary));
