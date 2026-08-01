import assert from "node:assert/strict";
import test from "node:test";

import {
  createCryptoMiningPlan,
  createCryptoWalletPlan,
  createDreamCoinPlan,
  cryptoMiningPlanRequestSchema,
  cryptoWalletPlanRequestSchema,
  dreamCoinPlanRequestSchema,
} from "../server/crypto-safety-policy";

test("wallet plans keep custody and signing secrets outside Buddy", () => {
  const parsed = cryptoWalletPlanRequestSchema.parse({
    networkFamily: "bitcoin",
    purpose: "Track a business treasury without spending access",
    custodyMode: "watch_only",
    transactionMode: "observe",
    ownerApproval: true,
  });
  const plan = createCryptoWalletPlan(parsed);
  assert.equal(plan.custody.privateKeysAccepted, false);
  assert.equal(plan.custody.seedPhrasesAccepted, false);
  assert.equal(plan.liveFundsMoved, false);
  assert.equal(cryptoWalletPlanRequestSchema.safeParse({ ...parsed, seedPhrase: "never accept this" }).success, false);
});

test("mining is a bounded cost simulation and blocks unauthorized mining", () => {
  const parsed = cryptoMiningPlanRequestSchema.parse({
    network: "example proof-of-work network",
    deviceCount: 2,
    wattsPerDevice: 1000,
    electricityUsdPerKwh: 0.1,
    expectedDailyRevenueUsd: 8,
    ownerApproval: true,
  });
  const plan = createCryptoMiningPlan(parsed);
  assert.equal(plan.estimate.dailyKwh, 48);
  assert.equal(plan.estimate.dailyEnergyCostUsd, 4.8);
  assert.equal(plan.liveMiningStarted, false);
  assert.ok(plan.blocked.includes("browser cryptojacking"));
});

test("DreamCoin remains a testnet design until launch gates pass", () => {
  const parsed = dreamCoinPlanRequestSchema.parse({
    purpose: "Test a transparent reward unit for a closed prototype.",
    proposedNetwork: "local_devnet",
    ownerApproval: true,
  });
  const plan = createDreamCoinPlan(parsed);
  assert.equal(plan.status, "design_and_testnet_only");
  assert.equal(plan.tokenCreated, false);
  assert.equal(plan.mainnetContractVerified, false);
});
