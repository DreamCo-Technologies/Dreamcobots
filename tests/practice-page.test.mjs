import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const catalogSource = fs.readFileSync('website/data/buddy-practice-lab.js', 'utf8');
const html = fs.readFileSync('website/practice.html', 'utf8');
const source = fs.readFileSync('website/practice.js', 'utf8');
const studioHtml = fs.readFileSync('website/studio.html', 'utf8');
const studioSource = fs.readFileSync('website/studio.js', 'utf8');
const fleet = JSON.parse(fs.readFileSync('website/data/bot-fleet-catalog.json', 'utf8'));
const context = { window: {} };
vm.runInNewContext(catalogSource, context);
const catalog = context.window.BUDDY_PRACTICE_LAB;

test('practice catalog routes nine modes only to registered fleet specialists', () => {
  assert.equal(catalog.schema, 'dreamco.buddy_practice_lab.v1');
  assert.equal(catalog.modes.length, 9);
  const slugs = new Set(fleet.bots.map((bot) => bot.identity.slug));
  for (const mode of catalog.modes) {
    assert.equal(mode.questions.length >= 6, true, mode.id);
    assert.equal(mode.specialists.length >= 3, true, mode.id);
    mode.specialists.forEach((slug) => assert.equal(slugs.has(slug), true, `${mode.id}:${slug}`));
  }
});

test('practice page provides text and voice rounds without embedding raw audio', () => {
  assert.match(html, /id="practice-record"/);
  assert.match(html, /id="practice-answer"/);
  assert.match(html, /id="practice-send-buddy"/);
  assert.match(source, /new MediaRecorder\(stream\)/);
  assert.match(source, /raw_voice_embedded: false/);
  assert.match(source, /candidate_impersonation_allowed: false/);
  assert.match(source, /protected_trait_inference_allowed: false/);
  assert.match(source, /live_external_action_taken: false/);
});

test('creative studio includes rap, singing, visual production, and bounded multi-take evidence', () => {
  assert.match(studioHtml, /id="voice-performance"/);
  assert.match(studioHtml, /id="voice-fixture"/);
  assert.match(studioHtml, /id="visual-output"/);
  assert.match(studioSource, /function analyzeVoiceBlob\(blob\)/);
  assert.match(studioSource, /voiceTakes\.length >= 12/);
  assert.match(studioSource, /content_or_identity_quality_claimed: false/);
  assert.match(studioSource, /raw_audio_embedded: false/);
  assert.match(studioSource, /raw_image_embedded: false/);
});
