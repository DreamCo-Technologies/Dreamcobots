import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Brain, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!r.ok) throw new Error(`${r.status}`);
  return (r.status === 204 ? (undefined as T) : (r.json() as Promise<T>));
}

interface Note {
  id: string;
  category: string;
  content: string;
  source: string;
  sessionId: string | null;
  createdAt: string;
}
interface NotesResponse {
  total: number;
  byCategory: Record<string, number>;
  notes: Note[];
}

const CATEGORIES = ["learning", "task", "preference", "capability_gap", "guidance"] as const;
const CAT_COLORS: Record<string, string> = {
  learning: "text-sky-400 border-sky-400/30",
  task: "text-amber-400 border-amber-400/30",
  preference: "text-emerald-400 border-emerald-400/30",
  capability_gap: "text-rose-400 border-rose-400/30",
  guidance: "text-violet-400 border-violet-400/30",
};

export default function MemoryPage() {
  const qc = useQueryClient();
  const [content, setContent] = useState("");
  const [category, setCategory] = useState<(typeof CATEGORIES)[number]>("guidance");
  const { data, isLoading } = useQuery<NotesResponse>({ queryKey: ["buddy-notes"], queryFn: () => api("/buddy/notes") });

  const addNote = useMutation({
    mutationFn: () => api("/buddy/notes", { method: "POST", body: JSON.stringify({ content, category, source: "human" }) }),
    onSuccess: () => {
      setContent("");
      qc.invalidateQueries({ queryKey: ["buddy-notes"] });
    },
  });
  const del = useMutation({
    mutationFn: (id: string) => api(`/buddy/notes/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["buddy-notes"] }),
  });

  const notes = data?.notes ?? [];

  return (
    <div className="p-6 space-y-6">
      <header className="flex items-center gap-3">
        <Brain className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-mono font-bold tracking-wide">Buddy_Memory</h1>
          <p className="text-sm text-muted-foreground">
            Buddy's persistent notes. Everything here is fed back into Buddy's context so it remembers across
            sessions. Tell Buddy "remember…" in chat and it saves a note automatically.{" "}
            <span className="text-emerald-400 font-mono">LIVE</span>
          </p>
        </div>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-6 gap-3">
        <Stat label="Total Notes" value={data?.total ?? 0} />
        {CATEGORIES.map((c) => (
          <Stat key={c} label={c.replace("_", " ")} value={data?.byCategory?.[c] ?? 0} />
        ))}
      </section>

      <section className="rounded-lg border border-border/40 bg-card p-4 space-y-3">
        <h2 className="font-mono text-sm font-bold">Give Buddy guidance</h2>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="e.g. Always label features LIVE / NEEDS_KEY / PLANNED and never show fake revenue."
          rows={3}
          className="w-full rounded-md bg-background border border-border/40 p-3 text-sm font-mono resize-y"
        />
        <div className="flex items-center gap-3 flex-wrap">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value as (typeof CATEGORIES)[number])}
            className="rounded-md bg-background border border-border/40 px-3 py-2 text-sm font-mono"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <Button onClick={() => addNote.mutate()} disabled={!content.trim() || addNote.isPending} className="font-mono">
            <Plus className="h-4 w-4 mr-2" />
            {addNote.isPending ? "Saving…" : "Save to Memory"}
          </Button>
          {addNote.isError && <span className="text-xs text-rose-400 font-mono">Sign in required to save.</span>}
        </div>
      </section>

      {isLoading ? (
        <div className="p-8 text-center text-muted-foreground font-mono text-sm">Loading memory…</div>
      ) : notes.length === 0 ? (
        <div className="rounded-lg border border-border/40 bg-card p-8 text-center text-muted-foreground font-mono text-sm">
          No notes yet. Save guidance above, or tell Buddy to "remember" something in chat.
        </div>
      ) : (
        <section className="space-y-2">
          {notes.map((n) => (
            <div key={n.id} className="rounded-lg border border-border/40 bg-card p-3 flex items-start gap-3">
              <span className={`px-2 py-0.5 rounded border text-[10px] font-mono shrink-0 ${CAT_COLORS[n.category] ?? "text-muted-foreground border-border/40"}`}>
                {n.category}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm break-words">{n.content}</p>
                <p className="text-[10px] font-mono text-muted-foreground mt-1">
                  {n.source} · {new Date(n.createdAt).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => del.mutate(n.id)}
                className="text-muted-foreground hover:text-rose-400 shrink-0"
                title="Delete note"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-border/40 bg-card p-3">
      <div className="text-[10px] font-mono uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 text-xl font-mono font-bold text-primary">{value.toLocaleString()}</div>
    </div>
  );
}
