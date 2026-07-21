import { pgTable, text, timestamp, uuid, jsonb, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

// Universal event bus log (e.g. house.detected, revenue.generated, agent.failed)
export const eventsTable = pgTable("events", {
  id: uuid("id").primaryKey().defaultRandom(),
  eventType: text("event_type").notNull(),
  source: text("source"),
  agentId: uuid("agent_id"),
  workflowId: uuid("workflow_id"),
  severity: text("severity").notNull().default("info"),
  payload: jsonb("payload").$type<Record<string, unknown>>().default({}),
  occurredAt: timestamp("occurred_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  typeIdx: index("events_type_idx").on(t.eventType),
  occurredIdx: index("events_occurred_idx").on(t.occurredAt),
  agentIdx: index("events_agent_idx").on(t.agentId),
}));

export const insertEventSchema = createInsertSchema(eventsTable).omit({ id: true, occurredAt: true });
export type InsertEvent = z.infer<typeof insertEventSchema>;
export type Event = typeof eventsTable.$inferSelect;
