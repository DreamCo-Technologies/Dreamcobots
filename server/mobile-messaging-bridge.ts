import { createHmac, timingSafeEqual } from "node:crypto";
import { z } from "zod";
import { SecureJsonWebhookAdapter } from "./outbound-adapters";
import { assessCommunicationAction, communicationTwinSettingsSchema, type CommunicationTwinSettings } from "./communication-twin";

export const mobilePlatformSchema = z.enum(["ios", "android"]);
export const mobileProviderSchema = z.enum(["bluebubbles_mac_relay", "android_companion"]);
export const mobileChannelSchema = z.enum(["sms", "messaging"]);

export const mobileBridgeRegistrationSchema = z.object({
  ownerId: z.string().trim().min(1).max(160),
  deviceId: z.string().trim().min(1).max(160),
  platform: mobilePlatformSchema,
  provider: mobileProviderSchema,
  enabled: z.boolean().default(false),
  sourceConsentGranted: z.boolean().default(false),
  secretReference: z.string().regex(/^[A-Z][A-Z0-9_]{2,127}$/),
  allowedContactIds: z.array(z.string().trim().min(1).max(160)).max(500).default([]),
}).strict().superRefine((value, ctx) => {
  if (value.platform === "ios" && value.provider !== "bluebubbles_mac_relay") ctx.addIssue({ code: z.ZodIssueCode.custom, message: "iOS devices must use the authorized Mac relay provider.", path: ["provider"] });
  if (value.platform === "android" && value.provider !== "android_companion") ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Android devices must use the Android companion provider.", path: ["provider"] });
  if (new Set(value.allowedContactIds).size !== value.allowedContactIds.length) ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Allowed contact IDs must be unique.", path: ["allowedContactIds"] });
});

export const mobileInboundEventSchema = z.object({
  schema: z.literal("dreamco.mobile_message_event.v1"),
  eventId: z.string().trim().min(8).max(200),
  deviceId: z.string().trim().min(1).max(160),
  platform: mobilePlatformSchema,
  provider: mobileProviderSchema,
  channel: mobileChannelSchema,
  providerContactId: z.string().trim().min(1).max(200),
  contactId: z.string().trim().min(1).max(160),
  messageId: z.string().trim().min(1).max(200),
  body: z.string().min(1).max(12_000),
  receivedAt: z.string().datetime(),
}).strict().superRefine((value, ctx) => {
  if (value.platform === "ios" && value.provider !== "bluebubbles_mac_relay") ctx.addIssue({ code: z.ZodIssueCode.custom, message: "iOS events must originate from the authorized Mac relay.", path: ["provider"] });
  if (value.platform === "android" && value.provider !== "android_companion") ctx.addIssue({ code: z.ZodIssueCode.custom, message: "Android events must originate from the Android companion.", path: ["provider"] });
  if (value.platform === "android" && value.channel !== "sms") ctx.addIssue({ code: z.ZodIssueCode.custom, message: "The Android companion bridge currently supports SMS only.", path: ["channel"] });
});

export type MobileBridgeRegistration = z.infer<typeof mobileBridgeRegistrationSchema>;
export type MobileInboundEvent = z.infer<typeof mobileInboundEventSchema>;
export type MobileOutboundPayload = {
  deviceId: string; contactId: string; providerContactId: string;
  channel: z.infer<typeof mobileChannelSchema>; body: string; idempotencyKey: string;
};
export type MobileOutboundTransport = { send(input: MobileOutboundPayload): Promise<{ providerMessageId: string }> };
export type ReplayClaimStore = { claim(key: string, expiresAt: number): Promise<boolean> | boolean };

export class InMemoryReplayClaimStore implements ReplayClaimStore {
  private readonly claims = new Map<string, number>();
  constructor(private readonly maximumClaims = 10_000) {}
  claim(key: string, expiresAt: number) {
    const now = Date.now();
    for (const [existingKey, expiry] of this.claims) if (expiry <= now) this.claims.delete(existingKey);
    if (this.claims.has(key)) return false;
    if (this.claims.size >= this.maximumClaims) {
      const oldest = this.claims.keys().next().value;
      if (oldest) this.claims.delete(oldest);
    }
    this.claims.set(key, expiresAt);
    return true;
  }
}

