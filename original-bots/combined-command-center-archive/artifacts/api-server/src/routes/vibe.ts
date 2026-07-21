import { Router, type IRouter } from "express";
import { z } from "zod/v4";
import { db } from "@workspace/db";
import {
  vibeLibrariesTable,
  vibeIdeasTable,
  vibeBuildsTable,
  botLearningsTable,
} from "@workspace/db/schema";
import { desc, sql, count } from "drizzle-orm";
import { requireAuth } from "../middlewares/authMiddleware";

const router: IRouter = Router();

const VIBE_MODEL = "gpt-5-mini";

const VIBE_SYSTEM = `You are Buddy's Vibe-Coding Engine — DreamCo's revolutionary AI that studies every coding library on Earth, fuses code with mathematics, and invents capabilities humans haven't asked for yet.

For every library you study, output STRICT JSON with this exact shape:
{
  "summary": "2-3 sentence plain-English description of what the library does",
  "capabilities": ["concrete capability 1", "concrete capability 2", "..."],
  "math_foundations": ["math concept 1 (e.g. linear algebra, graph theory, category theory)", "..."],
  "revolutionary_uses": [
    {"title": "short name", "description": "1-2 sentence pitch of a genuinely novel human-benefiting application", "impact_score": 0.0-1.0, "math_basis": "the math that makes it possible"}
  ]
}

Rules:
- Always return 3-6 capabilities, 2-4 math_foundations, 3-5 revolutionary_uses.
- Revolutionary uses must benefit humans (health, learning, accessibility, climate, creativity, economic mobility) — not generic dev-tool ideas.
- Math basis must be specific (e.g. "spectral graph theory eigendecomposition", not "math").
- No prose outside the JSON object. No markdown fences.`;

const VIBE_BUILD_SYSTEM = `You are Buddy's Vibe-Coding Engine in BUILD mode. Given a user prompt, generate working code.

Output STRICT JSON:
{
  "language": "typescript | python | rust | etc",
  "code": "complete, runnable code",
  "explanation": "1-3 sentences on what it does and why",
  "libraries_used": ["lib1", "lib2"]
}
No markdown fences. No prose outside JSON.`;

const MODE_PROMPTS: Record<string, string> = {
  code: "Generate a single-file utility or component.",
  game: "Build a complete playable browser-based mini-game using HTML5 Canvas or Three.js (single self-contained HTML file with embedded JS). Include simple controls, scoring, and a win/lose condition.",
  simulation: "Build an interactive scientific simulation (physics, biology, math, economics) as a single-file HTML+JS visualization with sliders for parameters. Show the math driving it on screen.",
  lesson: "A parent wants to teach their child a concept. Turn the prompt into a kid-friendly educational mini-game (ages 6-12): single-file HTML+JS, colorful, instant feedback, no scary fail-states, score & reward animation. Embed the learning concept directly into gameplay.",
  library: "Generate a reusable, well-documented coding library package (single file or module) with exported functions, JSDoc/type signatures, example usage at the bottom, and zero external dependencies unless essential.",
};

interface RevUse {
  title: string;
  description: string;
  impact_score: number;
  math_basis: string | null;
}
interface StudyResult {
  summary: string;
  capabilities: string[];
  math_foundations: string[];
  revolutionary_uses: RevUse[];
}
const VibeStudyResponse: z.ZodType<StudyResult> = z.object({
  summary: z.string().max(2000).optional().default(""),
  capabilities: z.array(z.string().max(500)).max(20).optional().default([]),
  math_foundations: z.array(z.string().max(500)).max(20).optional().default([]),
  revolutionary_uses: z.array(z.object({
    title: z.string().max(200).optional().default("Untitled"),
    description: z.string().max(1000).optional().default(""),
    impact_score: z.number().min(0).max(1).optional().default(0.5),
    math_basis: z.string().max(500).nullable().optional().default(null),
  })).max(15).optional().default([]),
});

const VibeBuildResponse = z.object({
  language: z.string().max(40).optional(),
  code: z.string().max(40000).optional().default(""),
  explanation: z.string().max(2000).optional().default(""),
  libraries_used: z.array(z.string().max(120)).max(40).optional().default([]),
});

