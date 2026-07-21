import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl } from "@shared/routes";
import type {
  CreateBotProfileRequest,
  UpdateBotProfileRequest,
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

export function useBots() {
  return useQuery({
    queryKey: [api.bots.list.path],
    queryFn: async () => {
      const res = await fetch(api.bots.list.path, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch bots");
      const json = await res.json();
      return parseWithLogging(api.bots.list.responses[200], json, "bots.list");
    },
  });
}

export function useCreateBot() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateBotProfileRequest) => {
      const validated = api.bots.create.input.parse(data);
      const res = await fetch(api.bots.create.path, {
        method: api.bots.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 400) {
          const err = parseWithLogging(api.bots.create.responses[400], await res.json(), "bots.create[400]");
          throw new Error(err.message);
        }
        throw new Error("Failed to create bot");
      }

      return parseWithLogging(api.bots.create.responses[201], await res.json(), "bots.create[201]");
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: [api.bots.list.path] });
    },
  });
}

export function useUpdateBot() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: UpdateBotProfileRequest }) => {
      const validated = api.bots.update.input.parse(updates);
      const url = buildUrl(api.bots.update.path, { id });
      const res = await fetch(url, {
        method: api.bots.update.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 400) {
          const err = parseWithLogging(api.bots.update.responses[400], await res.json(), "bots.update[400]");
          throw new Error(err.message);
        }
        if (res.status === 404) {
          const err = parseWithLogging(api.bots.update.responses[404], await res.json(), "bots.update[404]");
          throw new Error(err.message);
        }
        throw new Error("Failed to update bot");
      }

      return parseWithLogging(api.bots.update.responses[200], await res.json(), "bots.update[200]");
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: [api.bots.list.path] });
    },
  });
}

export function useSetDefaultBot() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const url = buildUrl(api.bots.setDefault.path, { id });
      const res = await fetch(url, {
        method: api.bots.setDefault.method,
        credentials: "include",
      });
      if (!res.ok) {
        if (res.status === 404) {
          const err = parseWithLogging(api.bots.setDefault.responses[404], await res.json(), "bots.setDefault[404]");
          throw new Error(err.message);
        }
        throw new Error("Failed to set default bot");
      }
      return parseWithLogging(api.bots.setDefault.responses[200], await res.json(), "bots.setDefault[200]");
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: [api.bots.list.path] });
    },
  });
}
