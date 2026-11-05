globalThis.gardenOfflineRangeResponse = function(blob, range, headers = {}) {
  const out = new Headers(headers)
  out.set("Accept-Ranges", "bytes")
  if (!range) { out.set("Content-Length", blob.size); return new Response(blob, { headers: out }) }
  const match = /^bytes=(\d*)-(\d*)$/.exec(range)
  let start, end
  if (match && (match[1] || match[2])) {
    start = match[1] ? Number(match[1]) : Math.max(0, blob.size - Number(match[2]))
    end = match[1] && match[2] ? Math.min(Number(match[2]), blob.size - 1) : blob.size - 1
  }
  if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start > end || start >= blob.size) {
    out.set("Content-Range", `bytes */${blob.size}`)
    return new Response(null, { status: 416, headers: out })
  }
  out.set("Content-Range", `bytes ${start}-${end}/${blob.size}`)
  out.set("Content-Length", end - start + 1)
  return new Response(blob.slice(start, end + 1), { status: 206, headers: out })
}
