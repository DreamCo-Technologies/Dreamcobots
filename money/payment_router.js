/**
 * DreamPayments routing policy core.
 * Calculation/decision support only: provider adapters remain responsible for
 * authorized payment execution, compliance controls, and credential handling.
 */

function n(v) { const x = Number(v); return Number.isFinite(x) ? x : 0; }

function scoreOption(option, context = {}) {
  const approval = n(option.approvalRate);
  const latency = Math.max(n(option.p95LatencyMs), 1);
  const cost = Math.max(n(option.effectiveCostRate), 0);
  const health = Math.min(Math.max(n(option.healthScore ?? 1), 0), 1);
  const merchantPreference = context.preferredProvider && option.providerId === context.preferredProvider ? 0.05 : 0;
  // Merchant economics and transaction success dominate provider preference.
  return (approval * 0.40) + (health * 0.25) + (1 / latency * 1000 * 0.10) + ((1 - Math.min(cost, 1)) * 0.20) + merchantPreference;
}

function rankOptions(options, context = {}) {
  return options
    .filter(o => o && o.eligible !== false)
    .map(o => ({ ...o, routingScore: scoreOption(o, context) }))
    .sort((a, b) => b.routingScore - a.routingScore);
}

function selectRoute(options, context = {}) {
  const ranked = rankOptions(options, context);
  return {
    selected: ranked[0] || null,
    alternatives: ranked.slice(1),
    reason: ranked[0] ? 'highest evidence-backed merchant/transaction score' : 'no eligible route',
    executionRequired: true,
  };
}

module.exports = { scoreOption, rankOptions, selectRoute };
