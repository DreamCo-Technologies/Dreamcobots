import { pgTable, text, timestamp, uuid, jsonb, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const capabilitiesTable = pgTable("capabilities", {
  id: uuid("id").primaryKey().defaultRandom(),
  slug: text("slug").notNull().unique(),
  name: text("name").notNull(),
  description: text("description"),
  category: text("category").notNull(),
  inputSchema: jsonb("input_schema").$type<Record<string, unknown>>().default({}),
  outputSchema: jsonb("output_schema").$type<Record<string, unknown>>().default({}),
  version: text("version").notNull().default("1.0.0"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow().$onUpdate(() => new Date()),
}, (t) => ({
  categoryIdx: index("capabilities_category_idx").on(t.category),
}));

export const insertCapabilitySchema = createInsertSchema(capabilitiesTable).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertCapability = z.infer<typeof insertCapabilitySchema>;
export type Capability = typeof capabilitiesTable.$inferSelect;
