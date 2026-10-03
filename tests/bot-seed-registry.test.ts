import assert from "node:assert/strict";
import test from "node:test";

import { ALL_BOTS, composeBotSeeds, findDuplicateBotSlugs } from "../server/bot-seed-registry.ts";
import { ALL_BOTS as CORE_BOTS } from "../server/seed-bots.ts";
import { GITHUB_BOTS } from "../server/seed-github-bots.ts";
import { CODELAB_BOTS } from "../server/seed-codelabs.ts";
import { SUPPLEMENTAL_BOTS } from "../server/seed-supplemental-bots.ts";
import { buildFleetCatalog } from "../tools/generate_bot_fleet_catalog.ts";

const sources = { core: CORE_BOTS, github: GITHUB_BOTS, codelab: CODELAB_BOTS, supplemental: SUPPLEMENTAL_BOTS };

test("runtime bot seeds served by server/routes.ts have unique slugs", () => {
  assert.deepEqual(findDuplicateBotSlugs(ALL_BOTS), []);
  assert.equal(new Set(ALL_BOTS.map((bot) => bot.slug)).size, ALL_BOTS.length);
});

test("each seed file is internally free of duplicate slugs", () => {
  for (const [name, bots] of Object.entries(sources)) {
    assert.deepEqual(findDuplicateBotSlugs(bots), [], `${name} seed file repeats a slug`);
  }
});

test("duplicate slugs are rejected with the offending slugs named", () => {
  const [first, second] = CORE_BOTS;
  const repeated = { ...second, slug: first.slug, displayName: "Distinct Bot Sharing A Slug" };
  assert.throws(
    () => composeBotSeeds({ ...sources, core: [first, repeated] }),
    new RegExp(`duplicate canonical/supplemental identities: ${first.slug}$`),
  );
  const supplementalClash = { ...SUPPLEMENTAL_BOTS[0], slug: first.slug };
  assert.throws(() => composeBotSeeds({ ...sources, supplemental: [supplementalClash] }), /duplicate/);
});

test("GitHub and CodeLab overlaps with core slugs are still dropped, not thrown", () => {
  const overlap = { ...GITHUB_BOTS[0], slug: CORE_BOTS[0].slug };
  const bots = composeBotSeeds({ ...sources, github: [overlap, ...GITHUB_BOTS], codelab: [{ ...CODELAB_BOTS[0], slug: GITHUB_BOTS[0].slug }] });
  assert.equal(bots.filter((bot) => bot.slug === CORE_BOTS[0].slug).length, 1);
  assert.equal(bots.filter((bot) => bot.slug === GITHUB_BOTS[0].slug).length, 1);
});

test("every published catalog profile (1,101 across 55 divisions) keeps a runtime seed", () => {
  const catalog = buildFleetCatalog();
  const runtimeSlugs = new Set(ALL_BOTS.map((bot) => bot.slug));
  const published = [...catalog.bots, ...catalog.supplemental_bots];
  assert.equal(published.length, 1101);
  assert.equal(catalog.divisions.length + catalog.supplemental_divisions.length, 55);
  assert.deepEqual(published.filter((bot) => !runtimeSlugs.has(bot.identity.slug)).map((bot) => bot.identity.slug), []);
  for (const bot of published) {
    const seed = ALL_BOTS.find((item) => item.slug === bot.identity.slug)!;
    assert.equal(seed.division, bot.identity.division, `${bot.identity.slug} runtime seed division drifted from catalog`);
  }
});
