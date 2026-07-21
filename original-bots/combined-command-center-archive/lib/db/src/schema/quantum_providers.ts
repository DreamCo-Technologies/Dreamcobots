import { pgTable, text, timestamp, uuid, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

/**
 * Curated directory of real quantum-computing providers DreamCo can resell or
 * route client workloads to (Enterprise, IonQ, D-Wave, etc.). This is a reference
 * catalog of publicly known companies — NOT live capacity or pricing. It carries
 * no fabricated metrics; only factual company attributes (modality, access
 * model, HQ, public URL).
 */
export const quantumProvidersTable = pgTable("quantum_providers", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull().unique(),
  hardware: text("hardware"), // superconducting | trapped-ion | photonic | neutral-atom | annealing | spin | simulator | software
  accessModel: text("access_model"), // cloud | sdk | on-prem | research
  headquarters: text("headquarters"),
  url: text("url"),
  summary: text("summary"),
  category: text("category").notNull().default("hardware"), // hardware | cloud-access | software
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
}, (t) => ({
  categoryIdx: index("quantum_providers_category_idx").on(t.category),
}));

export const insertQuantumProviderSchema = createInsertSchema(quantumProvidersTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertQuantumProvider = z.infer<typeof insertQuantumProviderSchema>;
export type QuantumProvider = typeof quantumProvidersTable.$inferSelect;
