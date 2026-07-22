import assert from "node:assert/strict";
import test from "node:test";

import {
  LeadSuppressionLedger,
  authorizeLeadAction,
  buildGovernedLeadPlan,
  type LeadCampaignRequest,
} from "../server/governed-leads";

const now = new Date("2026-07-22T15:00:00.000Z");

function campaign(overrides: Partial<LeadCampaignRequest> = {}): LeadCampaignRequest {
  return {
    campaignId: "campaign-example-1",
    ownerUserId: "owner-1",
    botSlug: "commercial-scanner",
    objective: "Offer an approved property analysis consultation.",
    audience: "Commercial property owners",
    offer: "a no-pressure property analysis",
    requestedChannels: ["email", "sms"],
    suppressionRefs: [],
    campaignSendsToday: 0,
    maximumDailySends: 20,
    minimumFollowUpHours: 48,
    maximumFollowUps: 2,
    prospects: [{
      leadId: "lead-example-1",
      organizationName: "Example Property Group",
      contactRef: "contact_ref:example_001",
      source: {
        type: "inbound_request",
        reference: "crm:inbound/example-1",
        termsConfirmed: true,
        purchasedOrStolenList: false,
      },
      consent: {
        basis: "inbound_request",
        channels: ["email"],
        obtainedAt: "2026-07-21T14:00:00.000Z",
        expiresAt: "2026-08-21T14:00:00.000Z",
        evidenceRef: "consent:example-1",
      },
      engagement: {
        state: "never_contacted",
        followUpsSent: 0,
        sentToday: 0,
      },
      qualificationSignals: ["Requested a property analysis"],
      sensitiveTargeting: false,
      includesMinor: false,
    }],
    ...overrides,
  };
}

test("keeps public-directory leads research-only without recipient permission", () => {
  const input = campaign();
  input.prospects[0] = {
    ...input.prospects[0],
    source: {
      type: "public_business_directory",
      reference: "directory:example-1",
      termsConfirmed: true,
      purchasedOrStolenList: false,
    },
    consent: { basis: "none", channels: [] },
  };
  const plan = buildGovernedLeadPlan(input, now);
  assert.equal(plan.status, "research_only");
  assert.equal(plan.actions[0].status, "research_only");
  assert.equal(plan.actions[0].draft, null);
  assert.equal(plan.externalActionTaken, false);
});

test("routes only a recipient-permitted channel and requires exact owner approval", () => {
  const plan = buildGovernedLeadPlan(campaign(), now);
  const action = plan.actions[0];
  assert.equal(action.status, "approval_required");
  assert.equal(action.channel, "email");
  assert.match(action.draft ?? "", /you gave permission/i);

  const packet = authorizeLeadAction(plan, {
    approvalRequestId: "approval-example-1",
    actionId: action.actionId,
    campaignId: plan.campaignId,
    leadId: action.leadId,
    ownerUserId: plan.ownerUserId,
    botSlug: plan.botSlug,
    channel: "email",
    stepNumber: 1,
    approvedAt: "2026-07-22T14:55:00.000Z",
    expiresAt: "2026-07-22T15:10:00.000Z",
    oneActionOnly: true,
  }, now);
  assert.equal(packet.status, "ready_for_configured_adapter");
  assert.equal(packet.oneActionOnly, true);
  assert.equal(packet.externalDispatchExecuted, false);
  assert.equal(packet.idempotencyKey, action.actionId);
});

test("rejects mismatched and expired approvals", () => {
  const plan = buildGovernedLeadPlan(campaign(), now);
  const action = plan.actions[0];
  const valid = {
    approvalRequestId: "approval-example-1",
    actionId: action.actionId,
    campaignId: plan.campaignId,
    leadId: action.leadId,
    ownerUserId: plan.ownerUserId,
    botSlug: plan.botSlug,
    channel: "email" as const,
    stepNumber: 1,
    approvedAt: "2026-07-22T14:55:00.000Z",
    expiresAt: "2026-07-22T15:10:00.000Z",
    oneActionOnly: true as const,
  };
  assert.throws(() => authorizeLeadAction(plan, { ...valid, ownerUserId: "owner-2" }, now), /does not match/);
  assert.throws(() => authorizeLeadAction(plan, { ...valid, expiresAt: "2026-07-22T14:59:00.000Z" }, now), /expired/);
});

