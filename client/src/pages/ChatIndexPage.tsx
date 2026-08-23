import { useState, useEffect, useMemo } from "react";
import { useLocation } from "wouter";
import { useQuery, useMutation } from "@tanstack/react-query";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import MasterBotHomepageGrid from "@/components/MasterBotHomepageGrid";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { useCreateConversation } from "@/hooks/use-conversations";
import { useBots } from "@/hooks/use-bots";
import { useEmpireOverview } from "@/hooks/use-empire";
import { useToast } from "@/hooks/use-toast";
import {
  Send, Map, Hammer, Zap, GraduationCap, ShoppingCart, Search,
  Bot, Sparkles, Terminal, ChevronRight, Star, Building2,
  Code2, Cpu, DollarSign, Activity, Lock, CheckCircle2,
  CreditCard, Crown, Rocket, Loader2, Unlock,
} from "lucide-react";
import { useSubscriptionTier, isBotUnlocked } from "@/hooks/use-subscription";

// MasterBotHomepageGrid is mounted near the main homepage content below the primary chat/plan area.

type ChatMode = "plan" | "build" | "execute" | "teach";

const MODES: { id: ChatMode; label: string; icon: typeof Map; color: string; bg: string; desc: string; prompts: string[] }[] = [
  {
    id: "plan", label: "Plan", icon: Map, color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/30 hover:border-blue-400/60",
    desc: "Strategy & roadmaps",
    prompts: ["Map out a 90-day revenue plan for my AI-powered SaaS.","Design the architecture for an autonomous content empire.","Break my business idea into phases with revenue milestones.","Create a competitive analysis of the top 10 players in my niche."],
  },
  {
    id: "build", label: "Build", icon: Hammer, color: "text-amber-400", bg: "bg-amber-500/10 border-amber-500/30 hover:border-amber-400/60",
    desc: "Create & implement",
    prompts: ["Build an automation pipeline that generates passive income.","Help me create a full landing page for my AI product launch.","Set up an automated lead generation system for my business.","Design a bot workflow that handles customer onboarding end-to-end."],
  },
  {
    id: "execute", label: "Execute", icon: Zap, color: "text-green-400", bg: "bg-green-500/10 border-green-500/30 hover:border-green-400/60",
    desc: "Take action & results",
    prompts: ["Write 5 high-converting email sequences for my product launch.","Generate a week of social media content for my AI startup.","Create a pitch deck outline that closes investors.","Draft a partnership proposal for a strategic alliance."],
  },
  {
    id: "teach", label: "Teach", icon: GraduationCap, color: "text-purple-400", bg: "bg-purple-500/10 border-purple-500/30 hover:border-purple-400/60",
    desc: "Learn & master skills",
    prompts: ["Teach me how to use AI to automate my entire business workflow.","Explain prompt engineering like I'm a beginner entrepreneur.","Walk me through building my first revenue-generating bot.","Show me the top money-making strategies using AI tools today."],
  },
];

const CODE_LINES = [
  { t: 0, text: "// DreamCo Empire OS — Live Bot Monitor", cls: "text-slate-500" },
  { t: 200, text: "import { EmpireOS } from '@dreamco/core';", cls: "text-blue-400" },
  { t: 400, text: "", cls: "" },
  { t: 600, text: "const empire = new EmpireOS({", cls: "text-slate-200" },
  { t: 700, text: "  bots: 1051,", cls: "text-emerald-400" },
  { t: 800, text: "  divisions: 65,", cls: "text-emerald-400" },
  { t: 900, text: "  autonomy: 'full-auto',", cls: "text-yellow-400" },
  { t: 1000, text: "  architecture: '65-masterbots',", cls: "text-purple-400" },
  { t: 1100, text: "});", cls: "text-slate-200" },
  { t: 1300, text: "", cls: "" },
  { t: 1400, text: "// MasterBot routing + benchmark gap closure", cls: "text-slate-500" },
  { t: 1600, text: "await empire.deploy({", cls: "text-slate-200" },
  { t: 1700, text: "  mode: 'benchmark-gap-closure',", cls: "text-yellow-400" },
  { t: 1800, text: "  routing: 'evidence-based',", cls: "text-blue-400" },
  { t: 1900, text: "  schedule: 'continuous',", cls: "text-emerald-400" },
  { t: 2000, text: "});", cls: "text-slate-200" },
  { t: 2200, text: "", cls: "" },
  { t: 2300, text: "// ✅ 65 MasterBot architecture online", cls: "text-emerald-500" },
];

