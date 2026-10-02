import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = readFileSync('website/service-worker.js', 'utf8');

test('service worker versions and caches benchmark Pages assets together', () => {
  const shell = source.match(/buddy-shell-v(\d+)/)?.[1];
  const runtime = source.match(/buddy-runtime-v(\d+)/)?.[1];
  assert.ok(shell);
  assert.equal(runtime, shell);
  assert.match(source, /\.\/actions\.html/);
  assert.match(source, /\.\/data\/actions-health-report\.json/);
  assert.match(source, /\.\/data\/buddy-demand-ontology\.js\?v=1/);
  assert.match(source, /\.\/data\/buddy-benchmark-index\.js\?v=1/);
  assert.match(source, /\.\/data\/buddy-model-progress-center\.js\?v=2/);
  assert.match(source, /\.\/data\/repository-test-registry\.json\?v=4/);
});

// Exercise the actual worker lifecycle. Old caches deliberately precede new
// caches in insertion order, as they do for an existing Pages visitor.
function workerHarness() {
  const base = 'https://example.github.io/Dreamcobots/';
  const stores = new Map();
  const events = new Map();
  const requests = [];
  let offline = false;
  let claimed = false;
  let waitingSkipped = false;
  const fresh = new Map([
    [new URL('nav.js', base).href, 'current navigation with repository controls'],
    [new URL('data/bot-fleet-catalog.json', base).href, '{"fleet":"current"}'],
  ]);
  const key = request => new URL(typeof request === 'string' ? request : request.url, base).href;
  const network = async request => {
    const url = key(request);
    requests.push(url);
    if (offline) throw new TypeError('Offline');
    return new Response(fresh.get(url) || `current asset: ${url}`, { status: 200 });
  };
  async function open(name) {
    if (!stores.has(name)) stores.set(name, new Map());
    const contents = stores.get(name);
    return {
      async addAll(paths) {
        const responses = await Promise.all(paths.map(network));
        paths.forEach((path, index) => contents.set(key(path), responses[index].clone()));
      },
      async put(request, response) { contents.set(key(request), response.clone()); },
      async match(request, options = {}) {
        const url = key(request);
        let response = contents.get(url);
        if (!response && options.ignoreSearch) {
          const noSearch = value => { const parsed = new URL(value); parsed.search = ''; return parsed.href; };
          response = [...contents].find(([candidate]) => noSearch(candidate) === noSearch(url))?.[1];
        }
        return response?.clone();
      },
    };
  }
  const caches = {
    open,
    async keys() { return [...stores.keys()]; },
    async delete(name) { return stores.delete(name); },
    async match(request, options) {
      for (const name of stores.keys()) {
        const response = await (await open(name)).match(request, options);
        if (response) return response;
      }
    },
  };
  const self = {
    location: { origin: new URL(base).origin },
    addEventListener(name, callback) { events.set(name, callback); },
    skipWaiting() { waitingSkipped = true; },
    clients: { async claim() { claimed = true; } },
  };
  vm.runInNewContext(source, { self, caches, fetch: network, URL, Response }, { filename: 'service-worker.js' });
  return {
    caches, requests, fresh,
    setOffline(value) { offline = value; },
    get claimed() { return claimed; },
    get waitingSkipped() { return waitingSkipped; },
    async lifecycle(name) {
      const promises = [];
      events.get(name)({ waitUntil(promise) { promises.push(promise); } });
      await Promise.all(promises);
    },
    async request(path, mode = 'cors') {
      let result;
      events.get('fetch')({
        request: { url: key(path), method: 'GET', mode },
        respondWith(promise) { result = promise; },
      });
      assert.ok(result, 'same-origin GET must be handled by the worker');
      return result;
    },
  };
}

test('v60 visitors upgrade nav and fleet data, retire old caches, and keep the new shell offline', async () => {
  const worker = workerHarness();
  const shellName = source.match(/const SHELL_CACHE = '([^']+)'/)[1];
  const runtimeName = source.match(/const RUNTIME_CACHE = '([^']+)'/)[1];
  assert.notEqual(shellName, 'buddy-shell-v60', 'release must change the worker and shell cache version');
  assert.notEqual(runtimeName, 'buddy-runtime-v60', 'release must retire the old runtime cache');
  const oldShell = await worker.caches.open('buddy-shell-v60');
  const oldRuntime = await worker.caches.open('buddy-runtime-v60');
  await oldShell.put('./nav.js', new Response('obsolete navigation'));
  await oldRuntime.put('./data/bot-fleet-catalog.json', new Response('{"fleet":"obsolete"}'));
  // Before installation, this visitor reproduces the stale cache-first result.
  assert.equal(await (await worker.request('nav.js')).text(), 'obsolete navigation');
  assert.equal(await (await worker.request('data/bot-fleet-catalog.json')).text(), '{"fleet":"obsolete"}');
  assert.equal(worker.requests.length, 0);

  await worker.lifecycle('install');
  assert.equal(worker.waitingSkipped, true);
  assert.equal(await (await oldShell.match('./nav.js')).text(), 'obsolete navigation', 'install stages a separate cache');
  const currentRuntime = await worker.caches.open(runtimeName);
  await currentRuntime.put('./current-evidence.txt', new Response('preserve current runtime'));
  await worker.lifecycle('activate');
  assert.deepEqual(new Set(await worker.caches.keys()), new Set([shellName, runtimeName]));
  assert.equal(worker.claimed, true);
  assert.equal(await (await currentRuntime.match('./current-evidence.txt')).text(), 'preserve current runtime');

  const requestsAfterInstall = worker.requests.length;
  worker.setOffline(true);
  for (const [url, expected] of worker.fresh) {
    assert.equal(await (await worker.request(url)).text(), expected);
  }
  assert.equal(worker.requests.length, requestsAfterInstall, 'new shell is available without another network request');
});
