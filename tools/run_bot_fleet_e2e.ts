import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

import { FleetRuntimeRegistry } from "../server/fleet-runtime";

const markdownPath = resolve(process.cwd(), "reports", "BOT_FLEET_E2E.md");
const webJsonPath = resolve(process.cwd(), "website", "data", "bot-fleet-e2e.json");
const webShardDir = resolve(process.cwd(), "website", "data", "bot-capability-tests");
const checkOnly = process.argv.includes("--check");

const report = FleetRuntimeRegistry.fromFile().certifyAllEndToEnd();
const webIndex = {
  schema: report.schema,
  capabilityTestContract: report.capabilityTestContract,
  summary: report.summary,
  divisions: report.divisions,
  profiles: report.profiles.map((profile) => ({
    slug: profile.slug,
    division: profile.division,
    status: profile.status,
    declaredCapabilityCount: profile.declaredCapabilityCount,
    capabilityTestsPassed: profile.capabilityTests.filter((test) => test.status === "sandbox_contract_passed").length,
    capabilityTestsFailed: profile.capabilityTests.filter((test) => test.status === "failed").length,
    capabilityTestsRef: `bot-capability-tests/${profile.division}.json#${profile.slug}`,
  })),
};
const json = `${JSON.stringify(webIndex, null, 2)}\n`;
const divisionShards = report.divisions.map((division) => {
  const profiles = report.profiles.filter((profile) => profile.division === division.division);
  return {
    path: join(webShardDir, `${division.division}.json`),
    content: `${JSON.stringify({
      schema: "dreamco.bot_capability_test_division.v1",
      division: division.division,
      capabilityTestContract: report.capabilityTestContract,
      summary: division,
      profiles,
    }, null, 2)}\n`,
  };
});
const markdown = `# Buddy Bot Fleet End-to-End Certification

This report executes every registered bot through the repository-controlled Buddy flow. It verifies profile and route integrity, declared capabilities, runtime tools, a bot-specific sandbox task packet, required sandbox evidence, and the one-action live approval stop.

## Result

| Gate | Result |
|---|---:|
| Profiles tested | ${report.summary.profilesTested.toLocaleString("en-US")} |
| Sandbox certified | ${report.summary.sandboxCertified.toLocaleString("en-US")} |
| Failed | ${report.summary.failed.toLocaleString("en-US")} |
| Divisions tested | ${report.summary.divisionsTested} |
| Declared capabilities tested | ${report.summary.declaredCapabilitiesTested.toLocaleString("en-US")} |
| Capability contracts passed | ${report.summary.sandboxCapabilityTestsPassed.toLocaleString("en-US")} |
| Capability contracts failed | ${report.summary.sandboxCapabilityTestsFailed.toLocaleString("en-US")} |
| Every declared capability tested | ${report.summary.allDeclaredCapabilitiesTested ? "Yes" : "No"} |
| Repository-controlled flow complete | ${report.summary.repositoryControlledFlowComplete ? "Yes" : "No"} |
| Live external flow complete | ${report.summary.liveExternalFlowComplete ? "Yes" : "No"} |

## Deployment Boundary

Live external provider calls are not simulated as successful. They require ${report.summary.liveExternalBoundary}. Fleet totals are recorded in \`website/data/bot-fleet-e2e.json\`; per-capability evidence is sharded by division under \`website/data/bot-capability-tests/\`.

## Divisions

| Division | Profiles | Passed | Failed | Capability tests | Capability passed | Capability failed |
|---|---:|---:|---:|---:|---:|---:|
${report.divisions.map((division) => `| ${division.division} | ${division.profiles} | ${division.passed} | ${division.failed} | ${division.capabilityTests} | ${division.capabilityTestsPassed} | ${division.capabilityTestsFailed} |`).join("\n")}
`;

function verify(path: string, expected: string) {
  if (!existsSync(path)) throw new Error(`Missing generated report: ${path}`);
  if (readFileSync(path, "utf8") !== expected) throw new Error(`Generated report is stale: ${path}`);
}

if (checkOnly) {
  verify(markdownPath, markdown);
  verify(webJsonPath, json);
  divisionShards.forEach((shard) => verify(shard.path, shard.content));
} else {
  mkdirSync(webShardDir, { recursive: true });
  writeFileSync(markdownPath, markdown);
  writeFileSync(webJsonPath, json);
  divisionShards.forEach((shard) => writeFileSync(shard.path, shard.content));
}

if (
  !report.summary.repositoryControlledFlowComplete ||
  !report.summary.allDeclaredCapabilitiesTested ||
  report.summary.failed > 0 ||
  report.summary.sandboxCapabilityTestsFailed > 0
) {
  process.exitCode = 1;
}

console.log(JSON.stringify({ ok: report.summary.failed === 0, ...report.summary }, null, 2));