export type MobileSignatureHeaders = { timestamp: string; signature: string };

export function signMobileWebhook(rawBody: string, timestampSeconds: number, secret: string) {
  return createHmac("sha256", secret).update(`${timestampSeconds}.${rawBody}`).digest("hex");
}

export function verifyMobileWebhookSignature(input: {
  rawBody: string; headers: MobileSignatureHeaders; secret: string; nowMs?: number; toleranceSeconds?: number;
}) {
  const nowMs = input.nowMs ?? Date.now();
  const toleranceSeconds = input.toleranceSeconds ?? 300;
  const timestamp = Number(input.headers.timestamp);
  if (!Number.isInteger(timestamp) || timestamp <= 0) return false;
  if (Math.abs(nowMs - timestamp * 1000) > toleranceSeconds * 1000) return false;
  if (!/^[a-f0-9]{64}$/i.test(input.headers.signature)) return false;
  const expected = Buffer.from(signMobileWebhook(input.rawBody, timestamp, input.secret), "hex");
  const supplied = Buffer.from(input.headers.signature, "hex");
  return expected.length === supplied.length && timingSafeEqual(expected, supplied);
}

export async function acceptInboundMobileMessage(input: {
  rawBody: string; headers: MobileSignatureHeaders; registration: MobileBridgeRegistration;
  settings: CommunicationTwinSettings; secret: string; replayStore: ReplayClaimStore; nowMs?: number;
}) {
  const registration = mobileBridgeRegistrationSchema.parse(input.registration);
  const settings = communicationTwinSettingsSchema.parse(input.settings);
  if (!registration.enabled || !registration.sourceConsentGranted || !settings.sourceConsentGranted) {
    return { accepted: false as const, status: "blocked" as const, reason: "The device bridge and owner source consent must both be enabled." };
  }
  if (!verifyMobileWebhookSignature({ rawBody: input.rawBody, headers: input.headers, secret: input.secret, nowMs: input.nowMs })) {
    return { accepted: false as const, status: "blocked" as const, reason: "Webhook signature is invalid or expired." };
  }
  let payload: unknown;
  try { payload = JSON.parse(input.rawBody); } catch {
    return { accepted: false as const, status: "blocked" as const, reason: "Webhook body must be valid JSON." };
  }
  const parsed = mobileInboundEventSchema.safeParse(payload);
  if (!parsed.success) return { accepted: false as const, status: "blocked" as const, reason: "Webhook event does not match the mobile messaging contract." };
  const event = parsed.data;
  if (event.deviceId !== registration.deviceId || event.platform !== registration.platform || event.provider !== registration.provider) {
    return { accepted: false as const, status: "blocked" as const, reason: "Event device identity does not match the registered bridge." };
  }
  if (!registration.allowedContactIds.includes(event.contactId)) {
    return { accepted: false as const, status: "blocked" as const, reason: "Contact is not allowlisted for this device bridge." };
  }
  const permission = assessCommunicationAction({ action: "read", channel: event.channel, contactId: event.contactId, sourceConsentGranted: true }, settings);
  if (!permission.allowed) return { accepted: false as const, status: "blocked" as const, reason: permission.reason };

  const replayKey = `${registration.ownerId}:${registration.deviceId}:${event.eventId}`;
  const claimed = await input.replayStore.claim(replayKey, (input.nowMs ?? Date.now()) + 10 * 60 * 1000);
  if (!claimed) return { accepted: false as const, status: "duplicate" as const, reason: "This webhook event has already been processed." };
  return {
    accepted: true as const, status: "accepted" as const,
    ownerId: registration.ownerId, deviceId: registration.deviceId, platform: event.platform,
    provider: event.provider, channel: event.channel, contactId: event.contactId,
    providerContactId: event.providerContactId, messageId: event.messageId, receivedAt: event.receivedAt,
    body: event.body, persistence: "ephemeral_until_draft_generation" as const,
    rawMessageRetention: false as const, modelTrainingAuthorized: false as const,
  };
}

