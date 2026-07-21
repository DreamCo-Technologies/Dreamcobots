import { pgTable, text, integer, timestamp, uuid, jsonb, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

/**
 * Global AI Sources registry — one row per AI-infrastructure module discovered
 * in the Dreamcobots repo (model registries, task routers, capability
 * registries, connectors, orchestrators, the global-ai-sources flow, etc.).
 * This is the catalog Buddy reads to know what it can route to and learn from.
 */
export const aiSourcesTable = pgTable("ai_sources", {
  id: uuid("id").primaryKey().defaultRandom(),
  key: text("key").notNull().unique(), // repo path, the stable identity
  name: text("name").notNull(),
  role: text("role").notNull().default("module"), // registry | router | flow | capability | connector | orchestrator | module
  language: text("language").notNull().default("python"),
  summary: text("summary"), // module docstring / first lines
  repoPath: text("repo_path").notNull(),
  sizeBytes: integer("size_bytes").notNull().default(0),
  signals: jsonb("signals").$type<Record<string, unknown>>().notNull().default({}), // parsed counts: models, useCases, classes, functions, providers
  indexedFrom: text("indexed_from").notNull().default("Dreamcobots"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
}, (t) => ({
  roleIdx: index("ai_sources_role_idx").on(t.role),
}));

export const insertAiSourceSchema = createInsertSchema(aiSourcesTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertAiSource = z.infer<typeof insertAiSourceSchema>;
export type AiSource = typeof aiSourcesTable.$inferSelect;
