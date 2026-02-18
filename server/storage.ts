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
}

export const storage = new DatabaseStorage();
