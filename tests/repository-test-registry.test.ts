import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import {
  createRepositoryTestPlan,
  type RepositoryTestRegistry,
} from "../server/repository-test-policy";

const registry = JSON.parse(
  readFileSync(new URL("../config/generated/repository_test_registry.json", import.meta.url), "utf8"),
) as RepositoryTestRegistry & {
  routes: Array<{ path: string; suite_id: string }>;
  files: Array<{ path: string; suite_id: string }>;
};

test("repository registry covers files, routes, pages, and test suites", () => {
  assert.equal(registry.schema, "dreamco.repository_test_registry.v1");
  assert.ok(registry.summary.files_scanned > 700);
  assert.ok(registry.summary.literal_api_routes > 100);
  assert.ok(registry.summary.web_pages > 30);
  assert.ok(registry.summary.test_files > 20);
  assert.ok(registry.summary.test_suites >= 25);
  assert.equal(registry.summary.blocked_suites, 0);
  assert.equal(registry.safety_contract.browser_executes_repository_commands, false);
  assert.equal(registry.safety_contract.external_writes, "forbidden");
  const suiteIds = new Set(registry.suites.map((suite) => suite.id));
  assert.ok(registry.routes.every((route) => suiteIds.has(route.suite_id)));
  assert.ok(registry.files.every((file) => suiteIds.has(file.suite_id)));
});

test("repository test planner accepts only catalog suites and executes nothing", () => {
  const plan = createRepositoryTestPlan({
    suiteIds: ["repository-contracts", "data-rights", "bot-fleet"],
    mode: "sandbox",
    allowNetwork: false,
    exactApprovalForExternalTests: false,
    maxBudgetUsd: 0,
  }, registry);
  assert.equal(plan.testsExecutedByPlanner, false);
  assert.equal(plan.externalActionTaken, false);
  assert.equal(plan.arbitraryCommandsAccepted, false);
  assert.ok(plan.suites.every((suite) => suite.browserExecutionAllowed === false));
  assert.throws(() => createRepositoryTestPlan({
    suiteIds: ["run-any-command"],
    mode: "contract",
    allowNetwork: false,
    exactApprovalForExternalTests: false,
    maxBudgetUsd: 0,
  }, registry), /Unknown repository test suite/);
});

test("credential and adapter suites stay held without network and exact approval", () => {
  const held = createRepositoryTestPlan({
    suiteIds: ["github", "payments", "connections"],
    mode: "adapter",
    allowNetwork: false,
    exactApprovalForExternalTests: false,
    maxBudgetUsd: 0,
  }, registry);
  assert.ok(held.suites.every((suite) => suite.readiness === "held_network_and_exact_approval_required"));
  const approvedPlan = createRepositoryTestPlan({
    suiteIds: ["github"],
    mode: "adapter",
    allowNetwork: true,
    exactApprovalForExternalTests: true,
    maxBudgetUsd: 0,
  }, registry);
  assert.equal(approvedPlan.suites[0].readiness, "adapter_credentials_and_runner_verification_required");
  assert.equal(approvedPlan.testsExecutedByPlanner, false);
});
