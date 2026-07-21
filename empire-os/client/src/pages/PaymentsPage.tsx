import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Activity,
  CheckCircle2,
  CircleDollarSign,
  Clock,
  CreditCard,
  DollarSign,
  FileText,
  Monitor,
  NfcIcon,
  Plus,
  QrCode,
  Receipt,
  Send,
  Smartphone,
  Terminal,
  TrendingUp,
  Wallet,
  Wifi,
  WifiOff,
  XCircle,
} from "lucide-react";

const PAYMENT_METHODS = [
  { name: "Apple Pay", icon: Wallet, enabled: true, transactions: 1247 },
  { name: "Google Pay", icon: Smartphone, enabled: true, transactions: 983 },
  { name: "Samsung Pay", icon: CreditCard, enabled: true, transactions: 412 },
  { name: "NFC Cards", icon: NfcIcon, enabled: true, transactions: 2156 },
];

const TERMINALS = [
  { id: "POS-001", location: "Downtown Store - Register 1", status: "active" as const, lastTransaction: "2 min ago", dailyVolume: 14820.50, transactionCount: 187 },
  { id: "POS-002", location: "Downtown Store - Register 2", status: "active" as const, lastTransaction: "8 min ago", dailyVolume: 11340.25, transactionCount: 142 },
  { id: "POS-003", location: "Mall Kiosk - East Wing", status: "active" as const, lastTransaction: "1 min ago", dailyVolume: 19450.75, transactionCount: 231 },
  { id: "POS-004", location: "Airport Terminal B", status: "offline" as const, lastTransaction: "3 hrs ago", dailyVolume: 0, transactionCount: 0 },
  { id: "POS-005", location: "Warehouse Pickup", status: "active" as const, lastTransaction: "15 min ago", dailyVolume: 8920.00, transactionCount: 94 },
  { id: "POS-006", location: "Pop-Up Market Stand", status: "offline" as const, lastTransaction: "1 day ago", dailyVolume: 0, transactionCount: 0 },
  { id: "POS-007", location: "Mall Kiosk - West Wing", status: "active" as const, lastTransaction: "5 min ago", dailyVolume: 16780.30, transactionCount: 198 },
  { id: "POS-008", location: "Flagship Store - VIP", status: "active" as const, lastTransaction: "30 sec ago", dailyVolume: 27640.90, transactionCount: 312 },
];

const TRANSACTIONS = [
  { id: "TXN-78412", amount: 249.99, method: "Apple Pay", status: "completed" as const, timestamp: "Feb 19, 2026 14:32:18", customer: "Sarah M." },
  { id: "TXN-78411", amount: 89.50, method: "NFC Card", status: "completed" as const, timestamp: "Feb 19, 2026 14:28:05", customer: "James K." },
  { id: "TXN-78410", amount: 1250.00, method: "Google Pay", status: "pending" as const, timestamp: "Feb 19, 2026 14:25:41", customer: "Tech Solutions Inc." },
  { id: "TXN-78409", amount: 34.99, method: "Samsung Pay", status: "completed" as const, timestamp: "Feb 19, 2026 14:22:10", customer: "Maria L." },
  { id: "TXN-78408", amount: 599.00, method: "NFC Card", status: "failed" as const, timestamp: "Feb 19, 2026 14:18:33", customer: "Robert D." },
  { id: "TXN-78407", amount: 175.25, method: "Apple Pay", status: "completed" as const, timestamp: "Feb 19, 2026 14:15:02", customer: "Emily R." },
  { id: "TXN-78406", amount: 42.00, method: "Google Pay", status: "completed" as const, timestamp: "Feb 19, 2026 14:11:47", customer: "David W." },
  { id: "TXN-78405", amount: 890.00, method: "NFC Card", status: "completed" as const, timestamp: "Feb 19, 2026 14:08:19", customer: "Anderson Corp." },
  { id: "TXN-78404", amount: 67.50, method: "Apple Pay", status: "pending" as const, timestamp: "Feb 19, 2026 14:04:55", customer: "Lisa T." },
  { id: "TXN-78403", amount: 3200.00, method: "NFC Card", status: "completed" as const, timestamp: "Feb 19, 2026 14:01:30", customer: "Premier Holdings" },
];

