import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'
const app = fs.readFileSync(new URL('./app.js', import.meta.url), 'utf8')
const api = app.slice(app.indexOf('async function api('), app.indexOf('async function remoteApi('))
const stream = app.slice(app.indexOf('async function stream('), app.indexOf('async function prepareNext('))

test('production playback uses downloaded media without requesting a signed URL', async () => {
  let calls = 0
  const context = vm.createContext({ offlineOwner: 'alice', account: () => 'alice', offlineBrowsing: false,
    offlineLibrary: { localUrl: path => path === '/book/a.mp3' ? 'https://local/offline' : null },
    api: () => { calls++; throw new Error('must not request AList') } })
  vm.runInContext(stream, context)
  assert.equal(await context.stream({ path: '/book/a.mp3' }), 'https://local/offline')
  assert.equal(calls, 0)
})
test('production offline browse reads local directories and never silently streams missing files', async () => {
  let calls = 0
  const context = vm.createContext({ offlineOwner: 'alice', account: () => 'alice', offlineBrowsing: true, auth: null,
    navigator: { onLine: true }, offlineLibrary: { localUrl: () => null, listing: path => path === '/book' ? { content: [{ name: 'a.mp3' }], total: 1 } : null },
    remoteApi: () => { calls++; throw new Error('network forbidden') } })
  vm.runInContext(api + stream, context)
  assert.equal((await context.api('fs/list', { path: '/book', page: 1 })).content.length, 1)
  await assert.rejects(context.api('fs/get', { path: '/missing' }), /本机没有/)
  await assert.rejects(context.stream({ path: '/missing' }), /尚未下载/)
  assert.equal(calls, 0)
})
test('production playback cannot read another account cache', async () => {
  const context = vm.createContext({ offlineOwner: 'alice', account: () => 'bob', offlineBrowsing: false,
    directoryPassword: '', endpoint: 'https://remote',
    offlineLibrary: { localUrl: () => 'https://local/alice' }, api: async () => ({ sign: 'signed' }), mediaUrl: () => 'https://remote/bob' })
  vm.runInContext(stream, context)
  assert.equal(await context.stream({ path: '/book/a.mp3' }), 'https://remote/bob')
})
