import { sql } from "drizzle-orm";
import { pgTable, serial, text, integer, boolean, timestamp, jsonb, } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
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
    "DreamInfluence",
    "DreamDecision",
    "DreamOps",
    "DreamPlanetary",
    "DreamEntFinance",
    "DreamCustIntel",
    "DreamLegal",
    "DreamCyber",
    "DreamHealth",
    "DreamEducation",
    "DreamConstruction",
    "DreamTransport",
    "DreamFood",
    "DreamScience",
    "DreamArts",
    "DreamProtection",
    "DreamAgriculture",
    "DreamMaintenance",
    "DreamProduction",
    "DreamSocial",
    "DreamAdmin",
    "DreamCrypto",
    "DreamPayments",
    "DreamBizLaunch",
    "DreamCodeLab",
    "DreamLoans",
    "DreamPersonalCare",
    "DreamMilitary",
    "DreamAgents",
];
export const AUTONOMY_MODES = [
    "guided",
    "semi-autonomous",
    "full-autonomy",
];
export const BOT_TIERS = [
    "free",
    "pro",
    "enterprise",
    "elite",
];
export const conversations = pgTable("conversations", {
    id: serial("id").primaryKey(),
    title: text("title").notNull(),
    createdAt: timestamp("created_at").default(sql `CURRENT_TIMESTAMP`).notNull(),
});
export const messages = pgTable("messages", {
    id: serial("id").primaryKey(),
    conversationId: integer("conversation_id")
        .notNull()
        .references(() => conversations.id, { onDelete: "cascade" }),
    role: text("role").notNull(),
    content: text("content").notNull(),
    createdAt: timestamp("created_at").default(sql `CURRENT_TIMESTAMP`).notNull(),
});
export const BOT_OPERATIONAL_MODES = [
    "sandbox",
    "live",
    "offline",
];
export const botProfiles = pgTable("bot_profiles", {
    id: serial("id").primaryKey(),
    slug: text("slug").notNull().unique(),
    displayName: text("display_name").notNull(),
    systemPrompt: text("system_prompt").notNull(),
    traits: jsonb("traits").notNull().default(sql `'{}'::jsonb`),
    isDefault: boolean("is_default").notNull().default(false),
    division: text("division").notNull().default("CommandCore"),
    category: text("category").notNull().default("general"),
    tier: text("tier").notNull().default("free"),
    description: text("description").notNull().default(""),
    capabilities: jsonb("capabilities").notNull().default(sql `'[]'::jsonb`),
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
    output: jsonb("output").notNull().default(sql `'{}'::jsonb`),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const empireSettings = pgTable("empire_settings", {
    id: serial("id").primaryKey(),
    key: text("key").notNull().unique(),
    value: jsonb("value").notNull().default(sql `'{}'::jsonb`),
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
    metadata: jsonb("metadata").notNull().default(sql `'{}'::jsonb`),
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
export const insertBotMetricSchema = createInsertSchema(botMetrics).omit({ id: true, createdAt: true });
export const insertBotErrorSchema = createInsertSchema(botErrors).omit({ id: true, createdAt: true });
export const insertBotInteractionSchema = createInsertSchema(botInteractions).omit({ id: true, createdAt: true });
export const insertBotFinancialSchema = createInsertSchema(botFinancials).omit({ id: true, createdAt: true });
export const insertAlertRuleSchema = createInsertSchema(alertRules).omit({ id: true, createdAt: true });
export const TASK_STATUSES = [
    "pending",
    "running",
    "paused",
    "complete",
    "failed",
];
export const BOT_CATEGORIES = [
    "general", "trading", "portfolio", "analytics", "research",
    "sales", "marketing", "infrastructure", "automation", "content",
    "security", "compliance", "gaming", "real-estate", "retail",
    "finance", "data", "global", "services", "system",
];
export const DIVISION_RUNTIME_HEALTH = ["healthy", "warning", "critical"];
export const DIVISION_LEARNING_STATUS = ["warming", "learning", "optimized"];
export const DELEGATION_RISK_LEVELS = ["low", "medium", "high"];
export const DELEGATION_STATUSES = ["draft", "pending", "in_progress", "awaiting_approval", "approved", "rejected", "complete"];
export const DEAL_TYPES = ["real_estate", "car"];
export const DEAL_STATUSES = ["green", "yellow", "red"];
export const deals = pgTable("deals", {
    id: serial("id").primaryKey(),
    name: text("name").notNull(),
    dealType: text("deal_type").notNull().default("real_estate"),
    status: text("status").notNull().default("red"),
    inputs: jsonb("inputs").notNull().default(sql `'{}'::jsonb`),
    results: jsonb("results").notNull().default(sql `'{}'::jsonb`),
    netProfit: integer("net_profit").notNull().default(0),
    roi: integer("roi").notNull().default(0),
    capitalEfficiency: integer("capital_efficiency").notNull().default(0),
    daysHeld: integer("days_held").notNull().default(0),
    cashInvested: integer("cash_invested").notNull().default(0),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const insertDealSchema = createInsertSchema(deals).omit({ id: true, createdAt: true });
export const DEBUG_EVENT_CATEGORIES = [
    "syntax_error", "runtime_crash", "api_failure", "auth_error",
    "logic_bug", "performance_issue", "ux_friction", "revenue_leak",
    "security_risk", "infinite_loop", "model_drift", "cost_explosion",
];
export const DEBUG_EVENT_STATUSES = ["open", "investigating", "resolved", "ignored"];
export const AUTO_FIX_STATUSES = ["queued", "applied", "rejected"];
export const debugEvents = pgTable("debug_events", {
    id: serial("id").primaryKey(),
    botId: integer("bot_id").references(() => botProfiles.id, { onDelete: "cascade" }),
    taskId: integer("task_id"),
    category: text("category").notNull().default("runtime_crash"),
    severity: integer("severity").notNull().default(5),
    revenueImpact: integer("revenue_impact").notNull().default(0),
    fixPriority: integer("fix_priority").notNull().default(5),
    status: text("status").notNull().default("open"),
    summary: text("summary").notNull(),
    details: jsonb("details").notNull().default(sql `'{}'::jsonb`),
    resolution: text("resolution"),
    resolvedAt: timestamp("resolved_at"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const autoFixes = pgTable("auto_fixes", {
    id: serial("id").primaryKey(),
    debugEventId: integer("debug_event_id").references(() => debugEvents.id, { onDelete: "cascade" }),
    botId: integer("bot_id").references(() => botProfiles.id, { onDelete: "cascade" }),
    confidence: integer("confidence").notNull().default(0),
    status: text("status").notNull().default("queued"),
    patchSummary: text("patch_summary").notNull(),
    codeBefore: text("code_before").notNull().default(""),
    codeAfter: text("code_after").notNull().default(""),
    appliedAt: timestamp("applied_at"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const revenueLeaks = pgTable("revenue_leaks", {
    id: serial("id").primaryKey(),
    botId: integer("bot_id").references(() => botProfiles.id, { onDelete: "cascade" }),
    debugEventId: integer("debug_event_id").references(() => debugEvents.id, { onDelete: "cascade" }),
    leakType: text("leak_type").notNull(),
    impactEstimate: integer("impact_estimate").notNull().default(0),
    status: text("status").notNull().default("open"),
    notes: text("notes").notNull().default(""),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const securityScans = pgTable("security_scans", {
    id: serial("id").primaryKey(),
    botId: integer("bot_id").references(() => botProfiles.id, { onDelete: "cascade" }),
    debugEventId: integer("debug_event_id").references(() => debugEvents.id, { onDelete: "cascade" }),
    scanType: text("scan_type").notNull(),
    severity: integer("severity").notNull().default(5),
    status: text("status").notNull().default("open"),
    finding: text("finding").notNull(),
    mitigation: text("mitigation").notNull().default(""),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const insertDebugEventSchema = createInsertSchema(debugEvents).omit({ id: true, createdAt: true, resolvedAt: true });
export const insertAutoFixSchema = createInsertSchema(autoFixes).omit({ id: true, createdAt: true, appliedAt: true });
export const insertRevenueLeakSchema = createInsertSchema(revenueLeaks).omit({ id: true, createdAt: true });
export const insertSecurityScanSchema = createInsertSchema(securityScans).omit({ id: true, createdAt: true });
export const ALERT_TRIGGERS = [
    "task_fail_consecutive",
    "cpu_high",
    "unauthorized_access",
    "model_drift",
    "high_error_rate",
    "revenue_drop",
    "bot_offline",
];
export const formulas = pgTable("formulas", {
    id: serial("id").primaryKey(),
    name: text("name").notNull(),
    category: text("category").notNull(),
    description: text("description").notNull(),
    formula: text("formula").notNull(),
    variables: jsonb("variables").notNull().default(sql `'[]'::jsonb`),
    target: text("target").notNull().default(""),
    tags: jsonb("tags").notNull().default(sql `'[]'::jsonb`),
    isSystem: boolean("is_system").notNull().default(false),
});
export const insertFormulaSchema = createInsertSchema(formulas).omit({ id: true });
export const PLATFORM_TYPES = [
    "telegram", "slack", "sms", "webhook", "api", "discord", "zoom", "roku", "mobile", "gaming",
];
export const platformConnections = pgTable("platform_connections", {
    id: serial("id").primaryKey(),
    platform: text("platform").notNull(),
    name: text("name").notNull(),
    webhookUrl: text("webhook_url").notNull().default(""),
    apiKey: text("api_key").notNull().default(""),
    status: text("status").notNull().default("disconnected"),
    config: jsonb("config").notNull().default(sql `'{}'::jsonb`),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const insertPlatformConnectionSchema = createInsertSchema(platformConnections).omit({ id: true, createdAt: true });
export const plugins = pgTable("plugins", {
    id: serial("id").primaryKey(),
    name: text("name").notNull(),
    slug: text("slug").notNull().unique(),
    description: text("description").notNull(),
    category: text("category").notNull().default("general"),
    author: text("author").notNull().default("DreamCo"),
    version: text("version").notNull().default("1.0.0"),
    downloads: integer("downloads").notNull().default(0),
    rating: integer("rating").notNull().default(0),
    status: text("status").notNull().default("published"),
    config: jsonb("config").notNull().default(sql `'{}'::jsonb`),
    capabilities: jsonb("capabilities").notNull().default(sql `'[]'::jsonb`),
    installed: boolean("installed").notNull().default(false),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const insertPluginSchema = createInsertSchema(plugins).omit({ id: true, createdAt: true });
export const botMemory = pgTable("bot_memory", {
    id: serial("id").primaryKey(),
    botId: integer("bot_id").references(() => botProfiles.id, { onDelete: "cascade" }),
    key: text("key").notNull(),
    value: text("value").notNull(),
    category: text("category").notNull().default("general"),
    pinned: boolean("pinned").notNull().default(false),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const insertBotMemorySchema = createInsertSchema(botMemory).omit({ id: true, createdAt: true });
export const systemSnapshots = pgTable("system_snapshots", {
    id: serial("id").primaryKey(),
    name: text("name").notNull(),
    description: text("description").notNull().default(""),
    snapshotData: jsonb("snapshot_data").notNull().default(sql `'{}'::jsonb`),
    botCount: integer("bot_count").notNull().default(0),
    taskCount: integer("task_count").notNull().default(0),
    settingsCount: integer("settings_count").notNull().default(0),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const insertSystemSnapshotSchema = createInsertSchema(systemSnapshots).omit({ id: true, createdAt: true });
export const costEvents = pgTable("cost_events", {
    id: serial("id").primaryKey(),
    botId: integer("bot_id").references(() => botProfiles.id, { onDelete: "cascade" }),
    service: text("service").notNull().default("openai"),
    tokens: integer("tokens").notNull().default(0),
    cost: integer("cost").notNull().default(0),
    endpoint: text("endpoint").notNull().default(""),
    createdAt: timestamp("created_at").defaultNow().notNull(),
});
export const insertCostEventSchema = createInsertSchema(costEvents).omit({ id: true, createdAt: true });
