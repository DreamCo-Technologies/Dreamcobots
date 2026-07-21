import { pgTable, uuid, timestamp, jsonb, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const snapshotsTable = pgTable("snapshots", {
  id: uuid("id").primaryKey().defaultRandom(),
  capturedAt: timestamp("captured_at", { withTimezone: true }).notNull().defaultNow(),
  metrics: jsonb("metrics").$type<Record<string, number>>().notNull().default({}),
  meta: jsonb("meta").$type<Record<string, unknown>>().default({}),
}, (t) => ({
  capturedIdx: index("snapshots_captured_idx").on(t.capturedAt),
}));

export const insertSnapshotSchema = createInsertSchema(snapshotsTable).omit({ id: true, capturedAt: true });
export type InsertSnapshot = z.infer<typeof insertSnapshotSchema>;
export type Snapshot = typeof snapshotsTable.$inferSelect;
