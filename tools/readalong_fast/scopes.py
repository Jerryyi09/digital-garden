"""Source-bound material ranges and exact interval-union arithmetic."""
import math
import re


def subtract_ranges(start, end, ranges):
  """Return physical portions not covered by an already merged range union."""
  result, edge = [], start
  for a, b in ranges:
    if b <= edge or a >= end:
      continue
    if a > edge:
      result.append((edge, min(a, end)))
    edge = max(edge, min(b, end))
  if edge < end:
    result.append((edge, end))
  return result


def material_ranges(material, sources, source_fingerprint=None):
  """Proposals never grant exemptions; authorize and bind selected ranges first."""
  if not material:
    return {}
  fingerprint = material.get("sourceFingerprint")
  if (not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
      or fingerprint != source_fingerprint):
    raise ValueError("Material policy must bind the current audio and EPUB fingerprint")
  if material.get("approved") is False or not (material.get("approved") is True or material.get("authorization")):
    raise ValueError("Unapproved material scope cannot alter quality metrics")
  if "materialIntervals" in material and "materialInterval" in material:
    raise ValueError("Use one material-range representation, not conflicting policies")
  rows = material.get("materialIntervals") if "materialIntervals" in material else [material.get("materialInterval")]
  if not isinstance(rows, list) or not rows:
    raise ValueError("Material policy needs explicit physical ranges")
  grouped = {}
  for row in rows:
    if (not isinstance(row, dict) or row.get("approved") is False
        or not isinstance(row.get("evidence"), str) or not row["evidence"].strip()):
      raise ValueError("Every material interval needs evidence and cannot be an unapproved proposal")
    sid, a, b = row.get("audioSourceId"), row.get("start"), row.get("end")
    if (sid not in sources or any(type(v) not in (int, float) or not math.isfinite(v) for v in (a, b))
        or not 0 <= a < b <= sources[sid]["duration"]):
      raise ValueError("Material interval is outside a registered physical audio source")
    grouped.setdefault(sid, []).append((a, b))
  merged = {}
  for sid, ranges in grouped.items():
    union = []
    for a, b in sorted(ranges):
      if union and a <= union[-1][1]:
        union[-1] = (union[-1][0], max(union[-1][1], b))
      else:
        union.append((a, b))
    merged[sid] = union
  return merged
