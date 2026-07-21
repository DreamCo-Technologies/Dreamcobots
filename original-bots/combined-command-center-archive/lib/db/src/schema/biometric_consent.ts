import { pgTable, text, uuid, timestamp, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

/**
 * Legal acknowledgments. Before a user may enroll a biometric (their own voice
 * or face) or use any cloning feature, they must read and accept the versioned
 * biometric/likeness policy. Every acceptance is recorded here with the exact
 * policy version and timestamp — this is the "read all the laws before signing
 * up to use Buddy" audit record. Acceptance of an old version does not satisfy
 * a newer one (re-acknowledgment required when the policy version changes).
 */
export const legalAcknowledgmentsTable = pgTable(
  "legal_acknowledgments",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id").notNull(),
    documentKey: text("document_key").notNull(), // e.g. "biometric-cloning-policy"
    version: text("version").notNull(),
    acknowledgedAt: timestamp("acknowledged_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => ({
    userIdx: index("legal_ack_user_idx").on(t.userId),
    docIdx: index("legal_ack_doc_idx").on(t.documentKey),
  }),
);

export const insertLegalAcknowledgmentSchema = createInsertSchema(legalAcknowledgmentsTable).omit({
  id: true,
  acknowledgedAt: true,
});
export type InsertLegalAcknowledgment = z.infer<typeof insertLegalAcknowledgmentSchema>;
export type LegalAcknowledgment = typeof legalAcknowledgmentsTable.$inferSelect;

/**
 * Biometric enrollments. A user can only clone a voice or face they have
 * personally enrolled and consented to — this is the "sign in with your voice
 * and/or image to use your voice and/or image" authorization model. Each row
 * records the modality, the reference to the user's own enrolled sample, the
 * method (recorded in-browser or uploaded), which policy version they accepted
 * at enrollment, consent timestamp, and revocation state. Cloning is gated to
 * modalities that have an active (non-revoked) enrollment for the requesting
 * user.
 *
 * Honesty note: actual biometric *matching* (verifying a presented sample truly
 * belongs to the enrolled person) and the cloning itself require a connected
 * engine (DREAMCO_VOICE_URL / DREAMCO_IMAGE_CLONE_URL). This table is the real,
 * enforced consent/authorization ledger; it does not fabricate the engine.
 */
export const biometricEnrollmentsTable = pgTable(
  "biometric_enrollments",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: text("user_id").notNull(),
    modality: text("modality").notNull(), // "voice" | "image"
    status: text("status").notNull().default("enrolled"), // "enrolled" | "revoked"
    sampleRef: text("sample_ref").notNull(), // server-generated id of the user's own enrolled sample (never client-supplied)
    enrollmentMethod: text("enrollment_method"), // "recorded" | "uploaded"
    lawsVersion: text("laws_version").notNull(), // policy version accepted at enrollment
    consentGivenAt: timestamp("consent_given_at", { withTimezone: true }).notNull().defaultNow(),
    revokedAt: timestamp("revoked_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow()
      .$onUpdate(() => new Date()),
  },
  (t) => ({
    userIdx: index("biometric_enroll_user_idx").on(t.userId),
    modalityIdx: index("biometric_enroll_modality_idx").on(t.modality),
  }),
);

export const insertBiometricEnrollmentSchema = createInsertSchema(biometricEnrollmentsTable).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertBiometricEnrollment = z.infer<typeof insertBiometricEnrollmentSchema>;
export type BiometricEnrollment = typeof biometricEnrollmentsTable.$inferSelect;