function CodexPanel({ selectedBot }: { selectedBot: any }) {
  const [visibleLines, setVisibleLines] = useState(0);
  const [cursor, setCursor] = useState(true);
  useEffect(() => { setVisibleLines(0); const timers = CODE_LINES.map((line, idx) => setTimeout(() => setVisibleLines(idx + 1), line.t)); return () => timers.forEach(clearTimeout); }, []);
  useEffect(() => { const t = setInterval(() => setCursor(c => !c), 530); return () => clearInterval(t); }, []);
  return (<div className="h-full flex flex-col bg-[#0d1117] rounded-2xl border border-white/10 overflow-hidden shadow-2xl"><div className="flex items-center gap-2 px-4 py-3 border-b border-white/8 bg-[#161b22]"><div className="flex gap-1.5"><span className="h-3 w-3 rounded-full bg-red-500/80" /><span className="h-3 w-3 rounded-full bg-yellow-500/80" /><span className="h-3 w-3 rounded-full bg-green-500/80" /></div><div className="flex items-center gap-2 ml-2"><Code2 className="h-3.5 w-3.5 text-slate-400" /><span className="text-xs text-slate-400 font-mono">empire-os.ts</span></div><div className="ml-auto flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse" /><span className="text-[10px] text-green-400 font-mono">LIVE</span></div></div><ScrollArea className="flex-1"><div className="p-4 font-mono text-[13px] leading-6">{CODE_LINES.slice(0, visibleLines).map((line, i) => (<div key={i} className={cn("whitespace-pre", line.cls || "text-slate-300")}><span className="text-slate-600 select-none mr-4 text-[11px]">{String(i + 1).padStart(2, "0")}</span>{line.text}{i === visibleLines - 1 && visibleLines < CODE_LINES.length && (<span className={cn("inline-block w-2 h-4 bg-primary/80 ml-0.5 align-middle", cursor ? "opacity-100" : "opacity-0")} />)}</div>))}{visibleLines >= CODE_LINES.length && (<div className="text-slate-300"><span className="text-slate-600 select-none mr-4 text-[11px]">{String(CODE_LINES.length + 1).padStart(2, "0")}</span><span className={cn("inline-block w-2 h-4 bg-primary/80 ml-0.5 align-middle", cursor ? "opacity-100" : "opacity-0")} /></div>)}</div></ScrollArea>{selectedBot && (<div className="border-t border-white/8 bg-[#161b22] p-3"><div className="flex items-center gap-2 mb-2"><Terminal className="h-3 w-3 text-green-400" /><span className="text-[10px] font-mono text-green-400">ACTIVE BOT</span></div><div className="font-mono text-[11px] space-y-1"><div className="flex justify-between"><span className="text-slate-400">name:</span><span className="text-blue-300 truncate ml-2 max-w-[160px]">{selectedBot.displayName}</span></div><div className="flex justify-between"><span className="text-slate-400">division:</span><span className="text-emerald-300">{selectedBot.division}</span></div><div className="flex justify-between"><span className="text-slate-400">tier:</span><span className="text-yellow-300">{selectedBot.tier ?? "free"}</span></div><div className="flex justify-between"><span className="text-slate-400">status:</span><span className="text-green-400">● online</span></div></div></div>)}</div>);
}

const TIER_COLORS: Record<string, string> = { free: "bg-slate-500/20 text-slate-300 border-slate-500/30", pro: "bg-blue-500/20 text-blue-300 border-blue-500/30", elite: "bg-purple-500/20 text-purple-300 border-purple-500/30", enterprise: "bg-amber-500/20 text-amber-300 border-amber-500/30" };
const PLAN_META: Record<string, { icon: typeof Bot; color: string; highlight: boolean; perks: string[] }> = { free:{icon:Bot,color:"text-slate-400",highlight:false,perks:["5 bots","Guided mode","All 45 divisions","Community support"]},pro:{icon:Rocket,color:"text-blue-400",highlight:true,perks:["50 bots","Semi-auto mode","Advanced analytics","Priority API access"]},enterprise:{icon:Star,color:"text-amber-400",highlight:false,perks:["150 bots","Full autonomy","All 269 APIs","Dedicated support"]},elite:{icon:Crown,color:"text-purple-400",highlight:false,perks:["Unlimited bots","White-glove onboarding","Custom divisions","Dedicated infra"]} };

