# DreamCo Command Center — Honest Build-Out Roadmap

_Last updated: 2026-05-28. Maintained by Buddy + the user. Source of truth for "what's actually built vs what needs work."_

This roadmap exists because vague promises kill credibility with investors. Every item here is in one of four states: **LIVE**, **NEEDS_KEY**, **PLANNED**, or **OUT_OF_SCOPE**.

---

## PHASE 0 — Foundation (LIVE)

- [x] Postgres schema + Drizzle ORM (agents, divisions, capabilities, workflows, events, bot_runs, vibe_libraries, vibe_ideas, vibe_builds)
- [x] Express API server, requireAuth middleware, Zod input validation everywhere
- [x] React+Vite dashboard, Wouter routing, TanStack Query, shadcn/ui
- [x] OpenAI proxy wired via DreamCo AI Integrations (gpt-5-mini, gpt-image-1)
- [x] GitHub REST integration: repos, commits, activity, workflow runs
- [x] DreamCo Auth (OpenID Connect) — admin gate on all mutating endpoints
- [x] Stripe webhook handler (charge.succeeded, payment_intent.succeeded, customer.subscription.created)

## PHASE 1 — Intelligence layer (LIVE)

- [x] **Buddy chat** — system prompt with full fleet knowledge, emotion tagging
- [x] **Vibe Engine LEARN** — ingest any library by name, generate revolutionary uses + math basis
- [x] **Vibe Engine SWEEP** — batch ingest top N libraries per ecosystem
- [x] **Vibe Engine TRAIN_ALL** — global mastery sweep across **40+ languages, 250+ libraries** including non-Western ecosystems (PaddlePaddle, MindSpore, Chainer, GiNZA, KoNLPy, IndicNLP, CatBoost, DeepPavlov)
- [x] **Vibe Engine BUILD** — 5 modes: code, game, simulation, lesson (parent→kid), library
- [x] **In-dashboard preview** — sandboxed iframe runs generated games/sims/lessons instantly
- [x] **Image Studio** — text → image via OpenAI gpt-image-1
- [x] **GH Actions page** — live workflow run feed across all org repos
- [x] **Capabilities matrix** — `/capabilities` page lists every capability with honest status

## PHASE 2 — Capabilities requiring USER-PROVIDED API KEYS (NEEDS_KEY)

| Capability | Provider | Key needed | Est. cost |
|---|---|---|---|
| Voice cloning / mimicking | ElevenLabs | `ELEVENLABS_API_KEY` | $5–$22/mo |
| Premium TTS (30+ languages) | ElevenLabs | same | included above |
| Speech-to-text | OpenAI Whisper | already have | $0.006/min |
| AI video / reels / music-video clips | Runway OR Replicate | `RUNWAY_API_KEY` OR `REPLICATE_API_TOKEN` | $15+/mo |
| AI music generation | Suno OR Replicate | `SUNO_API_KEY` OR `REPLICATE_API_TOKEN` | $10+/mo |
| Real phone calls (AI voice) | Twilio + ElevenLabs | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `ELEVENLABS_API_KEY` | $1/mo phone + per-minute |
| SMS / WhatsApp | Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | per-message |
| Transactional email | Resend | `RESEND_API_KEY` | free tier 3k/mo |

**Engineering effort per item:** ~2–4 hours each once the key is in place. All endpoint scaffolds will live under `/api/buddy/voice`, `/api/buddy/video`, `/api/buddy/call`, etc.

## PHASE 3 — Engineering work, no external dep (PLANNED)

- [ ] **Vision-in** (image understanding) — gpt-4o multimodal. ~2hr.
- [ ] **Long-term memory** — pgvector embeddings table, retrieve top-K per session. ~4hr.
- [ ] **RAG over repo + docs** — index source files, embed, semantic search before answering. ~6hr.
- [ ] **Browser automation agent** — Playwright is already a workspace dep; wrap as `/api/buddy/browse`. ~6hr.
- [ ] **Bot scheduler** — cron-driven bot runs (currently manual). ~3hr.
- [ ] **Real-time bot status dashboard** — websocket stream of bot heartbeats. ~5hr.
- [ ] **Investor PDF generator** — one-click monthly metrics PDF from live data. ~4hr.

## PHASE 4 — Compliance / risk (REQUIRED BEFORE LAUNCH)

- [ ] Stripe webhook signature verification → currently uses STRIPE_WEBHOOK_SECRET, verify wired
- [ ] Rate limiting on all `/api/buddy/*` (cost-control)
- [ ] Per-tier usage tracking enforced in middleware (currently advisory)
- [ ] Voice/video consent & disclosure UI before generating likeness of real people
- [ ] Terms of Service + Privacy Policy pages
- [ ] GDPR data export / deletion endpoints

## OUT OF SCOPE (be honest with investors)

- ❌ **AGI / "Buddy can do anything"** — Buddy is a high-quality orchestrator over best-in-class models. It cannot do things current AI cannot do.
- ❌ **Real-time un-cloned voice impersonation of arbitrary people** — legal and technical limits.
- ❌ **Guaranteed revenue** — $500/day target is a goal, not a forecast.
- ❌ **Replacing all human work** — bots automate specific workflows, not general labor.

---

## How Buddy is connected to all bots

Every bot in the Dreamcobots fleet (171 total) is registered in `agents` and exposed through:
- `GET  /api/bots` — list all with status, tier, capabilities
- `POST /api/bots/:name/run` — manual trigger (records heartbeat, increments invocations)
- `GET  /api/bots/:name` — individual bot status
- `GET  /api/bots/:name/capabilities` — what this bot can do

Buddy's system prompt includes the full fleet roster + capability taxonomy, so it can answer "which bot handles X?" and "run bot Y" by name.

## How to add a NEW capability

1. Add a row to `CAPABILITIES` in `artifacts/api-server/src/routes/buddyCapabilities.ts` (status = `needs_key` or `planned`)
2. Add a new route under `/api/buddy/<name>`
3. Flip status to `live` when wired
4. Push — the `/capabilities` page auto-updates

This roadmap is committed to git so we're accountable to ourselves and to investors.
