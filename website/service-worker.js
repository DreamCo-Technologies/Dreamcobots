const SHELL_CACHE = 'buddy-shell-v41';
const RUNTIME_CACHE = 'buddy-runtime-v41';
const APP_SHELL = [
  './',
  './buddy.html',
  './buddy.css?v=28',
  './buddy.js?v=28',
  './success.html',
  './success.css?v=2',
  './success.js?v=4',
  './robot-avatar.js?v=1',
  './search.html',
  './dream-search.css',
  './dream-search.js',
  './install.html',
  './install.css',
  './install.js',
  './leads.html',
  './leads.css',
  './leads.js',
  './calculator.html',
  './studio.html',
  './studio.css?v=22',
  './studio.js?v=22',
  './practice.html',
  './practice.css?v=1',
  './practice.js?v=1',
  './crypto.html',
  './crypto.css',
  './crypto.js',
  './government.html',
  './government.css',
  './government.js',
  './data-control.html',
  './data-control.css',
  './data-control.js?v=3',
  './models.html',
  './models.css?v=3',
  './models.js?v=2',
  './connections.html',
  './connections.js?v=4',
  './data/buddy-connection-catalog.json?v=2',
  './open-model-lab.html',
  './open-model-lab.css',
  './open-model-lab.js',
  './security.html',
  './security.css?v=1',
  './security.js',
  './test-center.html',
  './test-center.css',
  './test-center.js',
  './styles.css?v=41',
  './nav.js',
  './manifest.webmanifest',
  './data/buddy-routing-index.js',
  './data/dreamco-search-index.js',
  './data/buddy-model-router.js',
  './data/buddy-model-benchmarks.js',
  './data/ai-organization-intelligence.js?v=1',
  './data/buddy-open-model-coding-lab.js',
  './data/buddy-open-secure-ai-defense.js',
  './data/buddy-success-program.js?v=2',
  './data/repository-test-registry.json',
  './data/buddy-fleet-quality-program.js',
  './data/buddy-capability-certifications.js',
  './data/buddy-distribution-catalog.json',
  './data/buddy-specialized-hubs.js',
  './data/buddy-production-group.js?v=22',
  './data/buddy-local-media-engines.js?v=22',
  './data/buddy-media-quality-lab.js?v=22',
  './data/buddy-practice-lab.js?v=1',
  './data/buddy-connected-life.js?v=1',
  './data/buddy-communication-behavior.js?v=26',
  './data/buddy-workforce-system.js?v=23',
  './data/buddy-setup-catalog.js?v=25',
  './assets/images/favicon.svg',
  './assets/images/buddy-icon-192.png',
  './assets/images/buddy-icon-512.png',
  './assets/images/buddy-futuristic-v1.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  const allowed = new Set([SHELL_CACHE, RUNTIME_CACHE]);
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => !allowed.has(key)).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

async function networkFirst(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  try {
    const response = await fetch(request);
    if (response.ok) await cache.put(request, response.clone());
    return response;
  } catch (error) {
    return (await cache.match(request, { ignoreSearch: true }))
      || (await caches.match('./buddy.html'))
      || Response.error();
  }
}

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(RUNTIME_CACHE);
    await cache.put(request, response.clone());
  }
  return response;
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.includes('/api/')) return;
  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request));
    return;
  }
  event.respondWith(cacheFirst(request));
});
