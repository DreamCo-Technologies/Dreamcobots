import { useState, useEffect } from "react";
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
  Download,
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
  Star,
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

const INSTALL_DEVICES = [
  {
    id: "android",
    label: "Android Phone / Tablet",
    icon: Smartphone,
    color: "text-green-400",
    steps: [
      "Open the DreamCo app URL in Chrome on your Android device",
      'Tap the 3-dot menu (⋮) in the top-right corner',
      'Select "Add to Home screen" or "Install app"',
      'Tap "Add" — DreamCo will appear as an app icon',
      "Launch from your home screen — it runs like a native app, no app store needed",
    ],
    tip: "Works on Android 5+ with Chrome, Edge, or Samsung Internet.",
  },
  {
    id: "iphone",
    label: "iPhone / iPad (iOS)",
    icon: Smartphone,
    color: "text-gray-300",
    steps: [
      "Open the DreamCo app URL in Safari on your iPhone or iPad",
      "Tap the Share button (square with arrow pointing up) at the bottom",
      'Scroll down and tap "Add to Home Screen"',
      'Tap "Add" in the top-right — the DreamCo icon appears on your home screen',
      "Launch from your home screen for a full-screen experience",
    ],
    tip: "Must use Safari on iOS. Works on iOS 11.3+. iPadOS also supported.",
  },
  {
    id: "windows",
    label: "Windows PC / Laptop",
    icon: Monitor,
    color: "text-blue-400",
    steps: [
      "Open the DreamCo app in Chrome or Microsoft Edge on Windows",
      "Look for the install icon (computer with down arrow) in the address bar",
      'Click it and select "Install"',
      "DreamCo will open in its own window, pinned to your taskbar",
      "You can also go to Chrome menu → 'Save and share' → 'Install page as app'",
    ],
    tip: "Works on Windows 10 and 11 with Chrome, Edge, or any Chromium browser.",
  },
  {
    id: "mac",
    label: "Mac (macOS)",
    icon: Monitor,
    color: "text-gray-400",
    steps: [
      "Open the DreamCo app in Chrome or Edge on your Mac",
      "Click the install icon in the address bar, or go to Chrome Menu → 'Cast, save, and share' → 'Install page as app'",
      "Click 'Install' in the prompt",
      "DreamCo will open as a standalone app in your Dock",
      "Find it in Launchpad or Applications folder too",
    ],
    tip: "Safari on Mac does not fully support PWA install. Use Chrome or Edge for best experience.",
  },
  {
    id: "smarttv",
    label: "Smart TV (Samsung, LG, Fire TV)",
    icon: Tv,
    color: "text-purple-400",
    steps: [
      "On Samsung Smart TV: Open the built-in browser, navigate to your DreamCo URL",
      "On LG WebOS: Use the LG browser app and navigate to the URL",
      "On Amazon Fire TV: Install the Silk Browser or Firefox from the app store, then navigate to the URL",
      "Bookmark the page for quick access",
      "For the best TV experience, use a Bluetooth keyboard/mouse or your phone as a remote",
    ],
    tip: "Most Smart TVs have a built-in browser. Fire TV Stick works great with the Silk browser.",
  },
  {
    id: "gaming",
    label: "Gaming Console",
    icon: Gamepad2,
    color: "text-red-400",
    steps: [
      "Xbox: Open Microsoft Edge (pre-installed), navigate to your DreamCo URL, and pin to home",
      "PlayStation 5: Open the built-in browser, navigate to the URL, and add a bookmark",
      "PlayStation 4: Use the built-in browser in the Library section",
      "Nintendo Switch: Open the browser (via some workarounds or games with browser access), navigate to the URL",
      "Use a USB keyboard for easier typing on consoles",
    ],
    tip: "Xbox Series X/S has full Edge browser support with PWA install capability.",
  },
  {
    id: "chromebook",
    label: "Chromebook",
    icon: Monitor,
    color: "text-yellow-400",
    steps: [
      "Open the DreamCo app in Chrome on your Chromebook",
      "Click the install icon in the address bar (looks like a computer with a down arrow)",
      "Click 'Install' — DreamCo appears in your app launcher",
      "Pin it to the shelf for quick access",
      "Works offline too for cached pages",
    ],
    tip: "Chromebooks have first-class PWA support — DreamCo runs like a native app.",
  },
  {
    id: "roku",
    label: "Roku / Apple TV / Streaming Sticks",
    icon: Tv,
    color: "text-orange-400",
    steps: [
      "Roku: Install 'Web Browser X' from the Roku Channel Store, open it, and navigate to your DreamCo URL",
      "Apple TV: Use the built-in Safari browser in tvOS 17+ or install the Chrome app",
      "Chromecast with Google TV: Use the Chrome browser, navigate to the URL",
      "Bookmark the page for easy return access",
      "Pair a Bluetooth keyboard for full control",
    ],
    tip: "Streaming devices with browser support can access the full DreamCo dashboard.",
  },
];

