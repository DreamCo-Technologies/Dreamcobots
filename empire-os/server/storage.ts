import { db } from "./db";
import {
  botProfiles,
  conversations,
  messages,
  autonomousTasks,
  taskRuns,
  empireSettings,
  botMetrics,
  botErrors,
  botInteractions,
  botFinancials,
  alertRules,
  deals,
  debugEvents,
  autoFixes,
  revenueLeaks,
  securityScans,
  formulas,
  type BotProfile,
  type InsertBotProfile,
  type AutonomousTask,
  type InsertAutonomousTask,
  type TaskRun,
  type EmpireSetting,
  type InsertEmpireSetting,
  type BotMetric,
  type InsertBotMetric,
  type BotError,
  type InsertBotError,
  type BotInteraction,
  type InsertBotInteraction,
  type BotFinancial,
  type InsertBotFinancial,
  type AlertRule,
  type InsertAlertRule,
  type BotHealthSummary,
  type Deal,
  type InsertDeal,
  type DebugEvent,
  type InsertDebugEvent,
  type AutoFix,
  type InsertAutoFix,
  type RevenueLeak,
  type InsertRevenueLeak,
  type SecurityScan,
  type InsertSecurityScan,
  type DebugOverview,
  type Formula,
  type InsertFormula,
  platformConnections,
  plugins,
  botMemory,
  systemSnapshots,
  costEvents,
  type PlatformConnection,
  type InsertPlatformConnection,
  type Plugin,
  type InsertPlugin,
  type BotMemory,
  type InsertBotMemory,
  type SystemSnapshot,
  type InsertSystemSnapshot,
  type CostEvent,
  type InsertCostEvent,
} from "@shared/schema";
import { and, desc, eq, ne, sql, count, inArray, sum, avg } from "drizzle-orm";

export interface IStorage {
  listBotProfiles(): Promise<BotProfile[]>;
  getBotProfileById(id: number): Promise<BotProfile | undefined>;
  listBotsByDivision(division: string): Promise<BotProfile[]>;
  createBotProfile(input: InsertBotProfile): Promise<BotProfile>;
  updateBotProfile(id: number, updates: Partial<InsertBotProfile>): Promise<BotProfile | undefined>;
  setDefaultBotProfile(id: number): Promise<BotProfile | undefined>;
  getDefaultBotProfile(): Promise<BotProfile | undefined>;
  getBotProfileBySlug(slug: string): Promise<BotProfile | undefined>;
  getBotCountByDivision(): Promise<{ division: string; count: number }[]>;

  listConversations(): Promise<(typeof conversations.$inferSelect)[]>;
  getConversation(id: number): Promise<(typeof conversations.$inferSelect) | undefined>;
  createConversation(title: string): Promise<(typeof conversations.$inferSelect)>;
  deleteConversation(id: number): Promise<void>;
  getMessages(conversationId: number): Promise<(typeof messages.$inferSelect)[]>;
  createMessage(conversationId: number, role: "user" | "assistant", content: string): Promise<(typeof messages.$inferSelect)>;

  listTasks(): Promise<AutonomousTask[]>;
  listTasksByDivision(division: string): Promise<AutonomousTask[]>;
  createTask(input: InsertAutonomousTask & { status?: string; priority?: number; autonomyMode?: string; division?: string; assignedBotId?: number }): Promise<AutonomousTask>;
  updateTask(id: number, updates: Partial<InsertAutonomousTask> & { status?: string; priority?: number; autonomyMode?: string }): Promise<AutonomousTask | undefined>;
  deleteTask(id: number): Promise<void>;
  createTaskRun(taskId: number, status: string, summary: string, output: unknown): Promise<TaskRun>;
  listTaskRuns(taskId: number): Promise<TaskRun[]>;

  getSetting(key: string): Promise<EmpireSetting | undefined>;
  upsertSetting(key: string, value: unknown): Promise<EmpireSetting>;

