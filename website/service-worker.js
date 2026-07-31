const SHELL_CACHE = 'buddy-shell-v23';
const RUNTIME_CACHE = 'buddy-runtime-v23';
const APP_SHELL = [
  './',
  './buddy.html',
  './buddy.css?v=23',
  './buddy.js?v=23',
  './install.html',
  './install.css',
  './install.js',
  './leads.html',
  './leads.css',
  './leads.js',
  './calculator.html',
  './studio.html',
  './studio.css',
  './studio.js',
  './crypto.html',
  './crypto.css',
  './crypto.js',
  './government.html',
  './government.css',
  './government.js',
  './data-control.html',
  './data-control.css',
  './data-control.js',
  './models.html',
  './models.css',
  './models.js',
  './open-model-lab.html',
  './open-model-lab.css',
  './open-model-lab.js',
  './test-center.html',
  './test-center.css',
  './test-center.js',
  './styles.css',
  './nav.js',
  './manifest.webmanifest',
  './data/buddy-routing-index.js',
  './data/buddy-model-router.js',
  './data/buddy-model-benchmarks.js',
  './data/buddy-open-model-coding-lab.js',
  './data/repository-test-registry.json',
  './data/buddy-capability-certifications.js',
  './data/buddy-distribution-catalog.json',
  './data/buddy-specialized-hubs.js',
  './data/buddy-production-group.js',
  './data/buddy-local-media-engines.js?v=17',
  './data/buddy-workforce-system.js?v=23',
  './data/buddy-setup-catalog.js?v=23',
  './assets/images/favicon.svg',
  './assets/images/buddy-icon-192.png',
  './assets/images/buddy-icon-512.png'
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
