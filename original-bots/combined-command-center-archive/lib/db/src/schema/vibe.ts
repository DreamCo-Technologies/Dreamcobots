import { pgTable, text, timestamp, uuid, jsonb, real, integer, index, uniqueIndex } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const vibeLibrariesTable = pgTable("vibe_libraries", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
  ecosystem: text("ecosystem").notNull(),
  summary: text("summary"),
  capabilities: jsonb("capabilities").$type<string[]>().default([]),
  mathFoundations: jsonb("math_foundations").$type<string[]>().default([]),
  revolutionaryUses: jsonb("revolutionary_uses").$type<string[]>().default([]),
  status: text("status").notNull().default("learned"),
  model: text("model"),
  learnedAt: timestamp("learned_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  nameEcoUnique: uniqueIndex("vibe_libraries_name_eco_unique").on(t.ecosystem, t.name),
  ecoIdx: index("vibe_libraries_eco_idx").on(t.ecosystem),
  learnedIdx: index("vibe_libraries_learned_idx").on(t.learnedAt),
}));

export const insertVibeLibrarySchema = createInsertSchema(vibeLibrariesTable).omit({ id: true, learnedAt: true });
export type InsertVibeLibrary = z.infer<typeof insertVibeLibrarySchema>;
export type VibeLibrary = typeof vibeLibrariesTable.$inferSelect;

export const vibeIdeasTable = pgTable("vibe_ideas", {
  id: uuid("id").primaryKey().defaultRandom(),
  title: text("title").notNull(),
  library: text("library"),
  ecosystem: text("ecosystem"),
  description: text("description").notNull(),
  impactScore: real("impact_score").notNull().default(0),
  mathBasis: text("math_basis"),
  generatedBy: text("generated_by").notNull().default("buddy"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  libIdx: index("vibe_ideas_lib_idx").on(t.library),
  scoreIdx: index("vibe_ideas_score_idx").on(t.impactScore),
  createdIdx: index("vibe_ideas_created_idx").on(t.createdAt),
}));

export const insertVibeIdeaSchema = createInsertSchema(vibeIdeasTable).omit({ id: true, createdAt: true });
export type InsertVibeIdea = z.infer<typeof insertVibeIdeaSchema>;
export type VibeIdea = typeof vibeIdeasTable.$inferSelect;

export const vibeBuildsTable = pgTable("vibe_builds", {
  id: uuid("id").primaryKey().defaultRandom(),
  prompt: text("prompt").notNull(),
  language: text("language").notNull().default("typescript"),
  outputCode: text("output_code"),
  explanation: text("explanation"),
  librariesUsed: jsonb("libraries_used").$type<string[]>().default([]),
  tokensUsed: integer("tokens_used").notNull().default(0),
  model: text("model"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  createdIdx: index("vibe_builds_created_idx").on(t.createdAt),
}));

export const insertVibeBuildSchema = createInsertSchema(vibeBuildsTable).omit({ id: true, createdAt: true });
export type InsertVibeBuild = z.infer<typeof insertVibeBuildSchema>;
export type VibeBuild = typeof vibeBuildsTable.$inferSelect;
