import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import { resolvePlaybackSegment, SYNC_STATE } from '../../../studio/audiobooks/readalong-sync.js';

test('R2-05: Stale fetch response must not overwrite displayed iframe content', async () => {
  const src = fs.readFileSync(new URL('../../../studio/audiobooks/app.js', import.meta.url), 'utf8');
  const implementation = src.slice(src.indexOf('function loadReadalongDoc('), src.indexOf('// Safe event listener helper'));

  let shown = '';
  const doc = {
    body: { style: {} },
    addEventListener() {},
    getElementById() { return { classList: { add() {} }, scrollIntoView() {} }; },
    querySelectorAll() { return [{ classList: { remove() {} } }]; }
  };
  const frame = {
    style: {},
    contentDocument: doc,
    contentWindow: { addEventListener() {} },
    set srcdoc(value) {
      shown = value;
      setTimeout(() => this.onload?.(), 0);
    }
  };
  const timeline = [
    { start: 0, end: 10, fragment: 'a', document: 'A.html' },
    { start: 20, end: 30, fragment: 'b', document: 'B.html' }
  ];

  const context = vm.createContext({
    resolvePlaybackSegment,
    SYNC_STATE,
    setTimeout,
    readalongActive: true,
    current: {},
    readalongTimeline: timeline,
    audio: { currentTime: 5 },
    currentSegment: null,
    currentDocPath: '',
    readalongParentPath: '/book',
    readalongDocCache: new Map(),
    directoryPassword: '',
    endpoint: '',
    readalongFollowing: false,
    readalongManifest: null,
    $: id => (id === 'readalong-frame' ? frame : { style: {}, value: '17' }),
    api: async () => ({ sign: '' }),
    mediaUrl: (_endpoint, obj) => obj.path,
    fetch: async url => {
      // Simulate A is slower (50ms) than B (10ms)
      await new Promise(resolve => setTimeout(resolve, url.includes('A.html') ? 50 : 10));
      return { text: async () => (url.includes('A.html') ? 'A_CONTENT' : 'B_CONTENT') };
    }
  });

  vm.runInContext(implementation, context);

  // Trigger A then immediately seek to B
  const pA = context.syncReadalong();
  context.audio.currentTime = 25;
  const pB = context.syncReadalong();

  await Promise.all([pA, pB]);

  // If committed document is B, iframe must show B_CONTENT, never stale A_CONTENT
  assert.equal(context.currentDocPath, 'B.html');
  assert.equal(shown, 'B_CONTENT', 'Iframe srcdoc was corrupted by stale fetch of A');

  // A pending request must also expire when the new intent needs no document.
  context.currentDocPath = '';
  context.currentSegment = null;
  context.readalongDocCache.clear();
  shown = '';
  context.audio.currentTime = 5;
  const pendingA = context.syncReadalong();
  context.audio.currentTime = 100;
  await context.syncReadalong();
  await pendingA;
  await new Promise(resolve => setTimeout(resolve, 65));
  assert.equal(shown, '', 'Seek to unmapped state must cancel DOM writes');
  assert.equal(context.currentSegment, null);

  // An in-flight request must not replace a chapter already available locally.
  context.currentDocPath = 'B.html';
  context.currentSegment = null;
  context.readalongDocCache.clear();
  shown = 'B_CONTENT';
  context.audio.currentTime = 5;
  const pendingAgain = context.syncReadalong();
  context.audio.currentTime = 25;
  await context.syncReadalong();
  await pendingAgain;
  await new Promise(resolve => setTimeout(resolve, 65));
  assert.equal(shown, 'B_CONTENT');
  assert.equal(context.currentSegment?.fragment, 'b');
});

test('R2-05: Non-active states (AFTER_END / BEFORE_START / UNMAPPED) must clear highlight', async () => {
  const src = fs.readFileSync(new URL('../../../studio/audiobooks/app.js', import.meta.url), 'utf8');
  const implementation = src.slice(src.indexOf('function loadReadalongDoc('), src.indexOf('// Safe event listener helper'));

  let removals = 0;
  const doc = {
    body: { style: {} },
    addEventListener() {},
    getElementById() { return { classList: { add() {} }, scrollIntoView() {} }; },
    querySelectorAll() {
      return [{ classList: { remove() { removals++; } } }];
    }
  };
  const frame = {
    contentDocument: doc,
    contentWindow: { addEventListener() {} },
    set srcdoc(value) { setTimeout(() => this.onload?.(), 0); }
  };
  const timeline = [
    { start: 0, end: 10, fragment: 'a', document: 'A.html' },
    { start: 20, end: 30, fragment: 'b', document: 'A.html' }
  ];

  const context = vm.createContext({
    resolvePlaybackSegment,
    SYNC_STATE,
    setTimeout,
    readalongActive: true,
    current: {},
    readalongTimeline: timeline,
    audio: { currentTime: 25 },
    currentSegment: null,
    currentDocPath: 'A.html',
    readalongParentPath: '/book',
    readalongDocCache: new Map([['A.html', '<div>dummy</div>']]),
    directoryPassword: '',
    endpoint: '',
    readalongFollowing: false,
    readalongManifest: null,
    $: id => (id === 'readalong-frame' ? frame : { style: {}, value: '17' }),
    api: async () => ({ sign: '' }),
    mediaUrl: (_endpoint, obj) => obj.path,
    fetch: async () => ({ text: async () => '<div>dummy</div>' })
  });

  vm.runInContext(implementation, context);

  // 1. Play active segment
  await context.syncReadalong();
  assert.equal(context.currentSegment?.fragment, 'b');

  // 2. Seek to AFTER_END (e.g. 100s)
  removals = 0;
  context.audio.currentTime = 100;
  await context.syncReadalong();

  assert.equal(context.currentSegment, null, 'currentSegment should be cleared on AFTER_END');
  assert.ok(removals > 0, 'Highlight removal should be called on AFTER_END');

  // Manual locate may scroll nearby text, but cannot restore an active highlight.
  await context.syncReadalong(true);
  assert.equal(context.currentSegment, null);
});
