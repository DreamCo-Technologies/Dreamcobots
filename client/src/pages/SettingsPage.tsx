import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { useAutonomyMode, useSetAutonomyMode } from "@/hooks/use-empire";
import { useQuery } from "@tanstack/react-query";
import {
  Settings, User, Shield, Globe, Bell, Palette, Database, Zap,
  CreditCard, Key, Moon, Sun, Monitor, Download, Trash2, Copy,
  CheckCircle2, AlertCircle, ExternalLink, RefreshCw, Lock,
  Wifi, WifiOff, BrainCircuit, DollarSign, Languages,
} from "lucide-react";
import { cn } from "@/lib/utils";

const THEMES = [
  { id: "light", label: "Light", icon: Sun },
  { id: "dark", label: "Dark", icon: Moon },
  { id: "system", label: "System", icon: Monitor },
];

const AUTONOMY_OPTIONS = [
  { value: "guided", label: "Guided", desc: "All actions require your approval", color: "text-blue-500", badge: "Safe" },
  { value: "semi-autonomous", label: "Semi-Auto", desc: "Low-risk actions execute automatically", color: "text-amber-500", badge: "Balanced" },
  { value: "full-autonomy", label: "Full Auto", desc: "Bots operate independently", color: "text-green-500", badge: "Power" },
];

const CURRENCIES = [
  { code: "USD", name: "US Dollar", symbol: "$" },
  { code: "EUR", name: "Euro", symbol: "€" },
  { code: "GBP", name: "British Pound", symbol: "£" },
  { code: "JPY", name: "Japanese Yen", symbol: "¥" },
  { code: "BTC", name: "Bitcoin", symbol: "₿" },
  { code: "ETH", name: "Ethereum", symbol: "Ξ" },
  { code: "USDT", name: "Tether (USDT)", symbol: "₮" },
  { code: "SOL", name: "Solana", symbol: "◎" },
  { code: "BNB", name: "BNB", symbol: "BNB" },
  { code: "CAD", name: "Canadian Dollar", symbol: "CA$" },
  { code: "AUD", name: "Australian Dollar", symbol: "A$" },
  { code: "INR", name: "Indian Rupee", symbol: "₹" },
  { code: "CNY", name: "Chinese Yuan", symbol: "¥" },
  { code: "MXN", name: "Mexican Peso", symbol: "MX$" },
  { code: "BRL", name: "Brazilian Real", symbol: "R$" },
];

const LANGUAGES = [
  "English", "Spanish", "French", "German", "Portuguese", "Japanese",
  "Chinese (Simplified)", "Chinese (Traditional)", "Korean", "Arabic",
  "Hindi", "Italian", "Russian", "Dutch", "Turkish", "Swedish",
];

const INTEGRATIONS = [
  { name: "OpenAI", status: "connected", desc: "GPT-4.1-mini · Chat, code, and AI features" },
  { name: "Stripe", status: "partial", desc: "Add STRIPE_SECRET_KEY to enable billing" },
  { name: "GitHub", status: "connected", desc: "Repo access and trending intelligence" },
  { name: "ElevenLabs", status: "disconnected", desc: "Add ELEVENLABS_API_KEY for voice cloning" },
  { name: "Serper", status: "disconnected", desc: "Add SERPER_API_KEY for premium web search" },
];

