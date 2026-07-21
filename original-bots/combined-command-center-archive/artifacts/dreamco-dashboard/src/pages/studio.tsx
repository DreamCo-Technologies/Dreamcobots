import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Clapperboard, Image as ImageIcon, Mic, Music, Video, Megaphone, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDreamcoVoice } from "@/lib/speech";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  const body = r.status === 204 ? undefined : await r.json().catch(() => undefined);
  if (!r.ok) {
    const err = new Error((body as { error?: string })?.error ?? `${r.status}`) as Error & { body?: unknown; status?: number };
    err.body = body;
    err.status = r.status;
    throw err;
  }
  return body as T;
}

type Kind = "image" | "voice" | "music" | "video" | "commercial";

type CapStatus = "live" | "needs_key" | "needs_config";
interface Capability {
  kind: Kind;
  status: CapStatus;
  provider: string;
  envVar: string | null;
  note: string;
}
function statusBadge(s: CapStatus): { label: string; cls: string } {
  if (s === "live") return { label: "LIVE", cls: "text-emerald-400 border-emerald-400/30" };
  if (s === "needs_config") return { label: "NEEDS_SETUP", cls: "text-amber-400 border-amber-400/30" };
  return { label: "NEEDS_KEY", cls: "text-amber-400 border-amber-400/30" };
}
interface CapsResponse { capabilities: Capability[] }

interface Job {
  id: string;
  kind: Kind;
  provider: string | null;
  status: string;
  prompt: string;
  resultUrl: string | null;
  error: string | null;
  createdAt: string;
}
interface JobsResponse { total: number; jobs: Job[] }

const KIND_META: Record<Kind, { label: string; icon: typeof ImageIcon; hint: string }> = {
  image: { label: "Image", icon: ImageIcon, hint: "Describe the image for your video / commercial frame." },
  voice: { label: "Voice", icon: Mic, hint: "Text to speak. Voice mimicry requires consent + authorization." },
  music: { label: "Music", icon: Music, hint: "Describe the track (genre, mood, tempo, instruments)." },
  video: { label: "Video", icon: Video, hint: "Describe the video clip to generate." },
  commercial: { label: "Commercial", icon: Megaphone, hint: "Describe the ad: product, message, vibe." },
};

const STATUS_COLORS: Record<string, string> = {
  succeeded: "text-emerald-400 border-emerald-400/30",
  running: "text-sky-400 border-sky-400/30",
  needs_key: "text-amber-400 border-amber-400/30",
  needs_config: "text-amber-400 border-amber-400/30",
  needs_consent: "text-amber-400 border-amber-400/30",
  failed: "text-rose-400 border-rose-400/30",
  queued: "text-muted-foreground border-border/40",
};

