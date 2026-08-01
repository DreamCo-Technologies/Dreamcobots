import { z } from "zod";

export const CRYPTO_NETWORK_FAMILIES = [
  "bitcoin", "evm", "solana", "cosmos", "substrate", "cardano", "xrpl", "stellar", "near", "other",
] as const;

export const cryptoWalletPlanRequestSchema = z.object({
  networkFamily: z.enum(CRYPTO_NETWORK_FAMILIES),
  purpose: z.string().trim().min(5).max(300),
  custodyMode: z.enum(["watch_only", "hardware_wallet", "multisig", "smart_account"]),
  transactionMode: z.enum(["observe", "draft_for_approval"]).default("observe"),
  ownerApproval: z.literal(true),
}).strict();

export type CryptoWalletPlanRequest = z.infer<typeof cryptoWalletPlanRequestSchema>;

export function createCryptoWalletPlan(input: CryptoWalletPlanRequest) {
  const signingGate = input.transactionMode === "draft_for_approval"
    ? "A user-controlled wallet must display and approve the exact transaction."
    : "No signing or transaction submission is included.";
  return {
    schema: "dreamco.buddy_crypto_wallet_plan.v1",
    status: "sandbox_plan",
    networkFamily: input.networkFamily,
    purpose: input.purpose,
    custodyMode: input.custodyMode,
    transactionMode: input.transactionMode,
    custody: {
      model: "non_custodial",
      privateKeysAccepted: false,
      seedPhrasesAccepted: false,
      secretsStoredByBuddy: false,
      signingGate,
    },
    buildSteps: [
      "Confirm the exact network, asset contract, decimals, and trusted explorer.",
      "Connect a watch-only address or a user-controlled hardware, multisig, or smart-account wallet.",
      "Apply account, network, address, amount, fee, slippage, and allowance checks.",
      "Simulate the transaction and show the full human-readable effect.",
      "Require approval in the user-controlled wallet for every signature.",
      "Record the transaction hash and verification evidence without storing signing secrets.",
    ],
    releaseGates: [
      "chain-specific adapter tests pass",
      "testnet or fork simulation passes",
      "address poisoning and wrong-network tests pass",
      "allowance and approval risk is visible",
      "recovery and incident plan is tested",
      "independent security review is complete",
    ],
    liveFundsMoved: false,
    securityClaim: "No wallet can promise absolute safety; this plan reduces risk and keeps custody with the user.",
  };
}

export const cryptoMiningPlanRequestSchema = z.object({
  network: z.string().trim().min(2).max(80),
  deviceCount: z.number().int().min(1).max(10_000),
  wattsPerDevice: z.number().positive().max(100_000),
  electricityUsdPerKwh: z.number().min(0).max(10),
  expectedDailyRevenueUsd: z.number().min(0).max(10_000_000),
  ownerApproval: z.literal(true),
}).strict();

export type CryptoMiningPlanRequest = z.infer<typeof cryptoMiningPlanRequestSchema>;

export function createCryptoMiningPlan(input: CryptoMiningPlanRequest) {
  const dailyKwh = input.deviceCount * input.wattsPerDevice * 24 / 1000;
  const dailyEnergyCostUsd = dailyKwh * input.electricityUsdPerKwh;
  return {
    schema: "dreamco.buddy_crypto_mining_plan.v1",
    status: "simulation_only",
    network: input.network,
    assumptions: { ...input, ownerApproval: undefined },
    estimate: {
      dailyKwh: Number(dailyKwh.toFixed(3)),
      dailyEnergyCostUsd: Number(dailyEnergyCostUsd.toFixed(2)),
      grossMarginBeforeHardwarePoolTaxUsd: Number((input.expectedDailyRevenueUsd - dailyEnergyCostUsd).toFixed(2)),
    },
    checks: [
      "network permits the proposed mining method",
      "hardware is owner-controlled and dedicated",
      "power circuit, heat, ventilation, noise, and fire risks are reviewed",
      "pool terms, fees, payout thresholds, and jurisdiction rules are verified",
      "hardware depreciation, downtime, taxes, and changing difficulty are modeled",
      "automatic shutdown thresholds are configured",
    ],
    blocked: ["hidden mining", "mining on third-party devices", "browser cryptojacking", "malware", "guaranteed-profit claims"],
    liveMiningStarted: false,
  };
}

export const dreamCoinPlanRequestSchema = z.object({
  purpose: z.string().trim().min(10).max(500),
  proposedNetwork: z.enum(["evm_testnet", "solana_devnet", "local_devnet", "undecided"]),
  ownerApproval: z.literal(true),
}).strict();

export function createDreamCoinPlan(input: z.infer<typeof dreamCoinPlanRequestSchema>) {
  return {
    schema: "dreamco.dreamcoin_launch_plan.v1",
    status: "design_and_testnet_only",
    purpose: input.purpose,
    proposedNetwork: input.proposedNetwork,
    mainnetContractVerified: false,
    marketValueClaimed: false,
    tokenCreated: false,
    requiredBeforeLaunch: [
      "written utility and non-misleading public claims",
      "jurisdiction-specific legal and tax review",
      "supply, distribution, treasury, and governance design",
      "audited contract and reproducible source build",
      "public testnet evidence and incident exercises",
      "multisig administration and recovery controls",
      "verified contract source and public risk disclosure",
    ],
  };
}
