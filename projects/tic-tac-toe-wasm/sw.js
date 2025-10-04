const CACHE_NAME = 'tic-tac-toe-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/pkg/tic_tac_toe_wasm.js',
  '/pkg/tic_tac_toe_wasm_bg.wasm'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});