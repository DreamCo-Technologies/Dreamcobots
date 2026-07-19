import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { useLocation } from "wouter";
import { useToast } from "@/hooks/use-toast";
import { useBots } from "@/hooks/use-bots";
import {
  Rocket,
  TrendingUp,
  Users,
  DollarSign,
  Target,
  FileText,
  Search,
  Scale,
  Palette,
  Globe,
  Calculator,
  UserCheck,
  Package,
  Contact,
  ClipboardList,
  Building2,
  MapPin,
  Banknote,
  MessageSquare,
  Copy,
  ExternalLink,
  Handshake,
  Plane,
  Brain,
  LineChart,
  BarChart3,
  Tag,
  Heart,
  CheckCircle2,
  ArrowUpRight,
  Sparkles,
  Briefcase,
  ShieldCheck,
  Layers,
  Bot,
  Zap,
} from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

const headerStats = [
  { label: "Businesses Launched", value: "2,847", icon: Rocket, change: "+124 this month" },
  { label: "Active Plans", value: "1,563", icon: ClipboardList, change: "89% completion rate" },
  { label: "Revenue Generated", value: "$18.4M", icon: DollarSign, change: "+22.3% growth" },
  { label: "Success Rate", value: "94.7%", icon: Target, change: "Top 5% industry" },
];

const startupTools = [
  {
    title: "Business Plan Generator",
    description: "AI-powered business plan creation with financial projections, market analysis, and investor-ready formatting.",
    icon: FileText,
    features: [
      "Executive summary auto-generation",
      "5-year financial projections",
      "Market sizing & TAM analysis",
      "Investor pitch deck export",
    ],
    metric: "1,247 plans created",
    status: "Popular",
    botSlug: "business-plan-bot",
  },
  {
    title: "Market Research",
    description: "Deep market intelligence with competitor tracking, trend analysis, and customer persona development.",
    icon: Search,
    features: [
      "Competitor landscape mapping",
      "Customer persona builder",
      "Industry trend reports",
      "SWOT analysis generator",
    ],
    metric: "893 reports generated",
    status: "Active",
    botSlug: "market-research-bot",
  },
  {
    title: "Legal Formation",
    description: "Streamlined business entity formation with document preparation and compliance guidance.",
    icon: Scale,
    options: ["LLC", "Corporation", "Sole Proprietorship"],
    features: [
      "State-specific filing assistance",
      "Operating agreement templates",
      "EIN registration guidance",
      "Compliance checklist",
    ],
    metric: "2,104 entities formed",
    status: "Essential",
    botSlug: "legal-bot",
  },
  {
    title: "Brand Identity",
    description: "Complete brand development toolkit with logo concepts, color palettes, and brand guideline generation.",
    icon: Palette,
    features: [
      "AI logo concept generator",
      "Color palette recommendations",
      "Brand voice & messaging",
      "Style guide creation",
    ],
    metric: "756 brands created",
    status: "Creative",
    botSlug: "brand-bot",
  },
  {
    title: "Domain & Website Setup",
    description: "Domain availability checking, website builder integration, and hosting configuration assistance.",
    icon: Globe,
    features: [
      "Domain name suggestions",
      "Availability & pricing check",
      "Website template selection",
      "SEO foundation setup",
    ],
    metric: "1,892 sites launched",
    status: "Technical",
    botSlug: "web-dev-bot",
  },
];

const runningTools = [
  {
    title: "Accounting & Bookkeeping",
    icon: Calculator,
    description: "Automated financial tracking with expense categorization, invoicing, and tax preparation.",
    metrics: { revenue: "$842K", expenses: "$341K", profit: "$501K", margin: "59.5%" },
    features: ["Auto-categorized transactions", "Invoice generation", "Tax estimation", "P&L statements"],
    botSlug: "finance-bot",
  },
  {
    title: "Employee Management",
    icon: UserCheck,
    description: "HR toolkit for payroll processing, time tracking, benefits administration, and team performance.",
    metrics: { employees: "48", payroll: "$286K/mo", satisfaction: "92%", retention: "96%" },
    features: ["Payroll automation", "Time & attendance", "Performance reviews", "Benefits admin"],
    botSlug: "hr-bot",
  },
  {
    title: "Inventory Tracking",
    icon: Package,
    description: "Real-time inventory management with automated reordering, supplier management, and demand forecasting.",
    metrics: { skus: "3,247", turnover: "8.2x", accuracy: "99.4%", value: "$1.2M" },
    features: ["Real-time stock levels", "Auto reorder points", "Supplier management", "Demand forecasting"],
    botSlug: "inventory-bot",
  },
  {
    title: "Customer Management (CRM)",
    icon: Contact,
    description: "Full-featured CRM with pipeline management, communication tracking, and customer segmentation.",
    metrics: { contacts: "12,480", deals: "847", conversion: "34%", ltv: "$2,840" },
    features: ["Pipeline management", "Email integration", "Customer segmentation", "Activity tracking"],
    botSlug: "crm-bot",
  },
  {
    title: "Task & Project Management",
    icon: ClipboardList,
    description: "Project planning and execution tools with team collaboration, milestones, and progress tracking.",
    metrics: { projects: "34", tasks: "1,247", completed: "89%", onTime: "94%" },
    features: ["Kanban boards", "Gantt charts", "Team assignments", "Milestone tracking"],
    botSlug: "pm-bot",
  },
];

