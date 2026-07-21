import { pgTable, text, timestamp, uuid, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

/**
 * Buddy's persistent memory. Every note Buddy takes (learnings, capability gaps
 * it noticed, tasks) and every piece of human guidance is stored here so Buddy
 * remembers across sessions instead of forgetting when a chat ends. This is the
 * store Buddy reads back into its own context — its way of "training" on real,
 * accumulated knowledge rather than pretending to learn.
 */
export const buddyNotesTable = pgTable("buddy_notes", {
  id: uuid("id").primaryKey().defaultRandom(),
  userId: text("user_id").notNull(), // owner — notes are private per authenticated user
  // learning | task | preference | capability_gap | guidance
  category: text("category").notNull().default("learning"),
  content: text("content").notNull(),
  source: text("source").notNull().default("buddy"), // buddy | human
  sessionId: text("session_id"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  categoryIdx: index("buddy_notes_category_idx").on(t.category),
  userIdx: index("buddy_notes_user_idx").on(t.userId),
  createdIdx: index("buddy_notes_created_idx").on(t.createdAt),
}));

export const insertBuddyNoteSchema = createInsertSchema(buddyNotesTable, {
  category: z.enum(["learning", "task", "preference", "capability_gap", "guidance"]),
  content: z.string().min(1).max(4000),
  source: z.enum(["buddy", "human"]).optional(),
  sessionId: z.string().max(200).optional(),
}).omit({ id: true, createdAt: true, userId: true });
export type InsertBuddyNote = z.infer<typeof insertBuddyNoteSchema>;
export type BuddyNote = typeof buddyNotesTable.$inferSelect;
