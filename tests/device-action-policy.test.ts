import assert from "node:assert/strict";
import test from "node:test";

import {
  createDeviceActionPlan,
  deviceActionPlanRequestSchema,
} from "../server/device-action-policy";

test("device plans are read-only-first and never grant takeover", () => {
  const request = deviceActionPlanRequestSchema.parse({
    objective: "Prepare a customer reply in the connected support app.",
    deviceType: "desktop",
    appName: "Support workspace",
    actionMode: "preview",
    requestedActions: ["Read the selected ticket", "Draft a response"],
    requestedScopes: ["tickets.read", "drafts.write"],
  });
  const plan = createDeviceActionPlan(request);
  assert.equal(plan.status, "sandbox_plan_ready");
  assert.equal(plan.executionPermittedByThisPlanner, false);
  assert.equal(plan.automaticDeviceTakeover, false);
  assert.equal(plan.controls.readOnlyFirst, true);
  assert.equal(plan.controls.pauseAndStopAlwaysAvailable, true);
  assert.equal(plan.liveExternalActionTaken, false);
});

test("execute requests stop at adapter and one-action approval gates", () => {
  const request = deviceActionPlanRequestSchema.parse({
    objective: "Publish the approved update in the connected app.",
    deviceType: "phone",
    appName: "Client social app",
    actionMode: "execute",
    requestedActions: ["Publish one approved update"],
    connectorId: "client-social",
    requestedScopes: ["posts.write"],
    exactApprovalForThisPlan: true,
  });
  const plan = createDeviceActionPlan(request);
  assert.equal(plan.status, "live_adapter_and_action_approval_required");
  assert.equal(plan.exactApprovalRecordedForPlan, true);
  assert.equal(plan.executionPermittedByThisPlanner, false);
  assert.equal(plan.controls.oneActionApproval, true);
});
