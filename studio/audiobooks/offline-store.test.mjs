import test from "node:test"
import assert from "node:assert/strict"
import { OfflineLibrary, rangeResponse, DEFAULT_LIMIT, CHUNK_SIZE } from "./offline-store.js"

class MemoryCache {
  data = new Map()
  async match(key) { return this.data.get(typeof key === 'string' ? key : key.url)?.clone() }
  async put(key, value) { const bytes = await value.arrayBuffer(); this.data.set(key, new Response(bytes, { headers: value.headers })) }
  async delete(key) { return this.data.delete(typeof key === 'string' ? key : key.url) }
  async keys() { return [...this.data.keys()].map(url => ({ url })) }
}
function fixture(extra = {}) {
  const book = "/root/category/book"
  const bytes = new Map([[`${book}/Volume 1/01.mp3`, "abc"], [`${book}/Volume 2/01.mp3`, "def"]])
  const tree = { [book]: [{ name: "Volume 2", is_dir: true }, { name: "Volume 1", is_dir: true }],
    [`${book}/Volume 1`]: [{ name: "01.mp3", size: 3 }], [`${book}/Volume 2`]: [{ name: "01.mp3", size: 3 }] }
  let requests = []
  const cache = new MemoryCache()
  const options = { cache, origin: "https://local.test", owner: "alice", root: "/root", storage: {},
    listRemote: async path => tree[path] || [], fetchFile: async path => { requests.push(path); return new Response(bytes.get(path)) }, ...extra }
  const library = new OfflineLibrary(options)
  return { book, bytes, tree, cache, options, library, requests }
}

test("manual whole-book download persists volume listings and reopens without network", async () => {
  const f = fixture()
  await f.library.open()
  assert.equal(f.library.state.limit, DEFAULT_LIMIT)
  await f.library.download(f.book)
  assert.equal(f.library.used, 6)
  assert.equal(f.library.state.books[f.book].complete, true)
  const reopened = await new OfflineLibrary({ ...f.options, fetchFile: () => { throw new Error("offline") } }).open()
  assert.equal(reopened.listing(f.book).content.length, 2)
  const response = await f.cache.match(reopened.localUrl(`${f.book}/Volume 2/01.mp3`))
  assert.equal(await response.text(), "def")
  const other = await new OfflineLibrary({ ...f.options, owner: "bob" }).open()
  assert.equal(other.localUrl(`${f.book}/Volume 2/01.mp3`), null)
})

test("quota preflight does not start downloading or erase existing files", async () => {
  const f = fixture()
  await f.library.setLimit(5)
  await assert.rejects(f.library.download(f.book), /空间不足/)
  assert.equal(f.requests.length, 0)
  await f.library.setLimit(6)
  await f.library.download(f.book)
  await assert.rejects(f.library.setLimit(5), /不能小于/)
})

test("unknown file sizes still obey streaming limits", async () => {
  const f = fixture()
  f.tree[`${f.book}/Volume 1`][0].size = 0
  f.tree[`${f.book}/Volume 2`][0].size = 0
  await f.library.setLimit(2)
  await assert.rejects(f.library.download(f.book), /上限/)
  assert.equal(f.library.used, 0)
  assert.equal(f.library.state.books[f.book].complete, false)
})

test("interrupted download resumes completed files instead of fetching them twice", async () => {
  const f = fixture()
  const fetchFile = f.library.fetchFile
  let fail = true
  f.library.fetchFile = async path => {
    if (path.includes('Volume 1') && fail) throw new Error("offline")
    return fetchFile(path)
  }
  await assert.rejects(f.library.download(f.book), /offline/)
  assert.equal(f.library.used, 3)
  fail = false
  await f.library.download(f.book)
  assert.equal(f.requests.filter(path => path.includes('Volume 2')).length, 1)
  assert.equal(f.library.used, 6)
})

test("missing cache data is detected after restart", async () => {
  const f = fixture()
  await f.library.download(f.book)
  await f.cache.delete(f.library.localUrl(`${f.book}/Volume 2/01.mp3`))
  const reopened = await new OfflineLibrary(f.options).open()
  // open() only reads the index so start-up is never blocked by per-file checks
  assert.equal(reopened.state.books[f.book].complete, true)
  assert.equal(await reopened.verify(), true)
  assert.equal(reopened.state.books[f.book].complete, false)
  assert.equal(reopened.used, 3)
  const again = await new OfflineLibrary(f.options).open()
  assert.equal(again.state.books[f.book].complete, false, "verify() persists the corrected index")
})

