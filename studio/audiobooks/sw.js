const CACHE = "garden-audiobooks-v3"
const SHELL = ["./", "./app.js", "./config.js", "./app.css", "./manifest.webmanifest", "./icon.svg", "./icon-180.png", "./icon-192.png", "./icon-512.png"]
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)))
})
self.addEventListener("activate", event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith("garden-audiobooks-") && key !== CACHE).map(key => caches.delete(key)))))
})
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url)
  const shell = SHELL.map(file => new URL(file, self.registration.scope).href)
  // Never intercept API calls, signed streams, Range requests, or other Garden pages.
  if (event.request.method !== "GET" || event.request.headers.has("Range") || !shell.includes(url.href)) return
  event.respondWith(fetch(event.request).then(response => {
    // Access login redirects and error documents must not replace the app shell.
    if (response.ok && !response.redirected && response.type !== "opaque") {
      const copy = response.clone()
      event.waitUntil(caches.open(CACHE).then(cache => cache.put(event.request, copy)))
    }
    return response
  }).catch(() => caches.match(event.request)))
})
