import type { Express } from "express";
import type { Server } from "http";
import { readFileSync } from "fs";
import { resolve } from "path";
import OpenAI from "openai";
import { z } from "zod";
import { sql } from "drizzle-orm";
import multer from "multer";
import { storage } from "./storage";
import { api } from "@shared/routes";
import { ALL_BOTS as CORE_BOTS } from "./seed-bots";
import { GITHUB_BOTS } from "./seed-github-bots";
import { CODELAB_BOTS } from "./seed-codelabs";
import { BUDDY_BOT } from "./seed-buddy-bot";
import { DIVISIONS, insertBotMetricSchema, insertBotErrorSchema, insertBotFinancialSchema, insertAlertRuleSchema, insertDealSchema, insertDebugEventSchema, insertAutoFixSchema, insertRevenueLeakSchema, insertSecurityScanSchema, insertFormulaSchema, insertPlatformConnectionSchema, insertPluginSchema, insertBotMemorySchema, insertSystemSnapshotSchema, insertCostEventSchema } from "@shared/schema";
import type { BotActivityResponse } from "@shared/schema";
import { calculateRealEstate, calculateCarFlip, type RealEstateInputs, type CarFlipInputs } from "@shared/deal-calculations";
import { FORMULA_LIBRARY } from "@shared/formula-library";
import { buildEnhancedSystemPrompt } from "@shared/tool-belt";
import { getUncachableStripeClient, getStripePublishableKey } from "./stripeClient";
import { db } from "./db";
import { batchProcessWithSSE } from "./dreamco_integrations/batch";
import { registerAudioRoutes } from "./dreamco_integrations/audio";
import { LOCAL_VOICE_ID, buildLocalImagePacket, buildLocalVoicePacket } from "./mediaEngine";

const CORE_SLUGS = new Set(CORE_BOTS.map(b => b.slug));
const GITHUB_SLUGS = new Set(GITHUB_BOTS.map(b => b.slug));
const DEDUPED_GITHUB = GITHUB_BOTS.filter(b => !CORE_SLUGS.has(b.slug));
const DEDUPED_CODELAB = CODELAB_BOTS.filter(b => !CORE_SLUGS.has(b.slug) && !GITHUB_SLUGS.has(b.slug));
const ALL_BOTS = [...CORE_BOTS, ...DEDUPED_GITHUB, ...DEDUPED_CODELAB];

// ─── COST-CONTROL CONSTANTS ──────────────────────────────────────────────────
// Keep bills as close to $0 as possible. Every byte saved is a dollar saved.
const CHEAP_MODEL     = "gpt-4o-mini";   // $0.15/1M in · $0.60/1M out  (default for ALL routes)
const CHAT_MODEL      = "gpt-4.1-mini";  // same price tier, already in use for streaming
const MAX_HISTORY_MSG = 16;              // trim conversation history — prevents unbounded token growth
const MAX_CHAT_TOKENS = 2000;            // 2k is enough for 99% of responses; saves ~50% vs 4k
const CACHE_TTL_MS    = 5 * 60 * 1000;  // 5-minute result cache for expensive routes

// Simple TTL cache (avoids re-hitting API for identical requests)
const _cache = new Map<string, { result: unknown; expiresAt: number }>();
function cacheKey(...parts: unknown[]): string {
  return parts.map(p => (typeof p === "string" ? p : JSON.stringify(p))).join("|").slice(0, 512);
}
function fromCache<T>(key: string): T | null {
  const entry = _cache.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expiresAt) { _cache.delete(key); return null; }
  return entry.result as T;
}
function toCache(key: string, result: unknown): void {
  if (_cache.size > 500) {
    // evict oldest 100 entries to prevent unbounded growth
    const oldest = [..._cache.entries()].sort((a, b) => a[1].expiresAt - b[1].expiresAt).slice(0, 100);
    oldest.forEach(([k]) => _cache.delete(k));
  }
  _cache.set(key, { result, expiresAt: Date.now() + CACHE_TTL_MS });
}

// Trim conversation history to stay within token budget
function trimHistory(messages: Array<{ role: string; content: string }>, max = MAX_HISTORY_MSG) {
  if (messages.length <= max) return messages;
  // Always keep first message (context) + last (max-1) messages
  return [messages[0], ...messages.slice(-(max - 1))];
}

const openai = new OpenAI({
  apiKey: process.env.AI_INTEGRATIONS_OPENAI_API_KEY,
  baseURL: process.env.AI_INTEGRATIONS_OPENAI_BASE_URL,
});

const HAS_OPENAI_KEY = Boolean(process.env.AI_INTEGRATIONS_OPENAI_API_KEY);
const EXTERNAL_VOICE_API_KEY = process.env.BUDDY_VOICE_API_KEY;
const EXTERNAL_VOICE_API_URL = process.env.BUDDY_VOICE_TTS_URL;

function zodValidationError(err: z.ZodError) {
  return {
    message: err.errors[0]?.message ?? "Invalid request",
    field: err.errors[0]?.path?.join("."),
  };
}

const offlineDealSchema = z.object({
  title: z.string().trim().min(1, "Deal title is required").max(160),
  customerName: z.string().trim().min(1, "Customer name is required").max(120),
  customerEmail: z.string().trim().email("Valid customer email is required").max(180),
  amount: z.coerce.number().positive("Amount must be greater than 0").max(1_000_000),
  currency: z.string().trim().min(3).max(3).default("USD"),
  method: z.enum(["cash", "check", "bank_transfer", "paypal", "cash_app", "zelle", "manual_invoice", "other"]).default("manual_invoice"),
  description: z.string().trim().max(2000).default(""),
  dueDays: z.coerce.number().int().min(0).max(365).default(7),
});

const offlineDealStatusSchema = z.object({
  status: z.enum(["draft", "sent", "approved", "paid", "failed", "refunded", "cancelled"]),
  note: z.string().trim().max(1000).default(""),
});

const creatorBuildPacketSchema = z.object({
  projectType: z.enum([
    "large_open_world_game",
    "autobiography",
    "studies_to_game",
    "college_3d_simulation",
    "kids_game",
    "music_video",
    "game_app",
  ]).default("game_app"),
  title: z.string().trim().min(1, "Project title is required").max(160),
  audience: z.string().trim().max(160).default("general"),
  sourceMaterial: z.string().trim().max(5000).default(""),
  modelPreference: z.string().trim().max(80).default("buddy_recommended"),
  outputTarget: z.string().trim().max(120).default("web_prototype"),
});

type OfflineDeal = {
  id: string;
  invoiceNumber: string;
  title: string;
  customerName: string;
  customerEmail: string;
  amount: number;
  currency: string;
  method: string;
  description: string;
  status: "draft" | "sent" | "approved" | "paid" | "failed" | "refunded" | "cancelled";
  paymentInstructions: string[];
  guardrails: string[];
  createdAt: string;
  dueAt: string;
  auditTrail: Array<{ at: string; event: string; note?: string }>;
};

const OFFLINE_DEALS_SETTING = "dreamco_offline_deal_ledger";

function buildPaymentInstructions(method: string, amount: number, currency: string) {
  const formatted = new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount);
  const base = [
    `Invoice amount: ${formatted}.`,
    "Do not collect or store card numbers, bank logins, SSNs, or customer passwords in Buddy.",
    "Confirm funds in your bank/payment app before marking the deal paid.",
  ];
  const methodSteps: Record<string, string[]> = {
    cash: ["Accept cash in person only when lawful and safe.", "Issue a receipt immediately after counting and confirming funds."],
    check: ["Send check mailing or pickup instructions outside this app.", "Mark paid only after the check clears."],
    bank_transfer: ["Send your official business bank transfer instructions directly to the customer.", "Mark paid only after the transfer is visible and settled."],
    paypal: ["Send your PayPal invoice or PayPal.me link from your own PayPal account.", "Reconcile PayPal fees before closing the deal."],
    cash_app: ["Send your business Cash App handle outside this app.", "Confirm the sender and amount before fulfillment."],
    zelle: ["Send your Zelle business email/phone outside this app.", "Confirm receipt with your bank before fulfillment."],
    manual_invoice: ["Send a PDF/email invoice with your preferred payment options.", "Keep proof of approval and proof of payment in your records."],
    other: ["Use only a lawful, approved payment method.", "Document who approved it, how it was paid, and when funds settled."],
  };
  return [...base, ...(methodSteps[method] ?? methodSteps.other)];
}

async function getOfflineDeals(): Promise<OfflineDeal[]> {
  const setting = await storage.getSetting(OFFLINE_DEALS_SETTING);
  return Array.isArray(setting?.value) ? setting.value as OfflineDeal[] : [];
}

async function saveOfflineDeals(deals: OfflineDeal[]) {
  await storage.upsertSetting(OFFLINE_DEALS_SETTING, deals.slice(0, 500));
}

function readRepoJson(relativePath: string) {
  try {
    return JSON.parse(readFileSync(resolve(process.cwd(), relativePath), "utf8"));
  } catch (error: any) {
    return { error: `Unable to read ${relativePath}`, detail: error.message };
  }
}

type CreatorBuildPacketInput = z.infer<typeof creatorBuildPacketSchema>;

function buildCreatorProjectPacket(input: CreatorBuildPacketInput) {
  const studio = readRepoJson("config/buddy_creator_studio.json");
  const modelRegistry = readRepoJson("config/buddy_user_model_choice_registry.json");
  const restoredFamilies = readRepoJson("config/buddy_restored_bot_family_bridge.json");
  const now = new Date().toISOString();
  const projectTypeLabels: Record<CreatorBuildPacketInput["projectType"], string> = {
    large_open_world_game: "Large open-world game",
    autobiography: "Autobiography and multimedia story",
    studies_to_game: "Study material to video game curriculum",
    college_3d_simulation: "College 3D simulation course",
    kids_game: "Kids learning game",
    music_video: "Music video and simulation",
    game_app: "Game or app store project",
  };
  const workflowMap: Record<CreatorBuildPacketInput["projectType"], string> = {
    large_open_world_game: "large_open_world_game_builder",
    autobiography: "autobiography_to_multimedia_project",
    studies_to_game: "studies_to_video_game_curriculum",
    college_3d_simulation: "college_3d_simulation_course",
    kids_game: "kids_voice_image_game_builder",
    music_video: "music_video_and_simulation_studio",
    game_app: "game_app_store_builder",
  };
  const workflows = Array.isArray(studio?.workflows) ? studio.workflows : [];
  const workflow = workflows.find((item: any) => item.id === workflowMap[input.projectType]) ?? workflows[0] ?? {};
  const modelChoices = Array.isArray(modelRegistry?.choices) ? modelRegistry.choices : [];
  const selectedModel = modelChoices.find((choice: any) => choice.id === input.modelPreference) ?? modelChoices.find((choice: any) => choice.id === "google_gemini") ?? modelChoices[0] ?? null;
  const restoredFamilyList = Array.isArray(restoredFamilies?.families) ? restoredFamilies.families : [];
  const suggestedBots = [
    "Buddy Bot",
    "DreamCodeLab",
    input.projectType.includes("game") ? "GameTitan" : "DreamContent",
    input.projectType.includes("studies") || input.projectType.includes("college") || input.projectType.includes("kids") ? "DreamEducation" : "DreamArts",
    "DreamLegal",
    "DreamData",
    "DreamPayments",
  ];
  const stageBase = [
    "Discovery: turn the prompt, audience, source material, and target device into a signed-off creative brief.",
    "Rights and privacy: check consent, likeness, citations, age safety, source ownership, and publishability before generation.",
    "Design: produce the world bible, story outline, curriculum map, or product spec with measurable acceptance criteria.",
    "Prototype: build the smallest playable or readable vertical slice locally first.",
    "Assets: generate or import only rights-safe text, images, audio, video, 3D, code, and data assets.",
    "Tests: run sandbox checks for syntax, performance, accessibility, content safety, save/load, API behavior, and mobile layout.",
    "Export/deploy: prepare web, PWA, store, ebook, PDF, LMS, or client handoff packages after owner approval.",
    "Review: Buddy summarizes risks, missing pieces, cost impact, and next build tasks before any public or paid action.",
  ];
  return {
    id: `creator_${Date.now()}`,
    title: input.title,
    projectType: input.projectType,
    projectTypeLabel: projectTypeLabels[input.projectType],
    audience: input.audience || "general",
    outputTarget: input.outputTarget || "web_prototype",
    generatedAt: now,
    sourceMaterialSummary: input.sourceMaterial ? input.sourceMaterial.slice(0, 500) : "No source material supplied yet.",
    workflow,
    endToEndStages: stageBase,
    suggestedBots,
    modelRoute: {
      requested: input.modelPreference,
      selected: selectedModel,
      fallback: "Use Buddy local packet generation, browser speech, local SVG/image placeholders, and free sandbox tests when paid keys are missing.",
      currentnessPolicy: modelRegistry?.currentness_policy ?? "Verify provider docs before production routing.",
    },
    restoredBotFamiliesAvailable: restoredFamilyList.map((family: any) => ({
      id: family.id,
      label: family.label,
      fileCount: family.file_count,
      jobs: family.buddy_jobs,
    })),
    firstPrototypeTasks: [
      "Create the project brief and approval checklist.",
      "Generate the folder/file manifest and data model.",
      "Build a local browser prototype with placeholder assets.",
      "Add a sandbox test plan for every API, asset pipeline, and export target.",
      "Run syntax, accessibility, responsiveness, and rights-safety checks before sharing.",
    ],
    filesToCreate: [
      "PROJECT_BRIEF.md",
      "RIGHTS_AND_CONSENT.md",
      "ASSET_MANIFEST.json",
      "SANDBOX_TEST_PLAN.md",
      "src/prototype/",
      "reports/build-readiness.md",
    ],
    guardrails: studio?.guardrails ?? [],
    approvalRequiredFor: studio?.production_packet_schema?.approval_gates ?? [],
  };
}

