import { useState } from "react";
import Seo from "@/components/Seo";
import AppShell from "@/components/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Activity,
  ArrowDownLeft,
  ArrowUpRight,
  Bitcoin,
  CircuitBoard,
  Coins,
  Cpu,
  Droplets,
  Flame,
  Gauge,
  Globe,
  Hash,
  Layers,
  LineChart,
  Lock,
  Megaphone,
  Monitor,
  Power,
  Server,
  Shield,
  Sparkles,
  Square,
  TrendingDown,
  TrendingUp,
  Wallet,
  Zap,
} from "lucide-react";

const WALLETS = [
  { name: "Bitcoin", symbol: "BTC", balance: 2.4831, usdPrice: 67842.50, change24h: 3.42 },
  { name: "Ethereum", symbol: "ETH", balance: 18.7265, usdPrice: 3521.80, change24h: -1.28 },
  { name: "Solana", symbol: "SOL", balance: 342.15, usdPrice: 178.42, change24h: 7.85 },
  { name: "Cardano", symbol: "ADA", balance: 28450.0, usdPrice: 0.6234, change24h: 2.14 },
  { name: "Polkadot", symbol: "DOT", balance: 1520.8, usdPrice: 8.72, change24h: -0.93 },
  { name: "Avalanche", symbol: "AVAX", balance: 215.6, usdPrice: 42.18, change24h: 5.67 },
  { name: "Chainlink", symbol: "LINK", balance: 890.3, usdPrice: 18.45, change24h: 1.22 },
  { name: "Polygon", symbol: "MATIC", balance: 15200.0, usdPrice: 0.9821, change24h: -2.45 },
  { name: "Litecoin", symbol: "LTC", balance: 45.72, usdPrice: 84.30, change24h: 0.87 },
  { name: "Ripple", symbol: "XRP", balance: 52000.0, usdPrice: 0.6312, change24h: 4.53 },
  { name: "Dogecoin", symbol: "DOGE", balance: 185000.0, usdPrice: 0.1245, change24h: -3.67 },
  { name: "Toncoin", symbol: "TON", balance: 620.4, usdPrice: 7.28, change24h: 6.12 },
];

const MINING_RIGS = [
  { name: "BTC Mining Rig Alpha", coin: "BTC", hashRate: "245 TH/s", power: "3,200W", profitPerDay: 42.85, coinsMined: 0.000632, difficulty: "High", status: "running" as const },
  { name: "ETH Mining Rig Beta", coin: "ETH", hashRate: "1.2 GH/s", power: "2,800W", profitPerDay: 28.42, coinsMined: 0.00807, difficulty: "Medium", status: "running" as const },
  { name: "SOL Mining Rig Gamma", coin: "SOL", hashRate: "580 MH/s", power: "1,500W", profitPerDay: 18.90, coinsMined: 0.106, difficulty: "Low", status: "stopped" as const },
  { name: "LTC Mining Rig Delta", coin: "LTC", hashRate: "9.8 GH/s", power: "2,100W", profitPerDay: 15.63, coinsMined: 0.1854, difficulty: "Medium", status: "running" as const },
];

