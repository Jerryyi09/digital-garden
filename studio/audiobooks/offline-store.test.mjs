import test from "node:test"
import assert from "node:assert/strict"
import { OfflineLibrary, rangeResponse, DEFAULT_LIMIT } from "./offline-store.js"

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
  assert.equal(reopened.state.books[f.book].complete, false)
  assert.equal(reopened.used, 3)
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
