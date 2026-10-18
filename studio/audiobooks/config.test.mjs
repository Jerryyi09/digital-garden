import { test } from "node:test"
import assert from "node:assert/strict"
import { ROOT, resolveEndpoint, isWithinRoot, mediaUrl, trackId } from "./config.js"

function location(origin) {
  const url = new URL(origin)
  return { origin: url.origin, protocol: url.protocol, hostname: url.hostname }
}

test("Cloudflare uses the public HTTPS library, not a private address", () => {
  assert.equal(resolveEndpoint("auto", location("https://notes.melyi.uk")), "https://melyi.uk/alist")
})

test("NUC HTTP and HTTPS keep their own origin and mapped port", () => {
  assert.equal(resolveEndpoint("auto", location("http://10.0.0.85:8088")), "http://10.0.0.85:8088/alist")
  assert.equal(resolveEndpoint("auto", location("https://melyi.uk")), "https://melyi.uk/alist")
  assert.equal(resolveEndpoint("auto", location("https://melyi.uk:8089")), "https://melyi.uk:8089/alist")
})

test("HTTPS cannot select an insecure LAN endpoint", () => {
  assert.throws(() => resolveEndpoint("lan", location("https://notes.melyi.uk")), /HTTPS/)
})

test("library path checks reject siblings and traversal", () => {
  assert.ok(isWithinRoot(`${ROOT}/历史/第1节.m4b`))
  for (const path of [`${ROOT}备份/file.mp3`, `${ROOT}/../private`, "/", null]) {
    assert.equal(isWithinRoot(path), false)
  }
})

test("signed URL preserves Chinese, spaces, hash and reserved filename characters", () => {
  const path = `${ROOT}/文学/A #?%& 01.m4b`
  const url = new URL(mediaUrl("https://melyi.uk/alist", { path }, "abc:1+/="))
  assert.equal(decodeURIComponent(url.pathname), `/alist/d${path}`)
  assert.equal(url.searchParams.get("sign"), "abc:1+/=")
  assert.equal(url.hash, "")
  assert.throws(() => mediaUrl("https://melyi.uk/alist", { path: "/secret/file.mp3" }, "abc"))
})

test("replacing a file creates a different progress identity", () => {
  const track = { path: `${ROOT}/book.mp3`, size: 100, modified: "2026-10-18" }
  assert.notEqual(trackId(track), trackId({ ...track, size: 200 }))
  assert.notEqual(trackId(track), trackId({ ...track, modified: "2026-10-19" }))
})

test("readalong paths remain strictly within library root", () => {
  const manifestPath = `${ROOT}/心智成长/The Power of Habit - Charles Duhigg/readalong/readalong.manifest.json`
  assert.ok(isWithinRoot(manifestPath))
  assert.equal(isWithinRoot(`${ROOT}/../readalong.manifest.json`), false)
})

test("binary search accurately locates active audio segment", () => {
  const timeline = [
    { start: 16.908, end: 22.588, fragment: "seg1" },
    { start: 22.588, end: 26.788, fragment: "seg2" },
    { start: 26.788, end: 27.748, fragment: "seg3" },
  ]
  function findSegment(list, time) {
    let low = 0, high = list.length - 1
    while (low <= high) {
      const mid = (low + high) >> 1
      const seg = list[mid]
      if (time < seg.start) high = mid - 1
      else if (time >= seg.end) low = mid + 1
      else return seg
    }
    if (high >= 0 && time - list[high].end < 0.6) return list[high]
    if (low < list.length && list[low].start - time < 0.6) return list[low]
    return null
  }
  assert.equal(findSegment(timeline, 10.0), null)
  assert.equal(findSegment(timeline, 18.0)?.fragment, "seg1")
  assert.equal(findSegment(timeline, 22.588)?.fragment, "seg2")
  assert.equal(findSegment(timeline, 27.0)?.fragment, "seg3")
  assert.equal(findSegment(timeline, 27.8)?.fragment, "seg3") // within 0.6s tolerance
  assert.equal(findSegment(timeline, 50.0), null)
})

