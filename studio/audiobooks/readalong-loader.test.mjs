import test from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import vm from "node:vm"
import * as loader from "./readalong-loader.js"
import { timelinePathForSource } from "./timeline-loader.js"

const sources = [1, 2].map(n => ({ id: `Volume ${n}/01.mp3`, name: "01.mp3" }))
const track = { path: "/library/book/Volume 2/01.mp3", name: "01.mp3" }

test("exact volume paths win over earlier basename matches", () => {
  assert.equal(loader.matchAudioSource(sources, track, "Volume 2/01.mp3"), sources[1])
  assert.equal(loader.matchAudioSource(sources, track, "other/01.mp3"), null)
  assert.equal(loader.matchAudioSource([sources[0]], track, "other/01.mp3"), sources[0])
  const rows = sources.map(source => ({ audioSourceId: source.id }))
  rows.push({ audioSourceId: "01.mp3" })
  assert.deepEqual(loader.segmentsForTrack(rows, sources, sources[1], track, "Volume 2/01.mp3"), [rows[1]])
  assert.deepEqual(loader.segmentsForTrack(rows, sources, null, track, "other/01.mp3"), [])
})

test("manifest traversal includes every ancestor and stops at the root", () => {
  assert.deepEqual(loader.manifestDirectories("/library/book/part/disc/01.mp3", "/library"),
    ["/library/book/part/disc", "/library/book/part", "/library/book", "/library"])
  assert.deepEqual(loader.manifestDirectories("/library-other/01.mp3", "/library"), [])
})

test("EPUB discovery paginates beyond the first 50 entries", async () => {
  const pages = []
  const epub = { name: "book.epub" }
  const result = await loader.findEpubInPages("/book", async (_path, page) => {
    pages.push(page)
    return { total: 201, content: page === 1 ? Array.from({ length: 200 }, () => ({ name: "01.mp3" })) : [epub] }
  }, () => true)
  assert.equal(result, epub)
  assert.deepEqual(pages, [1, 2])
})

test("cache evicts least recent entries, expires manifests, and skips huge timelines", () => {
  let now = 0
  const cache = new loader.ReadalongCache({ maxEntries: 2, maxWeight: 3, weight: x => x.length, ttl: 30, now: () => now })
  cache.set("a", [1]); cache.set("b", [2]); cache.get("a"); cache.set("c", [3])
  assert.equal(cache.get("b"), undefined)
  cache.set("huge", [1, 2, 3, 4])
  assert.equal(cache.get("huge"), undefined)
  assert.equal(cache.totalWeight, 2)
  now = 30
  assert.equal(cache.get("a"), undefined)
  cache.clear()
  assert.equal(cache.totalWeight, 0)
})

const source = fs.readFileSync(new URL("./app.js", import.meta.url), "utf8")
const implementation = source.slice(source.indexOf("async function setupReadalong("), source.indexOf("async function setupPdf("))
function harness() {
  const elements = new Map()
  const $ = id => {
    if (!elements.has(id)) elements.set(id, { hidden: false, srcdoc: "", label: {}, querySelector() { return this.label } })
    return elements.get(id)
  }
  const ctx = vm.createContext({ ...loader, $, ROOT: "/library", account: () => "user", endpoint: "local",
    directoryPassword: "", playRequest: 1, invalidateReadalong() {}, closeReadalong() {}, openReadalong() {},
    manifestMemoryCache: new loader.ReadalongCache(), timelineMemoryCache: new loader.ReadalongCache(),
    mediaUrl: (_endpoint, info) => info.path, timelinePathForSource, readalongActive: false,
    api: async () => ({ sign: "" }), fetch: async () => ({ json: async () => ({ schemaVersion: 1, readalongEnabled: false }) }) })
  vm.runInContext(implementation, ctx)
  return ctx
}
const deferred = () => { let resolve, reject; const promise = new Promise((a, b) => { resolve = a; reject = b }); return { promise, resolve, reject } }

for (const phase of ["manifest lookup", "manifest fetch", "EPUB listing", "EPUB listing error"]) {
  test(`stale ${phase} cannot change the new reader`, async () => {
    const ctx = harness()
    const pending = deferred()
    const entered = deferred()
    if (phase === "manifest fetch") ctx.fetch = () => { entered.resolve(); return pending.promise }
    else ctx.api = route => {
      if (phase === "manifest lookup" || route === "fs/list") { entered.resolve(); return pending.promise }
      return Promise.resolve({ sign: "" })
    }
    const work = ctx.setupReadalong(track, 1)
    await entered.promise
    ctx.playRequest = 2
    ctx.$("dock-readalong").hidden = false
    ctx.$("readalong-frame").srcdoc = "NEW_BOOK"
    if (phase.endsWith("error")) pending.reject(new Error("listing failed"))
    else pending.resolve(phase === "manifest fetch" ? { json: async () => ({ schemaVersion: 1, readalongEnabled: false }) } : { content: [] })
    await work
    assert.equal(ctx.$("dock-readalong").hidden, false)
    assert.equal(ctx.$("readalong-frame").srcdoc, "NEW_BOOK")
  })
}

test("deep-volume setup loads only the exact source shard and restores the reader button", async () => {
  const ctx = harness()
  const manifest = { schemaVersion: 1, assetRevision: "a".repeat(32), audioSources: sources,
    textRoot: "text/", timelineFormat: "per-audio-source-v1", timelineIndex: "index.json" }
  const requests = []
  ctx.$("dock-readalong").onclick = () => { throw new Error("stale EPUB handler") }
  ctx.api = async (_route, { path }) => {
    requests.push(path)
    if (path.includes("Volume 2/readalong")) throw new Error("no manifest")
    return { sign: "" }
  }
  ctx.fetch = async url => ({ json: async () => url.endsWith("manifest.json") ? manifest
    : url.endsWith("index.json") ? { files: { "Volume 1/01.mp3": "wrong.json", "Volume 2/01.mp3": "right.json" } }
    : [{ audioSourceId: "Volume 2/01.mp3", start: 0, end: 2 }] })
  await ctx.setupReadalong(track, 1)
  assert.ok(requests.some(path => path.endsWith("/right.json")))
  assert.ok(!requests.some(path => path.endsWith("/wrong.json")))
  assert.equal(ctx.readalongTimeline.length, 1)
  assert.equal(ctx.$("dock-readalong").onclick, ctx.openReadalong)
})
