import assert from "node:assert/strict";
import test from "node:test";

import type { ApprovalNotificationEnvelope } from "../server/approval-notifications";
import {
  LocalApprovalInboxAdapter,
  SecureJsonWebhookAdapter,
  WebhookApprovalNotificationAdapter,
  outboundAdapterReadiness,
} from "../server/outbound-adapters";

const envelope: ApprovalNotificationEnvelope = {
  schema: "dreamco.approval_notification.v1",
  notificationId: "approval-notice-test-1",
  approvalRequestId: "approval-test-1",
  userId: "owner-1",
  botSlug: "social-sharing-bot",
  actionType: "publish_social_post",
  channel: "in_app",
  destinationRef: "contact:owner:in-app",
  title: "Review one post",
  summary: "Review the exact content before one publish action.",
  risk: "medium",
  reviewPath: "/approvals/approval-test-1",
  createdAt: "2026-07-22T00:00:00.000Z",
  expiresAt: "2026-07-22T00:15:00.000Z",
  oneActionOnly: true,
  containsSecrets: false,
};

test("stores in-app approvals in a bounded local inbox", async () => {
  const adapter = new LocalApprovalInboxAdapter(2);
  await adapter.send(envelope);
  await adapter.send({ ...envelope, notificationId: "approval-notice-test-2" });
  await adapter.send({ ...envelope, notificationId: "approval-notice-test-3" });
  const messages = adapter.list(envelope.destinationRef);
  assert.deepEqual(messages.map((item) => item.notificationId), ["approval-notice-test-2", "approval-notice-test-3"]);
});

test("sends external approvals through a secure idempotent webhook", async () => {
  let captured: RequestInit | undefined;
  const fakeFetch: typeof fetch = async (_input, init) => {
    captured = init;
    return new Response(JSON.stringify({ providerMessageId: "provider-1" }), {
      status: 202,
      headers: { "Content-Type": "application/json" },
    });
  };
  const webhook = new SecureJsonWebhookAdapter(
    { id: "sms-test", endpoint: "https://notify.example.com/approval", secretReference: "BUDDY_NOTIFY_TOKEN" },
    (reference) => reference === "BUDDY_NOTIFY_TOKEN" ? "test-secret" : undefined,
    fakeFetch,
  );
  const adapter = new WebhookApprovalNotificationAdapter("sms", webhook);
  const result = await adapter.send({ ...envelope, channel: "sms", destinationRef: "contact:owner:mobile" });
  assert.equal(result.providerMessageId, "provider-1");
  assert.equal(new Headers(captured?.headers).get("Idempotency-Key"), envelope.notificationId);
  assert.equal(new Headers(captured?.headers).get("Authorization"), "Bearer test-secret");
});

test("reports adapter code separately from provider configuration", () => {
  const readiness = outboundAdapterReadiness({ BUDDY_EMAIL_WEBHOOK_URL: "https://notify.example.com/email" });
  assert.equal(readiness.channels.in_app.status, "ready");
  assert.equal(readiness.channels.email.status, "configured");
  assert.equal(readiness.channels.sms.status, "configuration_required");
  assert.throws(() => new SecureJsonWebhookAdapter({ id: "bad", endpoint: "http://example.com" }), /HTTPS/);
});