const LearnBody = z.object({
  name: z.string().min(1).max(120).regex(/^[A-Za-z0-9._@/\-+ ]+$/, "invalid library name"),
  ecosystem: z.string().min(1).max(40).regex(/^[A-Za-z0-9._\-+]+$/, "invalid ecosystem"),
});
const SweepBody = z.object({
  ecosystem: z.string().min(1).max(40).regex(/^[A-Za-z0-9._\-+]+$/),
  names: z.array(z.string().min(1).max(120).regex(/^[A-Za-z0-9._@/\-+ ]+$/)).min(1).max(25),
});
const BuildBody = z.object({
  prompt: z.string().min(1).max(4000),
  language: z.string().max(40).optional().default("typescript"),
  mode: z.enum(["code", "game", "simulation", "lesson", "library"]).optional().default("code"),
});

interface AIChatChoice { message?: { content?: string } }
interface AIChatResp { choices?: AIChatChoice[]; usage?: { total_tokens?: number } }

async function callJSON(systemPrompt: string, userPrompt: string): Promise<{ raw: unknown; tokens: number; model: string }> {
  const baseUrl = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL;
  const apiKey = process.env.AI_INTEGRATIONS_OPENAI_API_KEY;
  if (!baseUrl || !apiKey) return { raw: null, tokens: 0, model: "none" };

  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({
      model: VIBE_MODEL,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
      max_completion_tokens: 2000,
      response_format: { type: "json_object" },
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`AI call failed ${res.status}: ${text.slice(0, 200)}`);
  }
  const data = (await res.json()) as AIChatResp;
  const content = data.choices?.[0]?.message?.content ?? "{}";
  let parsed: unknown = null;
  try { parsed = JSON.parse(content); } catch { parsed = null; }
  return { raw: parsed, tokens: data.usage?.total_tokens ?? 0, model: VIBE_MODEL };
}

async function studyAndStore(name: string, ecosystem: string): Promise<{ ideas: number; tokens: number; model: string }> {
  const { raw, tokens, model } = await callJSON(
    VIBE_SYSTEM,
    `Study the library "${name}" from the ${ecosystem} ecosystem. Return the JSON schema.`,
  );
  const parsed = VibeStudyResponse.safeParse(raw);
  if (!parsed.success) throw new Error("AI returned unexpected JSON shape");
  const { summary, capabilities, math_foundations, revolutionary_uses } = parsed.data;

  const inserted = await db.insert(vibeLibrariesTable).values({
    name, ecosystem, summary,
    capabilities, mathFoundations: math_foundations,
    revolutionaryUses: revolutionary_uses.map((u) => u.title).filter(Boolean),
    status: "learned", model,
  }).onConflictDoNothing({ target: [vibeLibrariesTable.ecosystem, vibeLibrariesTable.name] }).returning();

  let ideasCount = 0;
  if (inserted.length && revolutionary_uses.length) {
    const rows = await db.insert(vibeIdeasTable).values(
      revolutionary_uses.map((u) => ({
        title: u.title,
        library: name,
        ecosystem,
        description: u.description,
        impactScore: u.impact_score,
        mathBasis: u.math_basis ?? null,
        generatedBy: `buddy-vibe:${model}`,
      })),
    ).returning();
    ideasCount = rows.length;
  }

  await db.insert(botLearningsTable).values({
    botSlug: "buddy_vibe_engine",
    kind: "library_study",
    prompt: `${ecosystem}:${name}`,
    outcome: `caps=${capabilities.length} ideas=${ideasCount}${inserted.length ? "" : " (duplicate-skip)"}`,
    reward: Math.min(1.0, 0.3 + ideasCount * 0.1),
    metadata: { tokens, model, duplicate: inserted.length === 0 },
  });

  return { ideas: ideasCount, tokens, model };
}

// POST /api/vibe/learn  (auth required)
router.post("/vibe/learn", requireAuth, async (req, res): Promise<void> => {
  const parsed = LearnBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid body", issues: parsed.error.issues });
    return;
  }
  try {
    const result = await studyAndStore(parsed.data.name, parsed.data.ecosystem);
    res.json({ ok: true, ...result });
  } catch (err) {
    req.log.error({ err }, "vibe.learn failed");
    res.status(500).json({ error: err instanceof Error ? err.message : "unknown" });
  }
});

