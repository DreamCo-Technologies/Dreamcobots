import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const script = readFileSync(new URL('../website/os-observability.js', import.meta.url), 'utf8');
const actionsHtml = readFileSync(new URL('../website/actions.html', import.meta.url), 'utf8');
const osHtml = readFileSync(new URL('../website/os.html', import.meta.url), 'utf8');
const pagesFeed = JSON.parse(readFileSync(new URL('../website/data/os-observability-metrics.json', import.meta.url), 'utf8'));
const reportStub = JSON.parse(readFileSync(new URL('../reports/os-observability-metrics.stub.json', import.meta.url), 'utf8'));

function makeRoot() {
  const attributes = {};
  return {
    innerHTML: '',
    attributes,
    setAttribute(name, value) {
      attributes[name] = String(value);
    },
  };
}

async function mountWith(fetchImpl) {
  const roots = [makeRoot(), makeRoot()];
  const events = [];
  const fetchCalls = [];
  const document = {
    readyState: 'complete',
    head: { appendChild() {} },
    getElementById() {
      return null;
    },
    createElement() {
      return {};
    },
    querySelectorAll(selector) {
      assert.equal(selector, '[data-os-observability]');
      return roots;
    },
    addEventListener() {
      throw new Error('mount must run immediately when the document is already loaded');
    },
  };
  class CustomEvent {
    constructor(type, init) {
      this.type = type;
      this.detail = init && init.detail;
    }
  }
  const window = {
    dispatchEvent(event) {
      events.push(event);
      return true;
    },
  };
  const context = {
    document,
    window,
    CustomEvent,
    fetch(url, options) {
      fetchCalls.push({ url, options });
      return fetchImpl(url, options);
    },
  };
  vm.runInNewContext(script, context, { filename: 'website/os-observability.js' });
  for (let i = 0; i < 5; i += 1) await new Promise((resolve) => setImmediate(resolve));
  return { roots, events, fetchCalls };
}

function jsonResponse(payload, ok = true, status = 200) {
  return Promise.resolve({ ok, status, json: () => Promise.resolve(payload) });
}

function tileStates(html) {
  return [...html.matchAll(/class="os-obs-tile"[^>]*data-state="([a-z]+)"[^>]*data-id="([^"]*)"/g)].map((m) => ({ state: m[1], id: m[2] }));
}

function surfaceStates(html) {
  return [...html.matchAll(/class="os-obs-surface" data-state="([a-z]+)"/g)].map((m) => m[1]);
}

test('OS observability strip fails closed to yellow when the feed cannot be fetched', async () => {
  const { roots, events, fetchCalls } = await mountWith(() => Promise.reject(new Error('network down')));
  assert.equal(fetchCalls.length, 1);
  assert.equal(fetchCalls[0].url, 'data/os-observability-metrics.json');
  assert.equal(fetchCalls[0].options.cache, 'no-store');
  for (const root of roots) {
    assert.equal(root.attributes['data-os-obs-ready'], '1');
    assert.equal(root.attributes['data-production-ready'], 'false');
    assert.match(root.innerHTML, /network down/);
    assert.deepEqual(surfaceStates(root.innerHTML), ['yellow', 'yellow', 'yellow', 'yellow']);
    assert.doesNotMatch(root.innerHTML, /data-state="green"/);
  }
  assert.equal(events.length, 0, 'fail-closed path must not broadcast a tile_state event');
});

test('OS observability strip fails closed on HTTP errors and non-object JSON', async () => {
  for (const respond of [() => jsonResponse({}, false, 404), () => jsonResponse(null)]) {
    const { roots } = await mountWith(respond);
    assert.equal(roots[0].attributes['data-production-ready'], 'false');
    assert.match(roots[0].innerHTML, /HTTP 404|invalid json/);
    assert.deepEqual(surfaceStates(roots[0].innerHTML), ['yellow', 'yellow', 'yellow', 'yellow']);
    assert.doesNotMatch(roots[0].innerHTML, /data-state="green"/);
  }
});

