import { sql } from "drizzle-orm";
import {
  pgTable,
  serial,
  text,
  integer,
  boolean,
  timestamp,
  jsonb,
} from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const DIVISIONS = [
  "DreamFinance",
  "DreamRealEstate",
  "DreamSalesPro",
  "DreamAIInfra",
  "DreamRetail",
  "DreamProServices",
  "DreamData",
  "DreamGlobal",
  "DreamAutomation",
  "DreamEmpire",
  "DreamContent",
  "DreamTrade",
  "DreamFlow",
  "DreamMarket",
  "CommandCore",
  "GameTitan",
] as const;

export type Division = (typeof DIVISIONS)[number];

export const AUTONOMY_MODES = [
  "guided",
  "semi-autonomous",
  "full-autonomy",
] as const;

export type AutonomyMode = (typeof AUTONOMY_MODES)[number];

export const BOT_TIERS = [
  "free",
  "pro",
  "enterprise",
  "elite",
] as const;

export type BotTier = (typeof BOT_TIERS)[number];

export const conversations = pgTable("conversations", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  createdAt: timestamp("created_at").default(sql`CURRENT_TIMESTAMP`).notNull(),
});

export const messages = pgTable("messages", {
  id: serial("id").primaryKey(),
  conversationId: integer("conversation_id")
    .notNull()
    .references(() => conversations.id, { onDelete: "cascade" }),
  role: text("role").notNull(),
  content: text("content").notNull(),
  createdAt: timestamp("created_at").default(sql`CURRENT_TIMESTAMP`).notNull(),
});

export const BOT_OPERATIONAL_MODES = [
  "sandbox",
  "live",
  "offline",
] as const;

export type BotOperationalMode = (typeof BOT_OPERATIONAL_MODES)[number];

export const botProfiles = pgTable("bot_profiles", {
  id: serial("id").primaryKey(),
  slug: text("slug").notNull().unique(),
  displayName: text("display_name").notNull(),
  systemPrompt: text("system_prompt").notNull(),
  traits: jsonb("traits").notNull().default(sql`'{}'::jsonb`),
  isDefault: boolean("is_default").notNull().default(false),
  division: text("division").notNull().default("CommandCore"),
  category: text("category").notNull().default("general"),
  tier: text("tier").notNull().default("free"),
  description: text("description").notNull().default(""),
  capabilities: jsonb("capabilities").notNull().default(sql`'[]'::jsonb`),
  revenueModel: text("revenue_model").notNull().default(""),
  targetUsers: text("target_users").notNull().default(""),
  status: text("bot_status").notNull().default("active"),
  priceRange: text("price_range").notNull().default(""),
  autonomyLevel: text("autonomy_level").notNull().default("guided"),
  operationalMode: text("operational_mode").notNull().default("sandbox"),
});

