/** Provider-neutral comparison. Decision support only. */
function n(v) { const x = Number(v); return Number.isFinite(x) ? x : 0; }

function compareProvider(provider, context = {}) {
  const monthlyVolume = Math.max(n(context.monthlyVolume), 0);
  const fixedFees = Math.max(n(provider.monthlyFee), 0) + Math.max(n(provider.otherMonthlyFees), 0);
  const variableCost = monthlyVolume * Math.max(n(provider.effectiveRate), 0);
  const switchingCost = Math.max(n(provider.switchingCost), 0);
  const annualCost = (fixedFees + variableCost) * 12 + switchingCost;
  const savingsVsBaseline = n(context.baselineAnnualCost) - annualCost;
  const dreamcoRevenue = Math.max(n(provider.disclosedDreamcoRevenue), 0);
  return {
    providerId: provider.providerId,
    annualCost,
    savingsVsBaseline,
    dreamcoRevenue,
    recommendationScore: savingsVsBaseline - (n(provider.riskAdjustment) + switchingCost),
    disclosed: provider.disclosedDreamcoRevenue !== undefined,
  };
}

function rankProviders(providers, context = {}) {
  return providers.map(p => compareProvider(p, context))
    .filter(p => p.disclosed)
    .sort((a, b) => b.recommendationScore - a.recommendationScore);
}

module.exports = { compareProvider, rankProviders };
