import { spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import type { VerificationExpectation, UniversalVerificationReport } from "../shared/universal-verification-contract.js";
import { isVerificationRunSuccessful } from "../shared/universal-verification-policy.js";

const args = new Set(process.argv.slice(2));
const mode = args.has("--production") ? "production" : args.has("--full") ? "full" : args.has("--quick") ? "quick" : "ci";

const expectations: VerificationExpectation[] = [
  { id: "types", owner: "platform", level: "contract", description: "TypeScript contracts and imports compile cleanly", command: "npm run check", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "dependencies", owner: "platform", level: "security", description: "Repository dependency graph and required files are valid", command: "npm run buddy:dependencies", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "governed-tests", owner: "fleet", level: "integration", description: "Governed bot, policy, runtime, UI, and Python tests pass", command: "npm run test:governed", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 1800 },
  { id: "repository-audit", owner: "platform", level: "contract", description: "Repository registry is current with no blocked structural checks", command: "npm run buddy:repository-audit", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "fleet-catalog", owner: "fleet", level: "contract", description: "Canonical bot fleet catalog and routing metadata are current", command: "npm run buddy:fleet", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "fleet-quality", owner: "fleet", level: "contract", description: "All generated fleet quality plans are current and valid", command: "npm run buddy:fleet-quality", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "fleet-e2e", owner: "fleet", level: "e2e", description: "Bot fleet end-to-end execution profiles pass", command: "npm run buddy:fleet:e2e", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 3600 },
  { id: "connections", owner: "integrations", level: "integration", description: "Connection catalog, auth boundaries, and connector contracts are current", command: "npm run buddy:connections", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "models", owner: "ai-infra", level: "integration", description: "Model router catalog and provider selection contracts are current", command: "npm run buddy:models", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "model-benchmarks", owner: "ai-infra", level: "performance", description: "Model benchmark definitions and evaluation contracts are current", command: "npm run buddy:model-benchmarks", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 1200 },
  { id: "ai-organizations", owner: "research", level: "integration", description: "AI organization intelligence catalog is current", command: "npm run buddy:ai-organizations", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "open-model-lab", owner: "ai-infra", level: "integration", description: "Open model evaluation and training-lab contracts are current", command: "npm run buddy:open-model-lab", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "search", owner: "search", level: "integration", description: "DreamCo search index is current and valid", command: "npm run buddy:search", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "platform", owner: "platform", level: "integration", description: "Platform expansion contracts and provider adapters are current", command: "npm run buddy:platform", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "distribution", owner: "distribution", level: "integration", description: "Distribution and packaging targets are current", command: "npm run buddy:distribution", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "workforce", owner: "workforce", level: "integration", description: "Workforce, job, and task-routing systems are current", command: "npm run buddy:workforce", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "calculators", owner: "fleet", level: "integration", description: "Bot calculator systems and deterministic formulas are current", command: "npm run buddy:calculators", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "specialized-hubs", owner: "platform", level: "integration", description: "Specialized hub catalogs and routes are current", command: "npm run buddy:specialized-hubs", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 900 },
  { id: "defense", owner: "security", level: "security", description: "Defensive AI/security program checks pass", command: "npm run buddy:defense", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "success", owner: "benchmarks", level: "integration", description: "Buddy success and division benchmark program checks pass", command: "npm run buddy:success", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "creative", owner: "creator", level: "integration", description: "Creative studio generated systems are current", command: "npm run buddy:creative-studio", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "local-media", owner: "media", level: "integration", description: "Local media catalog and offline media contracts are current", command: "npm run buddy:local-media", requiredForMerge: false, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "media-quality", owner: "media", level: "integration", description: "Media quality lab checks pass", command: "npm run buddy:media-quality", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "behavior", owner: "behavior", level: "integration", description: "Communication behavior program checks pass", command: "npm run buddy:behavior", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "self-improvement", owner: "learning", level: "integration", description: "Self-improvement program checks pass", command: "npm run buddy:self-improvement", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "connected-life", owner: "devices", level: "integration", description: "Connected-life policies and generated systems are current", command: "npm run buddy:connected-life", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "practice", owner: "learning", level: "integration", description: "Practice lab checks pass", command: "npm run buddy:practice", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "site", owner: "web", level: "ui", description: "Public Buddy site is current and internally valid", command: "npm run buddy:site:check", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "deployment-cost", owner: "platform", level: "performance", description: "Deployment cost policy remains within configured limits", command: "npm run buddy:deployment-cost-check", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 600 },
  { id: "build", owner: "platform", level: "build", description: "Production application build completes successfully", command: "npm run build", requiredForMerge: true, requiredForProduction: true, requiresCredentials: false, timeoutSeconds: 1800 }
];

function shouldRun(item: VerificationExpectation) {
  if (mode === "quick") return ["types", "dependencies", "governed-tests", "build"].includes(item.id);
  if (mode === "ci") return item.requiredForMerge;
  return true;
}

function run(item: VerificationExpectation) {
  const started = Date.now();
  if (!shouldRun(item)) return { expectationId: item.id, state: "skipped" as const, exitCode: null, durationMs: 0, summary: `Skipped in ${mode} mode` };
  const result = spawnSync(item.command, { shell: true, encoding: "utf8", timeout: item.timeoutSeconds * 1000, env: process.env });
  const output = `${result.stdout ?? ""}\n${result.stderr ?? ""}`.trim();
  const timedOut = result.error && (result.error as NodeJS.ErrnoException).code === "ETIMEDOUT";
  const state = result.status === 0 ? "passed" as const : "failed" as const;
  return { expectationId: item.id, state, exitCode: result.status, durationMs: Date.now() - started, summary: timedOut ? `Timed out after ${item.timeoutSeconds}s` : output.slice(-4000) || (state === "passed" ? "Passed" : "Failed without output") };
}

const startedAt = new Date().toISOString();
const results = expectations.map((item) => {
  process.stdout.write(`\n[verify] ${item.id}: ${item.description}\n`);
  const result = run(item);
  process.stdout.write(`[verify] ${item.id}: ${result.state} (${result.durationMs}ms)\n`);
  if (result.state === "failed") process.stdout.write(`${result.summary}\n`);
  return result;
});

const totals = {
  passed: results.filter(r => r.state === "passed").length,
  failed: results.filter(r => r.state === "failed").length,
  skipped: results.filter(r => r.state === "skipped").length,
  blocked: results.filter(r => r.state === "blocked").length,
};
const failedIds = new Set(results.filter(r => r.state === "failed").map(r => r.expectationId));
const mergeReady = expectations.filter(e => e.requiredForMerge).every(e => !failedIds.has(e.id) && results.find(r => r.expectationId === e.id)?.state === "passed");
const productionReady = expectations.filter(e => e.requiredForProduction).every(e => results.find(r => r.expectationId === e.id)?.state === "passed");
const report: UniversalVerificationReport = { schema: "dreamco.universal_verification_report.v1", startedAt, completedAt: new Date().toISOString(), mode, results, totals, mergeReady, productionReady };

const outDir = resolve("tmp", "dreamco-verification");
mkdirSync(outDir, { recursive: true });
writeFileSync(resolve(outDir, "latest.json"), JSON.stringify(report, null, 2));
const runPassed = isVerificationRunSuccessful({ mode, ...totals, mergeReady, productionReady });
console.log(`\nVerification summary: ${JSON.stringify({ mode, ...totals, mergeReady, productionReady, runPassed })}`);
process.exit(runPassed ? 0 : 1);