async function ensureSeeded() {
  const bots = await storage.listBotProfiles();
  const existingSlugs = new Set(bots.map(b => b.slug));
  const missingBots = ALL_BOTS.filter(b => !existingSlugs.has(b.slug));
  if (missingBots.length > 0) {
    for (const botData of missingBots) {
      try {
        await storage.createBotProfile(botData);
      } catch (e: any) {
        if (e?.code === "23505") continue;
        console.error(`Seed bot ${botData.slug} failed:`, e?.message);
      }
    }
    console.log(`Seeded ${missingBots.length} new bots`);
  }

  // Always upsert Buddy Bot with his full library curriculum so updates apply immediately
  try {
    const existingBuddy = bots.find(b => b.slug === "buddy-bot");
    if (existingBuddy) {
      await storage.updateBotProfile(existingBuddy.id, {
        systemPrompt: BUDDY_BOT.systemPrompt,
        capabilities: BUDDY_BOT.capabilities,
        description: BUDDY_BOT.description,
        traits: BUDDY_BOT.traits,
        tier: BUDDY_BOT.tier,
      });
      console.log("Buddy Bot updated with full library curriculum");
    } else {
      await storage.createBotProfile(BUDDY_BOT);
      console.log("Buddy Bot created with full library curriculum");
    }
  } catch (e: any) {
    console.error("Buddy Bot upsert failed:", e?.message);
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

  const existingFormulas = await storage.listFormulas();
  if (existingFormulas.length === 0) {
    for (const f of FORMULA_LIBRARY) {
      try {
        await storage.createFormula({
          name: f.name,
          category: f.category,
          description: f.description,
          formula: f.formula,
          variables: f.variables,
          target: f.target,
          tags: f.tags,
          isSystem: true,
        });
      } catch (e: any) {
        console.error(`Seed formula ${f.name} failed:`, e?.message);
      }
    }
    console.log(`Seeded ${FORMULA_LIBRARY.length} system formulas`);
  }

  // Seed default plugins
  const existingPlugins = await storage.listPlugins();
  if (existingPlugins.length === 0) {
    const defaultPlugins = [
      { name: "Deal Alert Pro", slug: "deal-alert-pro", description: "Real-time deal alerts via push notifications, email, SMS, and webhooks. Monitors price drops across all major retailers.", category: "alerts", author: "DreamCo", version: "2.1.0", rating: 5, status: "published", capabilities: ["Push notifications", "Email alerts", "SMS alerts", "Webhook integration", "Price monitoring"] },
      { name: "Coupon Stacker", slug: "coupon-stacker", description: "Automatically finds and stacks coupons, cashback offers, and loyalty rewards for maximum savings.", category: "savings", author: "DreamCo", version: "1.8.0", rating: 5, status: "published", capabilities: ["Coupon detection", "Stack optimization", "Cashback tracking", "Loyalty rewards"] },
      { name: "Flip Profit Calculator", slug: "flip-profit-calc", description: "Advanced ROI calculator for resale arbitrage. Accounts for fees, shipping, taxes, and time costs.", category: "finance", author: "DreamCo", version: "1.5.0", rating: 4, status: "published", capabilities: ["ROI calculation", "Fee estimation", "Shipping costs", "Tax tracking"] },
      { name: "Telegram Bot Connector", slug: "telegram-connector", description: "Connect your DreamCo Empire to Telegram for text-based control. Send commands, receive alerts, and manage bots from Telegram.", category: "integration", author: "DreamCo", version: "1.2.0", rating: 4, status: "published", capabilities: ["Telegram webhook", "Command interface", "Alert forwarding", "Bot control"] },
      { name: "Slack Workspace Plugin", slug: "slack-workspace", description: "Full Slack integration for team collaboration. Create channels per division, receive bot alerts, and manage workflows from Slack.", category: "integration", author: "DreamCo", version: "1.3.0", rating: 4, status: "published", capabilities: ["Slack webhooks", "Channel management", "Alert routing", "Workflow triggers"] },
      { name: "Discord Server Bot", slug: "discord-server", description: "Discord bot integration for community management and real-time bot control. Perfect for gaming and social divisions.", category: "integration", author: "DreamCo", version: "1.1.0", rating: 4, status: "published", capabilities: ["Discord webhooks", "Server management", "Real-time alerts", "Community tools"] },
      { name: "Receipt Scanner Pro", slug: "receipt-scanner", description: "OCR-powered receipt scanning for automatic cashback matching, expense tracking, and deal verification.", category: "tools", author: "DreamCo", version: "2.0.0", rating: 5, status: "published", capabilities: ["OCR scanning", "Cashback matching", "Expense categorization", "Deal verification"] },
      { name: "AI Model Router", slug: "ai-model-router", description: "Intelligent routing between 100+ AI models based on task requirements. Minimizes costs while maximizing quality.", category: "ai", author: "DreamCo", version: "1.4.0", rating: 5, status: "published", capabilities: ["Model selection", "Cost optimization", "Quality scoring", "Fallback routing"] },
      { name: "Crypto Price Tracker", slug: "crypto-tracker", description: "Real-time cryptocurrency price monitoring with alert triggers, portfolio tracking, and arbitrage detection.", category: "finance", author: "DreamCo", version: "1.6.0", rating: 4, status: "published", capabilities: ["Price monitoring", "Portfolio tracking", "Arbitrage detection", "Alert triggers"] },
      { name: "SEO Optimizer", slug: "seo-optimizer", description: "AI-powered SEO analysis and optimization for websites. Keyword research, content scoring, and competitor analysis.", category: "marketing", author: "DreamCo", version: "1.2.0", rating: 4, status: "published", capabilities: ["Keyword research", "Content scoring", "Competitor analysis", "Rank tracking"] },
      { name: "Inventory Manager", slug: "inventory-manager", description: "Track inventory across multiple locations and platforms. Sync with eBay, Amazon, and Facebook Marketplace listings.", category: "tools", author: "DreamCo", version: "1.3.0", rating: 4, status: "published", capabilities: ["Multi-platform sync", "Stock tracking", "Low stock alerts", "Listing management"] },
      { name: "Route Optimizer", slug: "route-optimizer", description: "Plan optimal clearance shopping routes. Calculates fuel costs, time estimates, and ROI per stop.", category: "tools", author: "DreamCo", version: "1.1.0", rating: 4, status: "published", capabilities: ["Route planning", "Fuel estimation", "ROI per stop", "Time optimization"] },
    ];
    for (const p of defaultPlugins) {
      try {
        await storage.createPlugin(p as any);
      } catch (e: any) {
        if (e?.code === "23505") continue;
        console.error(`Seed plugin ${p.slug} failed:`, e?.message);
      }
    }
    console.log(`Seeded ${defaultPlugins.length} default plugins`);
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

  // ===== IMAGE GENERATION =====
  app.post("/api/generate-image", async (req, res) => {
    try {
      const { prompt, size = "1024x1024" } = req.body ?? {};
      if (!prompt || !String(prompt).trim()) {
        return res.status(400).json({ error: "Prompt is required" });
      }
      const cleanPrompt = String(prompt).trim();
      if (!HAS_OPENAI_KEY) {
        return res.json(buildLocalImagePacket(cleanPrompt, size));
      }
      const response = await openai.images.generate({
        model: "gpt-image-1",
        prompt: cleanPrompt,
        n: 1,
        size: size as "1024x1024" | "512x512" | "256x256",
      });
      const imageData = (response.data ?? [])[0];
      if (!imageData || (!imageData.url && !(imageData as any).b64_json)) {
        return res.status(502).json({ error: "Image generation returned no data. The AI provider may be unavailable or the prompt was rejected." });
      }
      res.json({ url: imageData.url, b64_json: (imageData as any).b64_json, mimeType: "image/png", provider: "OpenAI", engine: "gpt-image-1" });
    } catch (e: any) {
      console.error("[image] generation error:", e.message);
      const prompt = String(req.body?.prompt ?? "").trim();
      if (prompt) {
        return res.json({
          ...buildLocalImagePacket(prompt, req.body?.size),
          fallbackReason: e.message || "AI image provider failed. Local image generation handled the request.",
        });
      }
      res.status(500).json({ error: e.message || "Failed to generate image" });
    }
  });

  // ===== DREAMCO VOICE =====
  app.post("/api/voice/clone", async (req, res) => {
    try {
      const { text, voiceId = LOCAL_VOICE_ID, provider = "dreamco-local" } = req.body ?? {};
      if (!text || !String(text).trim()) return res.status(400).json({ error: "Text is required" });

      const cleanText = String(text).trim();
      const externalRequested = provider === "external" || provider === "premium";
      if (!externalRequested || !EXTERNAL_VOICE_API_KEY || !EXTERNAL_VOICE_API_URL) {
        return res.json({
          status: "local-ready",
          capability: "voice-synthesis",
          fallbackReason: externalRequested ? "External voice endpoint is not configured." : "DreamCo local voice is the default.",
          packet: buildLocalVoicePacket(cleanText, String(voiceId)),
        });
      }

      const response = await fetch(EXTERNAL_VOICE_API_URL.replace(":voiceId", encodeURIComponent(String(voiceId))), {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${EXTERNAL_VOICE_API_KEY}`,
          "Content-Type": "application/json",
          "Accept": "audio/mpeg",
        },
        body: JSON.stringify({ text: cleanText, voiceId }),
      });
      if (!response.ok) {
        const err = await response.text();
        return res.status(response.status).json({ error: `External voice provider error: ${err}` });
      }
      const audioBuffer = Buffer.from(await response.arrayBuffer());
      res.set({ "Content-Type": "audio/mpeg", "Content-Length": audioBuffer.length });
      res.send(audioBuffer);
    } catch (e: any) {
      console.error("[voice] clone error:", e.message);
      res.status(500).json({ error: e.message || "Voice cloning failed" });
    }
  });

  // List available voices
  app.get("/api/voice/voices", async (req, res) => {
    res.json({
      defaultProvider: "dreamco-local-browser-tts",
      externalConfigured: Boolean(EXTERNAL_VOICE_API_KEY && EXTERNAL_VOICE_API_URL),
      voices: [
        { id: LOCAL_VOICE_ID, name: "Buddy Local", category: "local-browser", cost: "free" },
        { id: "dreamco-clear", name: "DreamCo Clear", category: "local-browser", cost: "free" },
        { id: "dreamco-warm", name: "DreamCo Warm", category: "local-browser", cost: "free" },
      ],
      policy: "External voice providers are optional. Real-person voice or likeness use requires explicit written consent.",
    });
  });

  // ===== WEB SEARCH =====
  app.post("/api/search/web", async (req, res) => {
    try {
      const { query, numResults = 5 } = req.body ?? {};
      if (!query || !String(query).trim()) return res.status(400).json({ error: "Query is required" });
      const q = String(query).trim();

      // Try Serper API first
      const serperKey = process.env.SERPER_API_KEY;
      if (serperKey) {
        const r = await fetch("https://google.serper.dev/search", {
          method: "POST",
          headers: { "X-API-KEY": serperKey, "Content-Type": "application/json" },
          body: JSON.stringify({ q, num: numResults }),
        });
        if (r.ok) {
          const data = await r.json() as any;
          const results = (data.organic ?? []).slice(0, numResults).map((item: any) => ({
            title: item.title, url: item.link, snippet: item.snippet,
          }));
          // Use Buddy (OpenAI) to synthesize a useful answer from results
          const synthesis = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [
              { role: "system", content: "You are Buddy Bot, DreamCo's research AI. Synthesize the search results into a clear, actionable answer. Include source links." },
              { role: "user", content: `Query: ${q}\n\nSearch results:\n${results.map((r: any, i: number) => `${i+1}. ${r.title}\n${r.url}\n${r.snippet}`).join("\n\n")}` },
            ],
            max_tokens: 800,
          });
          return res.json({ query: q, results, synthesis: synthesis.choices[0]?.message?.content ?? "", source: "serper" });
        }
      }

      // Fall back to GitHub search for tech queries + OpenAI synthesis
      const ghResponse = await fetch(`https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=stars&per_page=${numResults}`, {
        headers: { "Accept": "application/vnd.github.v3+json", ...(process.env.GITHUB_TOKEN ? { "Authorization": `token ${process.env.GITHUB_TOKEN}` } : {}) },
      });
      const ghData = await ghResponse.json() as any;
      const ghResults = (ghData.items ?? []).slice(0, numResults).map((item: any) => ({
        title: item.full_name, url: item.html_url, snippet: item.description ?? "No description",
        stars: item.stargazers_count, language: item.language,
      }));

      // Use OpenAI to synthesize a general research answer
      const synthesis = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "You are Buddy Bot, DreamCo's research AI. Answer the query with your knowledge + the GitHub repos found. Be comprehensive and include actionable steps." },
          { role: "user", content: `Research query: ${q}\n\nTop GitHub repos found:\n${ghResults.map((r: any, i: number) => `${i+1}. ${r.title} (⭐${r.stars}) — ${r.snippet}\n${r.url}`).join("\n\n")}` },
        ],
        max_tokens: 1000,
      });

      res.json({ query: q, results: ghResults, synthesis: synthesis.choices[0]?.message?.content ?? "", source: "github+openai" });
    } catch (e: any) {
      console.error("[search] web error:", e.message);
      res.status(500).json({ error: e.message || "Search failed" });
    }
  });

  // ===== GITHUB INTELLIGENCE =====
  // Every bot gets a GitHub intelligence feed — top tools/repos by topic
  app.get("/api/github-intel/trending", async (req, res) => {
    try {
      const topic = String(req.query.topic ?? "artificial-intelligence");
      const language = req.query.language as string | undefined;
      const langFilter = language ? `+language:${language}` : "";
      const ghUrl = `https://api.github.com/search/repositories?q=topic:${encodeURIComponent(topic)}${langFilter}&sort=stars&order=desc&per_page=10`;
      const r = await fetch(ghUrl, {
        headers: { "Accept": "application/vnd.github.v3+json", ...(process.env.GITHUB_TOKEN ? { "Authorization": `token ${process.env.GITHUB_TOKEN}` } : {}) },
      });
      const data = await r.json() as any;
      const repos = (data.items ?? []).map((item: any) => ({
        name: item.full_name, url: item.html_url, description: item.description,
        stars: item.stargazers_count, language: item.language, updatedAt: item.pushed_at,
        topics: item.topics ?? [],
      }));
      res.json({ topic, repos, fetchedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "GitHub intel fetch failed" });
    }
  });

  // Search GitHub for specific tools/code patterns
  app.post("/api/github-intel/search", async (req, res) => {
    try {
      const { query, type = "repositories" } = req.body ?? {};
      if (!query) return res.status(400).json({ error: "Query required" });
      const r = await fetch(`https://api.github.com/search/${type}?q=${encodeURIComponent(String(query))}&sort=stars&per_page=8`, {
        headers: { "Accept": "application/vnd.github.v3+json", ...(process.env.GITHUB_TOKEN ? { "Authorization": `token ${process.env.GITHUB_TOKEN}` } : {}) },
      });
      const data = await r.json() as any;
      res.json({ query, results: data.items ?? [], total: data.total_count ?? 0 });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "GitHub search failed" });
    }
  });

  // ===== COUNCIL SYSTEM =====
  // In-memory council store (persists in process, use DB for production)
  const councilProposals: Array<{
    id: string; botSlug: string; division: string; type: string;
    title: string; description: string; priority: "low"|"medium"|"high"|"critical";
    status: "pending"|"approved"|"rejected"; submittedAt: string;
  }> = [
    { id: "c1", botSlug: "research-bot", division: "CommandCore", type: "upgrade", title: "Add vector memory to all bots", description: "Each bot should store key learnings in a vector DB for retrieval across sessions.", priority: "high", status: "pending", submittedAt: new Date().toISOString() },
    { id: "c2", botSlug: "analytics-hub", division: "CommandCore", type: "integration", title: "Connect Serper API for live web search", description: "Add SERPER_API_KEY to enable real-time web search across all research bots.", priority: "high", status: "pending", submittedAt: new Date().toISOString() },
    { id: "c3", botSlug: "security-compliance-bot", division: "DreamCyber", type: "security", title: "Rotate all API keys every 90 days", description: "Implement automatic key rotation scheduler for all registered platform connections.", priority: "critical", status: "pending", submittedAt: new Date().toISOString() },
  ];

  app.get("/api/council/proposals", async (_req, res) => {
    res.json({ proposals: councilProposals, total: councilProposals.length });
  });

  app.post("/api/council/report", async (req, res) => {
    try {
      const { botSlug, division, type, title, description, priority = "medium" } = req.body ?? {};
      if (!botSlug || !title || !description) return res.status(400).json({ error: "botSlug, title, description required" });
      const proposal = {
        id: `c${Date.now()}`, botSlug: String(botSlug), division: String(division ?? "unknown"),
        type: String(type ?? "upgrade"), title: String(title), description: String(description),
        priority: (["low","medium","high","critical"].includes(priority) ? priority : "medium") as "low"|"medium"|"high"|"critical",
        status: "pending" as const, submittedAt: new Date().toISOString(),
      };
      councilProposals.unshift(proposal);
      console.log(`[council] New proposal from ${botSlug}: ${title}`);
      res.json({ success: true, proposal });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Council report failed" });
    }
  });

  app.patch("/api/council/proposals/:id", async (req, res) => {
    const { id } = req.params;
    const { status } = req.body ?? {};
    const idx = councilProposals.findIndex(p => p.id === id);
    if (idx === -1) return res.status(404).json({ error: "Proposal not found" });
    if (!["pending","approved","rejected"].includes(status)) return res.status(400).json({ error: "Invalid status" });
    councilProposals[idx].status = status;
    res.json({ success: true, proposal: councilProposals[idx] });
  });

  // ===== BUDDY SELF-TRAINING / BOOTCAMP =====
  app.post("/api/buddy/train", async (req, res) => {
    try {
      const { topic, difficulty = "intermediate", format = "exercise" } = req.body ?? {};
      if (!topic) return res.status(400).json({ error: "Topic required" });
      const prompt = format === "exercise"
        ? `Create a coding bootcamp exercise for: "${topic}". Difficulty: ${difficulty}. Include: 1) Learning objective, 2) Problem statement, 3) Starter code, 4) Expected solution, 5) Test cases, 6) How this earns revenue or solves a real problem.`
        : `Create a self-training curriculum for Buddy Bot to master: "${topic}". Include: phases, resources, practice projects, and how to verify mastery.`;
      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "You are Buddy Bot, DreamCo's master coder and trainer. Generate high-quality bootcamp content." },
          { role: "user", content: prompt },
        ],
        max_tokens: 1500,
      });
      res.json({ topic, difficulty, format, content: result.choices[0]?.message?.content ?? "", generatedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Training generation failed" });
    }
  });

  // ===== BOOK STUDY =====
  app.post("/api/buddy/study-book", async (req, res) => {
    try {
      const { title, author, extractType = "key-insights" } = req.body ?? {};
      if (!title) return res.status(400).json({ error: "Book title required" });
      const prompt = extractType === "key-insights"
        ? `Provide a comprehensive study guide for "${title}" by ${author ?? "unknown author"}. Include: 1) Core thesis, 2) 10 key insights, 3) Actionable takeaways for entrepreneurs/AI builders, 4) How to apply the lessons to build revenue-generating systems, 5) Related books to read next.`
        : `Summarize "${title}" by ${author ?? "unknown"} as a structured course outline with modules, lessons, and exercises for each chapter.`;
      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "You are Buddy Bot, an expert at extracting actionable insights from nonfiction books and turning them into executable business strategies." },
          { role: "user", content: prompt },
        ],
        max_tokens: 2000,
      });
      res.json({ title, author, extractType, content: result.choices[0]?.message?.content ?? "", studiedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Book study failed" });
    }
  });

  // ===== VIBE CODE — Full project generation =====
  app.post("/api/buddy/vibe-code", async (req, res) => {
    try {
      const { description, stack = "React + TypeScript + Tailwind", includeFiles = true } = req.body ?? {};
      if (!description) return res.status(400).json({ error: "Project description required" });
      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: `You are Buddy Bot, the world's best vibe coder. When given a project description, generate a complete, production-ready project in ${stack}. Include ALL files with full code. Format output as JSON: { "projectName": string, "description": string, "stack": string, "files": [{"path": string, "content": string, "type": "tsx"|"ts"|"css"|"json"|"md"}], "commands": string[], "features": string[] }` },
          { role: "user", content: `Vibe code this project from scratch: ${description}\n\nStack: ${stack}\n\nInclude every file needed to run this immediately.` },
        ],
        max_tokens: 3000,
        response_format: { type: "json_object" },
      });
      const raw = result.choices[0]?.message?.content ?? "{}";
      let project: any;
      try { project = JSON.parse(raw); } catch { project = { projectName: "Generated Project", files: [], rawOutput: raw }; }
      res.json({ ...project, generatedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Vibe code generation failed" });
    }
  });

  // ===== GAME BUILDER =====
  app.post("/api/buddy/build-game", async (req, res) => {
    try {
      const { gameType, description } = req.body ?? {};
      if (!description) return res.status(400).json({ error: "Game description required" });
      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: `You are Buddy Bot, expert game developer. Build complete browser games using HTML5 Canvas + JavaScript or Phaser 3. Output as JSON: { "gameName": string, "gameType": string, "files": [{"path": string, "content": string}], "instructions": string, "controls": string }` },
          { role: "user", content: `Build a complete ${gameType ?? "browser"} game: ${description}. Make it fully playable in a browser. Include HTML, CSS, and JavaScript.` },
        ],
        max_tokens: 3000,
        response_format: { type: "json_object" },
      });
      const raw = result.choices[0]?.message?.content ?? "{}";
      let game: any;
      try { game = JSON.parse(raw); } catch { game = { gameName: "Generated Game", files: [], rawOutput: raw }; }
      res.json({ ...game, generatedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Game build failed" });
    }
  });

  // ===== COLLEGE COURSE SIMULATOR =====
  app.post("/api/buddy/simulate-course", async (req, res) => {
    try {
      const { subject, level = "undergraduate", weeks = 12 } = req.body ?? {};
      if (!subject) return res.status(400).json({ error: "Subject required" });
      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: `You are Buddy Bot, curriculum designer. Create complete college course simulations. Output JSON: { "courseTitle": string, "subject": string, "level": string, "creditHours": number, "syllabus": string, "weeks": [{"week": number, "topic": string, "lecture": string, "assignment": string, "quiz": string}], "finalProject": string, "gradingRubric": string }` },
          { role: "user", content: `Simulate a complete ${level} college course on "${subject}" for ${weeks} weeks. Include full syllabus, weekly lectures, assignments, quizzes, and final project.` },
        ],
        max_tokens: 3000,
        response_format: { type: "json_object" },
      });
      const raw = result.choices[0]?.message?.content ?? "{}";
      let course: any;
      try { course = JSON.parse(raw); } catch { course = { courseTitle: subject, weeks: [], rawOutput: raw }; }
      res.json({ ...course, generatedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Course simulation failed" });
    }
  });

  // ===== COMPETITIVE INTELLIGENCE =====
  app.post("/api/intel/competitive", async (req, res) => {
    try {
      const { competitor, category = "ai-tools" } = req.body ?? {};
      if (!competitor) return res.status(400).json({ error: "Competitor name required" });
      const [ghData, analysisData] = await Promise.all([
        fetch(`https://api.github.com/search/repositories?q=${encodeURIComponent(competitor)}&sort=stars&per_page=5`, {
          headers: { "Accept": "application/vnd.github.v3+json", ...(process.env.GITHUB_TOKEN ? { "Authorization": `token ${process.env.GITHUB_TOKEN}` } : {}) },
        }).then(r => r.json() as Promise<any>),
        openai.chat.completions.create({
          model: "gpt-4o-mini",
          messages: [
            { role: "system", content: "You are DreamCo's competitive intelligence analyst. Analyze competitors and identify weaknesses DreamCo can exploit." },
            { role: "user", content: `Analyze competitor: "${competitor}" in the ${category} space. Identify: 1) Their strengths, 2) Their weaknesses/gaps, 3) How DreamCo can outcompete them, 4) Features to copy/improve, 5) Price positioning opportunities.` },
          ],
          max_tokens: 1000,
        }),
      ]);
      res.json({
        competitor, category,
        githubPresence: { repos: (ghData.items ?? []).slice(0, 5).map((r: any) => ({ name: r.full_name, stars: r.stargazers_count, url: r.html_url })) },
        analysis: analysisData.choices[0]?.message?.content ?? "",
        analyzedAt: new Date().toISOString(),
      });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Intel failed" });
    }
  });

  // ===== DATA PACKAGES (for selling training data) =====
  app.get("/api/data-packages", async (_req, res) => {
    res.json({
      packages: [
        { id: "dp-conversations", name: "Empire OS Conversation Dataset", size: "~50K conversations", price: "$299/mo", description: "High-quality AI conversations across 45 business domains for fine-tuning", tier: "pro" },
        { id: "dp-bot-prompts", name: "1,051 Bot System Prompts", size: "~2MB", price: "$499 one-time", description: "Complete system prompt library covering every industry vertical", tier: "enterprise" },
        { id: "dp-revenue-flows", name: "Revenue Automation Flows", size: "~500 workflows", price: "$199/mo", description: "n8n/workflow templates for autonomous revenue generation", tier: "pro" },
        { id: "dp-code-snippets", name: "DreamCode Snippet Library", size: "~10K snippets", price: "$149/mo", description: "Production-ready code snippets across 50+ languages and frameworks", tier: "pro" },
        { id: "dp-formulas", name: "High-Profit Formula Library", size: "~300 formulas", price: "$999 one-time", description: "Business formulas, deal calculators, and financial models", tier: "elite" },
      ],
    });
  });

  // ===== HARNESS TESTER =====
  // In-memory suite store (use DB for persistence in production)
  const harnessSuites: Array<{
    id: string; name: string; botSlug: string;
    cases: Array<{ id: string; name: string; prompt: string; expectedKeywords: string; mustNotContain: string }>;
    createdAt: string;
  }> = [];

  app.get("/api/harness/suites", (_req, res) => {
    res.json({ suites: harnessSuites });
  });

  app.post("/api/harness/suites", (req, res) => {
    const { name, botSlug, cases } = req.body ?? {};
    if (!name || !botSlug || !Array.isArray(cases) || cases.length === 0)
      return res.status(400).json({ error: "name, botSlug, and at least one case required" });
    const suite = { id: `hs-${Date.now()}`, name: String(name), botSlug: String(botSlug), cases, createdAt: new Date().toISOString() };
    harnessSuites.unshift(suite);
    res.json({ success: true, suite });
  });

  app.delete("/api/harness/suites/:id", (req, res) => {
    const idx = harnessSuites.findIndex(s => s.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "Suite not found" });
    harnessSuites.splice(idx, 1);
    res.json({ success: true });
  });

  app.post("/api/harness/run-suite", async (req, res) => {
    const { suiteId } = req.body ?? {};
    const suite = harnessSuites.find(s => s.id === suiteId);
    if (!suite) return res.status(404).json({ error: "Suite not found" });

    const results: Array<{
      caseId: string; caseName: string; prompt: string; response: string;
      passed: boolean; failReasons: string[]; latencyMs: number; runAt: string;
    }> = [];

    for (const tc of suite.cases) {
      const start = Date.now();
      let response = "";
      let passed = true;
      const failReasons: string[] = [];
      try {
        const botProfile = await storage.getBotProfileBySlug(suite.botSlug);
        const systemPrompt = botProfile?.systemPrompt ?? `You are ${suite.botSlug}, a DreamCo AI bot.`;
        const completion = await openai.chat.completions.create({
          model: "gpt-4o-mini",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: tc.prompt },
          ],
          max_tokens: 500,
        });
        response = completion.choices[0]?.message?.content ?? "";
      } catch (e: any) {
        response = `ERROR: ${e.message}`;
        passed = false;
        failReasons.push(`Bot failed to respond: ${e.message}`);
      }

      const lower = response.toLowerCase();

      if (tc.expectedKeywords) {
        for (const kw of tc.expectedKeywords.split(",").map(k => k.trim()).filter(Boolean)) {
          if (!lower.includes(kw.toLowerCase())) {
            passed = false;
            failReasons.push(`Missing expected keyword: "${kw}"`);
          }
        }
      }
      if (tc.mustNotContain) {
        for (const kw of tc.mustNotContain.split(",").map(k => k.trim()).filter(Boolean)) {
          if (lower.includes(kw.toLowerCase())) {
            passed = false;
            failReasons.push(`Response contains blocked keyword: "${kw}"`);
          }
        }
      }

      results.push({
        caseId: tc.id, caseName: tc.name || `Case ${results.length + 1}`,
        prompt: tc.prompt, response, passed, failReasons,
        latencyMs: Date.now() - start, runAt: new Date().toISOString(),
      });
    }

    const passed = results.filter(r => r.passed).length;
    const avgLatencyMs = Math.round(results.reduce((a, r) => a + r.latencyMs, 0) / results.length);
    res.json({
      suiteId: suite.id, suiteName: suite.name, botSlug: suite.botSlug,
      passed, failed: results.length - passed, total: results.length,
      avgLatencyMs, results, ranAt: new Date().toISOString(),
    });
  });

  // ===== GOVERNANCE RULES =====
  const governanceRules: Array<{
    id: string; name: string; description: string; trigger: string;
    condition: string; action: string;
    severity: "info"|"warning"|"critical"; scope: string; scopeTarget: string;
    enabled: boolean; createdAt: string;
  }> = [
    { id: "gr1", name: "Block Financial Guarantees", description: "Prevent bots from promising guaranteed returns", trigger: "Bot generates financial advice response", condition: "Response contains 'guaranteed return' OR 'risk-free' OR 'certain profit'", action: "Block response and flag for review. Replace with: 'All investments carry risk.'", severity: "critical", scope: "all-bots", scopeTarget: "", enabled: true, createdAt: new Date().toISOString() },
    { id: "gr2", name: "PII Leak Prevention", description: "Block responses that expose user personal data", trigger: "Any bot response", condition: "Response contains email addresses, SSNs, or phone numbers from other users", action: "Redact PII, log security event, alert council", severity: "critical", scope: "all-bots", scopeTarget: "", enabled: true, createdAt: new Date().toISOString() },
    { id: "gr3", name: "Autonomous Action Throttle", description: "Rate limit bots in full autonomy mode", trigger: "Bot initiates external API call", condition: "More than 100 external calls in 60 minutes from one bot", action: "Pause bot, submit council proposal for review, notify admin", severity: "warning", scope: "all-bots", scopeTarget: "", enabled: true, createdAt: new Date().toISOString() },
  ];

  app.get("/api/governance/rules", (_req, res) => {
    res.json({ rules: governanceRules });
  });

  app.post("/api/governance/rules", (req, res) => {
    const { name, description, trigger, condition, action, severity = "warning", scope = "all-bots", scopeTarget = "" } = req.body ?? {};
    if (!name || !trigger || !condition || !action)
      return res.status(400).json({ error: "name, trigger, condition, and action are required" });
    const rule = {
      id: `gr-${Date.now()}`, name: String(name), description: String(description ?? ""),
      trigger: String(trigger), condition: String(condition), action: String(action),
      severity: (["info","warning","critical"].includes(severity) ? severity : "warning") as "info"|"warning"|"critical",
      scope: String(scope), scopeTarget: String(scopeTarget),
      enabled: true, createdAt: new Date().toISOString(),
    };
    governanceRules.unshift(rule);
    res.json({ success: true, rule });
  });

  app.patch("/api/governance/rules/:id", (req, res) => {
    const idx = governanceRules.findIndex(r => r.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "Rule not found" });
    const { enabled } = req.body ?? {};
    if (typeof enabled === "boolean") governanceRules[idx].enabled = enabled;
    res.json({ success: true, rule: governanceRules[idx] });
  });

  app.delete("/api/governance/rules/:id", (req, res) => {
    const idx = governanceRules.findIndex(r => r.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "Rule not found" });
    governanceRules.splice(idx, 1);
    res.json({ success: true });
  });

  app.post("/api/governance/test", async (req, res) => {
    try {
      const { scenario, ruleId } = req.body ?? {};
      if (!scenario) return res.status(400).json({ error: "scenario required" });

      const rulesToTest = ruleId
        ? governanceRules.filter(r => r.id === ruleId && r.enabled)
        : governanceRules.filter(r => r.enabled);

      if (rulesToTest.length === 0)
        return res.json({ triggered: false, ruleName: "—", reasoning: "No active rules to test against.", suggestedAction: "", severity: "info", testedAt: new Date().toISOString() });

      const rulesContext = rulesToTest.map(r =>
        `Rule: "${r.name}" [${r.severity.toUpperCase()}]\nTrigger: ${r.trigger}\nCondition: ${r.condition}\nAction: ${r.action}`
      ).join("\n\n");

      const result = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: `You are DreamCo's governance AI. Analyze a scenario against governance rules and determine if any rule is triggered. Respond ONLY as JSON: { "triggered": boolean, "ruleName": string, "reasoning": string, "suggestedAction": string, "severity": "info"|"warning"|"critical" }` },
          { role: "user", content: `Scenario: ${scenario}\n\nGovernance Rules:\n${rulesContext}\n\nDoes this scenario violate any rule? Return JSON only.` },
        ],
        max_tokens: 600,
        response_format: { type: "json_object" },
      });

      const raw = result.choices[0]?.message?.content ?? "{}";
      let parsed: any;
      try { parsed = JSON.parse(raw); } catch { parsed = { triggered: false, reasoning: raw }; }

      res.json({ ...parsed, testedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message || "Governance test failed" });
    }
  });

  // ===== REVOLUTIONARY: CODE EXECUTION ENGINE =====
  app.post("/api/buddy/execute-code", async (req, res) => {
    const { code, language = "javascript" } = req.body ?? {};
    if (!code) return res.status(400).json({ error: "code required" });
    const start = Date.now();

    const lang = String(language).toLowerCase();
    if (lang === "javascript" || lang === "js" || lang === "typescript" || lang === "ts") {
      const vm = await import("vm");
      const logs: string[] = [];
      const errs: string[] = [];
      const sandbox = {
        console: {
          log: (...a: unknown[]) => logs.push(a.map(x => (typeof x === "object" ? JSON.stringify(x, null, 2) : String(x))).join(" ")),
          error: (...a: unknown[]) => errs.push(a.map(x => String(x)).join(" ")),
          warn: (...a: unknown[]) => logs.push("[WARN] " + a.map(x => String(x)).join(" ")),
          info: (...a: unknown[]) => logs.push("[INFO] " + a.map(x => String(x)).join(" ")),
          table: (d: unknown) => logs.push(JSON.stringify(d, null, 2)),
        },
        Math, JSON, parseInt, parseFloat, isNaN, isFinite,
        Array, Object, String, Number, Boolean, Date, RegExp, Error, Map, Set, WeakMap, WeakSet,
        Promise, Symbol, BigInt, Proxy, Reflect,
        setTimeout: (_fn: unknown, _ms: unknown) => undefined,
        clearTimeout: () => undefined,
        process: { env: {}, argv: [], version: "v20" },
        Buffer: { from: (s: string) => ({ toString: () => s }) },
      };
      try {
        const script = new vm.Script(code);
        const result = script.runInNewContext(sandbox, { timeout: 5000 } as any);
        if (result !== undefined && result !== null) logs.push(String(result));
        res.json({ output: logs.join("\n") || "(no output)", error: errs.length ? errs.join("\n") : null, executionTimeMs: Date.now() - start, language: lang });
      } catch (e: any) {
        res.json({ output: logs.join("\n"), error: e.message, executionTimeMs: Date.now() - start, language: lang });
      }
    } else {
      // For non-JS languages, use GPT to simulate execution
      try {
        const result = await openai.chat.completions.create({
          model: "gpt-4o-mini",
          messages: [
            { role: "system", content: `You are a precise code execution simulator for ${language}. Execute the code mentally and return ONLY a JSON object: { "output": "<exact stdout>", "error": null_or_string, "notes": "<any runtime notes>" }. No markdown.` },
            { role: "user", content: `Execute this ${language} code:\n\`\`\`${language}\n${code}\n\`\`\`` },
          ],
          max_tokens: 800,
          response_format: { type: "json_object" },
        });
        const parsed = JSON.parse(result.choices[0]?.message?.content ?? "{}") as Record<string, unknown>;
        res.json({ ...parsed, executionTimeMs: Date.now() - start, language, simulated: true });
      } catch (e: any) {
        res.status(500).json({ error: e.message });
      }
    }
  });

  // ===== REVOLUTIONARY: IMAGE / VISION ANALYSIS =====
  app.post("/api/buddy/analyze-image", async (req, res) => {
    const { imageUrl, base64Image, mimeType = "image/jpeg", prompt = "Analyze this image in complete detail." } = req.body ?? {};
    if (!imageUrl && !base64Image) return res.status(400).json({ error: "imageUrl or base64Image required" });
    try {
      if (!HAS_OPENAI_KEY) {
        const imageType = base64Image ? "base64 upload" : "image URL";
        const byteEstimate = typeof base64Image === "string" ? Math.round((base64Image.length * 3) / 4) : null;
        return res.json({
          analysis: [
            "Local image intake is working.",
            `Input type: ${imageType}.`,
            `MIME type: ${String(mimeType)}.`,
            byteEstimate ? `Estimated image bytes: ${byteEstimate}.` : `Image URL: ${String(imageUrl).slice(0, 180)}.`,
            `Requested task: ${String(prompt).slice(0, 500)}`,
            "Set AI_INTEGRATIONS_OPENAI_API_KEY to enable full visual reasoning, screenshot-to-code, OCR-style extraction, and diagram analysis.",
          ].join("\n"),
          provider: "DreamCo",
          engine: "dreamco-local-image-intake",
          analyzedAt: new Date().toISOString(),
          fallbackReason: "AI vision provider is not configured. Local intake still validates the image pipeline.",
        });
      }
      const imageSource = base64Image
        ? { type: "image_url" as const, image_url: { url: `data:${mimeType};base64,${base64Image}` } }
        : { type: "image_url" as const, image_url: { url: imageUrl as string } };

      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL, // gpt-4o-mini supports vision — 33× cheaper than gpt-4o
        messages: [
          { role: "system", content: "You are Buddy Bot's vision engine. For UI screenshots: generate pixel-accurate React+Tailwind code. For ERDs/diagrams: generate Drizzle schema or TypeScript types. For code screenshots: extract code, find bugs, rewrite with fixes. For whiteboards: produce full system design docs. Be concise and production-ready." },
          { role: "user", content: [{ type: "text", text: prompt as string }, imageSource] },
        ],
        max_tokens: 1500,
      });
      res.json({ analysis: result.choices[0]?.message?.content ?? "", provider: "OpenAI", engine: CHEAP_MODEL, analyzedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: AUTONOMOUS AGENT PIPELINE =====
  app.post("/api/buddy/agent-run", async (req, res) => {
    const { goal, context = "", maxSteps = 5 } = req.body ?? {};
    if (!goal) return res.status(400).json({ error: "goal required" });
    try {
      // Phase 1: Plan
      const planRes = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: 'You are Buddy Bot\'s planning engine. Break the goal into concrete, executable steps. Return ONLY valid JSON: { "plan": "one-line summary", "steps": [{ "id": 1, "title": "string", "description": "string", "expectedOutput": "string" }] }' },
          { role: "user", content: `Goal: ${goal}\nContext: ${context}\nMax steps: ${maxSteps}` },
        ],
        max_tokens: 1200,
        response_format: { type: "json_object" },
      });
      let planData: { plan?: string; steps?: Array<{ id: number; title: string; description: string; expectedOutput: string }> } = {};
      try { planData = JSON.parse(planRes.choices[0]?.message?.content ?? "{}"); } catch { planData = { steps: [] }; }

      // Phase 2: Execute each step
      const executedSteps: Array<{ id: number; title: string; result: string; status: string }> = [];
      for (const step of (planData.steps ?? []).slice(0, Number(maxSteps))) {
        const stepRes = await openai.chat.completions.create({
          model: "gpt-4o-mini",
          messages: [
            { role: "system", content: "You are Buddy Bot executing one step of an autonomous plan. Execute completely. Show all code, calculations, or content needed. Be thorough and production-ready." },
            { role: "user", content: `Goal: ${goal}\nStep ${step.id}: ${step.title}\n${step.description}\nExpected: ${step.expectedOutput}` },
          ],
          max_tokens: 1500,
        });
        executedSteps.push({ id: step.id, title: step.title, result: stepRes.choices[0]?.message?.content ?? "", status: "completed" });
      }

      // Phase 3: Synthesize final deliverable
      const synthRes = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: "You are Buddy Bot delivering the final result of an autonomous multi-step execution. Synthesize all steps into one complete, polished deliverable. Include all code, skip nothing. End with a SKILL CREATED entry." },
          { role: "user", content: `Goal: ${goal}\n\nCompleted steps:\n${executedSteps.map(s => `## Step ${s.id}: ${s.title}\n${s.result}`).join("\n\n")}` },
        ],
        max_tokens: 3000,
      });

      res.json({ goal, plan: planData.plan, steps: executedSteps, finalDeliverable: synthRes.choices[0]?.message?.content ?? "", completedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: SECURITY SCANNER (SAST-LEVEL) =====
  app.post("/api/buddy/security-scan", async (req, res) => {
    const { code, language = "javascript", scanType = "full" } = req.body ?? {};
    if (!code) return res.status(400).json({ error: "code required" });
    const ck = cacheKey("security-scan", code, language, scanType);
    const cached = fromCache<Record<string, unknown>>(ck);
    if (cached) return res.json({ ...cached, fromCache: true });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: `You are a SAST security engine. Scan for OWASP Top 10, CWE Top 25, hardcoded secrets, SQL injection, XSS, CSRF, auth bypass, broken access control, and crypto failures. Return ONLY valid JSON: { "riskLevel": "low|medium|high|critical", "score": 0-100, "vulnerabilities": [{ "id": "V001", "severity": "info|low|medium|high|critical", "title": "string", "description": "string", "lineHint": "string", "cwe": "CWE-89", "owasp": "A03:2021", "attack": "string", "fix": "string", "fixedCode": "string" }], "summary": "string", "passedChecks": ["string"] }` },
          { role: "user", content: `${scanType} scan — ${language}:\n\`\`\`${language}\n${code}\n\`\`\`` },
        ],
        max_tokens: 2000,
        response_format: { type: "json_object" },
      });
      const scan = JSON.parse(result.choices[0]?.message?.content ?? "{}") as Record<string, unknown>;
      toCache(ck, scan);
      res.json({ ...scan, scannedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: SYSTEM ARCHITECT =====
  app.post("/api/buddy/architect", async (req, res) => {
    const { requirements, style = "microservices", scale = "startup" } = req.body ?? {};
    if (!requirements) return res.status(400).json({ error: "requirements required" });
    const ck = cacheKey("architect", requirements, style, scale);
    const cached = fromCache<Record<string, unknown>>(ck);
    if (cached) return res.json({ ...cached, fromCache: true });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: 'Architecture design engine (C4 model). Return ONLY valid JSON: { "systemName": "string", "overview": "string", "components": [{ "name": "string", "role": "string", "technology": ["array"], "exposes": ["string"] }], "dataFlow": ["string"], "databases": [{ "name": "string", "type": "string", "purpose": "string" }], "infrastructure": ["string"], "securityLayers": ["string"], "estimatedMonthlyCost": "string", "scalingPlan": { "1k": "string", "10k": "string", "1m": "string" }, "diagramAscii": "string", "mermaidDiagram": "string", "techStack": ["string"], "keyDecisions": [{ "decision": "string", "rationale": "string", "alternatives": "string" }], "dockerCompose": "string", "nextSteps": ["string"] }' },
          { role: "user", content: `${style} architecture, ${scale} scale:\n${requirements}` },
        ],
        max_tokens: 2500,
        response_format: { type: "json_object" },
      });
      const arch = JSON.parse(result.choices[0]?.message?.content ?? "{}") as Record<string, unknown>;
      toCache(ck, arch);
      res.json({ ...arch, designedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: CODE TRANSLATOR =====
  app.post("/api/buddy/translate-code", async (req, res) => {
    const { code, fromLanguage, toLanguage, preserveComments = true } = req.body ?? {};
    if (!code || !fromLanguage || !toLanguage) return res.status(400).json({ error: "code, fromLanguage, toLanguage required" });
    const ck = cacheKey("translate", code, fromLanguage, toLanguage);
    const cached = fromCache<string>(ck);
    if (cached) return res.json({ translatedCode: cached, fromLanguage, toLanguage, fromCache: true, translatedAt: new Date().toISOString() });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: `Translate code from ${fromLanguage} to ${toLanguage} with 100% functional equivalence. Use idiomatic patterns. Include types if supported. ${preserveComments ? "Preserve" : "Omit"} comments. Output: the translated code block, then ## Notes with any idiom/library differences.` },
          { role: "user", content: `\`\`\`${fromLanguage}\n${code}\n\`\`\`` },
        ],
        max_tokens: 2000,
      });
      const translatedCode = result.choices[0]?.message?.content ?? "";
      toCache(ck, translatedCode);
      res.json({ translatedCode, fromLanguage, toLanguage, translatedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: DEEP CODE REVIEW =====
  app.post("/api/buddy/code-review", async (req, res) => {
    const { code, language = "javascript", focusAreas = ["security", "performance", "readability", "testing"] } = req.body ?? {};
    if (!code) return res.status(400).json({ error: "code required" });
    const ck = cacheKey("code-review", code, language, focusAreas);
    const cached = fromCache<Record<string, unknown>>(ck);
    if (cached) return res.json({ ...cached, fromCache: true });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: 'Senior engineer code review. Return ONLY valid JSON: { "overallScore": 0-100, "grade": "A+|A|B|C|D|F", "summary": "string", "strengths": ["string"], "issues": [{ "severity": "critical|major|minor|nitpick", "category": "security|performance|readability|testing|architecture|types|error-handling", "title": "string", "description": "string", "lineHint": "string", "improvement": "string", "improvedCode": "string" }], "refactoredVersion": "string", "testSuiteTemplate": "string", "performanceNotes": "string", "securityNotes": "string" }' },
          { role: "user", content: `Review this ${language} code. Focus: ${(focusAreas as string[]).join(", ")}.\n\`\`\`${language}\n${code}\n\`\`\`` },
        ],
        max_tokens: 2500,
        response_format: { type: "json_object" },
      });
      const review = JSON.parse(result.choices[0]?.message?.content ?? "{}") as Record<string, unknown>;
      toCache(ck, review);
      res.json({ ...review, reviewedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: PR GENERATOR =====
  app.post("/api/buddy/generate-pr", async (req, res) => {
    const { diff, repoContext = "", ticketId = "" } = req.body ?? {};
    if (!diff) return res.status(400).json({ error: "diff required" });
    const ck = cacheKey("generate-pr", diff, repoContext, ticketId);
    const cached = fromCache<Record<string, unknown>>(ck);
    if (cached) return res.json({ ...cached, fromCache: true });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: 'PR generator. Return ONLY valid JSON: { "title": "feat: title", "body": "markdown PR body", "commitMessages": ["string"], "labels": ["string"], "reviewers": ["string"], "changelog": "string", "breakingChanges": null, "migrationSteps": null }' },
          { role: "user", content: `Repo: ${repoContext} | Ticket: ${ticketId}\nDiff:\n${diff.slice(0, 3000)}` },
        ],
        max_tokens: 1200,
        response_format: { type: "json_object" },
      });
      const pr = JSON.parse(result.choices[0]?.message?.content ?? "{}") as Record<string, unknown>;
      toCache(ck, pr);
      res.json({ ...pr, generatedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: DEPLOY CONFIG GENERATOR =====
  app.post("/api/buddy/deploy-config", async (req, res) => {
    const { projectDescription, techStack = [], platform = "all", port = 3000 } = req.body ?? {};
    if (!projectDescription) return res.status(400).json({ error: "projectDescription required" });
    const ck = cacheKey("deploy-config", projectDescription, techStack, platform, port);
    const cached = fromCache<Record<string, unknown>>(ck);
    if (cached) return res.json({ ...cached, fromCache: true });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: 'Deployment config generator. Return ONLY valid JSON: { "dockerfile": "string", "dockerCompose": "string", "dockerComposeProduction": "string", "vercelJson": "string", "railwayToml": "string", "flyToml": "string", "githubActionsCI": "string", "envTemplate": "string", "nginxConfig": "string", "kubernetesManifest": "string", "readmeSection": "string" }' },
          { role: "user", content: `Project: ${projectDescription}\nStack: ${(techStack as string[]).join(", ") || "Node.js/Express"}\nTarget: ${platform}\nPort: ${port}` },
        ],
        max_tokens: 2500,
        response_format: { type: "json_object" },
      });
      const config = JSON.parse(result.choices[0]?.message?.content ?? "{}") as Record<string, unknown>;
      toCache(ck, config);
      res.json({ ...config, generatedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== REVOLUTIONARY: DEEP DEBUG ENGINE =====
  app.post("/api/buddy/debug-deep", async (req, res) => {
    const { errorMessage, stackTrace = "", code = "", context = "" } = req.body ?? {};
    if (!errorMessage) return res.status(400).json({ error: "errorMessage required" });
    const ck = cacheKey("debug-deep", errorMessage, stackTrace, code);
    const cached = fromCache<Record<string, unknown>>(ck);
    if (cached) return res.json({ ...cached, fromCache: true });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: 'Root-cause debugger. Return ONLY valid JSON: { "rootCause": "string", "explanation": "string", "errorCategory": "type-error|runtime|async|memory|network|auth|data|config|dependency", "affectedCode": "string", "fixedCode": "string", "stepByStepFix": ["string"], "preventionStrategy": "string", "relatedBugs": ["string"], "testToVerifyFix": "string", "confidence": 0-100 }' },
          { role: "user", content: `Error: ${errorMessage}\nStack: ${stackTrace}\nCode:\n${code}\nContext: ${context}` },
        ],
        max_tokens: 1800,
        response_format: { type: "json_object" },
      });
      const debug = JSON.parse(result.choices[0]?.message?.content ?? "{}") as Record<string, unknown>;
      toCache(ck, debug);
      res.json({ ...debug, debuggedAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== BUDDY CREATOR STUDIO, RESTORED BOT FAMILIES, AND MODEL CHOICE =====
  app.get("/api/buddy/creator-studio", async (_req, res) => {
    res.json(readRepoJson("config/buddy_creator_studio.json"));
  });

  app.get("/api/buddy/model-choices", async (_req, res) => {
    res.json(readRepoJson("config/buddy_user_model_choice_registry.json"));
  });

  app.get("/api/buddy/restored-bot-families", async (_req, res) => {
    res.json(readRepoJson("config/buddy_restored_bot_family_bridge.json"));
  });

  app.get("/api/buddy/bot-end-to-end-readiness", async (_req, res) => {
    res.json(readRepoJson("config/generated/bot_end_to_end_readiness/index.json"));
  });

  app.get("/api/buddy/bot-end-to-end-readiness/divisions/:division", async (req, res) => {
    const division = String(req.params.division || "").replace(/[^a-zA-Z0-9-]/g, "").toLowerCase();
    res.json(readRepoJson(`config/generated/bot_end_to_end_readiness/divisions/${division}.json`));
  });

  app.post("/api/buddy/creator-studio/build-packet", async (req, res) => {
    const parsed = creatorBuildPacketSchema.safeParse(req.body ?? {});
    if (!parsed.success) return res.status(400).json(zodValidationError(parsed.error));
    res.json(buildCreatorProjectPacket(parsed.data));
  });

  // ===== REVOLUTIONARY: MEMORY SYSTEM =====
  const buddyMemory: Array<{ id: string; category: string; key: string; value: string; savedAt: string }> = [];

  app.post("/api/buddy/memory/save", async (req, res) => {
    const { key, value, category = "general" } = req.body ?? {};
    if (!key || !value) return res.status(400).json({ error: "key and value required" });
    const existing = buddyMemory.findIndex(m => m.key === key);
    const entry = { id: existing >= 0 ? buddyMemory[existing].id : `mem_${Date.now()}`, category: String(category), key: String(key), value: String(value), savedAt: new Date().toISOString() };
    if (existing >= 0) buddyMemory[existing] = entry;
    else buddyMemory.push(entry);
    res.json({ saved: true, entry });
  });

  app.get("/api/buddy/memory", (_req, res) => {
    res.json({ memories: buddyMemory, total: buddyMemory.length });
  });

  app.delete("/api/buddy/memory/:id", (req, res) => {
    const idx = buddyMemory.findIndex(m => m.id === req.params.id);
    if (idx < 0) return res.status(404).json({ error: "Memory not found" });
    buddyMemory.splice(idx, 1);
    res.json({ deleted: true });
  });

  // ===== REVOLUTIONARY: CODE REFACTOR ENGINE =====
  app.post("/api/buddy/refactor", async (req, res) => {
    const { code, language = "javascript", goals = ["readability", "performance", "types", "error-handling"] } = req.body ?? {};
    if (!code) return res.status(400).json({ error: "code required" });
    const ck = cacheKey("refactor", code, language, goals);
    const cached = fromCache<string>(ck);
    if (cached) return res.json({ refactoredCode: cached, language, fromCache: true, refactoredAt: new Date().toISOString() });
    try {
      const result = await openai.chat.completions.create({
        model: CHEAP_MODEL,
        messages: [
          { role: "system", content: "Refactoring engine. Improve code without changing its external API. Apply: SOLID, DRY, proper error handling, TypeScript types, performance optimizations, modern idioms. Explain every change." },
          { role: "user", content: `Refactor this ${language} code. Goals: ${(goals as string[]).join(", ")}.\n\`\`\`${language}\n${code}\n\`\`\`\nOutput: refactored code block, then ## Changes Made.` },
        ],
        max_tokens: 2000,
      });
      const refactoredCode = result.choices[0]?.message?.content ?? "";
      toCache(ck, refactoredCode);
      res.json({ refactoredCode, language, refactoredAt: new Date().toISOString() });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== BUDDY FEATURES STATUS (UPDATED) =====
  app.get("/api/buddy/features", async (_req, res) => {
    res.json({
      features: [
        { name: "Vibe Coding", route: "POST /api/buddy/vibe-code", status: "live", description: "Generate full projects from description" },
        { name: "Image Generation", route: "POST /api/generate-image", status: "live", description: "AI image generation via gpt-image-1" },
        { name: "DreamCo Local Voice", route: "POST /api/voice/clone", status: "live", description: "Free local/browser text-to-speech by default; optional external provider only when configured", setup: "No paid key required for local voice" },
        { name: "Creator Studio", route: "GET /api/buddy/creator-studio", status: "live", description: "End-to-end workflows for games, apps, courses, simulations, music videos, and autobiographies" },
        { name: "Creator Build Packet", route: "POST /api/buddy/creator-studio/build-packet", status: "live", description: "Free local project packet for large games, study-to-game courses, autobiographies, and client prototypes" },
        { name: "Model Choice Registry", route: "GET /api/buddy/model-choices", status: "live", description: "User-selectable model families with strengths, watchouts, and budget-first routing" },
        { name: "Restored Bot Family Bridge", route: "GET /api/buddy/restored-bot-families", status: "live", description: "Recovered original bot families connected back to Buddy as capability groups" },
        { name: "Bot End-To-End Readiness", route: "GET /api/buddy/bot-end-to-end-readiness", status: "live", description: "One-by-one local-first readiness audit for every discovered bot and recovered system" },
        { name: "Web Search", route: "POST /api/search/web", status: "live", description: "GitHub + OpenAI synthesis search" },
        { name: "GitHub Intelligence", route: "GET /api/github-intel/trending", status: "live", description: "Hourly GitHub trending + search" },
        { name: "Council Governance", route: "GET /api/council/proposals", status: "live", description: "Bot proposal submission and approval" },
        { name: "Self Training", route: "POST /api/buddy/train", status: "live", description: "Generate coding bootcamp exercises" },
        { name: "Book Study", route: "POST /api/buddy/study-book", status: "live", description: "Extract insights from any nonfiction book" },
        { name: "Game Builder", route: "POST /api/buddy/build-game", status: "live", description: "Build browser-playable games from description" },
        { name: "Course Simulator", route: "POST /api/buddy/simulate-course", status: "live", description: "Simulate full college courses" },
        { name: "Competitive Intel", route: "POST /api/intel/competitive", status: "live", description: "Analyze any competitor" },
        { name: "Data Packages", route: "GET /api/data-packages", status: "live", description: "Sell training data to other AI models" },
        { name: "Code Execution", route: "POST /api/buddy/execute-code", status: "live", description: "Run JS/TS natively; simulate Python, Rust, Go, Java" },
        { name: "Image Analysis", route: "POST /api/buddy/analyze-image", status: "live", description: "GPT-4o vision: screenshots → code, diagrams → schema" },
        { name: "Agent Pipeline", route: "POST /api/buddy/agent-run", status: "live", description: "Multi-step autonomous Plan → Execute → Ship pipeline" },
        { name: "Security Scan", route: "POST /api/buddy/security-scan", status: "live", description: "SAST-level: OWASP Top 10, CWE Top 25, secret detection" },
        { name: "System Architect", route: "POST /api/buddy/architect", status: "live", description: "C4 architecture design with Mermaid + Docker Compose" },
        { name: "Code Translator", route: "POST /api/buddy/translate-code", status: "live", description: "Translate code between any two programming languages" },
        { name: "Code Review", route: "POST /api/buddy/code-review", status: "live", description: "Senior engineer code review with grade + refactored version" },
        { name: "PR Generator", route: "POST /api/buddy/generate-pr", status: "live", description: "Generate PR title, body, commits, changelog from diff" },
        { name: "Deploy Config", route: "POST /api/buddy/deploy-config", status: "live", description: "Docker, Vercel, Railway, Fly.io, K8s, GitHub Actions configs" },
        { name: "Deep Debug", route: "POST /api/buddy/debug-deep", status: "live", description: "Root-cause analysis + fix + prevention strategy" },
        { name: "Memory System", route: "POST /api/buddy/memory/save", status: "live", description: "Persistent memory: projects, preferences, decisions" },
        { name: "Code Refactor", route: "POST /api/buddy/refactor", status: "live", description: "SOLID + DRY + TypeScript refactor with change explanations" },
      ],
    });
  });

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

  app.post("/api/bots/normalize", async (req, res) => {
    const allBots = await storage.listBotProfiles();
    let fixed = 0;
    const issues: string[] = [];
    const tierFlags: string[] = [];

    const DIVISION_TIER_MAP: Record<string, string> = {
      CommandCore: "elite",
      DreamEmpire: "elite",
      DreamAgents: "enterprise",
      DreamAIInfra: "enterprise",
      DreamCyber: "enterprise",
      DreamEntFinance: "enterprise",
      DreamLegal: "enterprise",
      DreamCodeLab: "free",
    };

    function inferTierFromPriceRange(priceRange: string): string | null {
      const trimmed = priceRange?.trim() ?? "";
      if (!trimmed) return null;
      if (trimmed.toLowerCase() === "free") return "free";
      const match = trimmed.match(/\$?([\d,]+)/);
      if (!match) return null;
      const price = parseInt(match[1].replace(",", ""), 10);
      if (price <= 0) return "free";
      if (price < 200) return "pro";
      if (price < 500) return "enterprise";
      return "elite";
    }

    function inferTier(priceRange: string, division: string): string {
      const fromPrice = inferTierFromPriceRange(priceRange);
      if (fromPrice !== null) return fromPrice;
      return DIVISION_TIER_MAP[division] ?? "pro";
    }

    for (const bot of allBots) {
      const updates: Record<string, any> = {};

      if (!bot.systemPrompt || bot.systemPrompt.trim().length < 10) {
        updates.systemPrompt = `You are ${bot.displayName}, a specialized AI bot in the ${bot.division} division of DreamCo Empire OS. Help the user with tasks related to your expertise.`;
        issues.push(`${bot.slug}: missing/short systemPrompt`);
      }

      if (!bot.description || bot.description.trim().length < 5) {
        updates.description = `${bot.displayName} - ${bot.division} division bot`;
        issues.push(`${bot.slug}: missing description`);
      }

      if (!Array.isArray(bot.capabilities) || (bot.capabilities as any[]).length === 0) {
        updates.capabilities = ["general-assistance", "task-execution"];
        issues.push(`${bot.slug}: empty capabilities`);
      }

      if (!Array.isArray(bot.traits) || (bot.traits as any[]).length === 0) {
        updates.traits = ["reliable", "efficient"];
        issues.push(`${bot.slug}: empty traits`);
      }

      if (!bot.revenueModel) {
        updates.revenueModel = "subscription";
        issues.push(`${bot.slug}: missing revenueModel`);
      }

      if (!bot.category) {
        updates.category = "general";
        issues.push(`${bot.slug}: missing category`);
      }

      // Tier validation: fill in missing tier and flag potential miscategorization
      if (!bot.tier || bot.tier.trim() === "") {
        const inferred = inferTier(bot.priceRange ?? "", bot.division ?? "");
        updates.tier = inferred;
        const flag = `${bot.slug}: missing tier — inferred '${inferred}' from priceRange/division`;
        issues.push(flag);
        tierFlags.push(flag);
      } else if (bot.tier?.toLowerCase() === "free") {
        const inferred = inferTier(bot.priceRange ?? "", bot.division ?? "");
        if (inferred !== "free") {
          const flag = `${bot.slug}: tier='free' but priceRange/division suggests '${inferred}' — review needed`;
          tierFlags.push(flag);
        }
      }

      if (Object.keys(updates).length > 0) {
        await storage.updateBotProfile(bot.id, updates);
        fixed++;
      }
    }

    res.json({
      total: allBots.length,
      fixed,
      issues,
      tierFlags,
      message: fixed > 0 ? `Normalized ${fixed} bots` : "All bots already normalized",
    });
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

    let input: { content: string; botSlug?: string; mode?: string };
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

    const mode = (input as any).mode ?? "build";
    const basePrompt = bot?.systemPrompt ?? "You are the central AI brain of DreamCo Empire OS.";
    const botName = bot?.displayName ?? "Empire AI";
    const division = bot?.division ?? "CommandCore";
    const capabilities = Array.isArray(bot?.capabilities) ? (bot.capabilities as string[]) : [];

    // Load bot's learned memories for self-learning context injection
    const memories: string[] = [];
    if (bot?.id) {
      try {
        const memRecords = await storage.listBotMemory(bot.id);
        memRecords.slice(0, 15).forEach((m: any) => {
          if (m.content) memories.push(m.content);
        });
      } catch (_) {}
    }

    const system = buildEnhancedSystemPrompt(basePrompt, botName, division, capabilities, mode, memories, bot?.slug ?? "");

    const userMsg = await storage.createMessage(conversationId, "user", input.content);

    const history = await storage.getMessages(conversationId);
    // Trim history to MAX_HISTORY_MSG — prevents unbounded token growth on long conversations
    const historyMsgs: Array<{ role: "user" | "assistant"; content: string }> = history.map((m) => ({
      role: m.role === "assistant" ? "assistant" : "user",
      content: m.content,
    }));
    const trimmedHistory = trimHistory(historyMsgs) as Array<{ role: "user" | "assistant"; content: string }>;
    const messagesForModel: Array<{ role: "system" | "user" | "assistant"; content: string }> = [
      { role: "system" as const, content: system },
      ...trimmedHistory,
    ];

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    const stream = await openai.chat.completions.create({
      model: CHAT_MODEL,
      messages: messagesForModel,
      stream: true,
      max_completion_tokens: MAX_CHAT_TOKENS, // was 4000 — 2k saves ~50% output cost
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

      // Extract and persist learning log entries from the response (self-learning memory)
      if (bot?.id) {
        const learningMatch = assistantText.match(/🧠\s*LEARNING\s*LOG:\s*(.+?)(?:\n|$)/i);
        if (learningMatch && learningMatch[1]?.trim()) {
          try {
            await storage.createBotMemory({ botId: bot.id, key: "learning", value: learningMatch[1].trim(), category: "learning" });
          } catch (_) {}
        }
      }
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

  // ─── Safe Deal Rails: Stripe-Optional Manual Settlement ─────────────

  app.get("/api/payments/safe-rails/status", async (_req, res) => {
    const deals = await getOfflineDeals();
    const openDeals = deals.filter(d => ["draft", "sent", "approved"].includes(d.status));
    const paidDeals = deals.filter(d => d.status === "paid");
    res.json({
      mode: "safe-deal-rails",
      stripeRequired: false,
      cardDataStored: false,
      custodyOfFunds: false,
      moneyMovement: "external-provider-or-manual-confirmation",
      openDeals: openDeals.length,
      paidDeals: paidDeals.length,
      totalTracked: deals.length,
      paidVolume: paidDeals.reduce((sum, deal) => sum + deal.amount, 0),
      guardrails: [
        "Buddy creates invoices, approvals, reminders, and reconciliation records.",
        "Buddy does not process cards, hold funds, or store bank credentials.",
        "Mark a deal paid only after you confirm funds in the payment provider or bank.",
        "Use licensed providers for regulated money movement, lending, escrow, or card processing.",
      ],
    });
  });

  app.get("/api/payments/offline-deals", async (_req, res) => {
    res.json({ deals: await getOfflineDeals() });
  });

  app.post("/api/payments/offline-deals", async (req, res) => {
    const parsed = offlineDealSchema.safeParse(req.body ?? {});
    if (!parsed.success) return res.status(400).json(zodValidationError(parsed.error));

    const now = new Date();
    const dueAt = new Date(now);
    dueAt.setDate(dueAt.getDate() + parsed.data.dueDays);

    const existing = await getOfflineDeals();
    const deal: OfflineDeal = {
      id: `od_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`,
      invoiceNumber: `DRM-${now.getFullYear()}-${String(existing.length + 1).padStart(5, "0")}`,
      title: parsed.data.title,
      customerName: parsed.data.customerName,
      customerEmail: parsed.data.customerEmail.toLowerCase(),
      amount: Math.round(parsed.data.amount * 100) / 100,
      currency: parsed.data.currency.toUpperCase(),
      method: parsed.data.method,
      description: parsed.data.description,
      status: "draft",
      paymentInstructions: buildPaymentInstructions(parsed.data.method, parsed.data.amount, parsed.data.currency.toUpperCase()),
      guardrails: [
        "No card numbers or bank credentials are accepted here.",
        "Customer approval should be saved before fulfillment.",
        "Funds must be verified in the external account before paid status.",
        "High-risk, escrow, lending, or regulated transfers require a licensed provider.",
      ],
      createdAt: now.toISOString(),
      dueAt: dueAt.toISOString(),
      auditTrail: [{ at: now.toISOString(), event: "created", note: "Safe offline deal created." }],
    };

    await saveOfflineDeals([deal, ...existing]);
    res.status(201).json(deal);
  });

  app.patch("/api/payments/offline-deals/:id/status", async (req, res) => {
    const parsed = offlineDealStatusSchema.safeParse(req.body ?? {});
    if (!parsed.success) return res.status(400).json(zodValidationError(parsed.error));

    const deals = await getOfflineDeals();
    const index = deals.findIndex(deal => deal.id === req.params.id);
    if (index === -1) return res.status(404).json({ message: "Offline deal not found" });

    const updated: OfflineDeal = {
      ...deals[index],
      status: parsed.data.status,
      auditTrail: [
        { at: new Date().toISOString(), event: `status:${parsed.data.status}`, note: parsed.data.note || undefined },
        ...deals[index].auditTrail,
      ],
    };
    deals[index] = updated;
    await saveOfflineDeals(deals);
    res.json(updated);
  });

  app.get("/api/payments/offline-deals/export", async (_req, res) => {
    const deals = await getOfflineDeals();
    const rows = [
      ["Invoice", "Title", "Customer", "Email", "Amount", "Currency", "Method", "Status", "Created", "Due"].join(","),
      ...deals.map(deal => [
        deal.invoiceNumber,
        JSON.stringify(deal.title),
        JSON.stringify(deal.customerName),
        deal.customerEmail,
        deal.amount,
        deal.currency,
        deal.method,
        deal.status,
        deal.createdAt,
        deal.dueAt,
      ].join(",")),
    ];
    res.setHeader("Content-Type", "text/csv");
    res.setHeader("Content-Disposition", "attachment; filename=dreamco-safe-deal-ledger.csv");
    res.send(rows.join("\n"));
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
        details: { stackTrace: `Error at ${cat}.handler:${10 + i}\n  at processQueue (worker.ts:${44 + i})` },
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

  // ─── Formula Vault Routes ────────────────────────────────────────────

  app.get("/api/formulas", async (_req, res) => {
    const list = await storage.listFormulas();
    res.json(list);
  });

  app.get("/api/formulas/:id", async (req, res) => {
    const id = Number(req.params.id);
    if (isNaN(id)) return res.status(400).json({ message: "Invalid formula ID" });
    const formula = await storage.getFormula(id);
    if (!formula) return res.status(404).json({ message: "Formula not found" });
    res.json(formula);
  });

  app.post("/api/formulas", async (req, res) => {
    try {
      const input = insertFormulaSchema.parse(req.body);
      const formula = await storage.createFormula(input);
      res.status(201).json(formula);
    } catch (err) {
      if (err instanceof z.ZodError) return res.status(400).json(zodValidationError(err));
      throw err;
    }
  });

  app.patch("/api/formulas/:id", async (req, res) => {
    const id = Number(req.params.id);
    if (isNaN(id)) return res.status(400).json({ message: "Invalid formula ID" });
    const existing = await storage.getFormula(id);
    if (!existing) return res.status(404).json({ message: "Formula not found" });
    const updated = await storage.updateFormula(id, req.body);
    res.json(updated);
  });

  app.delete("/api/formulas/:id", async (req, res) => {
    const id = Number(req.params.id);
    if (isNaN(id)) return res.status(400).json({ message: "Invalid formula ID" });
    const existing = await storage.getFormula(id);
    if (!existing) return res.status(404).json({ message: "Formula not found" });
    await storage.deleteFormula(id);
    res.status(204).send();
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

      const inferTierFromName = (name: string | null | undefined): string | null => {
        if (!name) return null;
        const lower = name.toLowerCase();
        if (lower.includes("elite")) return "elite";
        if (lower.includes("enterprise")) return "enterprise";
        if (lower.includes("pro")) return "pro";
        if (lower.includes("free")) return "free";
        return null;
      };

      const productsMap = new Map<string, any>();
      for (const row of result.rows) {
        const r = row as any;
        if (!productsMap.has(r.product_id)) {
          const meta = r.product_metadata ?? {};
          if (!meta.tier) {
            const inferred = inferTierFromName(r.product_name);
            if (inferred) meta.tier = inferred;
          }
          productsMap.set(r.product_id, {
            id: r.product_id,
            name: r.product_name,
            description: r.product_description,
            metadata: meta,
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

      const dbProducts = Array.from(productsMap.values());

      if (dbProducts.length > 0) {
        return res.json({ products: dbProducts });
      }

      // DB is empty — sync hasn't finished yet. Fall back to a live Stripe API call.
      try {
        const stripe = await getUncachableStripeClient();
        const [stripeProducts, stripePrices] = await Promise.all([
          stripe.products.list({ active: true, limit: 100 }),
          stripe.prices.list({ active: true, limit: 100 }),
        ]);

        const livePricesByProduct = new Map<string, any[]>();
        for (const price of stripePrices.data) {
          const pid = typeof price.product === "string" ? price.product : (price.product as any).id;
          if (!livePricesByProduct.has(pid)) livePricesByProduct.set(pid, []);
          livePricesByProduct.get(pid)!.push({
            id: price.id,
            unit_amount: price.unit_amount,
            currency: price.currency,
            recurring: price.recurring,
          });
        }

        const liveProducts = stripeProducts.data.map((p) => {
          const meta: Record<string, string> = { ...(p.metadata as Record<string, string>) };
          if (!meta.tier) {
            const inferred = inferTierFromName(p.name);
            if (inferred) meta.tier = inferred;
          }
          return {
            id: p.id,
            name: p.name,
            description: p.description,
            metadata: meta,
            prices: livePricesByProduct.get(p.id) ?? [],
          };
        });

        return res.json({ products: liveProducts, source: "live" });
      } catch (liveError: any) {
        console.warn("Live Stripe fallback also failed:", liveError.message);
        return res.json({ products: [], syncing: true });
      }
    } catch (error: any) {
      console.error("Failed to list products:", error.message);
      res.json({ products: [], syncing: true });
    }
  });

  app.post("/api/stripe/checkout", async (req, res) => {
    try {
      const { priceId, successUrl, cancelUrl } = req.body;
      if (!priceId) {
        return res.status(400).json({ error: "priceId is required" });
      }

      const stripe = await getUncachableStripeClient();
      const baseUrl = `${req.protocol}://${req.get("host")}`;

      const session = await stripe.checkout.sessions.create({
        payment_method_types: ["card"],
        line_items: [{ price: priceId, quantity: 1 }],
        mode: "subscription",
        success_url: successUrl ?? `${baseUrl}/pricing?success=true&session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: cancelUrl ?? `${baseUrl}/pricing?canceled=true`,
      });

      res.json({ url: session.url });
    } catch (error: any) {
      console.error("Checkout error:", error.message);
      res.status(500).json({ error: "Failed to create checkout session" });
    }
  });

  app.get("/api/stripe/subscription-status", async (_req, res) => {
    try {
      let hasActiveSubscription = false;
      let tier: string | null = null;

      // Try DB first — join through subscription_items → prices → products to get tier metadata
      try {
        const result = await db.execute(sql`
          SELECT s.id, p.metadata
          FROM stripe.subscriptions s
          LEFT JOIN stripe.subscription_items si ON si.subscription = s.id
          LEFT JOIN stripe.prices pr ON pr.id = si.price
          LEFT JOIN stripe.products p ON p.id = pr.product
          WHERE s.status IN ('active', 'trialing')
          ORDER BY s.created DESC
          LIMIT 1
        `);

        if (result.rows.length > 0) {
          hasActiveSubscription = true;
          const row = result.rows[0] as any;
          const metadata = typeof row.metadata === "string" ? JSON.parse(row.metadata) : row.metadata;
          tier = metadata?.tier ?? null;
        }
      } catch {
        // DB join failed (tables may not exist yet), fall through to live API
      }

      if (!hasActiveSubscription) {
        // Fall back to live Stripe API in case DB sync hasn't populated yet
        try {
          const stripe = await getUncachableStripeClient();

          // Check if a customer email was stored from a previous restore operation
          let customerEmail: string | null = null;
          try {
            const stored = await storage.getSetting("stripe_customer_email");
            if (stored && typeof stored.value === "string" && stored.value.includes("@")) {
              customerEmail = stored.value;
            }
          } catch { /* ignore */ }

          let subs;
          if (customerEmail) {
            // Look up the specific customer by email first, then list their subscriptions
            const customers = await stripe.customers.list({ email: customerEmail, limit: 1 });
            if (customers.data.length > 0) {
              subs = await stripe.subscriptions.list({
                customer: customers.data[0].id,
                status: "active",
                limit: 1,
                expand: ["data.items.data.price.product"],
              });
            }
          }

          if (!subs || subs.data.length === 0) {
            subs = await stripe.subscriptions.list({
              status: "active",
              limit: 1,
              expand: ["data.items.data.price.product"],
            });
          }

          if (subs.data.length > 0) {
            hasActiveSubscription = true;
            const sub = subs.data[0];
            const item = sub.items?.data?.[0];
            const product = item?.price?.product as any;
            tier = product?.metadata?.tier ?? null;
          }
        } catch {
          // Live API also failed — return no subscription
        }
      }

      res.json({ hasActiveSubscription, tier });
    } catch (error: any) {
      console.error("Subscription status error:", error.message);
      res.json({ hasActiveSubscription: false, tier: null });
    }
  });

  app.post("/api/stripe/restore-subscription", async (req, res) => {
    try {
      const { email } = req.body;
      if (!email || typeof email !== "string" || !email.includes("@")) {
        return res.status(400).json({ error: "A valid email address is required" });
      }

      const stripe = await getUncachableStripeClient();

      // Find Stripe customer by email
      const customers = await stripe.customers.list({ email: email.trim().toLowerCase(), limit: 5 });
      if (customers.data.length === 0) {
        return res.status(404).json({ error: "No Stripe account found for that email address" });
      }

      // Check each matching customer for an active subscription
      let hasActiveSubscription = false;
      let tier: string | null = null;
      let resolvedCustomerId: string | null = null;

      for (const customer of customers.data) {
        const subs = await stripe.subscriptions.list({
          customer: customer.id,
          status: "active",
          limit: 1,
          expand: ["data.items.data.price.product"],
        });
        if (subs.data.length > 0) {
          hasActiveSubscription = true;
          resolvedCustomerId = customer.id;
          const sub = subs.data[0];
          const item = sub.items?.data?.[0];
          const product = item?.price?.product as any;
          tier = product?.metadata?.tier ?? null;
          break;
        }
        // Also check trialing
        const trialSubs = await stripe.subscriptions.list({
          customer: customer.id,
          status: "trialing",
          limit: 1,
          expand: ["data.items.data.price.product"],
        });
        if (trialSubs.data.length > 0) {
          hasActiveSubscription = true;
          resolvedCustomerId = customer.id;
          const sub = trialSubs.data[0];
          const item = sub.items?.data?.[0];
          const product = item?.price?.product as any;
          tier = product?.metadata?.tier ?? null;
          break;
        }
      }

      if (!hasActiveSubscription) {
        return res.status(404).json({ error: "No active subscription found for that email address" });
      }

      // Persist the customer email server-side so subscription status survives browser data clearing
      await storage.upsertSetting("stripe_customer_email", email.trim().toLowerCase());
      if (resolvedCustomerId) {
        await storage.upsertSetting("stripe_customer_id", resolvedCustomerId);
      }

      res.json({ hasActiveSubscription, tier });
    } catch (error: any) {
      console.error("Restore subscription error:", error.message);
      res.status(500).json({ error: "Failed to look up subscription" });
    }
  });

  app.post("/api/stripe/portal", async (req, res) => {
    try {
      // Resolve customer ID server-side from the active subscription — never trust client input
      let customerId: string | null = null;

      // Prefer the customer ID persisted by the restore flow (survives browser data clearing)
      try {
        const stored = await storage.getSetting("stripe_customer_id");
        if (stored && typeof stored.value === "string" && stored.value.startsWith("cus_")) {
          customerId = stored.value;
        }
      } catch { /* ignore */ }

      if (!customerId) {
        try {
          const result = await db.execute(sql`
            SELECT customer
            FROM stripe.subscriptions
            WHERE status IN ('active', 'trialing')
            ORDER BY created DESC
            LIMIT 1
          `);
          if (result.rows.length > 0) {
            customerId = (result.rows[0] as any).customer as string;
          }
        } catch {
          // DB lookup failed, fall through to live API
        }
      }

      if (!customerId) {
        // Fall back to live Stripe API — also check stored email for customer lookup
        const stripe = await getUncachableStripeClient();

        try {
          const emailSetting = await storage.getSetting("stripe_customer_email");
          if (emailSetting && typeof emailSetting.value === "string" && emailSetting.value.includes("@")) {
            const customers = await stripe.customers.list({ email: emailSetting.value, limit: 1 });
            if (customers.data.length > 0) {
              customerId = customers.data[0].id;
            }
          }
        } catch { /* ignore */ }

        if (!customerId) {
          const subs = await stripe.subscriptions.list({ status: "active", limit: 1 });
          if (subs.data.length > 0) {
            customerId = subs.data[0].customer as string;
          }
        }
      }

      if (!customerId) {
        return res.status(404).json({ error: "No active subscription found" });
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

      // Stripe not configured at all (missing keys)
      const msg: string = error?.message ?? "";
      if (msg.includes("Stripe not configured") || msg.includes("connection not found")) {
        return res.status(503).json({
          error: "Stripe is not configured on this server.",
          detail: "Add STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY as environment secrets to enable billing.",
          code: "stripe_not_configured",
        });
      }

      // Stripe billing portal not set up in the Dashboard
      if (
        error?.type === "invalid_request_error" &&
        (msg.toLowerCase().includes("no configuration") ||
          msg.toLowerCase().includes("portal") ||
          msg.toLowerCase().includes("billing portal"))
      ) {
        return res.status(422).json({
          error: "Billing Portal is not enabled in your Stripe Dashboard.",
          detail: "Go to stripe.com/dashboard → Settings → Billing → Customer portal and activate it.",
          code: "portal_not_configured",
        });
      }

      // Stripe API key invalid / authentication failure
      if (error?.type === "authentication_error" || error?.statusCode === 401) {
        return res.status(503).json({
          error: "Stripe authentication failed.",
          detail: "Check that your STRIPE_SECRET_KEY secret is correct and has not expired.",
          code: "stripe_auth_error",
        });
      }

      res.status(500).json({
        error: "Failed to open billing portal.",
        detail: msg || "An unexpected error occurred. Please try again.",
        code: "portal_error",
      });
    }
  });

  const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 500 * 1024, files: 20 },
  });

  app.post("/api/batch/process", upload.array("files", 20), async (req, res) => {
    try {
      const files = req.files as Express.Multer.File[] | undefined;
      const { instruction, language, mode } = req.body;

      if (!instruction && (!files || files.length === 0)) {
        return res.status(400).json({ error: "Provide files or an instruction" });
      }

      res.setHeader("Content-Type", "text/event-stream");
      res.setHeader("Cache-Control", "no-cache");
      res.setHeader("Connection", "keep-alive");

      const sendEvent = (event: { type: string; [key: string]: unknown }) => {
        res.write(`data: ${JSON.stringify(event)}\n\n`);
      };

      let items: Array<{ name: string; content: string; type: string }> = [];

      if (files && files.length > 0) {
        items = files.map((f) => ({
          name: f.originalname,
          content: f.buffer.toString("utf-8").slice(0, 8000),
          type: f.mimetype || "text/plain",
        }));
      } else if (instruction) {
        const chunks = splitLongRequest(instruction, 2000);
        items = chunks.map((chunk, i) => ({
          name: `Part ${i + 1} of ${chunks.length}`,
          content: chunk,
          type: "text/request",
        }));
      }

      const batchInstruction = instruction || "Analyze and process this file. Provide a summary, key findings, and any suggestions for improvement.";

      await batchProcessWithSSE(
        items,
        async (item) => {
          const isDataFile = item.name.endsWith(".csv") || item.name.endsWith(".json") || item.name.endsWith(".tsv");
          const isCodeFile = /\.(ts|tsx|js|jsx|py|go|rs|java|kt|swift|cpp|cs|rb|php|sol|sql)$/i.test(item.name);

          let systemMsg = "";
          if (isDataFile) {
            systemMsg = `You are a data analyst AI. Process this ${item.name} data file. ${batchInstruction}. Be concise and actionable.`;
          } else if (isCodeFile) {
            systemMsg = `You are a senior code reviewer AI. Review this ${language || "code"} file named "${item.name}". ${batchInstruction}. Be concise.`;
          } else if (item.type === "text/request") {
            systemMsg = `You are DreamCodeLab's AI assistant. Complete this part of a larger request in ${language || "TypeScript"}. Be thorough and provide complete code/output.`;
          } else {
            systemMsg = `You are DreamCodeLab's AI assistant. Process this content from "${item.name}". ${batchInstruction}. Be concise.`;
          }

          const response = await openai.chat.completions.create({
            model: "gpt-4.1-mini",
            messages: [
              { role: "system", content: systemMsg },
              { role: "user", content: item.content },
            ],
            max_completion_tokens: 8192,
          });

          return response.choices[0]?.message?.content || "No output";
        },
        sendEvent,
        { retries: 3, minTimeout: 2000 }
      );

      res.end();
    } catch (error: any) {
      console.error("Batch process error:", error.message);
      if (!res.headersSent) {
        res.status(500).json({ error: "Batch processing failed" });
      } else {
        res.write(`data: ${JSON.stringify({ type: "error", message: error.message })}\n\n`);
        res.end();
      }
    }
  });

  function splitLongRequest(text: string, maxChunkSize: number): string[] {
    if (text.length <= maxChunkSize) return [text];
    const chunks: string[] = [];
    const paragraphs = text.split(/\n\n+/);
    let current = "";

    for (const para of paragraphs) {
      if (current.length + para.length + 2 > maxChunkSize && current.length > 0) {
        chunks.push(current.trim());
        current = "";
      }
      if (para.length > maxChunkSize) {
        if (current) { chunks.push(current.trim()); current = ""; }
        for (let i = 0; i < para.length; i += maxChunkSize) {
          chunks.push(para.slice(i, i + maxChunkSize));
        }
      } else {
        current += (current ? "\n\n" : "") + para;
      }
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks.length > 0 ? chunks : [text];
  }

  const codeRunLimiter = new Map<string, number>();
  const CODE_MAX_LENGTH = 10000;
  const PROMPT_MAX_LENGTH = 1000;
  const RATE_LIMIT_MS = 3000;

  app.post("/api/code/run", async (req, res) => {
    try {
      const { code, language, prompt } = req.body;
      if (!code && !prompt) {
        return res.status(400).json({ error: "code or prompt is required" });
      }

      if (code && typeof code === "string" && code.length > CODE_MAX_LENGTH) {
        return res.status(400).json({ error: `Code must be under ${CODE_MAX_LENGTH} characters` });
      }
      if (prompt && typeof prompt === "string" && prompt.length > PROMPT_MAX_LENGTH) {
        return res.status(400).json({ error: `Prompt must be under ${PROMPT_MAX_LENGTH} characters` });
      }

      const clientIp = req.ip || "unknown";
      const lastCall = codeRunLimiter.get(clientIp) || 0;
      if (Date.now() - lastCall < RATE_LIMIT_MS) {
        return res.status(429).json({ error: "Please wait a moment before running again" });
      }
      codeRunLimiter.set(clientIp, Date.now());

      res.setHeader("Content-Type", "text/event-stream");
      res.setHeader("Cache-Control", "no-cache");
      res.setHeader("Connection", "keep-alive");

      const systemPrompt = prompt && !code
        ? `You are DreamCodeLab's AI coding assistant. The user wants you to generate code. Generate clean, production-ready code in ${language || "TypeScript"}. Respond with ONLY the code, no explanations. After the code block, add a separator "---OUTPUT---" followed by what the expected output would be if this code were run.`
        : `You are DreamCodeLab's AI code execution engine. The user has written code in ${language || "TypeScript"}. Analyze and simulate running this code. First, check for any syntax errors or issues. Then simulate the execution and provide the output. Format your response as:
---ANALYSIS---
Brief analysis of the code (1-2 sentences)
---OUTPUT---
The simulated output of running this code (show exactly what would print/return)
---SUGGESTIONS---
Any improvements or fixes (optional, 1-2 bullet points max)`;

      const userMessage = prompt && !code
        ? `Generate ${language || "TypeScript"} code for: ${prompt}`
        : `Run this ${language || "TypeScript"} code:\n\`\`\`\n${code}\n\`\`\``;

      const stream = await openai.chat.completions.create({
        model: "gpt-4.1-mini",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage },
        ],
        stream: true,
        max_completion_tokens: 8192,
      });

      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          res.write(`data: ${JSON.stringify({ content })}\n\n`);
        }
      }
      res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
      res.end();
    } catch (error: any) {
      console.error("Code run error:", error.message);
      if (!res.headersSent) {
        res.status(500).json({ error: "Code execution failed" });
      } else {
        res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
        res.end();
      }
    }
  });

  // ===== PLATFORM CONNECTIONS =====
  app.get("/api/platform-connections", async (_req, res) => {
    const connections = await storage.listPlatformConnections();
    res.json(connections);
  });

  app.post("/api/platform-connections", async (req, res) => {
    const parsed = insertPlatformConnectionSchema.safeParse(req.body);
    if (!parsed.success) return res.status(400).json(zodValidationError(parsed.error));
    const conn = await storage.createPlatformConnection(parsed.data);
    res.json(conn);
  });

  app.patch("/api/platform-connections/:id", async (req, res) => {
    const id = parseInt(req.params.id);
    const conn = await storage.updatePlatformConnection(id, req.body);
    if (!conn) return res.status(404).json({ error: "Connection not found" });
    res.json(conn);
  });

  app.delete("/api/platform-connections/:id", async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deletePlatformConnection(id);
    res.json({ success: true });
  });

  app.post("/api/platform-connections/disconnect-all", async (_req, res) => {
    const connections = await storage.listPlatformConnections();
    for (const conn of connections) {
      await storage.deletePlatformConnection(conn.id);
    }
    res.json({ success: true });
  });

  // Alias for connections as requested in the task
  app.post("/api/connections", async (req, res) => {
    const conn = await storage.createPlatformConnection(req.body);
    res.json(conn);
  });

  // ===== KILL SWITCH =====
  app.get("/api/kill-switch", async (_req, res) => {
    const setting = await storage.getSetting("kill_switch");
    res.json({ enabled: (setting?.value as any)?.enabled ?? false, updatedAt: setting?.updatedAt });
  });

  app.post("/api/kill-switch", async (req, res) => {
    const { enabled } = req.body;
    const setting = await storage.upsertSetting("kill_switch", { enabled: !!enabled, triggeredAt: new Date().toISOString() });
    res.json({ enabled: (setting.value as any)?.enabled ?? false, updatedAt: setting.updatedAt });
  });

  // ===== PLUGINS =====
  app.get("/api/plugins", async (req, res) => {
    const allPlugins = await storage.listPlugins();
    const search = (req.query.search as string)?.toLowerCase();
    const category = req.query.category as string;
    let filtered = allPlugins;
    if (search) filtered = filtered.filter(p => p.name.toLowerCase().includes(search) || p.description.toLowerCase().includes(search));
    if (category && category !== "all") filtered = filtered.filter(p => p.category === category);
    res.json(filtered);
  });

  app.post("/api/plugins", async (req, res) => {
    const parsed = insertPluginSchema.safeParse(req.body);
    if (!parsed.success) return res.status(400).json(zodValidationError(parsed.error));
    const plugin = await storage.createPlugin(parsed.data);
    res.json(plugin);
  });

  app.patch("/api/plugins/:id", async (req, res) => {
    const id = parseInt(req.params.id);
    const plugin = await storage.updatePlugin(id, req.body);
    if (!plugin) return res.status(404).json({ error: "Plugin not found" });
    res.json(plugin);
  });

  app.post("/api/plugins/:id/download", async (req, res) => {
    const id = parseInt(req.params.id);
    const plugin = await storage.incrementPluginDownloads(id);
    if (!plugin) return res.status(404).json({ error: "Plugin not found" });
    res.json(plugin);
  });

  app.post("/api/plugins/:id/install", async (req, res) => {
    const id = parseInt(req.params.id);
    const plugin = await storage.updatePlugin(id, { installed: true });
    if (!plugin) return res.status(404).json({ error: "Plugin not found" });
    res.json(plugin);
  });

  app.post("/api/plugins/:id/uninstall", async (req, res) => {
    const id = parseInt(req.params.id);
    const plugin = await storage.updatePlugin(id, { installed: false });
    if (!plugin) return res.status(404).json({ error: "Plugin not found" });
    res.json(plugin);
  });

  app.delete("/api/plugins/:id", async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deletePlugin(id);
    res.json({ success: true });
  });

  // ===== BOT MEMORY =====
  app.get("/api/bots/:botId/memory", async (req, res) => {
    const botId = parseInt(req.params.botId);
    const memories = await storage.listBotMemory(botId);
    res.json(memories);
  });

  app.post("/api/bots/:botId/memory", async (req, res) => {
    const botId = parseInt(req.params.botId);
    const parsed = insertBotMemorySchema.safeParse({ ...req.body, botId });
    if (!parsed.success) return res.status(400).json(zodValidationError(parsed.error));
    const mem = await storage.createBotMemory(parsed.data);
    res.json(mem);
  });

  app.delete("/api/bots/:botId/memory/:memId", async (req, res) => {
    const memId = parseInt(req.params.memId);
    await storage.deleteBotMemory(memId);
    res.json({ success: true });
  });

  // ===== SYSTEM SNAPSHOTS (TIME CAPSULE) =====
  app.get("/api/snapshots", async (_req, res) => {
    const snapshots = await storage.listSystemSnapshots();
    res.json(snapshots);
  });

  app.post("/api/snapshots", async (req, res) => {
    try {
      const bots = await storage.listBotProfiles();
      const tasks = await storage.listTasks();
      const settings: any[] = [];
      for (const key of ["autonomy_mode", "kill_switch"]) {
        const s = await storage.getSetting(key);
        if (s) settings.push(s);
      }
      const snapshot = await storage.createSystemSnapshot({
        name: req.body.name || `Snapshot ${new Date().toLocaleString()}`,
        description: req.body.description || "",
        snapshotData: { botCount: bots.length, taskCount: tasks.length, settings, timestamp: new Date().toISOString() },
        botCount: bots.length,
        taskCount: tasks.length,
        settingsCount: settings.length,
      });
      res.json(snapshot);
    } catch (err: any) {
      res.status(500).json({ error: err.message });
    }
  });

  app.delete("/api/snapshots/:id", async (req, res) => {
    const id = parseInt(req.params.id);
    await storage.deleteSystemSnapshot(id);
    res.json({ success: true });
  });

  // ===== COST TRACKING =====
  app.get("/api/costs", async (_req, res) => {
    const events = await storage.listCostEvents(100);
    res.json(events);
  });

  app.get("/api/costs/summary", async (_req, res) => {
    const summary = await storage.getCostSummary();
    res.json(summary);
  });

  // ===== GITHUB SYNC =====
  app.get("/api/github/status", async (_req, res) => {
    try {
      const { getRepoInfo, getPullRequests } = await import("./github-sync");
      const [repo, prs] = await Promise.all([getRepoInfo(), getPullRequests()]);
      res.json({ connected: true, repo: { name: repo.full_name, stars: repo.stargazers_count, forks: repo.forks_count, description: repo.description, url: repo.html_url, defaultBranch: repo.default_branch }, pullRequests: prs.map((pr: any) => ({ id: pr.number, title: pr.title, state: pr.state, url: pr.html_url, createdAt: pr.created_at, author: pr.user?.login })) });
    } catch (e: any) {
      // Try unauthenticated fetch for public repo info as fallback
      try {
        const r = await fetch("https://api.github.com/repos/DreamCo-Technologies/Dreamcobots", {
          headers: { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
        });
        if (r.ok) {
          const repo = await r.json();
          res.json({ connected: true, tokenValid: false, repo: { name: repo.full_name, stars: repo.stargazers_count, forks: repo.forks_count, description: repo.description, url: repo.html_url, defaultBranch: repo.default_branch }, pullRequests: [] });
          return;
        }
      } catch {}
      // Return graceful 200 so frontend shows "offline" state rather than crashing
      res.json({ connected: false, error: e.message?.replace(/ghp_[a-zA-Z0-9]+|ghs_[a-zA-Z0-9]+/, "***") ?? "GitHub token not configured" });
    }
  });

  app.post("/api/github/sync", async (_req, res) => {
    try {
      const { exec } = await import("child_process");
      const { promisify } = await import("util");
      const execAsync = promisify(exec);
      const token = process.env.GITHUB_TOKEN || process.env.GITHUB_PERSONAL_ACCESS_TOKEN || "";
      if (!token) {
        return res.status(400).json({ success: false, error: "GitHub token secret not set" });
      }
      const remote = `https://${token}@github.com/DreamCo-Technologies/Dreamcobots.git`;
      const { stdout, stderr } = await execAsync(
        `git --no-optional-locks push "${remote}" HEAD:codex/recover-buddy-after-import 2>&1 || true`,
        { env: process.env, timeout: 60000 }
      );
      const localSha = (await execAsync("git --no-optional-locks rev-parse HEAD")).stdout.trim();
      const localMsg = (await execAsync("git --no-optional-locks log -1 --pretty=format:%s")).stdout.trim();
      const success = !stderr.includes("error:") && !stdout.includes("error:");
      res.json({
        success,
        status: success ? "connected" : "error",
        sha: localSha,
        message: localMsg,
        lastSync: new Date().toISOString(),
        output: (stdout + stderr).replace(token, "***").trim(),
      });
    } catch (e: any) {
      res.status(500).json({ success: false, error: e.message?.replace(process.env.GITHUB_TOKEN || process.env.GITHUB_PERSONAL_ACCESS_TOKEN || "TOKEN", "***") });
    }
  });

  app.post("/api/github/push-all", async (_req, res) => {
    try {
      const { pushAllBotsToGitHub, pushFile, buildMasterReadme } = await import("./github-sync");
      const bots = await storage.listBotProfiles();
      const result = await pushAllBotsToGitHub(bots);
      // push master README after all bots
      try {
        await pushFile("README.md", buildMasterReadme(bots, result.byLang), "docs: update master README from Empire OS");
      } catch {}
      res.json({ success: true, pushed: result.pushed, errors: result.errors.slice(0, 20), byLang: result.byLang, total: bots.length });
    } catch (e: any) {
      res.status(500).json({ success: false, error: e.message });
    }
  });

  app.post("/api/github/push-source", async (_req, res) => {
    try {
      const { pushSourceCode } = await import("./github-sync");
      const result = await pushSourceCode();
      res.json({ success: true, pushed: result.pushed, sha: result.sha, errors: result.errors.slice(0, 10), skipped: result.skipped ?? false });
    } catch (e: any) {
      res.status(500).json({ success: false, error: e.message });
    }
  });

  // Auto-sync status + manual trigger
  app.get("/api/github/auto-sync", async (_req, res) => {
    try {
      const { getAutoSyncStatus } = await import("./github-sync");
      res.json(getAutoSyncStatus());
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  app.post("/api/github/auto-sync", async (_req, res) => {
    try {
      const { runAutoSync } = await import("./github-sync");
      const result = await runAutoSync();
      res.json({ success: true, pushed: result.pushed, sha: result.sha, errors: result.errors.slice(0, 10), skipped: result.skipped ?? false });
    } catch (e: any) {
      res.status(500).json({ success: false, error: e.message });
    }
  });

  app.get("/api/github/contents", async (req, res) => {
    try {
      const { getRepoContents } = await import("./github-sync");
      const path = (req.query.path as string) ?? "";
      const contents = await getRepoContents(path);
      res.json(contents);
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  app.get("/api/github/classify", async (_req, res) => {
    const { classifyBotLanguage } = await import("./github-sync");
    const bots = await storage.listBotProfiles();
    const classified = bots.map(b => ({ id: b.id, slug: b.slug, displayName: b.displayName, division: b.division, language: classifyBotLanguage(b) }));
    const summary = { python: classified.filter(b => b.language === "python").length, java: classified.filter(b => b.language === "java").length, typescript: classified.filter(b => b.language === "typescript").length, general: classified.filter(b => b.language === "general").length, total: classified.length };
    res.json({ summary, bots: classified });
  });

  // List workflows + recent runs for Live Dashboard tab
  app.get("/api/github/workflows", async (_req, res) => {
    try {
      const { getToken } = await import("./github-sync");
      const token = getToken();
      const REPO = "DreamCo-Technologies/Dreamcobots";
      const headers = { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "DreamCo-Empire-OS" };
      const [wfRes, runsRes] = await Promise.all([
        fetch(`https://api.github.com/repos/${REPO}/actions/workflows?per_page=50`, { headers }),
        fetch(`https://api.github.com/repos/${REPO}/actions/runs?per_page=20`, { headers }),
      ]);
      const [wfData, runsData] = await Promise.all([wfRes.json() as any, runsRes.json() as any]);
      res.json({
        workflows: (wfData.workflows ?? []).map((w: any) => ({ id: w.id, name: w.name, path: w.path, state: w.state, html_url: w.html_url })),
        runs: (runsData.workflow_runs ?? []).map((r: any) => ({ id: r.id, name: r.name, status: r.status, conclusion: r.conclusion, created_at: r.created_at, html_url: r.html_url, workflow_id: r.workflow_id })),
      });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // Get last completed Live Dashboard run with job results
  app.get("/api/github/last-dashboard-run", async (_req, res) => {
    try {
      const { getToken } = await import("./github-sync");
      const token = getToken();
      const REPO = "DreamCo-Technologies/Dreamcobots";
      const DASHBOARD_WF_ID = 284581909;
      const headers = { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "DreamCo-Empire-OS" };
      // Get last 5 runs of the dashboard workflow
      const runsRes = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${DASHBOARD_WF_ID}/runs?per_page=5&status=completed`, { headers });
      const runsData = await runsRes.json() as any;
      const runs = runsData.workflow_runs ?? [];
      if (runs.length === 0) return res.json({ run: null, jobs: [] });
      const lastRun = runs[0];
      // Get jobs for the last run
      const jobsRes = await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${lastRun.id}/jobs?filter=all`, { headers });
      const jobsData = await jobsRes.json() as any;
      // Get artifacts for the last run
      const artRes = await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${lastRun.id}/artifacts`, { headers });
      const artData = await artRes.json() as any;
      res.json({
        run: { id: lastRun.id, conclusion: lastRun.conclusion, created_at: lastRun.created_at, html_url: lastRun.html_url },
        jobs: (jobsData.jobs ?? []).map((j: any) => ({ id: j.id, name: j.name, conclusion: j.conclusion, status: j.status, started_at: j.started_at, completed_at: j.completed_at })),
        artifacts: (artData.artifacts ?? []).map((a: any) => ({ id: a.id, name: a.name, size_in_bytes: a.size_in_bytes, url: `https://github.com/${REPO}/actions/runs/${lastRun.id}/artifacts/${a.id}` })),
      });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // Trigger a workflow dispatch (Live Dashboard) — uses numeric ID for reliability
  app.post("/api/github/trigger-workflow", async (req, res) => {
    try {
      const { getToken } = await import("./github-sync");
      const token = getToken();
      const REPO = "DreamCo-Technologies/Dreamcobots";
      const DASHBOARD_WF_ID = 284581909;
      const { workflow } = req.body;
      // Use numeric workflow ID for dreamco-live-dashboard, filename for others
      const wfRef = (!workflow || workflow === "dreamco-live-dashboard.yml") ? String(DASHBOARD_WF_ID) : workflow;
      const r = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${wfRef}/dispatches`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "DreamCo-Empire-OS" },
        body: JSON.stringify({ ref: "main", inputs: { era: "all", mode: "all", deep_buddy: "true" } }),
      });
      if (r.status === 204) {
        res.json({ success: true, message: "Workflow triggered — check GitHub Actions in ~2 minutes" });
      } else {
        const body = await r.json() as any;
        res.status(r.status).json({ success: false, error: body.message ?? "Unknown error" });
      }
    } catch (e: any) {
      res.status(500).json({ success: false, error: e.message });
    }
  });

  // ===== MODULE STATUS — 24-module command center status =====
  app.get("/api/modules/status", async (_req, res) => {
    const MODULES = [
      { id: "fleet", name: "Bot Fleet", path: "/bots", jobKeyword: "Fleet Scan", icon: "Bot", color: "blue" },
      { id: "buddy", name: "Buddy Bot", path: "/bots/buddy-bot", jobKeyword: "Buddy Bot", icon: "BrainCircuit", color: "violet" },
      { id: "divisions", name: "Divisions", path: "/divisions", jobKeyword: "Fleet Scan", icon: "Building2", color: "indigo" },
      { id: "deals", name: "Deal Analyzer", path: "/deals", jobKeyword: "deal-analyzer", icon: "Calculator", color: "emerald" },
      { id: "formulas", name: "Formula Vault", path: "/formulas", jobKeyword: "formula-vault", icon: "FlaskConical", color: "amber" },
      { id: "learning", name: "Learning Matrix", path: "/learning-matrix", jobKeyword: "learning-matrix", icon: "Brain", color: "cyan" },
      { id: "ai-leaders", name: "AI Leaders", path: "/ai-leaders", jobKeyword: "ai-leaders", icon: "Trophy", color: "yellow" },
      { id: "ai-models", name: "AI Models Hub", path: "/ai-models", jobKeyword: "ai-models", icon: "Cpu", color: "pink" },
      { id: "ecosystem", name: "AI Ecosystem", path: "/ecosystem", jobKeyword: "Global AI", icon: "Globe", color: "teal" },
      { id: "orchestration", name: "Orchestration", path: "/orchestration", jobKeyword: "orchestration", icon: "Network", color: "purple" },
      { id: "marketplace", name: "Marketplace", path: "/marketplace", jobKeyword: "marketplace", icon: "Store", color: "orange" },
      { id: "crypto", name: "Crypto", path: "/crypto", jobKeyword: "crypto", icon: "Wallet", color: "green" },
      { id: "payments", name: "Payments", path: "/payments", jobKeyword: "payments", icon: "CreditCard", color: "blue" },
      { id: "business", name: "Biz Launch", path: "/business", jobKeyword: "biz-launch", icon: "Rocket", color: "rose" },
      { id: "code-lab", name: "Code Lab", path: "/code-lab", jobKeyword: "code-lab", icon: "Code", color: "cyan" },
      { id: "loans", name: "Loans & Deals", path: "/loans", jobKeyword: "loans", icon: "Landmark", color: "lime" },
      { id: "debug", name: "Debug Intel", path: "/debug", jobKeyword: "debug-intel", icon: "Bug", color: "red" },
      { id: "revenue", name: "Revenue", path: "/revenue", jobKeyword: "revenue", icon: "TrendingUp", color: "green" },
      { id: "pricing", name: "Pricing", path: "/pricing", jobKeyword: "pricing", icon: "Tag", color: "violet" },
      { id: "connections", name: "Connections", path: "/connections", jobKeyword: "connections", icon: "Plug", color: "sky" },
      { id: "time-capsule", name: "Time Capsule", path: "/time-capsule", jobKeyword: "time-capsule", icon: "Clock", color: "slate" },
      { id: "costs", name: "Cost Tracking", path: "/costs", jobKeyword: "cost-tracking", icon: "DollarSign", color: "amber" },
      { id: "autonomy", name: "Autonomy", path: "/autonomy", jobKeyword: "autonomy", icon: "Zap", color: "yellow" },
      { id: "era-testing", name: "Era Testing", path: "/bot-activity", jobKeyword: "Era Testing", icon: "Activity", color: "indigo" },
    ];
    try {
      const { getToken } = await import("./github-sync");
      const token = getToken();
      const REPO = "DreamCo-Technologies/Dreamcobots";
      const DASHBOARD_WF_ID = 284581909;
      const headers = { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "DreamCo-Empire-OS" };
      const runsRes = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/${DASHBOARD_WF_ID}/runs?per_page=3&status=completed`, { headers });
      const runsData = await runsRes.json() as any;
      const lastRun = (runsData.workflow_runs ?? [])[0];
      let jobs: any[] = [];
      if (lastRun) {
        const jobsRes = await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${lastRun.id}/jobs?filter=all`, { headers });
        const jobsData = await jobsRes.json() as any;
        jobs = jobsData.jobs ?? [];
      }
      const modules = MODULES.map(m => {
        const matchedJob = jobs.find((j: any) => j.name.toLowerCase().includes(m.jobKeyword.toLowerCase()));
        return {
          ...m,
          status: matchedJob ? (matchedJob.conclusion ?? matchedJob.status) : "unknown",
          jobName: matchedJob?.name ?? null,
          lastRunAt: lastRun?.created_at ?? null,
          runUrl: lastRun?.html_url ?? null,
        };
      });
      const passCount = modules.filter(m => m.status === "success").length;
      res.json({ modules, lastRunId: lastRun?.id, lastRunAt: lastRun?.created_at, lastRunUrl: lastRun?.html_url, overallHealth: Math.round((passCount / modules.length) * 100) });
    } catch (_e) {
      res.json({ modules: MODULES.map(m => ({ ...m, status: "unknown", jobName: null, lastRunAt: null, runUrl: null })), overallHealth: 0, offline: true });
    }
  });

  // ===== BOT BUILDER =====
  app.post("/api/bot-builder/generate", async (req, res) => {
    const { libraries = [], name, division = "DreamCodeLab", description = "" } = req.body;
    if (!name) return res.status(400).json({ error: "name is required" });
    try {
      const prompt = `You are a DreamCo Empire OS bot architect. Generate a complete bot profile as JSON for a bot named "${name}" that specializes in: ${libraries.join(", ")}. Division: ${division}. Additional context: ${description}

Return ONLY valid JSON with this exact shape:
{
  "slug": "kebab-case-unique-slug",
  "displayName": "${name}",
  "division": "${division}",
  "category": "coding-library",
  "tier": "pro",
  "description": "2-3 sentence specialist description",
  "capabilities": ["10 specific capabilities as strings"],
  "systemPrompt": "Detailed system prompt paragraph for this specialist bot",
  "revenueModel": "SaaS subscription",
  "targetUsers": "target user description",
  "priceRange": "$99/mo"
}`;
      const completion = await openai.chat.completions.create({ model: "gpt-4.1-mini", messages: [{ role: "user", content: prompt }], response_format: { type: "json_object" }, max_completion_tokens: 1500 });
      const botData = JSON.parse(completion.choices[0].message.content ?? "{}");
      botData.status = "active";
      botData.traits = { division, category: "coding-library", tier: "pro", version: "1.0", engine: "GPT-4.1", autonomy: "full", libraries: libraries.join(",") };
      res.json({ success: true, bot: botData });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  app.post("/api/bot-builder/save", async (req, res) => {
    const { bot } = req.body;
    if (!bot?.slug) return res.status(400).json({ error: "bot with slug required" });
    try {
      const existing = await storage.getBotProfileBySlug(bot.slug);
      if (existing) {
        const updated = await storage.updateBotProfile(existing.id, bot);
        return res.json({ success: true, bot: updated, action: "updated" });
      }
      const created = await storage.createBotProfile(bot);
      res.json({ success: true, bot: created, action: "created" });
    } catch (e: any) {
      res.status(500).json({ error: e.message });
    }
  });

  // ===== TASK RESTART ENDPOINTS =====
  app.post("/api/tasks/restart-all", async (_req, res) => {
    try {
      const tasks = await storage.listTasks();
      let restarted = 0;
      for (const task of tasks) {
        await storage.updateTask(task.id, { status: "pending" });
        restarted++;
      }
      res.json({ success: true, restarted });
    } catch (e: any) {
      res.status(500).json({ success: false, error: e.message });
    }
  });

  app.post("/api/tasks/:id/restart", async (req, res) => {
    try {
      const id = Number(req.params.id);
      const updated = await storage.updateTask(id, { status: "pending" });
      if (!updated) return res.status(404).json({ error: "Task not found" });
      res.json({ success: true, task: updated });
    } catch (e: any) {
      res.status(500).json({ success: false, error: e.message });
    }
  });

  // ===== GITHUB PULLS =====
  app.get("/api/github/pulls", async (_req, res) => {
    try {
      const { getPullRequests, getRepoInfo } = await import("./github-sync");
      const [prs, repo] = await Promise.all([getPullRequests(), getRepoInfo()]);
      res.json({
        connected: true,
        repo: { name: repo.full_name, url: repo.html_url, defaultBranch: repo.default_branch, stars: repo.stargazers_count },
        pullRequests: prs.map((pr: any) => ({
          id: pr.number, title: pr.title, state: pr.state,
          url: pr.html_url, createdAt: pr.created_at, author: pr.user?.login,
          body: pr.body?.slice(0, 200), draft: pr.draft,
        })),
      });
    } catch (e: any) {
      // Fallback: unauthenticated for public repo
      try {
        const r = await fetch("https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/pulls?state=all&per_page=20", {
          headers: { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
        });
        if (r.ok) {
          const prs = await r.json() as any[];
          res.json({ connected: true, tokenValid: false, pullRequests: prs.map((pr: any) => ({ id: pr.number, title: pr.title, state: pr.state, url: pr.html_url, createdAt: pr.created_at, author: pr.user?.login })) });
          return;
        }
      } catch {}
      res.json({ connected: false, pullRequests: [], error: e.message });
    }
  });

  // ===== GITHUB REPO TREE =====
  app.get("/api/github/repo-tree", async (_req, res) => {
    try {
      const { getToken } = await import("./github-sync");
      const token = getToken();
      const REPO = "DreamCo-Technologies/Dreamcobots";
      const r = await fetch(`https://api.github.com/repos/${REPO}/git/trees/main?recursive=1`, {
        headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
      });
      if (!r.ok) throw new Error(`GitHub ${r.status}`);
      const data = await r.json() as any;
      const tree = (data.tree ?? [])
        .filter((f: any) => f.type === "blob" && !f.path.startsWith(".git"))
        .slice(0, 300)
        .map((f: any) => ({ path: f.path, type: f.type, size: f.size, html_url: `https://github.com/${REPO}/blob/main/${f.path}` }));
      res.json({ tree, truncated: data.truncated, total: data.tree?.length ?? 0 });
    } catch (e: any) {
      // Unauthenticated fallback — list top-level contents
      try {
        const r = await fetch("https://api.github.com/repos/DreamCo-Technologies/Dreamcobots/contents/", {
          headers: { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
        });
        if (r.ok) {
          const contents = await r.json() as any[];
          res.json({ tree: contents.map((f: any) => ({ path: f.name, type: f.type === "dir" ? "tree" : "blob", size: f.size, html_url: f.html_url })), truncated: false, total: contents.length });
          return;
        }
      } catch {}
      res.json({ tree: [], error: e.message });
    }
  });

  // ===== BOT ACTIVITY =====
  app.get("/api/bot-activity", async (_req, res) => {
    const bots = await storage.listBotProfiles();
    const convs = await storage.listConversations();
    const botItems = await Promise.all(bots.slice(0, 100).map(async (bot) => {
      const memories = await storage.listBotMemory(bot.id).catch(() => []);
      const lastActive = memories[0]?.createdAt ?? null;
      return {
        id: bot.id,
        slug: bot.slug,
        displayName: bot.displayName,
        division: bot.division,
        tier: bot.tier,
        status: bot.status,
        memoryCount: memories.length,
        lastLearning: memories[0]?.value ?? null,
        lastActive: lastActive instanceof Date ? lastActive.toISOString() : lastActive,
      };
    }));
    const response: BotActivityResponse = {
      totalBots: bots.length,
      totalConversations: convs.length,
      bots: botItems,
    };
    res.json(response);
  });

  // ===== BOT RECOMMENDATIONS =====
  app.get("/api/bots/recommend", async (req, res) => {
    const context = (req.query.context as string)?.toLowerCase() || "";
    const bots = await storage.listBotProfiles();
    const keywords: Record<string, string[]> = {
      finance: ["finance", "money", "invest", "loan", "bank", "payment", "crypto", "trade"],
      sales: ["sales", "lead", "crm", "email", "marketing", "outreach", "pipeline"],
      "real-estate": ["real estate", "property", "house", "flip", "renovation", "mortgage"],
      gaming: ["game", "gaming", "play", "simulator", "build game"],
      coding: ["code", "develop", "build", "software", "website", "app", "program"],
      travel: ["travel", "trip", "flight", "hotel", "vacation", "booking"],
      production: ["produce", "production", "media", "video", "content", "film"],
      trade: ["trade", "import", "export", "supply chain", "logistics"],
      security: ["security", "protect", "hack", "cyber", "compliance"],
      data: ["data", "analytics", "report", "insight", "research"],
    };
    let bestCategory = "general";
    let bestScore = 0;
    for (const [cat, words] of Object.entries(keywords)) {
      const score = words.filter(w => context.includes(w)).length;
      if (score > bestScore) { bestCategory = cat; bestScore = score; }
    }
    const recommended = bots
      .filter(b => bestScore > 0 ? b.category === bestCategory || b.division.toLowerCase().includes(bestCategory) : true)
      .slice(0, 5)
      .map(b => ({ id: b.id, slug: b.slug, displayName: b.displayName, division: b.division, category: b.category, description: b.description, tier: b.tier }));
    res.json({ context, matchedCategory: bestCategory, recommendations: recommended });
  });

  // Register voice chat routes (distinct path: /api/conversations/:id/voice)
  registerAudioRoutes(app);

  return httpServer;
}
