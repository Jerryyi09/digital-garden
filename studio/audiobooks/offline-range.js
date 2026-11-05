// Shared by the page (offline-store.js) and the Service Worker (offline-worker.js).
//
// Large downloads are stored in fixed-size chunks: WebKit's Cache API buffers a whole
// response body in memory before writing it, so a single multi-hundred-MB cache entry fails
// on iPhone ("Internal error"). A chunked file is a small JSON head at the file's key
// (marked by the X-Garden-Chunks header) plus entries `${key}?chunk=N`, each exactly
// CHUNK_SIZE bytes except the last. Files that fit in one chunk, and everything downloaded
// before chunking existed, are a single raw entry at the key.
globalThis.gardenOfflineChunkSize = 8 * 1024 * 1024
globalThis.gardenOfflineChunkKey = (key, index) => `${key}?chunk=${index}`

function parseRange(range, size) {
  if (!range) return { start: 0, end: size - 1, partial: false }
  const match = /^bytes=(\d*)-(\d*)$/.exec(range)
  let start, end
  if (match && (match[1] || match[2])) {
    start = match[1] ? Number(match[1]) : Math.max(0, size - Number(match[2]))
    end = match[1] && match[2] ? Math.min(Number(match[2]), size - 1) : size - 1
  }
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end || start >= size) return null
  return { start, end, partial: true }
}

function unsatisfiable(size, headers) {
  const out = new Headers(headers)
  out.set("Accept-Ranges", "bytes")
  out.set("Content-Range", `bytes */${size}`)
  return new Response(null, { status: 416, headers: out })
}

globalThis.gardenOfflineRangeResponse = function(blob, range, headers = {}) {
  const out = new Headers(headers)
  out.set("Accept-Ranges", "bytes")
  const span = parseRange(range, blob.size)
  if (!span) return unsatisfiable(blob.size, headers)
  if (!span.partial) { out.set("Content-Length", blob.size); return new Response(blob, { headers: out }) }
  out.set("Content-Range", `bytes ${span.start}-${span.end}/${blob.size}`)
  out.set("Content-Length", span.end - span.start + 1)
  return new Response(blob.slice(span.start, span.end + 1), { status: 206, headers: out })
}

// Response for a stored offline file (raw or chunked), honouring an optional Range header.
// Chunked bodies are streamed one chunk at a time, so memory stays at about one chunk.
globalThis.gardenOfflineFileResponse = async function(cache, key, range = null) {
  const head = await cache.match(key)
  if (!head) return new Response("本机文件已丢失，请重新下载", { status: 404 })
  if (!head.headers.has("X-Garden-Chunks")) return globalThis.gardenOfflineRangeResponse(await head.blob(), range, head.headers)

  const meta = await head.json()
  const headers = { "Content-Type": meta.type || "application/octet-stream" }
  const span = parseRange(range, meta.size)
  if (!span) return unsatisfiable(meta.size, headers)
  const out = new Headers(headers)
  out.set("Accept-Ranges", "bytes")
  out.set("Content-Length", span.end - span.start + 1)
  if (span.partial) out.set("Content-Range", `bytes ${span.start}-${span.end}/${meta.size}`)

  let index = Math.floor(span.start / meta.chunkSize)
  const last = Math.floor(span.end / meta.chunkSize)
  const body = new ReadableStream({
    async pull(controller) {
      if (index > last) return controller.close()
      const chunk = await cache.match(globalThis.gardenOfflineChunkKey(key, index))
      if (!chunk) return controller.error(new Error("本机文件已丢失，请重新下载"))
      const offset = index * meta.chunkSize
      const blob = await chunk.blob()
      const from = Math.max(0, span.start - offset)
      const to = Math.min(blob.size, span.end - offset + 1)
      controller.enqueue(new Uint8Array(await blob.slice(from, to).arrayBuffer()))
      index++
    },
  })
  return new Response(body, { status: span.partial ? 206 : 200, headers: out })
}