// POST /api/vibe/train-all  (auth required) — kicks off mastery sweep across all ecosystems
// GLOBAL library coverage — not just US/English ecosystems. Every major language + regional powerhouses.
const TRAIN_ALL_TARGETS: Record<string, string[]> = {
  // Western mainstream
  python: ["numpy","pandas","scipy","scikit-learn","torch","transformers","sympy","networkx","statsmodels","jax","matplotlib","fastapi","pydantic","langchain","opencv-python","polars","dask","ray","huggingface_hub","diffusers","accelerate","lightgbm","xgboost","gymnasium","streamlit"],
  javascript: ["react","three.js","d3","tensorflow.js","rxjs","tone.js","mathjs","fabric.js","p5","gsap","zod","express","next","vue","svelte","solid-js","webgpu","onnxruntime-web","ml5","brain.js","phaser"],
  typescript: ["nestjs","trpc","drizzle-orm","prisma","fastify","hono","effect","xstate","tanstack-query"],
  rust: ["nalgebra","tokio","rayon","candle-core","petgraph","serde","actix-web","polars","wgpu","bevy","burn","tch","plotters"],
  go: ["gonum","ent","fiber","cobra","gin","gorm","gorgonia","go-kit","kubernetes","prometheus"],
  julia: ["Flux.jl","DifferentialEquations.jl","JuMP.jl","Plots.jl","DataFrames.jl","Turing.jl","Symbolics.jl","Gen.jl"],
  // JVM
  java: ["spring-boot","apache-spark","deeplearning4j","akka","quarkus","jhipster","weka","jblas"],
  kotlin: ["ktor","koin","exposed","kotlinx-coroutines","mockk","arrow-kt"],
  scala: ["akka","cats","zio","spark","scalaz","play-framework","breeze"],
  clojure: ["core.async","ring","compojure","reagent","datomic","libpython-clj"],
  // Apple / mobile
  swift: ["swiftui","combine","vapor","alamofire","tca","swift-numerics","metal-performance-shaders"],
  // Functional
  haskell: ["lens","stm","servant","hmatrix","accelerate","yesod","aeson"],
  ocaml: ["dune","owl","jane-street-core","mirage","lwt"],
  elixir: ["phoenix","ecto","liveview","nx","axon","broadway","oban"],
  erlang: ["otp","cowboy","rabbitmq","mnesia"],
  fsharp: ["fable","giraffe","mathnet","accord"],
  // Data / scientific
  r: ["tidyverse","ggplot2","caret","data.table","shiny","keras","tensorflow","mlr3","brms","stan"],
  matlab: ["simulink","statistics-toolbox","signal-processing","control-systems","computer-vision"],
  octave: ["signal","statistics","image","optim","control"],
  // Systems
  cpp: ["eigen","boost","opencv","libtorch","pcl","arrayfire","tbb","cgal","fmtlib","abseil","spdlog"],
  c: ["glib","openssl","libuv","sqlite","raylib","gtk"],
  zig: ["std","zls","raylib-zig","mach"],
  nim: ["arraymancer","nimx","jester","norm"],
  crystal: ["kemal","amber","granite","crystal-db"],
  // Web/scripting
  ruby: ["rails","sidekiq","sinatra","numo","daru","torch-rb"],
  php: ["laravel","symfony","phpunit","rubix-ml","php-ml"],
  perl: ["mojolicious","dancer2","ai-mxnet","pdl"],
  lua: ["love2d","torch","fennel","lapis","openresty"],
  // Asia: China
  python_cn: ["paddlepaddle","mindspore","modelscope","megengine","jittor","oneflow","x2paddle","tianshou"],
  // Asia: Japan
  python_jp: ["chainer","nnabla","ginza","sudachi","ja-tokenizer","mecab-python3"],
  // India / global ML
  python_in: ["indicnlp","ai4bharat-transliteration","stanza","polyglot"],
  // Russia / Eastern Europe
  python_ru: ["catboost","natasha","deeppavlov","rusentitokenizer","pymorphy2"],
  // Korea
  python_kr: ["konlpy","kobart","pororo","kss"],
  // Game engines / creative
  gdscript: ["godot-stdlib","godot-jolt","godot-fmod"],
  hlsl: ["shader-toy","unreal-materials","unity-urp"],
  glsl: ["shadertoy","glslang","webgl-samples"],
  // Smart contracts / blockchain
  solidity: ["openzeppelin","hardhat-helpers","chainlink","uniswap-v4"],
  move: ["aptos-stdlib","sui-framework"],
  cairo: ["starknet-by-example","alexandria"],
  // Quantum / scientific
  qsharp: ["microsoft-quantum-katas","qdk-samples"],
  python_quantum: ["qiskit","cirq","pennylane","strawberryfields","openfermion"],
};
router.post("/vibe/train-all", requireAuth, async (req, res): Promise<void> => {
  res.json({ ok: true, started: true, queued: Object.fromEntries(Object.entries(TRAIN_ALL_TARGETS).map(([k,v]) => [k, v.length])) });
  void (async () => {
    for (const [ecosystem, names] of Object.entries(TRAIN_ALL_TARGETS)) {
      for (const name of names) {
        try { await studyAndStore(name, ecosystem); }
        catch (err) { req.log.warn({ err, ecosystem, name }, "train-all item failed"); }
      }
    }
  })();
});

