export type LocalTestTier = "free" | "pro" | "enterprise" | "elite";

export interface LocalTestEntitlement {
  hasActiveSubscription: true;
  tier: LocalTestTier;
  source: "local_test_entitlement";
  isTestEntitlement: true;
  owner: string;
  message: string;
}

const VALID_TIERS = new Set<LocalTestTier>(["free", "pro", "enterprise", "elite"]);

function enabled(value: string | undefined): boolean {
  return value === "1" || value === "true" || value === "yes";
}

export function getLocalTestEntitlement(env: NodeJS.ProcessEnv = process.env): LocalTestEntitlement | null {
  if (!enabled(env.DREAMCO_ENABLE_LOCAL_TEST_ACCOUNT)) return null;
  if (env.NODE_ENV === "production") return null;

  const requestedTier = (env.DREAMCO_LOCAL_TEST_TIER || "elite").toLowerCase() as LocalTestTier;
  const tier = VALID_TIERS.has(requestedTier) ? requestedTier : "elite";
  const owner = env.DREAMCO_LOCAL_TEST_OWNER || "local-owner";

  return {
    hasActiveSubscription: true,
    tier,
    source: "local_test_entitlement",
    isTestEntitlement: true,
    owner,
    message: "Local test entitlement only. This does not create, change, or prove a paid Stripe subscription.",
  };
}
