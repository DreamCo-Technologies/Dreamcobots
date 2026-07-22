import assert from "node:assert/strict";
import test from "node:test";

import {
  createApprovalNotificationPlan,
  dispatchApprovalNotification,
  notificationPreferencesSchema,
  type ApprovalNotificationAdapter,
} from "../server/approval-notifications";

const request = {
  approvalRequestId: "approval-task-1234",
  userId: "owner-1",
  botSlug: "social-sharing-bot",
  actionType: "publish_social_post",
  title: "Approve scheduled post",
  summary: "Review one draft post before Buddy publishes it to the selected account.",
  risk: "medium" as const,
  expiresInSeconds: 900,
};

test("plans the user's verified notification choices without exposing contact details", () => {
  const plan = createApprovalNotificationPlan(request, {
    channels: [
      { channel: "in_app", enabled: true, verified: true, destinationRef: "contact:owner:in-app", explicitOptIn: true },
      { channel: "email", enabled: true, verified: true, destinationRef: "contact:owner:email-primary", explicitOptIn: true },
      { channel: "sms", enabled: true, verified: true, destinationRef: "contact:owner:mobile-primary", explicitOptIn: true },
      { channel: "voice_call", enabled: false, verified: true, destinationRef: "contact:owner:mobile-primary", explicitOptIn: true },
    ],
  }, new Date("2026-07-21T12:00:00Z"));
  assert.equal(plan.status, "ready_for_adapter_dispatch");
  assert.deepEqual(plan.notifications.map((item) => item.channel), ["in_app", "email", "sms"]);
  assert.equal(plan.skipped[0].reason, "disabled_by_user");
  const serialized = JSON.stringify(plan);
  assert.equal(serialized.includes("@"), false);
  assert.equal(serialized.includes("+1"), false);
});

test("blocks unverified destinations, missing SMS opt-in, raw addresses, and secrets", () => {
  const plan = createApprovalNotificationPlan(request, {
    channels: [
      { channel: "email", enabled: true, verified: false, destinationRef: "contact:owner:email-primary", explicitOptIn: true },
      { channel: "sms", enabled: true, verified: true, destinationRef: "contact:owner:mobile-primary", explicitOptIn: false },
    ],
  });
  assert.equal(plan.status, "no_verified_channel");
  assert.deepEqual(plan.skipped.map((item) => item.reason), ["destination_not_verified", "explicit_opt_in_required"]);

  assert.equal(notificationPreferencesSchema.safeParse({
    channels: [{ channel: "email", enabled: true, verified: true, destinationRef: "owner@example.com", explicitOptIn: true }],
  }).success, false);
  assert.equal(notificationPreferencesSchema.safeParse({
    channels: [{ channel: "in_app", enabled: true, verified: true, destinationRef: "contact:owner:in-app", explicitOptIn: true }],
    quietHours: {
      enabled: true,
      startHourLocal: 22,
      endHourLocal: 7,
      timezone: "Not/A-Timezone",
      criticalOverride: false,
    },
  }).success, false);
  assert.throws(() => createApprovalNotificationPlan({
    ...request,
    summary: "Use github_pat_12345678901234567890 for the action.",
  }, {
    channels: [{ channel: "in_app", enabled: true, verified: true, destinationRef: "contact:owner:in-app", explicitOptIn: true }],
  }), /credentials/);
});

test("dispatches once through the matching adapter", async () => {
  const plan = createApprovalNotificationPlan(request, {
    channels: [{ channel: "email", enabled: true, verified: true, destinationRef: "contact:owner:email-primary", explicitOptIn: true }],
  }, new Date("2026-07-21T12:00:00Z"));
  const sent: string[] = [];
  const adapter: ApprovalNotificationAdapter = {
    channel: "email",
    async send(envelope) {
      sent.push(envelope.notificationId);
      return { providerMessageId: "provider-message-1" };
    },
  };
  const claimed = new Set<string>();
  const replay = {
    async claim(id: string) {
      if (claimed.has(id)) return false;
      claimed.add(id);
      return true;
    },
  };
  const envelope = plan.notifications[0];
  const receipt = await dispatchApprovalNotification(
    envelope,
    adapter,
    replay,
    new Date("2026-07-21T12:01:00Z"),
  );
  assert.equal(receipt.channel, "email");
  assert.equal(sent.length, 1);
  await assert.rejects(
    dispatchApprovalNotification(envelope, adapter, replay, new Date("2026-07-21T12:02:00Z")),
    /already been dispatched/,
  );
});
