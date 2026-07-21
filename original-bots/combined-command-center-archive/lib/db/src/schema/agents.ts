import { pgTable, text, timestamp, uuid, jsonb, integer, real, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const agentsTable = pgTable("agents", {
  id: uuid("id").primaryKey().defaultRandom(),
  slug: text("slug").notNull().unique(),
  name: text("name").notNull(),
  description: text("description"),
  divisionId: uuid("division_id"),
  tier: text("tier").notNull().default("FREE"),
  status: text("status").notNull().default("idle"),
  repoPath: text("repo_path"),
  healthScore: real("health_score").notNull().default(1.0),
  revenueGenerated: real("revenue_generated").notNull().default(0),
  invocations: integer("invocations").notNull().default(0),
  lastHeartbeat: timestamp("last_heartbeat", { withTimezone: true }),
  runtimeConfig: jsonb("runtime_config").$type<Record<string, unknown>>().default({}),
  memoryConfig: jsonb("memory_config").$type<Record<string, unknown>>().default({}),
  costProfile: jsonb("cost_profile").$type<Record<string, unknown>>().default({}),
  permissions: jsonb("permissions").$type<string[]>().default([]),
  models: jsonb("models").$type<string[]>().default([]),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
}, (t) => ({
  statusIdx: index("agents_status_idx").on(t.status),
  divisionIdx: index("agents_division_idx").on(t.divisionId),
  tierIdx: index("agents_tier_idx").on(t.tier),
}));

export const insertAgentSchema = createInsertSchema(agentsTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertAgent = z.infer<typeof insertAgentSchema>;
export type Agent = typeof agentsTable.$inferSelect;