function PricingPlansTab() {
  const { toast } = useToast(); const [yearly, setYearly] = useState(false);
  const productsQuery = useQuery<{ products: any[]; syncing?: boolean; source?: string }>({ queryKey:["/api/stripe/products"], refetchInterval:(query)=>{const data=query.state.data;if(data&&(data.products.length>0||data.syncing===false))return false;return data?.syncing?4000:false;} });
  const checkoutMutation = useMutation({ mutationFn:async(priceId:string)=>{const res=await apiRequest("POST","/api/stripe/checkout",{priceId});return res.json();}, onSuccess:(data)=>{if(data?.url)window.location.href=data.url;else toast({title:"Checkout failed",description:"No checkout URL returned.",variant:"destructive"});}, onError:(err:any)=>toast({title:"Checkout failed",description:err?.message??"Something went wrong.",variant:"destructive"}) });
  const products=productsQuery.data?.products??[]; const tierOrder=["free","pro","enterprise","elite"]; const sorted=[...products].sort((a,b)=>tierOrder.indexOf(a.metadata?.tier??"")-tierOrder.indexOf(b.metadata?.tier??"")); const isSyncing=productsQuery.data?.syncing&&sorted.length===0;
  if(productsQuery.isLoading||isSyncing)return <div className="flex flex-col items-center gap-4 p-6"><div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full">{Array.from({length:4}).map((_,i)=><Skeleton key={i} className="h-56 rounded-2xl" />)}</div>{isSyncing&&<p className="text-sm text-muted-foreground flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin" />Pricing plans loading… checking again shortly</p>}</div>;
  if(sorted.length===0)return <div className="flex flex-col items-center justify-center py-16 gap-3 text-center"><CreditCard className="h-10 w-10 text-muted-foreground/40" /><p className="font-semibold">Stripe not connected yet</p><p className="text-sm text-muted-foreground max-w-xs">Add your <span className="font-mono text-xs bg-muted px-1 py-0.5 rounded">STRIPE_SECRET_KEY</span> and <span className="font-mono text-xs bg-muted px-1 py-0.5 rounded">STRIPE_PUBLISHABLE_KEY</span> environment secrets to enable live checkout.</p></div>;
  return <div className="p-6">Pricing plans</div>;
}

