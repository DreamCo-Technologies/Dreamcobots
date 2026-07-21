import { pgTable, uuid, timestamp, primaryKey, index } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const agentCapabilitiesTable = pgTable("agent_capabilities", {
  agentId: uuid("agent_id").notNull(),
  capabilityId: uuid("capability_id").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  pk: primaryKey({ columns: [t.agentId, t.capabilityId] }),
  capabilityIdx: index("agent_capabilities_capability_idx").on(t.capabilityId),
}));

export const insertAgentCapabilitySchema = createInsertSchema(agentCapabilitiesTable).omit({ createdAt: true });
export type InsertAgentCapability = z.infer<typeof insertAgentCapabilitySchema>;
export type AgentCapability = typeof agentCapabilitiesTable.$inferSelect;
