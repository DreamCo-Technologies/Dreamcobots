import { useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import {
  Clock,
  Download,
  Plus,
  RotateCcw,
  Save,
  Trash2,
} from "lucide-react";
import type { SystemSnapshot } from "@shared/schema";

export default function TimeCapsulePage() {
  const { toast } = useToast();
  const [label, setLabel] = useState("");

  const snapshotsQuery = useQuery<SystemSnapshot[]>({
    queryKey: ["/api/snapshots"],
  });

  const createSnapshot = useMutation({
    mutationFn: async (name: string) => {
      const res = await apiRequest("POST", "/api/snapshots", { name });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/snapshots"] });
      setLabel("");
      toast({ title: "Snapshot saved", description: "System state captured successfully." });
    },
    onError: () => {
      toast({ title: "Failed to save snapshot", variant: "destructive" });
    },
  });

  const deleteSnapshot = useMutation({
    mutationFn: async (id: number) => {
      await apiRequest("DELETE", `/api/snapshots/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/snapshots"] });
      toast({ title: "Snapshot deleted" });
    },
  });

  const snapshots = snapshotsQuery.data ?? [];

  return (
    <AppShell>
      <Seo title="Time Capsule | DreamCo Empire OS" description="Save and restore system states" />
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight" data-testid="text-time-capsule-title">Time Capsule</h1>
          <p className="text-muted-foreground text-sm mt-1">Save snapshots of your system state and restore them anytime</p>
        </div>

        <Card>
          <CardHeader className="pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <Save className="h-5 w-5 text-primary" />
              Create Snapshot
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-3">
              <Input
                placeholder="Snapshot label (e.g. Before major update)"
                value={label}
                onChange={(e) => setLabel(e.target.value)}
                className="flex-1"
                data-testid="input-snapshot-label"
              />
              <Button
                onClick={() => createSnapshot.mutate(label || `Snapshot ${new Date().toLocaleString()}`)}
                disabled={createSnapshot.isPending}
                data-testid="button-create-snapshot"
              >
                <Plus className="h-4 w-4 mr-1" />
                {createSnapshot.isPending ? "Saving..." : "Save Snapshot"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <div>
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            Saved Snapshots
            <Badge variant="secondary" className="rounded-full">{snapshots.length}</Badge>
          </h2>

          {snapshotsQuery.isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map(i => <Skeleton key={i} className="h-24" />)}
            </div>
          ) : snapshots.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <RotateCcw className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
                <p className="text-muted-foreground">No snapshots saved yet. Create one above to preserve your system state.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {snapshots.map((snap) => {
                const data = snap.snapshotData as any;
                return (
                  <Card key={snap.id} className="hover-elevate" data-testid={`card-snapshot-${snap.id}`}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <p className="font-medium">{snap.name}</p>
                          <div className="flex flex-wrap gap-2 mt-1.5">
                            <Badge variant="outline" className="text-xs">{data?.botCount ?? 0} bots</Badge>
                            <Badge variant="outline" className="text-xs">{data?.taskCount ?? 0} tasks</Badge>
                            <Badge variant="secondary" className="text-xs">
                              {new Date(snap.createdAt!).toLocaleString()}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex gap-2 flex-shrink-0">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => toast({ title: "Restore initiated", description: `Restoring system to "${snap.name}" state...` })}
                            data-testid={`button-restore-snapshot-${snap.id}`}
                          >
                            <RotateCcw className="h-3.5 w-3.5 mr-1" /> Restore
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-8 w-8"
                            onClick={() => deleteSnapshot.mutate(snap.id)}
                            data-testid={`button-delete-snapshot-${snap.id}`}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
