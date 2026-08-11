import assert from "node:assert/strict";
import test from "node:test";

import { executePublicBuddyRequest } from "../server/public-buddy-execution";

test("external actions are prepared for approval and never falsely executed", async () => {
  const result = await executePublicBuddyRequest({
    objective: "Send this sales email to my customer and publish the announcement.",
    mode: "Build",
    approvePaidModelForThisRequest: true,
  });
  assert.equal(result.executed, false);
  assert.equal(result.status, "prepared_for_approval");
  assert.equal(result.receipt.state, "prepared_for_approval");
});

test("unapproved model work cannot claim execution", async () => {
  const result = await executePublicBuddyRequest({
    objective: "Build a TypeScript utility that validates email addresses and include tests.",
    mode: "Build",
    approvePaidModelForThisRequest: false,
  });
  assert.equal(result.executed, false);
  assert.ok(["model_approval_required", "backend_model_not_configured"].includes(result.status));
  assert.equal(result.receipt.state, "prepared_for_execution");
  assert.equal(result.compilation.qualityPolicy, "best_verified_task_fit_first");
});
