import assert from "node:assert/strict";
import test from "node:test";

import { MODEL_BENCHMARK_TARGETS } from "../shared/model-benchmark-targets";
import { MODEL_PROVIDER_SOURCE_PROFILES } from "../shared/model-provider-sources";
import { getModelSourceConnectionAudit } from "../server/model-source-connection-policy";

test("all 500 targets resolve to one of 100 governed provider source profiles", () => {
  const audit = getModelSourceConnectionAudit({});
  assert.equal(MODEL_BENCHMARK_TARGETS.length, 500);
  assert.equal(MODEL_PROVIDER_SOURCE_PROFILES.length, 100);
  assert.equal(audit.summary.targets, 500);
  assert.equal(audit.summary.providerProfiles, 100);
  assert.equal(audit.summary.sourceLinkedTargets, 500);
  assert.equal(audit.summary.setupPathTargets, 500);
  assert.ok(audit.targets.every((target) => target.officialSource && target.setupPath));
  assert.equal(audit.summary.liveVerifiedTargets, 0);
});

test("configured references change readiness without exposing credentials or claiming a live connection", () => {
  const audit = getModelSourceConnectionAudit({ OPENAI_API_KEY: "test-only-value" });
  const openai = audit.providerConnections.find((provider) => provider.provider === "OpenAI");
  assert.equal(openai?.credentialReferenceConfigured, true);
  assert.equal(openai?.status, "exact_model_probe_required");
  assert.equal(openai?.liveProbePassed, false);
  const serialized = JSON.stringify(audit);
  assert.equal(serialized.includes("test-only-value"), false);
  assert.equal(audit.truthContract.credentialConfiguredMeansModelVerified, false);
});

test("every named source connector has a router contract", () => {
  const audit = getModelSourceConnectionAudit({});
  const missing = audit.providerConnections.filter((provider) => provider.connectorId && !provider.connectorContractPresent);
  assert.deepEqual(missing, []);
});
