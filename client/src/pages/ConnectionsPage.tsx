import { useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  AlertTriangle,
  Check,
  Copy,
  Globe,
  Key,
  Link2,
  MessageCircle,
  Monitor,
  Phone,
  Plug,
  Power,
  PowerOff,
  Radio,
  RefreshCw,
  Send,
  Shield,
  Smartphone,
  Tv,
  Gamepad2,
  Video,
  Webhook,
  Wifi,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { PlatformConnection } from "@shared/schema";

const PLATFORMS = [
  { id: "telegram", label: "Telegram", icon: Send, description: "Text-based control via Telegram bot. Send commands, receive alerts, manage bots.", color: "text-blue-400" },
  { id: "slack", label: "Slack", icon: MessageCircle, description: "Full Slack workspace integration. Channels per division, workflow triggers.", color: "text-purple-400" },
  { id: "discord", label: "Discord", icon: Radio, description: "Discord server bot for community management and real-time control.", color: "text-indigo-400" },
  { id: "sms", label: "SMS / Phone", icon: Phone, description: "SMS-based control from any phone. Kill switch, alerts, quick commands.", color: "text-green-400" },
  { id: "webhook", label: "Webhooks", icon: Webhook, description: "Custom webhook endpoints for real-time event notifications.", color: "text-orange-400" },
  { id: "api", label: "REST API", icon: Globe, description: "Full API access for custom integrations. Works with any platform.", color: "text-cyan-400" },
  { id: "zoom", label: "Zoom", icon: Video, description: "Zoom meeting bot integration for live presentations and reports.", color: "text-blue-500" },
  { id: "roku", label: "Roku / TV", icon: Tv, description: "Roku and smart TV dashboard for empire monitoring on any screen.", color: "text-purple-500" },
  { id: "mobile", label: "Mobile App", icon: Smartphone, description: "Progressive web app optimized for phones and tablets.", color: "text-green-500" },
  { id: "gaming", label: "Gaming Console", icon: Gamepad2, description: "Game console browser access for Xbox, PlayStation, Switch.", color: "text-red-400" },
];

function generateApiKey() {
  return "dco_" + Array.from(crypto.getRandomValues(new Uint8Array(24)))
    .map(b => b.toString(16).padStart(2, "0")).join("");
}

function generateWebhookUrl(platform: string) {
  const host = window.location.origin;
  return `${host}/api/webhooks/${platform}/${crypto.randomUUID().slice(0, 8)}`;
}

export default function ConnectionsPage() {
  const { toast } = useToast();
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<typeof PLATFORMS[0] | null>(null);

  const connectionsQuery = useQuery<PlatformConnection[]>({
    queryKey: ["/api/platform-connections"],
  });

  const killSwitchQuery = useQuery<{ enabled: boolean; updatedAt: string }>({
    queryKey: ["/api/kill-switch"],
  });

  const createConnection = useMutation({
    mutationFn: async (data: any) => {
      const res = await apiRequest("POST", "/api/platform-connections", data);
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/platform-connections"] });
      setConnectDialogOpen(false);
      toast({ title: "Platform connected", description: "Connection created successfully." });
    },
  });

  const toggleKillSwitch = useMutation({
    mutationFn: async (enabled: boolean) => {
      const res = await apiRequest("POST", "/api/kill-switch", { enabled });
      return res.json();
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ["/api/kill-switch"] });
      toast({
        title: data.enabled ? "KILL SWITCH ACTIVATED" : "Kill switch deactivated",
        description: data.enabled ? "All bot operations have been paused." : "Bot operations resumed.",
        variant: data.enabled ? "destructive" : "default",
      });
    },
  });

  const deleteConnection = useMutation({
    mutationFn: async (id: number) => {
      await apiRequest("DELETE", `/api/platform-connections/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/platform-connections"] });
      toast({ title: "Disconnected", description: "Platform connection removed." });
    },
  });

  const connections = connectionsQuery.data ?? [];
  const killSwitchEnabled = killSwitchQuery.data?.enabled ?? false;

  const handleConnect = (platform: typeof PLATFORMS[0]) => {
    setSelectedPlatform(platform);
    setConnectDialogOpen(true);
  };

  const handleConfirmConnect = () => {
    if (!selectedPlatform) return;
    createConnection.mutate({
      platform: selectedPlatform.id,
      name: selectedPlatform.label,
      webhookUrl: generateWebhookUrl(selectedPlatform.id),
      apiKey: generateApiKey(),
      status: "connected",
      config: {},
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({ title: "Copied", description: "Copied to clipboard." });
  };

  const getConnectionForPlatform = (platformId: string) => {
    return connections.find(c => c.platform === platformId);
  };

  return (
    <AppShell>
      <Seo title="Connections - DreamCo Empire OS" description="Multi-platform access and kill switch controls" />
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight" data-testid="text-connections-title">Connections & Control</h1>
            <p className="text-muted-foreground mt-1">Multi-platform access, kill switch, and integration controls</p>
          </div>
          <Badge variant="outline" className="gap-1">
            <Wifi className="h-3 w-3" />
            {connections.filter(c => c.status === "connected").length} Active
          </Badge>
        </div>

        {killSwitchEnabled && (
          <Card className="border-destructive bg-destructive/10">
            <CardContent className="p-4 flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              <div className="flex-1">
                <p className="font-semibold text-destructive" data-testid="text-kill-switch-warning">KILL SWITCH ACTIVE - All bot operations paused</p>
                <p className="text-sm text-muted-foreground">Deactivate the kill switch to resume operations.</p>
              </div>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => toggleKillSwitch.mutate(false)}
                disabled={toggleKillSwitch.isPending}
                data-testid="button-deactivate-kill-switch"
              >
                <Power className="h-4 w-4 mr-1" /> Resume
              </Button>
            </CardContent>
          </Card>
        )}

        <Tabs defaultValue="platforms">
          <TabsList>
            <TabsTrigger value="platforms" data-testid="tab-platforms">Platforms</TabsTrigger>
            <TabsTrigger value="kill-switch" data-testid="tab-kill-switch">Kill Switch</TabsTrigger>
            <TabsTrigger value="api-keys" data-testid="tab-api-keys">API Keys</TabsTrigger>
          </TabsList>

          <TabsContent value="platforms" className="space-y-4 mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {PLATFORMS.map((platform) => {
                const conn = getConnectionForPlatform(platform.id);
                const Icon = platform.icon;
                return (
                  <Card key={platform.id} data-testid={`card-platform-${platform.id}`} className="relative overflow-hidden">
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div className={cn("p-2 rounded-lg bg-muted", platform.color)}>
                            <Icon className="h-5 w-5" />
                          </div>
                          <div>
                            <h3 className="font-semibold" data-testid={`text-platform-name-${platform.id}`}>{platform.label}</h3>
                            <p className="text-sm text-muted-foreground mt-1">{platform.description}</p>
                          </div>
                        </div>
                        <Badge variant={conn ? "default" : "outline"} className={cn(conn ? "bg-green-500/15 text-green-500 border-green-500/20" : "")}>
                          {conn ? "Connected" : "Available"}
                        </Badge>
                      </div>

                      <div className="mt-4 flex gap-2">
                        {conn ? (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => copyToClipboard(conn.webhookUrl)}
                              data-testid={`button-copy-webhook-${platform.id}`}
                            >
                              <Copy className="h-3 w-3 mr-1" /> Webhook URL
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => copyToClipboard(conn.apiKey)}
                              data-testid={`button-copy-key-${platform.id}`}
                            >
                              <Key className="h-3 w-3 mr-1" /> API Key
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-destructive"
                              onClick={() => deleteConnection.mutate(conn.id)}
                              data-testid={`button-disconnect-${platform.id}`}
                            >
                              Disconnect
                            </Button>
                          </>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => handleConnect(platform)}
                            data-testid={`button-connect-${platform.id}`}
                          >
                            <Plug className="h-3 w-3 mr-1" /> Connect
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          <TabsContent value="kill-switch" className="space-y-4 mt-6">
            <Card data-testid="card-kill-switch">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PowerOff className="h-5 w-5 text-destructive" />
                  Emergency Kill Switch
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="text-muted-foreground">
                  The kill switch immediately pauses all bot operations, task execution, and automated workflows. 
                  Use this for emergency situations. Accessible from any device including phones.
                </p>

                <div className="flex items-center justify-between p-6 rounded-lg border-2 border-dashed">
                  <div className="flex items-center gap-4">
                    <div className={cn("p-4 rounded-full", killSwitchEnabled ? "bg-destructive/20" : "bg-muted")}>
                      {killSwitchEnabled ? (
                        <PowerOff className="h-8 w-8 text-destructive" />
                      ) : (
                        <Power className="h-8 w-8 text-green-500" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold" data-testid="text-kill-switch-status">
                        {killSwitchEnabled ? "SYSTEM PAUSED" : "System Active"}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {killSwitchEnabled 
                          ? "All operations are currently paused" 
                          : "All bots and workflows are running normally"}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Label htmlFor="kill-switch-toggle" className="text-sm font-medium">
                      {killSwitchEnabled ? "Deactivate" : "Activate"}
                    </Label>
                    <Switch
                      id="kill-switch-toggle"
                      checked={killSwitchEnabled}
                      onCheckedChange={(checked) => toggleKillSwitch.mutate(checked)}
                      disabled={toggleKillSwitch.isPending}
                      data-testid="switch-kill-switch"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Smartphone className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
                      <h4 className="font-semibold text-sm">Phone Access</h4>
                      <p className="text-xs text-muted-foreground mt-1">Toggle from any mobile browser</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Globe className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
                      <h4 className="font-semibold text-sm">API Access</h4>
                      <p className="text-xs text-muted-foreground mt-1">POST /api/kill-switch</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <Send className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
                      <h4 className="font-semibold text-sm">Telegram</h4>
                      <p className="text-xs text-muted-foreground mt-1">/kill command via bot</p>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api-keys" className="space-y-4 mt-6">
            <Card data-testid="card-api-keys">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="h-5 w-5" />
                  Active API Keys & Webhooks
                </CardTitle>
              </CardHeader>
              <CardContent>
                {connections.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8" data-testid="text-no-connections">
                    No active connections. Connect a platform to get API keys.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {connections.map((conn) => {
                      const platform = PLATFORMS.find(p => p.id === conn.platform);
                      const Icon = platform?.icon ?? Globe;
                      return (
                        <div key={conn.id} className="flex items-center gap-3 p-3 rounded-lg border" data-testid={`row-connection-${conn.id}`}>
                          <Icon className={cn("h-4 w-4", platform?.color)} />
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm">{conn.name}</p>
                            <p className="text-xs text-muted-foreground truncate font-mono">{conn.webhookUrl}</p>
                          </div>
                          <Badge variant="outline" className="text-xs">
                            {conn.status}
                          </Badge>
                          <Button size="sm" variant="ghost" onClick={() => copyToClipboard(conn.apiKey)}>
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 flex items-center gap-3">
                <Shield className="h-4 w-4 text-primary flex-shrink-0" />
                <p className="text-sm text-muted-foreground">
                  All API keys are encrypted. Low to zero API costs - you'll be notified before any charges apply. Same pricing as Replit.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      <Dialog open={connectDialogOpen} onOpenChange={setConnectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedPlatform && <selectedPlatform.icon className={cn("h-5 w-5", selectedPlatform.color)} />}
              Connect {selectedPlatform?.label}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">{selectedPlatform?.description}</p>
            <div className="space-y-2">
              <Label>Webhook URL (auto-generated)</Label>
              <Input readOnly value={selectedPlatform ? generateWebhookUrl(selectedPlatform.id) : ""} className="font-mono text-xs" />
            </div>
            <div className="space-y-2">
              <Label>API Key (auto-generated)</Label>
              <Input readOnly value="Will be generated on connect" className="font-mono text-xs" />
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setConnectDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleConfirmConnect} disabled={createConnection.isPending} data-testid="button-confirm-connect">
                <Plug className="h-4 w-4 mr-1" /> Connect
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
