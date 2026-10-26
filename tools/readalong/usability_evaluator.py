"""Practical diagnostics; structural coverage is not acoustic timing proof."""
import math
import re

USABILITY_USABLE = "USABLE"
USABILITY_USABLE_WITH_GAPS = "USABLE_WITH_GAPS"
USABILITY_REVIEW_MAPPING = "REVIEW_MAPPING"
USABILITY_REVIEW_MATERIAL = "REVIEW_MATERIAL"
USABILITY_SCRIPT_ERROR = "SCRIPT_ERROR"
USABILITY_BLOCKED_INPUT = "BLOCKED_INPUT"
USABILITY_NOT_RUN = "NOT_RUN"

# Short pauses are reported, not claimed to be measured silence.
SHORT_PAUSE_SECONDS = 3.5
MAX_UNEXPLAINED_CONTINUOUS_SECONDS = 20.0
MAX_NARRATION_GAP_RATIO = .05
HARD_ERROR_CODES = {
  "ERR_SCHEMA_INVALID", "ERR_TRACK_INVENTORY_MISMATCH", "ERR_TIMESTAMP_OVERLAP",
  "ERR_TIMESTAMP_INVALID", "ERR_DOM_REFERENCE_BROKEN", "ERR_DUPLICATE_DOM_ID",
  "ERR_SECURITY_VIOLATION", "ERR_AUDIO_DURATION_MISMATCH", "ERR_AUDIO_SHA256_MISMATCH",
}


def _finite(value):
  return type(value) in (int, float) and math.isfinite(value)


def _measure(report, material):
  if not isinstance(report, dict) or report.get("status") not in {"PASS", "PARTIAL", "NEEDS_REVIEW", "FAILED"}:
    raise ValueError("Missing or invalid audit status")
  errors = report.get("errors")
  if not isinstance(errors, list) or any(not isinstance(e, dict) or not isinstance(e.get("code"), str) for e in errors):
    raise ValueError("Missing or invalid error list")
  layers = report.get("quality_layers", {})
  if not all(layers.get(k) is True for k in ("schema", "inventory", "monotonicity", "dom_integrity")):
    raise ValueError("Structural checks missing or failed")
  tracks = report.get("track_stats")
  if not isinstance(tracks, dict) or not tracks:
    raise ValueError("Missing measured track inventory")
  for tid, stats in tracks.items():
    if (not isinstance(tid, str) or not isinstance(stats, dict)
        or not _finite(stats.get("duration")) or stats["duration"] <= 0
        or type(stats.get("segment_count")) is not int or stats["segment_count"] < 0):
      raise ValueError("Invalid duration or segment count")
  total = sum(s["duration"] for s in tracks.values())
  if not math.isfinite(total):
    raise ValueError("Non-finite total measured duration")
  intervals = report.get("uncovered_intervals")
  if not isinstance(intervals, list):
    raise ValueError("Missing uncovered interval measurements")
  allowed = None
  if material is not None:
    fingerprint = material.get("sourceFingerprint", "")
    if (not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)
        or report.get("sourceFingerprint") != fingerprint):
      raise ValueError("Material interval is not bound to the audited sources")
    allowed = material.get("materialInterval", {})
    tid = allowed.get("audioSourceId")
    a, b = allowed.get("start"), allowed.get("end")
    if (tid not in tracks or not _finite(a) or not _finite(b) or not 0 <= a < b <= tracks[tid]["duration"] + .001
        or not allowed.get("evidence")):
      raise ValueError("Invalid or unsupported material interval")

  by_track = {tid: [] for tid in tracks}
  for item in intervals:
    if not isinstance(item, dict):
      raise ValueError("Invalid uncovered interval")
    tid, a, b = item.get("track"), item.get("start"), item.get("end")
    if (tid not in tracks or not _finite(a) or not _finite(b) or not 0 <= a < b <= tracks[tid]["duration"] + .001
        or not _finite(item.get("gap")) or abs(item["gap"] - (b-a)) > .001
        or item.get("type") not in {"HEAD_DELAY", "TAIL_GAP", "INTERNAL_VOID"}):
      raise ValueError("Invalid uncovered interval bounds")
    by_track[tid].append((a, b, item["type"]))

  scope = narration = pauses = raw_gap = 0.0
  max_void = max_internal = 0.0
  empty = 0
  for tid, ranges in by_track.items():
    prior_end = -1.0
    ranges.sort()
    for a, b, kind in ranges:
      if a < prior_end - .000001:
        raise ValueError("Overlapping or duplicated gap measurements")
      prior_end = b
    if tracks[tid]["segment_count"] == 0:
      empty += 1
      raw_gap += tracks[tid]["duration"]
      narration += tracks[tid]["duration"]
      max_void = max(max_void, tracks[tid]["duration"])
      continue
    for a, b, kind in ranges:
      raw_gap += b-a
      remaining = [(a, b)]
      if allowed and allowed["audioSourceId"] == tid:
        left, right = max(a, allowed["start"]), min(b, allowed["end"])
        if right > left:
          scope += right-left
          remaining = [(a, left), (right, b)]
      for left, right in remaining:
        length = right-left
        if length <= 0:
          continue
        if length <= SHORT_PAUSE_SECONDS:
          pauses += length
        else:
          narration += length
          max_void = max(max_void, length)
          if kind == "INTERNAL_VOID":
            max_internal = max(max_internal, length)
  narration_duration = total-scope
  if narration_duration <= 0:
    raise ValueError("No narrated scope remains")
  return {
    "total_audio_duration_s": total, "narration_scope_duration_s": narration_duration,
    "scope_gap_duration_s": scope, "narration_gap_duration_s": narration,
    "scope_gap_ratio": scope/total, "narration_gap_ratio": narration/narration_duration,
    "total_difference_ratio": (scope+narration)/total,
    "raw_unmapped_duration_s": raw_gap, "short_pause_duration_s": pauses,
    "max_continuous_unexplained_s": max_void,
    "max_continuous_internal_void_s": max_internal, "empty_tracks_count": empty,
    "measurement": "timeline-interval-estimate-not-acoustic-accuracy",
  }


