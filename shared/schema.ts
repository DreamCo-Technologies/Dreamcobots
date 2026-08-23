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
  "DreamFinance", "DreamRealEstate", "DreamSalesPro", "DreamAIInfra", "DreamRetail",
  "DreamProServices", "DreamData", "DreamGlobal", "DreamAutomation", "DreamEmpire",
  "DreamContent", "DreamTrade", "DreamFlow", "DreamMarket", "CommandCore", "GameTitan",
  "DreamInfluence", "DreamDecision", "DreamOps", "DreamPlanetary", "DreamEntFinance",
  "DreamCustIntel", "DreamLegal", "DreamCyber", "DreamHealth", "DreamEducation",
  "DreamConstruction", "DreamTransport", "DreamFood", "DreamScience", "DreamArts",
  "DreamProtection", "DreamAgriculture", "DreamMaintenance", "DreamProduction", "DreamSocial",
  "DreamAdmin", "DreamCrypto", "DreamPayments", "DreamBizLaunch", "DreamCodeLab", "DreamLoans",
  "DreamPersonalCare", "DreamMilitary", "DreamAgents",
  "DreamResearch", "DreamBenchmark", "DreamKnowledge", "DreamEvolution", "DreamIntegration",
  "DreamReason", "DreamWorld", "DreamVision", "DreamVoice", "DreamHuman", "DreamSecurity",
  "DreamProduct", "DreamOperations", "DreamStrategy", "DreamExperiment", "DreamSimulation",
  "DreamDiscovery", "DreamQuality", "DreamResource", "DreamFuture",
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