  createBotMetric(input: InsertBotMetric): Promise<BotMetric>;
  listBotMetrics(botId: number): Promise<BotMetric[]>;
  getLatestBotMetrics(): Promise<BotMetric[]>;
  getBotHealthSummary(): Promise<BotHealthSummary>;

  createBotError(input: InsertBotError): Promise<BotError>;
  listBotErrors(botId?: number): Promise<BotError[]>;
  resolveError(id: number): Promise<BotError | undefined>;

  createBotInteraction(input: InsertBotInteraction): Promise<BotInteraction>;
  listBotInteractions(botId?: number, limit?: number): Promise<BotInteraction[]>;

  createBotFinancial(input: InsertBotFinancial): Promise<BotFinancial>;
  listBotFinancials(botId?: number): Promise<BotFinancial[]>;

  listAlertRules(): Promise<AlertRule[]>;
  createAlertRule(input: InsertAlertRule): Promise<AlertRule>;
  toggleAlertRule(id: number, enabled: boolean): Promise<AlertRule | undefined>;

  listDeals(): Promise<Deal[]>;
  getDeal(id: number): Promise<Deal | undefined>;
  createDeal(input: InsertDeal): Promise<Deal>;
  updateDeal(id: number, updates: Partial<InsertDeal>): Promise<Deal | undefined>;
  deleteDeal(id: number): Promise<void>;
  getDealKpis(): Promise<{
    totalDeals: number;
    totalNetProfit: number;
    avgRoi: number;
    avgCapitalEfficiency: number;
    greenDeals: number;
    yellowDeals: number;
    redDeals: number;
  }>;

  getBotProfile(id: number): Promise<BotProfile | undefined>;

  createDebugEvent(input: InsertDebugEvent): Promise<DebugEvent>;
  listDebugEvents(status?: string, botId?: number): Promise<DebugEvent[]>;
  resolveDebugEvent(id: number, resolution: string): Promise<DebugEvent | undefined>;
  getDebugEvent(id: number): Promise<DebugEvent | undefined>;

  createAutoFix(input: InsertAutoFix): Promise<AutoFix>;
  listAutoFixes(status?: string): Promise<AutoFix[]>;
  applyAutoFix(id: number): Promise<AutoFix | undefined>;
  rejectAutoFix(id: number): Promise<AutoFix | undefined>;

  createRevenueLeak(input: InsertRevenueLeak): Promise<RevenueLeak>;
  listRevenueLeaks(status?: string): Promise<RevenueLeak[]>;
  resolveRevenueLeak(id: number, notes: string): Promise<RevenueLeak | undefined>;

  createSecurityScan(input: InsertSecurityScan): Promise<SecurityScan>;
  listSecurityScans(status?: string): Promise<SecurityScan[]>;
  remediateSecurityScan(id: number, mitigation: string): Promise<SecurityScan | undefined>;

  getDebugOverview(): Promise<DebugOverview>;

  listFormulas(): Promise<Formula[]>;
  getFormula(id: number): Promise<Formula | undefined>;
  createFormula(input: InsertFormula): Promise<Formula>;
  updateFormula(id: number, updates: Partial<InsertFormula>): Promise<Formula | undefined>;
  deleteFormula(id: number): Promise<void>;

  listPlatformConnections(): Promise<PlatformConnection[]>;
  createPlatformConnection(input: InsertPlatformConnection): Promise<PlatformConnection>;
  updatePlatformConnection(id: number, updates: Partial<InsertPlatformConnection>): Promise<PlatformConnection | undefined>;
  deletePlatformConnection(id: number): Promise<void>;

  listPlugins(): Promise<Plugin[]>;
  getPlugin(id: number): Promise<Plugin | undefined>;
  createPlugin(input: InsertPlugin): Promise<Plugin>;
  updatePlugin(id: number, updates: Partial<InsertPlugin>): Promise<Plugin | undefined>;
  deletePlugin(id: number): Promise<void>;
  incrementPluginDownloads(id: number): Promise<Plugin | undefined>;

