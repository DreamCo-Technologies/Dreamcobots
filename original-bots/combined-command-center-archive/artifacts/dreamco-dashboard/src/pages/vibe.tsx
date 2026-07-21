import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Sparkles, BookOpen, Lightbulb, Code2, Loader2, Sigma } from "lucide-react";

interface VibeLib {
  id: string;
  name: string;
  ecosystem: string;
  summary: string | null;
  capabilities: string[];
  mathFoundations: string[];
  revolutionaryUses: string[];
  learnedAt: string;
}
interface VibeIdea {
  id: string;
  title: string;
  library: string | null;
  ecosystem: string | null;
  description: string;
  impactScore: number;
  mathBasis: string | null;
  createdAt: string;
}
interface VibeStats {
  librariesLearned: number;
  ideasGenerated: number;
  buildsCompleted: number;
  avgImpactScore: number;
  ecosystems: { ecosystem: string; n: number }[];
}
interface VibeBuild {
  id: string;
  prompt: string;
  language: string;
  outputCode: string | null;
  explanation: string | null;
  librariesUsed: string[];
  createdAt: string;
}

const API = "/api";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) } });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<T>;
}

const SEED_PRESETS: Record<string, string[]> = {
  python: ["numpy", "pandas", "scipy", "scikit-learn", "torch", "transformers", "sympy", "networkx", "statsmodels", "jax"],
  javascript: ["react", "three.js", "d3", "tensorflow.js", "rxjs", "tone.js", "mathjs", "fabric.js"],
  rust: ["nalgebra", "tokio", "rayon", "candle-core", "petgraph"],
  go: ["gonum", "ent", "fiber", "cobra"],
  julia: ["Flux.jl", "DifferentialEquations.jl", "JuMP.jl", "Plots.jl"],
};

