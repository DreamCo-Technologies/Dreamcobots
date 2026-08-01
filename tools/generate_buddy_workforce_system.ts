import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { buildWorkforceRegistry } from "../server/workforce-engine";

const root = process.cwd();
const jsonPath = resolve(root, "config", "generated", "buddy_workforce_system.json");
const jsPath = resolve(root, "website", "data", "buddy-workforce-system.js");
const registry = buildWorkforceRegistry();
const json = `${JSON.stringify(registry, null, 2)}\n`;
const js = `window.BUDDY_WORKFORCE_SYSTEM = ${JSON.stringify(registry)};\n`;
const check = process.argv.includes("--check");

if (registry.summary.syntheticJobFixtures !== 100) throw new Error("Workforce registry must include exactly 100 synthetic job fixtures.");
if (registry.summary.liveExternalActionsEnabled) throw new Error("Generated workforce registry cannot enable live external actions.");

if (check) {
  if (readFileSync(jsonPath, "utf8") !== json || readFileSync(jsPath, "utf8") !== js) {
    throw new Error("Buddy workforce outputs are stale. Regenerate them.");
  }
  process.stdout.write(`${JSON.stringify({ ok: true, workers: registry.summary.workerBots, fixtures: 100 }, null, 2)}\n`);
} else {
  writeFileSync(jsonPath, json, "utf8");
  writeFileSync(jsPath, js, "utf8");
  process.stdout.write(`${JSON.stringify({ generated: ["config/generated/buddy_workforce_system.json", "website/data/buddy-workforce-system.js"] }, null, 2)}\n`);
}
