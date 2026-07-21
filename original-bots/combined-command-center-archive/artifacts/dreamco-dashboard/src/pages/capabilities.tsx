import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Skeleton } from "@/components/ui/skeleton";
import { Brain, CheckCircle2, Key, Wrench, Image as ImageIcon, Loader2, ExternalLink } from "lucide-react";

interface Capability {
  id: string; name: string; category: string;
  status: "live" | "needs_key" | "planned";
  description: string;
  requiredEnv?: string[]; endpoint?: string; notes?: string;
}
interface CapsResp {
  totals: { total: number; live: number; needsKey: number; planned: number };
  capabilities: Capability[];
}

async function api<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!r.ok) throw new Error(`${r.status}: ${await r.text()}`);
  return r.json();
}

function statusBadge(s: Capability["status"]) {
  if (s === "live") return <Badge className="font-mono text-[10px] gap-1 bg-emerald-500/15 text-emerald-400 border-emerald-500/30"><CheckCircle2 className="h-3 w-3" />live</Badge>;
  if (s === "needs_key") return <Badge variant="outline" className="font-mono text-[10px] gap-1 text-amber-400 border-amber-500/30"><Key className="h-3 w-3" />needs key</Badge>;
  return <Badge variant="outline" className="font-mono text-[10px] gap-1 text-muted-foreground"><Wrench className="h-3 w-3" />planned</Badge>;
}

export default function CapabilitiesPage() {
  const caps = useQuery<CapsResp>({ queryKey: ["caps"], queryFn: () => api("/buddy/capabilities") });

  const [imgPrompt, setImgPrompt] = useState("");
  const [imgUrl, setImgUrl] = useState<string | null>(null);
  const imgGen = useMutation({
    mutationFn: (prompt: string) => api<{ url: string }>("/buddy/image", { method: "POST", body: JSON.stringify({ prompt }) }),
    onSuccess: (d) => setImgUrl(d.url),
  });

  const grouped: Record<string, Capability[]> = {};
  for (const c of caps.data?.capabilities ?? []) {
    (grouped[c.category] ??= []).push(c);
  }

  return (
    <div className="space-y-6">
      <div className="border-b border-border/40 pb-4">
        <h1 className="font-mono text-2xl text-primary tracking-wider flex items-center gap-2">
          <Brain className="h-6 w-6" /> BUDDY_CAPABILITIES
        </h1>
        <p className="font-mono text-xs text-muted-foreground mt-1">
          Full honest matrix of what Buddy can do today, what needs an API key, and what's planned
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label="TOTAL" value={caps.data?.totals.total ?? 0} loading={caps.isLoading} />
        <Stat label="LIVE_NOW" value={caps.data?.totals.live ?? 0} loading={caps.isLoading} tone="emerald" />
        <Stat label="NEEDS_API_KEY" value={caps.data?.totals.needsKey ?? 0} loading={caps.isLoading} tone="amber" />
        <Stat label="PLANNED" value={caps.data?.totals.planned ?? 0} loading={caps.isLoading} />
      </div>

      {/* Image Studio — first live demo of vision capability */}
      <Card className="p-4 space-y-3 border-border/40">
        <h2 className="font-mono text-sm text-primary uppercase tracking-wider flex items-center gap-2">
          <ImageIcon className="h-4 w-4" /> // image studio (live)
        </h2>
        <p className="font-mono text-xs text-muted-foreground">
          Generate any image via OpenAI gpt-image-1. Same key as chat — no extra setup needed. Music videos & reels need a separate provider (see below).
        </p>
        <Textarea
          value={imgPrompt}
          onChange={(e) => setImgPrompt(e.target.value)}
          placeholder="Cinematic poster: BuddyBot orchestrating 171 robots in a neon command center, holographic dashboards..."
          rows={3}
          className="font-mono text-sm"
          data-testid="input-image-prompt"
        />
        <Button
          onClick={() => imgPrompt && imgGen.mutate(imgPrompt.trim())}
          disabled={!imgPrompt || imgGen.isPending}
          className="font-mono text-xs"
          data-testid="button-image-gen"
        >
          {imgGen.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <ImageIcon className="h-4 w-4 mr-1" />}
          GENERATE_IMAGE
        </Button>
        {imgGen.error ? <div className="font-mono text-xs text-destructive">{String(imgGen.error as Error)}</div> : null}
        {imgUrl ? (
          <div className="space-y-2">
            <img src={imgUrl} alt="generated" className="max-w-full rounded border border-border/40" />
            <a href={imgUrl} download="buddy-image.png" className="font-mono text-[10px] text-primary inline-flex items-center gap-1">
              <ExternalLink className="h-3 w-3" /> open / download
            </a>
          </div>
        ) : null}
      </Card>

      {/* Capability matrix */}
      {caps.isLoading ? (
        <div className="space-y-2">{[1,2,3,4].map(i => <Skeleton key={i} className="h-24 w-full" />)}</div>
      ) : (
        Object.entries(grouped).map(([cat, items]) => (
          <Card key={cat} className="p-4 border-border/40">
            <h3 className="font-mono text-xs uppercase tracking-wider text-muted-foreground mb-3">// {cat}</h3>
            <div className="divide-y divide-border/40">
              {items.map(c => (
                <div key={c.id} className="py-3 flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-sm text-foreground">{c.name}</span>
                      {statusBadge(c.status)}
                    </div>
                    <div className="font-mono text-xs text-muted-foreground mt-1">{c.description}</div>
                    {c.endpoint ? <div className="font-mono text-[10px] text-primary/70 mt-1">{c.endpoint}</div> : null}
                    {c.requiredEnv?.length ? (
                      <div className="font-mono text-[10px] text-amber-400 mt-1">
                        needs: {c.requiredEnv.join(", ")}
                      </div>
                    ) : null}
                    {c.notes ? <div className="font-mono text-[10px] text-muted-foreground/70 mt-1 italic">{c.notes}</div> : null}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        ))
      )}
    </div>
  );
}

function Stat({ label, value, loading, tone }: { label: string; value: number; loading: boolean; tone?: "emerald" | "amber" }) {
  const color = tone === "emerald" ? "text-emerald-400" : tone === "amber" ? "text-amber-400" : "text-primary";
  return (
    <Card className="p-3 border-border/40">
      <div className="font-mono text-[10px] uppercase text-muted-foreground tracking-wider">{label}</div>
      {loading ? <Skeleton className="h-7 w-16 mt-1" /> : <div className={`font-mono text-2xl mt-1 ${color}`}>{value}</div>}
    </Card>
  );
}
