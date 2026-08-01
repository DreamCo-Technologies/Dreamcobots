import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const html = readFileSync('website/search.html', 'utf8');
const script = readFileSync('website/dream-search.js', 'utf8');
const css = readFileSync('website/dream-search.css', 'utf8');

test('DreamSearch page exposes local, web, filter, and Buddy controls', () => {
  for (const id of [
    'dream-search-form', 'dream-search-input', 'search-mode-dreamco', 'search-mode-web',
    'search-type-filter', 'search-division-filter', 'search-evidence-filter', 'search-results',
    'search-ask-buddy', 'web-provider-links', 'web-ask-buddy', 'web-local-approval', 'web-local-open',
  ]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `missing #${id}`);
  }
  assert.match(html, /data\/dreamco-search-index\.js/);
  assert.match(html, /DreamSearch does not crawl or invent web results/);
});

test('DreamSearch renders repository records without injecting indexed HTML', () => {
  assert.doesNotMatch(script, /innerHTML\s*=/);
  assert.match(script, /textContent\s*=/);
  assert.match(script, /evidence_level/);
  assert.match(script, /roadmap/);
  assert.match(script, /reference_catalog/);
});

test('DreamSearch web mode remains user initiated and privacy gated', () => {
  assert.doesNotMatch(script, /fetch\(['"]https?:\/\//);
  assert.match(script, /noopener noreferrer/);
  assert.match(script, /web-local-approval/);
  assert.match(script, /buddy-local-token/);
  assert.match(script, /approved: true/);
});

test('DreamSearch layout has responsive stable controls', () => {
  assert.match(css, /grid-template-columns:/);
  assert.match(css, /@media \(max-width: 640px\)/);
  assert.match(css, /height: 60px/);
  assert.doesNotMatch(css, /font-size:\s*[^;]*vw/);
  assert.doesNotMatch(css, /letter-spacing:\s*-/);
});
