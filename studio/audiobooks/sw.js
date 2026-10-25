const CACHE = "garden-audiobooks-v27-no-flash"
const SHELL = ["./", "./app.js", "./readalong-sync.js", "./config.js", "./summaries.js", "./app.css", "./pdf-viewer.html", "./manifest.webmanifest", "./icon.svg", "./icon-180.png", "./icon-192.png", "./icon-512.png"]

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting()))
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
  const shell = SHELL.map(file => new URL(file, self.registration.scope).href)
  // Never intercept API calls, signed streams, Range requests, or other Garden pages.
  if (event.request.method !== "GET" || event.request.headers.has("Range") || !shell.includes(url.href)) return

  // Stale-While-Revalidate for instant loading of app shell
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        if (networkResponse.ok && !networkResponse.redirected && networkResponse.type !== "opaque") {
          const copy = networkResponse.clone()
          caches.open(CACHE).then(cache => cache.put(event.request, copy))
        }
        return networkResponse
      }).catch(() => cachedResponse)

      return cachedResponse || fetchPromise
    })
  )
})
