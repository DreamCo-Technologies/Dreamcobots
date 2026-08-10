import test from "node:test";
import assert from "node:assert/strict";

import { buildSubBotTeam, loadSubBotRegistry } from "../server/subbot-team-engine";
import { getUnifiedWorkerRuntime } from "../server/unified-worker-runtime";

test("must-have registry contains at least 30 unique blueprints", () => {
  const registry = loadSubBotRegistry();
  assert.ok(registry.bots.length >= 30);
  const slugs = registry.bots.map((bot) => bot.slug);
  assert.equal(new Set(slugs).size, slugs.length);
});

test("sub-bot teams are task-scoped and never take live actions", () => {
  const plan = buildSubBotTeam({
    ownerBotSlug: "dreambot",
    objective: "Organize my authorized project files and create a searchable project knowledge base.",
    requestedRoles: ["personal-data-importer", "knowledge-indexer"],
    maximumTeamSize: 5,
    dataClasses: ["documents", "images", "notes"],
    liveActionRequested: true,
  });
  assert.equal(plan.externalActionTaken, false);
  assert.equal(plan.liveActionStatus, "approval_required");
  assert.ok(plan.members.some((member) => member.slug === "personal-data-importer"));
  assert.ok(plan.members.some((member) => member.slug === "knowledge-indexer"));
  assert.equal(plan.dataPolicy.readOnlyFirst, true);
  assert.equal(plan.dataPolicy.exportAndDeleteControlsRequired, true);
});

test("every routable canonical worker can own a sub-bot plan", () => {
  const runtime = getUnifiedWorkerRuntime();
  const summary = runtime.summary();
  assert.equal(summary.subBotTeams.enabledForEveryRoutableWorker, true);
  const plan = runtime.planSubBotTeam({
    ownerBotSlug: "dreambot",
    objective: "Inspect a failing software project and assemble the smallest safe engineering team to diagnose it.",
    requestedRoles: ["actions-doctor", "debug-detective-plus"],
    maximumTeamSize: 4,
    dataClasses: [],
    liveActionRequested: false,
  });
  assert.equal(plan.ownerBotSlug, "dreambot");
  assert.ok(plan.members.length >= 2);
});