  listBotMemory(botId: number): Promise<BotMemory[]>;
  createBotMemory(input: InsertBotMemory): Promise<BotMemory>;
  deleteBotMemory(id: number): Promise<void>;

  listSystemSnapshots(): Promise<SystemSnapshot[]>;
  createSystemSnapshot(input: InsertSystemSnapshot): Promise<SystemSnapshot>;
  getSystemSnapshot(id: number): Promise<SystemSnapshot | undefined>;
  deleteSystemSnapshot(id: number): Promise<void>;

  createCostEvent(input: InsertCostEvent): Promise<CostEvent>;
  listCostEvents(limit?: number): Promise<CostEvent[]>;
  getCostSummary(): Promise<{ totalTokens: number; totalCost: number; eventCount: number }>;
}

export class DatabaseStorage implements IStorage {
  async listBotProfiles(): Promise<BotProfile[]> {
    return await db.select().from(botProfiles).orderBy(botProfiles.id);
  }

  async getBotProfileById(id: number): Promise<BotProfile | undefined> {
    const [profile] = await db.select().from(botProfiles).where(eq(botProfiles.id, id));
    return profile;
  }

  async listBotsByDivision(division: string): Promise<BotProfile[]> {
    return await db.select().from(botProfiles).where(eq(botProfiles.division, division)).orderBy(botProfiles.id);
  }

  async createBotProfile(input: InsertBotProfile): Promise<BotProfile> {
    const [created] = await db.insert(botProfiles).values(input).returning();
    return created;
  }

  async updateBotProfile(id: number, updates: Partial<InsertBotProfile>): Promise<BotProfile | undefined> {
    const [updated] = await db
      .update(botProfiles)
      .set(updates)
      .where(eq(botProfiles.id, id))
      .returning();
    return updated;
  }

  async setDefaultBotProfile(id: number): Promise<BotProfile | undefined> {
    await db.update(botProfiles).set({ isDefault: false }).where(ne(botProfiles.id, id));
    const [updated] = await db
      .update(botProfiles)
      .set({ isDefault: true })
      .where(eq(botProfiles.id, id))
      .returning();
    return updated;
  }

  async getDefaultBotProfile(): Promise<BotProfile | undefined> {
    const [profile] = await db.select().from(botProfiles).where(eq(botProfiles.isDefault, true));
    return profile;
  }

  async getBotProfileBySlug(slug: string): Promise<BotProfile | undefined> {
    const [profile] = await db.select().from(botProfiles).where(eq(botProfiles.slug, slug));
    return profile;
  }

  async getBotCountByDivision(): Promise<{ division: string; count: number }[]> {
    const result = await db
      .select({ division: botProfiles.division, count: count() })
      .from(botProfiles)
      .groupBy(botProfiles.division)
      .orderBy(botProfiles.division);
    return result.map(r => ({ division: r.division, count: Number(r.count) }));
  }

  async listConversations() {
    return await db.select().from(conversations).orderBy(desc(conversations.createdAt));
  }

  async getConversation(id: number) {
    const [conv] = await db.select().from(conversations).where(eq(conversations.id, id));
    return conv;
  }

  async createConversation(title: string) {
    const [conv] = await db
      .insert(conversations)
      .values({ title })
      .returning();
    return conv;
  }

  async deleteConversation(id: number): Promise<void> {
    await db.delete(messages).where(eq(messages.conversationId, id));
    await db.delete(conversations).where(eq(conversations.id, id));
  }

  async getMessages(conversationId: number) {
    return await db
      .select()
      .from(messages)
      .where(eq(messages.conversationId, conversationId))
      .orderBy(messages.createdAt);
  }

  async createMessage(
    conversationId: number,
    role: "user" | "assistant",
    content: string,
  ) {
    const [msg] = await db
      .insert(messages)
      .values({ conversationId, role, content })
      .returning();
    return msg;
  }

