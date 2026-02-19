import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  Banknote,
  Building2,
  Calculator,
  Car,
  CheckCircle2,
  Clock,
  Copy,
  DollarSign,
  Gift,
  GraduationCap,
  Hammer,
  Landmark,
  Percent,
  Search,
  ShieldCheck,
  Sparkles,
  Tag,
  Target,
  TrendingUp,
  Truck,
  Wallet,
  Zap,
} from "lucide-react";

const LOAN_OFFERS = [
  { id: 1, lender: "Greenfield Capital", type: "Personal", apr: 5.49, minAmount: 5000, maxAmount: 50000, termMonths: 36, monthlyPayment: 452, approval: "high" as const, icon: Wallet },
  { id: 2, lender: "Horizon Business Fund", type: "Business", apr: 7.25, minAmount: 10000, maxAmount: 250000, termMonths: 60, monthlyPayment: 1985, approval: "medium" as const, icon: Building2 },
  { id: 3, lender: "National Home Lending", type: "Mortgage", apr: 6.75, minAmount: 150000, maxAmount: 750000, termMonths: 360, monthlyPayment: 3243, approval: "high" as const, icon: Landmark },
  { id: 4, lender: "AutoDrive Finance", type: "Auto", apr: 4.99, minAmount: 8000, maxAmount: 65000, termMonths: 48, monthlyPayment: 575, approval: "high" as const, icon: Car },
  { id: 5, lender: "EduFund Partners", type: "Student", apr: 3.75, minAmount: 2000, maxAmount: 100000, termMonths: 120, monthlyPayment: 348, approval: "medium" as const, icon: GraduationCap },
  { id: 6, lender: "EquipPro Lending", type: "Equipment", apr: 6.99, minAmount: 15000, maxAmount: 500000, termMonths: 72, monthlyPayment: 2934, approval: "low" as const, icon: Hammer },
  { id: 7, lender: "Federal SBA Direct", type: "SBA", apr: 5.50, minAmount: 25000, maxAmount: 350000, termMonths: 84, monthlyPayment: 2105, approval: "medium" as const, icon: ShieldCheck },
  { id: 8, lender: "MicroStart Capital", type: "Microloans", apr: 8.25, minAmount: 500, maxAmount: 15000, termMonths: 24, monthlyPayment: 339, approval: "high" as const, icon: Sparkles },
];

const FREEBIES = [
  { id: 1, name: "AWS Startup Credits", provider: "Amazon Web Services", value: "$5,000", expiry: "Mar 15, 2026", category: "Software" },
  { id: 2, name: "HubSpot CRM Free Tier", provider: "HubSpot", value: "$1,200/yr", expiry: "Ongoing", category: "Software" },
  { id: 3, name: "Google Workspace Trial", provider: "Google", value: "$720", expiry: "Apr 30, 2026", category: "Software" },
  { id: 4, name: "Free Legal Consultation", provider: "LegalZoom", value: "$500", expiry: "Jun 1, 2026", category: "Services" },
  { id: 5, name: "Coursera Business Plan", provider: "Coursera", value: "$399/yr", expiry: "May 20, 2026", category: "Education" },
  { id: 6, name: "Notion Team Plan Trial", provider: "Notion", value: "$960/yr", expiry: "Ongoing", category: "Tools" },
  { id: 7, name: "Stripe Atlas Credits", provider: "Stripe", value: "$500", expiry: "Jul 31, 2026", category: "Services" },
  { id: 8, name: "Figma Starter Plan", provider: "Figma", value: "$144/yr", expiry: "Ongoing", category: "Tools" },
  { id: 9, name: "LinkedIn Learning Access", provider: "LinkedIn", value: "$360/yr", expiry: "Dec 31, 2026", category: "Education" },
  { id: 10, name: "Cloudflare Pro Trial", provider: "Cloudflare", value: "$240/yr", expiry: "Aug 15, 2026", category: "Software" },
  { id: 11, name: "SCORE Mentorship Program", provider: "SCORE", value: "Priceless", expiry: "Ongoing", category: "Services" },
  { id: 12, name: "Canva Pro Trial", provider: "Canva", value: "$120/yr", expiry: "Ongoing", category: "Tools" },
];

