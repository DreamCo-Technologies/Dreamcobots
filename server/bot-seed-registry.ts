import type { InsertBotProfile } from "@shared/schema";
import { ALL_BOTS as CORE_BOTS } from "./seed-bots";
import { GITHUB_BOTS } from "./seed-github-bots";
import { CODELAB_BOTS } from "./seed-codelabs";
import { SUPPLEMENTAL_BOTS } from "./seed-supplemental-bots";

type SeedSources = {
  core: InsertBotProfile[];
  github: InsertBotProfile[];
  codelab: InsertBotProfile[];
  supplemental: InsertBotProfile[];
};

/** Slugs that appear more than once, in first-seen order. */
export function findDuplicateBotSlugs(bots: Pick<InsertBotProfile, "slug">[]): string[] {
  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const bot of bots) {
    if (seen.has(bot.slug)) duplicates.add(bot.slug);
    seen.add(bot.slug);
  }
  return [...duplicates];
}

/**
 * Builds the runtime seed list served by server/routes.ts.
 * GitHub and CodeLab profiles that overlap a core slug are intentionally dropped;
 * every other repeated slug (including repeats inside one seed file) is an error.
 */
export function composeBotSeeds(sources: SeedSources = {
  core: CORE_BOTS,
  github: GITHUB_BOTS,
  codelab: CODELAB_BOTS,
  supplemental: SUPPLEMENTAL_BOTS,
}): InsertBotProfile[] {
  const coreSlugs = new Set(sources.core.map((bot) => bot.slug));
  const githubSlugs = new Set(sources.github.map((bot) => bot.slug));
  const dedupedGithub = sources.github.filter((bot) => !coreSlugs.has(bot.slug));
  const dedupedCodelab = sources.codelab.filter((bot) => !coreSlugs.has(bot.slug) && !githubSlugs.has(bot.slug));
  const bots = [...sources.core, ...dedupedGithub, ...dedupedCodelab, ...sources.supplemental];
  const duplicates = findDuplicateBotSlugs(bots);
  if (duplicates.length) {
    throw new Error(`Bot seeds contain duplicate canonical/supplemental identities: ${duplicates.join(", ")}`);
  }
  return bots;
}

export const ALL_BOTS = composeBotSeeds();
