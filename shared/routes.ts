import { z } from "zod";
import {
  insertAutonomousTaskSchema,
  insertBotProfileSchema,
  type Conversation,
  type Message,
  type BotProfile,
  type AutonomousTask,
  type TaskRun,
} from "./schema";

export const errorSchemas = {
  validation: z.object({
    message: z.string(),
    field: z.string().optional(),
  }),
  notFound: z.object({
    message: z.string(),
  }),
  internal: z.object({
    message: z.string(),
  }),
};

export const api = {
  bots: {
    list: {
      method: "GET" as const,
      path: "/api/bots" as const,
      responses: {
        200: z.array(z.custom<BotProfile>()),
      },
    },
    create: {
      method: "POST" as const,
      path: "/api/bots" as const,
      input: insertBotProfileSchema,
      responses: {
        201: z.custom<BotProfile>(),
        400: errorSchemas.validation,
      },
    },
    update: {
      method: "PUT" as const,
      path: "/api/bots/:id" as const,
      input: insertBotProfileSchema.partial(),
      responses: {
        200: z.custom<BotProfile>(),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
    setDefault: {
      method: "POST" as const,
      path: "/api/bots/:id/default" as const,
      responses: {
        200: z.custom<BotProfile>(),
        404: errorSchemas.notFound,
      },
    },
  },
  conversations: {
    list: {
      method: "GET" as const,
      path: "/api/conversations" as const,
      responses: {
        200: z.array(z.custom<Conversation>()),
      },
    },
    get: {
      method: "GET" as const,
      path: "/api/conversations/:id" as const,
      responses: {
        200: z.object({
          conversation: z.custom<Conversation>(),
          messages: z.array(z.custom<Message>()),
        }),
        404: errorSchemas.notFound,
      },
    },
    create: {
      method: "POST" as const,
      path: "/api/conversations" as const,
      input: z
        .object({
          title: z.string().min(1).max(140).optional(),
        })
        .optional(),
      responses: {
        201: z.custom<Conversation>(),
        400: errorSchemas.validation,
      },
    },
    delete: {
      method: "DELETE" as const,
      path: "/api/conversations/:id" as const,
      responses: {
        204: z.void(),
        404: errorSchemas.notFound,
      },
    },
    createMessage: {
      method: "POST" as const,
      path: "/api/conversations/:id/messages" as const,
      input: z.object({
        content: z.string().min(1).max(8000),
        botSlug: z.string().optional(),
      }),
      responses: {
        201: z.object({
          message: z.custom<Message>(),
          assistantMessage: z.custom<Message>(),
        }),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
    stream: {
      method: "POST" as const,
      path: "/api/conversations/:id/stream" as const,
      input: z.object({
        content: z.string().min(1).max(8000),
        botSlug: z.string().optional(),
      }),
      responses: {
        200: z.unknown(),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
  },
  tasks: {
    list: {
      method: "GET" as const,
      path: "/api/tasks" as const,
      responses: {
        200: z.array(z.custom<AutonomousTask>()),
      },
    },
    create: {
      method: "POST" as const,
      path: "/api/tasks" as const,
      input: insertAutonomousTaskSchema.extend({
        status: z.string().optional(),
        priority: z.coerce.number().int().min(1).max(5).optional(),
      }),
      responses: {
        201: z.custom<AutonomousTask>(),
        400: errorSchemas.validation,
      },
    },
    update: {
      method: "PUT" as const,
      path: "/api/tasks/:id" as const,
      input: insertAutonomousTaskSchema
        .partial()
        .extend({
          status: z.string().optional(),
          priority: z.coerce.number().int().min(1).max(5).optional(),
        }),
      responses: {
        200: z.custom<AutonomousTask>(),
        400: errorSchemas.validation,
        404: errorSchemas.notFound,
      },
    },
    delete: {
      method: "DELETE" as const,
      path: "/api/tasks/:id" as const,
      responses: {
        204: z.void(),
        404: errorSchemas.notFound,
      },
    },
    run: {
      method: "POST" as const,
      path: "/api/tasks/:id/run" as const,
      input: z
        .object({
          dryRun: z.boolean().optional(),
        })
        .optional(),
      responses: {
        201: z.custom<TaskRun>(),
        404: errorSchemas.notFound,
      },
    },
    runs: {
      method: "GET" as const,
      path: "/api/tasks/:id/runs" as const,
      responses: {
        200: z.array(z.custom<TaskRun>()),
        404: errorSchemas.notFound,
      },
    },
  },
};

export function buildUrl(
  path: string,
  params?: Record<string, string | number>
): string {
  let url = path;
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      url = url.replace(`:${key}`, String(value));
    }
  }
  return url;
}

export const streams = {
  chat: {
    input: api.conversations.stream.input,
    chunk: z.object({
      type: z.enum(["delta", "done", "error"]),
      content: z.string().optional(),
      conversationId: z.number().optional(),
      messageId: z.number().optional(),
      error: z.string().optional(),
    }),
  },
};

export type BotProfileResponse = z.infer<typeof api.bots.list.responses[200]>[number];
export type BotsListResponse = z.infer<typeof api.bots.list.responses[200]>;

export type ConversationsListResponse = z.infer<
  typeof api.conversations.list.responses[200]
>;
export type ConversationGetResponse = z.infer<
  typeof api.conversations.get.responses[200]
>;

export type CreateMessageInput = z.infer<typeof api.conversations.createMessage.input>;
export type CreateMessageResponse = z.infer<
  typeof api.conversations.createMessage.responses[201]
>;

export type AutonomousTasksListResponse = z.infer<typeof api.tasks.list.responses[200]>;
export type TaskRunResponse = z.infer<typeof api.tasks.run.responses[201]>;

export type ValidationError = z.infer<typeof errorSchemas.validation>;
export type NotFoundError = z.infer<typeof errorSchemas.notFound>;
export type InternalError = z.infer<typeof errorSchemas.internal>;