export default function VibePage() {
  const qc = useQueryClient();
  const [eco, setEco] = useState("python");
  const [libName, setLibName] = useState("");
  const [buildPrompt, setBuildPrompt] = useState("");
  const [buildLang, setBuildLang] = useState("typescript");
  const [buildMode, setBuildMode] = useState<"code" | "game" | "simulation" | "lesson" | "library">("code");
  const [previewBuildId, setPreviewBuildId] = useState<string | null>(null);

  const stats = useQuery<VibeStats>({ queryKey: ["vibe-stats"], queryFn: () => api("/vibe/stats"), refetchInterval: 5000 });
  const libs = useQuery<VibeLib[]>({ queryKey: ["vibe-libs"], queryFn: () => api("/vibe/libraries?limit=50") });
  const ideas = useQuery<VibeIdea[]>({ queryKey: ["vibe-ideas"], queryFn: () => api("/vibe/ideas?limit=30") });
  const builds = useQuery<VibeBuild[]>({ queryKey: ["vibe-builds"], queryFn: () => api("/vibe/builds?limit=10") });

  const learn = useMutation({
    mutationFn: (v: { name: string; ecosystem: string }) =>
      api("/vibe/learn", { method: "POST", body: JSON.stringify(v) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["vibe-stats"] });
      qc.invalidateQueries({ queryKey: ["vibe-libs"] });
      qc.invalidateQueries({ queryKey: ["vibe-ideas"] });
      setLibName("");
    },
  });

  const sweep = useMutation({
    mutationFn: (v: { ecosystem: string; names: string[] }) =>
      api("/vibe/sweep", { method: "POST", body: JSON.stringify(v) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["vibe-stats"] });
      qc.invalidateQueries({ queryKey: ["vibe-libs"] });
      qc.invalidateQueries({ queryKey: ["vibe-ideas"] });
    },
  });

  const build = useMutation({
    mutationFn: (v: { prompt: string; language: string; mode: string }) =>
      api<VibeBuild>("/vibe/build", { method: "POST", body: JSON.stringify(v) }),
    onSuccess: (b) => {
      qc.invalidateQueries({ queryKey: ["vibe-stats"] });
      qc.invalidateQueries({ queryKey: ["vibe-builds"] });
      setBuildPrompt("");
      if (b?.language === "html" || (b?.outputCode ?? "").trim().startsWith("<!") || (b?.outputCode ?? "").includes("<html")) {
        setPreviewBuildId(b.id);
      }
    },
  });

  const trainAll = useMutation({
    mutationFn: () => api<{ queued: Record<string, number> }>("/vibe/train-all", { method: "POST", body: "{}" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["vibe-stats"] }),
  });

  const MODES: { id: typeof buildMode; label: string; hint: string }[] = [
    { id: "code", label: "CODE", hint: "single-file utility" },
    { id: "game", label: "GAME", hint: "playable browser mini-game" },
    { id: "simulation", label: "SIMULATION", hint: "interactive physics/math sim" },
    { id: "lesson", label: "LESSON", hint: "kid-friendly learning game (parents)" },
    { id: "library", label: "LIBRARY", hint: "reusable package for vibe coders" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between border-b border-border/40 pb-4">
        <div>
          <h1 className="font-mono text-2xl text-primary tracking-wider flex items-center gap-2">
            <Sparkles className="h-6 w-6" /> BUDDY_VIBE_ENGINE
          </h1>
          <p className="font-mono text-xs text-muted-foreground mt-1">
            Learn every coding library on Earth. Fuse code with mathematics. Invent revolutionary uses for humans.
          </p>
        </div>
        <Badge variant="outline" className="font-mono text-xs">
          model: gpt-5-mini
        </Badge>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="LIBRARIES_LEARNED" value={stats.data?.librariesLearned ?? 0} icon={<BookOpen className="h-4 w-4" />} />
        <StatCard label="REVOLUTIONARY_IDEAS" value={stats.data?.ideasGenerated ?? 0} icon={<Lightbulb className="h-4 w-4" />} />
        <StatCard label="BUILDS_SHIPPED" value={stats.data?.buildsCompleted ?? 0} icon={<Code2 className="h-4 w-4" />} />
        <StatCard label="AVG_IMPACT" value={(stats.data?.avgImpactScore ?? 0).toFixed(2)} icon={<Sigma className="h-4 w-4" />} />
      </div>

      {/* Learn / Sweep */}
      <Card className="p-4 space-y-4 border-border/40">
        <h2 className="font-mono text-sm text-primary uppercase tracking-wider">// study a library</h2>
        <div className="flex flex-wrap gap-2">
          {Object.keys(SEED_PRESETS).map((e) => (
            <Button key={e} size="sm" variant={eco === e ? "default" : "outline"} className="font-mono text-xs" onClick={() => setEco(e)}>
              {e}
            </Button>
          ))}
        </div>
        <div className="flex gap-2">
          <Input
            value={libName}
            onChange={(e) => setLibName(e.target.value)}
            placeholder={`library name (e.g. ${SEED_PRESETS[eco]?.[0] ?? "numpy"})`}
            className="font-mono text-sm"
            data-testid="input-lib-name"
          />
          <Button
            onClick={() => libName && learn.mutate({ name: libName.trim(), ecosystem: eco })}
            disabled={!libName || learn.isPending}
            className="font-mono text-xs"
            data-testid="button-learn"
          >
            {learn.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "LEARN"}
          </Button>
        </div>
        <div className="flex items-center justify-between pt-2 border-t border-border/40 gap-2 flex-wrap">
          <div className="font-mono text-xs text-muted-foreground">
            Sweep top {SEED_PRESETS[eco]?.length ?? 0} {eco} libs · or master all 5 ecosystems
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="secondary"
              onClick={() => sweep.mutate({ ecosystem: eco, names: SEED_PRESETS[eco] ?? [] })}
              disabled={sweep.isPending}
              className="font-mono text-xs"
              data-testid="button-sweep"
            >
              {sweep.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              SWEEP_{eco.toUpperCase()}
            </Button>
            <Button
              size="sm"
              onClick={() => trainAll.mutate()}
              disabled={trainAll.isPending}
              className="font-mono text-xs"
              data-testid="button-train-all"
            >
              {trainAll.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Sparkles className="h-3 w-3 mr-1" />}
              TRAIN_ALL
            </Button>
          </div>
        </div>
        {trainAll.data ? (
          <div className="font-mono text-xs text-muted-foreground">
            Mastery sweep queued: {Object.entries(trainAll.data.queued).map(([k,v]) => `${k}=${v}`).join(" · ")}. Watch counts climb in the stats above.
          </div>
        ) : null}
        {sweep.data ? (
          <div className="font-mono text-xs text-muted-foreground">
            Last sweep: {(sweep.data as { processed: number }).processed} libraries processed
          </div>
        ) : null}
        {(learn.error || sweep.error) ? (
          <div className="font-mono text-xs text-destructive">{String((learn.error || sweep.error) as Error)}</div>
        ) : null}
      </Card>

      {/* Vibe code */}
      <Card className="p-4 space-y-3 border-border/40">
        <h2 className="font-mono text-sm text-primary uppercase tracking-wider">// vibe-code something</h2>
        <div className="flex flex-wrap gap-2">
          {MODES.map((m) => (
            <button
              key={m.id}
              onClick={() => {
                setBuildMode(m.id);
                if (m.id === "game" || m.id === "simulation" || m.id === "lesson") setBuildLang("html");
                else if (m.id === "library") setBuildLang("typescript");
              }}
              className={`px-3 py-1.5 rounded border font-mono text-xs transition ${buildMode === m.id ? "bg-primary text-primary-foreground border-primary" : "border-border/40 text-muted-foreground hover:text-foreground"}`}
              data-testid={`mode-${m.id}`}
            >
              <div>{m.label}</div>
              <div className="text-[9px] opacity-70 normal-case">{m.hint}</div>
            </button>
          ))}
        </div>
        <Textarea
          value={buildPrompt}
          onChange={(e) => setBuildPrompt(e.target.value)}
          placeholder={
            buildMode === "lesson" ? "Teach my 8-year-old fractions through pizza-slicing..." :
            buildMode === "game" ? "A side-scrolling platformer where you collect prime numbers..." :
            buildMode === "simulation" ? "Simulate a double pendulum with adjustable damping..." :
            buildMode === "library" ? "A graph algorithms library with Dijkstra, A*, and topological sort..." :
            "describe what to build, in plain english..."
          }
          rows={3}
          className="font-mono text-sm"
          data-testid="input-build-prompt"
        />
        <div className="flex gap-2">
          <Input value={buildLang} onChange={(e) => setBuildLang(e.target.value)} className="font-mono text-sm w-48" placeholder="language" />
          <Button
            onClick={() => buildPrompt && build.mutate({ prompt: buildPrompt.trim(), language: buildLang, mode: buildMode })}
            disabled={!buildPrompt || build.isPending}
            className="font-mono text-xs flex-1"
            data-testid="button-build"
          >
            {build.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Sparkles className="h-4 w-4 mr-1" />}
            GENERATE_{buildMode.toUpperCase()}
          </Button>
        </div>
        {build.error ? <div className="font-mono text-xs text-destructive">{String(build.error as Error)}</div> : null}
      </Card>

      {/* Recent builds */}
      {builds.data && builds.data.length > 0 ? (
        <Card className="p-4 space-y-3 border-border/40">
          <h2 className="font-mono text-sm text-primary uppercase tracking-wider">// recent builds</h2>
          <div className="space-y-3">
            {builds.data.map((b) => (
              <div key={b.id} className="border border-border/40 p-3 rounded space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-mono text-xs text-foreground truncate">{b.prompt}</div>
                  <Badge variant="outline" className="font-mono text-[10px]">{b.language}</Badge>
                </div>
                {b.explanation ? <div className="font-mono text-xs text-muted-foreground">{b.explanation}</div> : null}
                {b.outputCode ? (
                  <>
                    {(b.language === "html" || b.outputCode.trim().startsWith("<!") || b.outputCode.includes("<html")) ? (
                      <div className="space-y-1">
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" className="font-mono text-[10px] h-6" onClick={() => setPreviewBuildId(previewBuildId === b.id ? null : b.id)}>
                            {previewBuildId === b.id ? "HIDE_PREVIEW" : "RUN_PREVIEW"}
                          </Button>
                        </div>
                        {previewBuildId === b.id ? (
                          <iframe
                            title={`vibe-${b.id}`}
                            srcDoc={b.outputCode}
                            sandbox="allow-scripts"
                            className="w-full h-96 rounded border border-border/40 bg-white"
                          />
                        ) : null}
                      </div>
                    ) : null}
                    <pre className="font-mono text-[11px] bg-muted/30 p-2 rounded overflow-x-auto max-h-64 whitespace-pre-wrap">{b.outputCode}</pre>
                  </>
                ) : null}
                {b.librariesUsed.length ? (
                  <div className="flex flex-wrap gap-1">
                    {b.librariesUsed.map((l) => <Badge key={l} variant="secondary" className="font-mono text-[10px]">{l}</Badge>)}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      {/* Top ideas */}
      <Card className="p-4 space-y-3 border-border/40">
        <h2 className="font-mono text-sm text-primary uppercase tracking-wider flex items-center gap-2">
          <Lightbulb className="h-4 w-4" /> revolutionary ideas (ranked by impact)
        </h2>
        {ideas.isLoading ? <div className="font-mono text-xs text-muted-foreground">Loading…</div> : null}
        {ideas.data && ideas.data.length === 0 ? <div className="font-mono text-xs text-muted-foreground">No ideas yet. Learn a library above.</div> : null}
        <div className="grid md:grid-cols-2 gap-3">
          {ideas.data?.map((i) => (
            <div key={i.id} className="border border-border/40 p-3 rounded space-y-1">
              <div className="flex items-center justify-between">
                <div className="font-mono text-sm text-primary">{i.title}</div>
                <Badge variant="outline" className="font-mono text-[10px]">{(i.impactScore * 100).toFixed(0)}%</Badge>
              </div>
              <div className="font-mono text-xs text-muted-foreground">{i.description}</div>
              <div className="flex items-center gap-2 pt-1">
                {i.library ? <Badge variant="secondary" className="font-mono text-[10px]">{i.library}</Badge> : null}
                {i.mathBasis ? <span className="font-mono text-[10px] text-accent-foreground/70">∑ {i.mathBasis}</span> : null}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Learned libraries */}
      <Card className="p-4 space-y-3 border-border/40">
        <h2 className="font-mono text-sm text-primary uppercase tracking-wider flex items-center gap-2">
          <BookOpen className="h-4 w-4" /> learned libraries
        </h2>
        {libs.data && libs.data.length === 0 ? <div className="font-mono text-xs text-muted-foreground">Nothing studied yet.</div> : null}
        <div className="grid md:grid-cols-2 gap-3">
          {libs.data?.map((l) => (
            <div key={l.id} className="border border-border/40 p-3 rounded space-y-2">
              <div className="flex items-center justify-between">
                <div className="font-mono text-sm text-primary">{l.name}</div>
                <Badge variant="outline" className="font-mono text-[10px]">{l.ecosystem}</Badge>
              </div>
              {l.summary ? <div className="font-mono text-xs text-muted-foreground">{l.summary}</div> : null}
              {l.capabilities.length ? (
                <div className="flex flex-wrap gap-1">
                  {l.capabilities.slice(0, 6).map((c) => <Badge key={c} variant="secondary" className="font-mono text-[10px]">{c}</Badge>)}
                </div>
              ) : null}
              {l.mathFoundations.length ? (
                <div className="font-mono text-[10px] text-muted-foreground">∑ {l.mathFoundations.join(" · ")}</div>
              ) : null}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: number | string; icon: React.ReactNode }) {
  return (
    <Card className="p-3 border-border/40">
      <div className="flex items-center justify-between">
        <div className="font-mono text-[10px] uppercase text-muted-foreground tracking-wider">{label}</div>
        <div className="text-muted-foreground">{icon}</div>
      </div>
      <div className="font-mono text-2xl text-primary mt-1">{value}</div>
    </Card>
  );
}
