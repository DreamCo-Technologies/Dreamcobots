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

export function isBotUnlocked(botTier: string | null | undefined, subscriptionTier: SubscriptionTier): boolean {
  const normalized = (botTier ?? "free").toLowerCase();
  if (normalized === "free") return true;
  if (!subscriptionTier) return false;
  return (TIER_RANK[subscriptionTier] ?? -1) >= (TIER_RANK[normalized] ?? 99);
}
