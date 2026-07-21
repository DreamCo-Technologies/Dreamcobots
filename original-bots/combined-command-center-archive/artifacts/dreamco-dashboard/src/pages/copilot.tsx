import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useListCopilotPrs,
  getListCopilotPrsQueryKey,
  requestCopilotRewrite,
} from "@workspace/api-client-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Bot,
  CheckCircle2,
  XCircle,
  ExternalLink,
  RefreshCw,
  GitPullRequest,
} from "lucide-react";

export default function Copilot() {
  const qc = useQueryClient();
  const { data: prs, isLoading, refetch } = useListCopilotPrs({
    query: { queryKey: getListCopilotPrsQueryKey() },
  });
  const [pending, setPending] = useState<number | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const total = prs?.length ?? 0;
  const compliant = prs?.filter((p) => p.contractCompliant).length ?? 0;
  const mergeable = prs?.filter((p) => p.mergeable === true).length ?? 0;

  async function onRewrite(prNumber: number) {
    setPending(prNumber);
    setToast(null);
    try {
      const r = await requestCopilotRewrite(prNumber);
      setToast(`Rewrite issue #${r.issueNumber} opened`);
      qc.invalidateQueries({ queryKey: getListCopilotPrsQueryKey() });
    } catch (err) {
      setToast(`Failed to request rewrite: ${(err as Error).message}`);
    } finally {
      setPending(null);
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-mono font-bold tracking-tight text-foreground uppercase flex items-center gap-3">
          <Bot className="h-8 w-8 text-primary" />
          Copilot_Collab
        </h1>
        <p className="text-muted-foreground font-mono text-sm uppercase tracking-wider">
          Open PRs: {total} // Contract-Compliant: {compliant} // Mergeable: {mergeable}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <Button
          variant="outline"
          size="sm"
          className="font-mono"
          onClick={() => refetch()}
        >
          <RefreshCw className="h-3.5 w-3.5 mr-2" />
          Refresh
        </Button>
        {toast && (
          <span className="text-xs font-mono text-primary">{toast}</span>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24 w-full rounded-md" />
          ))}
        </div>
      ) : total === 0 ? (
        <Card className="border-border/40 bg-card/50 backdrop-blur">
          <CardContent className="p-10 text-center">
            <p className="font-mono text-sm text-muted-foreground">
              No open Copilot PRs found in Dreamcobots.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {prs?.map((pr) => (
            <Card
              key={pr.number}
              className="border-border/40 bg-card/50 backdrop-blur hover:border-primary/40 transition-colors"
            >
              <CardContent className="p-5">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <GitPullRequest className="h-4 w-4 text-primary shrink-0" />
                      <span className="font-mono text-xs text-muted-foreground">
                        #{pr.number}
                      </span>
                      <span className="font-mono text-xs text-muted-foreground">
                        @{pr.author}
                      </span>
                      {pr.contractCompliant ? (
                        <Badge className="bg-primary/10 text-primary border-primary/30 font-mono text-[10px] uppercase">
                          <CheckCircle2 className="h-3 w-3 mr-1" /> Compliant
                        </Badge>
                      ) : (
                        <Badge className="bg-destructive/10 text-destructive border-destructive/30 font-mono text-[10px] uppercase">
                          <XCircle className="h-3 w-3 mr-1" /> Non-compliant
                        </Badge>
                      )}
                      {pr.mergeable === true && (
                        <Badge className="bg-blue-500/10 text-blue-400 border-blue-500/30 font-mono text-[10px] uppercase">
                          Mergeable
                        </Badge>
                      )}
                      {pr.mergeable === false && (
                        <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/30 font-mono text-[10px] uppercase">
                          Conflicts
                        </Badge>
                      )}
                    </div>
                    <h3 className="font-mono font-bold text-sm text-foreground truncate">
                      {pr.title}
                    </h3>
                    <p className="font-mono text-xs text-muted-foreground mt-1">
                      {pr.complianceReason}
                    </p>
                    {pr.touchedDirs.length > 0 && (
                      <p className="font-mono text-[11px] text-muted-foreground mt-2">
                        Touched bot dirs:{" "}
                        <span className="text-foreground">
                          {pr.touchedDirs.join(", ")}
                        </span>
                      </p>
                    )}
                  </div>
                  <div className="flex flex-row md:flex-col gap-2 shrink-0">
                    <Button
                      asChild
                      variant="outline"
                      size="sm"
                      className="font-mono"
                    >
                      <a href={pr.url} target="_blank" rel="noreferrer">
                        <ExternalLink className="h-3.5 w-3.5 mr-2" />
                        View PR
                      </a>
                    </Button>
                    {!pr.contractCompliant && (
                      <Button
                        size="sm"
                        className="font-mono"
                        disabled={pending === pr.number}
                        onClick={() => onRewrite(pr.number)}
                      >
                        {pending === pr.number
                          ? "Requesting…"
                          : "Rewrite to contract"}
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
