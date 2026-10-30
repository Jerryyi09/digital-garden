const CACHE = "garden-audiobooks-v48-network-first"
const SHELL = ["./", "./app.js", "./user-sync.js", "./sync-store.js", "./readalong-sync.js", "./timeline-loader.js", "./config.js", "./summaries.js", "./app.css", "./pdf-viewer.html", "./manifest.webmanifest", "./icon.svg", "./icon-180.png", "./icon-192.png", "./icon-512.png"]

// Precache bypasses the browser HTTP cache: app.js is served with max-age=14400, and a plain
// cache.addAll() would store that stale copy under the new cache name, so a deploy only reached
// devices hours later. "reload" always goes to the network for the precache.
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(SHELL.map(file => new Request(file, { cache: "reload" }))))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key.startsWith("garden-audiobooks-") && key !== CACHE).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  )
})

self.addEventListener("fetch", event => {
  const url = new URL(event.request.url)
  const cleanHref = url.origin + url.pathname
  const shell = SHELL.map(file => new URL(file, self.registration.scope).href.split("?")[0])
  // Never intercept API calls, signed streams, Range requests, or other Garden pages.
  if (event.request.method !== "GET" || event.request.headers.has("Range") || !shell.includes(cleanHref)) return

  // Network-first for the app shell (revalidated, 304 when unchanged), cache only when offline,
  // so a deploy takes effect on the next load instead of after the HTTP cache expires.
  event.respondWith(
    fetch(event.request, { cache: "no-cache", credentials: "same-origin" }).then(networkResponse => {
      if (networkResponse.ok && !networkResponse.redirected && networkResponse.type !== "opaque") {
        const copy = networkResponse.clone()
        caches.open(CACHE).then(cache => cache.put(event.request, copy))
        return networkResponse
      }
      return caches.match(event.request).then(cached => cached || networkResponse)
    }).catch(() => caches.match(event.request))
  )
})
