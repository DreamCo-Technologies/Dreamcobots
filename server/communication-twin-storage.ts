import {
  createCipheriv, createDecipheriv, createHmac, randomBytes, randomUUID,
} from "node:crypto";
import { and, desc, eq, gt, lt, sql } from "drizzle-orm";
import { z } from "zod";
import { db } from "./db";
import {
  communicationTwinSettings as communicationTwinSettingsTable,
  communicationTwinDrafts,
  communicationTwinAuditEvents,
  mobileBridgeDevices,
  mobileBridgeContactMappings,
  mobileBridgeReplayEvents,
  mobileBridgeDeliveryReceipts,
} from "@shared/schema";
import {
  communicationTwinSettingsSchema,
  createCommunicationAuditEvent,
  type CommunicationTwinSettings,
} from "./communication-twin";
import {
  mobileBridgeRegistrationSchema,
  type MobileBridgeRegistration,
  type ReplayClaimStore,
} from "./mobile-messaging-bridge";

const ownerIdSchema = z.string().regex(/^oauth_[a-f0-9]{48}$/);
const deviceIdSchema = z.string().trim().min(1).max(160);
const contactIdSchema = z.string().trim().min(1).max(160);
const providerContactIdSchema = z.string().trim().min(1).max(200);
const draftIdSchema = z.string().uuid();

type OwnerTx = Parameters<Parameters<typeof db.transaction>[0]>[0];

async function withOwner<T>(ownerId: string, operation: (tx: OwnerTx) => Promise<T>): Promise<T> {
  const safeOwnerId = ownerIdSchema.parse(ownerId);
  return db.transaction(async (tx) => {
    await tx.execute(sql`select set_config('app.owner_id', ${safeOwnerId}, true)`);
    return operation(tx);
  });
}

function mappingKey(): Buffer {
  const encoded = process.env.BUDDY_CONTACT_MAPPING_ENCRYPTION_KEY ?? "";
  if (!/^[A-Za-z0-9_-]{43}$/.test(encoded)) {
    throw new Error("BUDDY_CONTACT_MAPPING_ENCRYPTION_KEY must be a 32-byte base64url secret.");
  }
  const key = Buffer.from(encoded, "base64url");
  if (key.length !== 32) throw new Error("BUDDY_CONTACT_MAPPING_ENCRYPTION_KEY must decode to exactly 32 bytes.");
  return key;
}

function providerContactHash(ownerId: string, deviceId: string, providerContactId: string, key: Buffer): string {
  const indexKey = createHmac("sha256", key).update("buddy-mobile-contact-index-v1").digest();
  return createHmac("sha256", indexKey)
    .update(ownerId).update("\0").update(deviceId).update("\0").update(providerContactId)
    .digest("hex");
}

function encryptProviderContactId(value: string, key: Buffer) {
  const iv = randomBytes(12);
  const cipher = createCipheriv("aes-256-gcm", key, iv);
  const ciphertext = Buffer.concat([cipher.update(value, "utf8"), cipher.final()]);
  return {
    ciphertext: ciphertext.toString("base64url"),
    iv: iv.toString("base64url"),
    tag: cipher.getAuthTag().toString("base64url"),
  };
}

function decryptProviderContactId(
  ciphertext: string, iv: string, tag: string, key: Buffer,
): string {
  const decipher = createDecipheriv("aes-256-gcm", key, Buffer.from(iv, "base64url"));
  decipher.setAuthTag(Buffer.from(tag, "base64url"));
  return Buffer.concat([
    decipher.update(Buffer.from(ciphertext, "base64url")),
    decipher.final(),
  ]).toString("utf8");
}

export async function getCommunicationTwinSettings(ownerId: string): Promise<CommunicationTwinSettings> {
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.select().from(communicationTwinSettingsTable)
      .where(eq(communicationTwinSettingsTable.ownerId, ownerId)).limit(1);
    return communicationTwinSettingsSchema.parse(row?.settings ?? {});
  });
}

export async function saveCommunicationTwinSettings(
  ownerId: string, input: unknown,
): Promise<CommunicationTwinSettings> {
  const settings = communicationTwinSettingsSchema.parse(input);
  await withOwner(ownerId, async (tx) => {
    await tx.insert(communicationTwinSettingsTable).values({
      ownerId, settings, updatedAt: new Date(),
    }).onConflictDoUpdate({
      target: communicationTwinSettingsTable.ownerId,
      set: { settings, updatedAt: new Date() },
    });
  });
  return settings;
}

