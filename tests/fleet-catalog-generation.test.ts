import assert from "node:assert/strict";
import test from "node:test";
import { buildFleetCatalog } from "../tools/generate_bot_fleet_catalog.ts";

test("fleet catalog generator compiles and keeps domain divisions separate from specialist portfolios", () => {
  const catalog = buildFleetCatalog();
  const domainNames = new Set([
    ...catalog.divisions.map((division) => division.name),
    ...catalog.supplemental_divisions.map((division) => division.name),
  ]);
  const portfolioNames = new Set(catalog.supplemental_bots.map((bot) => bot.identity.division));
  assert.ok(domainNames.size > 0);
  assert.ok([...portfolioNames].some((name) => !domainNames.has(name)));
  for (const bot of [...catalog.bots, ...catalog.supplemental_bots]) {
    assert.ok(bot.identity.division);
    assert.ok(domainNames.has(bot.identity.division) || portfolioNames.has(bot.identity.division));
  }
});
