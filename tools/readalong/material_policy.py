"""User-selected book quarantine policy, separate from quality and publication."""
import hashlib
import json
from pathlib import Path

POLICY_PATH = Path(__file__).with_name("material-exceptions.json")


def policy_fingerprint():
  return hashlib.sha256(POLICY_PATH.read_bytes()).hexdigest()


def classify_quarantine(sample, report):
  policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
  if policy.get("schemaVersion") != 1 or not isinstance(policy.get("entries"), list):
    raise ValueError("Invalid user material policy")
  matches = [e for e in policy["entries"] if e.get("unitId") == sample["unitId"]
             and e.get("sourceFingerprint") == sample["sourceFingerprint"]]
  if len(matches) > 1:
    raise ValueError("Duplicate material policy")
  if not matches:
    return None
  entry = matches[0]
  if (entry.get("disposition") != "QUARANTINE_BOOK"
      or entry.get("qualityStatusUnchanged") is not True or entry.get("publishAllowed") is not False):
    raise ValueError("Material handling must not grant quality or publish approval")
  # A known source difference must not hide newly introduced script defects.
  required = ("schema", "inventory", "monotonicity", "dom_integrity", "density")
  if not all(report.get("quality_layers", {}).get(k) is True for k in required):
    return None
  codes = {e["code"] for e in report.get("errors", [])}
  if report.get("status") != "FAILED" or not codes.issubset(entry["allowedAuditCodes"]):
    return None
  # Only the recorded tail on the recorded physical source can be quarantined.
  allowed = entry["materialInterval"]
  pending = entry["mappingIntervalStillUnresolved"]
  gaps = [e for e in report.get("uncovered_intervals", [])
          if e.get("gap", 0) > (25 if e.get("type") == "HEAD_DELAY" else 20)]
  if not gaps or any(g.get("track") != allowed["audioSourceId"]
                     or g.get("start", -1) < pending["start"] - 0.001
                     or g.get("end", float("inf")) > allowed["end"] + 0.001
                     for g in gaps):
    return None
  return entry
