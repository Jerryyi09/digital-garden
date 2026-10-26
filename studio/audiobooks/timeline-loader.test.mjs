import assert from "node:assert/strict"
import test from "node:test"
import { timelinePathForSource } from "./timeline-loader.js"

test("keeps legacy timeline manifests compatible", () => {
  assert.equal(timelinePathForSource({ timeline: "timeline.json" }, null, "a.mp3"), "timeline.json")
})

test("selects only the current source shard", () => {
  const manifest = { timelineFormat: "per-audio-source-v1", timelineIndex: "timeline-index.json" }
  const index = { files: { "01.mp3": "timeline-shards/01.json", "02.mp3": "timeline-shards/02.json" } }
  assert.equal(timelinePathForSource(manifest, index, "02.mp3"), "timeline-shards/02.json")
  assert.equal(timelinePathForSource(manifest, index, "missing.mp3"), null)
})
