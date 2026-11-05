export const OFFLINE_CACHE = "garden-offline-library-v1"
export const DEFAULT_LIMIT = 5 * 1024 ** 3
export const OFFLINE_PREFIX = "/studio/audiobooks/offline-data/"

import "./offline-range.js"
export const rangeResponse = globalThis.gardenOfflineRangeResponse
export const fileResponse = globalThis.gardenOfflineFileResponse
export const CHUNK_SIZE = globalThis.gardenOfflineChunkSize
const chunkKey = globalThis.gardenOfflineChunkKey

export class OfflineLibrary {
  constructor({ cache, origin, owner, root, fetchFile, listRemote, storage = {}, onChange = () => {} }) {
    Object.assign(this, { cache, origin, owner, root, fetchFile, listRemote, storage, onChange })
    this.prefix = `${origin}${OFFLINE_PREFIX}${encodeURIComponent(owner)}/`
    this.indexKey = this.prefix + "index"
    this.state = { limit: DEFAULT_LIMIT, books: {} }
    this.controller = null
  }
  key(path) { return this.prefix + "file/" + encodeURIComponent(path) }
  // Every cache entry backing one stored file (head + chunks for chunked files).
  storedKeys(path, file = this.findFile(path)) {
    const key = this.key(path)
    return [key, ...Array.from({ length: file?.chunks || 0 }, (_, index) => chunkKey(key, index))]
  }
  async hasStored(path, file) {
    for (const key of this.storedKeys(path, file)) if (!await this.cache.match(key)) return false
    return true
  }
  // Same response the Service Worker serves, for in-page reads (export, tests).
  response(path, range = null) { return fileResponse(this.cache, this.key(path), range) }
  valid(path, base = this.root) {
    return typeof path === "string" && path.startsWith(base + "/") && !path.slice(1).split("/").some(p => !p || p === "." || p === "..")
  }
  // Reads only the index, so app start-up never waits on per-file checks.
  async open() {
    const saved = await this.cache.match(this.indexKey)
    if (saved) this.state = await saved.json()
    return this
  }
  // Drops entries whose bytes the system has evicted. Run in the background after start-up;
  // downloads and deletions repeat the same check under the lock before changing anything.
  async verify() {
    let changed = false
    for (const book of Object.values(this.state.books)) {
      for (const [path, file] of Object.entries(book.files)) {
        if (!await this.hasStored(path, file)) { delete book.files[path]; book.complete = false; changed = true }
      }
    }
    if (changed && !this.busy) await this.save()
    return changed
  }
  // Snapshot for the UI: complete / partial / downloading, with file and byte counts.
  status(path) {
    const book = this.state.books[path]
    if (!book) return { state: this.downloading === path ? "downloading" : "none", done: 0, total: 0, bytes: 0 }
    const done = Object.keys(book.files).length
    const inflight = this.inflight?.book === path ? this.inflight.bytes : 0
    const bytes = Object.values(book.files).reduce((n, file) => n + file.size, 0) + inflight
    const total = book.plan?.length || 0
    const totalBytes = (book.plan || []).reduce((n, file) => n + file.size, 0)
    const state = this.downloading === path ? "downloading" : book.complete ? "complete" : "partial"
    return { state, done, total, bytes, totalBytes }
  }
  async save() {
    await this.cache.put(this.indexKey, new Response(JSON.stringify(this.state), { headers: { "Content-Type": "application/json" } }))
    this.onChange()
  }
  get used() { return Object.values(this.state.books).reduce((sum, book) => sum + Object.values(book.files).reduce((n, file) => n + file.size, 0), 0) }
  async exclusive(action) {
    if (this.busy) throw new Error("已有下载或存储操作进行中")
    this.busy = true
    const run = async () => {
      const saved = await this.cache.match(this.indexKey)
      if (saved) this.state = await saved.json()
      for (const book of Object.values(this.state.books)) {
        for (const [path, file] of Object.entries(book.files)) {
          if (!await this.hasStored(path, file)) { delete book.files[path]; book.complete = false }
        }
      }
      // Only the lock holder may clean interrupted, uncommitted downloads (including chunks).
      const retained = new Set(Object.values(this.state.books).flatMap(book => Object.entries(book.files).flatMap(([path, file]) => this.storedKeys(path, file))))
      for (const key of await this.cache.keys()) {
        if (key.url.startsWith(this.prefix + "file/") && !retained.has(key.url)) await this.cache.delete(key)
      }
      return action()
    }
    try {
      if (globalThis.navigator?.locks) return await navigator.locks.request(this.prefix, { ifAvailable: true }, lock => {
        if (!lock) throw new Error("另一个窗口正在下载或管理存储")
        return run()
      })
      return await run()
    } finally { this.busy = false }
  }
  setLimit(bytes) { return this.exclusive(() => this._setLimit(bytes)) }
  remove(path) { return this.exclusive(() => this._remove(path)) }
  download(path) { return this.exclusive(() => this._download(path)) }
  async _setLimit(bytes) {
    if (!Number.isSafeInteger(bytes) || bytes <= 0 || bytes < this.used) throw new Error("上限不能小于已下载大小")
    this.state.limit = bytes
    await this.save()
  }
  findFile(path) { return Object.values(this.state.books).find(book => book.files[path])?.files[path] }
  localUrl(path) { return this.findFile(path) ? this.key(path) : null }
  listing(path) {
    const books = Object.values(this.state.books)
    const exact = books.find(book => book.dirs[path])
    if (exact) return { content: exact.dirs[path], total: exact.dirs[path].length }
    const children = new Map()
    for (const book of books) {
      if (!book.path.startsWith(path + "/")) continue
      const name = book.path.slice(path.length + 1).split("/")[0]
      children.set(name, { name, is_dir: true })
    }
    return children.size ? { content: [...children.values()], total: children.size } : null
  }
  pause() { this.controller?.abort() }
  async _remove(path) {
    if (this.controller) throw new Error("请先暂停下载")
    const book = this.state.books[path]
    if (!book) return
    for (const [file, meta] of Object.entries(book.files)) for (const key of this.storedKeys(file, meta)) await this.cache.delete(key)
    delete this.state.books[path]
    await this.save()
  }
  async _download(path) {
    if (this.controller) throw new Error("已有下载进行中")
    if (!this.valid(path) || path.slice(this.root.length + 1).split("/").length !== 2) throw new Error("请在书籍目录开始下载")
    this.controller = new AbortController()
    this.downloading = path
    this.onChange()
    const signal = this.controller.signal
    let book = this.state.books[path]
    try {
      await this.storage.persist?.()
      if (!book || !book.plan) {
        book = { path, dirs: {}, files: {}, plan: [], complete: false }
        const readalongRoots = []
        const scan = async directory => {
          signal.throwIfAborted()
          if (Object.keys(book.dirs).length >= 2000) throw new Error("目录过多，请拆分书籍后下载")
          const rows = await this.listRemote(directory, signal)
          book.dirs[directory] = rows
          if (rows.some(row => row.is_dir && row.name === "readalong")) readalongRoots.push(directory)
          for (const row of rows) {
            const file = `${directory}/${row.name}`
            if (!this.valid(file, path) || row.name.includes("/")) throw new Error("书籍包含无效路径")
            if (row.is_dir) {
              if (!row.name.startsWith(".") && !["readalong", "work", "cache", "generated", "preview", "runtime-snapshot", "__pycache__"].includes(row.name)) await scan(file)
            } else book.plan.push({ path: file, size: Number(row.size) || 0 })
          }
        }
        await scan(path)
        // Pin each volume's release as well as book-level manifests.
        for (const releaseRoot of [...readalongRoots]) {
          const manifestPath = `${releaseRoot}/readalong/readalong.manifest.json`
          const response = await this.fetchFile(manifestPath, signal)
          if (!response.ok || response.type === "opaque") throw new Error("无法读取跟读版本")
          const manifest = await response.json()
          const base = /^[a-f0-9]{32}$/.test(manifest.assetRevision || "")
            ? `${releaseRoot}/.readalong_revisions/${manifest.assetRevision}` : `${releaseRoot}/readalong`
          await scan(base)
          book.manifest = manifest
          book.plan = book.plan.filter(file => file.path != manifestPath)
          book.plan.push({ path: manifestPath, size: 0, json: manifest })
        }
        this.state.books[path] = book
        await this.save()
      }
      const remaining = book.plan.filter(file => !book.files[file.path]).reduce((sum, file) => sum + file.size, 0)
      const estimate = await this.storage.estimate?.()
      if (this.used + remaining > this.state.limit || (estimate?.quota != null && remaining > estimate.quota - estimate.usage)) throw new Error("空间不足，请调整上限或删除已下载书籍")
      for (const file of book.plan) {
        signal.throwIfAborted()
        if (book.files[file.path] && await this.hasStored(file.path, book.files[file.path])) continue
        const response = file.json ? new Response(JSON.stringify(file.json), { headers: { "Content-Type": "application/json" } }) : await this.fetchFile(file.path, signal)
        if (response.status !== 200 || response.type === "opaque" || !response.body) throw new Error(`文件下载失败：${file.path.split("/").pop()}`)
        delete book.files[file.path]
        book.files[file.path] = await this._store(book, file, response, signal)
        await this.save()
      }
      book.complete = true
      await this.save()
    } finally { this.controller = null; this.downloading = null; this.onChange() }
  }

