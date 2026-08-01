import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const html = fs.readFileSync('website/studio.html', 'utf8');
const script = fs.readFileSync('website/studio.js', 'utf8');
const config = JSON.parse(fs.readFileSync('config/buddy-creator-showrunner.json', 'utf8'));

test('Studio exposes every governed creator-show format', () => {
  assert.equal(config.formats.length, 6);
  for (const format of config.formats) {
    assert.match(html, new RegExp(`value=["']${format.id}["']`));
    assert.match(script, new RegExp(`['"]${format.id}['"]`));
    assert.equal(format.routes.length >= 4, true, format.id);
  }
});

test('character library is open ended while active production units are bounded', () => {
  assert.equal(config.character_library.application_character_limit, null);
  assert.equal(config.character_library.active_characters_per_production_unit, 100);
  assert.match(html, /no application-level character-count cap/i);
  assert.match(script, /activeProductionCast\(\)\.length > 100/);
  assert.match(script, /dreamco\.buddy\.character-library\.v1/);
  assert.match(script, /raw_media_embedded: false/);
});

test('show packets include calendars, continuity, platform variants, and truthful release state', () => {
  assert.match(script, /schema: 'dreamco\.buddy_creator_show_plan\.v1'/);
  assert.match(script, /show_bible_and_season_plan_ready/);
  assert.match(script, /channel_connected: false/);
  assert.match(script, /content_published: false/);
  assert.match(script, /publish_requires_exact_owner_approval: true/);
  assert.match(script, /quality_and_safety_gates/);
  assert.match(script, /character continuity/);
});

test('learning and simulation shows require measurable objectives', () => {
  assert.match(html, /id="show-learning-objectives"/);
  assert.match(script, /\['learning_series', 'simulation_series'\]\.includes\(selectedType\(\)\)/);
  assert.match(config.quality_and_safety_gates.join(' '), /learning objective/i);
  assert.match(config.quality_and_safety_gates.join(' '), /safe failure/i);
});
