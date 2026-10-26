import test from 'node:test';
import assert from 'node:assert/strict';
import { resolvePlaybackSegment, SYNC_STATE } from '../../../studio/audiobooks/readalong-sync.js';

test('resolvePlaybackSegment returns ACTIVE when time is within segment', () => {
  const timeline = [
    { start: 2.0, end: 5.0, fragment: 'seg1', document: 'ch1.html' },
    { start: 6.0, end: 10.0, fragment: 'seg2', document: 'ch1.html' }
  ];
  const res = resolvePlaybackSegment(timeline, 3.5);
  assert.equal(res.state, SYNC_STATE.ACTIVE);
  assert.equal(res.segment.fragment, 'seg1');
});

test('resolvePlaybackSegment returns SHORT_PAUSE for brief gap between sentences', () => {
  const timeline = [
    { start: 2.0, end: 5.0, fragment: 'seg1', document: 'ch1.html' },
    { start: 7.0, end: 10.0, fragment: 'seg2', document: 'ch1.html' }
  ];
  // 5.8s is 0.8s after seg1 end (<= 3.5s short pause)
  const res = resolvePlaybackSegment(timeline, 5.8);
  assert.equal(res.state, SYNC_STATE.SHORT_PAUSE);
  assert.equal(res.segment.fragment, 'seg1');
});

test('R1-06 exact repro: timeline [0,1] and [1000,1001] at 500s returns UNMAPPED and segment is null', () => {
  const timeline = [
    { start: 0.0, end: 1.0, fragment: 'seg1', document: 'ch1.html' },
    { start: 1000.0, end: 1005.0, fragment: 'seg2', document: 'ch2.html' }
  ];
  // At 500s (499s after seg1 ended, 500s before seg2), it must be UNMAPPED and segment must be null
  const res = resolvePlaybackSegment(timeline, 500.0);
  assert.equal(res.state, SYNC_STATE.UNMAPPED);
  assert.equal(res.segment, null);
  assert.notEqual(res.nearest, null);
  assert.equal(res.nearest.fragment, 'seg1');
});

test('resolvePlaybackSegment edge boundaries: BEFORE_START and AFTER_END', () => {
  const timeline = [
    { start: 10.0, end: 15.0, fragment: 'seg1', document: 'ch1.html' },
    { start: 20.0, end: 25.0, fragment: 'seg2', document: 'ch1.html' }
  ];
  // 2s is far before start -> BEFORE_START
  const before = resolvePlaybackSegment(timeline, 2.0);
  assert.equal(before.state, SYNC_STATE.BEFORE_START);
  assert.equal(before.segment, null);

  // 40s is far after end -> AFTER_END
  const after = resolvePlaybackSegment(timeline, 40.0);
  assert.equal(after.state, SYNC_STATE.AFTER_END);
  assert.equal(after.segment, null);
});

test('Rapid seek and document epoch race condition guard simulation', async () => {
  let docLoadEpoch = 0;
  let currentDocPath = '';
  let currentSegment = null;

  async function mockSync(timeline, time, simulatedLatencyMs) {
    const res = resolvePlaybackSegment(timeline, time, 3.5);
    let seg = res.segment;
    if (res.state === SYNC_STATE.UNMAPPED) {
      currentSegment = null;
      return { loaded: false, doc: currentDocPath };
    }
    if (!seg) return { loaded: false, doc: currentDocPath };

    if (currentDocPath !== seg.document) {
      const thisEpoch = ++docLoadEpoch;
      // Simulate network fetch with latency
      await new Promise(r => setTimeout(r, simulatedLatencyMs));
      // Stale response must be discarded if a newer seek updated the epoch
      if (thisEpoch !== docLoadEpoch) {
        return { discarded: true, thisEpoch, currentEpoch: docLoadEpoch };
      }
      currentDocPath = seg.document;
    }
    currentSegment = seg;
    return { loaded: true, doc: currentDocPath, seg: currentSegment.fragment };
  }

  const timeline = [
    { start: 0, end: 10, fragment: 'c1', document: 'ch1.html' },
    { start: 20, end: 30, fragment: 'c2', document: 'ch2.html' },
    { start: 40, end: 50, fragment: 'c3', document: 'ch3.html' }
  ];

  // Call 1: seek to ch2 (slow network, 50ms latency)
  const p1 = mockSync(timeline, 25, 50);
  // Call 2: immediately seek to ch3 (fast network, 10ms latency)
  const p2 = mockSync(timeline, 45, 10);

  const [res1, res2] = await Promise.all([p1, p2]);

  // res1 was superseded and discarded
  assert.equal(res1.discarded, true);
  // res2 committed successfully
  assert.equal(res2.loaded, true);
  assert.equal(res2.doc, 'ch3.html');
  assert.equal(currentDocPath, 'ch3.html');
  assert.equal(currentSegment.fragment, 'c3');
});

