import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import { RESOURCE_TYPES } from "../shared/bot-category-resource-pack-contract.js";

const ROOT = resolve(process.cwd());
const PROGRAM = JSON.parse(readFileSync(resolve(ROOT, "config/buddy-resource-connection-sandbox-program.json"), "utf8"));

const requiredSources = [
  "config/buddy-government-resources.json",
  "config/buddy-master-scout-opportunity-resource-library-program.json",
  "config/buddy-trusted-life-network-resource-marketplace-program.json",
  "config/mastery-data-pack-marketplace-program.json",
  "config/buddy-connector-registry.json",
  "website/data/buddy-connection-catalog.json",
  "shared/bot-category-resource-pack-contract.ts",
];

test("resource sandbox covers every canonical resource type", () => {
  assert.deepEqual([...PROGRAM.resource_types].sort(), [...RESOURCE_TYPES].sort());
});

test("every canonical resource type has category-specific sandbox checks", () => {
  for (const type of RESOURCE_TYPES) {
    assert.ok(Array.isArray(PROGRAM.category_overrides[type]), `missing sandbox override for ${type}`);
    assert.ok(PROGRAM.category_overrides[type].length >= 2, `sandbox coverage too small for ${type}`);
  }
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
});

test("sensitive resource categories keep explicit approval and truth boundaries", () => {
  const joined = JSON.stringify(PROGRAM.category_overrides).toLowerCase();
  for (const phrase of [
    "no guaranteed funding",
    "no guaranteed award",
    "no guaranteed approval",
    "money-action approval",
    "no bulk personal harvesting",
    "no private-person dossiering",
  ]) {
    assert.ok(joined.includes(phrase), `missing sensitive-category boundary: ${phrase}`);
  }
});
