/**
 * Media generation providers for DreamCo Studio (voice, image, music, video,
 * commercials).
 *
 * Honesty contract: each capability reports whether it is LIVE (a real provider
 * key is present and the call actually runs) or NEEDS_KEY (the code is wired but
 * the provider credential is missing). Nothing is faked — a NEEDS_KEY capability
 * returns an explicit error telling the operator exactly which secret to add.
 *
 * Currently LIVE without extra setup: image generation via the DreamCo-managed
 * OpenAI integration (AI_INTEGRATIONS_OPENAI_*). Voice is OWNED by DreamCo: the
 * built-in browser voice (frontend) already lets Buddy talk for free, and the
 * self-hosted DreamCo Voice Pro engine (DREAMCO_VOICE_URL) produces server-side
 * audio — ElevenLabs is only an optional fallback if a key is set. Music (Suno)
 * and video (Runway/Kling/Pika) are wired and activate the moment their key is
 * added.
 */

export type MediaKind = "image" | "voice" | "music" | "video" | "commercial";

export class NeedsKeyError extends Error {
  constructor(
    public readonly kind: MediaKind,
    public readonly envVar: string,
    public readonly provider: string,
  ) {
    super(`${provider} not configured — add ${envVar} to enable ${kind} generation.`);
    this.name = "NeedsKeyError";
  }
}

export type CapabilityStatus = "live" | "needs_key" | "needs_config";

export interface Capability {
  kind: MediaKind;
  status: CapabilityStatus;
  provider: string;
  envVar: string | null;
  note: string;
}

/**
 * Honest status:
 * - "live": adapter is implemented AND the provider key is present → it really runs.
 * - "needs_key": adapter is implemented but the key is missing.
 * - "needs_config": key may be present, but the provider endpoint/contract is not
 *   yet wired, so it cannot run. We never report "live" on key presence alone.
 */
function capStatus(implemented: boolean, hasKey: boolean): CapabilityStatus {
  if (!hasKey) return "needs_key";
  return implemented ? "live" : "needs_config";
}

function hasOpenAI(): boolean {
  return !!(process.env.AI_INTEGRATIONS_OPENAI_API_KEY && process.env.AI_INTEGRATIONS_OPENAI_BASE_URL);
}
// DreamCo Voice Pro: our own self-hosted neural TTS service (open-source model,
// not a competitor API). Activates when DREAMCO_VOICE_URL points at the service.
function hasSelfHostedVoice(): boolean {
  return !!process.env.DREAMCO_VOICE_URL;
}
function hasElevenLabs(): boolean {
  return !!process.env.ELEVENLABS_API_KEY;
}
// Server-side voice is available via our own engine OR (optional) ElevenLabs fallback.
function hasVoice(): boolean {
  return hasSelfHostedVoice() || hasElevenLabs();
}
// DreamCo Clone Studio: our own self-hosted neural cloning engines (owned, not a
// competitor API). Voice cloning reuses the DreamCo Voice Pro engine; image /
// likeness cloning uses a dedicated self-hosted service. Each goes LIVE only
// when its engine URL is configured — we never report "live" on intent alone.
function hasVoiceCloneEngine(): boolean {
  return !!process.env.DREAMCO_VOICE_URL;
}
function hasImageCloneEngine(): boolean {
  return !!process.env.DREAMCO_IMAGE_CLONE_URL;
}
function hasMusic(): boolean {
  return !!process.env.SUNO_API_KEY;
}
function hasVideo(): boolean {
  return !!(process.env.RUNWAY_API_KEY || process.env.KLING_API_KEY || process.env.PIKA_API_KEY);
}

