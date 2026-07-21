import { pgTable, text, timestamp, uuid, jsonb, integer, real, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const botRunsTable = pgTable("bot_runs", {
  id: uuid("id").primaryKey().defaultRandom(),
  botSlug: text("bot_slug").notNull(),
  status: text("status").notNull().default("started"),
  triggeredBy: text("triggered_by"),
  input: jsonb("input").$type<Record<string, unknown>>().default({}),
  output: jsonb("output").$type<Record<string, unknown>>().default({}),
  errorMessage: text("error_message"),
  durationMs: integer("duration_ms"),
  tokensUsed: integer("tokens_used").notNull().default(0),
  costUsd: real("cost_usd").notNull().default(0),
  revenueUsd: real("revenue_usd").notNull().default(0),
  startedAt: timestamp("started_at", { withTimezone: true }).notNull().defaultNow(),
  endedAt: timestamp("ended_at", { withTimezone: true }),
}, (t) => ({
  botIdx: index("bot_runs_bot_idx").on(t.botSlug),
  startedIdx: index("bot_runs_started_idx").on(t.startedAt),
  statusIdx: index("bot_runs_status_idx").on(t.status),
}));

export const insertBotRunSchema = createInsertSchema(botRunsTable).omit({ id: true, startedAt: true });
export type InsertBotRun = z.infer<typeof insertBotRunSchema>;
export type BotRun = typeof botRunsTable.$inferSelect;

export const botEarningsTable = pgTable("bot_earnings", {
  id: uuid("id").primaryKey().defaultRandom(),
  botSlug: text("bot_slug").notNull(),
  source: text("source").notNull(),
  amountUsd: real("amount_usd").notNull(),
  currency: text("currency").notNull().default("usd"),
  stripeChargeId: text("stripe_charge_id"),
  stripeCustomerId: text("stripe_customer_id"),
  metadata: jsonb("metadata").$type<Record<string, unknown>>().default({}),
  occurredAt: timestamp("occurred_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  botIdx: index("bot_earnings_bot_idx").on(t.botSlug),
  occurredIdx: index("bot_earnings_occurred_idx").on(t.occurredAt),
}));

export const insertBotEarningSchema = createInsertSchema(botEarningsTable).omit({ id: true, occurredAt: true });
export type InsertBotEarning = z.infer<typeof insertBotEarningSchema>;
export type BotEarning = typeof botEarningsTable.$inferSelect;

export const botLearningsTable = pgTable("bot_learnings", {
  id: uuid("id").primaryKey().defaultRandom(),
  botSlug: text("bot_slug").notNull(),
  kind: text("kind").notNull(),
  prompt: text("prompt"),
  outcome: text("outcome"),
  reward: real("reward").notNull().default(0),
  embedding: text("embedding"),
  metadata: jsonb("metadata").$type<Record<string, unknown>>().default({}),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  botIdx: index("bot_learnings_bot_idx").on(t.botSlug),
  kindIdx: index("bot_learnings_kind_idx").on(t.kind),
  createdIdx: index("bot_learnings_created_idx").on(t.createdAt),
}));

export const insertBotLearningSchema = createInsertSchema(botLearningsTable).omit({ id: true, createdAt: true });
export type InsertBotLearning = z.infer<typeof insertBotLearningSchema>;
export type BotLearning = typeof botLearningsTable.$inferSelect;