export const autonomousTasks = pgTable("autonomous_tasks", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  objective: text("objective").notNull(),
  status: text("status").notNull().default("pending"),
  priority: integer("priority").notNull().default(3),
  autonomyMode: text("autonomy_mode").notNull().default("guided"),
  division: text("division").notNull().default("CommandCore"),
  assignedBotId: integer("assigned_bot_id"),
  lastRunAt: timestamp("last_run_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const taskRuns = pgTable("task_runs", {
  id: serial("id").primaryKey(),
  taskId: integer("task_id")
    .notNull()
    .references(() => autonomousTasks.id, { onDelete: "cascade" }),
  status: text("status").notNull(),
  summary: text("summary").notNull().default(""),
  output: jsonb("output").notNull().default(sql`'{}'::jsonb`),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const empireSettings = pgTable("empire_settings", {
  id: serial("id").primaryKey(),
  key: text("key").notNull().unique(),
  value: jsonb("value").notNull().default(sql`'{}'::jsonb`),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const botMetrics = pgTable("bot_metrics", {
  id: serial("id").primaryKey(),
  botId: integer("bot_id").notNull().references(() => botProfiles.id, { onDelete: "cascade" }),
  cpuUsage: integer("cpu_usage").notNull().default(0),
  memoryUsage: integer("memory_usage").notNull().default(0),
  apiCalls: integer("api_calls").notNull().default(0),
  taskDuration: integer("task_duration").notNull().default(0),
  errorsCount: integer("errors_count").notNull().default(0),
  uptime: integer("uptime").notNull().default(100),
  tasksCompleted: integer("tasks_completed").notNull().default(0),
  tasksFailed: integer("tasks_failed").notNull().default(0),
  revenue: integer("revenue").notNull().default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const botErrors = pgTable("bot_errors", {
  id: serial("id").primaryKey(),
  botId: integer("bot_id").notNull().references(() => botProfiles.id, { onDelete: "cascade" }),
  taskId: integer("task_id"),
  errorType: text("error_type").notNull(),
  stackTrace: text("stack_trace").notNull().default(""),
  resolved: boolean("resolved").notNull().default(false),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const botInteractions = pgTable("bot_interactions", {
  id: serial("id").primaryKey(),
  botId: integer("bot_id").notNull().references(() => botProfiles.id, { onDelete: "cascade" }),
  userId: text("user_id").notNull().default("system"),
  inputText: text("input_text").notNull(),
  outputText: text("output_text").notNull().default(""),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const botFinancials = pgTable("bot_financials", {
  id: serial("id").primaryKey(),
  botId: integer("bot_id").notNull().references(() => botProfiles.id, { onDelete: "cascade" }),
  transactionType: text("transaction_type").notNull(),
  amount: integer("amount").notNull().default(0),
  currency: text("currency").notNull().default("USD"),
  status: text("status").notNull().default("pending"),
  metadata: jsonb("metadata").notNull().default(sql`'{}'::jsonb`),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const alertRules = pgTable("alert_rules", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  trigger: text("trigger").notNull(),
  action: text("action").notNull(),
  threshold: integer("threshold").notNull().default(5),
  enabled: boolean("enabled").notNull().default(true),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertConversationSchema = createInsertSchema(conversations).omit({
  id: true,
  createdAt: true,
});

export const insertMessageSchema = createInsertSchema(messages).omit({
  id: true,
  createdAt: true,
});

export const insertBotProfileSchema = createInsertSchema(botProfiles).omit({
  id: true,
});

export const insertAutonomousTaskSchema = createInsertSchema(autonomousTasks).omit({
  id: true,
  createdAt: true,
  lastRunAt: true,
});

export const insertTaskRunSchema = createInsertSchema(taskRuns).omit({
  id: true,
  createdAt: true,
});

export const insertEmpireSettingSchema = createInsertSchema(empireSettings).omit({
  id: true,
  updatedAt: true,
});

export type Conversation = typeof conversations.$inferSelect;
export type InsertConversation = z.infer<typeof insertConversationSchema>;

export type Message = typeof messages.$inferSelect;
export type InsertMessage = z.infer<typeof insertMessageSchema>;

export type BotProfile = typeof botProfiles.$inferSelect;
export type InsertBotProfile = z.infer<typeof insertBotProfileSchema>;

export type AutonomousTask = typeof autonomousTasks.$inferSelect;
export type InsertAutonomousTask = z.infer<typeof insertAutonomousTaskSchema>;

export type TaskRun = typeof taskRuns.$inferSelect;
export type InsertTaskRun = z.infer<typeof insertTaskRunSchema>;

export type EmpireSetting = typeof empireSettings.$inferSelect;
export type InsertEmpireSetting = z.infer<typeof insertEmpireSettingSchema>;

export type CreateConversationRequest = InsertConversation;
export type CreateMessageRequest = { content: string; botSlug?: string };
export type CreateMessageResponse = { message: Message; assistantMessage?: Message };

export type CreateBotProfileRequest = InsertBotProfile;
export type UpdateBotProfileRequest = Partial<InsertBotProfile>;

export type CreateAutonomousTaskRequest = InsertAutonomousTask;
export type UpdateAutonomousTaskRequest = Partial<InsertAutonomousTask>;

export type CreateTaskRunRequest = InsertTaskRun;

export type ConversationResponse = Conversation;
export type MessageResponse = Message;
export type BotProfileResponse = BotProfile;
export type AutonomousTaskResponse = AutonomousTask;
export type TaskRunResponse = TaskRun;

export const insertBotMetricSchema = createInsertSchema(botMetrics).omit({ id: true, createdAt: true });
export const insertBotErrorSchema = createInsertSchema(botErrors).omit({ id: true, createdAt: true });
export const insertBotInteractionSchema = createInsertSchema(botInteractions).omit({ id: true, createdAt: true });
export const insertBotFinancialSchema = createInsertSchema(botFinancials).omit({ id: true, createdAt: true });
export const insertAlertRuleSchema = createInsertSchema(alertRules).omit({ id: true, createdAt: true });

export type BotMetric = typeof botMetrics.$inferSelect;
export type InsertBotMetric = z.infer<typeof insertBotMetricSchema>;
export type BotError = typeof botErrors.$inferSelect;
export type InsertBotError = z.infer<typeof insertBotErrorSchema>;
export type BotInteraction = typeof botInteractions.$inferSelect;
export type InsertBotInteraction = z.infer<typeof insertBotInteractionSchema>;
export type BotFinancial = typeof botFinancials.$inferSelect;
export type InsertBotFinancial = z.infer<typeof insertBotFinancialSchema>;
export type AlertRule = typeof alertRules.$inferSelect;
export type InsertAlertRule = z.infer<typeof insertAlertRuleSchema>;

export const TASK_STATUSES = [
  "pending",
  "running",
  "paused",
  "complete",
  "failed",
] as const;

export type TaskStatus = (typeof TASK_STATUSES)[number];

export const BOT_CATEGORIES = [
  "general", "trading", "portfolio", "analytics", "research",
  "sales", "marketing", "infrastructure", "automation", "content",
  "security", "compliance", "gaming", "real-estate", "retail",
  "finance", "data", "global", "services", "system",
] as const;

export type BotCategory = (typeof BOT_CATEGORIES)[number];

export interface DivisionStats {
  division: Division;
  botCount: number;
  activeTasks: number;
  completedTasks: number;
  revenue: string;
}

export interface EmpireOverview {
  totalBots: number;
  totalDivisions: number;
  activeTasks: number;
  completedTasks: number;
  autonomyMode: AutonomyMode;
  divisions: DivisionStats[];
}

export interface BotHealthSummary {
  totalBots: number;
  activeBots: number;
  pausedBots: number;
  totalErrors: number;
  avgUptime: number;
  totalRevenue: number;
  totalApiCalls: number;
  totalTasksCompleted: number;
}

export interface DivisionMetrics {
  division: string;
  botCount: number;
  totalRevenue: number;
  totalErrors: number;
  avgUptime: number;
  activeBots: number;
}

export const DEAL_TYPES = ["real_estate", "car"] as const;
export type DealType = (typeof DEAL_TYPES)[number];

export const DEAL_STATUSES = ["green", "yellow", "red"] as const;
export type DealStatus = (typeof DEAL_STATUSES)[number];

export const deals = pgTable("deals", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  dealType: text("deal_type").notNull().default("real_estate"),
  status: text("status").notNull().default("red"),
  inputs: jsonb("inputs").notNull().default(sql`'{}'::jsonb`),
  results: jsonb("results").notNull().default(sql`'{}'::jsonb`),
  netProfit: integer("net_profit").notNull().default(0),
  roi: integer("roi").notNull().default(0),
  capitalEfficiency: integer("capital_efficiency").notNull().default(0),
  daysHeld: integer("days_held").notNull().default(0),
  cashInvested: integer("cash_invested").notNull().default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertDealSchema = createInsertSchema(deals).omit({ id: true, createdAt: true });
export type Deal = typeof deals.$inferSelect;
export type InsertDeal = z.infer<typeof insertDealSchema>;

export const ALERT_TRIGGERS = [
  "task_fail_consecutive",
  "cpu_high",
  "unauthorized_access",
  "model_drift",
  "high_error_rate",
  "revenue_drop",
  "bot_offline",
] as const;

export type AlertTrigger = (typeof ALERT_TRIGGERS)[number];
