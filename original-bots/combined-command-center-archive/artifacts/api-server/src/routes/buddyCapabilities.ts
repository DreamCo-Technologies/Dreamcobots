import { Router, type IRouter } from "express";
import { z } from "zod";
import { requireAuth } from "../middlewares/authMiddleware";

const router: IRouter = Router();

interface Capability {
  id: string;
  name: string;
  category: "language" | "vision" | "voice" | "video" | "comms" | "code" | "data";
  status: "live" | "needs_key" | "planned";
  description: string;
  requiredEnv?: string[];
  endpoint?: string;
  notes?: string;
}

const CAPABILITIES: Capability[] = [
  // LIVE
  { id: "chat", name: "Multi-turn chat / reasoning", category: "language", status: "live", description: "Conversational reasoning via GPT-5 family (OpenAI proxy).", endpoint: "POST /api/buddy/chat" },
  { id: "code_gen", name: "Code generation (all languages)", category: "code", status: "live", description: "Generates code in 40+ languages incl. Python, Rust, Go, Solidity, Move, Cairo, Q#, Erlang, OCaml.", endpoint: "POST /api/vibe/build" },
  { id: "games", name: "Playable browser games", category: "code", status: "live", description: "Single-file HTML5 mini-games with scoring and win/lose.", endpoint: "POST /api/vibe/build (mode=game)" },
  { id: "simulations", name: "Interactive scientific simulations", category: "code", status: "live", description: "Physics, biology, math sims with parameter sliders.", endpoint: "POST /api/vibe/build (mode=simulation)" },
  { id: "lessons", name: "Kid-friendly lesson games (parent input)", category: "code", status: "live", description: "Parent prompt → colorful learning mini-game for ages 6-12.", endpoint: "POST /api/vibe/build (mode=lesson)" },
  { id: "libraries", name: "Reusable code libraries", category: "code", status: "live", description: "Generates documented, exportable library packages for other vibe coders.", endpoint: "POST /api/vibe/build (mode=library)" },
  { id: "lib_mastery", name: "Library mastery (global)", category: "code", status: "live", description: "Studies + stores understanding of 250+ libs across 40+ languages incl. Chinese (PaddlePaddle, MindSpore), Japanese (Chainer, GiNZA), Russian (CatBoost, DeepPavlov), Korean (KoNLPy), Indian (IndicNLP).", endpoint: "POST /api/vibe/train-all" },
  { id: "image_gen", name: "Image generation", category: "vision", status: "live", description: "Generates images via OpenAI gpt-image-1 (same key as chat).", endpoint: "POST /api/buddy/image" },
  { id: "github_ops", name: "GitHub repo + actions intelligence", category: "code", status: "live", description: "Live read of repos, commits, workflow runs across DreamCo-Technologies org.", endpoint: "GET /api/github/*" },
  { id: "stripe", name: "Stripe revenue + webhooks", category: "comms", status: "live", description: "Charge attribution by bot, webhook handler for charge.succeeded / subscription.created.", endpoint: "POST /api/stripe/webhook" },
  { id: "bot_orchestration", name: "Bot orchestration (171 bots)", category: "code", status: "live", description: "Run, heartbeat, capability mapping for the entire Dreamcobots fleet.", endpoint: "POST /api/bots/:name/run" },

  // NEEDS USER-PROVIDED API KEY
  { id: "voice_clone", name: "Voice cloning / mimicking", category: "voice", status: "needs_key", description: "Clone any voice for narration, calls, or reels. Requires ElevenLabs API key (~$5+/mo).", requiredEnv: ["ELEVENLABS_API_KEY"], notes: "Consent + legal compliance is on you. Public-figure cloning may violate ToS." },
  { id: "tts", name: "Text-to-speech (premium voices)", category: "voice", status: "needs_key", description: "High-quality TTS in 30+ languages.", requiredEnv: ["ELEVENLABS_API_KEY"] },
  { id: "stt", name: "Speech-to-text / transcription", category: "voice", status: "needs_key", description: "Whisper-quality transcription. Can use OpenAI key, just needs endpoint wiring.", requiredEnv: [] },
  { id: "video_gen", name: "AI video / reels / music video clips", category: "video", status: "needs_key", description: "Generate short video clips. Requires Runway, Sora API, or Replicate (~$15+/mo).", requiredEnv: ["RUNWAY_API_KEY", "REPLICATE_API_TOKEN"], notes: "Pick one provider." },
  { id: "music_gen", name: "AI music generation", category: "video", status: "needs_key", description: "Generate original music tracks via Suno or Replicate music models.", requiredEnv: ["SUNO_API_KEY", "REPLICATE_API_TOKEN"] },
  { id: "phone_calls", name: "Real phone calls (AI voice)", category: "comms", status: "needs_key", description: "Outbound calls with Buddy's voice. Twilio for telephony + ElevenLabs for voice.", requiredEnv: ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "ELEVENLABS_API_KEY"] },
  { id: "sms", name: "SMS / WhatsApp messaging", category: "comms", status: "needs_key", description: "Outbound SMS and WhatsApp via Twilio.", requiredEnv: ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"] },
  { id: "email_send", name: "Transactional email send", category: "comms", status: "needs_key", description: "Send email via SendGrid, Resend, or Postmark.", requiredEnv: ["RESEND_API_KEY"] },

  // PLANNED (no external dep — just engineering work)
  { id: "vision", name: "Image understanding (vision-in)", category: "vision", status: "planned", description: "Upload image → Buddy describes/analyzes. Needs gpt-4o-vision wiring, ~2hr work." },
  { id: "long_memory", name: "Persistent long-term memory", category: "language", status: "planned", description: "Vector DB (pgvector) for cross-session memory. Schema exists in postgres, needs embedding pipeline." },
  { id: "rag", name: "RAG over your docs / repo", category: "data", status: "planned", description: "Index repo files + uploads, search semantically before answering." },
  { id: "browser", name: "Browser automation / web scraping", category: "data", status: "planned", description: "Headless Chrome agent for live web tasks. Playwright is already a workspace dep." },
];

