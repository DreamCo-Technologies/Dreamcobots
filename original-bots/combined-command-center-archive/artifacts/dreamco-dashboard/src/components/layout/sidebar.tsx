import { Link, useLocation } from "wouter";
import {
  Terminal,
  Activity,
  Bot,
  DollarSign,
  GitMerge,
  Network,
  GitPullRequest,
  LayoutGrid,
  Sparkles,
  PlayCircle,
  Brain,
  Zap,
  BarChart3,
  FlaskConical,
  GraduationCap,
  Globe,
  Store,
  Bitcoin,
  CreditCard,
  Rocket,
  Code2,
  Landmark,
  Bug,
  Tag,
  Plug,
  History,
  Wallet,
  Cpu,
  Atom,
  Clapperboard,
  ShieldCheck,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const navGroups: { label: string; items: { title: string; url: string; icon: typeof Activity }[] }[] = [
  {
    label: "Command",
    items: [
      { title: "Chat", url: "/chat", icon: Terminal },
      { title: "Empire HQ", url: "/", icon: Activity },
      { title: "Divisions", url: "/divisions", icon: Network },
      { title: "Bot Fleet", url: "/bots", icon: Bot },
      { title: "GH Actions", url: "/actions", icon: PlayCircle },
      { title: "Orchestration", url: "/orchestration", icon: GitPullRequest },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { title: "Deal Analyzer", url: "/deals", icon: BarChart3 },
      { title: "Formula Vault", url: "/formulas", icon: FlaskConical },
      { title: "Learning Matrix", url: "/learning-matrix", icon: GraduationCap },
      { title: "AI Sources", url: "/sources", icon: Network },
      { title: "Buddy Memory", url: "/memory", icon: Brain },
      { title: "Quantum", url: "/quantum", icon: Atom },
      { title: "Studio", url: "/studio", icon: Clapperboard },
      { title: "Cloning Consent", url: "/consent", icon: ShieldCheck },
      { title: "AI Leaders", url: "/ai-leaders", icon: Brain },
      { title: "AI Models Hub", url: "/ai-models", icon: LayoutGrid },
      { title: "AI Ecosystem", url: "/ecosystem", icon: Globe },
      { title: "Vibe Engine", url: "/vibe", icon: Sparkles },
      { title: "Capabilities", url: "/capabilities", icon: Cpu },
    ],
  },
  {
    label: "Commerce",
    items: [
      { title: "Marketplace", url: "/marketplace", icon: Store },
      { title: "Crypto", url: "/crypto", icon: Bitcoin },
      { title: "Payments", url: "/payments", icon: CreditCard },
      { title: "Biz Launch", url: "/business", icon: Rocket },
      { title: "Loans & Deals", url: "/loans", icon: Landmark },
      { title: "Revenue", url: "/revenue", icon: DollarSign },
      { title: "Pricing", url: "/pricing", icon: Tag },
    ],
  },
  {
    label: "Operations",
    items: [
      { title: "Code Lab", url: "/code-lab", icon: Code2 },
      { title: "Debug Intel", url: "/debug", icon: Bug },
      { title: "Repositories", url: "/github", icon: GitMerge },
      { title: "Connections", url: "/connections", icon: Plug },
      { title: "Time Capsule", url: "/time-capsule", icon: History },
      { title: "Cost Tracking", url: "/costs", icon: Wallet },
      { title: "Autonomy", url: "/autonomy", icon: Cpu },
    ],
  },
];

export function AppSidebar() {
  const [location] = useLocation();

  return (
    <Sidebar variant="sidebar" className="border-r border-border/40 bg-sidebar">
      <SidebarHeader className="h-14 flex items-center px-4 border-b border-border/40 justify-center">
        <div className="flex items-center gap-2 text-primary">
          <Zap className="h-5 w-5 fill-primary" />
          <span className="font-mono font-bold tracking-widest text-sm uppercase">DREAMCO_OS</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        {navGroups.map((group) => (
          <SidebarGroup key={group.label}>
            <SidebarGroupLabel className="text-xs font-mono uppercase text-muted-foreground tracking-wider mb-1">{group.label}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {group.items.map((item) => {
                  const isActive = location === item.url;
                  return (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton asChild isActive={isActive} tooltip={item.title}>
                        <Link href={item.url} className={`flex items-center gap-3 font-mono text-sm ${isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"}`}>
                          <item.icon className="h-4 w-4" />
                          <span>{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
    </Sidebar>
  );
}
