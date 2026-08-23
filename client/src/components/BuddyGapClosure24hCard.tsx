import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, BrainCircuit, Pause, Play, RefreshCw } from "lucide-react";

export function BuddyGapClosure24hCard({
  status = "scheduled",
  queueDepth = 0,
  sourcesThisWeek = 0,
  gapsClosed = 0,
  onRunNow,
  onPause,
  onResume,
}: {
  status?: "scheduled" | "running" | "paused" | "hold";
  queueDepth?: number;
  sourcesThisWeek?: number;
  gapsClosed?: number;
  onRunNow?: () => void;
  onPause?: () => void;
  onResume?: () => void;
}) {
  const active = status === "running";
  return (
    <Card className="p-4 border-primary/20 bg-primary/5" data-testid="buddy-gap-closure-24h">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BrainCircuit className="h-5 w-5" />
            <h3 className="font-semibold">Buddy 24h Gap Closure</h3>
            <Badge variant="outline">{status}</Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Discover sources, sandbox every learning job, measure gains and requeue unresolved gaps.
          </p>
        </div>
        <Activity className="h-5 w-5 text-primary" />
      </div>
      <div className="grid grid-cols-3 gap-3 mt-4 text-sm">
        <div><div className="text-muted-foreground">Queue</div><div className="font-semibold">{queueDepth}</div></div>
        <div><div className="text-muted-foreground">Sources / week</div><div className="font-semibold">{sourcesThisWeek} / 1,000</div></div>
        <div><div className="text-muted-foreground">Gaps closed</div><div className="font-semibold">{gapsClosed}</div></div>
      </div>
      <div className="flex gap-2 mt-4">
        <Button size="sm" onClick={onRunNow}><RefreshCw className="h-4 w-4 mr-1" />Run now</Button>
        {active ? (
          <Button size="sm" variant="outline" onClick={onPause}><Pause className="h-4 w-4 mr-1" />Pause</Button>
        ) : (
          <Button size="sm" variant="outline" onClick={onResume}><Play className="h-4 w-4 mr-1" />Resume</Button>
        )}
      </div>
    </Card>
  );
}
