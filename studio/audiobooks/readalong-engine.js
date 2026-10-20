/**
 * Readalong Sync Engine
 * Core synchronization algorithms, timeline normalization, multi-track mapping,
 * and gap-tolerant binary search.
 */

/**
 * Normalizes, cleans, and sorts timeline segments.
 * Filters out invalid entries and guarantees monotonically non-decreasing start times.
 * @param {Array<Object>} rawTimeline
 * @returns {Array<Object>}
 */
export function normalizeTimeline(rawTimeline) {
  if (!Array.isArray(rawTimeline)) return []

  const valid = []
  for (let i = 0; i < rawTimeline.length; i++) {
    const s = rawTimeline[i]
    if (!s || typeof s !== "object") continue

    const start = Number(s.start)
    const end = Number(s.end)
    if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) continue

    valid.push({
      ...s,
      start,
      end,
      document: s.document ? String(s.document).trim() : "",
      fragment: s.fragment ? String(s.fragment).trim() : "",
      audioSourceId: s.audioSourceId ? String(s.audioSourceId).trim() : "",
      text: s.text ? String(s.text) : "",
    })
  }

  // Stable sort by start time, then by end time
  return valid.sort((a, b) => a.start - b.start || a.end - b.end)
}

/**
 * Normalizes a filename for matching by removing extensions and spaces.
 */
function cleanIdentifier(id) {
  if (!id) return ""
  return decodeURIComponent(String(id))
    .trim()
    .replace(/\.[a-zA-Z0-9]+$/, "")
    .toLowerCase()
}

/**
 * Filters timeline segments for a given audio track name in multi-track audiobooks.
 * Handles exact matches, URI-decoded matches, base filename matches, and fallback.
 * @param {Array<Object>} timeline
 * @param {string} trackName
 * @returns {Array<Object>}
 */
export function filterTimelineForTrack(timeline, trackName) {
  if (!Array.isArray(timeline) || !timeline.length) return []
  if (!trackName) return timeline

  const cleanedTrack = cleanIdentifier(trackName)

  // 1. Try exact match on audioSourceId
  const exact = timeline.filter((s) => s.audioSourceId === trackName)
  if (exact.length) return exact

  // 2. Try URI-decoded or cleaned base filename match
  const cleaned = timeline.filter((s) => s.audioSourceId && cleanIdentifier(s.audioSourceId) === cleanedTrack)
  if (cleaned.length) return cleaned

  // 3. If segments have no audioSourceId assigned (single-track book), use whole timeline
  const unassigned = timeline.filter((s) => !s.audioSourceId)
  if (unassigned.length === timeline.length) return timeline

  // 4. If all segments belong to only ONE distinct audioSourceId, use whole timeline
  const distinctSources = new Set(timeline.map((s) => s.audioSourceId).filter(Boolean))
  if (distinctSources.size <= 1) return timeline

  // If there are multiple tracks and none matches this track, return empty array
  // (prevents mapping segments from Chapter 5 onto Chapter 1!)
  return []
}

/**
 * Finds the active segment for a given playback timestamp using binary search.
 * Handles lead-in silence, sentence gaps, and trailing audio gracefully.
 *
 * @param {Array<Object>} timeline - Sorted array of segment objects
 * @param {number} time - Current playback time in seconds
 * @param {Object} [options]
 * @param {number} [options.maxLeadIn=5] - Maximum lead-in seconds before first segment to snap forward
 * @param {number} [options.gapHold=4] - Maximum seconds to hold previous segment during inter-sentence pause
 * @param {number} [options.maxTrailing=5] - Maximum seconds to keep last segment highlighted after audio finishes
 * @returns {Object|null} The matching segment, or null if in far silence
 */
export function findActiveSegment(timeline, time, options = {}) {
  if (!Array.isArray(timeline) || !timeline.length) return null
  if (!Number.isFinite(time) || time < 0) return null

  const maxLeadIn = options.maxLeadIn ?? 5
  const gapHold = options.gapHold ?? 4
  const maxTrailing = options.maxTrailing ?? 5

  const first = timeline[0]
  const last = timeline[timeline.length - 1]

  // Time is before the first segment
  if (time < first.start) {
    if (first.start - time <= maxLeadIn) {
      return first
    }
    return null // In extended intro music/silence, do not jump forward
  }

  // Time is after the last segment
  if (time >= last.end) {
    if (time - last.end <= maxTrailing) {
      return last
    }
    return null // Audio is way past last sentence
  }

  // Binary search for exact match [start, end)
  let low = 0
  let high = timeline.length - 1

  while (low <= high) {
    const mid = (low + high) >> 1
    const seg = timeline[mid]
    if (time < seg.start) {
      high = mid - 1
    } else if (time >= seg.end) {
      low = mid + 1
    } else {
      return seg
    }
  }

  // If time falls in a gap between two sentences:
  // high points to the segment that just ended; low points to the next upcoming segment.
  if (high >= 0) {
    // If extremely close to next segment (e.g. within 0.4s), anticipate next segment
    if (low < timeline.length) {
      const nextSeg = timeline[low]
      if (nextSeg.start - time <= 0.4) {
        return nextSeg
      }
    }

    const prevSeg = timeline[high]
    const gapDuration = time - prevSeg.end

    // Hold the previous segment if gap is within tolerance
    if (gapDuration <= gapHold) {
      return prevSeg
    }
  }

  return null
}

/**
 * Waits for an iframe to be ready with contentDocument and body.
 * @param {HTMLIFrameElement} frame
 * @param {number} [timeoutMs=1500]
 * @returns {Promise<Document>}
 */
export function waitForFrameReady(frame, timeoutMs = 1500) {
  return new Promise((resolve, reject) => {
    const check = () => {
      try {
        const doc = frame.contentDocument
        if (doc && doc.readyState === "complete" && doc.body) {
          return resolve(doc)
        }
      } catch (err) {
        return reject(err)
      }
    }

    check()

    let timer = null
    const onFrameLoad = () => {
      if (timer) clearTimeout(timer)
      frame.removeEventListener("load", onFrameLoad)
      check()
    }

    frame.addEventListener("load", onFrameLoad, { once: true })
    timer = setTimeout(() => {
      frame.removeEventListener("load", onFrameLoad)
      try {
        const doc = frame.contentDocument
        if (doc && doc.body) resolve(doc)
        else resolve(null)
      } catch {
        resolve(null)
      }
    }, timeoutMs)
  })
}
