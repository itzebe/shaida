/* SHAIDA service worker.
 *
 * Purpose: keep the app shell usable with no connectivity, which the official Track 3 and
 * Track 5 briefs require. It deliberately caches only static assets — never API responses —
 * because a stale cached report could mislead a reviewer, and a cached "verified" result
 * would be worse than no result at all.
 */

const SHELL_CACHE = 'shaida-shell-v1'
const SHELL_ASSETS = ['/', '/index.html', '/manifest.webmanifest', '/icon.svg']

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS)).then(() => self.skipWaiting()),
  )
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SHELL_CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Never cache API traffic: reviewers must always see live data or an honest error.
  if (url.pathname.startsWith('/v1/')) return

  if (request.method !== 'GET') return

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached
      return fetch(request)
        .then((response) => {
          if (response.ok && url.origin === self.location.origin) {
            const copy = response.clone()
            caches.open(SHELL_CACHE).then((cache) => cache.put(request, copy))
          }
          return response
        })
        .catch(() => caches.match('/index.html'))
    }),
  )
})
