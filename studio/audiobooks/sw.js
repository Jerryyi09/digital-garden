importScripts("./offline-worker.js")
const CACHE = "garden-audiobooks-v63-network-first"
const SHELL = ["./", "./app.js", "./offline-store.js", "./offline-range.js", "./offline-worker.js", "./guide-math.js", "./user-sync.js", "./sync-store.js", "./readalong-sync.js", "./timeline-loader.js", "./readalong-loader.js", "./search-client.js", "./config.js", "./summaries.js", "./app.css", "./pdf-viewer.html", "./manifest.webmanifest", "./icon.svg", "./icon-180.png", "./icon-192.png", "./icon-512.png"]
SHELL.push(...["./vendor/pdf/pdf.min.js", "./vendor/pdf/pdf.worker.min.js", "./vendor/katex/katex.js", "./vendor/katex/katex.min.css", "./vendor/katex/fonts/KaTeX_AMS-Regular.woff2", "./vendor/katex/fonts/KaTeX_Caligraphic-Bold.woff2", "./vendor/katex/fonts/KaTeX_Caligraphic-Regular.woff2", "./vendor/katex/fonts/KaTeX_Fraktur-Bold.woff2", "./vendor/katex/fonts/KaTeX_Fraktur-Regular.woff2", "./vendor/katex/fonts/KaTeX_Main-Bold.woff2", "./vendor/katex/fonts/KaTeX_Main-BoldItalic.woff2", "./vendor/katex/fonts/KaTeX_Main-Italic.woff2", "./vendor/katex/fonts/KaTeX_Main-Regular.woff2", "./vendor/katex/fonts/KaTeX_Math-BoldItalic.woff2", "./vendor/katex/fonts/KaTeX_Math-Italic.woff2", "./vendor/katex/fonts/KaTeX_SansSerif-Bold.woff2", "./vendor/katex/fonts/KaTeX_SansSerif-Italic.woff2", "./vendor/katex/fonts/KaTeX_SansSerif-Regular.woff2", "./vendor/katex/fonts/KaTeX_Script-Regular.woff2", "./vendor/katex/fonts/KaTeX_Size1-Regular.woff2", "./vendor/katex/fonts/KaTeX_Size2-Regular.woff2", "./vendor/katex/fonts/KaTeX_Size3-Regular.woff2", "./vendor/katex/fonts/KaTeX_Size4-Regular.woff2", "./vendor/katex/fonts/KaTeX_Typewriter-Regular.woff2"])

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
  const mathAsset = cleanHref.startsWith(new URL("./vendor/katex/", self.registration.scope).href)
  // Never intercept API calls, signed streams, Range requests, or other Garden pages.
  if (event.request.method !== "GET" || event.request.headers.has("Range") || (!shell.includes(cleanHref) && !mathAsset)) return

  // Network-first for the app shell (revalidated, 304 when unchanged), cache only when offline,
  // so a deploy takes effect on the next load instead of after the HTTP cache expires.
  const cacheKey = new Request(cleanHref)
  event.respondWith(
    fetch(event.request, { cache: "no-cache", credentials: "same-origin" }).then(networkResponse => {
      if (networkResponse.ok && !networkResponse.redirected && networkResponse.type !== "opaque") {
        const copy = networkResponse.clone()
        caches.open(CACHE).then(cache => cache.put(cacheKey, copy))
        return networkResponse
      }
      return caches.match(cacheKey).then(cached => cached || networkResponse)
    }).catch(() => caches.match(cacheKey))
  )
})