def evaluate_readalong_usability(audit_report, material_policy_entry=None, unmapped_diagnostics=None):
  """Accept limited local gaps without inventing material or acoustic evidence."""
  errors = audit_report.get("errors", []) if isinstance(audit_report, dict) else []
  codes = [e.get("code") for e in errors if isinstance(e, dict)] if isinstance(errors, list) else []
  hard = [code for code in codes if code not in {"ERR_UNEXPLAINED_GAP", "ERR_TIMING_UNVERIFIED"}]
  cert = audit_report.get("status", "FAILED") if isinstance(audit_report, dict) else "FAILED"
  layers = audit_report.get("quality_layers", {}) if isinstance(audit_report, dict) else {}
  layers = layers if isinstance(layers, dict) else {}
  if cert == "PASS" and layers.get("timing_verified") is not True:
    cert = "NEEDS_REVIEW"
  metrics, notes = {}, []
  try:
    metrics = _measure(audit_report, material_policy_entry)
    if hard:
      raise ValueError("Structural or unknown audit errors")
    ratio = metrics["narration_gap_ratio"]
    evidence = audit_report.get("asrTokenEvidence")
    lexical_gap = None
    if evidence is not None:
      count, matched = evidence.get("audioTokens"), evidence.get("matchedTokens")
      if type(count) is not int or type(matched) is not int or not 0 <= matched <= count or count <= 0:
        raise ValueError("Invalid ASR token measurements")
      lexical_gap = 1-matched/count
      metrics["whole_audio_unmatched_asr_token_ratio"] = lexical_gap
      metrics["material_scope_asr_tokens"] = 0
      if "tokenIntervals" in evidence:
        intervals = evidence["tokenIntervals"]
        if not isinstance(intervals, list) or len(intervals) != count:
          raise ValueError("ASR token evidence count mismatch")
        excluded = excluded_matches = observed_matches = 0
        material_interval = material_policy_entry.get("materialInterval") if material_policy_entry else None
        for row in intervals:
          if (not isinstance(row, list) or len(row) != 4 or row[0] not in audit_report["track_stats"]
              or not _finite(row[1]) or not _finite(row[2]) or not 0 <= row[1] < row[2] <= audit_report["track_stats"][row[0]]["duration"]+.001
              or type(row[3]) is not int or row[3] not in (0, 1)):
            raise ValueError("Invalid observed ASR token interval")
          observed_matches += row[3]
          if (material_interval and row[0] == material_interval["audioSourceId"]
              and row[1] >= material_interval["start"] and row[2] <= material_interval["end"]):
            excluded += 1
            excluded_matches += row[3]
        if observed_matches != matched or count == excluded:
          raise ValueError("ASR token evidence totals do not close")
        lexical_gap = 1-(matched-excluded_matches)/(count-excluded)
        metrics["material_scope_asr_tokens"] = excluded
    metrics["unmatched_asr_token_ratio"] = lexical_gap
    metrics["short_pause_treatment"] = "heuristic-not-measured-silence"
    verified = audit_report.get("quality_layers", {}).get("timing_verified") is True
    if (metrics["empty_tracks_count"] or ratio > MAX_NARRATION_GAP_RATIO
        or metrics["max_continuous_unexplained_s"] > MAX_UNEXPLAINED_CONTINUOUS_SECONDS
        or (lexical_gap is None and not verified) or (lexical_gap is not None and lexical_gap > .05 + 1e-9)):
      usability, action = USABILITY_REVIEW_MAPPING, "REVIEW_LOCAL_MAPPING"
      notes.append("Unexplained gaps, insufficient lexical evidence or >5% unmatched ASR tokens require mapping review")
    elif metrics["narration_gap_duration_s"] > 0 or metrics["scope_gap_duration_s"] > 0:
      usability, action = USABILITY_USABLE_WITH_GAPS, "ACCEPT_WITH_GAPS"
      notes.append("Local gaps within 5% tolerance; declared material intervals are reported separately")
    else:
      usability, action = USABILITY_USABLE, "ACCEPT"
      notes.append("No significant unexplained timeline gaps; see independent certification status for acoustic accuracy")
  except (ValueError, TypeError, KeyError, AttributeError) as exc:
    usability, action = USABILITY_SCRIPT_ERROR, "REPAIR_SCRIPT_OR_INPUT"
    notes.append(str(exc))
  metrics["hard_error_count"] = len(hard)
  return {
    "readalongUsability": usability, "certificationStatus": cert,
    "metrics": metrics, "notes": notes, "actionRecommended": action,
    "materialPolicyApplied": bool(material_policy_entry) and usability != USABILITY_SCRIPT_ERROR,
    "hardErrors": hard, "policyVersion": "readalong-practical-5pct-v2",
    "acousticAccuracyVerified": layers.get("timing_verified") is True,
  }
