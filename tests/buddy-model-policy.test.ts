import assert from "node:assert/strict";
import test from "node:test";

import { resolveBuddyModelPlan } from "../server/buddy-model-policy";

test("Buddy defaults to a no-charge native model route", () => {
  const plan = resolveBuddyModelPlan({}, {});
  assert.equal(plan.mode, "free");
  assert.equal(plan.connector.id, "buddy_native");
  assert.equal(plan.status, "free_route_ready");
  assert.equal(plan.automaticPaidUpgrade, false);
  assert.equal(plan.providerCallExecuted, false);
});

test("premium mode pauses until this request is approved", () => {
  const plan = resolveBuddyModelPlan({
    modelMode: "premium",
    modelConnectorId: "openai",
    approvePaidModelForThisRequest: false,
  }, { OPENAI_API_KEY: "configured-for-test" });
  assert.equal(plan.status, "paid_approval_required");
  assert.equal(plan.paidUseApprovedForThisRequest, false);
  assert.equal(plan.providerCallExecuted, false);
});

test("approved premium mode still requires a configured provider adapter", () => {
  const plan = resolveBuddyModelPlan({
    modelMode: "premium",
    modelConnectorId: "google_gemini",
    selectedModelId: "owner-selected-model",
    approvePaidModelForThisRequest: true,
  }, {});
  assert.equal(plan.status, "configuration_required");
  assert.equal(plan.connector.configured, false);
  assert.equal(plan.selectedModelId, "owner-selected-model");
  assert.equal(plan.providerCallExecuted, false);
});