function toRegistration(row: typeof mobileBridgeDevices.$inferSelect): MobileBridgeRegistration {
  return mobileBridgeRegistrationSchema.parse({
    ownerId: row.ownerId,
    deviceId: row.deviceId,
    platform: row.platform,
    provider: row.provider,
    enabled: row.enabled && !row.revokedAt,
    sourceConsentGranted: row.sourceConsentGranted && !row.revokedAt,
    secretReference: row.secretReference,
    allowedContactIds: row.allowedContactIds,
  });
}

export async function getMobileBridgeDevice(ownerId: string, deviceId: string) {
  const safeDeviceId = deviceIdSchema.parse(deviceId);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.select().from(mobileBridgeDevices).where(and(
      eq(mobileBridgeDevices.ownerId, ownerId),
      eq(mobileBridgeDevices.deviceId, safeDeviceId),
    )).limit(1);
    return row ? toRegistration(row) : undefined;
  });
}

export async function listMobileBridgeRegistrations(ownerId: string): Promise<MobileBridgeRegistration[]> {
  return withOwner(ownerId, async (tx) => {
    const rows = await tx.select().from(mobileBridgeDevices)
      .where(eq(mobileBridgeDevices.ownerId, ownerId))
      .orderBy(desc(mobileBridgeDevices.createdAt));
    return rows.map(toRegistration);
  });
}

export async function listMobileBridgeDevices(ownerId: string) {
  return withOwner(ownerId, async (tx) => {
    const rows = await tx.select().from(mobileBridgeDevices)
      .where(eq(mobileBridgeDevices.ownerId, ownerId))
      .orderBy(desc(mobileBridgeDevices.createdAt));
    return rows.map((row) => ({
      deviceId: row.deviceId,
      platform: row.platform,
      provider: row.provider,
      enabled: row.enabled && !row.revokedAt,
      sourceConsentGranted: row.sourceConsentGranted && !row.revokedAt,
      allowedContactIds: row.allowedContactIds,
      revokedAt: row.revokedAt,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    }));
  });
}

export async function registerMobileBridgeDevice(ownerId: string, input: unknown) {
  const registration = mobileBridgeRegistrationSchema.parse({ ...(input as object), ownerId });
  if (registration.enabled) {
    const secret = process.env[registration.secretReference];
    if (!secret || Buffer.byteLength(secret, "utf8") < 32) {
      throw new Error("The referenced mobile webhook secret must be configured and contain at least 32 bytes before enabling a device.");
    }
  }
  const settings = await getCommunicationTwinSettings(ownerId);
  if (registration.allowedContactIds.some((id) => !settings.contacts.some((contact) => contact.contactId === id))) {
    throw new Error("Every device-allowed contact must exist in the owner's communication permission list.");
  }
  await withOwner(ownerId, async (tx) => {
    await tx.insert(mobileBridgeDevices).values({
      ownerId,
      deviceId: registration.deviceId,
      platform: registration.platform,
      provider: registration.provider,
      enabled: registration.enabled,
      sourceConsentGranted: registration.sourceConsentGranted,
      secretReference: registration.secretReference,
      allowedContactIds: registration.allowedContactIds,
      revokedAt: null,
      updatedAt: new Date(),
    }).onConflictDoUpdate({
      target: [mobileBridgeDevices.ownerId, mobileBridgeDevices.deviceId],
      set: {
        platform: registration.platform,
        provider: registration.provider,
        enabled: registration.enabled,
        sourceConsentGranted: registration.sourceConsentGranted,
        secretReference: registration.secretReference,
        allowedContactIds: registration.allowedContactIds,
        revokedAt: null,
        updatedAt: new Date(),
      },
    });
  });
  return getMobileBridgeDevice(ownerId, registration.deviceId);
}

export async function revokeMobileBridgeDevice(ownerId: string, deviceId: string) {
  const safeDeviceId = deviceIdSchema.parse(deviceId);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.update(mobileBridgeDevices).set({
      enabled: false, sourceConsentGranted: false, revokedAt: new Date(), updatedAt: new Date(),
    }).where(and(
      eq(mobileBridgeDevices.ownerId, ownerId),
      eq(mobileBridgeDevices.deviceId, safeDeviceId),
    )).returning({ deviceId: mobileBridgeDevices.deviceId });
    return Boolean(row);
  });
}