  async listTasks(): Promise<AutonomousTask[]> {
    return await db.select().from(autonomousTasks).orderBy(desc(autonomousTasks.createdAt));
  }

  async listTasksByDivision(division: string): Promise<AutonomousTask[]> {
    return await db.select().from(autonomousTasks).where(eq(autonomousTasks.division, division)).orderBy(desc(autonomousTasks.createdAt));
  }

  async createTask(input: InsertAutonomousTask & { status?: string; priority?: number; autonomyMode?: string; division?: string; assignedBotId?: number }): Promise<AutonomousTask> {
    const [task] = await db
      .insert(autonomousTasks)
      .values({
        title: input.title,
        objective: input.objective,
        status: input.status ?? "pending",
        priority: input.priority ?? 3,
        autonomyMode: input.autonomyMode ?? "guided",
        division: input.division ?? "CommandCore",
        assignedBotId: input.assignedBotId ?? null,
      })
      .returning();
    return task;
  }

  async updateTask(id: number, updates: Partial<InsertAutonomousTask> & { status?: string; priority?: number; autonomyMode?: string }): Promise<AutonomousTask | undefined> {
    const [task] = await db
      .update(autonomousTasks)
      .set(updates)
      .where(eq(autonomousTasks.id, id))
      .returning();
    return task;
  }

  async deleteTask(id: number): Promise<void> {
    await db.delete(taskRuns).where(eq(taskRuns.taskId, id));
    await db.delete(autonomousTasks).where(eq(autonomousTasks.id, id));
  }

  async createTaskRun(taskId: number, status: string, summary: string, output: unknown): Promise<TaskRun> {
    const [run] = await db
      .insert(taskRuns)
      .values({ taskId, status, summary, output })
      .returning();
    return run;
  }

  async listTaskRuns(taskId: number): Promise<TaskRun[]> {
    return await db.select().from(taskRuns).where(eq(taskRuns.taskId, taskId)).orderBy(desc(taskRuns.createdAt));
  }

  async getSetting(key: string): Promise<EmpireSetting | undefined> {
    const [setting] = await db.select().from(empireSettings).where(eq(empireSettings.key, key));
    return setting;
  }

  async upsertSetting(key: string, value: unknown): Promise<EmpireSetting> {
    const existing = await this.getSetting(key);
    if (existing) {
      const [updated] = await db
        .update(empireSettings)
        .set({ value, updatedAt: new Date() })
        .where(eq(empireSettings.key, key))
        .returning();
      return updated;
    }
    const [created] = await db
      .insert(empireSettings)
      .values({ key, value })
      .returning();
    return created;
  }

  async createBotMetric(input: InsertBotMetric): Promise<BotMetric> {
    const [created] = await db.insert(botMetrics).values(input).returning();
    return created;
  }

  async listBotMetrics(botId: number): Promise<BotMetric[]> {
    return await db.select().from(botMetrics).where(eq(botMetrics.botId, botId)).orderBy(desc(botMetrics.createdAt));
  }

  async getLatestBotMetrics(): Promise<BotMetric[]> {
    return await db.select().from(botMetrics).orderBy(desc(botMetrics.createdAt)).limit(100);
  }

  async getBotHealthSummary(): Promise<BotHealthSummary> {
    const bots = await this.listBotProfiles();
    const metrics = await this.getLatestBotMetrics();
    const errors = await db.select({ count: count() }).from(botErrors).where(eq(botErrors.resolved, false));
    const totalErrors = Number(errors[0]?.count ?? 0);

    const activeBots = bots.filter(b => b.status === "active").length;
    const pausedBots = bots.filter(b => b.status === "paused").length;

    let avgUptime = 100;
    let totalRevenue = 0;
    let totalApiCalls = 0;
    let totalTasksCompleted = 0;

    if (metrics.length > 0) {
      avgUptime = Math.round(metrics.reduce((s, m) => s + m.uptime, 0) / metrics.length);
      totalRevenue = metrics.reduce((s, m) => s + m.revenue, 0);
      totalApiCalls = metrics.reduce((s, m) => s + m.apiCalls, 0);
      totalTasksCompleted = metrics.reduce((s, m) => s + m.tasksCompleted, 0);
    }

    return {
      totalBots: bots.length,
      activeBots,
      pausedBots,
      totalErrors,
      avgUptime,
      totalRevenue,
      totalApiCalls,
      totalTasksCompleted,
    };
  }

