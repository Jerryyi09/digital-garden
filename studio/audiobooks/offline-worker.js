importScripts("./offline-range.js")
// Offline data has its own cache lifecycle; shell upgrades never evict downloads.
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url)
  if (url.origin !== self.location.origin || !url.pathname.startsWith("/studio/audiobooks/offline-data/")) return
  event.respondWith((async () => {
    const cache = await caches.open("garden-offline-library-v1")
    return globalThis.gardenOfflineFileResponse(cache, event.request.url, event.request.headers.get("Range"))
  })())
})