router.get("/buddy/capabilities", (_req, res) => {
  const live = CAPABILITIES.filter(c => c.status === "live").length;
  const needsKey = CAPABILITIES.filter(c => c.status === "needs_key").length;
  const planned = CAPABILITIES.filter(c => c.status === "planned").length;
  res.json({
    totals: { total: CAPABILITIES.length, live, needsKey, planned },
    capabilities: CAPABILITIES,
  });
});

// Image generation endpoint
const ImageBody = z.object({
  prompt: z.string().min(1).max(2000),
  size: z.enum(["1024x1024","1024x1536","1536x1024","auto"]).optional().default("1024x1024"),
});

router.post("/buddy/image", requireAuth, async (req, res): Promise<void> => {
  const parsed = ImageBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid body", issues: parsed.error.issues });
    return;
  }
  const baseUrl = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL;
  const apiKey = process.env.AI_INTEGRATIONS_OPENAI_API_KEY;
  if (!baseUrl || !apiKey) {
    res.status(503).json({ error: "OpenAI integration not configured" });
    return;
  }
  try {
    const r = await fetch(`${baseUrl}/images/generations`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({
        model: "gpt-image-1",
        prompt: parsed.data.prompt,
        size: parsed.data.size,
        n: 1,
      }),
    });
    if (!r.ok) {
      const t = await r.text();
      req.log.error({ status: r.status, body: t.slice(0, 500) }, "image gen failed");
      res.status(502).json({ error: "image generation failed", detail: t.slice(0, 300) });
      return;
    }
    const data = await r.json() as { data?: Array<{ b64_json?: string; url?: string }> };
    const first = data.data?.[0];
    if (!first) { res.status(500).json({ error: "no image returned" }); return; }
    res.json({
      prompt: parsed.data.prompt,
      size: parsed.data.size,
      url: first.url ?? (first.b64_json ? `data:image/png;base64,${first.b64_json}` : null),
    });
  } catch (err) {
    req.log.error({ err }, "image gen exception");
    res.status(500).json({ error: err instanceof Error ? err.message : "unknown" });
  }
});

export default router;