const INVOICES = [
  { id: "INV-2024-001", client: "Acme Corporation", amount: 15400.00, status: "paid" as const, dueDate: "Feb 15, 2026", issuedDate: "Jan 15, 2026" },
  { id: "INV-2024-002", client: "TechStart Inc.", amount: 8750.00, status: "pending" as const, dueDate: "Feb 28, 2026", issuedDate: "Jan 28, 2026" },
  { id: "INV-2024-003", client: "Global Dynamics", amount: 32100.00, status: "paid" as const, dueDate: "Feb 10, 2026", issuedDate: "Jan 10, 2026" },
  { id: "INV-2024-004", client: "Summit Partners", amount: 4200.00, status: "overdue" as const, dueDate: "Feb 05, 2026", issuedDate: "Jan 05, 2026" },
  { id: "INV-2024-005", client: "Meridian Group", amount: 19800.00, status: "pending" as const, dueDate: "Mar 01, 2026", issuedDate: "Feb 01, 2026" },
  { id: "INV-2024-006", client: "Vertex Solutions", amount: 6300.00, status: "paid" as const, dueDate: "Feb 12, 2026", issuedDate: "Jan 12, 2026" },
  { id: "INV-2024-007", client: "NorthStar LLC", amount: 11500.00, status: "overdue" as const, dueDate: "Feb 01, 2026", issuedDate: "Jan 01, 2026" },
  { id: "INV-2024-008", client: "Cascade Ventures", amount: 27650.00, status: "pending" as const, dueDate: "Mar 05, 2026", issuedDate: "Feb 05, 2026" },
];

function getStatusBadge(status: "completed" | "pending" | "failed") {
  switch (status) {
    case "completed":
      return <Badge variant="secondary"><CheckCircle2 className="h-3 w-3 mr-1 text-green-500" />Completed</Badge>;
    case "pending":
      return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1 text-yellow-500" />Pending</Badge>;
    case "failed":
      return <Badge variant="secondary"><XCircle className="h-3 w-3 mr-1 text-red-500" />Failed</Badge>;
  }
}

function getInvoiceStatusBadge(status: "paid" | "pending" | "overdue") {
  switch (status) {
    case "paid":
      return <Badge variant="secondary"><CheckCircle2 className="h-3 w-3 mr-1 text-green-500" />Paid</Badge>;
    case "pending":
      return <Badge variant="secondary"><Clock className="h-3 w-3 mr-1 text-yellow-500" />Pending</Badge>;
    case "overdue":
      return <Badge variant="secondary"><XCircle className="h-3 w-3 mr-1 text-red-500" />Overdue</Badge>;
  }
}

