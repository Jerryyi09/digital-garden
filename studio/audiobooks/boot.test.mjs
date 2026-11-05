// Start-up regression: the first screen, saved login and the login prompt must never wait
// on optional local stores (iOS can leave IndexedDB / CacheStorage opens pending forever).
import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'

const app = fs.readFileSync(new URL('./app.js', import.meta.url), 'utf8')
const html = fs.readFileSync(new URL('./index.html', import.meta.url), 'utf8')
const slice = (from, to) => app.slice(app.indexOf(from), app.indexOf(to, app.indexOf(from)))
const withTimeout = slice('function withTimeout(', 'async function openDatabase(')
const init = slice('async function init() {', 'queueMicrotask(init)')

function boot({ auth = null, onLine = true, downloads = 0, stuck = true } = {}) {
  const calls = { render: 0, browse: [], showModal: 0, startUserSync: 0, notices: [] }
  const never = () => new Promise(() => {})
  const el = () => ({ textContent: '', style: {}, hidden: true, checked: false, value: '', open: false,
    showModal() { calls.showModal++; this.open = true } })
  const nodes = new Map()
  const context = vm.createContext({
    console, setTimeout, clearTimeout, Promise,
    ROOT: '/root', prefs: { username: 'alice' }, auth, JOURNAL: 'j', AUDIO: /\.mp3$/,
    localStorage: {}, read: () => null, setSpeed() {},
    $: id => { if (!nodes.has(id)) nodes.set(id, el()); return nodes.get(id) },
    render: () => { calls.render++ }, notice: text => calls.notices.push(text),
    browse: path => { calls.browse.push(path); return Promise.resolve() },
    startUserSync: () => { calls.startUserSync++ },
    account: () => 'alice', offlineOwner: '', offlineLibrary: null, offlineBrowsing: false, offlineReady: Promise.resolve(),
    navigator: { onLine },
    openOfflineLibrary: stuck ? never : async () => {
      context.offlineOwner = 'alice'
      context.offlineLibrary = { state: { books: Object.fromEntries(Array.from({ length: downloads }, (_, i) => [`/b${i}`, {}])) } }
    },
    openDatabase: stuck ? never : async () => {}, openSyncStore: stuck ? never : async () => ({}),
  })
  vm.runInContext(withTimeout + init, context)
  return { context, calls, nodes, done: context.init() }
}

test('signed-in start renders and lists the library before local stores finish opening', async () => {
  const { calls } = boot({ auth: { token: 't' } })
  await new Promise(resolve => setImmediate(resolve))
  assert.ok(calls.render >= 1, 'first screen rendered')
  assert.deepEqual(calls.browse, ['/root'], 'library listing started without waiting for IndexedDB / CacheStorage')
})

test('signed-out start still shows the login dialog when every local store hangs', async () => {
  const { calls, done } = boot({ auth: null })
  await done // offline index is bounded by withTimeout; the prompt follows
  assert.equal(calls.showModal, 1)
  assert.ok(calls.notices.some(text => /下载库/.test(text)), 'user is told the download library is unavailable')
}, { timeout: 8000 })

test('signed-out but online with downloads: prompt to sign in instead of hiding the dialog', async () => {
  const { calls, done } = boot({ auth: null, downloads: 2, stuck: false })
  await done
  assert.equal(calls.showModal, 1)
})

test('signed-out and offline with downloads: open the downloaded books, no unusable login', async () => {
  const { calls, done, context } = boot({ auth: null, onLine: false, downloads: 1, stuck: false })
  await done
  assert.equal(calls.showModal, 0)
  assert.equal(context.offlineBrowsing, true)
  assert.equal(calls.browse.length, 1)
})

test('login is remembered on this device by default and the choice persists', () => {
  assert.match(html, /<input id="remember" type="checkbox" checked>/)
  assert.match(init, /prefs\.remember !== false/)
  assert.match(app, /remember: \$\("remember"\)\.checked/)
})
