import type { Express } from "express";
import type { Server } from "http";
import OpenAI from "openai";
import { z } from "zod";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { ALL_BOTS } from "./seed-bots";
import { DIVISIONS, insertBotMetricSchema, insertBotErrorSchema, insertBotFinancialSchema, insertAlertRuleSchema } from "@shared/schema";

const openai = new OpenAI({
  apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY,
  baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
});

function zodValidationError(err: z.ZodError) {
  return {
    message: err.errors[0]?.message ?? "Invalid request",
    field: err.errors[0]?.path?.join("."),
  };
}

async function ensureSeeded() {
  const bots = await storage.listBotProfiles();
  if (bots.length < 10) {
    if (bots.length > 0) {
      // don't double-seed
    } else {
      for (const botData of ALL_BOTS) {
        try {
          await storage.createBotProfile(botData);
        } catch (e: any) {
          if (e?.code === "23505") continue; // unique violation, skip
          console.error(`Seed bot ${botData.slug} failed:`, e?.message);
        }
      }
    }
  }

  const convs = await storage.listConversations();
  if (convs.length === 0) {
    const conv = await storage.createConversation("Welcome to DreamCo Empire OS");
    await storage.createMessage(
      conv.id,
      "assistant",
      "Welcome to DreamCo Empire OS. I'm your central AI brain, coordinating 250+ specialized bots across 16 divisions to build autonomous wealth-generation systems. Tell me what you want to automate first, and I'll route you to the right division and bots.",
    );
  }

  const tasks = await storage.listTasks();
  if (tasks.length === 0) {
    await storage.createTask({
      title: "Empire startup diagnostic",
      objective: "Scan all divisions, verify bot readiness, and generate an empire health report with recommended first actions.",
      status: "pending",
      priority: 1,
      autonomyMode: "guided",
      division: "CommandCore",
    });
  }
}

async function runAutonomousTask(taskId: number, dryRun: boolean) {
  const tasks = await storage.listTasks();
  const task = tasks.find((t) => t.id === taskId);
  if (!task) return undefined;

  const bot = task.assignedBotId
    ? (await storage.listBotProfiles()).find(b => b.id === task.assignedBotId)
    : (await storage.getDefaultBotProfile()) ?? (await storage.getBotProfileBySlug("dreambot"));

  const system = bot?.systemPrompt ?? "You are the central AI brain of DreamCo Empire OS.";

  const modeInstructions = task.autonomyMode === "full-autonomy"
    ? "Execute fully. Report results only."
    : task.autonomyMode === "semi-autonomous"
      ? "Execute low-risk steps automatically. Flag high-risk decisions for approval."
      : "Propose a plan. Wait for user approval before any execution.";

  const prompt = `Division: ${task.division}\nAutonomy Mode: ${task.autonomyMode} - ${modeInstructions}\nTask: ${task.title}\nObjective: ${task.objective}\n\nReturn JSON with keys: steps (array of {title, description, risk: "low"|"medium"|"high"}), risks (array of strings), estimatedRevenue (string), and "messageToUser" string. Be practical and revenue-focused.`;

  const response = await openai.chat.completions.create({
    model: "gpt-4.1-mini",
    messages: [
      { role: "system", content: system },
      { role: "user", content: prompt },
    ],
    response_format: { type: "json_object" },
    max_completion_tokens: 1200,
  });

  const content = response.choices[0]?.message?.content ?? "{}";
  let parsed: any = {};
  try {
    parsed = JSON.parse(content);
  } catch {
    parsed = { raw: content };
  }

  const summary =
    typeof parsed?.messageToUser === "string"
      ? parsed.messageToUser
      : "Generated task run output.";

  if (dryRun) {
    return await storage.createTaskRun(taskId, "dry_run", summary, parsed);
  }

  await storage.updateTask(taskId, { status: "complete" } as any);
  return await storage.createTaskRun(taskId, "complete", summary, parsed);
}

