const assert = require('assert');
const { compareOffer, revenueShare, transactionLedgerEvent } = require('../money/merchant_value_engine');

const result = compareOffer(
  { percentRate: 0.029, fixedFee: 0.30, averageTicket: 50, monthlyVolume: 100000 },
  { percentRate: 0.020, fixedFee: 0.10, averageTicket: 50, monthlyVolume: 100000 }
);
assert(result.monthlySavings > 0);
assert.strictEqual(result.requiresMerchantApproval, true);

const share = revenueShare({ verifiedMerchantSavings: 1000, shareRate: 0.10 });
assert.strictEqual(share.dreamcoShare, 100);
assert.strictEqual(share.merchantRetainedSavings, 900);
assert.strictEqual(share.requiresExplicitAgreement, true);

const event = transactionLedgerEvent({ merchantId: 'merchant-test', transactionId: 'txn-test', grossAmount: 100, processorFees: 3 });
assert.strictEqual(event.netAmount, 97);
console.log('merchant value engine tests passed');
