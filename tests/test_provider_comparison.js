const assert = require('assert');
const { rankProviders } = require('../money/provider_comparison');
const ranked = rankProviders([
  { providerId:'bank-a', effectiveRate:.020, monthlyFee:20, disclosedDreamcoRevenue:5, riskAdjustment:50 },
  { providerId:'bank-b', effectiveRate:.018, monthlyFee:10, disclosedDreamcoRevenue:100, riskAdjustment:10 },
], { monthlyVolume:100000, baselineAnnualCost:30000 });
assert.strictEqual(ranked[0].providerId, 'bank-b');
assert(ranked[0].savingsVsBaseline > 0);
assert(ranked[0].disclosed);
console.log('provider comparison tests passed');
