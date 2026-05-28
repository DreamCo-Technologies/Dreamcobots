import { useState, useMemo } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  Network,
  Zap,
  Shield,
  Target,
  Activity,
  ChevronRight,
  Layers,
  BarChart3,
  Filter,
  ArrowRight,
} from "lucide-react";
import { MOE_ROUTING_RULES } from "@shared/bundles";
import { AI_PROVIDERS, AI_CATEGORIES } from "@shared/ai-ecosystem";

const PRIORITY_COLORS: Record<string, string> = {
  accuracy: "border-blue-500/40 bg-blue-500/10 text-blue-600 dark:text-blue-400",
  speed: "border-green-500/40 bg-green-500/10 text-green-600 dark:text-green-400",
  quality: "border-purple-500/40 bg-purple-500/10 text-purple-600 dark:text-purple-400",
  safety: "border-red-500/40 bg-red-500/10 text-red-600 dark:text-red-400",
  scale: "border-amber-500/40 bg-amber-500/10 text-amber-600 dark:text-amber-400",
  compliance: "border-teal-500/40 bg-teal-500/10 text-teal-600 dark:text-teal-400",
};

const PRIORITY_ICONS: Record<string, typeof Target> = {
  accuracy: Target,
  speed: Zap,
  quality: Activity,
  safety: Shield,
  scale: Layers,
  compliance: BarChart3,
};

const ALL_PRIORITIES = ["accuracy", "speed", "quality", "safety", "scale", "compliance"];

const FLOW_STEPS = [
  { label: "Task Input", icon: Layers },
  { label: "MOE Router", icon: Network },
  { label: "Priority Analysis", icon: Target },
  { label: "Provider Selection", icon: Filter },
  { label: "Output", icon: Zap },
];