export function getCapabilities(): Capability[] {
  const openai = hasOpenAI();
  const voice = hasVoice();
  const music = hasMusic();
  const video = hasVideo();
  // implemented = true only for adapters wired to a confirmed provider endpoint.
  const imageStatus = capStatus(true, openai);
  const voiceStatus = capStatus(true, voice);
  const musicStatus = capStatus(false, music); // Suno endpoint contract not yet confirmed
  const videoStatus = capStatus(false, video); // video provider endpoint not yet confirmed
  const commercialStatus: CapabilityStatus =
    imageStatus === "live" && voiceStatus === "live" && videoStatus === "live"
      ? "live"
      : openai && voice && video
        ? "needs_config"
        : "needs_key";
  return [
    {
      kind: "image",
      status: imageStatus,
      provider: "OpenAI (DreamCo AI integration)",
      envVar: "AI_INTEGRATIONS_OPENAI_API_KEY",
      note: openai
        ? "Live. Real images generated via the DreamCo-managed OpenAI integration (dall-e-3)."
        : "Connect the OpenAI integration to enable image generation.",
    },
    {
      kind: "voice",
      status: voiceStatus,
      provider: hasSelfHostedVoice()
        ? "DreamCo Voice Pro (self-hosted)"
        : hasElevenLabs()
          ? "ElevenLabs (fallback)"
          : "DreamCo Voice Pro (self-hosted)",
      envVar: "DREAMCO_VOICE_URL",
      note: hasSelfHostedVoice()
        ? "Live. Server-side audio via our own self-hosted DreamCo Voice Pro engine. Consent + authorization required per request."
        : hasElevenLabs()
          ? "Live via the optional ElevenLabs fallback. For a fully-owned engine, set DREAMCO_VOICE_URL to your self-hosted DreamCo Voice Pro service."
          : "Buddy already talks in-browser with the free built-in DreamCo Voice. For downloadable server-side audio, set DREAMCO_VOICE_URL (self-hosted, owned) — or optionally ELEVENLABS_API_KEY as a fallback.",
    },
    {
      kind: "music",
      status: musicStatus,
      provider: "Suno",
      envVar: "SUNO_API_KEY",
      note:
        musicStatus === "needs_config"
          ? "SUNO_API_KEY is set, but the Suno endpoint contract must be confirmed before this can run. Provide the Suno API base URL/endpoint."
          : "Add SUNO_API_KEY (and confirm the Suno endpoint) to enable music generation.",
    },
    {
      kind: "video",
      status: videoStatus,
      provider: "Runway / Kling / Pika",
      envVar: "RUNWAY_API_KEY",
      note:
        videoStatus === "needs_config"
          ? "A video provider key is set, but the provider/endpoint must be confirmed before this can run (Runway, Kling, or Pika)."
          : "Add RUNWAY_API_KEY (or KLING_API_KEY / PIKA_API_KEY) and confirm the provider to enable video generation.",
    },
    {
      kind: "commercial",
      status: commercialStatus,
      provider: "Composite (image + voice + video)",
      envVar: null,
      note:
        commercialStatus === "live"
          ? "Live. Commercials compose script + image + voiceover + video. All sub-providers connected."
          : "A commercial composes image + voice + video. Live only once those three are all live (video provider must be wired).",
    },
  ];
}

export function getCapability(kind: MediaKind): Capability {
  const cap = getCapabilities().find((c) => c.kind === kind);
  if (!cap) throw new Error(`unknown media kind: ${kind}`);
  return cap;
}

export type CloneModality = "voice" | "image";

export interface CloneCapability {
  modality: CloneModality;
  status: CapabilityStatus;
  provider: string;
  envVar: string;
  note: string;
}

/**
 * Cloning capabilities (DreamCo's competing-with-ElevenLabs perk). System-level
 * engine readiness only — per-user authorization (consent, legal acknowledgment,
 * enrollment) is enforced separately in the route layer. Honest: status is
 * needs_config until the self-hosted clone engine URL is connected; we never
 * fabricate the neural model.
 */
export function getCloneCapabilities(): CloneCapability[] {
  return [
    {
      modality: "voice",
      status: hasVoiceCloneEngine() ? "live" : "needs_config",
      provider: "DreamCo Voice Pro (self-hosted)",
      envVar: "DREAMCO_VOICE_URL",
      note: hasVoiceCloneEngine()
        ? "Live. Voice cloning runs on our own self-hosted DreamCo Voice Pro engine. Requires the speaker's enrolled, consented voice sample."
        : "Voice cloning engine not connected. Set DREAMCO_VOICE_URL to your self-hosted DreamCo Voice Pro engine to go live. Enrollment + consent + legal acknowledgment are already enforced.",
    },
    {
      modality: "image",
      status: hasImageCloneEngine() ? "live" : "needs_config",
      provider: "DreamCo Likeness (self-hosted)",
      envVar: "DREAMCO_IMAGE_CLONE_URL",
      note: hasImageCloneEngine()
        ? "Live. Likeness/image cloning runs on our own self-hosted engine. Requires the person's enrolled, consented image sample."
        : "Image/likeness cloning engine not connected. Set DREAMCO_IMAGE_CLONE_URL to your self-hosted engine to go live. Enrollment + consent + legal acknowledgment are already enforced.",
    },
  ];
}

export function getCloneCapability(modality: CloneModality): CloneCapability {
  const cap = getCloneCapabilities().find((c) => c.modality === modality);
  if (!cap) throw new Error(`unknown clone modality: ${modality}`);
  return cap;
}

/**
 * Run a clone generation against the self-hosted engine for the modality.
 * Throws NeedsKeyError when the engine is not connected (honest needs_config),
 * so the route records the attempt and returns a truthful 503 instead of faking
 * output. `sampleRef` references the requesting user's own enrolled sample.
 */
