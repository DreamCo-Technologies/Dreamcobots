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

export const TASK_STATUSES = [
  "pending",
  "running",
  "paused",
  "complete",
  "failed",
] as const;

export type TaskStatus = (typeof TASK_STATUSES)[number];

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
