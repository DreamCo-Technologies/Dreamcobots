// ---------------------------------------------------------------------------
// Deal calculation helpers for real estate and car flips
// ---------------------------------------------------------------------------

// ── Real Estate ──────────────────────────────────────────────────────────────

export interface RealEstateInputs {
  arv: number;
  purchasePrice: number;
  repairCosts: number;
  closingCostsBuy: number;
  closingCostsSell: number;
  holdingCostMonthly: number;
  holdingMonths: number;
  agentFees: number;
  financingCosts: number;
  cashInvested: number;
  daysHeld: number;
  marketGrowthPct?: number;
  rehabRiskMultiplier?: number;
  daysOnMarketRisk?: number;
}

export interface RealEstateResult {
  status: "green" | "yellow" | "red";
  mao: number;
  netProfit: number;
  roi: number;
  cashOnCash: number;
  leverageRoi: number;
  dailyProfit: number;
  capitalEfficiency: number;
  safetyScore: number;
  equityMarginPct: number;
  totalExpenses: number;
  totalHoldingCosts: number;
  grossProfit: number;
  totalCosts: number;
}

// ── Car Flip ─────────────────────────────────────────────────────────────────

export interface CarFlipInputs {
  purchasePrice: number;
  expectedSalePrice: number;
  repairCosts: number;
  auctionFees: number;
  transportCosts: number;
  titleRegistration: number;
  reconditioning: number;
  advertising: number;
  taxes: number;
  cashInvested: number;
  daysHeld: number;
}

export interface CarFlipResult {
  status: "green" | "yellow" | "red";
  maxPurchase: number;
  targetProfit25Pct: number;
  netProfit: number;
  roi: number;
  dailyProfit: number;
  marginPct: number;
  capitalTurn: number;
  annualReturn: number;
  capitalEfficiency: number;
  totalExpenses: number;
}

// ── Comparison ───────────────────────────────────────────────────────────────

export interface ComparisonResult {
  winner: "real_estate" | "car" | "hold";
  recommendation: string;
}

// ── Config / Defaults ────────────────────────────────────────────────────────

export const STATUS_CONFIG = {
  green: { label: "Strong Deal", color: "text-green-600", bg: "bg-green-50" },
  yellow: { label: "Marginal Deal", color: "text-yellow-600", bg: "bg-yellow-50" },
  red: { label: "Avoid Deal", color: "text-red-600", bg: "bg-red-50" },
} as const;

export const DEFAULT_RE_INPUTS: RealEstateInputs = {
  arv: 250000,
  purchasePrice: 150000,
  repairCosts: 20000,
  closingCostsBuy: 3000,
  closingCostsSell: 5000,
  holdingCostMonthly: 1500,
  holdingMonths: 3,
  agentFees: 7500,
  financingCosts: 3000,
  cashInvested: 50000,
  daysHeld: 90,
  marketGrowthPct: 0,
  rehabRiskMultiplier: 1,
  daysOnMarketRisk: 30,
};

export const DEFAULT_CAR_INPUTS: CarFlipInputs = {
  purchasePrice: 8000,
  expectedSalePrice: 12000,
  repairCosts: 1500,
  auctionFees: 300,
  transportCosts: 200,
  titleRegistration: 150,
  reconditioning: 300,
  advertising: 100,
  taxes: 400,
  cashInvested: 10000,
  daysHeld: 30,
};

// ── Calculation Functions ────────────────────────────────────────────────────