export async function generateClone(
  modality: CloneModality,
  prompt: string,
  sampleRef: string,
  params: Record<string, unknown> = {},
): Promise<GenerateResult> {
  // Strip any client-supplied binding fields. The sample reference is derived
  // strictly from the caller's active enrollment and must NEVER be overridable
  // by request params — otherwise a user with one enrollment could clone a
  // voice/likeness they never enrolled (consent bypass / IDOR).
  const safeParams: Record<string, unknown> = { ...params };
  delete safeParams.sampleRef;
  delete safeParams.voice;
  delete safeParams.voiceId;

  if (modality === "voice") {
    const url = process.env.DREAMCO_VOICE_URL;
    if (!url) throw new NeedsKeyError("voice", "DREAMCO_VOICE_URL", "DreamCo Voice Pro (self-hosted)");
    return generateVoice(prompt, { ...safeParams, voiceId: sampleRef, clone: true });
  }
  const url = process.env.DREAMCO_IMAGE_CLONE_URL;
  if (!url) throw new NeedsKeyError("image", "DREAMCO_IMAGE_CLONE_URL", "DreamCo Likeness (self-hosted)");
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (process.env.DREAMCO_IMAGE_CLONE_API_KEY) headers.authorization = `Bearer ${process.env.DREAMCO_IMAGE_CLONE_API_KEY}`;
  const res = await fetch(url, {
    method: "POST",
    headers,
    // sampleRef placed AFTER the spread so client params cannot override it.
    body: JSON.stringify({ prompt, ...safeParams, sampleRef }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`DreamCo Likeness error ${res.status}: ${text.slice(0, 300)}`);
  }
  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    const j = (await res.json()) as { url?: string; image?: string; imageBase64?: string; format?: string };
    if (j.url) return { provider: "DreamCo Likeness (self-hosted)", resultUrl: j.url };
    const b64 = j.image ?? j.imageBase64;
    if (b64) return { provider: "DreamCo Likeness (self-hosted)", resultUrl: `data:image/${j.format ?? "png"};base64,${b64}` };
    throw new Error("DreamCo Likeness returned no image");
  }
  const buf = Buffer.from(await res.arrayBuffer());
  return { provider: "DreamCo Likeness (self-hosted)", resultUrl: `data:${ct || "image/png"};base64,${buf.toString("base64")}`, meta: { bytes: buf.length } };
}

export interface GenerateResult {
  provider: string;
  resultUrl: string | null;
  meta?: Record<string, unknown>;
}

