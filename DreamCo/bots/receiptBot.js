'use strict';

function run(options = {}) {
  const { items = [] } = options;
  const cashbackSources = ['Ibotta', 'Fetch Rewards', 'Rakuten', 'Checkout 51', 'Dosh'];
  const receipts = items.length > 0 ? items : ['Groceries', 'Electronics', 'Household'];
  const matched = receipts.map((item, i) => ({
    item,
    source: cashbackSources[i % cashbackSources.length],
    cashback: parseFloat((Math.random() * 5 + 0.5).toFixed(2)),
  }));
  const revenue = matched.reduce((sum, m) => sum + m.cashback, 0);
  return {
    bot: 'receiptBot',
    revenue: parseFloat(revenue.toFixed(2)),
    action: `Scanned ${receipts.length} receipt items for cashback`,
    timestamp: new Date().toISOString(),
    matched,
    totalCashback: parseFloat(revenue.toFixed(2)),
  };
}

module.exports = { run };
