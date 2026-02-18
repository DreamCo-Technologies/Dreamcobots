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
  marketGrowthPct: number;
  rehabRiskMultiplier: number;
  daysOnMarketRisk: number;
}

export interface RealEstateResults {
  mao: number;
  totalHoldingCosts: number;
  totalExpenses: number;
  netProfit: number;
  roi: number;
  cashOnCash: number;
  dailyProfit: number;
  capitalEfficiency: number;
  leverageRoi: number;
  safetyScore: number;
  equityMarginPct: number;
  status: DealStatus;
}

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

export interface CarFlipResults {
  targetProfit25Pct: number;
  maxPurchase: number;
  totalExpenses: number;
  netProfit: number;
  roi: number;
  dailyProfit: number;
  capitalTurn: number;
  annualReturn: number;
  capitalEfficiency: number;
  marginPct: number;
  status: DealStatus;
}

export type DealStatus = "green" | "yellow" | "red";
export type DealType = "real_estate" | "car";

export function calculateRealEstate(inputs: RealEstateInputs): RealEstateResults {
  const mao = (inputs.arv * 0.70) - inputs.repairCosts;

  const totalHoldingCosts = inputs.holdingCostMonthly * inputs.holdingMonths;

  const totalExpenses =
    inputs.purchasePrice +
    inputs.repairCosts +
    inputs.closingCostsBuy +
    inputs.closingCostsSell +
    totalHoldingCosts +
    inputs.agentFees +
    inputs.financingCosts;

  const netProfit = inputs.arv - totalExpenses;

  const cashInvested = inputs.cashInvested || inputs.purchasePrice;
  const roi = cashInvested > 0 ? (netProfit / cashInvested) * 100 : 0;

  const cashOnCash = cashInvested > 0 ? (netProfit / cashInvested) * 100 : 0;

  const daysHeld = inputs.daysHeld || 1;
  const dailyProfit = netProfit / daysHeld;

  const capitalEfficiency = cashInvested > 0 && daysHeld > 0
    ? (netProfit / cashInvested) / daysHeld
    : 0;

  const leverageRoi = inputs.cashInvested > 0
    ? (netProfit / inputs.cashInvested) * 100
    : roi;

  const equityMarginPct = inputs.arv > 0
    ? ((inputs.arv - inputs.purchasePrice - inputs.repairCosts) / inputs.arv) * 100
    : 0;

  const safetyScore =
    equityMarginPct +
    (inputs.marketGrowthPct * 0.5) -
    inputs.rehabRiskMultiplier -
    inputs.daysOnMarketRisk;

  let status: DealStatus = "red";
  if (roi >= 20 && netProfit > 0 && inputs.purchasePrice <= mao && safetyScore >= 15) {
    status = "green";
  } else if (roi >= 10 && netProfit > 0 && safetyScore >= 5) {
    status = "yellow";
  }

  return {
    mao: Math.round(mao),
    totalHoldingCosts: Math.round(totalHoldingCosts),
    totalExpenses: Math.round(totalExpenses),
    netProfit: Math.round(netProfit),
    roi: Math.round(roi * 100) / 100,
    cashOnCash: Math.round(cashOnCash * 100) / 100,
    dailyProfit: Math.round(dailyProfit),
    capitalEfficiency: Math.round(capitalEfficiency * 10000) / 10000,
    leverageRoi: Math.round(leverageRoi * 100) / 100,
    safetyScore: Math.round(safetyScore * 100) / 100,
    equityMarginPct: Math.round(equityMarginPct * 100) / 100,
    status,
  };
}

