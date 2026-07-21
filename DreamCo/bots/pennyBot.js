'use strict';

function run(options = {}) {
  const { threshold = 1.0 } = options;
  const stores = ['Dollar General', 'Walmart', 'Walgreens', 'CVS', 'Target'];
  const pennyDeals = stores.map((store, i) => ({
    id: `penny-${i + 1}`,
    name: `Clearance Item ${i + 1}`,
    store,
    current: parseFloat((Math.random() * threshold).toFixed(2)),
    original: parseFloat((Math.random() * 20 + 5).toFixed(2)),
    type: 'clearance',
  }));
  const revenue = pennyDeals.reduce((sum, d) => sum + (d.original - d.current), 0);
  return {
    bot: 'pennyBot',
    revenue: parseFloat(revenue.toFixed(2)),
    action: `Scanned ${pennyDeals.length} penny/clearance deals`,
    timestamp: new Date().toISOString(),
    pennyDeals,
  };
}

module.exports = { run };
