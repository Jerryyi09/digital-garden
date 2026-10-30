import { test } from 'node:test'
import assert from 'node:assert/strict'
import { UserSync } from './user-sync.js'

function fixture() {
  const local = new Map(), remote = new Map()
  let online = true
  const key = x => JSON.stringify([x.kind, x.id])
  const sync = new UserSync({
    list: async () => Array.from(local.values(), x => structuredClone(x)),
    put: async row => local.set(key(row), structuredClone(row)),
    request: async (method, body) => {
      if (!online) throw new Error('offline')
      if (method === 'GET') return { items: Array.from(remote.values(), x => structuredClone(x)) }
      const old = remote.get(key(body))
      if ((old?.revision ?? 0) !== body.revision) throw Object.assign(new Error('conflict'), { status: 409, current: old })
      const row = { ...body, revision: body.revision + 1 }
      remote.set(key(body), structuredClone(row))
      return { revision: row.revision }
    },
  })
  return { sync, local, remote, setOnline: value => { online = value } }
}

test('offline edit persists and syncs when reconnected', async () => {
  const f = fixture()
  f.setOnline(false)
  await f.sync.save('progress', 'track', { position: 4 })
  await assert.rejects(f.sync.sync())
  assert.equal([...f.local.values()][0].dirty, true)
  f.setOnline(true)
  await f.sync.sync()
  assert.equal([...f.remote.values()][0].value.position, 4)
  assert.equal([...f.local.values()][0].dirty, false)
})

test('conflicts preserve both values until explicit resolution, including seeking backward', async () => {
  const f = fixture()
  await f.sync.save('progress', 'track', { position: 20 })
  await f.sync.sync()
  await f.sync.save('progress', 'track', { position: 4 })
  const item = [...f.remote.values()][0]
  f.remote.set(JSON.stringify(['progress', 'track']), { ...item, revision: 2, value: { position: 50 } })
  await f.sync.sync()
  assert.equal([...f.local.values()][0].conflict.value.position, 50)
  assert.equal([...f.local.values()][0].value.position, 4)
  await f.sync.resolve('progress', 'track', 'local')
  await f.sync.sync()
  assert.equal([...f.remote.values()][0].value.position, 4)
})

test('an edit made while upload is in flight remains dirty', async () => {
  let row = null, finish
  const pending = new Promise(resolve => { finish = resolve })
  const sync = new UserSync({ list: async () => row ? [structuredClone(row)] : [], put: async x => { row = structuredClone(x) }, request: async method => method === 'GET' ? { items: [] } : pending })
  await sync.save('progress', 'track', { position: 1 })
  const running = sync.sync()
  await new Promise(resolve => setTimeout(resolve, 0))
  await sync.save('progress', 'track', { position: 2 })
  finish({ revision: 1 })
  await running
  assert.equal(row.dirty, true)
  assert.equal(row.value.position, 2)
  assert.equal(row.revision, 1)
})

test('legacy local records are not overwritten by an existing remote record', async () => {
  const f = fixture()
  const key = JSON.stringify(['progress', 'track'])
  f.remote.set(key, { kind: 'progress', id: 'track', revision: 3, value: { position: 90 } })
  await f.sync.save('progress', 'track', { position: 12 })
  await f.sync.sync()
  const row = f.local.get(key)
  assert.equal(row.value.position, 12)
  assert.equal(row.conflict.value.position, 90)
  assert.equal(f.remote.get(key).revision, 3)
  await f.sync.resolve('progress', 'track', 'remote')
  assert.equal(f.local.get(key).value.position, 90)
  assert.equal(f.local.get(key).dirty, false)
})

test('legacy migration never overwrites an edit already queued', async () => {
  const f = fixture()
  await f.sync.save('progress', 'track', { position: 25 })
  assert.equal(await f.sync.seed('progress', 'track', { position: 3 }), false)
  assert.equal([...f.local.values()][0].value.position, 25)
})

test('bookmark deletion remains a tombstone on the server', async () => {
  const f = fixture()
  await f.sync.save('bookmark', 'b1', { position: 10, deleted: false })
  await f.sync.sync()
  await f.sync.save('bookmark', 'b1', { position: 10, deleted: true })
  await f.sync.sync()
  assert.equal(f.remote.get(JSON.stringify(['bookmark', 'b1'])).value.deleted, true)
})

test('a missing server record does not silently discard previously synced local data', async () => {
  const f = fixture()
  await f.sync.save('progress', 'track', { position: 22 })
  await f.sync.sync()
  f.remote.clear()
  await f.sync.sync()
  const row = f.local.get(JSON.stringify(['progress', 'track']))
  assert.equal(row.conflict.missing, true)
  assert.equal(row.value.position, 22)
  await f.sync.resolve('progress', 'track', 'local')
  await f.sync.sync()
  assert.equal([...f.remote.values()][0].value.position, 22)
})

test('independent devices receive the same progress and bookmark from the shared service', async () => {
  const f = fixture()
  const second = new Map()
  const client = new UserSync({
    request: f.sync.request,
    list: async () => [...second.values()].map(row => structuredClone(row)),
    put: async row => second.set(JSON.stringify([row.kind, row.id]), structuredClone(row)),
  })
  await f.sync.save('progress', 'track', { position: 15 })
  await f.sync.save('bookmark', 'mark', { position: 9, deleted: false })
  await f.sync.sync()
  await client.sync()
  assert.equal(second.get(JSON.stringify(['progress', 'track'])).value.position, 15)
  assert.equal(second.get(JSON.stringify(['bookmark', 'mark'])).value.position, 9)
  await client.save('progress', 'track', { position: 7 })
  await client.sync()
  await f.sync.sync()
  assert.equal(f.local.get(JSON.stringify(['progress', 'track'])).value.position, 7)
})

test('a local upload acknowledgement does not request a redraw', async () => {
  const f = fixture()
  await f.sync.save('progress', 'track', { position: 15 })
  assert.equal(await f.sync.sync(), false)
  assert.equal(await f.sync.sync(), false)
})

test('a remote update reports a change', async () => {
  const f = fixture()
  await f.sync.save('progress', 'track', { position: 15 })
  await f.sync.sync()
  const key = JSON.stringify(['progress', 'track'])
  f.remote.set(key, { ...f.remote.get(key), revision: 2, value: { position: 44 } })
  assert.equal(await f.sync.sync(), true)
})