test("blocks cadence violations, replies, suppression, and completed sequences", () => {
  const base = campaign();
  const lead = base.prospects[0];
  const waiting = buildGovernedLeadPlan(campaign({ prospects: [{
    ...lead,
    engagement: {
      state: "waiting",
      followUpsSent: 1,
      sentToday: 0,
      lastContactAt: "2026-07-22T14:00:00.000Z",
    },
  }] }), now);
  assert.equal(waiting.actions[0].status, "waiting_for_cadence");

  const replied = buildGovernedLeadPlan(campaign({ prospects: [{
    ...lead,
    engagement: {
      state: "replied",
      followUpsSent: 1,
      sentToday: 1,
      lastContactAt: "2026-07-20T14:00:00.000Z",
    },
  }] }), now);
  assert.equal(replied.actions[0].status, "suppressed");

  const suppressed = buildGovernedLeadPlan(campaign({ suppressionRefs: [lead.contactRef] }), now);
  assert.equal(suppressed.actions[0].status, "suppressed");

  const complete = buildGovernedLeadPlan(campaign({ prospects: [{
    ...lead,
    engagement: {
      state: "waiting",
      followUpsSent: 3,
      sentToday: 0,
      lastContactAt: "2026-07-19T14:00:00.000Z",
    },
  }] }), now);
  assert.equal(complete.actions[0].status, "sequence_complete");
});

test("enforces both per-contact and campaign-wide daily caps", () => {
  const base = campaign();
  const contactCapped = buildGovernedLeadPlan(campaign({ prospects: [{
    ...base.prospects[0],
    engagement: { ...base.prospects[0].engagement, sentToday: 1 },
  }] }), now);
  assert.equal(contactCapped.actions[0].status, "daily_limit_reached");
  assert.equal(contactCapped.actions[0].reason, "contact_daily_cap_reached");

  const campaignCapped = buildGovernedLeadPlan(campaign({ campaignSendsToday: 20 }), now);
  assert.equal(campaignCapped.actions[0].status, "daily_limit_reached");
  assert.equal(campaignCapped.actions[0].reason, "campaign_daily_cap_reached");

  const secondLead = {
    ...base.prospects[0],
    leadId: "lead-example-2",
    organizationName: "Second Property Group",
    contactRef: "contact_ref:example_002",
  };
  const oneSlot = buildGovernedLeadPlan(campaign({
    maximumDailySends: 2,
    campaignSendsToday: 1,
    prospects: [base.prospects[0], secondLead],
  }), now);
  assert.equal(oneSlot.actions[0].status, "approval_required");
  assert.equal(oneSlot.actions[1].status, "daily_limit_reached");
  assert.equal(oneSlot.actions[1].reason, "campaign_daily_cap_reached");
});

test("requires explicit opt-in for SMS and voice calls", () => {
  const base = campaign();
  assert.throws(() => buildGovernedLeadPlan(campaign({ prospects: [{
    ...base.prospects[0],
    consent: { ...base.prospects[0].consent, channels: ["sms"] },
  }] }), now), /explicit opt-in/);

  const optedIn = buildGovernedLeadPlan(campaign({
    requestedChannels: ["voice_call"],
    prospects: [{
      ...base.prospects[0],
      consent: { ...base.prospects[0].consent, basis: "explicit_opt_in", channels: ["voice_call"] },
    }],
  }), now);
  assert.equal(optedIn.actions[0].status, "approval_required");
  assert.equal(optedIn.actions[0].channel, "voice_call");
});

test("rejects raw contacts, purchased lists, sensitive targeting, and minors", () => {
  const base = campaign();
  assert.throws(() => buildGovernedLeadPlan(campaign({ prospects: [{
    ...base.prospects[0],
    contactRef: "person@example.com",
  }] }), now));
  assert.throws(() => buildGovernedLeadPlan(campaign({ prospects: [{
    ...base.prospects[0],
    source: { ...base.prospects[0].source, purchasedOrStolenList: true as false },
  }] }), now));
  assert.throws(() => buildGovernedLeadPlan(campaign({ prospects: [{
    ...base.prospects[0],
    sensitiveTargeting: true as false,
  }] }), now));
  assert.throws(() => buildGovernedLeadPlan(campaign({ prospects: [{
    ...base.prospects[0],
    includesMinor: true as false,
  }] }), now));
});

test("keeps a bounded suppression ledger using opaque references", () => {
  const ledger = new LeadSuppressionLedger();
  ledger.suppress("contact_ref:example_001", "opt_out", now);
  assert.equal(ledger.has("contact_ref:example_001"), true);
  assert.deepEqual(ledger.list(), [{
    contactRef: "contact_ref:example_001",
    reason: "opt_out",
    suppressedAt: now.toISOString(),
  }]);
  assert.throws(() => ledger.suppress("person@example.com", "owner_block", now));

  const fullLedger = new LeadSuppressionLedger(1);
  fullLedger.suppress("contact_ref:example_001", "opt_out", now);
  assert.throws(
    () => fullLedger.suppress("contact_ref:example_002", "owner_block", now),
    /persist the ledger/,
  );
});
