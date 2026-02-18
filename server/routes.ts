import type { Express } from "express";
import type { Server } from "http";
import OpenAI from "openai";
import { z } from "zod";
import { sql } from "drizzle-orm";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { ALL_BOTS } from "./seed-bots";
import { DIVISIONS, insertBotMetricSchema, insertBotErrorSchema, insertBotFinancialSchema, insertAlertRuleSchema, insertDealSchema, insertDebugEventSchema, insertAutoFixSchema, insertRevenueLeakSchema, insertSecurityScanSchema } from "@shared/schema";
import { calculateRealEstate, calculateCarFlip, type RealEstateInputs, type CarFlipInputs } from "@shared/deal-calculations";
import { getUncachableStripeClient, getStripePublishableKey } from "./stripeClient";
import { db } from "./db";

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

  app.get("/api/bots/:id", async (req, res) => {
    const id = Number(req.params.id);
    if (isNaN(id)) return res.status(400).json({ message: "Invalid bot ID" });
    const bot = await storage.getBotProfileById(id);
    if (!bot) return res.status(404).json({ message: "Bot not found" });
    res.json(bot);
  });

  const botControlsSchema = z.object({
    autonomyLevel: z.enum(["guided", "semi-autonomous", "full-autonomy"]).optional(),
    operationalMode: z.enum(["sandbox", "live", "offline"]).optional(),
  }).refine(d => d.autonomyLevel || d.operationalMode, { message: "At least one field required" });

  const TIER_AUTONOMY_MAP: Record<string, string[]> = {
    free: ["guided"],
    pro: ["guided", "semi-autonomous"],
    enterprise: ["guided", "semi-autonomous", "full-autonomy"],
    elite: ["guided", "semi-autonomous", "full-autonomy"],
  };

  app.patch("/api/bots/:id/controls", async (req, res) => {
    const id = Number(req.params.id);
    if (isNaN(id)) return res.status(400).json({ message: "Invalid bot ID" });
    try {
      const parsed = botControlsSchema.parse(req.body);
      if (parsed.autonomyLevel) {
        const bot = await storage.getBotProfile(id);
        if (!bot) return res.status(404).json({ message: "Bot not found" });
        const allowed = TIER_AUTONOMY_MAP[bot.tier] ?? ["guided"];
        if (!allowed.includes(parsed.autonomyLevel)) {
          return res.status(403).json({
            message: `Autonomy level "${parsed.autonomyLevel}" requires a higher tier. Current tier: ${bot.tier}`,
          });
        }
      }
      const updates: Record<string, string> = {};
      if (parsed.autonomyLevel) updates.autonomyLevel = parsed.autonomyLevel;
      if (parsed.operationalMode) updates.operationalMode = parsed.operationalMode;
      const updated = await storage.updateBotProfile(id, updates);
      if (!updated) return res.status(404).json({ message: "Bot not found" });
      res.json(updated);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      throw err;
    }
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

  // ─── Deal Analyzer Routes ──────────────────────────────────────────

  app.get("/api/deals", async (_req, res) => {
    const allDeals = await storage.listDeals();
    res.json(allDeals);
  });

  app.get("/api/deals/kpis", async (_req, res) => {
    const kpis = await storage.getDealKpis();
    res.json(kpis);
  });

  app.get("/api/deals/:id", async (req, res) => {
    const id = Number(req.params.id);
    if (isNaN(id)) return res.status(400).json({ message: "Invalid deal ID" });
    const deal = await storage.getDeal(id);
    if (!deal) return res.status(404).json({ message: "Deal not found" });
    res.json(deal);
  });

  app.post("/api/deals", async (req, res) => {
    try {
      const { name, dealType, inputs: rawInputs } = req.body;
      if (!name || !dealType || !rawInputs) {
        return res.status(400).json({ message: "name, dealType, and inputs are required" });
      }

      let results: any;
      let status: string;
      let netProfit = 0;
      let roi = 0;
      let capitalEfficiency = 0;
      let daysHeld = 0;
      let cashInvested = 0;

      if (dealType === "real_estate") {
        const calc = calculateRealEstate(rawInputs as RealEstateInputs);
        results = calc;
        status = calc.status;
        netProfit = calc.netProfit;
        roi = Math.round(calc.roi);
        capitalEfficiency = Math.round(calc.capitalEfficiency * 10000);
        daysHeld = rawInputs.daysHeld || 0;
        cashInvested = rawInputs.cashInvested || 0;
      } else {
        const calc = calculateCarFlip(rawInputs as CarFlipInputs);
        results = calc;
        status = calc.status;
        netProfit = calc.netProfit;
        roi = Math.round(calc.roi);
        capitalEfficiency = Math.round(calc.capitalEfficiency * 10000);
        daysHeld = rawInputs.daysHeld || 0;
        cashInvested = rawInputs.cashInvested || 0;
      }

      const deal = await storage.createDeal({
        name,
        dealType,
        status,
        inputs: rawInputs,
        results,
        netProfit,
        roi,
        capitalEfficiency,
        daysHeld,
        cashInvested,
      });
      res.status(201).json(deal);
    } catch (err: any) {
      res.status(400).json({ message: err.message || "Invalid deal data" });
    }
  });

  app.delete("/api/deals/:id", async (req, res) => {
    const id = Number(req.params.id);
    if (isNaN(id)) return res.status(400).json({ message: "Invalid deal ID" });
    const deal = await storage.getDeal(id);
    if (!deal) return res.status(404).json({ message: "Deal not found" });
    await storage.deleteDeal(id);
    res.status(204).send();
  });

  // ─── Debug Intelligence System Routes ──────────────────────────────────

  app.get("/api/debug/overview", async (_req, res) => {
    const overview = await storage.getDebugOverview();
    res.json(overview);
  });

  app.get("/api/debug/events", async (req, res) => {
    const status = req.query.status as string | undefined;
    const botId = req.query.botId ? Number(req.query.botId) : undefined;
    const events = await storage.listDebugEvents(status, botId);
    res.json(events);
  });

  app.post("/api/debug/events", async (req, res) => {
    try {
      const input = insertDebugEventSchema.parse(req.body);
      const event = await storage.createDebugEvent(input);
      res.status(201).json(event);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      throw err;
    }
  });

  app.patch("/api/debug/events/:id/resolve", async (req, res) => {
    const id = Number(req.params.id);
    const { resolution } = req.body;
    const updated = await storage.resolveDebugEvent(id, resolution || "Resolved");
    if (!updated) return res.status(404).json({ message: "Event not found" });
    res.json(updated);
  });

  app.get("/api/debug/auto-fixes", async (req, res) => {
    const status = req.query.status as string | undefined;
    const fixes = await storage.listAutoFixes(status);
    res.json(fixes);
  });

  app.post("/api/debug/auto-fixes", async (req, res) => {
    try {
      const input = insertAutoFixSchema.parse(req.body);
      const fix = await storage.createAutoFix(input);
      if (fix.confidence >= 90) {
        const applied = await storage.applyAutoFix(fix.id);
        return res.status(201).json(applied);
      }
      res.status(201).json(fix);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      throw err;
    }
  });

  app.patch("/api/debug/auto-fixes/:id/apply", async (req, res) => {
    const id = Number(req.params.id);
    const applied = await storage.applyAutoFix(id);
    if (!applied) return res.status(404).json({ message: "Fix not found" });
    res.json(applied);
  });

  app.patch("/api/debug/auto-fixes/:id/reject", async (req, res) => {
    const id = Number(req.params.id);
    const rejected = await storage.rejectAutoFix(id);
    if (!rejected) return res.status(404).json({ message: "Fix not found" });
    res.json(rejected);
  });

  app.get("/api/debug/revenue-leaks", async (req, res) => {
    const status = req.query.status as string | undefined;
    const leaks = await storage.listRevenueLeaks(status);
    res.json(leaks);
  });

  app.post("/api/debug/revenue-leaks", async (req, res) => {
    try {
      const input = insertRevenueLeakSchema.parse(req.body);
      const leak = await storage.createRevenueLeak(input);
      res.status(201).json(leak);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      throw err;
    }
  });

  app.patch("/api/debug/revenue-leaks/:id/resolve", async (req, res) => {
    const id = Number(req.params.id);
    const { notes } = req.body;
    const resolved = await storage.resolveRevenueLeak(id, notes || "Resolved");
    if (!resolved) return res.status(404).json({ message: "Revenue leak not found" });
    res.json(resolved);
  });

  app.get("/api/debug/security-scans", async (req, res) => {
    const status = req.query.status as string | undefined;
    const scans = await storage.listSecurityScans(status);
    res.json(scans);
  });

  app.post("/api/debug/security-scans", async (req, res) => {
    try {
      const input = insertSecurityScanSchema.parse(req.body);
      const scan = await storage.createSecurityScan(input);
      res.status(201).json(scan);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      throw err;
    }
  });

  app.patch("/api/debug/security-scans/:id/remediate", async (req, res) => {
    const id = Number(req.params.id);
    const { mitigation } = req.body;
    const remediated = await storage.remediateSecurityScan(id, mitigation || "Remediated");
    if (!remediated) return res.status(404).json({ message: "Scan not found" });
    res.json(remediated);
  });

  app.post("/api/debug/seed", async (_req, res) => {
    const existing = await storage.listDebugEvents();
    if (existing.length > 0) {
      return res.json({ message: "Demo data already seeded", count: existing.length });
    }

    const categories = ["syntax_error", "runtime_crash", "api_failure", "auth_error", "logic_bug", "performance_issue", "ux_friction", "revenue_leak", "security_risk", "infinite_loop", "model_drift", "cost_explosion"];
    const allBots = await storage.listBotProfiles();
    const botIds = allBots.slice(0, 15).map(b => b.id);
    const summaries: Record<string, string[]> = {
      syntax_error: ["Unexpected token in response parser", "Missing semicolon in payment handler", "Invalid JSON template in email bot"],
      runtime_crash: ["Null reference in customer lookup", "Stack overflow in recursive task planner", "Out of memory during batch processing"],
      api_failure: ["Stripe webhook timeout after 30s", "OpenAI rate limit exceeded", "CRM sync returning 503"],
      auth_error: ["JWT expired for service account", "OAuth token refresh loop detected", "API key rotation missed for bot #42"],
      logic_bug: ["Commission calculator using wrong tier", "Lead scoring inverted priority weights", "Duplicate invoice generation on retry"],
      performance_issue: ["Response time >5s for search queries", "Database connection pool exhausted", "Memory leak in WebSocket handler"],
      ux_friction: ["Checkout button unresponsive on mobile", "Search results pagination broken", "Form validation error messages not visible"],
      revenue_leak: ["Failed checkout not triggering cart recovery", "Pricing page showing wrong tier features", "Abandoned cart emails not sending"],
      security_risk: ["SQL injection vector in search endpoint", "CORS misconfiguration allowing wildcard", "Unencrypted PII in log output"],
      infinite_loop: ["Task retry loop with no backoff", "Webhook echo causing infinite callbacks", "State machine stuck in processing state"],
      model_drift: ["Sentiment analysis accuracy dropped 15%", "Lead quality predictions diverging from actuals", "Price optimization suggesting below-cost items"],
      cost_explosion: ["API call volume 300% above forecast", "Cloud storage growing 50GB/day unexpectedly", "LLM token usage 5x projected budget"],
    };

    const events = [];
    for (let i = 0; i < 24; i++) {
      const cat = categories[i % categories.length];
      const sums = summaries[cat];
      const severity = cat === "security_risk" || cat === "cost_explosion" ? 8 + Math.floor(Math.random() * 3) :
                        cat === "syntax_error" || cat === "ux_friction" ? 2 + Math.floor(Math.random() * 4) :
                        4 + Math.floor(Math.random() * 5);
      const status = i < 8 ? "open" : i < 12 ? "investigating" : "resolved";
      const revenueImpact = ["revenue_leak", "cost_explosion", "api_failure"].includes(cat) ? 500 + Math.floor(Math.random() * 4500) : 0;
      events.push(await storage.createDebugEvent({
        category: cat,
        severity,
        summary: sums[i % sums.length],
        stackTrace: `Error at ${cat}.handler:${10 + i}\n  at processQueue (worker.ts:${44 + i})`,
        botId: botIds[i % botIds.length],
        status,
        resolution: status === "resolved" ? "Patched and deployed" : undefined,
        revenueImpact,
        fixPriority: severity,
      }));
    }

    const fixPatches = [
      { summary: "Fix null reference in customer lookup", before: "const name = customer.name;", after: "const name = customer?.name ?? 'Unknown';", confidence: 95 },
      { summary: "Add rate limit retry with exponential backoff", before: "await openai.chat(prompt);", after: "await retryWithBackoff(() => openai.chat(prompt), 3);", confidence: 92 },
      { summary: "Fix SQL injection in search endpoint", before: "WHERE name LIKE '%${query}%'", after: "WHERE name LIKE $1", confidence: 97 },
      { summary: "Fix commission calculation tier lookup", before: "const rate = tiers[tier - 1];", after: "const rate = tiers[Math.min(tier, tiers.length) - 1];", confidence: 78 },
      { summary: "Add connection pool limit increase", before: "pool: { max: 5 }", after: "pool: { max: 20, idleTimeoutMillis: 30000 }", confidence: 85 },
      { summary: "Fix JWT refresh token handling", before: "if (token.expired) throw new Error();", after: "if (token.expired) { token = await refreshToken(); }", confidence: 91 },
      { summary: "Add task retry backoff strategy", before: "while (!done) { retry(); }", after: "for (let i=0; i<maxRetries; i++) { await delay(2**i * 1000); retry(); }", confidence: 88 },
      { summary: "Fix CORS configuration", before: "origin: '*'", after: "origin: ALLOWED_ORIGINS", confidence: 94 },
    ];

    for (const p of fixPatches) {
      await storage.createAutoFix({
        debugEventId: events[fixPatches.indexOf(p) % events.length].id,
        botId: botIds[fixPatches.indexOf(p) % botIds.length],
        patchSummary: p.summary,
        codeBefore: p.before,
        codeAfter: p.after,
        confidence: p.confidence,
        status: p.confidence >= 90 ? "applied" : "queued",
      });
    }

    const leakTypes = ["failed_checkout", "broken_funnel", "pricing_error", "cart_abandonment", "api_overuse", "subscription_churn"];
    for (let i = 0; i < 6; i++) {
      await storage.createRevenueLeak({
        botId: botIds[i % botIds.length],
        leakType: leakTypes[i],
        impactEstimate: 1000 + Math.floor(Math.random() * 9000),
        status: i < 4 ? "open" : "resolved",
        notes: i >= 4 ? "Patched and verified" : undefined,
      });
    }

    const scanTypes = ["dependency_audit", "code_scan", "config_review", "penetration_test", "compliance_check"];
    const findings = [
      "Outdated dependency with known CVE-2025-1234",
      "Hardcoded credentials in config file",
      "Missing rate limiting on public endpoints",
      "XSS vulnerability in user input display",
      "Insecure deserialization in webhook handler",
    ];
    for (let i = 0; i < 5; i++) {
      await storage.createSecurityScan({
        botId: botIds[i % botIds.length],
        scanType: scanTypes[i],
        finding: findings[i],
        severity: 6 + Math.floor(Math.random() * 4),
        status: i < 3 ? "open" : "remediated",
        mitigation: i >= 3 ? "Patched and deployed" : undefined,
      });
    }

    res.json({ message: "Demo data seeded", events: events.length, fixes: fixPatches.length, leaks: 6, scans: 5 });
  });

  // ─── Stripe Payment Routes ───────────────────────────────────────────

  app.get("/api/stripe/publishable-key", async (_req, res) => {
    try {
      const key = await getStripePublishableKey();
      res.json({ publishableKey: key });
    } catch (error: any) {
      console.error("Failed to get Stripe publishable key:", error.message);
      res.status(500).json({ error: "Stripe not configured" });
    }
  });

  app.get("/api/stripe/products", async (_req, res) => {
    try {
      const result = await db.execute(sql`
        SELECT 
          p.id as product_id,
          p.name as product_name,
          p.description as product_description,
          p.active as product_active,
          p.metadata as product_metadata,
          pr.id as price_id,
          pr.unit_amount,
          pr.currency,
          pr.recurring,
          pr.active as price_active
        FROM stripe.products p
        LEFT JOIN stripe.prices pr ON pr.product = p.id AND pr.active = true
        WHERE p.active = true
        ORDER BY p.name, pr.unit_amount
      `);

      const productsMap = new Map<string, any>();
      for (const row of result.rows) {
        const r = row as any;
        if (!productsMap.has(r.product_id)) {
          productsMap.set(r.product_id, {
            id: r.product_id,
            name: r.product_name,
            description: r.product_description,
            metadata: r.product_metadata,
            prices: [],
          });
        }
        if (r.price_id) {
          productsMap.get(r.product_id).prices.push({
            id: r.price_id,
            unit_amount: r.unit_amount,
            currency: r.currency,
            recurring: r.recurring,
          });
        }
      }

      res.json({ products: Array.from(productsMap.values()) });
    } catch (error: any) {
      console.error("Failed to list products:", error.message);
      res.json({ products: [] });
    }
  });

  app.post("/api/stripe/checkout", async (req, res) => {
    try {
      const { priceId } = req.body;
      if (!priceId) {
        return res.status(400).json({ error: "priceId is required" });
      }

      const stripe = await getUncachableStripeClient();
      const baseUrl = `${req.protocol}://${req.get("host")}`;

      const session = await stripe.checkout.sessions.create({
        payment_method_types: ["card"],
        line_items: [{ price: priceId, quantity: 1 }],
        mode: "subscription",
        success_url: `${baseUrl}/pricing?success=true`,
        cancel_url: `${baseUrl}/pricing?canceled=true`,
      });

      res.json({ url: session.url });
    } catch (error: any) {
      console.error("Checkout error:", error.message);
      res.status(500).json({ error: "Failed to create checkout session" });
    }
  });

  app.post("/api/stripe/portal", async (req, res) => {
    try {
      const { customerId } = req.body;
      if (!customerId) {
        return res.status(400).json({ error: "customerId is required" });
      }

      const stripe = await getUncachableStripeClient();
      const baseUrl = `${req.protocol}://${req.get("host")}`;

      const session = await stripe.billingPortal.sessions.create({
        customer: customerId,
        return_url: `${baseUrl}/pricing`,
      });

      res.json({ url: session.url });
    } catch (error: any) {
      console.error("Portal error:", error.message);
      res.status(500).json({ error: "Failed to create portal session" });
    }
  });

  return httpServer;
}
