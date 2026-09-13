import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const source = fs.readFileSync('server/oauth-login.ts', 'utf8');
const page = fs.readFileSync('website/sign-in.html', 'utf8');
const browser = fs.readFileSync('website/sign-in.js', 'utf8');

test('Google and Apple OAuth use backend-only credentials and verified callback state', () => {
  assert.match(source, /GOOGLE_OAUTH_CLIENT_ID/);
  assert.match(source, /APPLE_OAUTH_CLIENT_ID/);
  assert.match(source, /AUTH_SESSION_SECRET/);
  assert.match(source, /randomBytes\(32\)/);
  assert.match(source, /verifyIdToken/);
  assert.match(source, /Identity-token signature did not verify/);
  assert.match(source, /SameSite=Lax/);
  assert.match(source, /rateLimit/);
  assert.match(source, /oauthStartRateLimit/);
  assert.match(source, /oauthCallbackRateLimit/);
  assert.match(source, /standardHeaders: "draft-8"/);
  assert.doesNotMatch(page + browser, /type=["'](?:password|hidden)["']|localStorage.*secret|sessionStorage.*secret/i);
});

test('the public sign-in page does not claim Pages itself can authenticate users', () => {
  assert.match(page, /GitHub Pages cannot authenticate by itself/);
  assert.match(browser, /\/api\/auth\/\$\{provider\.provider\}\/start/);
  assert.match(browser, /\/api\/auth\/providers/);
});