const MARKET_DATA = [
  { rank: 1, name: "Bitcoin", symbol: "BTC", price: 67842.50, marketCap: 1332000000000, volume24h: 28500000000, change24h: 3.42 },
  { rank: 2, name: "Ethereum", symbol: "ETH", price: 3521.80, marketCap: 423000000000, volume24h: 15200000000, change24h: -1.28 },
  { rank: 3, name: "Tether", symbol: "USDT", price: 1.0001, marketCap: 95800000000, volume24h: 52000000000, change24h: 0.01 },
  { rank: 4, name: "BNB", symbol: "BNB", price: 612.40, marketCap: 91200000000, volume24h: 1800000000, change24h: 2.15 },
  { rank: 5, name: "Solana", symbol: "SOL", price: 178.42, marketCap: 78500000000, volume24h: 3200000000, change24h: 7.85 },
  { rank: 6, name: "XRP", symbol: "XRP", price: 0.6312, marketCap: 34200000000, volume24h: 1500000000, change24h: 4.53 },
  { rank: 7, name: "USDC", symbol: "USDC", price: 0.9999, marketCap: 32400000000, volume24h: 8100000000, change24h: -0.01 },
  { rank: 8, name: "Cardano", symbol: "ADA", price: 0.6234, marketCap: 22100000000, volume24h: 680000000, change24h: 2.14 },
  { rank: 9, name: "Avalanche", symbol: "AVAX", price: 42.18, marketCap: 15800000000, volume24h: 520000000, change24h: 5.67 },
  { rank: 10, name: "Dogecoin", symbol: "DOGE", price: 0.1245, marketCap: 17800000000, volume24h: 1200000000, change24h: -3.67 },
  { rank: 11, name: "Toncoin", symbol: "TON", price: 7.28, marketCap: 17600000000, volume24h: 340000000, change24h: 6.12 },
  { rank: 12, name: "Polkadot", symbol: "DOT", price: 8.72, marketCap: 11200000000, volume24h: 290000000, change24h: -0.93 },
  { rank: 13, name: "Chainlink", symbol: "LINK", price: 18.45, marketCap: 10800000000, volume24h: 450000000, change24h: 1.22 },
  { rank: 14, name: "Polygon", symbol: "MATIC", price: 0.9821, marketCap: 9100000000, volume24h: 380000000, change24h: -2.45 },
  { rank: 15, name: "Litecoin", symbol: "LTC", price: 84.30, marketCap: 6300000000, volume24h: 420000000, change24h: 0.87 },
  { rank: 16, name: "Uniswap", symbol: "UNI", price: 12.85, marketCap: 7700000000, volume24h: 210000000, change24h: 3.94 },
  { rank: 17, name: "Cosmos", symbol: "ATOM", price: 11.42, marketCap: 4400000000, volume24h: 180000000, change24h: -1.58 },
  { rank: 18, name: "Stellar", symbol: "XLM", price: 0.1342, marketCap: 3800000000, volume24h: 120000000, change24h: 1.05 },
  { rank: 19, name: "Near Protocol", symbol: "NEAR", price: 7.82, marketCap: 8200000000, volume24h: 310000000, change24h: 4.21 },
  { rank: 20, name: "Filecoin", symbol: "FIL", price: 6.45, marketCap: 3200000000, volume24h: 160000000, change24h: -0.72 },
];

const CAMPAIGNS = [
  { name: "BTC Bull Run Promo", platform: "Twitter/X", status: "active" as const, reach: 245000, engagement: 8.4, budget: 5000 },
  { name: "DeFi Yield Guide", platform: "YouTube", status: "active" as const, reach: 128000, engagement: 12.1, budget: 3500 },
  { name: "SOL Ecosystem Review", platform: "Medium", status: "scheduled" as const, reach: 0, engagement: 0, budget: 1200 },
  { name: "Mining ROI Calculator", platform: "Reddit", status: "completed" as const, reach: 89000, engagement: 6.7, budget: 2000 },
];

const DEFI_FARMS = [
  { pool: "ETH/USDC", protocol: "Uniswap V3", apy: 24.5, tvl: 182000000, staked: 15420, reward: "UNI" },
  { pool: "SOL/USDT", protocol: "Raydium", apy: 38.2, tvl: 45000000, staked: 8200, reward: "RAY" },
  { pool: "AVAX/USDC", protocol: "TraderJoe", apy: 31.8, tvl: 28000000, staked: 5600, reward: "JOE" },
  { pool: "BTC/ETH", protocol: "Curve", apy: 12.4, tvl: 320000000, staked: 42000, reward: "CRV" },
];

const STAKING_POSITIONS = [
  { asset: "Ethereum", symbol: "ETH", amount: 12.5, apy: 4.8, validator: "Lido", rewards: 0.6, lockPeriod: "Flexible" },
  { asset: "Solana", symbol: "SOL", amount: 200, apy: 7.2, validator: "Marinade", rewards: 14.4, lockPeriod: "Flexible" },
  { asset: "Cardano", symbol: "ADA", amount: 15000, apy: 5.1, validator: "SundaeSwap", rewards: 765, lockPeriod: "Epoch" },
  { asset: "Polkadot", symbol: "DOT", amount: 800, apy: 14.2, validator: "Acala", rewards: 113.6, lockPeriod: "28 days" },
  { asset: "Cosmos", symbol: "ATOM", amount: 350, apy: 18.5, validator: "Osmosis", rewards: 64.75, lockPeriod: "21 days" },
];

