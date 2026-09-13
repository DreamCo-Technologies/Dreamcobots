import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const catalogSource = fs.readFileSync('website/data/buddy-practice-lab.js', 'utf8');
const html = fs.readFileSync('website/practice.html', 'utf8');
const source = fs.readFileSync('website/practice.js', 'utf8');
const studioHtml = fs.readFileSync('website/studio.html', 'utf8');
const studioSource = fs.readFileSync('website/studio.js', 'utf8');
const buddyPageSource = fs.readFileSync('client/src/pages/BuddyPage.tsx', 'utf8');
const conversationPageSource = fs.readFileSync('client/src/pages/ConversationPage.tsx', 'utf8');
const sandboxPageSource = fs.readFileSync('client/src/pages/SandboxPage.tsx', 'utf8');
const settingsPageSource = fs.readFileSync('client/src/pages/SettingsPage.tsx', 'utf8');
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

test('creative studio wires every static button and exposes an honest permission-free media self-test', () => {
  const buttonIds = [...studioHtml.matchAll(/<button\b[^>]*\bid="([^"]+)"[^>]*>/g)].map(([, id]) => id);
  assert.equal(buttonIds.length > 0, true);
  buttonIds.forEach((id) => {
    if (id === 'build-prototype') {
      assert.match(studioSource, /form\.addEventListener\('submit'/);
      return;
    }
    assert.match(studioSource, new RegExp(`getElementById\\('${id}'\\)\\.addEventListener`), `${id} has no direct event handler`);
  });
  assert.match(studioHtml, /id="run-media-self-test"/);
  assert.match(studioHtml, /without requesting camera or microphone access/);
  assert.match(studioSource, /function runMediaSelfTest\(\)/);
  assert.match(studioSource, /No device permission was requested and no generation claim was made/);
  assert.match(studioSource, /Provider rendering<\/span><strong>NOT TESTED/);
});

test('creative studio provides keyless local speech without claiming it is voice cloning', () => {
  assert.match(studioHtml, /id="browser-speech-text"/);
  assert.match(studioHtml, /id="browser-speech-voice"/);
  assert.match(studioHtml, /No account, cloud upload, or API key is required/);
  assert.match(studioHtml, /This is speech synthesis, not voice cloning/);
  assert.match(studioSource, /new SpeechSynthesisUtterance\(text\)/);
  assert.match(studioSource, /Local Buddy voice preview completed without an ElevenLabs key/);
  assert.match(studioSource, /browserSpeechStatus\.dataset\.activity = 'finished'/);
  assert.match(studioSource, /\['interrupted', 'canceled'\]\.includes\(event\.error\)/);
  assert.match(studioSource, /window\.speechSynthesis\.speak\(utterance\)/);
});

test('Buddy media surfaces distinguish keyless local readiness from provider rendering', () => {
  assert.match(buddyPageSource, /Local Voice & Cloning/);
  assert.match(buddyPageSource, /status: "local-setup"/);
  assert.match(buddyPageSource, /setLocation\("\/studio\.html"\)/);
  assert.match(conversationPageSource, /Image route contract reachable/);
  assert.match(conversationPageSource, /successful generated image are still required to prove rendering/);
  assert.match(sandboxPageSource, /Generation requires a verified local renderer or configured provider/);
  assert.match(settingsPageSource, /Keyless browser speech and capture ready/);
  assert.match(settingsPageSource, /install and verify OpenVoice or Chatterbox for local cloning/);
});
