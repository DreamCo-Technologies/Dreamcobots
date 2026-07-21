import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wrench, Key, CheckCircle2 } from "lucide-react";

type Status = "planned" | "needs_key";

interface Props {
  title: string;
  icon: React.ReactNode;
  status: Status;
  tagline: string;
  scope: string;
  willDo: string[];
  needs?: string[];
}

export function PlannedSection({ title, icon, status, tagline, scope, willDo, needs }: Props) {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <span className="text-primary">{icon}</span>
          {title}
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">{tagline}</p>
      </div>

      <Card className="p-6 border-border/40 bg-card/50 backdrop-blur max-w-3xl">
        <div className="flex items-center gap-2 mb-4">
          {status === "needs_key" ? (
            <Badge variant="outline" className="font-mono text-[10px] gap-1 text-amber-400 border-amber-500/30"><Key className="h-3 w-3" />NEEDS_KEY</Badge>
          ) : (
            <Badge variant="outline" className="font-mono text-[10px] gap-1 text-muted-foreground"><Wrench className="h-3 w-3" />PLANNED</Badge>
          )}
          <span className="font-mono text-xs text-muted-foreground">est. {scope}</span>
        </div>

        <p className="font-mono text-sm text-foreground/80 mb-6">
          This module is scaffolded and routed, but not yet wired to live data. Here's exactly what it will do once built — no fake numbers until it's real.
        </p>

        <div className="font-mono text-xs uppercase tracking-wider text-primary mb-2">// what this will do</div>
        <ul className="space-y-2 mb-6">
          {willDo.map((w, i) => (
            <li key={i} className="flex items-start gap-2 font-mono text-sm text-foreground/80">
              <CheckCircle2 className="h-4 w-4 text-emerald-400/70 mt-0.5 flex-shrink-0" />
              <span>{w}</span>
            </li>
          ))}
        </ul>

        {needs && needs.length > 0 ? (
          <>
            <div className="font-mono text-xs uppercase tracking-wider text-amber-400 mb-2">// requires</div>
            <ul className="space-y-1">
              {needs.map((n, i) => (
                <li key={i} className="flex items-start gap-2 font-mono text-sm text-amber-400/80">
                  <Key className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                  <code className="text-amber-300/90">{n}</code>
                </li>
              ))}
            </ul>
          </>
        ) : null}
      </Card>
    </div>
  );
}
