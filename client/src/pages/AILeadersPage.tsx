import { useMemo, useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { TOP_AI_COMPANIES } from "@shared/tool-belt";
import { useToast } from "@/hooks/use-toast";
import {
  Globe,
  Search,
  TrendingUp,
  Users,
  Heart,
  Shield,
  Sparkles,
  Building2,
  Trophy,
  ExternalLink,
  Copy,
  Star,
  Download,
} from "lucide-react";

const CATEGORIES = ["All", ...Array.from(new Set(TOP_AI_COMPANIES.map((c) => c.category)))];

function categoryColor(cat: string) {
  const map: Record<string, string> = {
    "Foundation Models": "bg-blue-500/10 text-blue-600 dark:text-blue-400",
    "Research & Models": "bg-violet-500/10 text-violet-600 dark:text-violet-400",
    Infrastructure: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    "Enterprise AI": "bg-green-500/10 text-green-600 dark:text-green-400",
    "Social AI": "bg-pink-500/10 text-pink-600 dark:text-pink-400",
    "AI Hardware": "bg-orange-500/10 text-orange-600 dark:text-orange-400",
    "AI Chips": "bg-red-500/10 text-red-600 dark:text-red-400",
    "Business AI": "bg-teal-500/10 text-teal-600 dark:text-teal-400",
    "AI Search": "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400",
    "Autonomous Vehicles": "bg-cyan-500/10 text-cyan-600 dark:text-cyan-400",
    Robotics: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    "AI Safety": "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400",
    "Healthcare AI": "bg-rose-500/10 text-rose-600 dark:text-rose-400",
    "Cloud AI": "bg-sky-500/10 text-sky-600 dark:text-sky-400",
    Defense: "bg-slate-500/10 text-slate-600 dark:text-slate-400",
    "AI Analytics": "bg-purple-500/10 text-purple-600 dark:text-purple-400",
    "AI Music": "bg-fuchsia-500/10 text-fuchsia-600 dark:text-fuchsia-400",
    "AI Writing": "bg-lime-500/10 text-lime-600 dark:text-lime-400",
    "AI Design": "bg-pink-500/10 text-pink-600 dark:text-pink-400",
    "AI Video": "bg-violet-500/10 text-violet-600 dark:text-violet-400",
    "AI Code": "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
  };
  return map[cat] ?? "bg-muted text-muted-foreground";
}

export default function AILeadersPage() {
  const { toast } = useToast();
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [starred, setStarred] = useState<Set<number>>(new Set());

  function toggleStar(rank: number, name: string) {
    setStarred(prev => {
      const next = new Set(prev);
      if (next.has(rank)) { next.delete(rank); toast({ title: `Unstarred ${name}` }); }
      else { next.add(rank); toast({ title: `Starred ${name}` }); }
      return next;
    });
  }

  function exportStarred() {
    const items = TOP_AI_COMPANIES.filter(c => starred.has(c.rank));
    if (!items.length) { toast({ title: "No starred companies", variant: "destructive" }); return; }
    const text = items.map(c => `#${c.rank} ${c.name} (${c.country}) — ${c.valuation}`).join("\n");
    navigator.clipboard.writeText(text);
    toast({ title: `Copied ${items.length} companies to clipboard` });
  }

  const filtered = useMemo(() => {
    return TOP_AI_COMPANIES.filter((c) => {
      const matchesSearch =
        !search ||
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        c.innovation.toLowerCase().includes(search.toLowerCase()) ||
        c.country.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = selectedCategory === "All" || c.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [search, selectedCategory]);

  const countryCount = useMemo(() => {
    return new Set(TOP_AI_COMPANIES.map((c) => c.country)).size;
  }, []);

  const categoryCount = useMemo(() => {
    return new Set(TOP_AI_COMPANIES.map((c) => c.category)).size;
  }, []);

  return (
    <AppShell>
      <Seo
        title="DreamCo Empire OS — AI Leaders & Advances"
        description="Top 100 AI companies shaping the future of technology and entrepreneurship."
      />

      <div className="buddy-appear">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div className="min-w-0">
            <h2 className="text-3xl md:text-4xl" data-testid="page-title">AI Leaders & Advances</h2>
            <p className="mt-2 text-sm text-muted-foreground max-w-2xl">
              The top 100 AI companies advancing innovation, creating jobs, and empowering entrepreneurs worldwide. You are the boss — AI and robots work for you.
            </p>
          </div>
        </div>

        <Card className="buddy-card rounded-3xl border-border/60 mt-6 p-5 md:p-6">
          <div className="flex items-start gap-4">
            <div className="h-12 w-12 rounded-2xl bg-primary/10 flex items-center justify-center shrink-0">
              <Heart className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-semibold" data-testid="mission-title">Our Mission</h3>
              <p className="mt-1 text-sm text-muted-foreground leading-relaxed">
                DreamCo Empire OS exists to make AI accessible to every person on the planet. We believe AI should reduce fear, not create it. Every human is an entrepreneur — AI and robots are your workforce. Together, we advance innovation, create opportunity, and build a future where technology serves humanity.
              </p>
            </div>
          </div>

          <Separator className="my-5" />

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="h-10 w-10 rounded-xl bg-blue-500/10 mx-auto flex items-center justify-center">
                <Building2 className="h-5 w-5 text-blue-500" />
              </div>
              <p className="mt-2 text-2xl font-bold" data-testid="stat-companies">100</p>
              <p className="text-xs text-muted-foreground">AI Companies</p>
            </div>
            <div className="text-center">
              <div className="h-10 w-10 rounded-xl bg-green-500/10 mx-auto flex items-center justify-center">
                <Globe className="h-5 w-5 text-green-500" />
              </div>
              <p className="mt-2 text-2xl font-bold" data-testid="stat-countries">{countryCount}</p>
              <p className="text-xs text-muted-foreground">Countries</p>
            </div>
            <div className="text-center">
              <div className="h-10 w-10 rounded-xl bg-purple-500/10 mx-auto flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-purple-500" />
              </div>
              <p className="mt-2 text-2xl font-bold" data-testid="stat-categories">{categoryCount}</p>
              <p className="text-xs text-muted-foreground">Categories</p>
            </div>
            <div className="text-center">
              <div className="h-10 w-10 rounded-xl bg-amber-500/10 mx-auto flex items-center justify-center">
                <Shield className="h-5 w-5 text-amber-500" />
              </div>
              <p className="mt-2 text-2xl font-bold" data-testid="stat-bots">857+</p>
              <p className="text-xs text-muted-foreground">Empire Bots</p>
            </div>
          </div>
        </Card>

        <Card className="buddy-card rounded-3xl border-border/60 mt-6 p-5 md:p-6">
          <div className="flex items-start gap-4 mb-4">
            <div className="h-10 w-10 rounded-2xl bg-amber-500/10 flex items-center justify-center shrink-0">
              <Users className="h-5 w-5 text-amber-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Human Impact</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                AI isn't replacing you — it's amplifying you. Every company below creates tools that make entrepreneurs more powerful.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="rounded-xl border border-border/60 bg-card/40 p-3">
              <p className="text-sm font-medium">You are the CEO</p>
              <p className="text-xs text-muted-foreground mt-1">AI bots are your employees. You set the vision, they execute. No coding required.</p>
            </div>
            <div className="rounded-xl border border-border/60 bg-card/40 p-3">
              <p className="text-sm font-medium">AI creates jobs</p>
              <p className="text-xs text-muted-foreground mt-1">Every AI tool below opens new career paths: prompt engineers, AI trainers, automation specialists.</p>
            </div>
            <div className="rounded-xl border border-border/60 bg-card/40 p-3">
              <p className="text-sm font-medium">Fear is outdated</p>
              <p className="text-xs text-muted-foreground mt-1">The best time to start using AI was yesterday. The second best time is now.</p>
            </div>
          </div>
        </Card>

        <div className="mt-6 space-y-4">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search companies, innovations, countries..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 rounded-xl"
                data-testid="search-companies"
              />
            </div>
            <Button variant="outline" size="sm" onClick={exportStarred} className="shrink-0" data-testid="button-export-starred">
              <Copy className="h-4 w-4 mr-2" />
              Copy Starred ({starred.size})
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="shrink-0"
              onClick={() => {
                const text = filtered.slice(0, 10).map(c => `#${c.rank} ${c.name} — ${c.valuation}`).join("\n");
                navigator.clipboard.writeText(text);
                toast({ title: "Copied top 10 companies" });
              }}
              data-testid="button-copy-top10"
            >
              <Download className="h-4 w-4 mr-2" />
              Copy Top 10
            </Button>
          </div>

          <div className="flex flex-wrap gap-2" data-testid="category-filters">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                  selectedCategory === cat
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-card/60 border border-border/60 text-muted-foreground hover:text-foreground hover:bg-card"
                }`}
                data-testid={`filter-${cat.toLowerCase().replace(/\s+/g, "-")}`}
              >
                {cat}
              </button>
            ))}
          </div>

          <p className="text-xs text-muted-foreground" data-testid="results-count">
            Showing {filtered.length} of {TOP_AI_COMPANIES.length} companies
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filtered.map((company) => (
              <Card
                key={company.rank}
                className="buddy-card rounded-2xl border-border/60 p-4 hover:shadow-md transition-all"
                data-testid={`company-card-${company.rank}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center shrink-0">
                      {company.rank <= 3 ? (
                        <Trophy className="h-4 w-4 text-amber-500" />
                      ) : (
                        <TrendingUp className="h-4 w-4 text-primary" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-sm truncate" data-testid={`company-name-${company.rank}`}>
                        #{company.rank} {company.name}
                      </p>
                      <p className="text-xs text-muted-foreground">{company.country}</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-[10px] shrink-0 rounded-lg">
                    {company.valuation}
                  </Badge>
                </div>

                <div className="mt-3">
                  <Badge className={`text-[10px] rounded-lg ${categoryColor(company.category)}`} variant="secondary">
                    {company.category}
                  </Badge>
                </div>

                <p className="mt-2 text-xs text-muted-foreground leading-relaxed line-clamp-2">
                  {company.innovation}
                </p>

                <Separator className="my-2" />

                <div className="flex items-start gap-1.5">
                  <Heart className="h-3 w-3 text-pink-500 mt-0.5 shrink-0" />
                  <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">
                    {company.impact}
                  </p>
                </div>
                <div className="flex gap-1.5 mt-3">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1 h-7 text-[11px] rounded-lg"
                    onClick={() => window.open(`https://www.google.com/search?q=${encodeURIComponent(company.name + " AI company")}`, "_blank")}
                    data-testid={`button-visit-${company.rank}`}
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    Visit
                  </Button>
                  <Button
                    size="sm"
                    variant={starred.has(company.rank) ? "default" : "outline"}
                    className="h-7 w-7 p-0 rounded-lg"
                    onClick={() => toggleStar(company.rank, company.name)}
                    data-testid={`button-star-${company.rank}`}
                  >
                    <Star className={`h-3 w-3 ${starred.has(company.rank) ? "fill-current" : ""}`} />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-7 w-7 p-0 rounded-lg"
                    onClick={() => {
                      navigator.clipboard.writeText(`#${company.rank} ${company.name} (${company.country}) — ${company.valuation}: ${company.innovation}`);
                      toast({ title: `Copied ${company.name}` });
                    }}
                    data-testid={`button-copy-company-${company.rank}`}
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          {filtered.length === 0 && (
            <div className="text-center py-12">
              <Globe className="h-10 w-10 text-muted-foreground mx-auto" />
              <p className="mt-3 text-sm font-medium">No companies found</p>
              <p className="text-xs text-muted-foreground mt-1">Try adjusting your search or filters.</p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
