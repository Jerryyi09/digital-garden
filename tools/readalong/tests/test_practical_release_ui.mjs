import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'

test('actual setupReadalong shows practical gaps without an out-of-scope badge variable', async () => {
  const source = fs.readFileSync(new URL('../../../studio/audiobooks/app.js', import.meta.url), 'utf8')
  const body = source.slice(source.indexOf('async function setupReadalong('), source.indexOf('async function setupPdf('))
  const nodes = new Map()
  const track = { path: '/750HD/有声书/category/book/a.mp3' }
  const manifest = { schemaVersion: 1, assetRevision: 'a'.repeat(32), timeline: 'timeline.json', textRoot: 'text/',
    audioSources: [{ id: 'a.mp3' }], practicalRelease: { decision: 'PUBLISH_WITH_GAPS' } }
  const context = vm.createContext({
    invalidateReadalong() {},
    closeReadalong() { nodes.get('readalong').hidden = true },
    $(id) { if (!nodes.has(id)) nodes.set(id, {}); return nodes.get(id) },
    api: async () => ({ sign: '' }), isWithinRoot: () => true,
    mediaUrl: (_, info) => info.path,
    fetch: async url => ({ json: async () => url.endsWith('readalong.manifest.json') ? manifest :
      [{ audioSourceId: 'a.mp3', start: 1, end: 2 }] }),
    endpoint: 'https://example.test', directoryPassword: '', playRequest: 1, readalongActive: false,
  })
  vm.runInContext(body+'\nglobalThis.run = setupReadalong', context)
  await context.run(track, 1)
  assert.equal(nodes.get('readalong-release-status').textContent, '跟读 · 有局部缺口')
  assert.equal(nodes.get('dock-readalong').hidden, false)
  nodes.set('readalong', { hidden: false })
  manifest.readalongEnabled = false
  context.playRequest = 2
  await context.run(track, 2)
  assert.equal(nodes.get('dock-readalong').hidden, true)
  assert.equal(nodes.get('readalong').hidden, true)
  assert.equal(nodes.get('readalong-frame').srcdoc, '')
})
