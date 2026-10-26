export function timelinePathForSource(manifest, index, sourceId) {
  if (manifest?.timelineFormat !== "per-audio-source-v1") {
    return manifest?.timeline || "timeline.json"
  }
  const path = index?.files?.[sourceId]
  return typeof path === "string" && path ? path : null
}
