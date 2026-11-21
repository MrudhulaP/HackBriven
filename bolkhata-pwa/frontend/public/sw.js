// App-shell cache so the PWA opens without network. API calls and the voice socket always go to the network.
const CACHE = 'bolkhata-v1'
self.addEventListener('install', (e) => e.waitUntil(caches.open(CACHE).then((c) => c.addAll(['/', '/icon.svg', '/pcm-worklet.js']))))
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()))
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url)
  if (e.request.method !== 'GET' || url.pathname.startsWith('/api') || url.pathname.startsWith('/ws')) return
  e.respondWith(fetch(e.request).then((r) => {
    const copy = r.clone()
    caches.open(CACHE).then((c) => c.put(e.request, copy))
    return r
  }).catch(() => caches.match(e.request).then((r) => r || caches.match('/'))))
})