export async function registerRoutes(
  httpServer: Server,
  app: Express,
): Promise<Server> {
  await ensureSeeded();

  // Bots
  app.get(api.bots.list.path, async (req, res) => {
    const division = req.query.division as string | undefined;
    if (division) {
      const bots = await storage.listBotsByDivision(division);
      return res.json(bots);
    }
    const bots = await storage.listBotProfiles();
    res.json(bots);
  });

  app.get(api.bots.byDivision.path, async (req, res) => {
    const division = req.params.division;
    const bots = await storage.listBotsByDivision(division);
    res.json(bots);
  });

  app.post(api.bots.create.path, async (req, res) => {
    try {
      const input = api.bots.create.input.parse(req.body);
      const created = await storage.createBotProfile(input);
      res.status(201).json(created);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json(zodValidationError(err));
      }
      throw err;
    }
  });

  app.put(api.bots.update.path, async (req, res) => {
    const id = Number(req.params.id);
    try {
      const updates = api.bots.update.input.parse(req.body);
      const updated = await storage.updateBotProfile(id, updates);
      if (!updated) return res.status(404).json({ message: "Bot not found" });
      res.json(updated);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json(zodValidationError(err));
      }
      throw err;
    }
  });

  app.post(api.bots.setDefault.path, async (req, res) => {
    const id = Number(req.params.id);
    const updated = await storage.setDefaultBotProfile(id);
    if (!updated) return res.status(404).json({ message: "Bot not found" });
    res.json(updated);
  });

  // Conversations
  app.get(api.conversations.list.path, async (req, res) => {
    const convs = await storage.listConversations();
    res.json(convs);
  });

  app.get(api.conversations.get.path, async (req, res) => {
    const id = Number(req.params.id);
    const conv = await storage.getConversation(id);
    if (!conv) return res.status(404).json({ message: "Conversation not found" });
    const msgs = await storage.getMessages(id);
    res.json({ conversation: conv, messages: msgs });
  });

  app.post(api.conversations.create.path, async (req, res) => {
    try {
      const input = api.conversations.create.input?.parse(req.body) ?? {};
      const title = input?.title?.trim() || "New chat";
      const conv = await storage.createConversation(title);
      res.status(201).json(conv);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json(zodValidationError(err));
      }
      throw err;
    }
  });

  app.delete(api.conversations.delete.path, async (req, res) => {
    const id = Number(req.params.id);
    const conv = await storage.getConversation(id);
    if (!conv) return res.status(404).json({ message: "Conversation not found" });
    await storage.deleteConversation(id);
    res.status(204).send();
  });

  app.post(api.conversations.createMessage.path, async (req, res) => {
    const conversationId = Number(req.params.id);
    const conv = await storage.getConversation(conversationId);
    if (!conv) return res.status(404).json({ message: "Conversation not found" });

    try {
      const input = api.conversations.createMessage.input.parse(req.body);
      const bot = input.botSlug
        ? await storage.getBotProfileBySlug(input.botSlug)
        : await storage.getDefaultBotProfile();

      const system = bot?.systemPrompt ?? "You are the central AI brain of DreamCo Empire OS.";

      const userMsg = await storage.createMessage(conversationId, "user", input.content);

      const history = await storage.getMessages(conversationId);
      const messagesForModel = [
        { role: "system" as const, content: system },
        ...history.map((m) => ({
          role: m.role as "user" | "assistant",
          content: m.content,
        })),
      ];

      const completion = await openai.chat.completions.create({
        model: "gpt-4.1-mini",
        messages: messagesForModel,
        max_completion_tokens: 1800,
      });

      const assistantText = completion.choices[0]?.message?.content ?? "";
      const assistantMsg = await storage.createMessage(conversationId, "assistant", assistantText);

      res.status(201).json({ message: userMsg, assistantMessage: assistantMsg });
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json(zodValidationError(err));
      }
      throw err;
    }
  });

  // Streaming SSE
  app.post(api.conversations.stream.path, async (req, res) => {
    const conversationId = Number(req.params.id);
    const conv = await storage.getConversation(conversationId);
    if (!conv) return res.status(404).json({ message: "Conversation not found" });

    let input: { content: string; botSlug?: string };
    try {
      input = api.conversations.stream.input.parse(req.body);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json(zodValidationError(err));
      }
      throw err;
    }

    const bot = input.botSlug
      ? await storage.getBotProfileBySlug(input.botSlug)
      : await storage.getDefaultBotProfile();

    const system = bot?.systemPrompt ?? "You are the central AI brain of DreamCo Empire OS.";

    const userMsg = await storage.createMessage(conversationId, "user", input.content);

    const history = await storage.getMessages(conversationId);
    const messagesForModel = [
      { role: "system" as const, content: system },
      ...history.map((m) => ({
        role: m.role as "user" | "assistant",
        content: m.content,
      })),
    ];

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    const stream = await openai.chat.completions.create({
      model: "gpt-4.1-mini",
      messages: messagesForModel,
      stream: true,
      max_completion_tokens: 1800,
    });

    let assistantText = "";
    try {
      for await (const chunk of stream) {
        const delta = chunk.choices[0]?.delta?.content ?? "";
        if (!delta) continue;
        assistantText += delta;
        res.write(`data: ${JSON.stringify({ type: "delta", content: delta, messageId: userMsg.id, conversationId })}\n\n`);
      }

      const assistantMsg = await storage.createMessage(conversationId, "assistant", assistantText);
      res.write(`data: ${JSON.stringify({ type: "done", conversationId, messageId: assistantMsg.id })}\n\n`);
      res.end();
    } catch (e) {
      res.write(`data: ${JSON.stringify({ type: "error", error: "Stream failed" })}\n\n`);
      res.end();
    }
  });

  // Tasks
  app.get(api.tasks.list.path, async (req, res) => {
    const division = req.query.division as string | undefined;
    if (division) {
      const tasks = await storage.listTasksByDivision(division);
      return res.json(tasks);
    }
    const tasks = await storage.listTasks();
    res.json(tasks);
  });

  app.post(api.tasks.create.path, async (req, res) => {
    try {
      const input = api.tasks.create.input.parse(req.body);
      const task = await storage.createTask(input as any);
      res.status(201).json(task);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json(zodValidationError(err));
      }
      throw err;
    }
  });

  app.put(api.tasks.update.path, async (req, res) => {
    const id = Number(req.params.id);
    try {
      const updates = api.tasks.update.input.parse(req.body);
      const task = await storage.updateTask(id, updates as any);
      if (!task) return res.status(404).json({ message: "Task not found" });
      res.json(task);
    } catch (err) {
      if (err instanceof z.ZodError) {
        return res.status(400).json(zodValidationError(err));
      }
      throw err;
    }
  });

  app.delete(api.tasks.delete.path, async (req, res) => {
    const id = Number(req.params.id);
    const tasks = await storage.listTasks();
    const exists = tasks.some((t) => t.id === id);
    if (!exists) return res.status(404).json({ message: "Task not found" });
    await storage.deleteTask(id);
    res.status(204).send();
  });

  app.post(api.tasks.run.path, async (req, res) => {
    const id = Number(req.params.id);
    const body = api.tasks.run.input?.safeParse(req.body);
    const dryRun = body?.success ? Boolean(body.data?.dryRun) : false;

    const tasks = await storage.listTasks();
    const exists = tasks.some((t) => t.id === id);
    if (!exists) return res.status(404).json({ message: "Task not found" });

    const run = await runAutonomousTask(id, dryRun);
    if (!run) return res.status(404).json({ message: "Task not found" });
    res.status(201).json(run);
  });

  app.get(api.tasks.runs.path, async (req, res) => {
    const id = Number(req.params.id);
    const tasks = await storage.listTasks();
    const exists = tasks.some((t) => t.id === id);
    if (!exists) return res.status(404).json({ message: "Task not found" });
    const runs = await storage.listTaskRuns(id);
    res.json(runs);
  });

  // Empire
  app.get(api.empire.overview.path, async (req, res) => {
    const bots = await storage.listBotProfiles();
    const tasks = await storage.listTasks();
    const divCounts = await storage.getBotCountByDivision();
    const autonomySetting = await storage.getSetting("autonomy_mode");
    const autonomyMode = (autonomySetting?.value as any)?.mode ?? "guided";

    const divisions = DIVISIONS.map(d => {
      const divBots = bots.filter(b => b.division === d);
      const divTasks = tasks.filter(t => t.division === d);
      return {
        division: d,
        botCount: divBots.length,
        activeTasks: divTasks.filter(t => t.status === "running" || t.status === "pending").length,
        completedTasks: divTasks.filter(t => t.status === "complete").length,
        revenue: divBots.length > 0 ? `$${(divBots.length * 199).toLocaleString()}/mo potential` : "$0",
      };
    });

    res.json({
      totalBots: bots.length,
      totalDivisions: DIVISIONS.length,
      activeTasks: tasks.filter(t => t.status === "running" || t.status === "pending").length,
      completedTasks: tasks.filter(t => t.status === "complete").length,
      autonomyMode,
      divisions,
    });
  });

  app.get(api.empire.divisions.path, async (req, res) => {
    const counts = await storage.getBotCountByDivision();
    res.json(counts);
  });

  app.get(api.empire.settings.get.path, async (req, res) => {
    const key = req.params.key;
    const setting = await storage.getSetting(key);
    if (!setting) return res.status(404).json({ message: "Setting not found" });
    res.json(setting);
  });

  app.put(api.empire.settings.set.path, async (req, res) => {
    const key = req.params.key;
    const { value } = req.body;
    const setting = await storage.upsertSetting(key, value);
    res.json(setting);
  });

  // Bot Metrics & Tracking
  app.get("/api/metrics/health", async (_req, res) => {
    const summary = await storage.getBotHealthSummary();
    res.json(summary);
  });

  app.get("/api/metrics/bot/:botId", async (req, res) => {
    const botId = Number(req.params.botId);
    const metrics = await storage.listBotMetrics(botId);
    res.json(metrics);
  });

  app.post("/api/metrics", async (req, res) => {
    try {
      const input = insertBotMetricSchema.parse(req.body);
      const metric = await storage.createBotMetric(input);
      res.status(201).json(metric);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      res.status(400).json({ message: "Invalid metric data" });
    }
  });

  app.get("/api/errors", async (req, res) => {
    const botId = req.query.botId ? Number(req.query.botId) : undefined;
    const errors = await storage.listBotErrors(botId);
    res.json(errors);
  });

  app.post("/api/errors", async (req, res) => {
    try {
      const input = insertBotErrorSchema.parse(req.body);
      const error = await storage.createBotError(input);
      res.status(201).json(error);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      res.status(400).json({ message: "Invalid error data" });
    }
  });

  app.put("/api/errors/:id/resolve", async (req, res) => {
    const id = Number(req.params.id);
    const resolved = await storage.resolveError(id);
    if (!resolved) return res.status(404).json({ message: "Error not found" });
    res.json(resolved);
  });

  app.get("/api/interactions", async (req, res) => {
    const botId = req.query.botId ? Number(req.query.botId) : undefined;
    const limit = req.query.limit ? Number(req.query.limit) : 50;
    const interactions = await storage.listBotInteractions(botId, limit);
    res.json(interactions);
  });

  app.get("/api/financials", async (req, res) => {
    const botId = req.query.botId ? Number(req.query.botId) : undefined;
    const financials = await storage.listBotFinancials(botId);
    res.json(financials);
  });

  app.post("/api/financials", async (req, res) => {
    try {
      const input = insertBotFinancialSchema.parse(req.body);
      const financial = await storage.createBotFinancial(input);
      res.status(201).json(financial);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      res.status(400).json({ message: "Invalid financial data" });
    }
  });

  app.get("/api/alerts", async (_req, res) => {
    const rules = await storage.listAlertRules();
    res.json(rules);
  });

  app.post("/api/alerts", async (req, res) => {
    try {
      const input = insertAlertRuleSchema.parse(req.body);
      const rule = await storage.createAlertRule(input);
      res.status(201).json(rule);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      res.status(400).json({ message: "Invalid alert rule data" });
    }
  });

  app.put("/api/alerts/:id/toggle", async (req, res) => {
    const id = Number(req.params.id);
    const { enabled } = req.body;
    const rule = await storage.toggleAlertRule(id, enabled);
    if (!rule) return res.status(404).json({ message: "Alert rule not found" });
    res.json(rule);
  });

  // Seed default alert rules if none exist
  const existingAlerts = await storage.listAlertRules();
  if (existingAlerts.length === 0) {
    const defaultAlerts = [
      { name: "Task Failure Cascade", trigger: "task_fail_consecutive", action: "Restart bot / rollback config", threshold: 5 },
      { name: "CPU Overload", trigger: "cpu_high", action: "Scale resources / notify engineer", threshold: 85 },
      { name: "Unauthorized Access", trigger: "unauthorized_access", action: "Lock bot / send security alert", threshold: 1 },
      { name: "Model Drift", trigger: "model_drift", action: "Queue bot for retraining", threshold: 10 },
      { name: "High Error Rate", trigger: "high_error_rate", action: "Pause bot / notify for review", threshold: 10 },
      { name: "Revenue Drop", trigger: "revenue_drop", action: "Alert finance team / investigate", threshold: 20 },
      { name: "Bot Offline", trigger: "bot_offline", action: "Auto-restart / escalate", threshold: 1 },
    ];
    for (const alert of defaultAlerts) {
      await storage.createAlertRule(alert);
    }
  }

  return httpServer;
}