export function calculateCarFlip(inputs: CarFlipInputs): CarFlipResults {
  const targetProfit25Pct = inputs.purchasePrice * 0.25;

  const totalFees =
    inputs.auctionFees +
    inputs.transportCosts +
    inputs.titleRegistration +
    inputs.reconditioning +
    inputs.advertising +
    inputs.taxes;

  const maxPurchase =
    inputs.expectedSalePrice -
    inputs.repairCosts -
    totalFees -
    targetProfit25Pct;

  const totalExpenses =
    inputs.purchasePrice +
    inputs.repairCosts +
    totalFees;

  const netProfit = inputs.expectedSalePrice - totalExpenses;

  const cashInvested = inputs.cashInvested || inputs.purchasePrice;
  const roi = cashInvested > 0 ? (netProfit / cashInvested) * 100 : 0;

  const daysHeld = inputs.daysHeld || 1;
  const dailyProfit = netProfit / daysHeld;

  const capitalTurn = cashInvested > 0
    ? (dailyProfit * 365) / cashInvested
    : 0;

  const annualReturn = capitalTurn * 100;

  const capitalEfficiency = cashInvested > 0 && daysHeld > 0
    ? (netProfit / cashInvested) / daysHeld
    : 0;

  const marginPct = inputs.expectedSalePrice > 0
    ? (netProfit / inputs.expectedSalePrice) * 100
    : 0;

  let status: DealStatus = "red";
  if (roi >= 20 && netProfit > 0 && marginPct >= 15) {
    status = "green";
  } else if (roi >= 10 && netProfit > 0) {
    status = "yellow";
  }

  return {
    targetProfit25Pct: Math.round(targetProfit25Pct),
    maxPurchase: Math.round(maxPurchase),
    totalExpenses: Math.round(totalExpenses),
    netProfit: Math.round(netProfit),
    roi: Math.round(roi * 100) / 100,
    dailyProfit: Math.round(dailyProfit),
    capitalTurn: Math.round(capitalTurn * 10000) / 10000,
    annualReturn: Math.round(annualReturn * 100) / 100,
    capitalEfficiency: Math.round(capitalEfficiency * 10000) / 10000,
    marginPct: Math.round(marginPct * 100) / 100,
    status,
  };
}

export function compareDeals(
  reCapitalEfficiency: number,
  carCapitalEfficiency: number
): { winner: "real_estate" | "car" | "hold"; recommendation: string } {
  if (reCapitalEfficiency <= 0 && carCapitalEfficiency <= 0) {
    return { winner: "hold", recommendation: "Both deals show negative or zero returns. Hold cash and wait for a better opportunity." };
  }
  if (reCapitalEfficiency > carCapitalEfficiency) {
    return { winner: "real_estate", recommendation: `Property flip wins with ${(reCapitalEfficiency * 100).toFixed(2)}% daily capital efficiency vs car's ${(carCapitalEfficiency * 100).toFixed(2)}%.` };
  }
  if (carCapitalEfficiency > reCapitalEfficiency) {
    return { winner: "car", recommendation: `Car flip wins with ${(carCapitalEfficiency * 100).toFixed(2)}% daily capital efficiency vs property's ${(reCapitalEfficiency * 100).toFixed(2)}%.` };
  }
  return { winner: "hold", recommendation: "Both deals have equal efficiency. Choose based on risk tolerance and liquidity needs." };
}

export const STATUS_CONFIG = {
  green: { label: "Approved", description: "High confidence - auto-execute", color: "text-green-500" },
  yellow: { label: "Review", description: "Moderate - manual review needed", color: "text-yellow-500" },
  red: { label: "Reject", description: "Low return or high risk - reject", color: "text-red-500" },
} as const;

export const DEFAULT_RE_INPUTS: RealEstateInputs = {
  arv: 300000,
  purchasePrice: 170000,
  repairCosts: 40000,
  closingCostsBuy: 3000,
  closingCostsSell: 8000,
  holdingCostMonthly: 2500,
  holdingMonths: 4,
  agentFees: 15000,
  financingCosts: 5000,
  cashInvested: 50000,
  daysHeld: 120,
  marketGrowthPct: 5,
  rehabRiskMultiplier: 3,
  daysOnMarketRisk: 2,
};

export const DEFAULT_CAR_INPUTS: CarFlipInputs = {
  purchasePrice: 8000,
  expectedSalePrice: 14000,
  repairCosts: 1500,
  auctionFees: 500,
  transportCosts: 300,
  titleRegistration: 200,
  reconditioning: 400,
  advertising: 200,
  taxes: 300,
  cashInvested: 8000,
  daysHeld: 21,
};
