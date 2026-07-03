import { z } from "zod";
import { insertBotProfileSchema, insertConversationSchema, insertAutonomousTaskSchema, } from "./schema";
// ---------------------------------------------------------------------------
// Utility: replace :param tokens in Express-style path strings
// ---------------------------------------------------------------------------
export function buildUrl(path, params) {
    let result = path;
    for (const [key, value] of Object.entries(params)) {
        result = result.replace(`:${key}`, String(value));
    }
    return result;
}
// ---------------------------------------------------------------------------
// Shared response schemas (database rows come back over JSON as ISO strings)
// ---------------------------------------------------------------------------
const dateField = z.union([z.string(), z.date()]);
const botProfileSchema = z.object({
    id: z.number(),
    slug: z.string(),
    displayName: z.string(),
    systemPrompt: z.string(),
    traits: z.unknown(),
    isDefault: z.boolean(),
    division: z.string(),
    category: z.string(),
    tier: z.string(),
    description: z.string(),
    capabilities: z.unknown(),
    revenueModel: z.string(),
    targetUsers: z.string(),
    status: z.string(),
    priceRange: z.string(),
    autonomyLevel: z.string(),
    operationalMode: z.string(),
});
const conversationSchema = z.object({
    id: z.number(),
    title: z.string(),
    createdAt: dateField,
});
const messageSchema = z.object({
    id: z.number(),
    conversationId: z.number(),
    role: z.string(),
    content: z.string(),
    createdAt: dateField,
});
const autonomousTaskSchema = z.object({
    id: z.number(),
    title: z.string(),
    objective: z.string(),
    status: z.string(),
    priority: z.number(),
    autonomyMode: z.string(),
    division: z.string(),
    assignedBotId: z.number().nullable().optional(),
    lastRunAt: dateField.nullable().optional(),
    createdAt: dateField,
});
const taskRunSchema = z.object({
    id: z.number(),
    taskId: z.number(),
    status: z.string(),
    summary: z.string(),
    output: z.unknown(),
    createdAt: dateField,
});
const empireSettingSchema = z.object({
    id: z.number(),
    key: z.string(),
    value: z.unknown(),
    updatedAt: dateField,
});
const errorResponseSchema = z.object({
    message: z.string(),
    field: z.string().optional(),
});
// ---------------------------------------------------------------------------
// Route registry
// ---------------------------------------------------------------------------
export const api = {
    // -- Bots ------------------------------------------------------------------
    bots: {
        list: {
            path: "/api/bots",
            method: "GET",
            responses: {
                200: z.array(botProfileSchema),
            },
        },
        byDivision: {
            path: "/api/bots/division/:division",
            method: "GET",
            responses: {
                200: z.array(botProfileSchema),
            },
        },
        create: {
            path: "/api/bots",
            method: "POST",
            input: insertBotProfileSchema,
            responses: {
                201: botProfileSchema,
                400: errorResponseSchema,
            },
        },
        update: {
            path: "/api/bots/:id",
            method: "PUT",
            input: insertBotProfileSchema.partial(),
            responses: {
                200: botProfileSchema,
                400: errorResponseSchema,
                404: errorResponseSchema,
            },
        },
        setDefault: {
            path: "/api/bots/:id/set-default",
            method: "POST",
            responses: {
                200: botProfileSchema,
                404: errorResponseSchema,
            },
        },
    },
    // -- Conversations ---------------------------------------------------------
    conversations: {
        list: {
            path: "/api/conversations",
            method: "GET",
            responses: {
                200: z.array(conversationSchema),
            },
        },
        get: {
            path: "/api/conversations/:id",
            method: "GET",
            responses: {
                200: z.object({
                    conversation: conversationSchema,
                    messages: z.array(messageSchema),
                }),
                404: errorResponseSchema,
            },
        },
        create: {
            path: "/api/conversations",
            method: "POST",
            input: insertConversationSchema.partial(),
            responses: {
                201: conversationSchema,
                400: errorResponseSchema,
            },
        },
        delete: {
            path: "/api/conversations/:id",
            method: "DELETE",
            responses: {
                404: errorResponseSchema,
            },
        },
        createMessage: {
            path: "/api/conversations/:id/messages",
            method: "POST",
            input: z.object({
                content: z.string().min(1),
                botSlug: z.string().optional(),
            }),
            responses: {
                201: z.object({
                    message: messageSchema,
                    assistantMessage: messageSchema.optional(),
                }),
                400: errorResponseSchema,
                404: errorResponseSchema,
            },
        },
        stream: {
            path: "/api/conversations/:id/stream",
            method: "POST",
            input: z.object({
                content: z.string().min(1),
                botSlug: z.string().optional(),
                mode: z.string().optional(),
            }),
            responses: {
                400: errorResponseSchema,
                404: errorResponseSchema,
            },
        },
    },
    // -- Autonomous Tasks ------------------------------------------------------
    tasks: {
        list: {
            path: "/api/tasks",
            method: "GET",
            responses: {
                200: z.array(autonomousTaskSchema),
            },
        },
        create: {
            path: "/api/tasks",
            method: "POST",
            input: insertAutonomousTaskSchema,
            responses: {
                201: autonomousTaskSchema,
                400: errorResponseSchema,
            },
        },
        update: {
            path: "/api/tasks/:id",
            method: "PUT",
            input: insertAutonomousTaskSchema.partial(),
            responses: {
                200: autonomousTaskSchema,
                400: errorResponseSchema,
                404: errorResponseSchema,
            },
        },
        delete: {
            path: "/api/tasks/:id",
            method: "DELETE",
            responses: {
                404: errorResponseSchema,
            },
        },
        run: {
            path: "/api/tasks/:id/run",
            method: "POST",
            input: z.object({
                dryRun: z.boolean().optional(),
            }),
            responses: {
                201: taskRunSchema,
                404: errorResponseSchema,
            },
        },
        runs: {
            path: "/api/tasks/:id/runs",
            method: "GET",
            responses: {
                200: z.array(taskRunSchema),
                404: errorResponseSchema,
            },
        },
    },
    // -- Empire ----------------------------------------------------------------
    empire: {
        overview: {
            path: "/api/empire/overview",
            method: "GET",
            responses: {
                200: z.object({
                    totalBots: z.number(),
                    totalDivisions: z.number(),
                    activeTasks: z.number(),
                    completedTasks: z.number(),
                    autonomyMode: z.string(),
                    divisions: z.array(z.object({
                        division: z.string(),
                        botCount: z.number(),
                        activeTasks: z.number(),
                        completedTasks: z.number(),
                        revenue: z.string(),
                        runtime: z.object({
                            division: z.string(),
                            health: z.string(),
                            activeAlerts: z.array(z.string()),
                            ceoAgent: z.object({
                                slug: z.string(),
                                displayName: z.string(),
                                status: z.string(),
                                autonomyMode: z.string(),
                                openDecisions: z.number(),
                                lastDecisionAt: z.string().nullable(),
                            }).nullable(),
                            specialists: z.array(z.object({
                                slug: z.string(),
                                displayName: z.string(),
                                status: z.string(),
                                tier: z.string(),
                                workload: z.number(),
                            })),
                            workflowEngine: z.object({
                                active: z.number(),
                                queued: z.number(),
                                blocked: z.number(),
                                completed: z.number(),
                                health: z.string(),
                            }),
                            learningEngine: z.object({
                                status: z.string(),
                                signalsLearned: z.number(),
                                knowledgeCoverage: z.number(),
                                lastSyncAt: z.string().nullable(),
                            }),
                            toolMarketplace: z.object({
                                availableTools: z.number(),
                                enabledTools: z.number(),
                                topTools: z.array(z.string()),
                            }),
                            knowledgeBase: z.object({
                                formulas: z.number(),
                                snippets: z.number(),
                                docs: z.number(),
                                lastUpdatedAt: z.string().nullable(),
                            }),
                            kpis: z.object({
                                activeWorkflows: z.number(),
                                revenueCents: z.number(),
                                uptimePct: z.number(),
                                openAlerts: z.number(),
                                failedRuns: z.number(),
                            }),
                        }),
                    })),
                }),
            },
        },
        divisions: {
            path: "/api/empire/divisions",
            method: "GET",
            responses: {
                200: z.array(z.object({
                    division: z.string(),
                    count: z.number(),
                    health: z.string().optional(),
                    activeWorkflows: z.number().optional(),
                })),
            },
        },
        settings: {
            get: {
                path: "/api/empire/settings/:key",
                method: "GET",
                responses: {
                    200: empireSettingSchema,
                    404: errorResponseSchema,
                },
            },
            set: {
                path: "/api/empire/settings/:key",
                method: "PUT",
                input: z.object({
                    value: z.unknown(),
                }),
                responses: {
                    200: empireSettingSchema,
                },
            },
        },
    },
};
// ---------------------------------------------------------------------------
// SSE stream chunk schemas
// ---------------------------------------------------------------------------
export const streams = {
    chat: {
        chunk: z.discriminatedUnion("type", [
            z.object({
                type: z.literal("delta"),
                content: z.string(),
                messageId: z.number(),
                conversationId: z.number(),
            }),
            z.object({
                type: z.literal("done"),
                conversationId: z.number(),
                messageId: z.number(),
            }),
            z.object({
                type: z.literal("error"),
                error: z.string(),
            }),
        ]),
    },
};