const DISCOUNTS = [
  { id: 1, merchant: "Dell Technologies", discount: 25, code: "DREAM25", autoApply: false, expiry: "Apr 10, 2026", savings: "$375", category: "Tech" },
  { id: 2, merchant: "WeWork", discount: 30, code: null, autoApply: true, expiry: "May 31, 2026", savings: "$540/mo", category: "Office" },
  { id: 3, merchant: "Mailchimp", discount: 50, code: "STARTUP50", autoApply: false, expiry: "Mar 25, 2026", savings: "$150/mo", category: "Marketing" },
  { id: 4, merchant: "United Airlines Business", discount: 15, code: "BIZFLY15", autoApply: false, expiry: "Jun 30, 2026", savings: "$200+", category: "Travel" },
  { id: 5, merchant: "Microsoft 365 Business", discount: 20, code: null, autoApply: true, expiry: "Ongoing", savings: "$48/yr", category: "Tech" },
  { id: 6, merchant: "Staples Business", discount: 10, code: "BIZ10", autoApply: false, expiry: "Ongoing", savings: "$25+", category: "Office" },
  { id: 7, merchant: "SEMrush", discount: 40, code: "GROW40", autoApply: false, expiry: "Apr 15, 2026", savings: "$480/yr", category: "Marketing" },
  { id: 8, merchant: "Hilton Business Travel", discount: 20, code: null, autoApply: true, expiry: "Dec 31, 2026", savings: "$150+", category: "Travel" },
  { id: 9, merchant: "Lenovo ThinkPad", discount: 35, code: "THINK35", autoApply: false, expiry: "May 1, 2026", savings: "$525", category: "Tech" },
  { id: 10, merchant: "Regus Offices", discount: 25, code: null, autoApply: true, expiry: "Jul 15, 2026", savings: "$300/mo", category: "Office" },
  { id: 11, merchant: "Adobe Creative Cloud", discount: 60, code: "CREATE60", autoApply: false, expiry: "Mar 31, 2026", savings: "$420/yr", category: "Marketing" },
  { id: 12, merchant: "Southwest Business", discount: 10, code: "SWBIZ10", autoApply: false, expiry: "Ongoing", savings: "$80+", category: "Travel" },
];

const CALC_PRINCIPAL = 25000;
const CALC_APR = 6.5;
const CALC_TERM = 60;
const monthlyRate = CALC_APR / 100 / 12;
const CALC_MONTHLY = Math.round((CALC_PRINCIPAL * monthlyRate * Math.pow(1 + monthlyRate, CALC_TERM)) / (Math.pow(1 + monthlyRate, CALC_TERM) - 1) * 100) / 100;
const CALC_TOTAL_COST = Math.round(CALC_MONTHLY * CALC_TERM * 100) / 100;
const CALC_TOTAL_INTEREST = Math.round((CALC_TOTAL_COST - CALC_PRINCIPAL) * 100) / 100;

function generateAmortization() {
  const rows = [];
  let balance = CALC_PRINCIPAL;
  for (let month = 1; month <= Math.min(CALC_TERM, 12); month++) {
    const interest = Math.round(balance * monthlyRate * 100) / 100;
    const principal = Math.round((CALC_MONTHLY - interest) * 100) / 100;
    balance = Math.round((balance - principal) * 100) / 100;
    rows.push({ month, payment: CALC_MONTHLY, principal, interest, balance: Math.max(0, balance) });
  }
  return rows;
}

const AMORTIZATION = generateAmortization();

const APPROVAL_COLORS: Record<string, string> = {
  high: "text-green-600 dark:text-green-400",
  medium: "text-yellow-600 dark:text-yellow-400",
  low: "text-red-500 dark:text-red-400",
};

const CATEGORY_ICONS: Record<string, typeof Gift> = {
  Software: Zap,
  Services: ShieldCheck,
  Education: GraduationCap,
  Tools: Hammer,
  Tech: Sparkles,
  Office: Building2,
  Marketing: Target,
  Travel: Truck,
};