export function calculateRealEstate(inputs: RealEstateInputs): RealEstateResult {
  const {
    arv,
    purchasePrice,
    repairCosts,
    closingCostsBuy,
    closingCostsSell,
    holdingCostMonthly,
    holdingMonths,
    agentFees,
    financingCosts,
    cashInvested,
    daysHeld,
  } = inputs;

  // MAO = 70% of ARV minus repairs (industry standard)
  const mao = Math.round(arv * 0.7 - repairCosts);

  const totalHoldingCosts = holdingCostMonthly * holdingMonths;
  const totalCosts = purchasePrice + repairCosts + closingCostsBuy + closingCostsSell
    + totalHoldingCosts + agentFees + financingCosts;
  const grossProfit = arv - purchasePrice;
  const netProfit = arv - totalCosts;
  const roi = cashInvested > 0 ? round2((netProfit / cashInvested) * 100) : 0;
  const cashOnCash = cashInvested > 0 ? round2((netProfit / cashInvested) * 100) : 0;
  const leverageRoi = purchasePrice > 0 ? round2((netProfit / purchasePrice) * 100) : 0;
  const days = daysHeld > 0 ? daysHeld : 1;
  const dailyProfit = Math.round(netProfit / days);
  const capitalEfficiency = cashInvested > 0 ? netProfit / cashInvested : 0;
  const equityMarginPct = arv > 0 ? round2(((arv - totalCosts) / arv) * 100) : 0;
  const safetyScore = round2((arv - purchasePrice - repairCosts) / Math.max(arv, 1) * 100);
  const totalExpenses = totalCosts - purchasePrice;

  let status: "green" | "yellow" | "red";
  if (roi >= 20) {
    status = "green";
  } else if (roi >= 10) {
    status = "yellow";
  } else {
    status = "red";
  }

  return {
    status,
    mao,
    netProfit,
    roi,
    cashOnCash,
    leverageRoi,
    dailyProfit,
    capitalEfficiency,
    safetyScore,
    equityMarginPct,
    totalExpenses,
    totalHoldingCosts,
    grossProfit,
    totalCosts,
  };
}

export function calculateCarFlip(inputs: CarFlipInputs): CarFlipResult {
  const {
    purchasePrice,
    expectedSalePrice,
    repairCosts,
    auctionFees,
    transportCosts,
    titleRegistration,
    reconditioning,
    advertising,
    taxes,
    cashInvested,
    daysHeld,
  } = inputs;

  const totalExpenses = repairCosts + auctionFees + transportCosts
    + titleRegistration + reconditioning + advertising + taxes;
  const totalCosts = purchasePrice + totalExpenses;
  const netProfit = expectedSalePrice - totalCosts;
  const roi = cashInvested > 0 ? round2((netProfit / cashInvested) * 100) : 0;
  const days = daysHeld > 0 ? daysHeld : 1;
  const dailyProfit = Math.round(netProfit / days);
  const marginPct = expectedSalePrice > 0 ? round2((netProfit / expectedSalePrice) * 100) : 0;
  const capitalEfficiency = cashInvested > 0 ? netProfit / cashInvested : 0;
  const capitalTurn = cashInvested > 0 ? netProfit / cashInvested : 0;
  const annualReturn = round2((365 / days) * roi);

  // Max purchase for 25% target profit margin on expected sale price
  const targetProfit25Pct = Math.round(expectedSalePrice * 0.25);
  const maxPurchase = Math.round(expectedSalePrice - totalExpenses - targetProfit25Pct);

  let status: "green" | "yellow" | "red";
  if (roi >= 20) {
    status = "green";
  } else if (roi >= 8) {
    status = "yellow";
  } else {
    status = "red";
  }

  return {
    status,
    maxPurchase,
    targetProfit25Pct,
    netProfit,
    roi,
    dailyProfit,
    marginPct,
    capitalTurn,
    annualReturn,
    capitalEfficiency,
    totalExpenses,
  };
}

export function compareDeals(
  realEstateCapitalEfficiency: number,
  carFlipCapitalEfficiency: number,
): ComparisonResult {
  const diff = realEstateCapitalEfficiency - carFlipCapitalEfficiency;
  if (realEstateCapitalEfficiency <= 0 && carFlipCapitalEfficiency <= 0) {
    return {
      winner: "hold",
      recommendation:
        "Neither deal meets minimum return thresholds. Hold capital for a better opportunity.",
    };
  }
  if (diff > 0.05) {
    return {
      winner: "real_estate",
      recommendation:
        "Real estate delivers superior capital efficiency. Prioritize property deals.",
    };
  }
  if (diff < -0.05) {
    return {
      winner: "car",
      recommendation:
        "Car flipping yields higher capital efficiency. Focus on vehicle deals.",
    };
  }
  return {
    winner: "hold",
    recommendation:
      "Both deal types show similar efficiency. Diversify across both strategies.",
  };
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}