export default function PaymentsPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);

  const totalTransactionsToday = TERMINALS.reduce((s, t) => s + t.transactionCount, 0);
  const totalVolume = TERMINALS.reduce((s, t) => s + t.dailyVolume, 0);
  const activeTerminals = TERMINALS.filter(t => t.status === "active").length;

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Payment Processing Hub - DreamPayments" description="Manage tap-to-pay, terminals, transactions, and invoicing for DreamPayments." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-payments-title">Payment Processing Hub</h1>
              <p className="text-sm text-muted-foreground mt-1">DreamPayments - Tap-to-pay & payment processing management</p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="rounded-full">
                <Activity className="h-3 w-3 mr-1.5 text-green-500" />
                Live
              </Badge>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-8 buddy-stagger">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <Card data-testid="stat-transactions-today">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Transactions Today</CardTitle>
                <Receipt className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight" data-testid="value-transactions-today">{totalTransactionsToday.toLocaleString()}</p>
                <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" /> +12.3% vs yesterday
                </p>
              </CardContent>
            </Card>

            <Card data-testid="stat-success-rate">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight" data-testid="value-success-rate">98.7%</p>
                <p className="text-xs text-muted-foreground mt-1">1.3% decline rate</p>
              </CardContent>
            </Card>

            <Card data-testid="stat-total-volume">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Volume</CardTitle>
                <CircleDollarSign className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight" data-testid="value-total-volume">${totalVolume.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
                <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" /> +8.5% vs yesterday
                </p>
              </CardContent>
            </Card>

            <Card data-testid="stat-active-terminals">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Active Terminals</CardTitle>
                <Terminal className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight" data-testid="value-active-terminals">{activeTerminals}/{TERMINALS.length}</p>
                <p className="text-xs text-muted-foreground mt-1">{TERMINALS.length - activeTerminals} offline</p>
              </CardContent>
            </Card>
          </div>

          <Tabs defaultValue="tap-to-pay" data-testid="payments-tabs">
            <TabsList className="w-full justify-start gap-1 flex-wrap" data-testid="payments-tabs-list">
              <TabsTrigger value="tap-to-pay" data-testid="tab-tap-to-pay">
                <Smartphone className="h-4 w-4 mr-1.5" />Tap to Pay
              </TabsTrigger>
              <TabsTrigger value="terminals" data-testid="tab-terminals">
                <Monitor className="h-4 w-4 mr-1.5" />Terminals
              </TabsTrigger>
              <TabsTrigger value="transactions" data-testid="tab-transactions">
                <Receipt className="h-4 w-4 mr-1.5" />Transactions
              </TabsTrigger>
              <TabsTrigger value="invoicing" data-testid="tab-invoicing">
                <FileText className="h-4 w-4 mr-1.5" />Invoicing
              </TabsTrigger>
            </TabsList>

            <TabsContent value="tap-to-pay" className="mt-6 space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4" data-testid="text-supported-methods">Supported Payment Methods</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {PAYMENT_METHODS.map((method) => {
                    const Icon = method.icon;
                    return (
                      <Card key={method.name} data-testid={`card-method-${method.name.toLowerCase().replace(/\s+/g, "-")}`}>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                              <Icon className="h-5 w-5 text-primary" />
                            </div>
                            <div className="min-w-0">
                              <p className="text-sm font-semibold">{method.name}</p>
                              <Badge variant="secondary" className="mt-0.5">
                                <CheckCircle2 className="h-3 w-3 mr-1 text-green-500" />Enabled
                              </Badge>
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground">{method.transactions.toLocaleString()} transactions today</p>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card data-testid="card-terminal-config">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0">
                    <CardTitle className="text-base">Terminal Configuration</CardTitle>
                    <NfcIcon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between gap-3 p-3 rounded-xl border border-border/40">
                      <div className="flex items-center gap-2">
                        <Wifi className="h-4 w-4 text-green-500" />
                        <span className="text-sm">NFC Reader</span>
                      </div>
                      <Badge variant="secondary">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between gap-3 p-3 rounded-xl border border-border/40">
                      <div className="flex items-center gap-2">
                        <CreditCard className="h-4 w-4 text-primary" />
                        <span className="text-sm">Chip Reader</span>
                      </div>
                      <Badge variant="secondary">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between gap-3 p-3 rounded-xl border border-border/40">
                      <div className="flex items-center gap-2">
                        <Smartphone className="h-4 w-4 text-primary" />
                        <span className="text-sm">Mobile Tap</span>
                      </div>
                      <Badge variant="secondary">Active</Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card data-testid="card-qr-payments">
                  <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0">
                    <CardTitle className="text-base">QR Code Payments</CardTitle>
                    <QrCode className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-center p-6 rounded-xl border border-dashed border-border/60 bg-muted/30">
                      <div className="text-center">
                        <QrCode className="h-16 w-16 text-muted-foreground mx-auto mb-3" />
                        <p className="text-sm font-medium">Dynamic QR Generation</p>
                        <p className="text-xs text-muted-foreground mt-1">Auto-generated per transaction</p>
                      </div>
                    </div>
                    <Button className="w-full" data-testid="button-generate-qr">
                      <QrCode className="h-4 w-4 mr-2" />Generate Payment QR
                    </Button>
                  </CardContent>
                </Card>
              </div>

              <Card data-testid="card-transaction-limits">
                <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0">
                  <CardTitle className="text-base">Transaction Limits</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="p-3 rounded-xl border border-border/40">
                      <p className="text-xs text-muted-foreground">Single Tap Limit</p>
                      <p className="text-lg font-bold mt-1">$500.00</p>
                    </div>
                    <div className="p-3 rounded-xl border border-border/40">
                      <p className="text-xs text-muted-foreground">Daily Limit per Terminal</p>
                      <p className="text-lg font-bold mt-1">$50,000.00</p>
                    </div>
                    <div className="p-3 rounded-xl border border-border/40">
                      <p className="text-xs text-muted-foreground">Monthly Volume Cap</p>
                      <p className="text-lg font-bold mt-1">$2,500,000.00</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="terminals" className="mt-6 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-lg font-semibold" data-testid="text-terminal-management">Terminal Management</h3>
                <Button data-testid="button-add-terminal">
                  <Plus className="h-4 w-4 mr-2" />Add Terminal
                </Button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {TERMINALS.map((terminal) => (
                  <Card key={terminal.id} data-testid={`card-terminal-${terminal.id}`}>
                    <CardContent className="p-4 space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-mono font-semibold" data-testid={`text-terminal-id-${terminal.id}`}>{terminal.id}</span>
                        {terminal.status === "active" ? (
                          <Badge variant="secondary">
                            <Wifi className="h-3 w-3 mr-1 text-green-500" />Active
                          </Badge>
                        ) : (
                          <Badge variant="secondary">
                            <WifiOff className="h-3 w-3 mr-1 text-red-500" />Offline
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground" data-testid={`text-terminal-location-${terminal.id}`}>{terminal.location}</p>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <p className="text-[10px] text-muted-foreground">Last Transaction</p>
                          <p className="text-xs font-medium">{terminal.lastTransaction}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-muted-foreground">Daily Volume</p>
                          <p className="text-xs font-medium">${terminal.dailyVolume.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">{terminal.transactionCount} transactions today</p>
                      {terminal.status === "active" ? (
                        <Button variant="outline" size="sm" className="w-full" data-testid={`button-deactivate-${terminal.id}`}>
                          <WifiOff className="h-3.5 w-3.5 mr-1.5" />Deactivate
                        </Button>
                      ) : (
                        <Button size="sm" className="w-full" data-testid={`button-activate-${terminal.id}`}>
                          <Wifi className="h-3.5 w-3.5 mr-1.5" />Activate
                        </Button>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="transactions" className="mt-6 space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card data-testid="stat-txn-completed">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-green-500/10 flex items-center justify-center flex-shrink-0">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Completed</p>
                        <p className="text-xl font-bold">{TRANSACTIONS.filter(t => t.status === "completed").length}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card data-testid="stat-txn-pending">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-yellow-500/10 flex items-center justify-center flex-shrink-0">
                        <Clock className="h-5 w-5 text-yellow-500" />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Pending</p>
                        <p className="text-xl font-bold">{TRANSACTIONS.filter(t => t.status === "pending").length}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card data-testid="stat-txn-failed">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-red-500/10 flex items-center justify-center flex-shrink-0">
                        <XCircle className="h-5 w-5 text-red-500" />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Failed</p>
                        <p className="text-xl font-bold">{TRANSACTIONS.filter(t => t.status === "failed").length}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card data-testid="card-transaction-log">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-base">Recent Transactions</CardTitle>
                  <Badge variant="secondary" className="rounded-full">{TRANSACTIONS.length} shown</Badge>
                </CardHeader>
                <CardContent className="space-y-2">
                  {TRANSACTIONS.map((txn) => (
                    <div
                      key={txn.id}
                      className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl border border-border/40"
                      data-testid={`row-txn-${txn.id}`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <CreditCard className="h-4 w-4 text-primary" />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="text-sm font-semibold" data-testid={`text-txn-id-${txn.id}`}>{txn.id}</p>
                            {getStatusBadge(txn.status)}
                          </div>
                          <p className="text-xs text-muted-foreground">{txn.customer} - {txn.method}</p>
                        </div>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="text-sm font-bold" data-testid={`text-txn-amount-${txn.id}`}>${txn.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                        <p className="text-[10px] text-muted-foreground">{txn.timestamp}</p>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="invoicing" className="mt-6 space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-lg font-semibold" data-testid="text-invoice-management">Invoice Management</h3>
                <Button data-testid="button-create-invoice">
                  <Plus className="h-4 w-4 mr-2" />Create Invoice
                </Button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card data-testid="stat-invoices-paid">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-green-500/10 flex items-center justify-center flex-shrink-0">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Paid</p>
                        <p className="text-xl font-bold">${INVOICES.filter(i => i.status === "paid").reduce((s, i) => s + i.amount, 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card data-testid="stat-invoices-pending">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-yellow-500/10 flex items-center justify-center flex-shrink-0">
                        <Clock className="h-5 w-5 text-yellow-500" />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Pending</p>
                        <p className="text-xl font-bold">${INVOICES.filter(i => i.status === "pending").reduce((s, i) => s + i.amount, 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card data-testid="stat-invoices-overdue">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-red-500/10 flex items-center justify-center flex-shrink-0">
                        <XCircle className="h-5 w-5 text-red-500" />
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Overdue</p>
                        <p className="text-xl font-bold">${INVOICES.filter(i => i.status === "overdue").reduce((s, i) => s + i.amount, 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card data-testid="card-invoice-list">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-base">Recent Invoices</CardTitle>
                  <Badge variant="secondary" className="rounded-full">{INVOICES.length} invoices</Badge>
                </CardHeader>
                <CardContent className="space-y-2">
                  {INVOICES.map((invoice) => (
                    <div
                      key={invoice.id}
                      className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl border border-border/40"
                      data-testid={`row-invoice-${invoice.id}`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                          <FileText className="h-4 w-4 text-primary" />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="text-sm font-semibold" data-testid={`text-invoice-id-${invoice.id}`}>{invoice.id}</p>
                            {getInvoiceStatusBadge(invoice.status)}
                          </div>
                          <p className="text-xs text-muted-foreground">{invoice.client}</p>
                        </div>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="text-sm font-bold" data-testid={`text-invoice-amount-${invoice.id}`}>${invoice.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                        <p className="text-[10px] text-muted-foreground">Due: {invoice.dueDate}</p>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <Button variant="outline" size="sm" data-testid={`button-view-invoice-${invoice.id}`}>
                          <FileText className="h-3.5 w-3.5 mr-1.5" />View
                        </Button>
                        {invoice.status === "pending" && (
                          <Button size="sm" data-testid={`button-send-invoice-${invoice.id}`}>
                            <Send className="h-3.5 w-3.5 mr-1.5" />Send
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppShell>
  );
}