  async createBotError(input: InsertBotError): Promise<BotError> {
    const [created] = await db.insert(botErrors).values(input).returning();
    return created;
  }

  async listBotErrors(botId?: number): Promise<BotError[]> {
    if (botId) {
      return await db.select().from(botErrors).where(eq(botErrors.botId, botId)).orderBy(desc(botErrors.createdAt)).limit(100);
    }
    return await db.select().from(botErrors).orderBy(desc(botErrors.createdAt)).limit(100);
  }

  async resolveError(id: number): Promise<BotError | undefined> {
    const [updated] = await db.update(botErrors).set({ resolved: true }).where(eq(botErrors.id, id)).returning();
    return updated;
  }

  async createBotInteraction(input: InsertBotInteraction): Promise<BotInteraction> {
    const [created] = await db.insert(botInteractions).values(input).returning();
    return created;
  }

  async listBotInteractions(botId?: number, limit = 50): Promise<BotInteraction[]> {
    if (botId) {
      return await db.select().from(botInteractions).where(eq(botInteractions.botId, botId)).orderBy(desc(botInteractions.createdAt)).limit(limit);
    }
    return await db.select().from(botInteractions).orderBy(desc(botInteractions.createdAt)).limit(limit);
  }

  async createBotFinancial(input: InsertBotFinancial): Promise<BotFinancial> {
    const [created] = await db.insert(botFinancials).values(input).returning();
    return created;
  }

  async listBotFinancials(botId?: number): Promise<BotFinancial[]> {
    if (botId) {
      return await db.select().from(botFinancials).where(eq(botFinancials.botId, botId)).orderBy(desc(botFinancials.createdAt)).limit(100);
    }
    return await db.select().from(botFinancials).orderBy(desc(botFinancials.createdAt)).limit(100);
  }

  async listAlertRules(): Promise<AlertRule[]> {
    return await db.select().from(alertRules).orderBy(alertRules.id);
  }

  async createAlertRule(input: InsertAlertRule): Promise<AlertRule> {
    const [created] = await db.insert(alertRules).values(input).returning();
    return created;
  }

  async toggleAlertRule(id: number, enabled: boolean): Promise<AlertRule | undefined> {
    const [updated] = await db.update(alertRules).set({ enabled }).where(eq(alertRules.id, id)).returning();
    return updated;
  }

  async listDeals(): Promise<Deal[]> {
    return await db.select().from(deals).orderBy(desc(deals.createdAt));
  }

  async getDeal(id: number): Promise<Deal | undefined> {
    const [deal] = await db.select().from(deals).where(eq(deals.id, id));
    return deal;
  }

  async createDeal(input: InsertDeal): Promise<Deal> {
    const [created] = await db.insert(deals).values(input).returning();
    return created;
  }

  async updateDeal(id: number, updates: Partial<InsertDeal>): Promise<Deal | undefined> {
    const [updated] = await db.update(deals).set(updates).where(eq(deals.id, id)).returning();
    return updated;
  }

  async deleteDeal(id: number): Promise<void> {
    await db.delete(deals).where(eq(deals.id, id));
  }