  // Streams one file into the cache: one raw entry if it fits in a chunk, otherwise
  // fixed-size chunks plus a head. Nothing is registered until every entry is written;
  // on failure all entries written for this file are removed.
  async _store(book, file, response, signal) {
    const key = this.key(file.path)
    const name = file.path.split("/").pop()
    const type = response.headers.get("Content-Type") || "application/octet-stream"
    const used = this.used
    const limit = this.state.limit
    const reader = response.body.getReader()
    const buffer = new Uint8Array(CHUNK_SIZE)
    const written = []
    let filled = 0
    let size = 0
    let chunks = 0
    const put = async (entryKey, body, headers) => {
      try {
        await this.cache.put(entryKey, new Response(body, { headers }))
        written.push(entryKey)
      } catch (error) {
        const wrapped = new Error(`写入本机失败：${name}（${error.name}: ${error.message}）`)
        wrapped.name = error.name
        wrapped.cause = error
        throw wrapped
      }
    }
    const flushChunk = async () => {
      await put(chunkKey(key, chunks), new Blob([buffer.subarray(0, filled)]), { "Content-Type": type })
      chunks++
      filled = 0
      this.inflight = { book: book.path, bytes: chunks * CHUNK_SIZE } // bytes safely written so far
      this.onChange()
    }
    try {
      this.inflight = { book: book.path, bytes: 0 }
      for (;;) {
        signal.throwIfAborted()
        const { done, value } = await reader.read()
        if (done) break
        size += value.byteLength
        if (used + size > limit) throw new Error("达到下载上限，下载已暂停")
        let offset = 0
        while (offset < value.byteLength) {
          const take = Math.min(CHUNK_SIZE - filled, value.byteLength - offset)
          buffer.set(value.subarray(offset, offset + take), filled)
          filled += take
          offset += take
          if (filled === CHUNK_SIZE) await flushChunk()
        }
      }
      signal.throwIfAborted()
      if (file.size && size !== file.size) throw new Error("下载文件大小不一致，请重试")
      if (!chunks) {
        await put(key, new Blob([buffer.subarray(0, filled)]), { "Content-Type": type })
      } else {
        if (filled) await flushChunk()
        await put(key, JSON.stringify({ size, chunkSize: CHUNK_SIZE, chunks, type }),
          { "Content-Type": "application/json", "X-Garden-Chunks": String(chunks) })
      }
      return chunks ? { size, chunks } : { size }
    } catch (error) {
      reader.cancel().catch(() => {})
      for (const entryKey of written) await this.cache.delete(entryKey)
      throw error
    } finally {
      this.inflight = null
    }
  }
}
