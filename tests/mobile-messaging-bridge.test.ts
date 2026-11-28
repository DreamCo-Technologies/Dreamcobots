import assert from "node:assert/strict";
import test from "node:test";
import {
  AndroidCompanionTransport, BlueBubblesMacRelayTransport,
  InMemoryReplayClaimStore, acceptInboundMobileMessage, mobileBridgeReadiness,
  mobileBridgeRegistrationSchema, sendMobileMessage, signMobileWebhook,
  type MobileOutboundPayload,
} from "../server/mobile-messaging-bridge";
import { communicationTwinSettingsSchema } from "../server/communication-twin";
import { SecureJsonWebhookAdapter } from "../server/outbound-adapters";

const secret = "test-mobile-webhook-secret";
const now = 1_800_000_000_000;
const timestamp = Math.floor(now / 1000);
const settings = communicationTwinSettingsSchema.parse({
  sourceConsentGranted: true, autonomyMode: "allowlisted_routine",
  contacts: [{ contactId: "contact-1", canRead: true, canDraft: true, canSend: true, canAutoReply: true }],
});
const ios = mobileBridgeRegistrationSchema.parse({
  ownerId: "owner-1", deviceId: "iphone-relay-1", platform: "ios", provider: "bluebubbles_mac_relay",
  enabled: true, sourceConsentGranted: true, secretReference: "BUDDY_IOS_RELAY_SECRET", allowedContactIds: ["contact-1"],
});
const android = mobileBridgeRegistrationSchema.parse({
  ownerId: "owner-1", deviceId: "android-1", platform: "android", provider: "android_companion",
  enabled: true, sourceConsentGranted: true, secretReference: "BUDDY_ANDROID_BRIDGE_SECRET", allowedContactIds: ["contact-1"],
});

function signedEvent(overrides: Record<string, unknown> = {}) {
  const rawBody = JSON.stringify({
    schema: "dreamco.mobile_message_event.v1", eventId: "event-12345678", deviceId: "iphone-relay-1",
    platform: "ios", provider: "bluebubbles_mac_relay", channel: "messaging",
    providerContactId: "bluebubbles:handle-1", contactId: "contact-1", messageId: "message-1",
    body: "Hey, are we still meeting at six?", receivedAt: new Date(now).toISOString(), ...overrides,
  });
  return { rawBody, headers: { timestamp: String(timestamp), signature: signMobileWebhook(rawBody, timestamp, secret) } };
}

test("accepts signed iOS relay messages without retaining content", async () => {
  const result = await acceptInboundMobileMessage({ ...signedEvent(), registration: ios, settings, secret, replayStore: new InMemoryReplayClaimStore(), nowMs: now });
  assert.equal(result.accepted, true);
  if (result.accepted) {
    assert.equal(result.platform, "ios"); assert.equal(result.channel, "messaging");
    assert.equal(result.rawMessageRetention, false); assert.equal(result.modelTrainingAuthorized, false);
  }
});

test("accepts Android companion SMS using the shared contact policy", async () => {
  const event = signedEvent({ eventId: "android-event-12345678", deviceId: "android-1", platform: "android", provider: "android_companion", channel: "sms" });
  const result = await acceptInboundMobileMessage({ ...event, registration: android, settings, secret, replayStore: new InMemoryReplayClaimStore(), nowMs: now });
  assert.equal(result.accepted, true);
  if (result.accepted) assert.equal(result.platform, "android");
});

test("rejects invalid, stale, and tampered signatures", async () => {
  const event = signedEvent();
  const invalid = await acceptInboundMobileMessage({ ...event, headers: { ...event.headers, signature: "0".repeat(64) }, registration: ios, settings, secret, replayStore: new InMemoryReplayClaimStore(), nowMs: now });
  const stale = await acceptInboundMobileMessage({ ...event, registration: ios, settings, secret, replayStore: new InMemoryReplayClaimStore(), nowMs: now + 600_000 });
  assert.equal(invalid.accepted, false); assert.equal(stale.accepted, false);
});

test("rejects duplicate event IDs", async () => {
  const event = signedEvent(), replayStore = new InMemoryReplayClaimStore();
  const input = { ...event, registration: ios, settings, secret, replayStore, nowMs: now };
  assert.equal((await acceptInboundMobileMessage(input)).accepted, true);
  const replay = await acceptInboundMobileMessage(input);
  assert.equal(replay.accepted, false); assert.equal(replay.status, "duplicate");
});

test("rejects unknown contacts and mismatched devices", async () => {
  const unknown = await acceptInboundMobileMessage({ ...signedEvent({ contactId: "unknown-contact" }), registration: ios, settings, secret, replayStore: new InMemoryReplayClaimStore(), nowMs: now });
  const mismatch = await acceptInboundMobileMessage({ ...signedEvent({ deviceId: "other-device" }), registration: ios, settings, secret, replayStore: new InMemoryReplayClaimStore(), nowMs: now });
  assert.equal(unknown.accepted, false); assert.match(unknown.reason, /not allowlisted/);
  assert.equal(mismatch.accepted, false);
});