export default function LoansPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Loan & Savings Finder - DreamLoans" description="Find loans, freebies, discounts, and deals for your business." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-loans-title">Loan & Savings Finder</h1>
              <p className="text-sm text-muted-foreground mt-1">Find the best loans, freebies, discounts, and deals for your business</p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <Badge variant="secondary" className="rounded-full">
                <Search className="h-3 w-3 mr-1.5 text-primary" />
                24 Active Searches
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <DollarSign className="h-3 w-3 mr-1.5 text-green-500" />
                $12,450 Savings Found
              </Badge>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-8 buddy-stagger">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <Card data-testid="stat-active-searches">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Active Searches</CardTitle>
                <Search className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">24</p>
                <p className="text-xs text-muted-foreground mt-1">Across all categories</p>
              </CardContent>
            </Card>

            <Card data-testid="stat-savings-found">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Savings Found</CardTitle>
                <DollarSign className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">$12,450</p>
                <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" /> +32% this month
                </p>
              </CardContent>
            </Card>

            <Card data-testid="stat-loans-matched">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Loans Matched</CardTitle>
                <Banknote className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">8</p>
                <p className="text-xs text-muted-foreground mt-1">Best rates selected</p>
              </CardContent>
            </Card>

            <Card data-testid="stat-freebies-tracked">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Freebies Tracked</CardTitle>
                <Gift className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">12</p>
                <p className="text-xs text-muted-foreground mt-1">Worth $10,143+ total</p>
              </CardContent>
            </Card>
          </div>

          <Tabs defaultValue="loans" data-testid="tabs-loans">
            <TabsList className="flex-wrap">
              <TabsTrigger value="loans" data-testid="tab-loans">
                <Banknote className="h-4 w-4 mr-1.5" />
                Loans
              </TabsTrigger>
              <TabsTrigger value="freebies" data-testid="tab-freebies">
                <Gift className="h-4 w-4 mr-1.5" />
                Freebies
              </TabsTrigger>
              <TabsTrigger value="discounts" data-testid="tab-discounts">
                <Tag className="h-4 w-4 mr-1.5" />
                Discounts
              </TabsTrigger>
              <TabsTrigger value="calculator" data-testid="tab-calculator">
                <Calculator className="h-4 w-4 mr-1.5" />
                Calculator
              </TabsTrigger>
            </TabsList>

            <TabsContent value="loans" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {LOAN_OFFERS.map((loan) => {
                  const Icon = loan.icon;
                  return (
                    <Card key={loan.id} data-testid={`card-loan-${loan.id}`}>
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <Icon className="h-5 w-5 text-primary" />
                          </div>
                          <Badge variant="outline" className="rounded-full text-[10px]">{loan.type}</Badge>
                        </div>
                        <CardTitle className="text-sm mt-2">{loan.lender}</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex items-baseline gap-1">
                          <span className="text-2xl font-bold">{loan.apr}%</span>
                          <span className="text-xs text-muted-foreground">APR</span>
                        </div>
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between gap-2 text-xs">
                            <span className="text-muted-foreground">Amount</span>
                            <span className="font-medium">${loan.minAmount.toLocaleString()} - ${loan.maxAmount.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center justify-between gap-2 text-xs">
                            <span className="text-muted-foreground">Term</span>
                            <span className="font-medium">{loan.termMonths} months</span>
                          </div>
                          <div className="flex items-center justify-between gap-2 text-xs">
                            <span className="text-muted-foreground">Est. Monthly</span>
                            <span className="font-medium">${loan.monthlyPayment.toLocaleString()}</span>
                          </div>
                          <div className="flex items-center justify-between gap-2 text-xs">
                            <span className="text-muted-foreground">Approval</span>
                            <span className={`font-medium capitalize ${APPROVAL_COLORS[loan.approval]}`}>
                              {loan.approval === "high" && <CheckCircle2 className="h-3 w-3 inline mr-0.5" />}
                              {loan.approval}
                            </span>
                          </div>
                        </div>
                        <Button className="w-full" size="sm" data-testid={`button-apply-loan-${loan.id}`}>
                          Apply Now
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="freebies" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {FREEBIES.map((freebie) => {
                  const CatIcon = CATEGORY_ICONS[freebie.category] || Gift;
                  return (
                    <Card key={freebie.id} data-testid={`card-freebie-${freebie.id}`}>
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                              <CatIcon className="h-5 w-5 text-primary" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate">{freebie.name}</p>
                              <p className="text-xs text-muted-foreground truncate">{freebie.provider}</p>
                            </div>
                          </div>
                          <Badge variant="outline" className="rounded-full text-[10px] flex-shrink-0">{freebie.category}</Badge>
                        </div>
                        <div className="flex items-center justify-between gap-2">
                          <div>
                            <p className="text-xs text-muted-foreground">Value</p>
                            <p className="text-lg font-bold text-green-600 dark:text-green-400">{freebie.value}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-muted-foreground">Expires</p>
                            <p className="text-xs font-medium flex items-center gap-1">
                              <Clock className="h-3 w-3" /> {freebie.expiry}
                            </p>
                          </div>
                        </div>
                        <Button className="w-full" size="sm" variant="outline" data-testid={`button-claim-freebie-${freebie.id}`}>
                          <Gift className="h-4 w-4 mr-1.5" />
                          Claim Free
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="discounts" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {DISCOUNTS.map((deal) => {
                  const CatIcon = CATEGORY_ICONS[deal.category] || Tag;
                  return (
                    <Card key={deal.id} data-testid={`card-discount-${deal.id}`}>
                      <CardContent className="p-4 space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                              <CatIcon className="h-5 w-5 text-primary" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate">{deal.merchant}</p>
                              <Badge variant="outline" className="rounded-full text-[10px] mt-0.5">{deal.category}</Badge>
                            </div>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{deal.discount}%</p>
                            <p className="text-[10px] text-muted-foreground">off</p>
                          </div>
                        </div>
                        <div className="flex items-center justify-between gap-2">
                          <div>
                            <p className="text-xs text-muted-foreground">Savings</p>
                            <p className="text-sm font-semibold">{deal.savings}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-muted-foreground">Expires</p>
                            <p className="text-xs font-medium">{deal.expiry}</p>
                          </div>
                        </div>
                        {deal.code ? (
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-muted/50 rounded-md px-3 py-1.5 font-mono text-xs text-center tracking-wider">
                              {deal.code}
                            </div>
                            <Button size="icon" variant="outline" data-testid={`button-copy-code-${deal.id}`}>
                              <Copy className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : (
                          <Badge variant="secondary" className="w-full justify-center rounded-full">
                            <Zap className="h-3 w-3 mr-1.5" />
                            Auto-Applied
                          </Badge>
                        )}
                        <Button className="w-full" size="sm" data-testid={`button-get-discount-${deal.id}`}>
                          <Percent className="h-4 w-4 mr-1.5" />
                          Get Discount
                        </Button>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="calculator" className="mt-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card data-testid="card-calc-inputs">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Calculator className="h-5 w-5 text-primary" />
                      Loan Parameters
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-5">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm text-muted-foreground">Principal Amount</span>
                        <span className="text-lg font-bold">${CALC_PRINCIPAL.toLocaleString()}</span>
                      </div>
                      <Progress value={50} className="h-2" />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm text-muted-foreground">Interest Rate (APR)</span>
                        <span className="text-lg font-bold">{CALC_APR}%</span>
                      </div>
                      <Progress value={32.5} className="h-2" />
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm text-muted-foreground">Loan Term</span>
                        <span className="text-lg font-bold">{CALC_TERM} months</span>
                      </div>
                      <Progress value={50} className="h-2" />
                    </div>

                    <div className="border-t border-border/60 pt-4 space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium">Monthly Payment</span>
                        <span className="text-2xl font-bold text-primary">${CALC_MONTHLY.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm text-muted-foreground">Total Interest</span>
                        <span className="text-sm font-semibold text-red-500 dark:text-red-400">${CALC_TOTAL_INTEREST.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm text-muted-foreground">Total Cost</span>
                        <span className="text-sm font-semibold">${CALC_TOTAL_COST.toLocaleString()}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card data-testid="card-calc-amortization">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-primary" />
                      Amortization Preview (First 12 Months)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs" data-testid="table-amortization">
                        <thead>
                          <tr className="border-b border-border/60">
                            <th className="text-left py-2 pr-3 text-muted-foreground font-medium">Month</th>
                            <th className="text-right py-2 px-3 text-muted-foreground font-medium">Payment</th>
                            <th className="text-right py-2 px-3 text-muted-foreground font-medium">Principal</th>
                            <th className="text-right py-2 px-3 text-muted-foreground font-medium">Interest</th>
                            <th className="text-right py-2 pl-3 text-muted-foreground font-medium">Balance</th>
                          </tr>
                        </thead>
                        <tbody>
                          {AMORTIZATION.map((row) => (
                            <tr key={row.month} className="border-b border-border/30" data-testid={`row-amort-${row.month}`}>
                              <td className="py-2 pr-3 font-medium">{row.month}</td>
                              <td className="text-right py-2 px-3">${row.payment.toFixed(2)}</td>
                              <td className="text-right py-2 px-3 text-green-600 dark:text-green-400">${row.principal.toFixed(2)}</td>
                              <td className="text-right py-2 px-3 text-red-500 dark:text-red-400">${row.interest.toFixed(2)}</td>
                              <td className="text-right py-2 pl-3">${row.balance.toFixed(2)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <p className="text-xs text-muted-foreground mt-3 text-center">
                      Showing first 12 of {CALC_TERM} monthly payments
                    </p>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppShell>
  );
}
