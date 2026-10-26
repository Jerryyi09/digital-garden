"""Recompute strict timing evidence; candidate metrics are never trusted."""
import hashlib
import json
import math
from pathlib import Path

POLICY_VERSION = "readalong-strict-200ms-v2"
MAX_ALLOWED_MAE = 0.08
MAX_ALLOWED_P95 = 0.15
MAX_ALLOWED_PEAK = 0.20
MIN_COVERAGE_RATIO = 1.0


def sha256(path):
  with Path(path).open("rb") as stream:
    return hashlib.file_digest(stream, "sha256").hexdigest()


def occurrence_key(segment):
  return (segment.get("audioSourceId"), segment.get("document"),
          segment.get("fragment"), segment.get("occurrenceId", "0"))


def valid_interval(segment):
  a, b = segment.get("start"), segment.get("end")
  return (all(isinstance(v, (int, float)) and not isinstance(v, bool)
              and math.isfinite(v) for v in (a, b)) and 0 <= a < b)


def evaluate_acoustic_accuracy(timeline, reference_data=None):
  """Require full declared scope; fragment-only keys are legacy metric-test input."""
  if not reference_data or not timeline:
    return {"status": "TIMING_UNVERIFIED", "passed": False, "metrics": None}
  errors, used = [], set()
  matched = 0
  for seg in timeline:
    key = occurrence_key(seg)
    if key not in reference_data:
      key = (seg.get("audioSourceId"), seg.get("fragment"))
    if key not in reference_data:
      key = seg.get("fragment")
    ref = reference_data.get(key)
    if ref is None:
      continue
    if key in used or not valid_interval(seg) or not valid_interval(ref):
      return {"status": "ACCURACY_REJECTED", "passed": False, "metrics": None}
    used.add(key)
    matched += 1
    errors.extend([abs(seg["start"] - ref["start"]), abs(seg["end"] - ref["end"])])
  if not errors:
    return {"status": "TIMING_UNVERIFIED", "passed": False, "metrics": None}
  errors.sort()
  metrics = {
    "evaluated_segments": matched, "total_segments": len(timeline),
    "coverage_ratio": matched / len(timeline),
    "mae_seconds": sum(errors) / len(errors),
    "p50_seconds": errors[len(errors) // 2],
    "p95_seconds": errors[min(len(errors)-1, math.ceil(len(errors)*.95)-1)],
    "max_error_seconds": max(errors),
  }
  accurate = (metrics["mae_seconds"] <= MAX_ALLOWED_MAE
              and metrics["p95_seconds"] <= MAX_ALLOWED_P95
              and metrics["max_error_seconds"] <= MAX_ALLOWED_PEAK)
  complete = matched == len(timeline)
  status = "ACCURACY_REJECTED" if not accurate else (
    "TIMING_VERIFIED" if complete else "COVERAGE_INSUFFICIENT")
  return {"status": status, "passed": accurate and complete, "metrics": metrics,
          "policyVersion": POLICY_VERSION,
          "coverage_status": "COVERAGE_SUFFICIENT" if complete else "COVERAGE_INSUFFICIENT"}


def verify_reference(reference_path, assets, book, timeline_path, timeline, sources):
  """Trust only an operator-selected external reference, never a manifest path.

  Human approval remains the operator's responsibility. The reference records an
  approved scope and binds it to exact source, document and timeline bytes.
  """
  if reference_path is None:
    return {"status": "TIMING_UNVERIFIED", "passed": False, "metrics": None}
  path = Path(reference_path).resolve(strict=True)
  if path.is_relative_to(assets.resolve()) or path.is_relative_to(book.resolve()):
    raise ValueError("Reference must be outside candidate and book directories")
  raw = path.read_bytes()
  ref = json.loads(raw)
  if (ref.get("schemaVersion") != 1 or ref.get("policyVersion") != POLICY_VERSION
      or ref.get("scope") != "complete-timeline"
      or not isinstance(ref.get("approvedBy"), str) or not ref["approvedBy"].strip()
      or not isinstance(ref.get("approvedAt"), str) or not ref["approvedAt"].strip()):
    raise ValueError("Reference requires approved identity, date, policy and scope")
  if ref.get("timelineSha256") != sha256(timeline_path) or ref.get("audioSha256") != sources:
    raise ValueError("Reference source/timeline hash mismatch")
  docs = ref.get("documentsSha256")
  if not isinstance(docs, dict) or set(docs) != {s["document"] for s in timeline}:
    raise ValueError("Reference document scope mismatch")
  for name, digest in docs.items():
    doc = (assets / name).resolve(strict=True)
    if not doc.is_relative_to(assets.resolve()) or sha256(doc) != digest:
      raise ValueError("Reference document hash mismatch")
  refs = {}
  for seg in ref.get("segments", []):
    key = occurrence_key(seg)
    if key in refs or not all(isinstance(v, str) and v for v in key):
      raise ValueError("Reference requires unique complete occurrence identities")
    refs[key] = seg
  if set(refs) != {occurrence_key(s) for s in timeline} or len(refs) != len(timeline):
    raise ValueError("Reference must cover every occurrence exactly once")
  result = evaluate_acoustic_accuracy(timeline, refs)
  result["referenceSha256"] = hashlib.sha256(raw).hexdigest()
  result["approvedBy"] = ref["approvedBy"]
  return result
