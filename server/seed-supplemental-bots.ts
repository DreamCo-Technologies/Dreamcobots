import { readFileSync, readdirSync } from "node:fs";
import { join, resolve } from "node:path";
import type { InsertBotProfile } from "@shared/schema";

export type SupplementalProfile = {
  slug: string;
  displayName: string;
  division: string;
  tier: string;
  category: string;
  description: string;
  capabilities: string[];
  revenueModel: string;
  targetUsers: string;
  priceRange: string;
  status: string;
  systemPrompt?: string;
};

/** Growth sources are preserved separately; this does not promote production ability. */
export function loadSupplementalBotSources(root = process.cwd()) {
  const directory = resolve(root, "App_bots");
  const seen = new Set<string>();
  return readdirSync(directory).filter((name) => name.endsWith(".json")).sort().flatMap((name) => {
    const source = JSON.parse(readFileSync(join(directory, name), "utf8"));
    if (source.growth !== true) return [];
    if (!Array.isArray(source.bots) || source.total !== source.bots.length || !source.division) {
      throw new Error(`${name}: invalid supplemental division`);
    }
    return source.bots.map((bot: SupplementalProfile) => {
      for (const field of ["slug", "displayName", "description", "category", "tier"] as const) {
        if (typeof bot[field] !== "string" || !bot[field].trim()) throw new Error(`${name}: missing ${field}`);
      }
      if (seen.has(bot.slug)) throw new Error(`Duplicate supplemental bot slug: ${bot.slug}`);
      seen.add(bot.slug);
      if (!Array.isArray(bot.capabilities) || !bot.capabilities.length ||
          bot.capabilities.some((capability) => typeof capability !== "string" || !capability.trim())) {
        throw new Error(`${name}: invalid capabilities for ${bot.slug}`);
      }
      return { source: `App_bots/${name}`, profile: { ...bot, division: source.division } as SupplementalProfile };
    });
  });
}

export function buildSupplementalBotSeeds(root = process.cwd()): InsertBotProfile[] {
  return loadSupplementalBotSources(root).map(({ profile, source }) => ({
    slug: profile.slug,
    displayName: profile.displayName,
    division: profile.division,
    category: profile.category,
    tier: profile.tier,
    description: profile.description,
    capabilities: [...profile.capabilities],
    revenueModel: profile.revenueModel,
    targetUsers: profile.targetUsers,
    priceRange: profile.priceRange,
    status: "sandbox",
    isDefault: false,
    systemPrompt: `${profile.systemPrompt || `You are ${profile.displayName}. ${profile.description} Declared capabilities: ${profile.capabilities.join("; ")}.`} This is a supplemental historical profile. Provide a reviewable sandbox plan. Do not claim completed external actions or production readiness without outcome evidence and the required owner approval.`,
    traits: { division: profile.division, source, supplemental: true, executionScope: "sandbox_plan", productionVerified: false },
  }));
}

export const SUPPLEMENTAL_BOTS = buildSupplementalBotSeeds();