const expansionTools = [
  {
    title: "Franchise Model Builder",
    icon: Building2,
    description: "Design and structure your franchise system with territory planning, fee structures, and operations manuals.",
    features: ["Territory mapping & planning", "Fee structure calculator", "Operations manual templates", "Franchisee qualification criteria"],
    stat: "142 models built",
    botSlug: "franchise-bot",
  },
  {
    title: "Market Expansion Analyzer",
    icon: MapPin,
    description: "Identify and evaluate new market opportunities with demographic analysis and competitive assessment.",
    features: ["Geographic opportunity scoring", "Demographic analysis", "Competitive density mapping", "Revenue potential estimation"],
    stat: "89 markets analyzed",
    botSlug: "expansion-bot",
  },
  {
    title: "Funding & Investor Matching",
    icon: Banknote,
    description: "Connect with investors and funding sources matched to your business stage, industry, and capital needs.",
    features: ["Investor database access", "Pitch deck optimization", "Valuation calculator", "Term sheet analysis"],
    stat: "$24M matched",
    botSlug: "investor-bot",
  },
  {
    title: "Partnership Finder",
    icon: Handshake,
    description: "Discover and evaluate strategic partnership opportunities with compatibility scoring and deal structuring.",
    features: ["Partner compatibility scoring", "Deal structure templates", "Due diligence checklists", "Integration planning"],
    stat: "367 partnerships formed",
    botSlug: "partnership-bot",
  },
  {
    title: "International Expansion Planner",
    icon: Plane,
    description: "Navigate international markets with localization guides, regulatory compliance, and cultural adaptation tools.",
    features: ["Market entry strategies", "Regulatory compliance guides", "Cultural adaptation tools", "Currency & tax planning"],
    stat: "28 countries covered",
    botSlug: "international-bot",
  },
];

const aiTools = [
  {
    title: "AI Business Advisor",
    icon: Bot,
    description: "24/7 AI-powered business consulting with strategic recommendations and actionable insights.",
    features: ["Strategic planning assistance", "Real-time Q&A support", "Industry-specific advice", "Growth strategy recommendations"],
    accuracy: "94%",
    queries: "48,293",
    botSlug: "advisor-bot",
  },
  {
    title: "Financial Forecasting",
    icon: LineChart,
    description: "Machine learning-driven financial projections with scenario modeling and risk assessment.",
    features: ["Revenue prediction models", "Cash flow forecasting", "Scenario analysis (best/worst/likely)", "Risk quantification"],
    accuracy: "91%",
    queries: "12,847",
    botSlug: "forecasting-bot",
  },
  {
    title: "Competitive Analysis",
    icon: BarChart3,
    description: "AI-powered competitor monitoring with market positioning insights and strategic gap analysis.",
    features: ["Real-time competitor tracking", "Market share estimation", "Feature comparison matrices", "Strategic gap identification"],
    accuracy: "89%",
    queries: "8,924",
    botSlug: "competitive-bot",
  },
  {
    title: "Pricing Optimization",
    icon: Tag,
    description: "Dynamic pricing recommendations using market data, competitor analysis, and demand elasticity modeling.",
    features: ["Price elasticity modeling", "Competitor price monitoring", "Bundle optimization", "A/B test recommendations"],
    accuracy: "92%",
    queries: "6,341",
    botSlug: "pricing-bot",
  },
  {
    title: "Customer Sentiment Analysis",
    icon: Heart,
    description: "Real-time customer feedback analysis across reviews, social media, and support interactions.",
    features: ["Multi-channel monitoring", "Sentiment trend tracking", "Topic extraction", "Actionable insight generation"],
    accuracy: "96%",
    queries: "34,102",
    botSlug: "sentiment-bot",
  },
];

