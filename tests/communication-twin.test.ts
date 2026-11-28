import assert from "node:assert/strict";
import test from "node:test";

import {
  assessCommunicationAction,
  assessCommunicationIngestion,
  communicationTwinSettingsSchema,
  createCommunicationAuditEvent,
} from "../server/communication-twin";

const baseSettings = communicationTwinSettingsSchema.parse({
  sourceConsentGranted: true,
  contacts: [{
    contactId: "contact-1",
    relationship: "vip",
    canRead: true,
    canDraft: true,
    canSend: true,
    canAutoReply: true,
    canReceiveVoiceCalls: true,
  }],
});

const consent = { sourceConsentGranted: true };

test("default mode allows drafting but never silently sends", () => {
  const draft = assessCommunicationAction({
    action: "draft", channel: "email", contactId: "contact-1", ...consent,
  }, baseSettings);
  assert.equal(draft.allowed, true);
  assert.equal(draft.decision, "draft_only");

  const send = assessCommunicationAction({
    action: "send", channel: "email", contactId: "contact-1", content: "Thanks for the update.", ...consent,
  }, baseSettings);
  assert.equal(send.allowed, false);
  assert.match(send.reason, /explicit owner approval/);
});

test("unknown contacts and missing source consent fail closed", () => {
  const unknown = assessCommunicationAction({
    action: "draft", channel: "sms", contactId: "unknown", ...consent,
  }, baseSettings);
  assert.equal(unknown.allowed, false);

  const noConsent = assessCommunicationAction({
    action: "read", channel: "email", contactId: "contact-1",
  }, baseSettings);
  assert.equal(noConsent.allowed, false);
});

test("high-impact content cannot be sent or auto-replied", () => {
  const approvedSettings = communicationTwinSettingsSchema.parse({
    ...baseSettings,
    autonomyMode: "allowlisted_routine",
  });
  const content = "Please wire the payment funds today.";
  for (const action of ["send", "auto_reply"] as const) {
    const result = assessCommunicationAction({
      action, channel: "email", contactId: "contact-1", content,
      explicitOwnerApproval: true, lowStakesRoutine: true, ...consent,
    }, approvedSettings);
    assert.equal(result.allowed, false);
    assert.match(result.reason, /High-impact/);
  }
});

test("routine auto-replies require the autonomy mode and explicit contact allowlist", () => {
  const settings = communicationTwinSettingsSchema.parse({
    ...baseSettings,
    autonomyMode: "allowlisted_routine",
  });
  const result = assessCommunicationAction({
    action: "auto_reply", channel: "sms", contactId: "contact-1",
    content: "I received this. I'll take a look.", lowStakesRoutine: true, ...consent,
  }, settings);
  assert.equal(result.allowed, true);
  assert.equal(result.requiresOwnerApproval, false);
});

test("voice answering requires disclosure and human takeover", () => {
  const result = assessCommunicationAction({
    action: "answer_call", channel: "voice", contactId: "contact-1",
    aiDisclosureDelivered: false, ...consent,
  }, baseSettings);
  assert.equal(result.allowed, false);
  assert.match(result.reason, /disclosure/);
});

test("voice synthesis is blocked for contacts without voice permission", () => {
  const settings = communicationTwinSettingsSchema.parse({
    sourceConsentGranted: true,
    ownerVoiceCloneConsent: true,
    contacts: [{ contactId: "contact-no-voice", canDraft: true }],
  });
  const result = assessCommunicationAction({
    action: "synthesize_owner_voice", channel: "voice", contactId: "contact-no-voice",
    ownerVoiceCloneConsent: true, aiDisclosureDelivered: true, ...consent,
  }, settings);
  assert.equal(result.allowed, false);
  assert.match(result.reason, /not authorized for this contact/);
});

test("voice synthesis requires owner consent and AI disclosure", () => {
  const settings = communicationTwinSettingsSchema.parse({
    ...baseSettings, ownerVoiceCloneConsent: true,
  });
  const denied = assessCommunicationAction({
    action: "synthesize_owner_voice", channel: "voice", contactId: "contact-1",
    ownerVoiceCloneConsent: false, aiDisclosureDelivered: true, ...consent,
  }, settings);
  assert.equal(denied.allowed, false);

  const allowed = assessCommunicationAction({
    action: "synthesize_owner_voice", channel: "voice", contactId: "contact-1",
    ownerVoiceCloneConsent: true, aiDisclosureDelivered: true, ...consent,
  }, settings);
  assert.equal(allowed.allowed, true);
});

test("ingestion requires authorized source and explicit consent; training is not authorized", () => {
  const denied = assessCommunicationIngestion({
    source: "gmail", ownerAuthorized: false, sourceConsentGranted: true, contactIds: ["contact-1"],
  });
  assert.equal(denied.allowed, false);

  const accepted = assessCommunicationIngestion({
    source: "gmail", ownerAuthorized: true, sourceConsentGranted: true, contactIds: ["contact-1", "contact-1"],
  });
  assert.equal(accepted.allowed, true);
  assert.equal(accepted.contactCount, 1);
  assert.equal(accepted.rawMessageRetention, false);
  assert.equal(accepted.trainingEligibility, "not_authorized");
});

test("audit events never retain message content", () => {
  const event = createCommunicationAuditEvent({
    action: "send", channel: "email", contactId: "contact-1",
    decision: "blocked", reason: "Approval missing.",
  });
  assert.equal(event.messageContentStored, false);
  assert.equal("content" in event, false);
});

test("duplicate contact permissions are rejected", () => {
  assert.throws(() => communicationTwinSettingsSchema.parse({
    sourceConsentGranted: true,
    contacts: [
      { contactId: "same", canRead: true },
      { contactId: "same", canDraft: true },
    ],
  }), /unique contact IDs/);
});
