'use strict';

/**
 * RankingAI — scores and ranks opportunities 0–100.
 */

function score(item) {
  let s = 0;
  const profit = parseFloat(item.profit || item.revenue || 0);
  const effort = parseInt(item.effort || 3, 10);
  const fastPayout = Boolean(item.fast_payout || item.fastPayout);

  if (profit > 100) {
    s += 40;
  } else if (profit > 50) {
    s += 30;
  } else if (profit > 20) {
    s += 20;
  } else if (profit > 5) {
    s += 10;
  }

  if (effort <= 1) {
    s += 30;
  } else if (effort === 2) {
    s += 20;
  } else {
    s += 5;
  }

  if (fastPayout) {
    s += 20;
  }

  const category = (item.category || '').toLowerCase();
  if (category === 'electronics' || category === 'appliances') {
    s += 10;
  }

  return Math.min(s, 100);
}

function rank(items) {
  return items
    .map((item) => ({ ...item, rankScore: score(item) }))
    .sort((a, b) => b.rankScore - a.rankScore);
}

function topN(items, n = 10) {
  return rank(items).slice(0, n);
}

module.exports = { score, rank, topN };
