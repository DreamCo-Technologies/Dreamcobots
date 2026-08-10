import assert from "node:assert/strict";
import test from "node:test";

import { compileIntelligentTask } from "../server/intelligent-task-router";

test("router activates only a small task-scoped subset of the fleet", () => {
  const result = compileIntelligentTask({
    objective: "Debug a TypeScript API bug, patch only the affected files, then run tests.",
    requiredCapabilities: ["debugging", "coding", "testing"],
    writeScopes: ["server/api.ts"],
  });
  assert.equal(result.activation.lazy, true);
  assert.equal(result.activation.allUnusedBotsRemainInactive, true);
  assert.ok(result.activation.activeBotCount < result.activation.totalFleetBotCount);
  assert.ok(result.activation.fleetActivationRatio < 0.02);
});

test("quality-first model selection is embedded into the compiled task graph", () => {
  const result = compileIntelligentTask({
    objective: "Research current evidence on the web and analyze an image before writing a report.",
    requiredTools: ["web_search"],
    requiredModalities: ["image"],
    allowPaid: true,
  });
  assert.equal(result.qualityPolicy, "best_verified_task_fit_first");
  assert.ok(result.modelRoute.selected);
  assert.equal(result.modelRoute.truthContract.qualityDominatesCostAndLatencyByDefault, true);
});

test("router never compiles more than 32 parallel lanes", () => {
  const result = compileIntelligentTask({
    objective: "Research, build, test and deploy a service with careful verification.",
    maximumParallelLanes: 32,
  });
  assert.equal(result.graph.maximumParallelLanes, 32);
  assert.equal(result.graph.maximumParallelWritersPerOwner, 1);
});

test("write conflicts are serialized by owner scope", () => {
  const result = compileIntelligentTask({
    objective: "Build and test a code change in the server runtime.",
    writeScopes: ["server"],
  });
  const writers = result.graph.stages.filter((stage) => stage.write);
  assert.ok(writers.length >= 1);
  assert.ok(writers.every((stage) => stage.writerOwner === "server"));
  assert.equal(result.graph.conflictingWritesSerialized, true);
});

test("open-weight requirement keeps the model route open-weight only", () => {
  const result = compileIntelligentTask({
    objective: "Run private local reasoning and coding on owner hardware.",
    requireOpenWeight: true,
    preferLocal: true,
  });
  assert.ok(result.modelRoute.selected);
  assert.ok(["open_weight", "open_weight_base", "weights_available"].includes(result.modelRoute.selected!.weightAccess));
});
