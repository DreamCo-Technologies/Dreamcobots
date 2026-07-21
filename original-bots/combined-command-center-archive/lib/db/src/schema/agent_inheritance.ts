import { pgTable, uuid, timestamp, primaryKey, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

// Parent → Child agent inheritance (e.g., HouseFlippingBot inherits from RealEstate, Finance)
export const agentInheritanceTable = pgTable("agent_inheritance", {
  childId: uuid("child_id").notNull(),
  parentId: uuid("parent_id").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  pk: primaryKey({ columns: [t.childId, t.parentId] }),
  parentIdx: index("agent_inheritance_parent_idx").on(t.parentId),
}));

export const insertAgentInheritanceSchema = createInsertSchema(agentInheritanceTable).omit({ createdAt: true });
export type InsertAgentInheritance = z.infer<typeof insertAgentInheritanceSchema>;
export type AgentInheritance = typeof agentInheritanceTable.$inferSelect;