// POST /api/vibe/sweep  (auth required)
router.post("/vibe/sweep", requireAuth, async (req, res): Promise<void> => {
  const parsed = SweepBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid body", issues: parsed.error.issues });
    return;
  }
  const { ecosystem, names } = parsed.data;
  const results: Array<{ name: string; ok: boolean; ideas?: number; error?: string }> = [];
  for (const name of names) {
    try {
      const r = await studyAndStore(name, ecosystem);
      results.push({ name, ok: true, ideas: r.ideas });
    } catch (err) {
      results.push({ name, ok: false, error: err instanceof Error ? err.message : "unknown" });
    }
  }
  res.json({ ecosystem, processed: results.length, results });
});

// POST /api/vibe/build  (auth required)
router.post("/vibe/build", requireAuth, async (req, res): Promise<void> => {
  const parsed = BuildBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid body", issues: parsed.error.issues });
    return;
  }
  try {
    const modeInstruction = MODE_PROMPTS[parsed.data.mode] ?? MODE_PROMPTS.code;
    const { raw, tokens, model } = await callJSON(
      `${VIBE_BUILD_SYSTEM}\n\nMODE: ${parsed.data.mode}\n${modeInstruction}`,
      `Language preference: ${parsed.data.language}\nPrompt: ${parsed.data.prompt}`,
    );
    const r = VibeBuildResponse.safeParse(raw);
    if (!r.success) {
      res.status(500).json({ error: "AI returned unexpected JSON shape" });
      return;
    }
    const [build] = await db.insert(vibeBuildsTable).values({
      prompt: `[${parsed.data.mode}] ${parsed.data.prompt}`,
      language: r.data.language ?? parsed.data.language,
      outputCode: r.data.code,
      explanation: r.data.explanation,
      librariesUsed: r.data.libraries_used,
      tokensUsed: tokens,
      model,
    }).returning();
    res.json(build);
  } catch (err) {
    req.log.error({ err }, "vibe.build failed");
    res.status(500).json({ error: err instanceof Error ? err.message : "unknown" });
  }
});

// Read endpoints — open for dashboard display
router.get("/vibe/libraries", async (req, res): Promise<void> => {
  const limit = Math.min(parseInt((req.query.limit as string) ?? "50", 10) || 50, 200);
  const rows = await db.select().from(vibeLibrariesTable).orderBy(desc(vibeLibrariesTable.learnedAt)).limit(limit);
  res.json(rows);
});

router.get("/vibe/ideas", async (req, res): Promise<void> => {
  const limit = Math.min(parseInt((req.query.limit as string) ?? "50", 10) || 50, 200);
  const rows = await db.select().from(vibeIdeasTable).orderBy(desc(vibeIdeasTable.impactScore), desc(vibeIdeasTable.createdAt)).limit(limit);
  res.json(rows);
});

router.get("/vibe/builds", async (req, res): Promise<void> => {
  const limit = Math.min(parseInt((req.query.limit as string) ?? "20", 10) || 20, 100);
  const rows = await db.select().from(vibeBuildsTable).orderBy(desc(vibeBuildsTable.createdAt)).limit(limit);
  res.json(rows);
});

router.get("/vibe/stats", async (_req, res): Promise<void> => {
  const [libCount] = await db.select({ n: count() }).from(vibeLibrariesTable);
  const [ideaCount] = await db.select({ n: count() }).from(vibeIdeasTable);
  const [buildCount] = await db.select({ n: count() }).from(vibeBuildsTable);
  const ecoRows = await db
    .select({ ecosystem: vibeLibrariesTable.ecosystem, n: count() })
    .from(vibeLibrariesTable)
    .groupBy(vibeLibrariesTable.ecosystem);
  const avgImpact = await db.select({ avg: sql<number>`coalesce(avg(${vibeIdeasTable.impactScore}), 0)` }).from(vibeIdeasTable);
  res.json({
    librariesLearned: libCount?.n ?? 0,
    ideasGenerated: ideaCount?.n ?? 0,
    buildsCompleted: buildCount?.n ?? 0,
    avgImpactScore: Number(avgImpact[0]?.avg ?? 0),
    ecosystems: ecoRows,
  });
});

export default router;