export default function StudioPage() {
  const qc = useQueryClient();
  const [kind, setKind] = useState<Kind>("image");
  const [prompt, setPrompt] = useState("");
  const [consent, setConsent] = useState(false);
  const voice = useDreamcoVoice();

  const { data: capsData } = useQuery<CapsResponse>({ queryKey: ["media-caps"], queryFn: () => api("/media/capabilities") });
  const { data: jobsData, isError: jobsError } = useQuery<JobsResponse>({ queryKey: ["media-jobs"], queryFn: () => api("/media/jobs"), retry: false });

  const caps = capsData?.capabilities ?? [];
  const activeCap = caps.find((c) => c.kind === kind);

  const gen = useMutation({
    mutationFn: () => api<{ status: string; job: Job }>("/media/generate", { method: "POST", body: JSON.stringify({ kind, prompt, consent }) }),
    onSuccess: () => {
      setPrompt("");
      qc.invalidateQueries({ queryKey: ["media-jobs"] });
    },
    onError: () => qc.invalidateQueries({ queryKey: ["media-jobs"] }),
  });

  const genErr = gen.error as (Error & { status?: number; body?: { error?: string; capability?: Capability } }) | null;

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center gap-3">
        <Clapperboard className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-mono font-bold tracking-wide">DreamCo_Studio</h1>
          <p className="text-sm text-muted-foreground max-w-3xl">
            Generate voice, images, music, video, and commercials. Every request is authenticated, gated behind an
            explicit consent / authorization checkbox, and recorded as an audit-trail job. Each capability is labeled{" "}
            <span className="text-emerald-400 font-mono">LIVE</span> or{" "}
            <span className="text-amber-400 font-mono">NEEDS_KEY</span> — nothing is faked.
          </p>
        </div>
      </header>

      {/* Capability status grid */}
      <section className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {(Object.keys(KIND_META) as Kind[]).map((k) => {
          const cap = caps.find((c) => c.kind === k);
          const Icon = KIND_META[k].icon;
          const badge = statusBadge(cap?.status ?? "needs_key");
          return (
            <button
              key={k}
              onClick={() => setKind(k)}
              className={`text-left rounded-lg border bg-card p-3 transition ${kind === k ? "border-primary" : "border-border/40 hover:border-border"}`}
            >
              <div className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-primary" />
                <span className="font-mono text-sm font-bold">{KIND_META[k].label}</span>
              </div>
              <div className={`mt-2 inline-block px-2 py-0.5 rounded border text-[10px] font-mono ${badge.cls}`}>
                {badge.label}
              </div>
              <p className="mt-2 text-[10px] text-muted-foreground leading-snug">{cap?.provider}</p>
            </button>
          );
        })}
      </section>

      {/* Generator */}
      <section className="rounded-lg border border-border/40 bg-card p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-mono text-sm font-bold">{KIND_META[kind].label} generation</h2>
          {activeCap && (
            <span className={`px-2 py-0.5 rounded border text-[10px] font-mono ${statusBadge(activeCap.status).cls}`}>
              {statusBadge(activeCap.status).label}
            </span>
          )}
        </div>
        {activeCap && <p className="text-xs text-muted-foreground">{activeCap.note}</p>}

        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={KIND_META[kind].hint}
          rows={3}
          className="w-full rounded-md bg-background border border-border/40 p-3 text-sm font-mono resize-y"
        />

        <label className="flex items-start gap-2 text-xs text-muted-foreground cursor-pointer select-none">
          <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="mt-0.5" />
          <span>
            I confirm I am authorized to generate{kind === "voice" ? " or clone this voice" : " this content"} and have the
            rights / consent of any person or brand depicted. This acknowledgement is logged with my account.
          </span>
        </label>

        <div className="flex items-center gap-3 flex-wrap">
          <Button
            onClick={() => gen.mutate()}
            disabled={!prompt.trim() || !consent || gen.isPending}
            className="font-mono"
          >
            {gen.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
            {gen.isPending ? "Generating…" : `Generate ${KIND_META[kind].label}`}
          </Button>
          {kind === "voice" && voice.supported && (
            <Button
              type="button"
              variant="outline"
              className="font-mono"
              disabled={!prompt.trim()}
              onClick={() => (voice.speaking ? voice.stop() : voice.speak(prompt))}
              title="Preview instantly in your browser with the free built-in DreamCo Voice (no key needed)"
            >
              {voice.speaking ? "Stop preview" : "Preview (DreamCo Voice)"}
            </Button>
          )}
          {!consent && <span className="text-[10px] font-mono text-amber-400">Consent required to enable.</span>}
        </div>
        {kind === "voice" && voice.supported && (
          <p className="text-[10px] font-mono text-muted-foreground">
            Preview uses the free built-in DreamCo Voice (your browser). The Generate button produces a downloadable
            audio file via our self-hosted DreamCo Voice Pro engine when configured.
          </p>
        )}

        {genErr && (
          <div className="rounded-md border border-amber-400/30 bg-amber-400/5 p-3 text-xs font-mono text-amber-300">
            {genErr.status === 401
              ? "Sign in required to generate media."
              : genErr.status === 503
                ? `Not connected: ${genErr.body?.error ?? genErr.message}`
                : `Failed: ${genErr.body?.error ?? genErr.message}`}
          </div>
        )}
      </section>

      {/* Job history / audit trail */}
      <section className="space-y-2">
        <h2 className="font-mono text-sm font-bold">Your generations <span className="text-muted-foreground font-normal">(audit trail)</span></h2>
        {jobsError ? (
          <div className="rounded-lg border border-border/40 bg-card p-6 text-center text-muted-foreground font-mono text-sm">
            Sign in to view and create media generations.
          </div>
        ) : (jobsData?.jobs.length ?? 0) === 0 ? (
          <div className="rounded-lg border border-border/40 bg-card p-6 text-center text-muted-foreground font-mono text-sm">
            No generations yet.
          </div>
        ) : (
          jobsData!.jobs.map((j) => {
            const Icon = KIND_META[j.kind]?.icon ?? ImageIcon;
            return (
              <div key={j.id} className="rounded-lg border border-border/40 bg-card p-3 flex items-start gap-3">
                <Icon className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-2 py-0.5 rounded border text-[10px] font-mono ${STATUS_COLORS[j.status] ?? "text-muted-foreground border-border/40"}`}>
                      {j.status}
                    </span>
                    <span className="text-[10px] font-mono text-muted-foreground">{j.kind} · {j.provider ?? "—"}</span>
                  </div>
                  <p className="text-sm break-words mt-1">{j.prompt}</p>
                  {j.error && <p className="text-[10px] font-mono text-amber-400 mt-1 break-words">{j.error}</p>}
                  {j.resultUrl && j.kind === "image" && (
                    <img src={j.resultUrl} alt={j.prompt} className="mt-2 rounded-md max-h-64 border border-border/40" />
                  )}
                  {j.resultUrl && j.kind === "voice" && (
                    <audio controls src={j.resultUrl} className="mt-2 w-full max-w-md" />
                  )}
                  <p className="text-[10px] font-mono text-muted-foreground mt-1">{new Date(j.createdAt).toLocaleString()}</p>
                </div>
              </div>
            );
          })
        )}
      </section>
    </div>
  );
}
