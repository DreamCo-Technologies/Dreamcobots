import assert from "node:assert/strict";
import test from "node:test";

import { DEMAND_CATALOG_IDS, DEMAND_REASONS } from "../shared/ai-demand-ontology";
import { getDemandOntology, matchDemandReasonToModels } from "../server/demand-model-policy";
import { getBuddyModelAllowlist } from "../server/buddy-model-policy";

test("demand ontology contains three complete 100-reason catalogs", () => {
  const ontology = getDemandOntology();
  assert.equal(ontology.summary.catalogs, 3);
  assert.equal(ontology.summary.reasons, 300);
  for (const catalogId of DEMAND_CATALOG_IDS) {
    assert.equal(DEMAND_REASONS.filter((reason) => reason.catalogId === catalogId).length, 100);
  }
  assert.ok(DEMAND_REASONS.every((reason) => reason.taskCategory && reason.capabilities.length >= 3));
});

test("for the owner, each demand reason produces 20 provider-diverse discovery choices without a provider call", () => {
  for (const reasonId of ["ai_usage-014", "downloaded_apps-027", "online_purchases-084"]) {
    const result = matchDemandReasonToModels({ reasonId, preferredTier: "any" }, {}, { role: "owner" });
    assert.equal(result.optionCount, 20);
    assert.equal(result.modelOptions.length, 20);
    assert.equal(new Set(result.modelOptions.map((option) => option.provider)).size, 20);
    assert.equal(result.selectedModelTargetId, null);
    assert.equal(result.userChoiceRequired, true);
    assert.equal(result.providerCallExecuted, false);
    assert.equal(result.paymentAuthorized, false);
  }
});

test("for a normal caller, demand matching returns only allowlisted model options", () => {
  const allowlisted = new Set(getBuddyModelAllowlist().entries.map((entry) => entry.targetId));
  for (const reasonId of ["ai_usage-014", "downloaded_apps-027", "online_purchases-084"]) {
    const result = matchDemandReasonToModels({ reasonId, preferredTier: "any" }, {});
    assert.ok(result.optionCount >= 1);
    assert.ok(result.modelOptions.every((option) => allowlisted.has(option.targetId) && !option.discoveryTarget));
    assert.equal(result.access.allowlistOnly, true);
    assert.equal(result.providerCallExecuted, false);
    assert.equal(result.paymentAuthorized, false);
  }
});