test("status reports none, downloading, partial and complete for the UI", async () => {
  const f = fixture()
  assert.equal(f.library.status(f.book).state, "none")
  const seen = []
  f.library.onChange = () => seen.push(f.library.status(f.book).state)
  const fetchFile = f.library.fetchFile
  let fail = true
  f.library.fetchFile = async path => { if (path.includes("Volume 1") && fail) throw new Error("offline"); return fetchFile(path) }
  await assert.rejects(f.library.download(f.book), /offline/)
  assert.ok(seen.includes("downloading"))
  assert.deepEqual({ ...f.library.status(f.book) }, { state: "partial", done: 1, total: 2, bytes: 3, totalBytes: 6 })
  fail = false
  await f.library.download(f.book)
  assert.equal(f.library.status(f.book).state, "complete")
})

test("pinned release download excludes historical revisions and stores the entry manifest", async () => {
  const f = fixture()
  f.tree[f.book].push({ name: "readalong", is_dir: true }, { name: ".readalong_revisions", is_dir: true })
  const base = `${f.book}/.readalong_revisions/${"a".repeat(32)}`
  f.tree[base] = [{ name: "timeline.json", size: 2 }]
  f.bytes.set(`${f.book}/readalong/readalong.manifest.json`, JSON.stringify({ assetRevision: "a".repeat(32) }))
  f.bytes.set(`${base}/timeline.json`, "[]")
  await f.library.download(f.book)
  assert.ok(f.library.localUrl(`${base}/timeline.json`))
  assert.equal((await (await f.cache.match(f.library.localUrl(`${f.book}/readalong/readalong.manifest.json`))).json()).assetRevision, "a".repeat(32))
})

for (const [range, status, text] of [[null, 200, "abcdef"], ["bytes=1-3", 206, "bcd"], ["bytes=3-", 206, "def"], ["bytes=-2", 206, "ef"], ["bytes=99-", 416, ""], ["bytes=3-1", 416, ""], ["bytes=0-1,3-4", 416, ""]]) {
  test(`offline audio range ${range}`, async () => {
    const response = rangeResponse(new Blob(["abcdef"]), range, { "Content-Type": "audio/mpeg" })
    assert.equal(response.status, status)
    assert.equal(await response.text(), text)
  })
}

test("quota write failure leaves no partial file and remains resumable", async () => {
  const f = fixture()
  const put = f.cache.put.bind(f.cache)
  f.cache.put = async (key, response) => {
    if (key.includes('/file/')) throw new DOMException('full', 'QuotaExceededError')
    return put(key, response)
  }
  await assert.rejects(f.library.download(f.book), { name: 'QuotaExceededError' })
  assert.equal(f.library.used, 0)
  assert.equal(f.library.controller, null)
  f.cache.put = put
  await f.library.download(f.book)
  assert.equal(f.library.state.books[f.book].complete, true)
})

test("pause aborts a stream and retry does not count partial bytes", async () => {
  const f = fixture()
  let paused = false
  f.library.fetchFile = async () => new Response(new ReadableStream({ start(controller) {
    controller.enqueue(new Uint8Array([1]))
    if (!paused) { paused = true; f.library.pause() }
    controller.close()
  } }))
  await assert.rejects(f.library.download(f.book), { name: 'AbortError' })
  assert.equal(f.library.used, 0)
  assert.equal(f.library.controller, null)
})

test("delete removes only the selected account's downloaded bytes", async () => {
  const f = fixture()
  await f.library.download(f.book)
  const other = new OfflineLibrary({ ...f.options, owner: 'bob' })
  await other.download(f.book)
  await f.library.remove(f.book)
  assert.equal(f.library.used, 0)
  assert.ok(await f.cache.match(other.localUrl(`${f.book}/Volume 1/01.mp3`)))
})

test("unsafe filenames and category-wide downloads are rejected", async () => {
  const f = fixture()
  await assert.rejects(f.library.download('/root/category'), /书籍目录/)
  f.tree[f.book] = [{ name: '../other.mp3', size: 3 }]
  await assert.rejects(f.library.download(f.book), /无效路径/)
})

// ── Chunked storage (iPhone "Internal error" on a 288 MB single-file book) ─────────────
const MB = 1024 * 1024
function bigFixture(size, extra = {}) {
  const book = "/root/category/single"
  const data = new Uint8Array(size)
  for (let i = 0; i < size; i++) data[i] = (i * 31 + 7) & 255
  const file = `${book}/book.mp3`
  const cache = new MemoryCache()
  const options = { cache, origin: "https://local.test", owner: "alice", root: "/root", storage: {},
    listRemote: async path => path === book ? [{ name: "book.mp3", size }] : [],
    fetchFile: async () => new Response(new Blob([data]), { headers: { "Content-Type": "audio/mpeg" } }), ...extra }
  return { book, file, data, cache, options, library: new OfflineLibrary(options) }
}
const bytesOf = async response => new Uint8Array(await response.arrayBuffer())