export async function saveMobileBridgeContactMapping(input: {
  ownerId: string; deviceId: string; providerContactId: string; contactId: string;
}) {
  const ownerId = ownerIdSchema.parse(input.ownerId);
  const deviceId = deviceIdSchema.parse(input.deviceId);
  const providerId = providerContactIdSchema.parse(input.providerContactId);
  const contactId = contactIdSchema.parse(input.contactId);
  const registration = await getMobileBridgeDevice(ownerId, deviceId);
  if (!registration || !registration.enabled || !registration.sourceConsentGranted) {
    throw new Error("An enabled, consented device registration is required before mapping contacts.");
  }
  if (!registration.allowedContactIds.includes(contactId)) {
    throw new Error("The contact is not allowlisted for this device.");
  }
  const settings = await getCommunicationTwinSettings(ownerId);
  const permission = settings.contacts.find((item) => item.contactId === contactId);
  if (!permission || (!permission.canRead && !permission.canSend)) {
    throw new Error("The contact needs explicit read or send permission before provider mapping.");
  }
  const key = mappingKey();
  const hash = providerContactHash(ownerId, deviceId, providerId, key);
  const encrypted = encryptProviderContactId(providerId, key);
  await withOwner(ownerId, async (tx) => {
    await tx.insert(mobileBridgeContactMappings).values({
      ownerId, deviceId, providerContactHash: hash,
      providerContactCiphertext: encrypted.ciphertext,
      providerContactIv: encrypted.iv,
      providerContactTag: encrypted.tag,
      contactId, revokedAt: null,
    }).onConflictDoUpdate({
      target: [
        mobileBridgeContactMappings.ownerId,
        mobileBridgeContactMappings.deviceId,
        mobileBridgeContactMappings.providerContactHash,
      ],
      set: {
        providerContactCiphertext: encrypted.ciphertext,
        providerContactIv: encrypted.iv,
        providerContactTag: encrypted.tag,
        contactId,
        revokedAt: null,
      },
    });
  });
  return { mapped: true as const, deviceId, contactId, providerContactStoredEncrypted: true as const };
}

export async function resolveMobileContactId(input: {
  ownerId: string; deviceId: string; providerContactId: string;
}) {
  const key = mappingKey();
  const hash = providerContactHash(input.ownerId, input.deviceId, input.providerContactId, key);
  return withOwner(input.ownerId, async (tx) => {
    const [row] = await tx.select({ contactId: mobileBridgeContactMappings.contactId })
      .from(mobileBridgeContactMappings).where(and(
        eq(mobileBridgeContactMappings.ownerId, input.ownerId),
        eq(mobileBridgeContactMappings.deviceId, input.deviceId),
        eq(mobileBridgeContactMappings.providerContactHash, hash),
        sql`${mobileBridgeContactMappings.revokedAt} IS NULL`,
      )).limit(1);
    return row?.contactId;
  });
}

export async function resolveMobileProviderContactId(input: {
  ownerId: string; deviceId: string; contactId: string;
}) {
  const key = mappingKey();
  const [row] = await withOwner(input.ownerId, async (tx) => tx.select()
    .from(mobileBridgeContactMappings).where(and(
      eq(mobileBridgeContactMappings.ownerId, input.ownerId),
      eq(mobileBridgeContactMappings.deviceId, input.deviceId),
      eq(mobileBridgeContactMappings.contactId, input.contactId),
      sql`${mobileBridgeContactMappings.revokedAt} IS NULL`,
    )).limit(1));
  if (!row) return undefined;
  return decryptProviderContactId(
    row.providerContactCiphertext, row.providerContactIv, row.providerContactTag, key,
  );
}

export async function claimMobileReplayEvent(
  ownerId: string, deviceId: string, eventId: string, expiresAt: number,
): Promise<boolean> {
  const safeEventId = z.string().trim().min(8).max(200).parse(eventId);
  return withOwner(ownerId, async (tx) => {
    const now = new Date();
    await tx.delete(mobileBridgeReplayEvents).where(and(
      eq(mobileBridgeReplayEvents.ownerId, ownerId),
      lt(mobileBridgeReplayEvents.expiresAt, now),
    ));
    const [claimed] = await tx.insert(mobileBridgeReplayEvents).values({
      ownerId, deviceId, eventId: safeEventId, expiresAt: new Date(expiresAt),
    }).onConflictDoNothing({
      target: [
        mobileBridgeReplayEvents.ownerId,
        mobileBridgeReplayEvents.deviceId,
        mobileBridgeReplayEvents.eventId,
      ],
    }).returning({ id: mobileBridgeReplayEvents.id });
    return Boolean(claimed);
  });
}