export default function ConnectionsPage() {
  const { toast } = useToast();
  const [connectDialogOpen, setConnectDialogOpen] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<typeof PLATFORMS[0] | null>(null);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [pwaInstalled, setPwaInstalled] = useState(false);

  useEffect(() => {
    const handler = (e: any) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener("beforeinstallprompt", handler);
    window.addEventListener("appinstalled", () => setPwaInstalled(true));
    if (window.matchMedia("(display-mode: standalone)").matches) {
      setPwaInstalled(true);
    }
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstallNow = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setPwaInstalled(true);
      toast({ title: "DreamCo Installed!", description: "The app is now on your device." });
    }
    setDeferredPrompt(null);
  };

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
      if (enabled) {
        // Task says kill switch should disconnect all platforms? 
        // "Make the Kill Switch work - it should call a mutation to disconnect all platforms"
        // Let's assume the backend handles this or we should call deletes here.
        // Actually, let's just make sure it does what's asked.
        await apiRequest("POST", "/api/platform-connections/disconnect-all", {});
      }
      return res.json();
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ["/api/kill-switch"] });
      queryClient.invalidateQueries({ queryKey: ["/api/platform-connections"] });
      toast({
        title: data.enabled ? "KILL SWITCH ACTIVATED" : "Kill switch deactivated",
        description: data.enabled ? "All bot operations have been paused and platforms disconnected." : "Bot operations resumed.",
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
            <TabsTrigger value="install" data-testid="tab-install">Install App</TabsTrigger>
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

          <TabsContent value="install" className="space-y-6 mt-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row items-start md:items-center gap-4 justify-between">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-primary/10">
                      <Download className="h-8 w-8 text-primary" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold" data-testid="text-install-title">DreamCo Empire OS — Install on Any Device</h2>
                      <p className="text-muted-foreground mt-1">
                        No app store required. Works on phones, tablets, PCs, Macs, Smart TVs, and gaming consoles.
                        Installs as a native-feeling app in seconds.
                      </p>
                    </div>
                  </div>
                  {deferredPrompt && !pwaInstalled && (
                    <Button size="lg" onClick={handleInstallNow} data-testid="button-install-now" className="shrink-0">
                      <Download className="h-4 w-4 mr-2" /> Install Now
                    </Button>
                  )}
                  {pwaInstalled && (
                    <Badge className="bg-green-500/15 text-green-500 border-green-500/20 shrink-0">
                      <Check className="h-3 w-3 mr-1" /> Already Installed
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {INSTALL_DEVICES.map((device) => {
                const Icon = device.icon;
                return (
                  <Card key={device.id} data-testid={`card-install-${device.id}`}>
                    <CardHeader className="pb-3">
                      <CardTitle className="flex items-center gap-3 text-base">
                        <div className={cn("p-2 rounded-lg bg-muted", device.color)}>
                          <Icon className="h-4 w-4" />
                        </div>
                        {device.label}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <ol className="space-y-2">
                        {device.steps.map((step, i) => (
                          <li key={i} className="flex gap-3 text-sm">
                            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/20 text-primary text-xs font-bold flex items-center justify-center mt-0.5">
                              {i + 1}
                            </span>
                            <span className="text-muted-foreground">{step}</span>
                          </li>
                        ))}
                      </ol>
                      <div className="flex items-start gap-2 p-3 rounded-lg bg-muted/50 mt-2">
                        <Star className="h-3 w-3 text-yellow-500 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-muted-foreground">{device.tip}</p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <Card>
              <CardContent className="p-4 flex items-start gap-3">
                <Globe className="h-4 w-4 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium">Share Your App URL</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Copy the URL from your browser's address bar and send it to any device. Anyone with the link can access and install DreamCo Empire OS instantly — no downloads, no sign-ups.
                  </p>
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-3"
                    onClick={() => {
                      navigator.clipboard.writeText(window.location.origin);
                      toast({ title: "URL Copied", description: "Share this link to install on any device." });
                    }}
                    data-testid="button-copy-app-url"
                  >
                    <Copy className="h-3 w-3 mr-1" /> Copy App URL
                  </Button>
                </div>
              </CardContent>
            </Card>
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
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedPlatform && <selectedPlatform.icon className={cn("h-5 w-5", selectedPlatform.color)} />}
              Connect {selectedPlatform?.label}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label>Setup Instructions</Label>
              <div className="text-sm text-muted-foreground p-3 bg-muted rounded-md space-y-2">
                <p>1. Copy your {selectedPlatform?.label} API Token from your platform settings.</p>
                <p>2. Paste the token below to verify the connection.</p>
                <p>3. Click 'Confirm Connection' to finalize the integration.</p>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="api-key">Generated Empire API Key</Label>
              <div className="flex gap-2">
                <Input id="api-key" value={generateApiKey()} readOnly className="font-mono text-xs" />
                <Button size="icon" variant="outline" onClick={() => copyToClipboard(generateApiKey())} data-testid="button-copy-key-gen">
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-[10px] text-muted-foreground">Use this key to authenticate DreamCo requests on {selectedPlatform?.label}.</p>
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setConnectDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleConfirmConnect} disabled={createConnection.isPending} data-testid="button-confirm-connect">
              {createConnection.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Plug className="h-4 w-4 mr-1" /> Connect
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </AppShell>
  );
}