  async getDealKpis() {
    const allDeals = await this.listDeals();
    const totalDeals = allDeals.length;
    const totalNetProfit = allDeals.reduce((s, d) => s + d.netProfit, 0);
    const avgRoi = totalDeals > 0 ? Math.round(allDeals.reduce((s, d) => s + d.roi, 0) / totalDeals) : 0;
    const avgCapitalEfficiency = totalDeals > 0 ? Math.round(allDeals.reduce((s, d) => s + d.capitalEfficiency, 0) / totalDeals) : 0;
    const greenDeals = allDeals.filter(d => d.status === "green").length;
    const yellowDeals = allDeals.filter(d => d.status === "yellow").length;
    const redDeals = allDeals.filter(d => d.status === "red").length;
    return { totalDeals, totalNetProfit, avgRoi, avgCapitalEfficiency, greenDeals, yellowDeals, redDeals };
  }

  async getBotProfile(id: number): Promise<BotProfile | undefined> {
    return this.getBotProfileById(id);
  }

  async createDebugEvent(input: InsertDebugEvent): Promise<DebugEvent> {
    const [created] = await db.insert(debugEvents).values(input).returning();
    return created;
  }

  async listDebugEvents(status?: string, botId?: number): Promise<DebugEvent[]> {
    const conditions = [];
    if (status) conditions.push(eq(debugEvents.status, status));
    if (botId) conditions.push(eq(debugEvents.botId, botId));
    if (conditions.length > 0) {
      return await db.select().from(debugEvents).where(and(...conditions)).orderBy(desc(debugEvents.createdAt)).limit(200);
    }
    return await db.select().from(debugEvents).orderBy(desc(debugEvents.createdAt)).limit(200);
  }

  async getDebugEvent(id: number): Promise<DebugEvent | undefined> {
    const [event] = await db.select().from(debugEvents).where(eq(debugEvents.id, id));
    return event;
  }

  async resolveDebugEvent(id: number, resolution: string): Promise<DebugEvent | undefined> {
    const [updated] = await db.update(debugEvents)
      .set({ status: "resolved", resolution, resolvedAt: new Date() })
      .where(eq(debugEvents.id, id))
      .returning();
    return updated;
  }

  async createAutoFix(input: InsertAutoFix): Promise<AutoFix> {
    const [created] = await db.insert(autoFixes).values(input).returning();
    return created;
  }

  async listAutoFixes(status?: string): Promise<AutoFix[]> {
    if (status) {
      return await db.select().from(autoFixes).where(eq(autoFixes.status, status)).orderBy(desc(autoFixes.createdAt)).limit(200);
    }
    return await db.select().from(autoFixes).orderBy(desc(autoFixes.createdAt)).limit(200);
  }

  async applyAutoFix(id: number): Promise<AutoFix | undefined> {
    const [updated] = await db.update(autoFixes)
      .set({ status: "applied", appliedAt: new Date() })
      .where(eq(autoFixes.id, id))
      .returning();
    if (updated?.debugEventId) {
      await db.update(debugEvents)
        .set({ status: "resolved", resolution: `Auto-fix #${id} applied`, resolvedAt: new Date() })
        .where(eq(debugEvents.id, updated.debugEventId));
    }
    return updated;
  }

  async rejectAutoFix(id: number): Promise<AutoFix | undefined> {
    const [updated] = await db.update(autoFixes)
      .set({ status: "rejected" })
      .where(eq(autoFixes.id, id))
      .returning();
    return updated;
  }

  async createRevenueLeak(input: InsertRevenueLeak): Promise<RevenueLeak> {
    const [created] = await db.insert(revenueLeaks).values(input).returning();
    return created;
  }

  async listRevenueLeaks(status?: string): Promise<RevenueLeak[]> {
    if (status) {
      return await db.select().from(revenueLeaks).where(eq(revenueLeaks.status, status)).orderBy(desc(revenueLeaks.createdAt)).limit(200);
    }
    return await db.select().from(revenueLeaks).orderBy(desc(revenueLeaks.createdAt)).limit(200);
  }

  async resolveRevenueLeak(id: number, notes: string): Promise<RevenueLeak | undefined> {
    const [updated] = await db.update(revenueLeaks)
      .set({ status: "resolved", notes })
      .where(eq(revenueLeaks.id, id))
      .returning();
    return updated;
  }

