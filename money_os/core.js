export function calculateEconomics({price=0,coupon=0,cashback=0,fees=0,shipping=0,resale=0}) {
  const acquisitionCost = Math.max(0, price - coupon - cashback);
  const netProfit = resale - acquisitionCost - fees - shipping;
  const roi = acquisitionCost > 0 ? netProfit / acquisitionCost : (netProfit > 0 ? Infinity : 0);
  return { acquisitionCost, netProfit, roi };
}

export function scoreOpportunity(o) {
  const profit = Number(o.netProfit ?? calculateEconomics(o).netProfit);
  const roi = Number(o.roi ?? calculateEconomics(o).roi);
  const confidence = Number(o.confidence ?? 0);
  const effort = Number(o.effort ?? 5);
  const freshness = Number(o.freshness ?? 0.5);
  const score = Math.max(0, profit) * 0.45 + Math.min(Math.max(roi,0),10) * 8 * 0.25 + confidence * 20 * 0.2 + freshness * 10 * 0.1 - effort * 1.5;
  return Number(score.toFixed(2));
}

export function validateOpportunity(o) {
  const errors=[];
  if (!o.source) errors.push('missing source');
  if (!o.title) errors.push('missing title');
  if (o.url && !/^https?:\\/\\//i.test(o.url)) errors.push('invalid url');
  if (o.claimType === 'legal' && o.proofRequirement === 'none' && o.eligibilityVerified !== true) errors.push('legal claim requires eligibility verification');
  if (Number(o.netProfit ?? 0) < 0) errors.push('negative net profit');
  return {valid: errors.length===0, errors};
}

export const SOURCE_CLASSES = Object.freeze({
  deals:['price-drop','coupon','clearance','penny'],
  receipts:['receipt-reward','cashback'],
  legal:['class-action','settlement','unclaimed-money'],
  work:['fiverr','job','lead'],
  property:['real-estate','government-contract','grant'],
  resale:['marketplace','auction']
});

export function routeOpportunity(o) {
  if (o.category === 'legal') return 'legal_money_bot';
  if (o.category === 'deal' || o.category === 'coupon') return 'deal_hunter';
  if (o.category === 'receipt') return 'receipt_rewards';
  if (o.category === 'resale') return 'flip_finder';
  if (o.category === 'grant' || o.category === 'government-contract') return 'government_money';
  if (o.category === 'job' || o.category === 'fiverr') return 'work_revenue';
  if (o.category === 'real-estate') return 'real_estate';
  return 'global_opportunity_router';
}
