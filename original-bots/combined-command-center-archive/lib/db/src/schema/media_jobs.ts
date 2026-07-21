import { pgTable, text, uuid, jsonb, boolean, timestamp, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

/**
 * Audit log + record for every media-generation request (voice, image, video,
 * music, commercial). Every row captures who asked, what for, whether they
 * affirmed consent/authorization, the provider used, and the outcome. This is
 * the audit trail the build directive requires for media generation — no job
 * runs without an authenticated user and an explicit consent acknowledgement.
 */
export const mediaJobsTable = pgTable("media_jobs", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: text("user_id").notNull(),
  kind: text("kind").notNull(), // image | voice | music | video | commercial
  provider: text("provider"),
  // queued | running | succeeded | failed | needs_key | needs_consent
  status: text("status").notNull().default("queued"),
  prompt: text("prompt").notNull(),
  params: jsonb("params").$type<Record<string, unknown>>().notNull().default({}),
  resultUrl: text("result_url"),
  error: text("error"),
  consent: boolean("consent").notNull().default(false),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
}, (t) => ({
  userIdx: index("media_jobs_user_idx").on(t.userId),
  kindIdx: index("media_jobs_kind_idx").on(t.kind),
}));

export const insertMediaJobSchema = createInsertSchema(mediaJobsTable).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});
export type InsertMediaJob = z.infer<typeof insertMediaJobSchema>;
export type MediaJob = typeof mediaJobsTable.$inferSelect;
