import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import { FleetRuntimeRegistry } from "../server/fleet-runtime";

const markdownPath = resolve(process.cwd(), "reports", "BOT_FLEET_E2E.md");
const webJsonPath = resolve(process.cwd(), "website", "data", "bot-fleet-e2e.json");
const checkOnly = process.argv.includes("--check");

const report = FleetRuntimeRegistry.fromFile().certifyAllEndToEnd();
const json = `${JSON.stringify(report, null, 2)}\n`;
const markdown = `# Buddy Bot Fleet End-to-End Certification

This report executes every registered bot through the repository-controlled Buddy flow. It verifies profile and route integrity, declared capabilities, runtime tools, a bot-specific sandbox task packet, required sandbox evidence, and the one-action live approval stop.

## Result

| Gate | Result |
|---|---:|
| Profiles tested | ${report.summary.profilesTested.toLocaleString("en-US")} |
| Sandbox certified | ${report.summary.sandboxCertified.toLocaleString("en-US")} |
| Failed | ${report.summary.failed.toLocaleString("en-US")} |
| Divisions tested | ${report.summary.divisionsTested} |
| Repository-controlled flow complete | ${report.summary.repositoryControlledFlowComplete ? "Yes" : "No"} |
| Live external flow complete | ${report.summary.liveExternalFlowComplete ? "Yes" : "No"} |

## Deployment Boundary

Live external provider calls are not simulated as successful. They require ${report.summary.liveExternalBoundary}. Per-bot evidence is recorded in \`website/data/bot-fleet-e2e.json\`.

## Divisions

| Division | Profiles | Passed | Failed |
|---|---:|---:|---:|
${report.divisions.map((division) => `| ${division.division} | ${division.profiles} | ${division.passed} | ${division.failed} |`).join("\n")}
`;

function verify(path: string, expected: string) {
  if (!existsSync(path)) throw new Error(`Missing generated report: ${path}`);
  if (readFileSync(path, "utf8") !== expected) throw new Error(`Generated report is stale: ${path}`);
}

if (checkOnly) {
  verify(markdownPath, markdown);
  verify(webJsonPath, json);
} else {
  writeFileSync(markdownPath, markdown);
  writeFileSync(webJsonPath, json);
}

if (!report.summary.repositoryControlledFlowComplete || report.summary.failed > 0) {
  process.exitCode = 1;
}

console.log(JSON.stringify({ ok: report.summary.failed === 0, ...report.summary }, null, 2));
