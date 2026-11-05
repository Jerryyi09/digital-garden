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
  const context = vm.createContext({ offlineReady: Promise.resolve(), offlineOwner: 'alice', account: () => 'alice', offlineBrowsing: true, auth: null,
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
test('api waits for the offline index opened in the background before choosing local or remote', async () => {
  let calls = 0
  let open
  const context = vm.createContext({ offlineOwner: '', account: () => 'alice', offlineBrowsing: false, auth: null, offlineLibrary: null,
    navigator: { onLine: false }, remoteApi: () => { calls++; throw new Error('network forbidden') } })
  context.offlineReady = new Promise(resolve => { open = () => {
    context.offlineOwner = 'alice'
    context.offlineLibrary = { localUrl: () => null, listing: path => path === '/root' ? { content: [{ name: 'book', is_dir: true }], total: 1 } : null }
    resolve()
  } })
  vm.runInContext(api, context)
  const pending = context.api('fs/list', { path: '/root', page: 1 })
  open()
  assert.equal((await pending).content[0].name, 'book')
  assert.equal(calls, 0)
})
