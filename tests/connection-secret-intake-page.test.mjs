import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync('website/connections.html', 'utf8');
const script = readFileSync('website/connections.js', 'utf8');

test('App Connections provides a password-only local Keychain dialog', () => {
  for (const id of ['secret-intake-dialog', 'secret-intake-form', 'secret-intake-account', 'secret-intake-value', 'secret-intake-approval', 'secret-intake-submit']) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
  assert.match(html, /id="secret-intake-value" type="password" autocomplete="new-password"/);
});

test('raw key detection redirects values to the loopback bridge and clears the field', () => {
  assert.match(script, /looksLikeRawSecret/);
  assert.match(script, /fetch\('\/api\/local\/secrets\/store'/);
  assert.match(script, /byId\('secret-intake-value'\)\.value = ''/);
  assert.doesNotMatch(script, /localStorage\.setItem\([^\n]*secret/i);
  assert.doesNotMatch(script, /console\.(?:log|error|warn)\([^\n]*secret/i);
});

test('public and file previews cannot submit keys without a local bridge session token', () => {
  assert.match(script, /sessionStorage\.getItem\(LOCAL_TOKEN_KEY\)/);
  assert.match(script, /Public and file previews never accept raw credentials/);
});