export async function releaseMobileReplayEvent(ownerId: string, deviceId: string, eventId: string) {
  return withOwner(ownerId, async (tx) => {
    await tx.delete(mobileBridgeReplayEvents).where(and(
      eq(mobileBridgeReplayEvents.ownerId, ownerId),
      eq(mobileBridgeReplayEvents.deviceId, deviceId),
      eq(mobileBridgeReplayEvents.eventId, eventId),
    ));
  });
}

export class PostgresMobileReplayClaimStore implements ReplayClaimStore {
  constructor(private readonly ownerId: string, private readonly deviceId: string) {}
  claim(key: string, expiresAt: number) {
    const prefix = `${this.ownerId}:${this.deviceId}:`;
    if (!key.startsWith(prefix)) return false;
    return claimMobileReplayEvent(this.ownerId, this.deviceId, key.slice(prefix.length), expiresAt);
  }
  release(eventId: string) {
    return releaseMobileReplayEvent(this.ownerId, this.deviceId, eventId);
  }
}

export async function appendCommunicationTwinAudit(
  ownerId: string,
  deviceId: string | undefined,
  input: Parameters<typeof createCommunicationAuditEvent>[0],
) {
  const event = createCommunicationAuditEvent(input);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.insert(communicationTwinAuditEvents).values({
      ownerId, deviceId: deviceId ?? null,
      action: event.action, channel: event.channel, contactId: event.contactId,
      decision: event.decision, reason: event.reason,
    }).returning();
    return row;
  });
}

export async function createCommunicationTwinDraft(input: {
  ownerId: string; deviceId: string; messageId: string; contactId: string;
  channel: "sms" | "messaging"; draftBody: string; expiresAt?: Date;
}) {
  const draftBody = z.string().trim().min(1).max(12_000).parse(input.draftBody);
  const draftId = randomUUID();
  return withOwner(input.ownerId, async (tx) => {
    const [created] = await tx.insert(communicationTwinDrafts).values({
      ownerId: input.ownerId, draftId, deviceId: input.deviceId,
      messageId: z.string().trim().min(1).max(200).parse(input.messageId),
      contactId: contactIdSchema.parse(input.contactId),
      channel: input.channel, draftBody, status: "pending_approval",
      expiresAt: input.expiresAt ?? new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    }).onConflictDoNothing({
      target: [
        communicationTwinDrafts.ownerId,
        communicationTwinDrafts.deviceId,
        communicationTwinDrafts.messageId,
      ],
    }).returning();
    if (created) return created;
    const [existing] = await tx.select().from(communicationTwinDrafts).where(and(
      eq(communicationTwinDrafts.ownerId, input.ownerId),
      eq(communicationTwinDrafts.deviceId, input.deviceId),
      eq(communicationTwinDrafts.messageId, input.messageId),
    )).limit(1);
    if (!existing) throw new Error("communication_twin_draft_conflict");
    return existing;
  });
}

export async function listCommunicationTwinDrafts(ownerId: string, limit = 50) {
  const safeLimit = z.number().int().min(1).max(100).parse(limit);
  return withOwner(ownerId, async (tx) => tx.select({
    draftId: communicationTwinDrafts.draftId,
    deviceId: communicationTwinDrafts.deviceId,
    messageId: communicationTwinDrafts.messageId,
    contactId: communicationTwinDrafts.contactId,
    channel: communicationTwinDrafts.channel,
    draftBody: communicationTwinDrafts.draftBody,
    status: communicationTwinDrafts.status,
    expiresAt: communicationTwinDrafts.expiresAt,
    createdAt: communicationTwinDrafts.createdAt,
    updatedAt: communicationTwinDrafts.updatedAt,
  }).from(communicationTwinDrafts).where(and(
    eq(communicationTwinDrafts.ownerId, ownerId),
    gt(communicationTwinDrafts.expiresAt, new Date()),
  )).orderBy(desc(communicationTwinDrafts.createdAt)).limit(safeLimit));
}

