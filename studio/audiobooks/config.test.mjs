import { test } from "node:test"
import assert from "node:assert/strict"
import { ROOT, resolveEndpoint, isWithinRoot, mediaUrl, trackId } from "./config.js"

function location(origin) {
  const url = new URL(origin)
  return { origin: url.origin, protocol: url.protocol, hostname: url.hostname }
}

test("Cloudflare uses the public HTTPS library, not a private address", () => {
  assert.equal(resolveEndpoint("auto", location("https://notes.melyi.uk")), "https://melyi.uk:8089/alist")
})

test("NUC HTTP and HTTPS keep their own origin and mapped port", () => {
  assert.equal(resolveEndpoint("auto", location("http://10.0.0.85:8088")), "http://10.0.0.85:8088/alist")
  assert.equal(resolveEndpoint("auto", location("https://melyi.uk")), "https://melyi.uk:8089/alist")
  assert.equal(resolveEndpoint("auto", location("https://melyi.uk:8089")), "https://melyi.uk:8089/alist")
})

test("HTTPS cannot select an insecure LAN endpoint, safely falls back to external HTTPS", () => {
  assert.equal(resolveEndpoint("lan", location("https://notes.melyi.uk")), "https://melyi.uk:8089/alist")
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

test("production resolver reports unmapped intro and outro honestly", async () => {
  const { resolvePlaybackSegment, SYNC_STATE } = await import("./readalong-sync.js")
  const timeline = [
    { start: 16.908, end: 22.588, fragment: "seg1" },
    { start: 22.588, end: 26.788, fragment: "seg2" },
    { start: 26.788, end: 27.748, fragment: "seg3" },
  ]
  assert.equal(resolvePlaybackSegment(timeline, 10).state, SYNC_STATE.BEFORE_START)
  assert.equal(resolvePlaybackSegment(timeline, 18).segment.fragment, "seg1")
  assert.equal(resolvePlaybackSegment(timeline, 22.588).segment.fragment, "seg2")
  assert.equal(resolvePlaybackSegment(timeline, 27).segment.fragment, "seg3")
  assert.equal(resolvePlaybackSegment(timeline, 50).state, SYNC_STATE.AFTER_END)
  assert.equal(resolvePlaybackSegment(timeline, 50).segment, null)
})

