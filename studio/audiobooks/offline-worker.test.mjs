import test from "node:test"
import assert from "node:assert/strict"
import fs from "node:fs"
import vm from "node:vm"
import { OFFLINE_CACHE } from "./offline-store.js"
const source = fs.readFileSync(new URL("./sw.js", import.meta.url), "utf8")
function worker(cache) {
  const events = new Map()
  const ctx = vm.createContext({ URL, Request, Response, Headers, Blob,
    self: { location: { origin: 'https://local.test' }, registration: { scope: 'https://local.test/studio/audiobooks/' },
      clients: { claim() {} }, addEventListener(name, fn) { const rows = events.get(name) || []; rows.push(fn); events.set(name, rows) } },
    caches: cache, fetch: async () => { throw new Error('offline') } })
  ctx.importScripts = file => vm.runInContext(fs.readFileSync(new URL(file, import.meta.url), 'utf8'), ctx)
  vm.runInContext(source, ctx)
  return events
}
test("shell activation preserves manual downloads", async () => {
  const deleted = []
  const events = worker({ keys: async () => [OFFLINE_CACHE, 'garden-audiobooks-v60-network-first', 'garden-covers'], delete: key => deleted.push(key) })
  let done
  events.get('activate')[0]({ waitUntil(promise) { done = promise } })
  await done
  assert.deepEqual(deleted, ['garden-audiobooks-v60-network-first'])
})
test("offline shell with cache-busting query falls back to precached canonical URL", async () => {
  const events = worker({ match: async key => key.url === 'https://local.test/studio/audiobooks/app.js' ? new Response('cached app') : undefined })
  let answer
  const event = { request: new Request('https://local.test/studio/audiobooks/app.js?v=52'), respondWith(promise) { answer = promise } }
  for (const handler of events.get('fetch')) handler(event)
  assert.equal(await (await answer).text(), 'cached app')
})
test("worker serves local audio range without a network request", async () => {
  const events = worker({ open: async () => ({ match: async () => new Response('abcdef', { headers: { 'Content-Type': 'audio/mpeg' } }) }) })
  let answer
  const event = { request: new Request('https://local.test/studio/audiobooks/offline-data/user/file/audio', { headers: { Range: 'bytes=2-4' } }), respondWith(promise) { assert.equal(answer, undefined); answer = promise } }
  for (const handler of events.get('fetch')) handler(event)
  const response = await answer
  assert.equal(response.status, 206)
  assert.equal(await response.text(), 'cde')
})