test("a file larger than one chunk is stored as fixed-size chunks, never one huge entry", async () => {
  const f = bigFixture(2 * CHUNK_SIZE + 123)
  const put = f.cache.put.bind(f.cache)
  // WebKit-like: a single cache entry above the chunk size fails with a generic error
  f.cache.put = async (key, response) => {
    const clone = response.clone()
    if ((await clone.arrayBuffer()).byteLength > CHUNK_SIZE) throw new DOMException("Internal error", "UnknownError")
    return put(key, response)
  }
  await f.library.download(f.book)
  assert.equal(f.library.state.books[f.book].complete, true)
  assert.deepEqual(f.library.findFile(f.file), { size: f.data.length, chunks: 3 })
  assert.deepEqual(await bytesOf(await f.library.response(f.file)), f.data)
})

test("chunked ranges cross chunk boundaries exactly like the original bytes", async () => {
  const f = bigFixture(CHUNK_SIZE + 5 * MB)
  await f.library.download(f.book)
  for (const [start, end] of [[0, 9], [CHUNK_SIZE - 3, CHUNK_SIZE + 2], [CHUNK_SIZE, CHUNK_SIZE], [f.data.length - 4, f.data.length - 1]]) {
    const response = await f.library.response(f.file, `bytes=${start}-${end}`)
    assert.equal(response.status, 206)
    assert.equal(response.headers.get("Content-Range"), `bytes ${start}-${end}/${f.data.length}`)
    assert.equal(Number(response.headers.get("Content-Length")), end - start + 1)
    assert.deepEqual(await bytesOf(response), f.data.slice(start, end + 1))
  }
  const open = await f.library.response(f.file, "bytes=100-")
  assert.equal(open.status, 206)
  assert.equal((await bytesOf(open)).length, f.data.length - 100)
  assert.equal((await f.library.response(f.file, `bytes=${f.data.length}-`)).status, 416)
})

test("a write failure mid-file removes that file's chunks and stays resumable", async () => {
  const f = bigFixture(3 * CHUNK_SIZE)
  const put = f.cache.put.bind(f.cache)
  let fail = true
  f.cache.put = async (key, response) => {
    if (fail && key.endsWith("?chunk=1")) throw new DOMException("Internal error", "UnknownError")
    return put(key, response)
  }
  await assert.rejects(f.library.download(f.book), error => error.name === "UnknownError" && /book\.mp3/.test(error.message))
  assert.equal([...f.cache.data.keys()].filter(key => key.includes("/file/")).length, 0)
  assert.equal(f.library.status(f.book).state, "partial")
  fail = false
  await f.library.download(f.book)
  assert.deepEqual(await bytesOf(await f.library.response(f.file)), f.data)
})

test("progress counts bytes inside a large file, not only finished files", async () => {
  const f = bigFixture(3 * CHUNK_SIZE)
  const seen = []
  f.library.onChange = () => { const s = f.library.status(f.book); if (s.state === "downloading") seen.push(s.bytes) }
  await f.library.download(f.book)
  assert.ok(seen.some(bytes => bytes > 0 && bytes < f.data.length), `in-flight bytes reported: ${seen}`)
})

test("missing chunks are detected, and delete removes every chunk", async () => {
  const f = bigFixture(2 * CHUNK_SIZE + 1)
  await f.library.download(f.book)
  const keys = f.library.storedKeys(f.file)
  assert.equal(keys.length, 4)
  await f.cache.delete(keys[2])
  assert.equal(await f.library.verify(), true)
  assert.equal(f.library.status(f.book).state, "partial")
  await f.library.download(f.book)
  await f.library.remove(f.book)
  assert.equal([...f.cache.data.keys()].filter(key => key.includes("/file/")).length, 0)
})

test("files downloaded before chunking (single raw entry) still play and export", async () => {
  const f = fixture()
  await f.library.download(f.book)
  const path = `${f.book}/Volume 2/01.mp3`
  assert.equal(f.library.findFile(path).chunks, undefined)
  assert.equal(await (await f.library.response(path, "bytes=1-2")).text(), "ef")
  assert.equal(await (await f.library.response(path)).text(), "def")
})
