import { test } from "node:test"
import assert from "node:assert/strict"
import {
  normalizeTimeline,
  filterTimelineForTrack,
  findActiveSegment,
} from "./readalong-engine.js"

// --- 复杂多场景 Fixture ---

// 模拟真实书籍片段：《时间简史》型（长片头音乐 + 间隙停顿 + 多文档）
const COMPLEX_BOOK_TIMELINE = [
  {
    audioSourceId: "chapter1.mp3",
    start: 120.0,
    end: 124.5,
    document: "text/part01.xhtml",
    fragment: "p1-seg1",
    text: "A well-known scientist once gave a public lecture.",
  },
  {
    audioSourceId: "chapter1.mp3",
    start: 125.5,
    end: 130.0,
    document: "text/part01.xhtml",
    fragment: "p1-seg2",
    text: "He described how the earth orbits around the sun.",
  },
  // 跨文档到 part02.xhtml
  {
    audioSourceId: "chapter1.mp3",
    start: 132.0,
    end: 138.0,
    document: "text/part02.xhtml",
    fragment: "p2-seg1",
    text: "At the end of the lecture, a little old lady stood up.",
  },
  // 第二音频文件：chapter2.mp3
  {
    audioSourceId: "chapter2.mp3",
    start: 5.0,
    end: 10.0,
    document: "text/part03.xhtml",
    fragment: "p3-seg1",
    text: "Chapter 2 begins here.",
  },
]

test("Readalong: Normalizes and sorts disordered or malformed timeline", () => {
  const disordered = [
    { start: 20, end: 25, document: "docB", fragment: "f2" },
    { start: 5, end: 10, document: "docA", fragment: "f1" },
    { start: "invalid", end: 15 },
    { start: 30, end: 20 }, // end < start
    null,
  ]
  const cleaned = normalizeTimeline(disordered)
  assert.equal(cleaned.length, 2)
  assert.equal(cleaned[0].fragment, "f1")
  assert.equal(cleaned[1].fragment, "f2")
  assert.equal(cleaned[0].start, 5)
  assert.equal(cleaned[1].start, 20)
})

test("Readalong: Handles lead-in silence without falsely jumping ahead", () => {
  const timeline = COMPLEX_BOOK_TIMELINE.filter((s) => s.audioSourceId === "chapter1.mp3")

  // During early intro music (0 - 110s), should NOT falsely highlight first sentence at 120s!
  assert.equal(findActiveSegment(timeline, 0), null)
  assert.equal(findActiveSegment(timeline, 60), null)
  assert.equal(findActiveSegment(timeline, 114), null)

  // Within 5s before start (115 - 120s), snaps forward to prepare reader
  assert.equal(findActiveSegment(timeline, 116)?.fragment, "p1-seg1")
  assert.equal(findActiveSegment(timeline, 119.9)?.fragment, "p1-seg1")
})

test("Readalong: Accurately locates active segments during normal playback", () => {
  const timeline = COMPLEX_BOOK_TIMELINE.filter((s) => s.audioSourceId === "chapter1.mp3")

  assert.equal(findActiveSegment(timeline, 120.0)?.fragment, "p1-seg1")
  assert.equal(findActiveSegment(timeline, 122.5)?.fragment, "p1-seg1")
  assert.equal(findActiveSegment(timeline, 126.0)?.fragment, "p1-seg2")
  assert.equal(findActiveSegment(timeline, 135.0)?.fragment, "p2-seg1")
})

test("Readalong: Adsorbs during inter-sentence pause (gap hold)", () => {
  const timeline = COMPLEX_BOOK_TIMELINE.filter((s) => s.audioSourceId === "chapter1.mp3")

  // Between seg1 (ends 124.5) and seg2 (starts 125.5) at 124.8s:
  // Should hold seg1 so highlight doesn't blink away during 1s pause
  const held = findActiveSegment(timeline, 124.8)
  assert.equal(held?.fragment, "p1-seg1")

  // At 125.3s (0.2s before seg2 starts): snaps smoothly to seg2
  const nextSnap = findActiveSegment(timeline, 125.3)
  assert.equal(nextSnap?.fragment, "p1-seg2")
})

test("Readalong: Handles audio trailing silence and far-out seek", () => {
  const timeline = COMPLEX_BOOK_TIMELINE.filter((s) => s.audioSourceId === "chapter1.mp3")
  const lastEnd = 138.0

  // 2 seconds after last sentence finishes: holds last segment
  assert.equal(findActiveSegment(timeline, lastEnd + 2.0)?.fragment, "p2-seg1")

  // Far beyond last sentence (e.g. 30s after audio ends): returns null
  assert.equal(findActiveSegment(timeline, lastEnd + 30.0), null)
})

test("Readalong: Filters timeline accurately for multi-track audiobooks", () => {
  // Exact match
  const track1 = filterTimelineForTrack(COMPLEX_BOOK_TIMELINE, "chapter1.mp3")
  assert.equal(track1.length, 3)
  assert.equal(track1[0].audioSourceId, "chapter1.mp3")

  const track2 = filterTimelineForTrack(COMPLEX_BOOK_TIMELINE, "chapter2.mp3")
  assert.equal(track2.length, 1)
  assert.equal(track2[0].audioSourceId, "chapter2.mp3")

  // Fuzzy match without extension
  const track1Fuzzy = filterTimelineForTrack(COMPLEX_BOOK_TIMELINE, "chapter1")
  assert.equal(track1Fuzzy.length, 3)

  // Unrelated track in multi-track book should NOT bleed into other tracks
  const trackUnknown = filterTimelineForTrack(COMPLEX_BOOK_TIMELINE, "chapter99.mp3")
  assert.equal(trackUnknown.length, 0)
})

test("Readalong: Detects cross-document transition during seek or playback", () => {
  const timeline = COMPLEX_BOOK_TIMELINE.filter((s) => s.audioSourceId === "chapter1.mp3")

  // Playing at part 1
  const segA = findActiveSegment(timeline, 123.0)
  assert.equal(segA.document, "text/part01.xhtml")

  // User drags slider (seek) to 135s -> crosses document boundary to part 2!
  const segB = findActiveSegment(timeline, 135.0)
  assert.equal(segB.document, "text/part02.xhtml")
  assert.notEqual(segA.document, segB.document)
})

test("Readalong: Robust against invalid or abnormal timestamps", () => {
  const timeline = COMPLEX_BOOK_TIMELINE.filter((s) => s.audioSourceId === "chapter1.mp3")

  assert.equal(findActiveSegment(timeline, -10), null)
  assert.equal(findActiveSegment(timeline, Number.NaN), null)
  assert.equal(findActiveSegment(timeline, Number.POSITIVE_INFINITY), null)
  assert.equal(findActiveSegment(null, 120), null)
  assert.equal(findActiveSegment([], 120), null)
})
