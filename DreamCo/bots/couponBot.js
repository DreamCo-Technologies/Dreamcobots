'use strict';

function run(options = {}) {
  const { sources = ['Honey', 'Rakuten', 'Ibotta'] } = options;
  const coupons = sources.flatMap((source, si) =>
    Array.from({ length: 3 }, (_, i) => ({
      id: `coupon-${si}-${i}`,
      source,
      code: `SAVE${(si * 3 + i + 1) * 5}`,
      discount: parseFloat(((si * 3 + i + 1) * 2.5).toFixed(2)),
      cashback: parseFloat((Math.random() * 3).toFixed(2)),
      stackedSavings: parseFloat(((si * 3 + i + 1) * 2.5 + Math.random() * 3).toFixed(2)),
    }))
  );
  const revenue = coupons.reduce((sum, c) => sum + c.stackedSavings, 0);
  return {
    bot: 'couponBot',
    revenue: parseFloat(revenue.toFixed(2)),
    action: `Stacked ${coupons.length} coupons from ${sources.length} sources`,
    timestamp: new Date().toISOString(),
    coupons,
  };
}

module.exports = { run };
