/**
 * Merchant Value Engine
 *
 * Purpose: help a store owner reduce verified operating/transaction costs while
 * giving DreamCo a transparent, consent-based way to earn from value created.
 *
 * This module is calculation/decision support only. It does not move money,
 * change processors, or enroll a merchant without explicit authorization.
 */

function num(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function compareOffer(current, candidate) {
  const currentRate = num(current.percentRate) + num(current.fixedFee) / Math.max(num(current.averageTicket), 1);
  const candidateRate = num(candidate.percentRate) + num(candidate.fixedFee) / Math.max(num(candidate.averageTicket), 1);
  const monthlySavings = Math.max(0, num(current.monthlyVolume) * (currentRate - candidateRate));
  return {
    monthlySavings,
    annualSavings: monthlySavings * 12,
    currentEffectiveRate: currentRate,
    candidateEffectiveRate: candidateRate,
    merchantBenefits: monthlySavings > 0,
    requiresMerchantApproval: true,
  };
}

function revenueShare({ verifiedMerchantSavings, shareRate = 0.10 }) {
  const savings = Math.max(0, num(verifiedMerchantSavings));
  const rate = Math.min(Math.max(num(shareRate), 0), 0.50);
  const dreamcoShare = savings * rate;
  return {
    verifiedMerchantSavings: savings,
    shareRate: rate,
    dreamcoShare,
    merchantRetainedSavings: savings - dreamcoShare,
    requiresExplicitAgreement: true,
  };
}

function transactionLedgerEvent({ merchantId, transactionId, grossAmount, processorFees, currency = 'USD' }) {
  return {
    merchantId,
    transactionId,
    grossAmount: num(grossAmount),
    processorFees: num(processorFees),
    netAmount: num(grossAmount) - num(processorFees),
    currency,
    timestamp: new Date().toISOString(),
    attribution: 'merchant-value-engine',
  };
}

module.exports = { compareOffer, revenueShare, transactionLedgerEvent };
