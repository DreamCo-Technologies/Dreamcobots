import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const html = readFileSync('website/connections.html', 'utf8');
const script = readFileSync('website/connections.js', 'utf8');
const styles = readFileSync('website/styles.css', 'utf8');
const catalog = JSON.parse(readFileSync('website/data/buddy-connection-catalog.json', 'utf8'));

test('Access Center unifies connections, authentication methods, and secret storage', () => {
  for (const id of [
    'access-center-panel', 'access-center-summary', 'access-search', 'access-type', 'access-status',
    'access-registry', 'access-row-count', 'access-new-connection', 'access-store-secret', 'access-view-auth',
    'access-connection-count', 'access-secret-location-count', 'access-live-count',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
    if (id !== 'access-center-panel') assert.match(script, new RegExp(`byId\\(["']${id}["']\\)`), `unbound #${id}`);
  }
  assert.equal(catalog.auth_methods.length, 8);
  assert.equal(catalog.platform_profiles.length, 3);
  assert.equal(catalog.secret_stores.length, 3);
  assert.deepEqual(catalog.secret_stores.map((store) => store.id).sort(), ['environment', 'managed_vault', 'os_keychain']);
  assert.match(html, /connections\.js\?v=5/);
  assert.match(script, /buddy-connection-catalog\.json\?v=2/);
  assert.match(styles, /\.access-table-wrap[^{]*\{[^}]*overflow:\s*auto/s);
  assert.match(styles, /\.access-table[^{]*\{[^}]*min-width:/s);
});

test('Access Center exposes only public connection records and secret-reference metadata', () => {
  assert.match(script, /fetch\('\/api\/platform-connections'/);
  assert.match(script, /item\.rawCredentialsExposed === false/);
  assert.match(script, /secretReferenceConfigured === true/);
  assert.match(html, /Credential values are never enumerated/);
  assert.ok(catalog.secret_stores.every((store) => store.enumeration_allowed === false));
  assert.ok(catalog.public_contract.stored_browser_data.includes('secret-reference presence flag'));
  assert.doesNotMatch(script, /console\.(?:log|error|warn)\(/);
});

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
