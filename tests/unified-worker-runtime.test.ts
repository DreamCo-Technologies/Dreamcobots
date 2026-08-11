import assert from "node:assert/strict";
import test from "node:test";

import { getUnifiedWorkerRuntime } from "../server/unified-worker-runtime";

test("unified worker runtime preserves the 1,051 canonical baseline", () => {
  const runtime = getUnifiedWorkerRuntime();
  const summary = runtime.summary();
  assert.equal(summary.canonicalBaselinePreserved, true);
  assert.equal(summary.canonical.instances, 1051);
  assert.equal(summary.executionMode, "sandbox");
  assert.equal(summary.liveExternalActionsRequireApproval, true);
});

test("unified worker runtime resolves canonical DreamBot", () => {
  const runtime = getUnifiedWorkerRuntime();
  const resolved = runtime.get("dreambot");
  assert.ok(resolved);
  assert.equal(resolved?.source, "canonical");
});
