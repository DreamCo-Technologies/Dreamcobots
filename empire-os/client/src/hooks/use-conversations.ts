import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl, streams } from "@shared/routes";
import type {
  CreateConversationRequest,
  CreateMessageRequest,
} from "@shared/schema";
import { z } from "zod";

function parseWithLogging<T>(schema: z.ZodSchema<T>, data: unknown, label: string): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    console.error(`[Zod] ${label} validation failed:`, result.error.format());
    throw result.error;
  }
  return result.data;
}

export function useConversations() {
  return useQuery({
    queryKey: [api.conversations.list.path],
    queryFn: async () => {
      const res = await fetch(api.conversations.list.path, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch conversations");
      return parseWithLogging(api.conversations.list.responses[200], await res.json(), "conversations.list");
    },
  });
}

export function useConversation(id?: number) {
  return useQuery({
    enabled: typeof id === "number" && Number.isFinite(id),
    queryKey: [api.conversations.get.path, id ?? -1],
    queryFn: async () => {
      const url = buildUrl(api.conversations.get.path, { id: id as number });
      const res = await fetch(url, { credentials: "include" });
      if (res.status === 404) return null;
      if (!res.ok) throw new Error("Failed to fetch conversation");
      return parseWithLogging(api.conversations.get.responses[200], await res.json(), "conversations.get");
    },
  });
}

export function useCreateConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data?: CreateConversationRequest) => {
      const validated = api.conversations.create.input.parse(data ?? {});
      const res = await fetch(api.conversations.create.path, {
        method: api.conversations.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 400) {
          const err = parseWithLogging(api.conversations.create.responses[400], await res.json(), "conversations.create[400]");
          throw new Error(err.message);
        }
        throw new Error("Failed to create conversation");
      }
      return parseWithLogging(api.conversations.create.responses[201], await res.json(), "conversations.create[201]");
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: [api.conversations.list.path] });
    },
  });
}

export function useDeleteConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const url = buildUrl(api.conversations.delete.path, { id });
      const res = await fetch(url, {
        method: api.conversations.delete.method,
        credentials: "include",
      });
      if (!res.ok) {
        if (res.status === 404) {
          const err = parseWithLogging(api.conversations.delete.responses[404], await res.json(), "conversations.delete[404]");
          throw new Error(err.message);
        }
        throw new Error("Failed to delete conversation");
      }
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: [api.conversations.list.path] });
    },
  });
}

export function useCreateMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ conversationId, data }: { conversationId: number; data: CreateMessageRequest }) => {
      const url = buildUrl(api.conversations.createMessage.path, { id: conversationId });
      const validated = api.conversations.createMessage.input.parse({
        content: data.content,
        botSlug: data.botSlug,
      });

      const res = await fetch(url, {
        method: api.conversations.createMessage.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 400) {
          const err = parseWithLogging(api.conversations.createMessage.responses[400], await res.json(), "conversations.createMessage[400]");
          throw new Error(err.message);
        }
        if (res.status === 404) {
          const err = parseWithLogging(api.conversations.createMessage.responses[404], await res.json(), "conversations.createMessage[404]");
          throw new Error(err.message);
        }
        throw new Error("Failed to send message");
      }

      const json = await res.json();
      const parsed = parseWithLogging(api.conversations.createMessage.responses[201], json, "conversations.createMessage[201]");
      return parsed;
    },
    onSuccess: async (_data, vars) => {
      await qc.invalidateQueries({ queryKey: [api.conversations.get.path, vars.conversationId] });
      await qc.invalidateQueries({ queryKey: [api.conversations.list.path] });
    },
  });
}

/**
 * Streaming: POST /api/conversations/:id/stream => SSE
 * Client-side helper (NOT a React hook) you can call from pages.
 */
export async function streamAssistantReply(opts: {
  conversationId: number;
  input: z.infer<typeof api.conversations.stream.input>;
  onEvent: (chunk: z.infer<typeof streams.chat.chunk>) => void;
  signal?: AbortSignal;
}) {
  const url = buildUrl(api.conversations.stream.path, { id: opts.conversationId });
  const validated = api.conversations.stream.input.parse(opts.input);

  const res = await fetch(url, {
    method: api.conversations.stream.method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validated),
    credentials: "include",
    signal: opts.signal,
  });

  if (!res.ok) {
    if (res.status === 400) {
      const err = parseWithLogging(api.conversations.stream.responses[400], await res.json(), "conversations.stream[400]");
      throw new Error(err.message);
    }
    if (res.status === 404) {
      const err = parseWithLogging(api.conversations.stream.responses[404], await res.json(), "conversations.stream[404]");
      throw new Error(err.message);
    }
    throw new Error("Failed to start stream");
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("Streaming not supported (no reader)");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    for (const part of parts) {
      const lines = part.split("\n");
      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        if (!payload) continue;

        try {
          const raw = JSON.parse(payload);
          const evt = parseWithLogging(streams.chat.chunk, raw, "streams.chat.chunk");
          opts.onEvent(evt);
        } catch (e) {
          console.error("[SSE] failed to parse chunk:", e);
        }
      }
    }
  }
}