  async createSecurityScan(input: InsertSecurityScan): Promise<SecurityScan> {
    const [created] = await db.insert(securityScans).values(input).returning();
    return created;
  }

  async listSecurityScans(status?: string): Promise<SecurityScan[]> {
    if (status) {
      return await db.select().from(securityScans).where(eq(securityScans.status, status)).orderBy(desc(securityScans.createdAt)).limit(200);
    }
    return await db.select().from(securityScans).orderBy(desc(securityScans.createdAt)).limit(200);
  }

  async remediateSecurityScan(id: number, mitigation: string): Promise<SecurityScan | undefined> {
    const [updated] = await db.update(securityScans)
      .set({ status: "remediated", mitigation })
      .where(eq(securityScans.id, id))
      .returning();
    return updated;
  }

  async getDebugOverview(): Promise<DebugOverview> {
    const allEvents = await db.select().from(debugEvents);
    const allFixes = await db.select().from(autoFixes);
    const allLeaks = await db.select().from(revenueLeaks);
    const allScans = await db.select().from(securityScans);

    const openEvents = allEvents.filter(e => e.status === "open" || e.status === "investigating").length;
    const criticalEvents = allEvents.filter(e => e.severity >= 8 && e.status !== "resolved").length;
    const totalAutoFixes = allFixes.length;
    const appliedFixes = allFixes.filter(f => f.status === "applied").length;
    const queuedFixes = allFixes.filter(f => f.status === "queued").length;
    const rejectedFixes = allFixes.filter(f => f.status === "rejected").length;
    const totalRevenueLeaks = allLeaks.length;
    const openRevenueLeaks = allLeaks.filter(l => l.status === "open").length;
    const revenueAtRisk = allLeaks.filter(l => l.status === "open").reduce((s, l) => s + l.impactEstimate, 0);
    const totalSecurityIssues = allScans.length;
    const openSecurityIssues = allScans.filter(s => s.status === "open").length;
    const avgSeverity = allEvents.length > 0 ? Math.round(allEvents.reduce((s, e) => s + e.severity, 0) / allEvents.length * 10) / 10 : 0;

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const eventsToday = allEvents.filter(e => new Date(e.createdAt) >= today).length;
    const fixSuccessRate = totalAutoFixes > 0 ? Math.round((appliedFixes / totalAutoFixes) * 100) : 100;

    const resolvedEvents = allEvents.filter(e => e.status === "resolved").length;
    const totalEvents = allEvents.length;
    const healthBase = totalEvents > 0 ? Math.round((resolvedEvents / totalEvents) * 100) : 100;
    const severityPenalty = criticalEvents * 5;
    const leakPenalty = openRevenueLeaks * 2;
    const secPenalty = openSecurityIssues * 3;
    const globalHealthScore = Math.max(0, Math.min(100, healthBase - severityPenalty - leakPenalty - secPenalty));

    return {
      globalHealthScore,
      openEvents,
      criticalEvents,
      totalAutoFixes,
      appliedFixes,
      queuedFixes,
      rejectedFixes,
      totalRevenueLeaks,
      openRevenueLeaks,
      revenueAtRisk,
      totalSecurityIssues,
      openSecurityIssues,
      avgSeverity,
      eventsToday,
      fixSuccessRate,
    };
  }
  async listFormulas(): Promise<Formula[]> {
    return await db.select().from(formulas).orderBy(formulas.category, formulas.name);
  }

  async getFormula(id: number): Promise<Formula | undefined> {
    const [row] = await db.select().from(formulas).where(eq(formulas.id, id));
    return row;
  }

  async createFormula(input: InsertFormula): Promise<Formula> {
    const [row] = await db.insert(formulas).values(input).returning();
    return row;
  }

  async updateFormula(id: number, updates: Partial<InsertFormula>): Promise<Formula | undefined> {
    const [row] = await db.update(formulas).set(updates).where(eq(formulas.id, id)).returning();
    return row;
  }

