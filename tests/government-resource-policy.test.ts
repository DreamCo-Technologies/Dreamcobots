import assert from "node:assert/strict";
import test from "node:test";

import {
  createGovernmentResourcePlan,
  governmentResourcePlanRequestSchema,
} from "../server/government-resource-policy";

test("government plans use official sources and never submit", () => {
  const parsed = governmentResourcePlanRequestSchema.parse({
    query: "Find relevant federal construction opportunities",
    category: "contracts",
    jurisdiction: "US federal",
    profileFacts: ["Small construction company"],
    ownerApproval: true,
  });
  const plan = createGovernmentResourcePlan(parsed);
  assert.equal(plan.coverage, "verified_source_registry");
  assert.equal(plan.liveApplicationSubmitted, false);
  assert.equal(plan.guardrails.automaticSubmission, false);
  assert.ok(plan.resources.every((resource) => new URL(resource.url).hostname.endsWith(".gov") || new URL(resource.url).hostname === "sam.gov"));
});

test("unverified jurisdictions are marked for source verification", () => {
  const parsed = governmentResourcePlanRequestSchema.parse({
    query: "Find a local business permit",
    category: "business",
    jurisdiction: "A city not yet cataloged",
    ownerApproval: true,
  });
  const plan = createGovernmentResourcePlan(parsed);
  assert.equal(plan.coverage, "official_source_verification_required");
});
