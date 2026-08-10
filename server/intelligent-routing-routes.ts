import type { Express } from "express";
import { ZodError } from "zod";

import { compileIntelligentTask } from "./intelligent-task-router";
import { compileModelTask, protocolForProvider } from "./model-protocol-compiler";

export function registerIntelligentRoutingRoutes(app: Express) {
  app.post("/api/buddy/task/compile", (req, res) => {
    try {
      const result = compileIntelligentTask(req.body);
      return res.status(200).json(result);
    } catch (error) {
      if (error instanceof ZodError) {
        return res.status(400).json({
          error: "invalid_task_compilation_request",
          issues: error.issues,
        });
      }
      const message = error instanceof Error ? error.message : String(error);
      return res.status(500).json({ error: "task_compilation_failed", message });
    }
  });

  app.post("/api/buddy/model/compile-protocol", (req, res) => {
    try {
      const { providerId, exactModelId, task } = req.body ?? {};
      if (typeof providerId !== "string" || !providerId.trim()) {
        return res.status(400).json({ error: "providerId is required" });
      }
      if (typeof exactModelId !== "string" || !exactModelId.trim()) {
        return res.status(400).json({ error: "exactModelId is required" });
      }
      const protocol = protocolForProvider(providerId);
      const compiled = compileModelTask(task, protocol, exactModelId);
      return res.status(200).json({
        schema: "dreamco.model_protocol_compilation.v1",
        providerId,
        protocol,
        liveProviderCallExecuted: false,
        compiled,
      });
    } catch (error) {
      if (error instanceof ZodError) {
        return res.status(400).json({
          error: "invalid_model_protocol_request",
          issues: error.issues,
        });
      }
      const message = error instanceof Error ? error.message : String(error);
      return res.status(500).json({ error: "model_protocol_compilation_failed", message });
    }
  });
}
