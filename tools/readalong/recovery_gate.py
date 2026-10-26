"""Live structural recovery checks. Stored decisions and reports are never authority."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from tools.readalong.acoustic_evaluator import POLICY_VERSION
from tools.readalong.authoritative_validator import audit_book_authoritative
from tools.readalong.candidate_safety import source_files
from tools.readalong.controlled_publisher import compute_dir_fingerprint
from tools.readalong.validator import compute_sha256

REQUIRED_STRUCTURAL_LAYERS = (
  "schema", "inventory", "monotonicity", "dom_integrity", "coverage_and_gaps", "density",
)
REQUIRED_UNITS = ("心智成长/Make Your Bed", "文学作品/了不起的盖茨比")
SHA256 = re.compile(r"[0-9a-f]{64}")


class RecoveryGateRejection(RuntimeError):
  pass


def current_identity():
  from tools.readalong.batch_candidate_remapper import code_identity
  from tools.readalong.config import resolve_model_path
  from tools.readalong.input_inventory import model_fingerprint
  from tools.readalong.material_policy import policy_fingerprint
  return {"codeSha256": code_identity(), "policyVersion": POLICY_VERSION,
          "modelSha256": model_fingerprint(resolve_model_path()),
          "materialPolicySha256": policy_fingerprint()}


def source_fingerprint(book):
  book = Path(book).resolve(strict=True)
  files = source_files(book, {".mp3", ".m4a", ".m4b", ".wav", ".epub"})
  if not files:
    raise ValueError("No physical book inputs")
  rows = {}
  for path in files:
    if path.is_symlink() or not path.resolve().is_relative_to(book):
      raise ValueError("Linked or escaping input")
    rows[path.relative_to(book).as_posix()] = compute_sha256(path)
  return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def bind_sample(unit_id, book_dir, candidate_dir):
  """Explicit operator-selected paths; binding is integrity, not approval."""
  return {"unitId": unit_id, "bookDir": str(Path(book_dir).resolve(strict=True)),
          "candidatePath": str(Path(candidate_dir).resolve(strict=True)),
          "expectedFingerprint": compute_dir_fingerprint(candidate_dir),
          "sourceFingerprint": source_fingerprint(book_dir)}


def evaluate_sample_candidate(sample_info, expected_books=None):
  uid = sample_info.get("unitId") if isinstance(sample_info, dict) else None
  result = {"unitId": uid, "passed": False, "status": "REJECTED"}
  try:
    if not isinstance(uid, str) or not uid:
      raise ValueError("Missing unit identity")
    book = Path(sample_info["bookDir"]).resolve(strict=True)
    candidate = Path(sample_info["candidatePath"]).resolve(strict=True)
    if expected_books is not None:
      if uid not in expected_books or book != Path(expected_books[uid]).resolve(strict=True):
        raise ValueError("Sample book does not match execution inventory")
    for field in ("expectedFingerprint", "sourceFingerprint"):
      if not isinstance(sample_info.get(field), str) or not SHA256.fullmatch(sample_info[field]):
        raise ValueError(f"Required SHA-256 missing or invalid: {field}")
    before = compute_dir_fingerprint(candidate)
    if before != sample_info["expectedFingerprint"]:
      raise ValueError("Candidate fingerprint mismatch")
    source_before = source_fingerprint(book)
    if source_before != sample_info["sourceFingerprint"]:
      raise ValueError("Physical source fingerprint mismatch")
    # No reportPath or caller-supplied layers/status can grant permission.
    report = audit_book_authoritative(candidate, book_dir=book)
    if compute_dir_fingerprint(candidate) != before or source_fingerprint(book) != source_before:
      raise ValueError("Candidate or source changed during live audit")
    layers = report.get("quality_layers", {})
    hard_errors = [e for e in report.get("errors", [])
                   if e.get("code") != "ERR_TIMING_UNVERIFIED"]
    structure_ok = all(layers.get(k) is True for k in REQUIRED_STRUCTURAL_LAYERS)
    status_ok = report.get("status") in {"PASS", "NEEDS_REVIEW"}
    if not structure_ok or hard_errors or not status_ok:
      result.update(reason="Live authoritative audit rejected structural recovery", audit=report)
      from tools.readalong.material_policy import classify_quarantine
      material = classify_quarantine(sample_info, report)
      if material is not None:
        result.update(status="QUARANTINED_MATERIAL_MISMATCH", batchExcluded=True,
                      materialIssue=material, candidatePath=str(candidate),
                      candidateFingerprint=before, sourceFingerprint=source_before)
      return result
    if report["status"] == "PASS" and layers.get("timing_verified") is not True:
      raise ValueError("Inconsistent acoustic status")
    result.update(passed=True,
                  status="FULL_PASS" if report["status"] == "PASS" else "STRUCTURAL_PASS",
                  acousticVerified=layers.get("timing_verified") is True,
                  candidateFingerprint=before, sourceFingerprint=source_before,
                  quality_layers=layers, audit=report)
  except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
    result["reason"] = str(exc)
  return result


def evaluate_recovery_gate(samples, required_units=None, expected_books=None):
  required = list(REQUIRED_UNITS) if required_units is None else required_units
  # Callers may ADD mandatory samples, never remove the canonical ones.
  if (not isinstance(required, list) or not all(isinstance(u, str) and u for u in required)
      or len(required) != len(set(required)) or not set(REQUIRED_UNITS).issubset(required)):
    raise RecoveryGateRejection("Required samples cannot be empty, reduced or duplicated")
  if not isinstance(samples, list):
    raise RecoveryGateRejection("Sample bindings must be a list")
  decisions = {}
  for sample in samples:
    if not isinstance(sample, dict) or not isinstance(sample.get("unitId"), str):
      raise RecoveryGateRejection("Malformed sample identity")
    uid = sample["unitId"]
    if uid in decisions:
      raise RecoveryGateRejection("Duplicate sample identity")
    decisions[uid] = evaluate_sample_candidate(sample, expected_books)
  missing = [uid for uid in required if uid not in decisions]
  quarantined = [uid for uid, d in decisions.items() if d.get("batchExcluded") is True]
  failed = [uid for uid, d in decisions.items() if not d["passed"] and uid not in quarantined]
  passed = not missing and not failed
  decision = ("APPROVED_FOR_BATCH_WITH_QUARANTINE" if quarantined else "APPROVED_FOR_BATCH") if passed else "REJECTED"
  return {"gatePassed": passed, "decision": decision, "quarantinedUnits": quarantined,
          "requiredUnits": required, "missingRequiredUnits": missing, "failedUnits": failed,
          "sampleEvaluations": decisions}


def build_gate_evidence(samples):
  identity = current_identity()
  decision = evaluate_recovery_gate(samples)
  if current_identity() != identity:
    raise RecoveryGateRejection("Code/model changed during gate audit")
  return {"schemaVersion": 2, "identity": identity, "samples": samples, **decision}


def assert_recovery_gate_passed(gate_evidence_path, expected_books=None):
  """Recompute on entry; a stored 'approved' boolean never grants permission."""
  try:
    evidence = json.loads(Path(gate_evidence_path).read_text(encoding="utf-8"))
    if not isinstance(evidence, dict) or evidence.get("schemaVersion") != 2:
      raise RecoveryGateRejection("Missing live-gate schema v2 bindings")
    identity = current_identity()
    if evidence.get("identity") != identity:
      raise RecoveryGateRejection("Stale code, model or policy identity")
    decision = evaluate_recovery_gate(evidence["samples"], evidence.get("requiredUnits"), expected_books)
    if current_identity() != identity:
      raise RecoveryGateRejection("Code/model changed during gate audit")
    if not decision["gatePassed"]:
      raise RecoveryGateRejection(f"Live recovery gate rejected: {decision['failedUnits']}; missing={decision['missingRequiredUnits']}")
    return decision
  except (OSError, ValueError, TypeError, KeyError) as exc:
    raise RecoveryGateRejection(f"Invalid recovery evidence: {exc}") from exc


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("bindings", type=Path, help="JSON list of explicitly selected sample bindings")
  parser.add_argument("--output", required=True, type=Path, help="New private evidence file")
  args = parser.parse_args()
  if args.output.exists():
    parser.error("Use a new output file; preserve old gate evidence")
  from tools.readalong.batch_candidate_remapper import atomic_json
  evidence = build_gate_evidence(json.loads(args.bindings.read_text(encoding="utf-8")))
  atomic_json(args.output, evidence)
  print(json.dumps({"decision": evidence["decision"], "output": str(args.output)}))
  return 0 if evidence["gatePassed"] else 2


if __name__ == "__main__":
  raise SystemExit(main())