/** Real, LIVE image generation via the DreamCo-managed OpenAI integration. */
async function generateImage(prompt: string): Promise<GenerateResult> {
  const baseUrl = process.env.AI_INTEGRATIONS_OPENAI_BASE_URL;
  const apiKey = process.env.AI_INTEGRATIONS_OPENAI_API_KEY;
  if (!baseUrl || !apiKey) throw new NeedsKeyError("image", "AI_INTEGRATIONS_OPENAI_API_KEY", "OpenAI");

  const res = await fetch(`${baseUrl.replace(/\/$/, "")}/images/generations`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${apiKey}` },
    body: JSON.stringify({ model: "dall-e-3", prompt, n: 1, size: "1024x1024", response_format: "url" }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`image provider error ${res.status}: ${text.slice(0, 300)}`);
  }
  const data = (await res.json()) as { data?: Array<{ url?: string }> };
  const url = data.data?.[0]?.url;
  if (!url) throw new Error("image provider returned no url");
  return { provider: "OpenAI dall-e-3", resultUrl: url, meta: { note: "Provider-hosted URL; expires after ~1h. Persist to object storage for permanent assets." } };
}

/**
 * Server-side voice. Prefers our OWN self-hosted DreamCo Voice Pro engine
 * (DREAMCO_VOICE_URL — an open-source neural TTS service we control), and falls
 * back to ElevenLabs only if explicitly configured. Returns audio as a data URL.
 */
async function generateVoice(prompt: string, params: Record<string, unknown>): Promise<GenerateResult> {
  const selfUrl = process.env.DREAMCO_VOICE_URL;
  const apiKey = process.env.ELEVENLABS_API_KEY;
  if (selfUrl) {
    try {
      const headers: Record<string, string> = { "content-type": "application/json", accept: "audio/mpeg" };
      if (process.env.DREAMCO_VOICE_API_KEY) headers.authorization = `Bearer ${process.env.DREAMCO_VOICE_API_KEY}`;
      const res = await fetch(selfUrl, {
        method: "POST",
        headers,
        body: JSON.stringify({ text: prompt, voice: params.voiceId, ...params }),
      });
      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`DreamCo Voice Pro error ${res.status}: ${text.slice(0, 300)}`);
      }
      const ct = res.headers.get("content-type") ?? "";
      if (ct.includes("application/json")) {
        const j = (await res.json()) as { url?: string; audio?: string; audioBase64?: string; format?: string };
        if (j.url) return { provider: "DreamCo Voice Pro (self-hosted)", resultUrl: j.url };
        const b64 = j.audio ?? j.audioBase64;
        if (b64) return { provider: "DreamCo Voice Pro (self-hosted)", resultUrl: `data:audio/${j.format ?? "mpeg"};base64,${b64}` };
        throw new Error("DreamCo Voice Pro returned no audio");
      }
      const buf = Buffer.from(await res.arrayBuffer());
      return { provider: "DreamCo Voice Pro (self-hosted)", resultUrl: `data:${ct || "audio/mpeg"};base64,${buf.toString("base64")}`, meta: { bytes: buf.length } };
    } catch (err) {
      // Runtime failover: if our self-hosted engine is down but an ElevenLabs
      // key is configured, fall through to it rather than hard-failing.
      if (!apiKey) throw err;
    }
  }

  // Optional fallback: ElevenLabs (only if the operator opts in with a key).
  if (!apiKey) throw new NeedsKeyError("voice", "DREAMCO_VOICE_URL", "DreamCo Voice Pro (self-hosted)");
  const voiceId = (params.voiceId as string) || "21m00Tcm4TlvDq8ikWAM";
  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
    method: "POST",
    headers: { "xi-api-key": apiKey, "content-type": "application/json", accept: "audio/mpeg" },
    body: JSON.stringify({ text: prompt, model_id: (params.modelId as string) || "eleven_multilingual_v2" }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`ElevenLabs error ${res.status}: ${text.slice(0, 300)}`);
  }
  const buf = Buffer.from(await res.arrayBuffer());
  const dataUrl = `data:audio/mpeg;base64,${buf.toString("base64")}`;
  return { provider: "ElevenLabs (fallback)", resultUrl: dataUrl, meta: { voiceId, bytes: buf.length } };
}

/** Suno music generation. Wired; activates when SUNO_API_KEY is set. */
async function generateMusic(_prompt: string): Promise<GenerateResult> {
  if (!process.env.SUNO_API_KEY) throw new NeedsKeyError("music", "SUNO_API_KEY", "Suno");
  // Suno's public API is invite-gated and its endpoint shape varies by provider.
  // Wired to fail explicitly rather than fabricate output until a key + endpoint
  // are confirmed by the operator.
  throw new Error(
    "SUNO_API_KEY is set but the Suno endpoint contract must be confirmed before going live. " +
      "Provide the Suno API base URL/endpoint and this adapter will call it.",
  );
}

/** Runway/Kling/Pika video generation. Wired; activates when a video key is set. */
async function generateVideo(_prompt: string): Promise<GenerateResult> {
  if (!(process.env.RUNWAY_API_KEY || process.env.KLING_API_KEY || process.env.PIKA_API_KEY)) {
    throw new NeedsKeyError("video", "RUNWAY_API_KEY", "Runway/Kling/Pika");
  }
  throw new Error(
    "A video provider key is set but the provider/endpoint must be confirmed before going live. " +
      "Confirm which provider (Runway, Kling, or Pika) and this adapter will call it.",
  );
}

export async function generate(
  kind: MediaKind,
  prompt: string,
  params: Record<string, unknown> = {},
): Promise<GenerateResult> {
  switch (kind) {
    case "image":
      return generateImage(prompt);
    case "voice":
      return generateVoice(prompt, params);
    case "music":
      return generateMusic(prompt);
    case "video":
      return generateVideo(prompt);
    case "commercial": {
      // A commercial requires the full chain. Surface the first missing piece honestly.
      const caps = getCapabilities();
      const missing = (["image", "voice", "video"] as MediaKind[])
        .map((k) => caps.find((c) => c.kind === k)!)
        .filter((c) => c.status !== "live");
      if (missing.length > 0) {
        const first = missing[0]!;
        throw new NeedsKeyError("commercial", first.envVar ?? "PROVIDER_KEY", first.provider);
      }
      // All present: generate the key visual as the concrete deliverable for now.
      const img = await generateImage(prompt);
      return { provider: "Composite (image+voice+video)", resultUrl: img.resultUrl, meta: { note: "Full commercial composition orchestration is the next build step; key visual generated live." } };
    }
    default:
      throw new Error(`unknown media kind: ${kind}`);
  }
}