const LIQUIDITY_POOLS = [
  { pair: "ETH/DAI", protocol: "Aave", tvl: 450000000, apy: 6.8, utilization: 78.4 },
  { pair: "BTC/WBTC", protocol: "Compound", tvl: 280000000, apy: 3.2, utilization: 65.2 },
  { pair: "USDC/USDT", protocol: "Curve", tvl: 1200000000, apy: 8.5, utilization: 92.1 },
  { pair: "SOL/mSOL", protocol: "Marinade", tvl: 85000000, apy: 11.4, utilization: 88.7 },
];

function formatLargeNumber(n: number): string {
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `$${(n / 1e3).toFixed(1)}K`;
  return `$${n.toFixed(2)}`;
}

function formatUsd(n: number): string {
  if (n >= 1000) return `$${n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (n >= 1) return `$${n.toFixed(2)}`;
  return `$${n.toFixed(4)}`;
}

export default function CryptoPage() {
  const [botSlug, setBotSlug] = useState<string | undefined>(undefined);
  const [activeTab, setActiveTab] = useState("wallet");

  const totalWalletValue = WALLETS.reduce((sum, w) => sum + w.balance * w.usdPrice, 0);
  const totalMiningProfit = MINING_RIGS.reduce((sum, r) => sum + r.profitPerDay, 0);

  return (
    <AppShell selectedBotSlug={botSlug} onBotChange={setBotSlug}>
      <Seo title="Crypto Command Center - DreamCrypto" description="Comprehensive crypto dashboard for the DreamCrypto division." />

      <div className="buddy-card buddy-noise buddy-appear overflow-hidden">
        <div className="px-5 pt-6 pb-5 md:px-8 md:pt-8 md:pb-6 border-b border-border/60">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl" data-testid="text-crypto-title">Crypto Command Center</h1>
              <p className="text-sm text-muted-foreground mt-1">DreamCrypto division overview and operations</p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              <Badge variant="secondary" className="rounded-full">
                <Wallet className="h-3 w-3 mr-1.5 text-primary" />
                {WALLETS.length} Total Wallets
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <Server className="h-3 w-3 mr-1.5 text-yellow-500" />
                {MINING_RIGS.filter(r => r.status === "running").length} Mining Rigs Active
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <Coins className="h-3 w-3 mr-1.5 text-blue-500" />
                {MARKET_DATA.length} Currencies Tracked
              </Badge>
              <Badge variant="secondary" className="rounded-full">
                <Activity className="h-3 w-3 mr-1.5 text-green-500" />
                $28.5B 24h Volume
              </Badge>
            </div>
          </div>
        </div>

        <div className="p-5 md:p-8 space-y-8 buddy-stagger">
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            <Card data-testid="stat-portfolio-value">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Portfolio Value</CardTitle>
                <Wallet className="h-4 w-4 text-primary" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">${totalWalletValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
                <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" /> +5.2% vs yesterday
                </p>
              </CardContent>
            </Card>

            <Card data-testid="stat-mining-profit">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Daily Mining Profit</CardTitle>
                <Cpu className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">${totalMiningProfit.toFixed(2)}</p>
                <p className="text-xs text-muted-foreground mt-1">{MINING_RIGS.filter(r => r.status === "running").length} of {MINING_RIGS.length} rigs active</p>
              </CardContent>
            </Card>

            <Card data-testid="stat-defi-tvl">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">DeFi TVL Exposure</CardTitle>
                <Layers className="h-4 w-4 text-violet-500" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">$71.2K</p>
                <p className="text-xs text-green-600 dark:text-green-400 mt-1 flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" /> Avg APY 21.7%
                </p>
              </CardContent>
            </Card>

            <Card data-testid="stat-staking-rewards">
              <CardHeader className="flex flex-row items-center justify-between gap-1 space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">Staking Rewards</CardTitle>
                <Lock className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold tracking-tight">{STAKING_POSITIONS.length} Active</p>
                <p className="text-xs text-muted-foreground mt-1">Avg APY 9.96%</p>
              </CardContent>
            </Card>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList data-testid="tabs-crypto">
              <TabsTrigger value="wallet" data-testid="tab-wallet">
                <Wallet className="h-4 w-4 mr-1.5" />
                Wallet
              </TabsTrigger>
              <TabsTrigger value="mining" data-testid="tab-mining">
                <Cpu className="h-4 w-4 mr-1.5" />
                Mining
              </TabsTrigger>
              <TabsTrigger value="market" data-testid="tab-market">
                <LineChart className="h-4 w-4 mr-1.5" />
                Market
              </TabsTrigger>
              <TabsTrigger value="defi" data-testid="tab-defi">
                <Layers className="h-4 w-4 mr-1.5" />
                DeFi
              </TabsTrigger>
            </TabsList>

            <TabsContent value="wallet" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {WALLETS.map((w) => {
                  const usdValue = w.balance * w.usdPrice;
                  const isPositive = w.change24h >= 0;
                  return (
                    <Card key={w.symbol} data-testid={`wallet-card-${w.symbol.toLowerCase()}`}>
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                              <Bitcoin className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                              <p className="text-sm font-semibold" data-testid={`text-wallet-name-${w.symbol.toLowerCase()}`}>{w.name}</p>
                              <p className="text-xs text-muted-foreground">{w.symbol}</p>
                            </div>
                          </div>
                          <div className={`flex items-center gap-1 text-xs font-medium ${isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`} data-testid={`text-change-${w.symbol.toLowerCase()}`}>
                            {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                            {isPositive ? "+" : ""}{w.change24h.toFixed(2)}%
                          </div>
                        </div>
                        <div className="mt-3">
                          <p className="text-lg font-bold" data-testid={`text-balance-${w.symbol.toLowerCase()}`}>{w.balance.toLocaleString(undefined, { maximumFractionDigits: 4 })} {w.symbol}</p>
                          <p className="text-sm text-muted-foreground" data-testid={`text-usd-value-${w.symbol.toLowerCase()}`}>{formatUsd(usdValue)}</p>
                        </div>
                        <div className="flex items-center gap-2 mt-4">
                          <Button size="sm" variant="default" data-testid={`button-send-${w.symbol.toLowerCase()}`}>
                            <ArrowUpRight className="h-3.5 w-3.5 mr-1.5" />
                            Send
                          </Button>
                          <Button size="sm" variant="outline" data-testid={`button-receive-${w.symbol.toLowerCase()}`}>
                            <ArrowDownLeft className="h-3.5 w-3.5 mr-1.5" />
                            Receive
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="mining" className="mt-6 space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4">
                <Card data-testid="mining-stat-hashrate">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Hash className="h-4 w-4 text-primary flex-shrink-0" />
                      <p className="text-xs text-muted-foreground">Total Hash Rate</p>
                    </div>
                    <p className="text-lg font-bold mt-1">245.6 TH/s</p>
                  </CardContent>
                </Card>
                <Card data-testid="mining-stat-power">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Zap className="h-4 w-4 text-yellow-500 flex-shrink-0" />
                      <p className="text-xs text-muted-foreground">Power Consumption</p>
                    </div>
                    <p className="text-lg font-bold mt-1">9,600W</p>
                  </CardContent>
                </Card>
                <Card data-testid="mining-stat-profit">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-green-500 flex-shrink-0" />
                      <p className="text-xs text-muted-foreground">Profitability/Day</p>
                    </div>
                    <p className="text-lg font-bold mt-1">${totalMiningProfit.toFixed(2)}</p>
                  </CardContent>
                </Card>
                <Card data-testid="mining-stat-mined">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Coins className="h-4 w-4 text-orange-500 flex-shrink-0" />
                      <p className="text-xs text-muted-foreground">Coins Mined (24h)</p>
                    </div>
                    <p className="text-lg font-bold mt-1">4 currencies</p>
                  </CardContent>
                </Card>
                <Card data-testid="mining-stat-difficulty">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Gauge className="h-4 w-4 text-red-500 flex-shrink-0" />
                      <p className="text-xs text-muted-foreground">Difficulty Adj.</p>
                    </div>
                    <p className="text-lg font-bold mt-1">+2.4%</p>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {MINING_RIGS.map((rig) => {
                  const isRunning = rig.status === "running";
                  return (
                    <Card key={rig.name} data-testid={`mining-rig-${rig.coin.toLowerCase()}`}>
                      <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0 pb-2">
                        <CardTitle className="text-sm font-semibold flex items-center gap-2">
                          <Server className="h-4 w-4 text-primary" />
                          {rig.name}
                        </CardTitle>
                        <Badge variant={isRunning ? "default" : "secondary"} className="rounded-full">
                          {isRunning ? <Activity className="h-3 w-3 mr-1" /> : <Square className="h-3 w-3 mr-1" />}
                          {isRunning ? "Running" : "Stopped"}
                        </Badge>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div>
                            <p className="text-[10px] text-muted-foreground">Hash Rate</p>
                            <p className="text-sm font-semibold">{rig.hashRate}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Power</p>
                            <p className="text-sm font-semibold">{rig.power}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Profit/Day</p>
                            <p className="text-sm font-semibold text-green-600 dark:text-green-400">${rig.profitPerDay.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Coins Mined/Day</p>
                            <p className="text-sm font-semibold">{rig.coinsMined} {rig.coin}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Difficulty</p>
                            <p className="text-sm font-semibold">{rig.difficulty}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {isRunning ? (
                            <Button size="sm" variant="outline" data-testid={`button-stop-${rig.coin.toLowerCase()}`}>
                              <Power className="h-3.5 w-3.5 mr-1.5" />
                              Stop
                            </Button>
                          ) : (
                            <Button size="sm" variant="default" data-testid={`button-start-${rig.coin.toLowerCase()}`}>
                              <Power className="h-3.5 w-3.5 mr-1.5" />
                              Start
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </TabsContent>

            <TabsContent value="market" className="mt-6 space-y-6">
              <Card data-testid="market-overview">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Globe className="h-5 w-5 text-primary" />
                    Market Overview
                  </CardTitle>
                  <Badge variant="secondary" className="rounded-full">
                    <Activity className="h-3 w-3 mr-1.5 text-green-500" />
                    Live
                  </Badge>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="hidden md:grid grid-cols-6 gap-3 px-3 py-2 text-xs font-medium text-muted-foreground border-b border-border/40">
                      <span>Rank / Name</span>
                      <span className="text-right">Price</span>
                      <span className="text-right">24h Change</span>
                      <span className="text-right">Market Cap</span>
                      <span className="text-right">Volume (24h)</span>
                      <span></span>
                    </div>
                    {MARKET_DATA.map((coin) => {
                      const isPositive = coin.change24h >= 0;
                      return (
                        <div key={coin.symbol} className="grid grid-cols-2 md:grid-cols-6 gap-3 items-center px-3 py-2.5 rounded-lg border border-border/20" data-testid={`market-row-${coin.symbol.toLowerCase()}`}>
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono text-muted-foreground w-5 text-right">{coin.rank}</span>
                            <div>
                              <p className="text-sm font-semibold">{coin.name}</p>
                              <p className="text-xs text-muted-foreground">{coin.symbol}</p>
                            </div>
                          </div>
                          <p className="text-sm font-bold text-right">{formatUsd(coin.price)}</p>
                          <div className={`hidden md:flex items-center justify-end gap-1 text-xs font-medium ${isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                            {isPositive ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                            {isPositive ? "+" : ""}{coin.change24h.toFixed(2)}%
                          </div>
                          <p className="hidden md:block text-xs text-muted-foreground text-right">{formatLargeNumber(coin.marketCap)}</p>
                          <p className="hidden md:block text-xs text-muted-foreground text-right">{formatLargeNumber(coin.volume24h)}</p>
                          <div className="hidden md:flex justify-end">
                            <Button size="sm" variant="outline" data-testid={`button-trade-${coin.symbol.toLowerCase()}`}>
                              Trade
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="marketing-campaigns">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Megaphone className="h-5 w-5 text-primary" />
                    Marketing Bot Campaigns
                  </CardTitle>
                  <Badge variant="secondary" className="rounded-full">{CAMPAIGNS.filter(c => c.status === "active").length} Active</Badge>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {CAMPAIGNS.map((campaign) => (
                      <div key={campaign.name} className="p-4 rounded-lg border border-border/40" data-testid={`campaign-${campaign.name.toLowerCase().replace(/\s+/g, "-")}`}>
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold">{campaign.name}</p>
                            <p className="text-xs text-muted-foreground">{campaign.platform}</p>
                          </div>
                          <Badge variant={campaign.status === "active" ? "default" : campaign.status === "scheduled" ? "secondary" : "outline"} className="rounded-full text-xs capitalize">
                            {campaign.status}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-2 mt-3">
                          <div>
                            <p className="text-[10px] text-muted-foreground">Reach</p>
                            <p className="text-xs font-semibold">{campaign.reach > 0 ? `${(campaign.reach / 1000).toFixed(0)}K` : "--"}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Engagement</p>
                            <p className="text-xs font-semibold">{campaign.engagement > 0 ? `${campaign.engagement}%` : "--"}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Budget</p>
                            <p className="text-xs font-semibold">${campaign.budget.toLocaleString()}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="defi" className="mt-6 space-y-6">
              <Card data-testid="defi-yield-farming">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    Yield Farming Positions
                  </CardTitle>
                  <Badge variant="secondary" className="rounded-full">{DEFI_FARMS.length} Active</Badge>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {DEFI_FARMS.map((farm) => (
                      <div key={farm.pool} className="p-4 rounded-lg border border-border/40" data-testid={`farm-${farm.pool.toLowerCase().replace("/", "-")}`}>
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold">{farm.pool}</p>
                            <p className="text-xs text-muted-foreground">{farm.protocol}</p>
                          </div>
                          <Badge variant="outline" className="rounded-full text-xs text-green-600 dark:text-green-400 border-green-500/40 no-default-hover-elevate no-default-active-elevate">
                            {farm.apy}% APY
                          </Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-2 mt-3">
                          <div>
                            <p className="text-[10px] text-muted-foreground">TVL</p>
                            <p className="text-xs font-semibold">{formatLargeNumber(farm.tvl)}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Staked Value</p>
                            <p className="text-xs font-semibold">${farm.staked.toLocaleString()}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Reward Token</p>
                            <p className="text-xs font-semibold">{farm.reward}</p>
                          </div>
                        </div>
                        <div className="mt-3">
                          <Button size="sm" variant="outline" data-testid={`button-harvest-${farm.pool.toLowerCase().replace("/", "-")}`}>
                            <Flame className="h-3.5 w-3.5 mr-1.5" />
                            Harvest
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="defi-staking">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Lock className="h-5 w-5 text-primary" />
                    Staking Positions
                  </CardTitle>
                  <Badge variant="secondary" className="rounded-full">{STAKING_POSITIONS.length} Active</Badge>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {STAKING_POSITIONS.map((pos) => (
                      <div key={pos.symbol} className="flex items-center justify-between gap-3 p-3 rounded-lg border border-border/40" data-testid={`staking-${pos.symbol.toLowerCase()}`}>
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="h-9 w-9 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <Shield className="h-4 w-4 text-primary" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-semibold">{pos.asset} ({pos.symbol})</p>
                            <p className="text-xs text-muted-foreground">Validator: {pos.validator}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 flex-shrink-0">
                          <div className="text-right">
                            <p className="text-sm font-bold">{pos.amount.toLocaleString()} {pos.symbol}</p>
                            <p className="text-xs text-muted-foreground">Lock: {pos.lockPeriod}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs font-semibold text-green-600 dark:text-green-400">{pos.apy}% APY</p>
                            <p className="text-xs text-muted-foreground">+{pos.rewards} {pos.symbol}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card data-testid="defi-liquidity-pools">
                <CardHeader className="flex flex-row items-center justify-between gap-2 space-y-0">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Droplets className="h-5 w-5 text-primary" />
                    Liquidity Pools
                  </CardTitle>
                  <Badge variant="secondary" className="rounded-full">{LIQUIDITY_POOLS.length} Pools</Badge>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {LIQUIDITY_POOLS.map((pool) => (
                      <div key={pool.pair} className="p-4 rounded-lg border border-border/40" data-testid={`pool-${pool.pair.toLowerCase().replace("/", "-")}`}>
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold">{pool.pair}</p>
                            <p className="text-xs text-muted-foreground">{pool.protocol}</p>
                          </div>
                          <Badge variant="outline" className="rounded-full text-xs text-green-600 dark:text-green-400 border-green-500/40 no-default-hover-elevate no-default-active-elevate">
                            {pool.apy}% APY
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-2 mt-3">
                          <div>
                            <p className="text-[10px] text-muted-foreground">TVL</p>
                            <p className="text-xs font-semibold">{formatLargeNumber(pool.tvl)}</p>
                          </div>
                          <div>
                            <p className="text-[10px] text-muted-foreground">Utilization</p>
                            <p className="text-xs font-semibold">{pool.utilization}%</p>
                          </div>
                        </div>
                        <div className="mt-3">
                          <Button size="sm" variant="outline" data-testid={`button-provide-${pool.pair.toLowerCase().replace("/", "-")}`}>
                            <Droplets className="h-3.5 w-3.5 mr-1.5" />
                            Provide Liquidity
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppShell>
  );
}
