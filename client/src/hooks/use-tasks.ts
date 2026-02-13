import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, buildUrl } from "@shared/routes";
import type {
  CreateAutonomousTaskRequest,
  UpdateAutonomousTaskRequest,
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

export function useTasks() {
  return useQuery({
    queryKey: [api.tasks.list.path],
    queryFn: async () => {
      const res = await fetch(api.tasks.list.path, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch tasks");
      return parseWithLogging(api.tasks.list.responses[200], await res.json(), "tasks.list");
    },
  });
}

export function useCreateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: CreateAutonomousTaskRequest) => {
      const validated = api.tasks.create.input.parse(data);
      const res = await fetch(api.tasks.create.path, {
        method: api.tasks.create.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 400) {
          const err = parseWithLogging(api.tasks.create.responses[400], await res.json(), "tasks.create[400]");
          throw new Error(err.message);
        }
        throw new Error("Failed to create task");
      }
      return parseWithLogging(api.tasks.create.responses[201], await res.json(), "tasks.create[201]");
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: [api.tasks.list.path] });
    },
  });
}

export function useUpdateTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, updates }: { id: number; updates: UpdateAutonomousTaskRequest }) => {
      const validated = api.tasks.update.input.parse(updates);
      const url = buildUrl(api.tasks.update.path, { id });
      const res = await fetch(url, {
        method: api.tasks.update.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 400) {
          const err = parseWithLogging(api.tasks.update.responses[400], await res.json(), "tasks.update[400]");
          throw new Error(err.message);
        }
        if (res.status === 404) {
          const err = parseWithLogging(api.tasks.update.responses[404], await res.json(), "tasks.update[404]");
          throw new Error(err.message);
        }
        throw new Error("Failed to update task");
      }

      return parseWithLogging(api.tasks.update.responses[200], await res.json(), "tasks.update[200]");
    },
    onSuccess: async (_data, vars) => {
      await qc.invalidateQueries({ queryKey: [api.tasks.list.path] });
      await qc.invalidateQueries({ queryKey: [api.tasks.runs.path, vars.id] });
    },
  });
}

export function useDeleteTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      const url = buildUrl(api.tasks.delete.path, { id });
      const res = await fetch(url, {
        method: api.tasks.delete.method,
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 404) {
          const err = parseWithLogging(api.tasks.delete.responses[404], await res.json(), "tasks.delete[404]");
          throw new Error(err.message);
        }
        throw new Error("Failed to delete task");
      }
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: [api.tasks.list.path] });
    },
  });
}

export function useRunTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, dryRun }: { id: number; dryRun?: boolean }) => {
      const url = buildUrl(api.tasks.run.path, { id });
      const validated = api.tasks.run.input.parse({ dryRun });

      const res = await fetch(url, {
        method: api.tasks.run.method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(validated),
        credentials: "include",
      });

      if (!res.ok) {
        if (res.status === 404) {
          const err = parseWithLogging(api.tasks.run.responses[404], await res.json(), "tasks.run[404]");
          throw new Error(err.message);
        }
        throw new Error("Failed to run task");
      }

      return parseWithLogging(api.tasks.run.responses[201], await res.json(), "tasks.run[201]");
    },
    onSuccess: async (_data, vars) => {
      await qc.invalidateQueries({ queryKey: [api.tasks.list.path] });
      await qc.invalidateQueries({ queryKey: [api.tasks.runs.path, vars.id] });
    },
  });
}

export function useTaskRuns(taskId?: number) {
  return useQuery({
    enabled: typeof taskId === "number" && Number.isFinite(taskId),
    queryKey: [api.tasks.runs.path, taskId ?? -1],
    queryFn: async () => {
      const url = buildUrl(api.tasks.runs.path, { id: taskId as number });
      const res = await fetch(url, { credentials: "include" });
      if (res.status === 404) return null;
      if (!res.ok) throw new Error("Failed to fetch task runs");
      return parseWithLogging(api.tasks.runs.responses[200], await res.json(), "tasks.runs[200]");
    },
  });
}