export default function OrchestrationPage() {
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [costFilter, setCostFilter] = useState("all");

  const filtered = useMemo(() => {
    return MOE_ROUTING_RULES.filter((r) => {
      if (priorityFilter !== "all" && r.priority !== priorityFilter) return false;
      if (costFilter !== "all" && r.costTier !== costFilter) return false;
      return true;
    });
  }, [priorityFilter, costFilter]);

  const uniquePriorities = useMemo(
    () => new Set(MOE_ROUTING_RULES.map((r) => r.priority)),
    [],
  );

  const standardCount = MOE_ROUTING_RULES.filter((r) => r.costTier === "standard").length;
  const premiumCount = MOE_ROUTING_RULES.filter((r) => r.costTier === "premium").length;

  return (
    <AppShell>
      <Seo title="Model Orchestration Engine | DreamCo Empire OS" />
      <div className="space-y-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-md bg-primary/10 flex items-center justify-center">
              <Network className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-bold" data-testid="text-page-title">
                Model Orchestration Engine
              </h2>
              <p className="text-sm text-muted-foreground">
                Intelligent task routing across {AI_PROVIDERS.length} AI providers and {AI_CATEGORIES.length} categories
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-md border border-border/60 bg-muted/20 p-4">
          <p className="text-xs font-medium text-muted-foreground mb-3">Architecture Flow</p>
          <div className="flex flex-wrap items-center justify-center gap-2">
            {FLOW_STEPS.map((step, i) => {
              const Icon = step.icon;
              return (
                <div key={step.label} className="flex items-center gap-2">
                  <div
                    className="flex items-center gap-2 rounded-md border border-border/60 bg-card px-3 py-2"
                    data-testid={`flow-step-${i}`}
                  >
                    <Icon className="h-4 w-4 text-primary" />
                    <span className="text-xs font-medium whitespace-nowrap">{step.label}</span>
                  </div>
                  {i < FLOW_STEPS.length - 1 && (
                    <ArrowRight className="h-4 w-4 text-muted-foreground shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <Card data-testid="stat-total-rules">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center">
                  <Network className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Total Rules</p>
                  <p className="text-lg font-bold" data-testid="stat-total-rules-value">
                    {MOE_ROUTING_RULES.length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-priority-types">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-md bg-purple-500/10 flex items-center justify-center">
                  <Target className="h-4 w-4 text-purple-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Priority Types</p>
                  <p className="text-lg font-bold" data-testid="stat-priority-types-value">
                    {uniquePriorities.size}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-standard-routes">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-md bg-green-500/10 flex items-center justify-center">
                  <Zap className="h-4 w-4 text-green-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Standard Routes</p>
                  <p className="text-lg font-bold" data-testid="stat-standard-routes-value">
                    {standardCount}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card data-testid="stat-premium-routes">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-md bg-amber-500/10 flex items-center justify-center">
                  <Shield className="h-4 w-4 text-amber-500" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Premium Routes</p>
                  <p className="text-lg font-bold" data-testid="stat-premium-routes-value">
                    {premiumCount}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-3">
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Filter by Priority</p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={priorityFilter === "all" ? "default" : "outline"}
                size="sm"
                onClick={() => setPriorityFilter("all")}
                data-testid="filter-priority-all"
              >
                All
              </Button>
              {ALL_PRIORITIES.map((p) => (
                <Button
                  key={p}
                  variant={priorityFilter === p ? "default" : "outline"}
                  size="sm"
                  onClick={() => setPriorityFilter(p)}
                  data-testid={`filter-priority-${p}`}
                >
                  {p.charAt(0).toUpperCase() + p.slice(1)}
                </Button>
              ))}
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Filter by Cost Tier</p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={costFilter === "all" ? "default" : "outline"}
                size="sm"
                onClick={() => setCostFilter("all")}
                data-testid="filter-cost-all"
              >
                All
              </Button>
              <Button
                variant={costFilter === "standard" ? "default" : "outline"}
                size="sm"
                onClick={() => setCostFilter("standard")}
                data-testid="filter-cost-standard"
              >
                Standard
              </Button>
              <Button
                variant={costFilter === "premium" ? "default" : "outline"}
                size="sm"
                onClick={() => setCostFilter("premium")}
                data-testid="filter-cost-premium"
              >
                Premium
              </Button>
            </div>
          </div>
        </div>

        <div>
          <p className="text-sm text-muted-foreground mb-3">
            Showing {filtered.length} of {MOE_ROUTING_RULES.length} routing rules
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filtered.map((rule, idx) => {
              const PriorityIcon = PRIORITY_ICONS[rule.priority] ?? Target;
              return (
                <Card
                  key={rule.taskType}
                  className="hover-elevate"
                  data-testid={`card-rule-${idx}`}
                >
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex flex-wrap items-center justify-between gap-2">
                      <span className="flex items-center gap-2">
                        <PriorityIcon className="h-4 w-4 text-muted-foreground" />
                        {rule.taskType}
                      </span>
                      <div className="flex flex-wrap items-center gap-1.5">
                        <Badge
                          variant="outline"
                          className={cn("text-xs rounded-md", PRIORITY_COLORS[rule.priority])}
                          data-testid={`badge-priority-${rule.priority}-${idx}`}
                        >
                          {rule.priority}
                        </Badge>
                        <Badge
                          variant={rule.costTier === "premium" ? "default" : "outline"}
                          className="text-xs rounded-md"
                          data-testid={`badge-cost-${rule.costTier}-${idx}`}
                        >
                          {rule.costTier}
                        </Badge>
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-muted-foreground mb-2">Provider Chain</p>
                    <div className="flex flex-wrap items-center gap-1.5">
                      {rule.providers.map((provider, pIdx) => (
                        <div key={provider} className="flex items-center gap-1.5">
                          <Badge
                            variant="secondary"
                            className="text-xs rounded-md"
                            data-testid={`badge-provider-${idx}-${pIdx}`}
                          >
                            {provider}
                          </Badge>
                          {pIdx < rule.providers.length - 1 && (
                            <ChevronRight className="h-3 w-3 text-muted-foreground shrink-0" />
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
