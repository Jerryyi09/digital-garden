importScripts("./offline-range.js")
// Offline data has its own cache lifecycle; shell upgrades never evict downloads.
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url)
  if (url.origin !== self.location.origin || !url.pathname.startsWith("/studio/audiobooks/offline-data/")) return
  event.respondWith((async () => {
    const cache = await caches.open("garden-offline-library-v1")
    const response = await cache.match(event.request.url)
    if (!response) return new Response("本机文件已丢失，请重新下载", { status: 404 })
    return globalThis.gardenOfflineRangeResponse(await response.blob(), event.request.headers.get("Range"), response.headers)
  })())
})