test('A5.8: resolvePlaybackSegment accurately resolves multi-occurrence segments based on physical playback time without backtracking', () => {
  const multiOccurrenceTimeline = [
    { start: 10.0, end: 20.0, fragment: 'paragraph-1', document: 'chapter1.xhtml', occurrenceId: '0' },
    { start: 30.0, end: 40.0, fragment: 'paragraph-2', document: 'chapter1.xhtml', occurrenceId: '0' },
    { start: 50.0, end: 60.0, fragment: 'paragraph-3', document: 'chapter2.xhtml', occurrenceId: '0' },
    // Paragraph-1 is re-read at the end of the audiobook
    { start: 100.0, end: 110.0, fragment: 'paragraph-1', document: 'chapter1.xhtml', occurrenceId: '1' },
  ];

  // At 15.0s, physical speech is inside the first occurrence
  const resFirst = resolvePlaybackSegment(multiOccurrenceTimeline, 15.0);
  assert.equal(resFirst.state, SYNC_STATE.ACTIVE);
  assert.equal(resFirst.segment.fragment, 'paragraph-1');
  assert.equal(resFirst.segment.occurrenceId, '0');
  assert.equal(resFirst.segment.start, 10.0);

  // At 55.0s, physical speech is inside paragraph-3
  const resMiddle = resolvePlaybackSegment(multiOccurrenceTimeline, 55.0);
  assert.equal(resMiddle.state, SYNC_STATE.ACTIVE);
  assert.equal(resMiddle.segment.fragment, 'paragraph-3');

  // At 105.0s, physical speech is inside the second occurrence (re-read tail)
  const resSecond = resolvePlaybackSegment(multiOccurrenceTimeline, 105.0);
  assert.equal(resSecond.state, SYNC_STATE.ACTIVE);
  assert.equal(resSecond.segment.fragment, 'paragraph-1');
  assert.equal(resSecond.segment.occurrenceId, '1');
  assert.equal(resSecond.segment.start, 100.0);
  assert.notEqual(resSecond.segment.start, 10.0, 'Must not backtrack to first occurrence start time');

  // At 100.0s (exact boundary)
  const resBoundary = resolvePlaybackSegment(multiOccurrenceTimeline, 100.0);
  assert.equal(resBoundary.state, SYNC_STATE.ACTIVE);
  assert.equal(resBoundary.segment.occurrenceId, '1');
});

test('R03-06: resolvePlaybackSegment supports triple re-read occurrences (A B A B A) with monotonic physical time', () => {
  const tripleReReadTimeline = [
    { start: 0.0, end: 10.0, fragment: 'para-A', document: 'ch1.html', occurrenceId: '0' },
    { start: 10.0, end: 20.0, fragment: 'para-B', document: 'ch1.html', occurrenceId: '0' },
    { start: 20.0, end: 30.0, fragment: 'para-A', document: 'ch1.html', occurrenceId: '1' },
    { start: 30.0, end: 40.0, fragment: 'para-B', document: 'ch1.html', occurrenceId: '1' },
    { start: 40.0, end: 50.0, fragment: 'para-A', document: 'ch1.html', occurrenceId: '2' },
  ];

  const t1 = resolvePlaybackSegment(tripleReReadTimeline, 5.0);
  assert.equal(t1.segment.fragment, 'para-A');
  assert.equal(t1.segment.occurrenceId, '0');

  const t2 = resolvePlaybackSegment(tripleReReadTimeline, 25.0);
  assert.equal(t2.segment.fragment, 'para-A');
  assert.equal(t2.segment.occurrenceId, '1');

  const t3 = resolvePlaybackSegment(tripleReReadTimeline, 45.0);
  assert.equal(t3.segment.fragment, 'para-A');
  assert.equal(t3.segment.occurrenceId, '2');
});