  async deleteFormula(id: number): Promise<void> {
    await db.delete(formulas).where(eq(formulas.id, id));
  }

  async listPlatformConnections(): Promise<PlatformConnection[]> {
    return await db.select().from(platformConnections).orderBy(platformConnections.platform);
  }

  async createPlatformConnection(input: InsertPlatformConnection): Promise<PlatformConnection> {
    const [row] = await db.insert(platformConnections).values(input).returning();
    return row;
  }

  async updatePlatformConnection(id: number, updates: Partial<InsertPlatformConnection>): Promise<PlatformConnection | undefined> {
    const [row] = await db.update(platformConnections).set(updates).where(eq(platformConnections.id, id)).returning();
    return row;
  }

  async deletePlatformConnection(id: number): Promise<void> {
    await db.delete(platformConnections).where(eq(platformConnections.id, id));
  }

  async listPlugins(): Promise<Plugin[]> {
    return await db.select().from(plugins).orderBy(plugins.name);
  }

  async getPlugin(id: number): Promise<Plugin | undefined> {
    const [row] = await db.select().from(plugins).where(eq(plugins.id, id));
    return row;
  }

  async createPlugin(input: InsertPlugin): Promise<Plugin> {
    const [row] = await db.insert(plugins).values(input).returning();
    return row;
  }

  async updatePlugin(id: number, updates: Partial<InsertPlugin>): Promise<Plugin | undefined> {
    const [row] = await db.update(plugins).set(updates).where(eq(plugins.id, id)).returning();
    return row;
  }

  async deletePlugin(id: number): Promise<void> {
    await db.delete(plugins).where(eq(plugins.id, id));
  }

  async incrementPluginDownloads(id: number): Promise<Plugin | undefined> {
    const [row] = await db.update(plugins).set({ downloads: sql`${plugins.downloads} + 1` }).where(eq(plugins.id, id)).returning();
    return row;
  }

  async listBotMemory(botId: number): Promise<BotMemory[]> {
    return await db.select().from(botMemory).where(eq(botMemory.botId, botId)).orderBy(desc(botMemory.createdAt));
  }

  async createBotMemory(input: InsertBotMemory): Promise<BotMemory> {
    const [row] = await db.insert(botMemory).values(input).returning();
    return row;
  }

  async deleteBotMemory(id: number): Promise<void> {
    await db.delete(botMemory).where(eq(botMemory.id, id));
  }

  async listSystemSnapshots(): Promise<SystemSnapshot[]> {
    return await db.select().from(systemSnapshots).orderBy(desc(systemSnapshots.createdAt));
  }

  async createSystemSnapshot(input: InsertSystemSnapshot): Promise<SystemSnapshot> {
    const [row] = await db.insert(systemSnapshots).values(input).returning();
    return row;
  }

  async getSystemSnapshot(id: number): Promise<SystemSnapshot | undefined> {
    const [row] = await db.select().from(systemSnapshots).where(eq(systemSnapshots.id, id));
    return row;
  }

  async deleteSystemSnapshot(id: number): Promise<void> {
    await db.delete(systemSnapshots).where(eq(systemSnapshots.id, id));
  }

  async createCostEvent(input: InsertCostEvent): Promise<CostEvent> {
    const [row] = await db.insert(costEvents).values(input).returning();
    return row;
  }

  async listCostEvents(limit = 100): Promise<CostEvent[]> {
    return await db.select().from(costEvents).orderBy(desc(costEvents.createdAt)).limit(limit);
  }

  async getCostSummary(): Promise<{ totalTokens: number; totalCost: number; eventCount: number }> {
    const events = await db.select().from(costEvents);
    const totalTokens = events.reduce((s, e) => s + (e.tokens ?? 0), 0);
    const totalCost = events.reduce((s, e) => s + (e.cost ?? 0), 0);
    return { totalTokens, totalCost, eventCount: events.length };
  }
}

export const storage = new DatabaseStorage();
