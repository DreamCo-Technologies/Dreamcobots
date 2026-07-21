'use strict';

/**
 * ProfitEngine — calculates ROI and net profit for deals, flips, jobs, and grants.
 */

function calculateDeal(deal) {
  const price = parseFloat(deal.current || deal.price || 0);
  const coupon = parseFloat(deal.coupon || 0);
  const cashback = parseFloat(deal.cashback || 0);
  const resale = parseFloat(deal.resale || 0);
  const finalCost = Math.max(0, price - coupon - cashback);
  const profit = resale > 0 ? resale - finalCost : cashback + coupon;
  const roi = finalCost > 0 ? (profit / finalCost) * 100 : 0;
  return {
    finalCost: Math.round(finalCost * 100) / 100,
    profit: Math.round(profit * 100) / 100,
    roi: Math.round(roi * 10) / 10,
  };
}

function calculateFlip(buyPrice, sellPrice, feesPct = 0.13) {
  const gross = sellPrice - buyPrice;
  const fees = sellPrice * feesPct;
  const net = gross - fees;
  const roi = buyPrice > 0 ? (net / buyPrice) * 100 : 0;
  return {
    gross: Math.round(gross * 100) / 100,
    fees: Math.round(fees * 100) / 100,
    net: Math.round(net * 100) / 100,
    roi: Math.round(roi * 10) / 10,
  };
}

function calculateJob(hourlyRate, hoursPerWeek, weeksPerYear = 52) {
  const annual = hourlyRate * hoursPerWeek * weeksPerYear;
  const monthly = annual / 12;
  return {
    hourlyRate,
    annual: Math.round(annual * 100) / 100,
    monthly: Math.round(monthly * 100) / 100,
  };
}

function calculateGrant(grantAmount, applicationCost = 0, successRate = 0.1) {
  const expectedValue = grantAmount * successRate - applicationCost;
  return {
    grantAmount,
    applicationCost,
    successRate,
    expectedValue: Math.round(expectedValue * 100) / 100,
  };
}

module.exports = { calculateDeal, calculateFlip, calculateJob, calculateGrant };
