/**
 * Readalong Segment & Playback State Resolver (RA-09 Core)
 *
 * Honest synchronization states:
 * - ACTIVE: Currently inside a spoken segment.
 * - SHORT_PAUSE: In a brief gap between sentences (<= 3.5s); preserves highlight honestly.
 * - UNMAPPED: Long silence, musical bridge, or missing text (> 3.5s); revokes active highlight.
 * - BEFORE_START: Before track speech starts.
 * - AFTER_END: After track speech ends.
 */

export const SYNC_STATE = {
  ACTIVE: "ACTIVE",
  SHORT_PAUSE: "SHORT_PAUSE",
  UNMAPPED: "UNMAPPED",
  BEFORE_START: "BEFORE_START",
  AFTER_END: "AFTER_END",
  EMPTY: "EMPTY"
};

export function resolvePlaybackSegment(timeline, time, shortPauseMax = 3.5) {
  if (!timeline || !timeline.length) {
    return { state: SYNC_STATE.EMPTY, segment: null, nearest: null };
  }
  if (!Number.isFinite(time) || time < 0) {
    return { state: SYNC_STATE.EMPTY, segment: null, nearest: null };
  }

  const first = timeline[0];
  const last = timeline[timeline.length - 1];

  if (time < first.start) {
    const gap = first.start - time;
    return {
      state: gap <= 1.5 ? SYNC_STATE.SHORT_PAUSE : SYNC_STATE.BEFORE_START,
      segment: gap <= 1.5 ? first : null,
      nearest: first,
      gapSeconds: gap
    };
  }

  if (time >= last.end) {
    const gap = time - last.end;
    return {
      state: gap <= 2.0 ? SYNC_STATE.SHORT_PAUSE : SYNC_STATE.AFTER_END,
      segment: gap <= 2.0 ? last : null,
      nearest: last,
      gapSeconds: gap
    };
  }

  // Binary search for exact active segment
  let low = 0;
  let high = timeline.length - 1;
  while (low <= high) {
    const mid = (low + high) >> 1;
    const seg = timeline[mid];
    if (time < seg.start) {
      high = mid - 1;
    } else if (time >= seg.end) {
      low = mid + 1;
    } else {
      return {
        state: SYNC_STATE.ACTIVE,
        segment: seg,
        nearest: seg,
        gapSeconds: 0
      };
    }
  }

  // Not in active segment: determine pause vs long unmapped gap
  const prevSeg = high >= 0 ? timeline[high] : null;
  const nextSeg = low < timeline.length ? timeline[low] : null;

  const gapFromPrev = prevSeg ? time - prevSeg.end : Infinity;
  const gapToNext = nextSeg ? nextSeg.start - time : Infinity;
  const minGap = Math.min(gapFromPrev, gapToNext);
  const nearest = gapFromPrev <= gapToNext ? prevSeg : nextSeg;

  // Next sentence is about to start (< 0.5s anticipation)
  if (gapToNext <= 0.5 && nextSeg) {
    return {
      state: SYNC_STATE.SHORT_PAUSE,
      segment: nextSeg,
      nearest: nextSeg,
      gapSeconds: gapToNext
    };
  }

  // Normal sentence pause
  if (gapFromPrev <= shortPauseMax && prevSeg) {
    return {
      state: SYNC_STATE.SHORT_PAUSE,
      segment: prevSeg,
      nearest: prevSeg,
      gapSeconds: gapFromPrev
    };
  }

  // Truly unmapped gap (> shortPauseMax): revoke active highlight
  return {
    state: SYNC_STATE.UNMAPPED,
    segment: null,
    nearest: nearest,
    gapSeconds: minGap
  };
}