test('OS observability tiles never promote evidence-free or unknown states to green', async () => {
  const payload = {
    provenance: { evidence_complete: false },
    surfaces: { actions: { state: 'green' }, pr: { state: 'red' }, issues: { state: 'bogus' } },
    aggregate: { os_green_pct: null, counts: { green: 1, red: 1, yellow: 2 } },
    metrics: [
      { id: 'green_without_evidence', label: 'G no evidence', state: 'green', value: 99, unit: '%', evidence: { present: false } },
      { id: 'green_missing_evidence', label: 'G missing', state: 'green', value: 1 },
      { id: 'unknown_state', label: 'Unknown', state: 'teal', value: null },
      { id: 'red_metric', label: 'Red', state: 'red', value: 3 },
      { id: 'green_with_evidence', label: 'G evidence', state: 'green', value: true, evidence: { present: true } },
    ],
    production_ready: false,
  };
  const { roots, events } = await mountWith(() => jsonResponse(payload));
  const html = roots[0].innerHTML;
  assert.deepEqual(tileStates(html), [
    { state: 'yellow', id: 'green_without_evidence' },
    { state: 'yellow', id: 'green_missing_evidence' },
    { state: 'yellow', id: 'unknown_state' },
    { state: 'red', id: 'red_metric' },
    { state: 'green', id: 'green_with_evidence' },
  ]);
  // Surfaces cannot show green while provenance says evidence is incomplete; missing surfaces stay yellow.
  assert.deepEqual(surfaceStates(html), ['yellow', 'red', 'yellow', 'yellow']);
  assert.match(html, /Fail-closed stub/);
  assert.equal(events.length, 1);
  assert.equal(events[0].type, 'dreamco:observability.tile_state');
  assert.equal(events[0].detail.evidence_complete, false);
  assert.equal(events[0].detail.production_ready, false);
});

test('OS observability strip refuses a production_ready claim from the stub feed', async () => {
  const payload = {
    provenance: { evidence_complete: true },
    surfaces: { actions: { state: 'green' }, pr: { state: 'green' }, issues: { state: 'green' }, agents: { state: 'green' } },
    aggregate: { os_green_pct: 100, os_soak_ok: true, counts: { green: 1, red: 0, yellow: 0 } },
    metrics: [{ id: 'ok', label: 'OK', state: 'green', value: 100, unit: '%', evidence: { present: true } }],
    production_ready: true,
  };
  const { roots, events } = await mountWith(() => jsonResponse(payload));
  for (const root of roots) {
    assert.equal(root.attributes['data-production-ready'], 'false');
    assert.match(root.innerHTML, /production_ready=false/);
    assert.match(root.innerHTML, /Control-plane evidence loaded/);
    assert.deepEqual(surfaceStates(root.innerHTML), ['green', 'green', 'green', 'green']);
  }
  assert.equal(events.length, 1);
  assert.equal(events[0].detail.production_ready, false);
  assert.equal(events[0].detail.evidence_complete, true);
});

test('Shipped OS observability feed is a fail-closed stub with no vanity green', () => {
  assert.deepEqual(pagesFeed, reportStub, 'Pages feed must match the reviewed report stub');
  assert.equal(pagesFeed.production_ready, false);
  assert.equal(pagesFeed.provenance.evidence_complete, false);
  assert.equal(pagesFeed.anti_vanity.yellow_never_counts_as_green, true);
  assert.equal(pagesFeed.aggregate.counts.green, 0);
  assert.equal(pagesFeed.aggregate.os_green_pct, null);
  assert.ok(pagesFeed.metrics.length > 0);
  assert.equal(pagesFeed.aggregate.counts.yellow + pagesFeed.aggregate.counts.red, pagesFeed.metrics.length);
  for (const metric of pagesFeed.metrics) {
    assert.notEqual(metric.state, 'green', `${metric.id} must not be green without evidence`);
    assert.equal(metric.evidence.present, false, `${metric.id} must not claim evidence in the stub`);
  }
  for (const surface of Object.values(pagesFeed.surfaces)) assert.notEqual(surface.state, 'green');
});

test('Actions and OS pages mount the observability strip and load its script', () => {
  for (const html of [actionsHtml, osHtml]) {
    assert.match(html, /class="os-obs-strip" data-os-observability/);
    assert.match(html, /<script src="os-observability\.js\?v=\d+"><\/script>/);
  }
});