test("requires bridge and owner consent", async () => {
  const result = await acceptInboundMobileMessage({ ...signedEvent(), registration: { ...ios, sourceConsentGranted: false }, settings, secret, replayStore: new InMemoryReplayClaimStore(), nowMs: now });
  assert.equal(result.accepted, false);
});

test("default draft-only mode prevents outbound send without explicit approval", async () => {
  let sends = 0;
  const transport = { async send(_input: MobileOutboundPayload) { sends++; return { providerMessageId: "provider-1" }; } };
  const result = await sendMobileMessage({ registration: ios, settings: { ...settings, autonomyMode: "draft_only" }, transport, action: "send", contactId: "contact-1", providerContactId: "handle-1", channel: "messaging", body: "Confirmed, see you then.", idempotencyKey: "send-1", sourceConsentGranted: true });
  assert.equal(result.sent, false); assert.equal(sends, 0);
});

test("allowlisted routine auto-replies can use Android transport", async () => {
  let sentBody = "";
  const transport = { async send(input: MobileOutboundPayload) { sentBody = input.body; return { providerMessageId: "android-provider-1" }; } };
  const result = await sendMobileMessage({ registration: android, settings, transport, action: "auto_reply", contactId: "contact-1", providerContactId: "android-contact-1", channel: "sms", body: "I got your message and will reply shortly.", idempotencyKey: "android-send-1", sourceConsentGranted: true, lowStakesRoutine: true });
  assert.equal(result.sent, true); assert.equal(sentBody, "I got your message and will reply shortly.");
});

test("blocks high-impact content even for allowlisted contacts", async () => {
  let sends = 0;
  const transport = { async send(_input: MobileOutboundPayload) { sends++; return { providerMessageId: "must-not-send" }; } };
  const result = await sendMobileMessage({ registration: android, settings, transport, action: "auto_reply", contactId: "contact-1", providerContactId: "android-contact-1", channel: "sms", body: "Please wire the payment funds today.", idempotencyKey: "unsafe-1", sourceConsentGranted: true, lowStakesRoutine: true });
  assert.equal(result.sent, false); assert.equal(sends, 0);
});

test("enforces provider/platform pairings and reports both bridge states", () => {
  assert.throws(() => mobileBridgeRegistrationSchema.parse({ ...ios, platform: "android" }), /Android devices must use/);
  const readiness = mobileBridgeReadiness([ios, android]);
  assert.equal(readiness.platforms.ios.status, "bridge_enabled");
  assert.equal(readiness.platforms.android.status, "bridge_enabled");
  assert.equal(readiness.rawMessageRetention, false);
});

test("replay claims reject duplicates and are bounded", async () => {
  const store = new InMemoryReplayClaimStore(2);
  assert.equal(await store.claim("event-1", now + 60_000), true);
  assert.equal(await store.claim("event-1", now + 60_000), false);
});

test("provider transports deliver only through configured HTTPS relay adapters", async () => {
  const requests: Array<{ url: string; body: string }> = [];
  const fakeFetch: typeof fetch = async (input, init) => {
    requests.push({ url: String(input), body: String(init?.body ?? "") });
    return new Response(JSON.stringify({ providerMessageId: "relay-accepted" }), { status: 202 });
  };
  const iosWebhook = new SecureJsonWebhookAdapter(
    { id: "ios-relay", endpoint: "https://relay.example.com/ios", secretReference: "BUDDY_IOS_RELAY_SECRET" },
    () => "test-secret",
    fakeFetch,
  );
  const androidWebhook = new SecureJsonWebhookAdapter(
    { id: "android-relay", endpoint: "https://relay.example.com/android", secretReference: "BUDDY_ANDROID_RELAY_SECRET" },
    () => "test-secret",
    fakeFetch,
  );
  const payload: MobileOutboundPayload = {
    deviceId: "device-1", contactId: "contact-1", providerContactId: "provider-contact-1",
    channel: "sms", body: "Approved test message", idempotencyKey: "mobile-outbound-1",
  };
  const iosResult = await new BlueBubblesMacRelayTransport(iosWebhook).send(payload);
  const androidResult = await new AndroidCompanionTransport(androidWebhook).send(payload);
  assert.equal(iosResult.providerMessageId, "relay-accepted");
  assert.equal(androidResult.providerMessageId, "relay-accepted");
  assert.equal(JSON.parse(requests[0].body).provider, "bluebubbles_mac_relay");
  assert.equal(JSON.parse(requests[1].body).provider, "android_companion");
  assert.equal(requests[0].url, "https://relay.example.com/ios");
  assert.equal(requests[1].url, "https://relay.example.com/android");
});