export default function BusinessPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const { data: botsList } = useBots();

  const handleLaunch = async (slug: string, toolTitle: string) => {
    // Find the closest bot in the system
    const targetBot = botsList?.find(b => b.slug === slug) || botsList?.[0];

    if (targetBot) {
      try {
        const res = await apiRequest("POST", "/api/conversations", { title: `New ${toolTitle} Project` });
        const convo = await res.json();
        setLocation(`/c/${convo.id}?bot=${targetBot.slug}`);
      } catch (e) {
        toast({
          title: "Failed to launch",
          description: "Could not initialize tool conversation.",
          variant: "destructive"
        });
      }
    } else {
      toast({
        title: toolTitle,
        description: "Tool initializing. Our specialized AI is preparing your project workspace.",
      });
    }
  };

  const handleLearnMore = (toolTitle: string) => {
    toast({
      title: `About ${toolTitle}`,
      description: "This enterprise tool utilizes advanced DreamCo AI models to automate core business logic.",
    });
  };

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Business Launch Pad - DreamBizLaunch" description="Launch, run, and expand your business with AI-powered tools and intelligent automation." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-business-title">Business Launch Pad</h1>
              <p className="text-sm text-muted-foreground mt-1">Launch, run, and expand your business with AI-powered tools</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="rounded-full">
                <Sparkles className="h-3 w-3 mr-1.5 text-primary" />
                AI-Powered
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <ShieldCheck className="h-3 w-3 mr-1.5 text-green-500" />
                Enterprise Ready
              </Badge>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-8 buddy-stagger">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            {headerStats.map((stat) => (
              <Card key={stat.label} data-testid={`stat-${stat.label.toLowerCase().replace(/\s+/g, "-")}`}>
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
                    <Badge variant="outline" className="text-[9px] px-1 py-0 h-4 rounded-sm font-normal text-muted-foreground">Projected</Badge>
                  </div>
                  <stat.icon className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold tracking-tight">{stat.value}</p>
                  <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    <TrendingUp className="h-3 w-3 text-green-500" /> {stat.change}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Tabs defaultValue="start" data-testid="tabs-business">
            <TabsList className="w-full justify-start gap-1 flex-wrap" data-testid="tabs-list-business">
              <TabsTrigger value="start" data-testid="tab-start">
                <Rocket className="h-4 w-4 mr-1.5" />
                Start
              </TabsTrigger>
              <TabsTrigger value="run" data-testid="tab-run">
                <Briefcase className="h-4 w-4 mr-1.5" />
                Run
              </TabsTrigger>
              <TabsTrigger value="expand" data-testid="tab-expand">
                <Layers className="h-4 w-4 mr-1.5" />
                Expand
              </TabsTrigger>
              <TabsTrigger value="ai-tools" data-testid="tab-ai-tools">
                <Brain className="h-4 w-4 mr-1.5" />
                AI Tools
              </TabsTrigger>
            </TabsList>

            <TabsContent value="start" className="mt-6 space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {startupTools.map((tool) => (
                  <Card key={tool.title} data-testid={`card-start-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}>
                    <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <tool.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-base">{tool.title}</CardTitle>
                          <p className="text-xs text-muted-foreground mt-0.5">{tool.metric}</p>
                        </div>
                      </div>
                      <Badge variant="secondary" className="rounded-full text-[10px]">{tool.status}</Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">{tool.description}</p>
                      {tool.options && (
                        <div className="flex flex-wrap gap-2">
                          {tool.options.map((opt) => (
                            <Badge key={opt} variant="outline" className="rounded-full">{opt}</Badge>
                          ))}
                        </div>
                      )}
                      <ul className="space-y-1.5">
                        {tool.features.map((feature) => (
                          <li key={feature} className="flex items-center gap-2 text-sm">
                            <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                            <span className="text-muted-foreground">{feature}</span>
                          </li>
                        ))}
                      </ul>
                      <div className="flex flex-wrap items-center gap-2">
                        <Button
                          size="sm"
                          data-testid={`button-launch-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => handleLaunch(tool.botSlug, tool.title)}
                        >
                          <Zap className="h-3.5 w-3.5 mr-1.5" />
                          Launch Tool
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          data-testid={`button-chat-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => {
                            const { setLocation } = (window as any).__dreamLocation ?? {};
                            window.location.href = `/?bot=${tool.botSlug}`;
                          }}
                        >
                          <MessageSquare className="h-3.5 w-3.5 mr-1.5" />
                          Chat
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`button-copy-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => {
                            const text = `${tool.title}\n${tool.description}\nFeatures:\n${tool.features.map(f => `• ${f}`).join("\n")}`;
                            navigator.clipboard.writeText(text);
                            toast({ title: `Copied ${tool.title}` });
                          }}
                        >
                          <Copy className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          data-testid={`button-learn-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => handleLearnMore(tool.title)}
                        >
                          Learn More
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="run" className="mt-6 space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {runningTools.map((tool) => {
                  const metricEntries = Object.entries(tool.metrics);
                  return (
                    <Card key={tool.title} data-testid={`card-run-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}>
                      <CardHeader className="flex flex-row items-start gap-3 space-y-0">
                        <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <tool.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div className="min-w-0">
                          <CardTitle className="text-base">{tool.title}</CardTitle>
                          <p className="text-xs text-muted-foreground mt-0.5">{tool.description}</p>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                          {metricEntries.map(([key, value]) => (
                            <div key={key} className="p-2.5 rounded-lg border border-border/40 text-center relative">
                              <Badge variant="outline" className="absolute -top-1.5 -right-1 text-[8px] px-1 py-0 h-3 rounded-xs font-normal bg-card">Proj.</Badge>
                              <p className="text-lg font-bold">{value}</p>
                              <p className="text-[10px] text-muted-foreground capitalize">{key}</p>
                            </div>
                          ))}
                        </div>
                        <ul className="grid grid-cols-2 gap-1.5">
                          {tool.features.map((feature) => (
                            <li key={feature} className="flex items-center gap-2 text-sm">
                              <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                              <span className="text-muted-foreground">{feature}</span>
                            </li>
                          ))}
                        </ul>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            data-testid={`button-open-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                            onClick={() => handleLaunch(tool.botSlug, tool.title)}
                          >
                            Open Dashboard
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            data-testid={`button-settings-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                            onClick={() => handleLearnMore(`${tool.title} Settings`)}
                          >
                            Settings
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="expand" className="mt-6 space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {expansionTools.map((tool) => (
                  <Card key={tool.title} data-testid={`card-expand-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}>
                    <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <tool.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-base">{tool.title}</CardTitle>
                          <p className="text-xs text-muted-foreground mt-0.5">{tool.stat}</p>
                        </div>
                      </div>
                      <Badge variant="outline" className="rounded-full">
                        <ArrowUpRight className="h-3 w-3 mr-1" />
                        Growth
                      </Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">{tool.description}</p>
                      <ul className="space-y-1.5">
                        {tool.features.map((feature) => (
                          <li key={feature} className="flex items-center gap-2 text-sm">
                            <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                            <span className="text-muted-foreground">{feature}</span>
                          </li>
                        ))}
                      </ul>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          data-testid={`button-explore-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => handleLaunch(tool.botSlug, tool.title)}
                        >
                          <Rocket className="h-3.5 w-3.5 mr-1.5" />
                          Explore
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          data-testid={`button-details-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => handleLearnMore(`${tool.title} Details`)}
                        >
                          View Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="ai-tools" className="mt-6 space-y-4">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {aiTools.map((tool) => (
                  <Card key={tool.title} data-testid={`card-ai-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}>
                    <CardHeader className="flex flex-row items-start justify-between gap-2 space-y-0">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <tool.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-base">{tool.title}</CardTitle>
                          <p className="text-xs text-muted-foreground mt-0.5">{tool.queries} queries processed</p>
                        </div>
                      </div>
                      <Badge variant="secondary" className="rounded-full">
                        <Sparkles className="h-3 w-3 mr-1" />
                        {tool.accuracy} accuracy
                      </Badge>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">{tool.description}</p>
                      <div className="flex items-center gap-3">
                        <div className="flex-1">
                          <div className="flex items-center justify-between gap-2 mb-1">
                            <span className="text-xs text-muted-foreground">Model Confidence</span>
                            <span className="text-xs font-medium">{tool.accuracy}</span>
                          </div>
                          <Progress value={parseFloat(tool.accuracy)} className="h-1.5" />
                        </div>
                      </div>
                      <ul className="space-y-1.5">
                        {tool.features.map((feature) => (
                          <li key={feature} className="flex items-center gap-2 text-sm">
                            <CheckCircle2 className="h-3.5 w-3.5 text-green-500 flex-shrink-0" />
                            <span className="text-muted-foreground">{feature}</span>
                          </li>
                        ))}
                      </ul>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          data-testid={`button-activate-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => handleLaunch(tool.botSlug, tool.title)}
                        >
                          <Brain className="h-3.5 w-3.5 mr-1.5" />
                          Activate
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          data-testid={`button-config-${tool.title.toLowerCase().replace(/\s+/g, "-")}`}
                          onClick={() => handleLearnMore(`${tool.title} Configuration`)}
                        >
                          Configure
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppShell>
  );
}
