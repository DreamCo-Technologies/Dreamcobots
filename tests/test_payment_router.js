const assert = require('assert');
const { rankOptions, selectRoute } = require('../money/payment_router');

const options = rankOptions([
  { providerId: 'a', approvalRate: .97, p95LatencyMs: 250, effectiveCostRate: .030, healthScore: .99 },
  { providerId: 'b', approvalRate: .98, p95LatencyMs: 180, effectiveCostRate: .020, healthScore: .995 },
]);
assert.strictEqual(options[0].providerId, 'b');
const route = selectRoute(options);
assert.strictEqual(route.selected.providerId, 'b');
assert.strictEqual(route.executionRequired, true);
console.log('payment router tests passed');