export class SignedMobileWebhookTransport implements MobileOutboundTransport {
  constructor(
    readonly provider: z.infer<typeof mobileProviderSchema>,
    private readonly webhook: SecureJsonWebhookAdapter,
  ) {}
  async send(input: MobileOutboundPayload) {
    const result = await this.webhook.send({ schema: "dreamco.mobile_outbound_message.v1", provider: this.provider, ...input }, input.idempotencyKey);
    return { providerMessageId: result.providerMessageId };
  }
}

export class BlueBubblesMacRelayTransport extends SignedMobileWebhookTransport {
  constructor(webhook: SecureJsonWebhookAdapter) { super("bluebubbles_mac_relay", webhook); }
}
export class AndroidCompanionTransport extends SignedMobileWebhookTransport {
  constructor(webhook: SecureJsonWebhookAdapter) { super("android_companion", webhook); }
}

export async function sendMobileMessage(input: {
  registration: MobileBridgeRegistration; settings: CommunicationTwinSettings; transport: MobileOutboundTransport;
  action: "send" | "auto_reply"; contactId: string; providerContactId: string;
  channel: z.infer<typeof mobileChannelSchema>; body: string; idempotencyKey: string;
  explicitOwnerApproval?: boolean; lowStakesRoutine?: boolean; sourceConsentGranted: boolean;
}) {
  const registration = mobileBridgeRegistrationSchema.parse(input.registration);
  const settings = communicationTwinSettingsSchema.parse(input.settings);
  if (!registration.enabled || !registration.sourceConsentGranted || !settings.sourceConsentGranted || !input.sourceConsentGranted) {
    return { sent: false as const, status: "blocked" as const, reason: "The device bridge and owner source consent must both be enabled." };
  }
  if (!registration.allowedContactIds.includes(input.contactId)) return { sent: false as const, status: "blocked" as const, reason: "Contact is not allowlisted for this device bridge." };
  if (!input.body.trim() || input.body.length > 12_000) return { sent: false as const, status: "blocked" as const, reason: "Message body must contain 1–12,000 characters." };
  const decision = assessCommunicationAction({
    action: input.action, channel: input.channel, contactId: input.contactId, content: input.body,
    sourceConsentGranted: input.sourceConsentGranted,
    explicitOwnerApproval: input.explicitOwnerApproval ?? false,
    lowStakesRoutine: input.lowStakesRoutine ?? false,
  }, settings);
  if (!decision.allowed || decision.requiresOwnerApproval) return { sent: false as const, status: "approval_required" as const, reason: decision.reason };
  const result = await input.transport.send({
    deviceId: registration.deviceId, contactId: input.contactId, providerContactId: input.providerContactId,
    channel: input.channel, body: input.body, idempotencyKey: input.idempotencyKey,
  });
  return { sent: true as const, status: "accepted" as const, providerMessageId: result.providerMessageId, messageContentStored: false as const };
}

export function mobileBridgeReadiness(registrations: MobileBridgeRegistration[]) {
  const parsed = registrations.map((registration) => mobileBridgeRegistrationSchema.parse(registration));
  return {
    schema: "dreamco.mobile_messaging_readiness.v1",
    platforms: {
      ios: { provider: "bluebubbles_mac_relay", status: parsed.some((item) => item.platform === "ios" && item.enabled && item.sourceConsentGranted) ? "bridge_enabled" : "setup_required", requirements: ["owner-authorized Mac", "BlueBubbles server", "signed Buddy relay webhook", "explicit owner and contact consent"] },
      android: { provider: "android_companion", status: parsed.some((item) => item.platform === "android" && item.enabled && item.sourceConsentGranted) ? "bridge_enabled" : "setup_required", requirements: ["owner-installed Android companion", "SMS permissions as applicable", "signed Buddy webhook", "explicit owner and contact consent"] },
    },
    sharedPolicy: "server/communication-twin.ts", draftOnlyDefault: true, unknownContactsDenied: true,
    rawMessageRetention: false, modelTrainingAuthorized: false, durableReplayStoreRequiredForProduction: true,
  } as const;
}
