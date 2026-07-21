#!/usr/bin/env node

const { RevenueLedger } = require('./revenue-ledger');

const ledger = new RevenueLedger();
const reportPath = ledger.writeMarkdownReport();
const summary = ledger.writeSummaries().summary;

console.log(`Stripe revenue report written to ${reportPath}`);
console.log(`Tracked events: ${summary.totalEvents}`);
console.log(`Gross tracked revenue: $${(summary.grossRevenueCents / 100).toFixed(2)}`);
console.log(`Failed attempted revenue: $${(summary.failedRevenueCents / 100).toFixed(2)}`);
