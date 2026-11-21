// Offline app shell. API calls and the voice socket always go to the network.
// Rules that keep the app from ever going blank:
//  - only good (200, same-origin) responses are cached;
//  - the cached page is used only for page loads (navigations), never in place of a script or stylesheet;
//  - each new version replaces the old cache and takes over straight away.
const CACHE = 'bolkhata-v2'
self.addEventListener('install', (e) => {
  self.skipWaiting()
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(['/', '/icon.svg', '/pcm-worklet.js'])).catch(() => {}))
})
self.addEventListener('activate', (e) => e.waitUntil(
  caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()),
))
self.addEventListener('fetch', (e) => {
  const req = e.request
  const url = new URL(req.url)
  if (req.method !== 'GET' || url.origin !== location.origin || url.pathname.startsWith('/api') || url.pathname.startsWith('/ws')) return
  e.respondWith(fetch(req).then((r) => {
    if (r.ok && r.type === 'basic') {
      const copy = r.clone()
      caches.open(CACHE).then((c) => c.put(req, copy))
    }
    return r
  }).catch(async () => {
    const hit = await caches.match(req)
    if (hit) return hit
    if (req.mode === 'navigate') return (await caches.match('/')) || Response.error()
    return Response.error() // a missing script stays missing; never replace it with HTML
  }))
})
