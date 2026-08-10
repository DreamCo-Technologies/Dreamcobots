import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const generated = JSON.parse(readFileSync(resolve(root, "config", "generated", "buddy_demand_ontology.json"), "utf8"));
const publicScript = readFileSync(resolve(root, "website", "data", "buddy-demand-ontology.js"), "utf8");

if (generated.summary.catalogs !== 3 || generated.summary.reasons !== 300 || generated.summary.modelOptionsPerReason !== 20) {
  throw new Error("Demand ontology summary is invalid");
}
for (const catalog of generated.catalogs) {
  if (catalog.reasonCount !== 100) throw new Error(`Expected 100 reasons for ${catalog.id}`);
}
if (generated.reasons.some((reason) => !reason.taskCategory || reason.capabilities.length < 3)) {
  throw new Error("Every demand reason must map to a task category and capabilities");
}
if (publicScript !== `window.BUDDY_DEMAND_ONTOLOGY = ${JSON.stringify(generated)};\n`) {
  throw new Error("Public demand ontology is stale");
}
console.log(JSON.stringify(generated.summary));
