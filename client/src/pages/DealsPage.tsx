import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState, useMemo } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import {
  calculateRealEstate,
  calculateCarFlip,
  compareDeals,
  STATUS_CONFIG,
  DEFAULT_RE_INPUTS,
  DEFAULT_CAR_INPUTS,
  type RealEstateInputs,
  type CarFlipInputs,
} from "@shared/deal-calculations";
import type { Deal } from "@shared/schema";
import {
  ArrowDown,
  ArrowUp,
  BarChart3,
  Building2,
  Calculator,
  Car,
  Check,
  CircleDollarSign,
  Clock,
  Flame,
  Gauge,
  Home,
  Loader2,
  PieChart,
  Plus,
  Save,
  Scale,
  Shield,
  Target,
  TrendingUp,
  Trash2,
  X,
  Zap,
} from "lucide-react";

function NumberField({ label, value, onChange, prefix, suffix, testId }: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  prefix?: string;
  suffix?: string;
  testId: string;
}) {
  return (
    <div>
      <Label className="text-xs text-muted-foreground">{label}</Label>
      <div className="relative mt-1">
        {prefix && <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">{prefix}</span>}
        <Input
          type="number"
          value={value}
          onChange={e => onChange(Number(e.target.value) || 0)}
          className={cn("text-sm", prefix && "pl-6", suffix && "pr-10")}
          data-testid={testId}
        />
        {suffix && <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">{suffix}</span>}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.red;
  return (
    <Badge
      variant="outline"
      className={cn(
        "rounded-full text-xs font-bold",
        status === "green" && "border-green-500/40 bg-green-500/10 text-green-600 dark:text-green-400",
        status === "yellow" && "border-yellow-500/40 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400",
        status === "red" && "border-red-500/40 bg-red-500/10 text-red-600 dark:text-red-400",
      )}
      data-testid={`badge-status-${status}`}
    >
      {status === "green" && <Check className="h-3 w-3 mr-1" />}
      {status === "yellow" && <Shield className="h-3 w-3 mr-1" />}
      {status === "red" && <X className="h-3 w-3 mr-1" />}
      {cfg.label}
    </Badge>
  );
}

function MetricCard({ label, value, icon: Icon, trend, testId }: {
  label: string;
  value: string;
  icon: typeof CircleDollarSign;
  trend?: "up" | "down" | "neutral";
  testId: string;
}) {
  return (
    <Card data-testid={testId}>
      <CardContent className="p-4">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-lg font-bold" data-testid={`${testId}-value`}>{value}</p>
            </div>
          </div>
          {trend && trend !== "neutral" && (
            <div className={cn("flex items-center gap-0.5 text-xs", trend === "up" ? "text-green-500" : "text-red-500")}>
              {trend === "up" ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function RealEstateCalculator({ onSave }: { onSave: (name: string, inputs: RealEstateInputs) => void }) {
  const [inputs, setInputs] = useState<RealEstateInputs>({ ...DEFAULT_RE_INPUTS });
  const [dealName, setDealName] = useState("");

  const results = useMemo(() => calculateRealEstate(inputs), [inputs]);

  const update = (field: keyof RealEstateInputs) => (value: number) => {
    setInputs(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-xl bg-[rgb(59_130_246)]/15 flex items-center justify-center">
            <Home className="h-5 w-5 text-[rgb(59_130_246)]" />
          </div>
          <div>
            <h3 className="text-lg font-bold">Real Estate Flip Analyzer</h3>
            <p className="text-xs text-muted-foreground">MAO, Net Profit, ROI, Safety Score</p>
          </div>
        </div>
        <StatusBadge status={results.status} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Calculator className="h-4 w-4" /> Deal Inputs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <NumberField label="After Repair Value (ARV)" value={inputs.arv} onChange={update("arv")} prefix="$" testId="input-arv" />
            <NumberField label="Purchase Price" value={inputs.purchasePrice} onChange={update("purchasePrice")} prefix="$" testId="input-purchase-price" />
            <NumberField label="Repair Costs" value={inputs.repairCosts} onChange={update("repairCosts")} prefix="$" testId="input-repair-costs" />
            <div className="grid grid-cols-2 gap-3">
              <NumberField label="Closing (Buy)" value={inputs.closingCostsBuy} onChange={update("closingCostsBuy")} prefix="$" testId="input-closing-buy" />
              <NumberField label="Closing (Sell)" value={inputs.closingCostsSell} onChange={update("closingCostsSell")} prefix="$" testId="input-closing-sell" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <NumberField label="Holding $/mo" value={inputs.holdingCostMonthly} onChange={update("holdingCostMonthly")} prefix="$" testId="input-holding-monthly" />
              <NumberField label="Hold Months" value={inputs.holdingMonths} onChange={update("holdingMonths")} testId="input-hold-months" />
            </div>
            <NumberField label="Agent Fees" value={inputs.agentFees} onChange={update("agentFees")} prefix="$" testId="input-agent-fees" />
            <NumberField label="Financing Costs" value={inputs.financingCosts} onChange={update("financingCosts")} prefix="$" testId="input-financing" />
            <NumberField label="Cash Invested (Down Payment)" value={inputs.cashInvested} onChange={update("cashInvested")} prefix="$" testId="input-cash-invested" />
            <NumberField label="Days Held" value={inputs.daysHeld} onChange={update("daysHeld")} suffix="days" testId="input-days-held" />
            <div className="grid grid-cols-3 gap-3">
              <NumberField label="Market Growth %" value={inputs.marketGrowthPct} onChange={update("marketGrowthPct")} suffix="%" testId="input-market-growth" />
              <NumberField label="Rehab Risk" value={inputs.rehabRiskMultiplier} onChange={update("rehabRiskMultiplier")} testId="input-rehab-risk" />
              <NumberField label="DOM Risk" value={inputs.daysOnMarketRisk} onChange={update("daysOnMarketRisk")} testId="input-dom-risk" />
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card className={cn(
            "border-2",
            results.status === "green" && "border-green-500/30",
            results.status === "yellow" && "border-yellow-500/30",
            results.status === "red" && "border-red-500/30",
          )}>
            <CardHeader>
              <CardTitle className="text-sm flex items-center justify-between gap-2">
                <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4" /> Results</span>
                <StatusBadge status={results.status} />
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                <p className="text-xs text-muted-foreground mb-1">Maximum Allowable Offer (70% Rule)</p>
                <p className="text-2xl font-bold" data-testid="result-mao">${results.mao.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {inputs.purchasePrice <= results.mao
                    ? "Purchase price is within MAO range"
                    : "Purchase price EXCEEDS MAO - high risk"}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Net Profit</p>
                  <p className={cn("text-xl font-bold", results.netProfit >= 0 ? "text-green-500" : "text-red-500")} data-testid="result-net-profit">
                    ${results.netProfit.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">ROI</p>
                  <p className={cn("text-xl font-bold", results.roi >= 20 ? "text-green-500" : results.roi >= 10 ? "text-yellow-500" : "text-red-500")} data-testid="result-roi">
                    {results.roi}%
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Cash-on-Cash</p>
                  <p className="text-lg font-bold" data-testid="result-coc">{results.cashOnCash}%</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Leverage ROI</p>
                  <p className="text-lg font-bold" data-testid="result-leverage">{results.leverageRoi}%</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Daily Profit</p>
                  <p className="text-lg font-bold" data-testid="result-daily-profit">${results.dailyProfit.toLocaleString()}/day</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Capital Efficiency</p>
                  <p className="text-lg font-bold" data-testid="result-cap-eff">{results.capitalEfficiency.toFixed(4)}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Safety Score</p>
                  <p className={cn("text-lg font-bold", results.safetyScore >= 15 ? "text-green-500" : results.safetyScore >= 5 ? "text-yellow-500" : "text-red-500")} data-testid="result-safety">
                    {results.safetyScore}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Equity Margin</p>
                  <p className="text-lg font-bold" data-testid="result-equity">{results.equityMarginPct}%</p>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                <p className="text-xs text-muted-foreground">Total Expenses</p>
                <p className="text-sm font-semibold">${results.totalExpenses.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground mt-1">Holding: ${results.totalHoldingCosts.toLocaleString()} ({inputs.holdingMonths} months)</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Deal name (e.g. 123 Main St Flip)"
                  value={dealName}
                  onChange={e => setDealName(e.target.value)}
                  className="text-sm"
                  data-testid="input-deal-name-re"
                />
                <Button
                  onClick={() => { if (dealName.trim()) { onSave(dealName.trim(), inputs); setDealName(""); } }}
                  disabled={!dealName.trim()}
                  data-testid="btn-save-deal-re"
                >
                  <Save className="h-4 w-4 mr-2" /> Save
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function CarFlipCalculator({ onSave }: { onSave: (name: string, inputs: CarFlipInputs) => void }) {
  const [inputs, setInputs] = useState<CarFlipInputs>({ ...DEFAULT_CAR_INPUTS });
  const [dealName, setDealName] = useState("");

  const results = useMemo(() => calculateCarFlip(inputs), [inputs]);

  const update = (field: keyof CarFlipInputs) => (value: number) => {
    setInputs(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-xl bg-[rgb(245_158_11)]/15 flex items-center justify-center">
            <Car className="h-5 w-5 text-[rgb(245_158_11)]" />
          </div>
          <div>
            <h3 className="text-lg font-bold">Car Flip Analyzer</h3>
            <p className="text-xs text-muted-foreground">Profit, ROI, Daily Velocity, Capital Turn</p>
          </div>
        </div>
        <StatusBadge status={results.status} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Calculator className="h-4 w-4" /> Deal Inputs
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <NumberField label="Purchase Price" value={inputs.purchasePrice} onChange={update("purchasePrice")} prefix="$" testId="input-car-purchase" />
            <NumberField label="Expected Sale Price" value={inputs.expectedSalePrice} onChange={update("expectedSalePrice")} prefix="$" testId="input-car-sale" />
            <NumberField label="Repair Costs" value={inputs.repairCosts} onChange={update("repairCosts")} prefix="$" testId="input-car-repairs" />
            <div className="grid grid-cols-2 gap-3">
              <NumberField label="Auction Fees" value={inputs.auctionFees} onChange={update("auctionFees")} prefix="$" testId="input-car-auction" />
              <NumberField label="Transport" value={inputs.transportCosts} onChange={update("transportCosts")} prefix="$" testId="input-car-transport" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <NumberField label="Title/Registration" value={inputs.titleRegistration} onChange={update("titleRegistration")} prefix="$" testId="input-car-title" />
              <NumberField label="Reconditioning" value={inputs.reconditioning} onChange={update("reconditioning")} prefix="$" testId="input-car-recond" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <NumberField label="Advertising" value={inputs.advertising} onChange={update("advertising")} prefix="$" testId="input-car-ads" />
              <NumberField label="Taxes" value={inputs.taxes} onChange={update("taxes")} prefix="$" testId="input-car-taxes" />
            </div>
            <NumberField label="Cash Invested" value={inputs.cashInvested} onChange={update("cashInvested")} prefix="$" testId="input-car-cash" />
            <NumberField label="Days Held" value={inputs.daysHeld} onChange={update("daysHeld")} suffix="days" testId="input-car-days" />
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card className={cn(
            "border-2",
            results.status === "green" && "border-green-500/30",
            results.status === "yellow" && "border-yellow-500/30",
            results.status === "red" && "border-red-500/30",
          )}>
            <CardHeader>
              <CardTitle className="text-sm flex items-center justify-between gap-2">
                <span className="flex items-center gap-2"><BarChart3 className="h-4 w-4" /> Results</span>
                <StatusBadge status={results.status} />
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                <p className="text-xs text-muted-foreground mb-1">Max Purchase Price (25% target margin)</p>
                <p className="text-2xl font-bold" data-testid="result-car-max-purchase">${results.maxPurchase.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground mt-1">Target profit at 25%: ${results.targetProfit25Pct.toLocaleString()}</p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Net Profit</p>
                  <p className={cn("text-xl font-bold", results.netProfit >= 0 ? "text-green-500" : "text-red-500")} data-testid="result-car-profit">
                    ${results.netProfit.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">ROI</p>
                  <p className={cn("text-xl font-bold", results.roi >= 20 ? "text-green-500" : results.roi >= 10 ? "text-yellow-500" : "text-red-500")} data-testid="result-car-roi">
                    {results.roi}%
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Daily Profit</p>
                  <p className="text-lg font-bold" data-testid="result-car-daily">${results.dailyProfit.toLocaleString()}/day</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Margin</p>
                  <p className="text-lg font-bold" data-testid="result-car-margin">{results.marginPct}%</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Capital Turn</p>
                  <p className="text-lg font-bold" data-testid="result-car-turn">{results.capitalTurn.toFixed(4)}</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                  <p className="text-xs text-muted-foreground">Annual Return</p>
                  <p className="text-lg font-bold" data-testid="result-car-annual">{results.annualReturn}%</p>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                <p className="text-xs text-muted-foreground">Capital Efficiency</p>
                <p className="text-lg font-bold" data-testid="result-car-cap-eff">{results.capitalEfficiency.toFixed(4)}</p>
              </div>

              <div className="p-3 rounded-lg bg-muted/30 border border-border/40">
                <p className="text-xs text-muted-foreground">Total Expenses</p>
                <p className="text-sm font-semibold">${results.totalExpenses.toLocaleString()}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Input
                  placeholder="Deal name (e.g. 2022 BMW 3-Series Flip)"
                  value={dealName}
                  onChange={e => setDealName(e.target.value)}
                  className="text-sm"
                  data-testid="input-deal-name-car"
                />
                <Button
                  onClick={() => { if (dealName.trim()) { onSave(dealName.trim(), inputs); setDealName(""); } }}
                  disabled={!dealName.trim()}
                  data-testid="btn-save-deal-car"
                >
                  <Save className="h-4 w-4 mr-2" /> Save
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function PortfolioTab() {
  const { toast } = useToast();

  const { data: allDeals = [], isLoading: dealsLoading } = useQuery<Deal[]>({
    queryKey: ["/api/deals"],
  });

  const { data: kpis } = useQuery<{
    totalDeals: number;
    totalNetProfit: number;
    avgRoi: number;
    avgCapitalEfficiency: number;
    greenDeals: number;
    yellowDeals: number;
    redDeals: number;
  }>({
    queryKey: ["/api/deals", "kpis"],
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: number) => {
      await apiRequest("DELETE", `/api/deals/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/deals"] });
      toast({ title: "Deal deleted" });
    },
  });

  const reDeals = allDeals.filter(d => d.dealType === "real_estate");
  const carDeals = allDeals.filter(d => d.dealType === "car");

  const reCapEff = reDeals.length > 0 ? reDeals.reduce((s, d) => s + d.capitalEfficiency, 0) / reDeals.length / 10000 : 0;
  const carCapEff = carDeals.length > 0 ? carDeals.reduce((s, d) => s + d.capitalEfficiency, 0) / carDeals.length / 10000 : 0;
  const comparison = compareDeals(reCapEff, carCapEff);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <div className="h-10 w-10 rounded-xl bg-[rgb(34_197_94)]/15 flex items-center justify-center">
          <PieChart className="h-5 w-5 text-[rgb(34_197_94)]" />
        </div>
        <div>
          <h3 className="text-lg font-bold">Portfolio & KPIs</h3>
          <p className="text-xs text-muted-foreground">Capital efficiency, deal comparison, performance tracking</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard label="Total Net Profit" value={`$${(kpis?.totalNetProfit ?? 0).toLocaleString()}`} icon={CircleDollarSign} trend={(kpis?.totalNetProfit ?? 0) > 0 ? "up" : "down"} testId="kpi-profit" />
        <MetricCard label="Avg ROI" value={`${kpis?.avgRoi ?? 0}%`} icon={TrendingUp} trend={(kpis?.avgRoi ?? 0) >= 20 ? "up" : "down"} testId="kpi-roi" />
        <MetricCard label="Total Deals" value={String(kpis?.totalDeals ?? 0)} icon={BarChart3} testId="kpi-deals" />
        <MetricCard label="Avg Cap. Efficiency" value={((kpis?.avgCapitalEfficiency ?? 0) / 10000).toFixed(4)} icon={Gauge} testId="kpi-capeff" />
      </div>

      <div className="grid grid-cols-3 gap-3">
        <Card data-testid="kpi-green">
          <CardContent className="p-4 text-center">
            <div className="inline-flex h-8 w-8 rounded-full bg-green-500/10 items-center justify-center mb-2">
              <Check className="h-4 w-4 text-green-500" />
            </div>
            <p className="text-2xl font-bold text-green-500">{kpis?.greenDeals ?? 0}</p>
            <p className="text-xs text-muted-foreground">Green (Go)</p>
          </CardContent>
        </Card>
        <Card data-testid="kpi-yellow">
          <CardContent className="p-4 text-center">
            <div className="inline-flex h-8 w-8 rounded-full bg-yellow-500/10 items-center justify-center mb-2">
              <Shield className="h-4 w-4 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold text-yellow-500">{kpis?.yellowDeals ?? 0}</p>
            <p className="text-xs text-muted-foreground">Yellow (Review)</p>
          </CardContent>
        </Card>
        <Card data-testid="kpi-red">
          <CardContent className="p-4 text-center">
            <div className="inline-flex h-8 w-8 rounded-full bg-red-500/10 items-center justify-center mb-2">
              <X className="h-4 w-4 text-red-500" />
            </div>
            <p className="text-2xl font-bold text-red-500">{kpis?.redDeals ?? 0}</p>
            <p className="text-xs text-muted-foreground">Red (Reject)</p>
          </CardContent>
        </Card>
      </div>

      {allDeals.length > 0 && (
        <Card data-testid="capital-comparison">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Scale className="h-4 w-4" /> Capital Efficiency Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between gap-4 p-4 rounded-lg bg-muted/30 border border-border/40">
              <div className="text-center flex-1">
                <Building2 className="h-6 w-6 mx-auto mb-1 text-[rgb(59_130_246)]" />
                <p className="text-xs text-muted-foreground">Property ({reDeals.length})</p>
                <p className="text-lg font-bold">{(reCapEff * 100).toFixed(2)}%</p>
              </div>
              <div className="text-center px-4">
                <p className="text-xs font-semibold text-muted-foreground">VS</p>
                <Badge
                  variant="outline"
                  className={cn(
                    "mt-1 rounded-full",
                    comparison.winner === "real_estate" && "border-[rgb(59_130_246)]/40 text-[rgb(59_130_246)]",
                    comparison.winner === "car" && "border-[rgb(245_158_11)]/40 text-[rgb(245_158_11)]",
                    comparison.winner === "hold" && "border-muted-foreground/40",
                  )}
                >
                  {comparison.winner === "real_estate" ? "Property Wins" : comparison.winner === "car" ? "Car Wins" : "Hold Cash"}
                </Badge>
              </div>
              <div className="text-center flex-1">
                <Car className="h-6 w-6 mx-auto mb-1 text-[rgb(245_158_11)]" />
                <p className="text-xs text-muted-foreground">Car ({carDeals.length})</p>
                <p className="text-lg font-bold">{(carCapEff * 100).toFixed(2)}%</p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-3">{comparison.recommendation}</p>
          </CardContent>
        </Card>
      )}

      <Card data-testid="deal-history">
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2">
            <Clock className="h-4 w-4" /> Deal History ({allDeals.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {dealsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : allDeals.length === 0 ? (
            <div className="text-center py-8">
              <Target className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">No deals analyzed yet</p>
              <p className="text-xs text-muted-foreground mt-1">Use the Property or Car tab to analyze and save deals</p>
            </div>
          ) : (
            <div className="space-y-2">
              {allDeals.map(deal => {
                const res = deal.results as any;
                return (
                  <div key={deal.id} className="flex items-center justify-between gap-3 p-3 rounded-lg border border-border/40" data-testid={`deal-row-${deal.id}`}>
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={cn(
                        "h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0",
                        deal.dealType === "real_estate" ? "bg-[rgb(59_130_246)]/15" : "bg-[rgb(245_158_11)]/15"
                      )}>
                        {deal.dealType === "real_estate" ? <Home className="h-4 w-4 text-[rgb(59_130_246)]" /> : <Car className="h-4 w-4 text-[rgb(245_158_11)]" />}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium truncate">{deal.name}</p>
                        <div className="flex items-center gap-2 flex-wrap">
                          <StatusBadge status={deal.status} />
                          <span className="text-xs text-muted-foreground">
                            ${deal.netProfit.toLocaleString()} profit
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {deal.roi}% ROI
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => deleteMutation.mutate(deal.id)}
                      disabled={deleteMutation.isPending}
                      data-testid={`btn-delete-deal-${deal.id}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default function DealsPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const { toast } = useToast();

  const saveDealMutation = useMutation({
    mutationFn: async (data: { name: string; dealType: string; inputs: any }) => {
      const res = await apiRequest("POST", "/api/deals", data);
      return await res.json();
    },
    onSuccess: (deal: Deal) => {
      queryClient.invalidateQueries({ queryKey: ["/api/deals"] });
      const statusLabel = STATUS_CONFIG[deal.status as keyof typeof STATUS_CONFIG]?.label ?? deal.status;
      toast({
        title: `Deal Saved: ${statusLabel}`,
        description: `${deal.name} - $${deal.netProfit.toLocaleString()} net profit, ${deal.roi}% ROI`,
      });
    },
    onError: (err: Error) => {
      toast({ title: "Failed to save deal", description: err.message, variant: "destructive" });
    },
  });

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Deal Analyzer - DreamCo Empire OS" description="Autonomous deal scoring for real estate and car flips" />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-deals-title">Deal Analyzer</h1>
              <p className="text-sm text-muted-foreground mt-1">
                Score, rank, and compare real estate and car flip deals with autonomous AI formulas
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="rounded-full">
                <Flame className="h-3 w-3 mr-1" /> Capital Efficiency Engine
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <Zap className="h-3 w-3 mr-1" /> AI Scoring
              </Badge>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8">
          <Tabs defaultValue="real_estate" data-testid="deals-tabs">
            <TabsList className="mb-6">
              <TabsTrigger value="real_estate" data-testid="tab-real-estate">
                <Home className="h-4 w-4 mr-2" /> Property Flip
              </TabsTrigger>
              <TabsTrigger value="car" data-testid="tab-car">
                <Car className="h-4 w-4 mr-2" /> Car Flip
              </TabsTrigger>
              <TabsTrigger value="portfolio" data-testid="tab-portfolio">
                <PieChart className="h-4 w-4 mr-2" /> Portfolio
              </TabsTrigger>
            </TabsList>

            <TabsContent value="real_estate">
              <RealEstateCalculator
                onSave={(name, inputs) => saveDealMutation.mutate({ name, dealType: "real_estate", inputs })}
              />
            </TabsContent>

            <TabsContent value="car">
              <CarFlipCalculator
                onSave={(name, inputs) => saveDealMutation.mutate({ name, dealType: "car", inputs })}
              />
            </TabsContent>

            <TabsContent value="portfolio">
              <PortfolioTab />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppShell>
  );
}
