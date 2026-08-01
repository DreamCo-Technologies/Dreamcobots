import assert from "node:assert/strict";
import test from "node:test";

import {
  createAppConnectionPlan,
  createAppGroupWorkflowPlan,
  createFinanceWorkspacePlan,
  createSocialWorkspacePlan,
} from "../server/connected-life-policy";

test("app connections keep credentials out and isolate high-impact actions", () => {
  const plan = createAppConnectionPlan({
    appName: "Owner Social Account",
    officialUrl: "https://social.example/settings/apps",
    category: "social",
    groupName: "Audience",
    authMethod: "oauth_pkce",
    accessLevel: "approved_actions",
    requestedActions: ["read", "draft", "publish"],
    requestedDataCategories: ["posts", "analytics"],
    retentionDays: 30,
    ownerAuthorized: true,
  });
  assert.equal(plan.connection.rawCredentialsAccepted, false);
  assert.deepEqual(plan.highImpactActions, ["publish"]);
  assert.equal(plan.connection.connected, false);
});

test("catalog-only apps cannot silently request action access", () => {
  assert.throws(() => createAppConnectionPlan({
    appName: "Catalog Item",
    officialUrl: "https://example.com/app",
    category: "custom",
    groupName: "Reference",
    authMethod: "browser_handoff",
    accessLevel: "catalog_only",
    requestedActions: ["read"],
    requestedDataCategories: [],
    retentionDays: 7,
    ownerAuthorized: true,
  }), /Catalog-only/);
});

test("grouped app workflows require a sandbox and preserve per-action approval", () => {
  const plan = createAppGroupWorkflowPlan({
    groupName: "Creator Launch",
    objective: "Coordinate approved drafts and analytics across the owner's selected creator apps.",
    appPlanIds: ["app-plan-one", "app-plan-two"],
    actions: ["read", "compare", "draft", "publish"],
    ownerApprovedSandbox: true,
  });
  assert.equal(plan.status, "sandbox_plan_ready");
  assert.deepEqual(plan.highImpactActions, ["publish"]);
  assert.equal(plan.controls.liveActionsTaken, false);
});

test("social live shows require moderation and never start from a plan", () => {
  assert.throws(() => createSocialWorkspacePlan({
    platform: "Owner Channel",
    accountReference: "social-account:owner-channel",
    objective: "Host a live product workshop with approved media and audience questions.",
    mode: "live_show",
    contentTypes: ["livestream", "video"],
    syntheticMedia: true,
    mediaRightsConfirmed: true,
    adultSubjectConsentConfirmed: true,
    ownerAuthorizedAccount: true,
    moderationEnabled: false,
  }), /moderation/);

  const plan = createSocialWorkspacePlan({
    platform: "Owner Channel",
    accountReference: "social-account:owner-channel",
    objective: "Host a live product workshop with approved media and audience questions.",
    mode: "live_show",
    contentTypes: ["livestream", "video"],
    syntheticMedia: true,
    mediaRightsConfirmed: true,
    adultSubjectConsentConfirmed: true,
    ownerAuthorizedAccount: true,
    moderationEnabled: true,
  });
  assert.equal(plan.status, "owner_action_approval_required");
  assert.equal(plan.liveExternalActionTaken, false);
  assert.equal(plan.rawCredentialsAccepted, false);
});

test("finance workspace normalizes subscription costs and detects duplicates without moving money", () => {
  const plan = createFinanceWorkspacePlan({
    subscriptions: [
      {
        id: "subscription-one",
        merchant: "Design Suite",
        amount: "12.00",
        currency: "USD",
        cadence: "monthly",
        renewalAt: "2027-01-01T00:00:00.000Z",
        cancellationUrl: "https://example.com/account/cancel",
      },
      {
        id: "subscription-two",
        merchant: "Design Suite",
        amount: "12.00",
        currency: "USD",
        cadence: "monthly",
        renewalAt: "2027-01-02T00:00:00.000Z",
      },
      {
        id: "subscription-three",
        merchant: "Music Tools",
        amount: "120.00",
        currency: "USD",
        cadence: "annual",
        renewalAt: "2027-03-01T00:00:00.000Z",
      },
    ],
    bills: [],
    monthlyBudget: "100.00",
    budgetCurrency: "USD",
  });
  assert.equal(plan.monthlyTotals.USD, 34);
  assert.equal(plan.annualizedTotals.USD, 408);
  assert.deepEqual(plan.possibleDuplicates, [["subscription-one", "subscription-two"]]);
  assert.equal(plan.paymentExecuted, false);
  assert.equal(plan.cancellationSubmitted, false);
});
