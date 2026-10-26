"""Bounded ASR boundary deconfliction without extending any observed interval."""
import math

MAX_BOUNDARY_OVERLAP_SECONDS = .05


def resolve_boundaries(segments):
  """Split only tiny adjacent boundary overlaps; reject swallowed/reversed intervals.

  Keep raw intervals in each changed segment. This is a declared display-boundary
  heuristic, not acoustic certification. Larger conflicts require realignment.
  """
  output, last_by_track, repairs = [], {}, []
  for original in segments:
    seg = dict(original)
    a, b = seg.get("start"), seg.get("end")
    if (type(a) not in (int, float) or type(b) not in (int, float)
        or not math.isfinite(a) or not math.isfinite(b) or not 0 <= a < b):
      raise ValueError(f"Invalid observed segment interval {seg.get('audioSourceId')}: {a}..{b} fragment={seg.get('fragment')}; cannot manufacture duration")
    sid = seg["audioSourceId"]
    previous = last_by_track.get(sid)
    if previous is not None and a < previous["end"]:
      overlap = previous["end"] - a
      if (overlap > MAX_BOUNDARY_OVERLAP_SECONDS + 1e-9
          or a <= previous["start"] or b <= previous["end"]):
        raise ValueError(f"Unresolved timing conflict in {sid}: {previous['start']}..{previous['end']} vs {a}..{b}")
      boundary = (a + previous["end"]) / 2
      for item in (previous, seg):
        item.setdefault("observedInterval", {"start": item["start"], "end": item["end"]})
        item["boundaryMethod"] = "bounded-overlap-midpoint-unverified"
      repairs.append({"audioSourceId": sid, "overlap_s": overlap, "boundary": boundary,
                      "previousFragment": previous.get("fragment"), "nextFragment": seg.get("fragment")})
      previous["end"] = boundary
      seg["start"] = boundary
    output.append(seg)
    last_by_track[sid] = seg
  return output, repairs