export default function ChatIndexPage() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const [mode, setMode] = useState<ChatMode>("plan");
  const [input, setInput] = useState("");
  const [buyOpen, setBuyOpen] = useState(false);
  const { tier } = useSubscriptionTier();
  const { bots, totalBots, isLoading: botsLoading } = useBots();
  const { data: empire } = useEmpireOverview();
  const [selectedBotId, setSelectedBotId] = useState<string | null>(null);
  const selectedBot = useMemo(() => bots.find((b:any)=>b.id===selectedBotId) ?? bots[0], [bots, selectedBotId]);
  const createConversation = useCreateConversation();
  const modeConfig = MODES.find(m=>m.id===mode) ?? MODES[0];
  const handleSend = (prompt?: string) => { const text=(prompt??input).trim(); if(!text)return; createConversation.mutate({title:text.slice(0,80),firstMessage:text,mode}, {onSuccess:(data:any)=>{setInput("");navigate(`/chat/${data.id}`);}}); };
  const unlockedBots = bots.filter((b:any)=>isBotUnlocked(b,tier));
  return (<AppShell><Seo title="DreamCo — AI Empire OS" description="Build, automate, and scale with DreamCo's AI-powered empire operating system." /><div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8"><div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-6 min-h-[calc(100vh-8rem)]"><div className="flex flex-col gap-4"><div className="rounded-2xl border border-border/60 bg-card/50 backdrop-blur p-5 shadow-lg"><div className="flex items-start justify-between gap-4 mb-5"><div><div className="flex items-center gap-2 mb-1"><Sparkles className="h-5 w-5 text-primary" /><h1 className="text-xl font-bold">DreamCo Empire OS</h1></div><p className="text-sm text-muted-foreground">Your AI workforce. One command center. Infinite possibility.</p></div><Button variant="outline" size="sm" onClick={()=>navigate("/bots")} className="rounded-xl gap-2"><Bot className="h-4 w-4" />Browse Bots<Badge className="text-[9px] h-5 px-1.5">{totalBots}</Badge></Button></div><div className="grid grid-cols-4 gap-2">{MODES.map(m=>{const Icon=m.icon;const active=mode===m.id;return <button key={m.id} onClick={()=>setMode(m.id)} className={cn("flex flex-col items-center gap-1.5 rounded-xl border px-2 py-3 text-center transition-all",active?cn("border-primary/60 bg-primary/10 shadow-sm shadow-primary/20",m.color):cn("border-border/50 bg-card/40 text-muted-foreground",m.bg))}><Icon className={cn("h-4 w-4",active?m.color:"")} /><span className="text-xs font-semibold">{m.label}</span><span className="text-[10px] opacity-70 hidden sm:block">{m.desc}</span></button>})}</div><div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3">{modeConfig.prompts.map((prompt,i)=><button key={i} onClick={()=>handleSend(prompt)} className="text-left rounded-xl border border-border/50 bg-card/40 px-4 py-3 text-sm text-muted-foreground hover:text-foreground hover:border-primary/40 hover:bg-card/70 transition-all group"><span className="flex items-start gap-2"><ChevronRight className="h-3.5 w-3.5 mt-0.5 text-primary/60 flex-shrink-0 group-hover:text-primary transition-colors" /><span className="line-clamp-2">{prompt}</span></span></button>)}</div><div className="grid grid-cols-3 gap-3 mt-3">{[{icon:Cpu,label:"Active Bots",value:totalBots.toLocaleString()},{icon:Building2,label:"MasterBot Divisions",value:"65"},{icon:Activity,label:"Routing",value:"Evidence-based"}].map(({icon:Icon,label,value})=><div key={label} className="rounded-xl border border-border/40 bg-card/30 px-3 py-2.5 text-center"><Icon className="h-4 w-4 text-primary mx-auto mb-1" /><p className="text-base font-bold">{value}</p><p className="text-[10px] text-muted-foreground">{label}</p></div>)}</div><div className="mt-5"><MasterBotHomepageGrid /></div><div className="mt-5 rounded-2xl border border-border/60 bg-card/60 backdrop-blur p-3 shadow-lg"><div className="flex gap-2 items-end"><div className="flex-1"><textarea value={input} onChange={e=>setInput(e.target.value)} placeholder={`${modeConfig.desc} — describe your goal or pick a prompt above…`} rows={2} className="w-full resize-none rounded-xl border border-border/60 bg-background/50 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring/30 focus:border-primary/60 transition-all placeholder:text-muted-foreground/60" onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();handleSend();}}} data-testid="chat-input" /></div><Button onClick={()=>handleSend()} disabled={!input.trim()||createConversation.isPending} className="rounded-xl px-4 py-3 h-auto bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-md hover:shadow-lg hover:shadow-primary/25 hover:-translate-y-0.5 active:translate-y-0 transition-all flex-shrink-0" data-testid="send-btn"><Send className="h-4 w-4" /></Button></div><div className="flex items-center justify-between mt-2 px-1"><p className="text-[11px] text-muted-foreground">↵ Enter to send · Shift+Enter for newline</p><Button variant="outline" size="sm" onClick={()=>setBuyOpen(true)} className="rounded-xl text-xs border-primary/40 text-primary hover:bg-primary/10 hover:border-primary/70 gap-1.5 h-8 font-semibold" data-testid="buy-bots-btn"><ShoppingCart className="h-3.5 w-3.5" />Buy Bots<Badge className="ml-1 text-[9px] h-4 px-1 bg-primary/20 text-primary border-primary/30">{totalBots}</Badge></Button></div></div></div><div className="hidden xl:flex flex-col gap-4"><div className="flex-1 min-h-0"><CodexPanel selectedBot={selectedBot}/></div><div className="grid grid-cols-2 gap-2">{[{icon:ShoppingCart,label:"Buy Bots",sub:`${totalBots} available`,action:()=>setBuyOpen(true),primary:true},{icon:Star,label:"Bot Fleet",sub:"Manage all bots",action:()=>navigate("/bots"),primary:false},{icon:DollarSign,label:"Revenue",sub:"$18.4M ARR",action:()=>navigate("/revenue"),primary:false},{icon:Lock,label:"Full Auto",sub:"Autonomy on",action:()=>navigate("/autonomy"),primary:false}].map(({icon:Icon,label,sub,action,primary})=><button key={label} onClick={action} className={cn("flex items-center gap-3 rounded-xl border px-3 py-3 text-left transition-all hover:-translate-y-0.5",primary?"border-primary/40 bg-primary/8 hover:bg-primary/14 hover:border-primary/60":"border-border/50 bg-card/40 hover:bg-card/70 hover:border-border")} data-testid={`quick-${label.toLowerCase().replace(/\s/g,"-")}`}><span className={cn("inline-flex h-8 w-8 items-center justify-center rounded-lg flex-shrink-0",primary?"bg-primary/15":"bg-muted/60")}><Icon className={cn("h-4 w-4",primary?"text-primary":"text-muted-foreground")}/></span><div className="min-w-0"><p className={cn("text-sm font-semibold",primary?"text-primary":"")}>{label}</p><p className="text-[11px] text-muted-foreground">{sub}</p></div></button>)}</div></div></div></div></AppShell>);
}
