import type { Express } from "express";
import type { Server } from "http";
import OpenAI from "openai";
import { z } from "zod";
import { storage } from "./storage";
import { api } from "@shared/routes";

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
  if (bots.length === 0) {
    await storage.createBotProfile({
      slug: "buddy",
      displayName: "Buddy",
      isDefault: true,
      systemPrompt:
        "You are Buddy, a realistic, grounded assistant. You ask one clarifying question when needed, otherwise you propose a concrete next step and execute. You help the user build autonomous systems responsibly. Be concise, practical, and honest about limitations.",
      traits: {
        vibe: "calm",
        style: "practical",
        focus: "autonomy",
      },
    });

    await storage.createBotProfile({
      slug: "research",
      displayName: "Research Buddy",
      isDefault: false,
      systemPrompt:
        "You are Research Buddy. You generate structured research plans, checklists, and summaries with sources when provided. Keep output organized and actionable.",
      traits: {
        vibe: "analytical",
        output: "structured",
      },
    });
  }

  const convs = await storage.listConversations();
  if (convs.length === 0) {
    const conv = await storage.createConversation("Welcome to Buddy");
    await storage.createMessage(
      conv.id,
      "assistant",
      "Tell me what you want to automate first. We can start with one small loop: pick a goal, break it into tasks, and schedule runs.",
    );
  }

  const tasks = await storage.listTasks();
  if (tasks.length === 0) {
    await storage.createTask({
      title: "Daily autonomy check-in",
      objective:
        "Review current project goal, propose the next 3 actions, and draft a message for me to approve.",
      status: "paused",
      priority: 3,
    });
  }
}

async function runAutonomousTask(taskId: number, dryRun: boolean) {
  const tasks = await storage.listTasks();
  const task = tasks.find((t) => t.id === taskId);
  if (!task) return undefined;

  const bot = (await storage.getDefaultBotProfile()) ?? (await storage.getBotProfileBySlug("buddy"));
  const system = bot?.systemPrompt ?? "You are a helpful assistant.";

  const prompt = `Task title: ${task.title}\nObjective: ${task.objective}\n\nReturn JSON with keys: steps (array of {title, description}), risks (array of strings), and a short "messageToUser" string. Keep it practical.`;

  const response = await openai.chat.completions.create({
    model: "gpt-5.2",
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

  await storage.updateTask(taskId, {
    status: "complete",
  } as any);

  return await storage.createTaskRun(taskId, "complete", summary, parsed);
}

export async function registerRoutes(
  httpServer: Server,
  app: Express,
): Promise<Server> {
  await ensureSeeded();

  // Bots
  app.get(api.bots.list.path, async (req, res) => {
    const bots = await storage.listBotProfiles();
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

      const system =
        bot?.systemPrompt ??
        "You are Buddy, a helpful assistant that is realistic and practical.";

      const userMsg = await storage.createMessage(
        conversationId,
        "user",
        input.content,
      );

      const history = await storage.getMessages(conversationId);
      const messagesForModel = [
        { role: "system" as const, content: system },
        ...history.map((m) => ({
          role: m.role as "user" | "assistant",
          content: m.content,
        })),
      ];

      const completion = await openai.chat.completions.create({
        model: "gpt-5.2",
        messages: messagesForModel,
        max_completion_tokens: 1800,
      });

      const assistantText = completion.choices[0]?.message?.content ?? "";
      const assistantMsg = await storage.createMessage(
        conversationId,
        "assistant",
        assistantText,
      );

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

    const system =
      bot?.systemPrompt ?? "You are Buddy, a helpful assistant.";

    const userMsg = await storage.createMessage(
      conversationId,
      "user",
      input.content,
    );

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
      model: "gpt-5.2",
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

      const assistantMsg = await storage.createMessage(
        conversationId,
        "assistant",
        assistantText,
      );

      res.write(`data: ${JSON.stringify({ type: "done", conversationId, messageId: assistantMsg.id })}\n\n`);
      res.end();
    } catch (e) {
      res.write(`data: ${JSON.stringify({ type: "error", error: "Stream failed" })}\n\n`);
      res.end();
    }
  });

  // Tasks
  app.get(api.tasks.list.path, async (req, res) => {
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

  return httpServer;
}
