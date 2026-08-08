import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { RESOURCE_TYPES } from "../shared/bot-category-resource-pack-contract.js";

const ROOT = resolve(process.cwd());
const PROGRAM = JSON.parse(readFileSync(resolve(ROOT, "config/buddy-resource-connection-sandbox-program.json"), "utf8"));
const ARSENAL = JSON.parse(readFileSync(resolve(ROOT, "config/resource-sandbox-test-arsenal.json"), "utf8"));

const requiredSources = [
  "config/buddy-government-resources.json",
  "config/buddy-master-scout-opportunity-resource-library-program.json",
  "config/buddy-trusted-life-network-resource-marketplace-program.json",
  "config/mastery-data-pack-marketplace-program.json",
  "config/buddy-connector-registry.json",
  "config/resource-sandbox-test-arsenal.json",
  "website/data/buddy-connection-catalog.json",
  "shared/bot-category-resource-pack-contract.ts",
];

const sharedArsenalCount = Object.values(ARSENAL.shared_test_families as Record<string, string[]>).reduce(
  (sum, tests) => sum + tests.length,
  0,
);
const categoryArsenalCount = Object.values(ARSENAL.category_scenarios as Record<string, string[]>).reduce(
  (sum, tests) => sum + tests.length,
  0,
);
const expandedMatrixCount = sharedArsenalCount * RESOURCE_TYPES.length + categoryArsenalCount;

test("resource sandbox covers every canonical resource type", () => {
  assert.deepEqual([...PROGRAM.resource_types].sort(), [...RESOURCE_TYPES].sort());
  assert.deepEqual(Object.keys(ARSENAL.category_scenarios).sort(), [...RESOURCE_TYPES].sort());
});

test("every canonical resource type has baseline and deep category-specific sandbox checks", () => {
  for (const type of RESOURCE_TYPES) {
    assert.ok(Array.isArray(PROGRAM.category_overrides[type]), `missing sandbox override for ${type}`);
    assert.ok(PROGRAM.category_overrides[type].length >= 2, `baseline sandbox coverage too small for ${type}`);
    assert.ok(Array.isArray(ARSENAL.category_scenarios[type]), `missing deep sandbox scenarios for ${type}`);
    assert.ok(ARSENAL.category_scenarios[type].length >= 8, `deep sandbox coverage too small for ${type}`);
  }
});

test("resource sandbox maintains a large shared stress-test library", () => {
  assert.ok(Object.keys(ARSENAL.shared_test_families).length >= 15, "too few shared test families");
  assert.ok(sharedArsenalCount >= 200, `shared sandbox arsenal shrank to ${sharedArsenalCount} tests`);
  assert.ok(categoryArsenalCount >= 200, `category sandbox arsenal shrank to ${categoryArsenalCount} tests`);
  assert.ok(sharedArsenalCount + categoryArsenalCount >= 400, "raw resource sandbox arsenal must remain at least 400 planned checks");
  assert.ok(expandedMatrixCount >= 6000, `expanded resource sandbox matrix shrank to ${expandedMatrixCount} test instances`);
});

test("shared sandbox template covers core connection safety", () => {
  const checks = new Set(PROGRAM.sandbox_test_template);
  for (const required of [
    "catalog discovery",
    "source/provenance presence",
    "permission boundary",
    "read-only or mock first",
    "outbound-contact approval gate",
    "privacy/minimum-data check",
    "cost/spend gate",
    "failure-state visibility",
    "audit/evidence record",
  ]) {
    assert.ok(checks.has(required), `missing shared resource check: ${required}`);
  }
});

test("deep arsenal includes security, privacy, money, resilience, data quality and UX families", () => {
  for (const family of [
    "source_and_provenance",
    "freshness",
    "permissions_and_access",
    "credentials_and_secrets",
    "network_and_resilience",
    "schema_and_data_quality",
    "privacy",
    "security",
    "contact_and_outreach",
    "cost_and_money",
    "eligibility_and_requirements",
    "search_and_matching",
    "comparison",
    "audit_and_observability",
    "failure_and_recovery",
    "user_experience",
    "sandbox_boundaries",
  ]) {
    assert.ok(Array.isArray(ARSENAL.shared_test_families[family]), `missing test family: ${family}`);
  }
});

test("Buddy resource sources exist in the repository", () => {
  for (const path of requiredSources) {
    assert.ok(existsSync(resolve(ROOT, path)), `missing resource source: ${path}`);
  }
});

test("program separates catalog availability from live connectivity", () => {
  assert.equal(PROGRAM.connection_policy.buddy_is_front_door, true);
  assert.equal(PROGRAM.connection_policy.catalog_entries_are_not_live_connections, true);
  assert.ok(PROGRAM.connection_policy.live_connection_requires.includes("sandbox verification"));
  assert.ok(PROGRAM.connection_policy.live_connection_requires.includes("runtime evidence"));
  assert.equal(PROGRAM.connection_policy.write_actions, "approval_gated");
  assert.equal(ARSENAL.execution_policy.live_verified_requires_runtime_evidence, true);
});

test("sensitive resource categories keep explicit approval and truth boundaries", () => {
  const joined = `${JSON.stringify(PROGRAM.category_overrides)} ${JSON.stringify(ARSENAL.category_scenarios)}`.toLowerCase();
  for (const phrase of [
    "no guaranteed funding",
    "no guaranteed award",
    "no guaranteed approval",
    "money-action approval",
    "bulk personal harvesting",
    "private-person dossier",
    "submission blocked",
    "application blocked",
    "transaction blocked",
  ]) {
    assert.ok(joined.includes(phrase), `missing sensitive-category boundary: ${phrase}`);
  }
});

test("sandbox arsenal keeps production side effects disabled by default", () => {
  const boundaries = new Set(ARSENAL.shared_test_families.sandbox_boundaries);
  for (const required of [
    "no production write",
    "no real application submission",
    "no real purchase",
    "no real transfer",
    "no live outreach",
    "test credentials only",
  ]) {
    assert.ok(boundaries.has(required), `missing sandbox boundary: ${required}`);
  }
});