export default function SettingsPage() {
  const { toast } = useToast();
  const autonomyQuery = useAutonomyMode();
  const setMode = useSetAutonomyMode();
  const currentMode = (autonomyQuery.data as any)?.mode ?? "guided";

  const [theme, setTheme] = useState("dark");
  const [currency, setCurrency] = useState("USD");
  const [language, setLanguage] = useState("English");
  const [notifications, setNotifications] = useState({ revenue: true, errors: true, tasks: true, updates: false });
  const [privacy, setPrivacy] = useState({ analytics: true, crashReports: true, dataSharing: false });
  const [profile, setProfile] = useState({ name: "DreamCo Owner", email: "", timezone: "UTC" });

  const { data: costs } = useQuery<any>({ queryKey: ["/api/costs/summary"] });

  function copySystemInfo() {
    const info = [
      "DreamCo Empire OS — System Info",
      `Autonomy Mode: ${currentMode}`,
      `Theme: ${theme}`,
      `Currency: ${currency}`,
      `Language: ${language}`,
      `Build: 1.0.0`,
    ].join("\n");
    navigator.clipboard.writeText(info);
    toast({ title: "System info copied" });
  }

  function exportSettings() {
    const data = JSON.stringify({ profile, notifications, privacy, theme, currency, language }, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `empire-os-settings-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast({ title: "Settings exported" });
  }

  return (
    <AppShell>
      <Seo title="Settings | DreamCo Empire OS" description="Configure your Empire OS — autonomy, appearance, integrations, privacy, and more." />

      <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl" data-testid="text-settings-title">Settings</h1>
            <p className="text-sm text-muted-foreground mt-1">Configure your Empire OS — autonomy, appearance, integrations & privacy</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={copySystemInfo} data-testid="button-copy-system-info">
              <Copy className="h-3.5 w-3.5 mr-1.5" /> Copy Info
            </Button>
            <Button variant="outline" size="sm" onClick={exportSettings} data-testid="button-export-settings">
              <Download className="h-3.5 w-3.5 mr-1.5" /> Export
            </Button>
          </div>
        </div>
      </div>

      <div className="p-5 md:p-8">
        <Tabs defaultValue="general">
          <TabsList className="flex flex-wrap h-auto gap-1 mb-6">
            <TabsTrigger value="general" data-testid="tab-settings-general"><User className="h-3.5 w-3.5 mr-1.5" />General</TabsTrigger>
            <TabsTrigger value="autonomy" data-testid="tab-settings-autonomy"><Zap className="h-3.5 w-3.5 mr-1.5" />Autonomy</TabsTrigger>
            <TabsTrigger value="appearance" data-testid="tab-settings-appearance"><Palette className="h-3.5 w-3.5 mr-1.5" />Appearance</TabsTrigger>
            <TabsTrigger value="integrations" data-testid="tab-settings-integrations"><Key className="h-3.5 w-3.5 mr-1.5" />Integrations</TabsTrigger>
            <TabsTrigger value="international" data-testid="tab-settings-international"><Globe className="h-3.5 w-3.5 mr-1.5" />International</TabsTrigger>
            <TabsTrigger value="notifications" data-testid="tab-settings-notifications"><Bell className="h-3.5 w-3.5 mr-1.5" />Notifications</TabsTrigger>
            <TabsTrigger value="privacy" data-testid="tab-settings-privacy"><Shield className="h-3.5 w-3.5 mr-1.5" />Privacy</TabsTrigger>
            <TabsTrigger value="data" data-testid="tab-settings-data"><Database className="h-3.5 w-3.5 mr-1.5" />Data</TabsTrigger>
          </TabsList>

          {/* GENERAL */}
          <TabsContent value="general" className="space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><User className="h-4 w-4" />Profile</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label>Display Name</Label>
                    <Input value={profile.name} onChange={e => setProfile(p => ({ ...p, name: e.target.value }))} className="mt-1.5" data-testid="input-profile-name" />
                  </div>
                  <div>
                    <Label>Email (optional)</Label>
                    <Input value={profile.email} onChange={e => setProfile(p => ({ ...p, email: e.target.value }))} placeholder="you@example.com" className="mt-1.5" data-testid="input-profile-email" />
                  </div>
                  <div>
                    <Label>Timezone</Label>
                    <Input value={profile.timezone} onChange={e => setProfile(p => ({ ...p, timezone: e.target.value }))} placeholder="UTC" className="mt-1.5" data-testid="input-profile-timezone" />
                  </div>
                </div>
                <Button onClick={() => toast({ title: "Profile saved" })} data-testid="button-save-profile">Save Profile</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Settings className="h-4 w-4" />System Info</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {[
                    { label: "Version", value: "1.0.0" },
                    { label: "Bots", value: "1,051+" },
                    { label: "Divisions", value: "45" },
                    { label: "Autonomy", value: currentMode },
                    { label: "AI Model", value: "GPT-4.1-mini" },
                    { label: "Database", value: "PostgreSQL (Neon)" },
                  ].map(item => (
                    <div key={item.label} className="rounded-xl border border-border/60 bg-card/60 p-3">
                      <p className="text-xs text-muted-foreground">{item.label}</p>
                      <p className="text-sm font-medium mt-0.5 capitalize">{item.value}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AUTONOMY */}
          <TabsContent value="autonomy" className="space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Zap className="h-4 w-4" />Autonomy Mode</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {AUTONOMY_OPTIONS.map(opt => (
                  <button
                    key={opt.value}
                    onClick={async () => {
                      await setMode.mutateAsync(opt.value as "guided" | "semi-autonomous" | "full-autonomy");
                      toast({ title: `Autonomy set to ${opt.label}` });
                    }}
                    className={cn(
                      "w-full flex items-center gap-4 rounded-xl border p-4 text-left transition-all",
                      currentMode === opt.value
                        ? "border-primary/50 bg-primary/8 ring-2 ring-primary/20"
                        : "border-border/60 bg-card/60 hover:bg-card"
                    )}
                    data-testid={`autonomy-option-${opt.value}`}
                  >
                    <div className={cn("h-3 w-3 rounded-full flex-shrink-0", opt.value === "guided" ? "bg-blue-500" : opt.value === "semi-autonomous" ? "bg-amber-500" : "bg-green-500")} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{opt.label}</span>
                        <Badge variant="outline" className="text-[10px]">{opt.badge}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{opt.desc}</p>
                    </div>
                    {currentMode === opt.value && <CheckCircle2 className="h-4 w-4 text-primary flex-shrink-0" />}
                  </button>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* APPEARANCE */}
          <TabsContent value="appearance" className="space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Palette className="h-4 w-4" />Theme</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-3">
                  {THEMES.map(t => {
                    const Icon = t.icon;
                    return (
                      <button
                        key={t.id}
                        onClick={() => { setTheme(t.id); toast({ title: `Theme: ${t.label}` }); }}
                        className={cn(
                          "flex flex-col items-center gap-2 rounded-xl border p-4 transition-all",
                          theme === t.id ? "border-primary/50 bg-primary/8 ring-2 ring-primary/20" : "border-border/60 bg-card/60 hover:bg-card"
                        )}
                        data-testid={`theme-option-${t.id}`}
                      >
                        <Icon className="h-5 w-5" />
                        <span className="text-sm font-medium">{t.label}</span>
                        {theme === t.id && <CheckCircle2 className="h-3.5 w-3.5 text-primary" />}
                      </button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* INTEGRATIONS */}
          <TabsContent value="integrations" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Key className="h-4 w-4" />API Integrations
                  <Badge variant="secondary" className="ml-auto">{INTEGRATIONS.filter(i => i.status === "connected").length}/{INTEGRATIONS.length} connected</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {INTEGRATIONS.map(int => (
                  <div key={int.name} className={cn(
                    "flex items-center gap-3 rounded-xl border p-3",
                    int.status === "connected" ? "border-green-500/30 bg-green-500/5" : int.status === "partial" ? "border-amber-500/30 bg-amber-500/5" : "border-border/60 bg-card/40"
                  )} data-testid={`integration-${int.name.toLowerCase()}`}>
                    <div className={cn("h-2.5 w-2.5 rounded-full flex-shrink-0", int.status === "connected" ? "bg-green-500" : int.status === "partial" ? "bg-amber-500" : "bg-muted-foreground")} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">{int.name}</span>
                        <Badge variant="outline" className="text-[10px]">{int.status}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{int.desc}</p>
                    </div>
                    {int.status !== "connected" && (
                      <Button variant="outline" size="sm" className="text-xs" onClick={() => toast({ title: `Configure ${int.name}`, description: "Add the API key as a DreamCo secret." })} data-testid={`button-configure-${int.name.toLowerCase()}`}>
                        Configure
                      </Button>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><BrainCircuit className="h-4 w-4" />Buddy Bot</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="rounded-xl border border-primary/30 bg-primary/5 p-4 flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium">Buddy Bot is active</p>
                    <p className="text-xs text-muted-foreground mt-0.5">Elite CommandCore master coding AI. Routes all 1,051 bots' coding tasks. Access via sidebar or <code className="bg-card px-1 rounded">/buddy</code></p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* INTERNATIONAL */}
          <TabsContent value="international" className="space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><DollarSign className="h-4 w-4" />Currency</CardTitle></CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground mb-3">Select your preferred currency for deal analytics, revenue tracking, and payments</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-2">
                  {CURRENCIES.map(c => (
                    <button
                      key={c.code}
                      onClick={() => { setCurrency(c.code); toast({ title: `Currency: ${c.code}` }); }}
                      className={cn(
                        "flex flex-col items-center rounded-xl border p-3 text-center transition-all",
                        currency === c.code ? "border-primary/50 bg-primary/8 ring-2 ring-primary/20" : "border-border/60 bg-card/60 hover:bg-card"
                      )}
                      data-testid={`currency-${c.code.toLowerCase()}`}
                    >
                      <span className="text-lg font-bold">{c.symbol}</span>
                      <span className="text-xs font-medium mt-1">{c.code}</span>
                      <span className="text-[10px] text-muted-foreground">{c.name.split(" ")[0]}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Languages className="h-4 w-4" />Language</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 gap-2">
                  {LANGUAGES.map(lang => (
                    <button
                      key={lang}
                      onClick={() => { setLanguage(lang); toast({ title: `Language: ${lang}` }); }}
                      className={cn(
                        "rounded-xl border px-3 py-2 text-sm text-left transition-all",
                        language === lang ? "border-primary/50 bg-primary/8" : "border-border/60 bg-card/60 hover:bg-card"
                      )}
                      data-testid={`language-${lang.toLowerCase().replace(/\s+/g, "-").replace(/[()]/g, "")}`}
                    >
                      {lang}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* NOTIFICATIONS */}
          <TabsContent value="notifications" className="space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Bell className="h-4 w-4" />Notification Preferences</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {[
                  { key: "revenue", label: "Revenue Alerts", desc: "New revenue events and milestones" },
                  { key: "errors", label: "Error Alerts", desc: "System errors and auto-fix events" },
                  { key: "tasks", label: "Task Completions", desc: "When bots complete assigned tasks" },
                  { key: "updates", label: "System Updates", desc: "Empire OS updates and new features" },
                ].map(n => (
                  <div key={n.key} className="flex items-center justify-between py-2">
                    <div>
                      <p className="text-sm font-medium">{n.label}</p>
                      <p className="text-xs text-muted-foreground">{n.desc}</p>
                    </div>
                    <Switch
                      checked={notifications[n.key as keyof typeof notifications]}
                      onCheckedChange={v => { setNotifications(p => ({ ...p, [n.key]: v })); toast({ title: `${n.label} ${v ? "enabled" : "disabled"}` }); }}
                      data-testid={`toggle-notify-${n.key}`}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* PRIVACY */}
          <TabsContent value="privacy" className="space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Shield className="h-4 w-4" />Privacy Controls</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {[
                  { key: "analytics", label: "Usage Analytics", desc: "Help improve Empire OS by sharing anonymous usage data" },
                  { key: "crashReports", label: "Crash Reports", desc: "Automatically send error reports to help fix bugs" },
                  { key: "dataSharing", label: "Data Sharing", desc: "Share anonymized data with AI training improvements" },
                ].map(n => (
                  <div key={n.key} className="flex items-center justify-between py-2">
                    <div>
                      <p className="text-sm font-medium">{n.label}</p>
                      <p className="text-xs text-muted-foreground">{n.desc}</p>
                    </div>
                    <Switch
                      checked={privacy[n.key as keyof typeof privacy]}
                      onCheckedChange={v => { setPrivacy(p => ({ ...p, [n.key]: v })); toast({ title: `${n.label} ${v ? "enabled" : "disabled"}` }); }}
                      data-testid={`toggle-privacy-${n.key}`}
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* DATA */}
          <TabsContent value="data" className="space-y-6">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Database className="h-4 w-4" />Your Data</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">Download or manage all data tracked by Empire OS. Use it for your own analysis or sell it.</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    { label: "Export Bot Data", desc: "All 1,051 bot profiles and metrics", icon: Download },
                    { label: "Export Conversations", desc: "Full chat history with all bots", icon: Download },
                    { label: "Export Revenue Data", desc: "All revenue events and analytics", icon: Download },
                    { label: "Export Cost Data", desc: "API usage and cost tracking data", icon: Download },
                    { label: "Export Settings", desc: "Your current configuration", icon: Download },
                    { label: "Export Formulas", desc: "All division formulas and calculations", icon: Download },
                  ].map(item => {
                    const Icon = item.icon;
                    return (
                      <Button
                        key={item.label}
                        variant="outline"
                        className="h-auto py-3 px-4 justify-start flex-col items-start gap-1"
                        onClick={exportSettings}
                        data-testid={`button-export-${item.label.toLowerCase().replace(/\s+/g, "-")}`}
                      >
                        <div className="flex items-center gap-2 w-full">
                          <Icon className="h-4 w-4 text-primary" />
                          <span className="font-medium">{item.label}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">{item.desc}</span>
                      </Button>
                    );
                  })}
                </div>

                <Separator />
                <div>
                  <p className="text-sm font-medium text-destructive mb-2">Danger Zone</p>
                  <Button
                    variant="outline"
                    className="border-destructive/50 text-destructive hover:bg-destructive/10"
                    onClick={() => toast({ title: "Contact support to delete all data", variant: "destructive" })}
                    data-testid="button-delete-all-data"
                  >
                    <Trash2 className="h-4 w-4 mr-2" /> Request Data Deletion
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppShell>
  );
}
