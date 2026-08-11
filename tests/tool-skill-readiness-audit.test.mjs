import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import test from "node:test";

const AUDIT = "automation-tools/agents/tool-skill-readiness-audit.cjs";
const JSON_REPORT = "reports/tool-skill-readiness-report.json";

test("tool skill readiness audit validates the governed catalog", () => {
  assert.ok(fs.existsSync(AUDIT), `${AUDIT} must exist on the integrated repository revision`);
  const run = spawnSync(process.execPath, [AUDIT, "--strict"], {
    encoding: "utf8",
    env: process.env,
  });
  assert.equal(run.status, 0, `${run.stdout}\n${run.stderr}`);
  assert.match(run.stdout, /readiness audit complete/i);
  assert.ok(fs.existsSync(JSON_REPORT), "audit must emit machine-readable evidence");

  const report = JSON.parse(fs.readFileSync(JSON_REPORT, "utf8"));
  assert.equal(report.strict, true);
  assert.equal(report.failed, 0);
  assert.ok(report.passed > 0);
  assert.ok(Array.isArray(report.topLevelChecks));
  assert.ok(report.topLevelChecks.every((check) => check.ok === true));
});

test("tool skill readiness audit includes approval guards for risky actions", () => {
  const catalog = JSON.parse(fs.readFileSync("config/buddy_tool_skill_catalog.json", "utf8"));
  const approvals = new Set(catalog?.evidencePolicy?.approvalRequiredFor || []);
  for (const action of [
    "posting_to_social_media",
    "contacting_customers",
    "spending_money",
    "moving_money",
    "installing_dependencies",
    "publishing_code",
    "training_external_model_with_private_data",
  ]) {
    assert.ok(approvals.has(action), `missing approval boundary: ${action}`);
  }
});
