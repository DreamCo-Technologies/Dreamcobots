import assert from "node:assert/strict";
import test from "node:test";

import {
  createResourceOnboardingPlan,
  getResourceOnboardingCatalog,
} from "../server/model-source-connection-policy";

test("the 500 resource targets collapse into one governed setup per provider", () => {
  const catalog = getResourceOnboardingCatalog({});
  assert.equal(catalog.summary.resourceTargets, 500);
  assert.equal(catalog.summary.uniqueProviders, 100);
  assert.equal(
    catalog.summary.providerAccountMaximum + catalog.summary.noAccountProviderSetups,
    100,
  );
  assert.equal(catalog.providers.reduce((total, provider) => total + provider.targetCount, 0), 500);
  assert.equal(catalog.summary.automaticAccountSubmissions, 0);
  assert.equal(catalog.summary.liveVerifiedProviders, 0);
  assert.ok(catalog.providers.every((provider) => provider.officialSource && provider.setupPath));
  assert.ok(catalog.providers.every((provider) => provider.efficiencyGuidance.length >= 3));
  assert.ok(catalog.providers.every((provider) => provider.automaticSubmission === false));
  assert.equal(catalog.truthContract.fiveHundredTargetsMeanFiveHundredAccounts, false);
});

test("the all-provider queue prepares batches without creating accounts or spending", () => {
  const plan = createResourceOnboardingPlan({
    objective: "Prepare all Buddy model resources for efficient task routing",
    accessMode: "free_first",
    queueMode: "prepare_provider_queue",
    batchSize: 3,
  }, {});
  assert.equal(plan.summary.resourceTargetsCovered, 500);
  assert.equal(plan.summary.uniqueProvidersQueued, 100);
  assert.equal(plan.summary.accountsCreated, 0);
  assert.equal(plan.summary.formsSubmitted, 0);
  assert.equal(plan.summary.paymentsMade, 0);
  assert.ok(plan.batches.every((batch) => batch.providers.length <= 3));
  assert.ok(plan.batches.every((batch) => batch.maximumConcurrentUserHandoffs === 1));
  assert.equal(plan.boundaries.automaticTermsAcceptance, false);
  assert.equal(plan.boundaries.automaticCaptchaOrIdentityCompletion, false);
  assert.equal(plan.boundaries.exactApprovalRequiredForEveryExternalWriteOrPurchase, true);
});

test("paid options can be cataloged without approving a paid account or provider call", () => {
  const plan = createResourceOnboardingPlan({
    objective: "Show every available setup route",
    providers: ["OpenAI", "DreamCo", "Midjourney"],
    accessMode: "include_paid_options",
    queueMode: "guided_one_at_a_time",
    batchSize: 2,
  }, {});
  assert.equal(plan.summary.uniqueProvidersQueued, 3);
  assert.equal(plan.summary.heldForPaidReview, 0);
  assert.ok(plan.batches.flatMap((batch) => batch.providers).every((provider) => provider.paidUseApproved === false));
});
