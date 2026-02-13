import { db } from "./db";
import {
  botProfiles,
  conversations,
  messages,
  autonomousTasks,
  taskRuns,
  type BotProfile,
  type InsertBotProfile,
  type AutonomousTask,
  type InsertAutonomousTask,
  type TaskRun,
} from "@shared/schema";
import { and, desc, eq, ne, sql } from "drizzle-orm";

export interface IStorage {
  // Bots
  listBotProfiles(): Promise<BotProfile[]>;
  createBotProfile(input: InsertBotProfile): Promise<BotProfile>;
  updateBotProfile(id: number, updates: Partial<InsertBotProfile>): Promise<BotProfile | undefined>;
  setDefaultBotProfile(id: number): Promise<BotProfile | undefined>;
  getDefaultBotProfile(): Promise<BotProfile | undefined>;
  getBotProfileBySlug(slug: string): Promise<BotProfile | undefined>;

  // Conversations
  listConversations(): Promise<(typeof conversations.$inferSelect)[]>;
  getConversation(id: number): Promise<(typeof conversations.$inferSelect) | undefined>;
  createConversation(title: string): Promise<(typeof conversations.$inferSelect)>;
  deleteConversation(id: number): Promise<void>;
  getMessages(conversationId: number): Promise<(typeof messages.$inferSelect)[]>;
  createMessage(conversationId: number, role: "user" | "assistant", content: string): Promise<(typeof messages.$inferSelect)>;

  // Tasks
  listTasks(): Promise<AutonomousTask[]>;
  createTask(input: InsertAutonomousTask & { status?: string; priority?: number }): Promise<AutonomousTask>;
  updateTask(id: number, updates: Partial<InsertAutonomousTask> & { status?: string; priority?: number }): Promise<AutonomousTask | undefined>;
  deleteTask(id: number): Promise<void>;
  createTaskRun(taskId: number, status: string, summary: string, output: unknown): Promise<TaskRun>;
  listTaskRuns(taskId: number): Promise<TaskRun[]>;
}

export class DatabaseStorage implements IStorage {
  async listBotProfiles(): Promise<BotProfile[]> {
    return await db.select().from(botProfiles).orderBy(botProfiles.id);
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

  async createTask(input: InsertAutonomousTask & { status?: string; priority?: number }): Promise<AutonomousTask> {
    const [task] = await db
      .insert(autonomousTasks)
      .values({
        title: input.title,
        objective: input.objective,
        status: input.status ?? input.status ?? "pending",
        priority: input.priority ?? input.priority ?? 3,
      })
      .returning();
    return task;
  }

  async updateTask(id: number, updates: Partial<InsertAutonomousTask> & { status?: string; priority?: number }): Promise<AutonomousTask | undefined> {
    const [task] = await db
      .update(autonomousTasks)
      .set({
        ...updates,
      })
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
}

export const storage = new DatabaseStorage();
