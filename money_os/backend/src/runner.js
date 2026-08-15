const jobs = [
  'deal_hunter',
  'penny_deal',
  'coupon_stack',
  'receipt_match',
  'flip_finder',
  'settlement_finder',
  'profit_ranker'
];

console.log(JSON.stringify({ mode: process.env.MONEY_OS_MODE || 'dry-run', jobs, status: 'ready_for_authorized_adapters' }, null, 2));
