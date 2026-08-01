import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const script = readFileSync('website/robot-avatar.js', 'utf8');
const context = { window: {} };
vm.runInNewContext(script, context);

test('robot identities are deterministic and category-specific', () => {
  const engine = context.window.DREAMCO_ROBOT_AVATAR;
  const first = engine.describe('dreambot', 'CommandCore', 'system');
  const again = engine.describe('dreambot', 'CommandCore', 'system');
  const other = engine.describe('music-bot', 'DreamArts', 'music');
  assert.deepEqual(JSON.parse(JSON.stringify(first)), JSON.parse(JSON.stringify(again)));
  assert.notDeepEqual(JSON.parse(JSON.stringify(first)), JSON.parse(JSON.stringify(other)));
  assert.ok(first.palette.length === 4);
  assert.ok(first.motif);
});

test('all division seeds can produce bounded robot descriptors', () => {
  const programSource = readFileSync('website/data/buddy-success-program.js', 'utf8');
  const dataContext = { window: {} };
  vm.runInNewContext(programSource, dataContext);
  const descriptors = dataContext.window.BUDDY_SUCCESS_PROGRAM.divisions.map((division) =>
    context.window.DREAMCO_ROBOT_AVATAR.describe(division.robot_identity.deterministic_seed, division.name, division.top_categories[0]?.name || 'system'));
  assert.equal(descriptors.length, 45);
  assert.ok(descriptors.every((descriptor) => descriptor.faceWidth >= 78 && descriptor.faceWidth <= 92));
  assert.ok(descriptors.every((descriptor) => descriptor.badgeSides >= 4 && descriptor.badgeSides <= 7));
});

test('all 1,051 fleet profiles receive a stable robot identity code', () => {
  const fleet = JSON.parse(readFileSync('config/generated/bots.catalog.json', 'utf8'));
  const codes = fleet.bots.map((bot) => context.window.DREAMCO_ROBOT_AVATAR.describe(
    bot.identity.slug, bot.identity.division, bot.identity.category,
  ).identityCode);
  assert.equal(codes.length, 1051);
  assert.equal(new Set(codes).size, 1051);
});
