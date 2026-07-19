import { useQuery } from "@tanstack/react-query";

export type SubscriptionTier = "free" | "pro" | "enterprise" | "elite" | null;

export interface SubscriptionStatus {
  hasActiveSubscription: boolean;
  tier: SubscriptionTier;
}

const TIER_RANK: Record<string, number> = {
  free: 0,
  pro: 1,
  enterprise: 2,
  elite: 3,
};

export function useSubscriptionTier() {
  return useQuery<SubscriptionStatus>({
    queryKey: ["/api/stripe/subscription-status"],
    staleTime: 60_000,
  });
}

/**
 * Returns true if the bot is accessible at the user's subscription tier.
 * Returns false if the bot requires a higher tier.
 * Returns null if the bot's tier is missing/unknown — callers must render a
 * neutral state (neither "Unlocked" nor "Locked") in this case.
 */
export function isBotUnlocked(
  botTier: string | null | undefined,
  subscriptionTier: SubscriptionTier
): boolean | null {
  if (botTier == null || botTier.trim() === "") return null;
  const normalized = botTier.toLowerCase();
  if (normalized === "free") return true;
  if (!subscriptionTier) return false;
  return (TIER_RANK[subscriptionTier] ?? -1) >= (TIER_RANK[normalized] ?? 99);
}