export async function getCommunicationTwinDraft(ownerId: string, draftId: string) {
  const safeDraftId = draftIdSchema.parse(draftId);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.select().from(communicationTwinDrafts).where(and(
      eq(communicationTwinDrafts.ownerId, ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
    )).limit(1);
    return row;
  });
}

export async function claimCommunicationTwinDraftForSend(ownerId: string, draftId: string) {
  const safeDraftId = draftIdSchema.parse(draftId);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.update(communicationTwinDrafts).set({
      status: "sending", updatedAt: new Date(),
    }).where(and(
      eq(communicationTwinDrafts.ownerId, ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
      eq(communicationTwinDrafts.status, "pending_approval"),
      gt(communicationTwinDrafts.expiresAt, new Date()),
    )).returning();
    return row;
  });
}

export async function completeCommunicationTwinDraftSend(input: {
  ownerId: string; draftId: string; providerMessageId: string; idempotencyKey: string;
}) {
  const safeDraftId = draftIdSchema.parse(input.draftId);
  return withOwner(input.ownerId, async (tx) => {
    const [draft] = await tx.select().from(communicationTwinDrafts).where(and(
      eq(communicationTwinDrafts.ownerId, input.ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
      eq(communicationTwinDrafts.status, "sending"),
    )).limit(1);
    if (!draft) throw new Error("communication_twin_draft_send_claim_missing");
    await tx.insert(mobileBridgeDeliveryReceipts).values({
      ownerId: input.ownerId, deviceId: draft.deviceId,
      idempotencyKey: input.idempotencyKey,
      providerMessageId: input.providerMessageId,
      contactId: draft.contactId, channel: draft.channel, status: "accepted",
    }).onConflictDoNothing({
      target: [
        mobileBridgeDeliveryReceipts.ownerId,
        mobileBridgeDeliveryReceipts.deviceId,
        mobileBridgeDeliveryReceipts.idempotencyKey,
      ],
    });
    const [updated] = await tx.update(communicationTwinDrafts).set({
      status: "sent", updatedAt: new Date(),
    }).where(and(
      eq(communicationTwinDrafts.ownerId, input.ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
      eq(communicationTwinDrafts.status, "sending"),
    )).returning();
    return updated;
  });
}

export async function markCommunicationTwinDraftDeliveryUnknown(ownerId: string, draftId: string) {
  const safeDraftId = draftIdSchema.parse(draftId);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.update(communicationTwinDrafts).set({
      status: "delivery_unknown", updatedAt: new Date(),
    }).where(and(
      eq(communicationTwinDrafts.ownerId, ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
      eq(communicationTwinDrafts.status, "sending"),
    )).returning();
    return row;
  });
}

export async function updateCommunicationTwinDraftBody(
  ownerId: string, draftId: string, draftBody: string,
) {
  const safeDraftId = draftIdSchema.parse(draftId);
  const safeBody = z.string().trim().min(1).max(12_000).parse(draftBody);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.update(communicationTwinDrafts).set({
      draftBody: safeBody, updatedAt: new Date(),
    }).where(and(
      eq(communicationTwinDrafts.ownerId, ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
      eq(communicationTwinDrafts.status, "pending_approval"),
      gt(communicationTwinDrafts.expiresAt, new Date()),
    )).returning({ draftId: communicationTwinDrafts.draftId });
    return Boolean(row);
  });
}

export async function resetCommunicationTwinDraftSendClaim(ownerId: string, draftId: string) {
  const safeDraftId = draftIdSchema.parse(draftId);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.update(communicationTwinDrafts).set({
      status: "pending_approval", updatedAt: new Date(),
    }).where(and(
      eq(communicationTwinDrafts.ownerId, ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
      eq(communicationTwinDrafts.status, "sending"),
    )).returning({ draftId: communicationTwinDrafts.draftId });
    return Boolean(row);
  });
}

export async function rejectCommunicationTwinDraft(ownerId: string, draftId: string) {
  const safeDraftId = draftIdSchema.parse(draftId);
  return withOwner(ownerId, async (tx) => {
    const [row] = await tx.update(communicationTwinDrafts).set({
      status: "rejected", updatedAt: new Date(),
    }).where(and(
      eq(communicationTwinDrafts.ownerId, ownerId),
      eq(communicationTwinDrafts.draftId, safeDraftId),
      eq(communicationTwinDrafts.status, "pending_approval"),
    )).returning({ draftId: communicationTwinDrafts.draftId });
    return Boolean(row);
  });
}
