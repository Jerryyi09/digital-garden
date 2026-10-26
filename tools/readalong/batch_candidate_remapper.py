"""Conservative serial orchestration. No automatic retry, publication or gate changes."""
import argparse
from contextlib import contextmanager
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import traceback

from tools.readalong.universal_aligner import align_single_book_universal
from tools.readalong.universal_stream_aligner import align_volume_full_stream
from tools.readalong.authoritative_validator import audit_book_authoritative
from tools.readalong.candidate_safety import source_files
from tools.readalong.controlled_publisher import compute_dir_fingerprint
from tools.readalong.validator import compute_sha256


def sanitize_slug(name):
  return hashlib.sha256(name.encode()).hexdigest()[:20]


def atomic_json(path, data):
  path.parent.mkdir(parents=True, exist_ok=True)
  fd, temporary = tempfile.mkstemp(prefix=".checkpoint-", dir=path.parent)
  try:
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
      json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
      handle.write("\n")
      handle.flush()
      os.fsync(handle.fileno())
    os.replace(temporary, path)
  finally:
    if os.path.exists(temporary):
      os.unlink(temporary)


@contextmanager
def run_lock(run_dir):
  with (run_dir / ".batch.lock").open("a") as handle:
    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
      yield
    finally:
      fcntl.flock(handle, fcntl.LOCK_UN)


def input_blocker(unit, allow_epub_pairing=False):
  from tools.readalong.languages import normalized_language
  if not unit.get("audio_tracks"):
    return "MISSING_AUDIO"
  epubs = unit.get("epubs", [])
  if not epubs:
    return "MISSING_EPUB"
  if len(epubs) > 1:
    return None if allow_epub_pairing and any(e.get('valid_zip') is True for e in epubs) else 'MULTI_EPUB'
  if any("Physical file missing" in note for note in unit.get("discovery_notes", [])):
    return "MULTI_EPUB_PENDING_OPERATOR_PAIRING"
  if epubs[0].get("valid_zip") is not True:
    return "INVALID_EPUB"
  override = unit.get('languageOverride', {})
  if isinstance(override, dict) and normalized_language(override.get('language')) == 'en' and override.get('source') == 'direct_user_confirmation':
    return None
  languages = [normalized_language(lang) for lang in unit.get("detected_languages", [])]
  known = {lang for lang in languages if lang is not None}
  if known and 'en' not in known:
    return "LANGUAGE_REQUIRES_REVIEW"
  return None


def snapshot(book):
  files = source_files(book, {".mp3", ".m4a", ".m4b", ".epub"})
  return {
    "sources": {p.relative_to(book).as_posix(): compute_sha256(p) for p in files},
    "active": compute_dir_fingerprint(book / "readalong")
              if (book / "readalong").exists() else None,
  }


def code_identity():
  # Bind dirty source contents too; a Git commit alone is not an engine identity.
  paths = sorted(Path(__file__).parent.rglob("*.py"))
  digest = hashlib.sha256()
  for path in paths:
    if ".venv" in path.parts or "tests" in path.parts:
      continue
    digest.update(str(path.relative_to(Path(__file__).parent)).encode())
    digest.update(path.read_bytes())
  return digest.hexdigest()


class BatchRemapper:
  def __init__(self, run_dir, require_gate=False):
    self.run_dir = Path(run_dir).resolve(strict=True)
    self.stop_md = self.run_dir / "STOP.md"
    if self.stop_md.exists():
      raise RuntimeError("Batch is stopped. Preserve this run; explicit reviewed recovery is required.")
    self.gate_path = self.run_dir / "recovery-gate.json"
    self.inv_path = self.run_dir / "inventory.json"
    self.inventory = json.loads(self.inv_path.read_text(encoding="utf-8"))
    self.units = self.inventory["units"]
    ids = [u["unit_id"] for u in self.units]
    if not ids or len(ids) != len(set(ids)):
      raise ValueError("Empty or duplicate inventory units")
    self.results_json = self.run_dir / "results.json"
    self.events_log = self.run_dir / "events.jsonl"
    self.identity = {"inventorySha256": compute_sha256(self.inv_path), "codeSha256": code_identity()}
    self.predecessor_dir = self._resolve_and_verify_predecessor()
    self.ledger = self._load_ledger()
    # Construction without a gate is allowed for inspection only. run_unit
    # always performs the live check, including direct Python callers.
    if require_gate:
      self._gate_decision = self._assert_gate()

  def _assert_gate(self):
    from tools.readalong.recovery_gate import assert_recovery_gate_passed
    if not (self.run_dir / "run.json").is_file():
      raise RuntimeError("Execution requires explicit run metadata and predecessor review")
    self._resolve_and_verify_predecessor()
    return assert_recovery_gate_passed(
      self.gate_path, expected_books={u["unit_id"]: u["book_dir"] for u in self.units})

  def _resolve_and_verify_predecessor(self):
    run_json_path = self.run_dir / "run.json"
    if not run_json_path.exists():
      return None
    try:
      meta = json.loads(run_json_path.read_text(encoding="utf-8"))
    except Exception as exc:
      raise ValueError(f"Corrupt run.json: {exc}")
    # Verify run.json matches live code and inventory identity (R03-05)
    meta_code = meta.get("code_sha256")
    meta_inv = meta.get("inventory_sha256")
    if meta_code != self.identity["codeSha256"]:
      raise ValueError("run.json and results.json identity mismatch: code_sha256 differs")
    if meta_inv != self.identity["inventorySha256"]:
      raise ValueError("run.json and results.json identity mismatch: inventory_sha256 differs")

    pred_str = meta.get("predecessor")
    if not pred_str:
      return None
    pred_dir = Path(pred_str)
    if not pred_dir.is_absolute():
      pred_dir = (self.run_dir.parent / pred_str).resolve()
    if not pred_dir.is_dir():
      raise RuntimeError(f"Declared predecessor directory does not exist: {pred_dir}")
    pred_results = pred_dir / "results.json"
    if not pred_results.is_file():
      raise RuntimeError(f"Predecessor results.json missing: {pred_results}")
    if meta.get("predecessor_results_sha256") != compute_sha256(pred_results):
      raise ValueError("Predecessor ledger fingerprint missing or changed")
    return pred_dir

  def _load_ledger(self):
    if not self.results_json.exists():
      # Never reset attempts when candidates survived a lost checkpoint.
      if (self.run_dir / "candidates").exists() and any((self.run_dir / "candidates").iterdir()):
        raise RuntimeError("Candidates exist without a checkpoint; manual reconciliation required")
      inherited_records = {}
      if self.predecessor_dir:
        if self._resolve_and_verify_predecessor() != self.predecessor_dir:
          raise ValueError("Predecessor changed during recovery")
        pred_results = self.predecessor_dir / "results.json"
        try:
          pred_data = json.loads(pred_results.read_text(encoding="utf-8"))
          pred_recs = pred_data.get("records", {})
          for uid, prec in pred_recs.items():
            if uid in {u["unit_id"] for u in self.units}:
              attempts = prec.get("attempts")
              if type(attempts) is not int or not 0 <= attempts <= 2:
                raise ValueError("Invalid historical attempt budget")
              # Inherit costs, never unproven old completion/quality claims.
              inherited_records[uid] = {
                "unitId": uid, "attempts": attempts, "inheritedOnly": True,
                "workflow_completed": False, "candidateStatusAfter": None,
                "predecessor": str(self.predecessor_dir),
                "predecessorLedgerSha256": compute_sha256(pred_results),
              }
        except Exception as exc:
          raise RuntimeError(f"Failed reading predecessor ledger: {exc}")
      return {"schema_version": 3, "identity": self.identity, "records": inherited_records}
    data = json.loads(self.results_json.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("schema_version") != 3 or data.get("identity") != self.identity
        or not isinstance(data.get("records"), dict)):
      raise ValueError("Checkpoint incompatible, changed or corrupt; refusing budget reset")
    for key, rec in data["records"].items():
      if not isinstance(rec, dict):
        raise ValueError("Invalid checkpoint record")
      if key not in {u["unit_id"] for u in self.units}:
        raise ValueError("Checkpoint contains an unknown unit")
      attempts = rec.get("attempts")
      if type(attempts) is not int or not 0 <= attempts <= 2:
        raise ValueError("Invalid persisted attempt budget")
    return data

  def _log_event(self, kind, **details):
    with self.events_log.open("a", encoding="utf-8") as handle:
      handle.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                               "event": kind, **details}, ensure_ascii=False) + "\n")
      handle.flush()
      os.fsync(handle.fileno())

  def _save_ledger(self):
    atomic_json(self.results_json, self.ledger)
    records = list(self.ledger["records"].values())
    fields = ["unitId", "activeStatusBefore", "candidateStatusAfter", "attempts",
              "blockingReason", "candidatePath", "finalReportPath", "activeChanged", "published"]
    # JSON is the authoritative checkpoint; CSV/Markdown are derived views.
    with (self.run_dir / "results.csv").open("w", encoding="utf-8", newline="") as handle:
      writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
      writer.writeheader()
      writer.writerows(records)
    counts = {}
    for rec in records:
      status = rec["candidateStatusAfter"]
      counts[status] = counts.get(status, 0) + 1
    (self.run_dir / "summary.md").write_text(
      "# Isolated candidate run\n\n"
      + f"Recorded units: {len(records)} / {len(self.units)}\n\n"
      + json.dumps(counts, ensure_ascii=False, indent=2)
      + "\n\nNo production replacement or deployment. See results.json for evidence.\n",
      encoding="utf-8")

  def trigger_stop(self, reason, unit_id, details):
    self._log_event("GLOBAL_BATCH_STOP_TRIGGERED", unit_id=unit_id, reason=reason)
    self.stop_md.write_text(
      "# Emergency batch stop\n\n"
      + f"Unit: {unit_id}\n\nReason: {reason}\n\n"
      + json.dumps(details, ensure_ascii=False, indent=2)
      + "\n\n" + traceback.format_exc()
      + "\nDo not resume this batch or reset attempts without explicit reviewed recovery.\n",
      encoding="utf-8")
    raise RuntimeError(f"GLOBAL_STOP: {reason}")

  def run_unit(self, unit):
    with run_lock(self.run_dir):
      if self.stop_md.exists():
        raise RuntimeError("STOP.md present; refusing resume")
      self._gate_decision = self._assert_gate()
      self.ledger = self._load_ledger()
      try:
        return self._run_unit_locked(unit)
      except Exception as exc:
        if self.stop_md.exists():
          raise
        self.trigger_stop(str(exc), unit["unit_id"], {"exceptionType": type(exc).__name__})

  def _run_unit_locked(self, unit):
    uid, book = unit["unit_id"], Path(unit["book_dir"])
    before = snapshot(book)
    expected = {entry["rel_to_book"]: entry["sha256"]
                for entry in unit["audio_tracks"] + unit.get("epubs", [])}
    if before["sources"] != expected:
      raise RuntimeError("Source inventory changed or omitted source files")
    if before["active"] != unit.get("active_readalong_fingerprint"):
      raise RuntimeError("Active fingerprint differs from inventory")
    prior = self.ledger["records"].get(uid)
    budget_before = prior.get("attempts", 0) if prior else 0
    decision = getattr(self, "_gate_decision", {}).get("sampleEvaluations", {}).get(uid, {})
    if decision.get("batchExcluded") is True:
      report_path = self.run_dir / "audits" / sanitize_slug(uid) / "material-quarantine.json"
      atomic_json(report_path, decision["audit"])
      record = {"unitId": uid, "attempts": budget_before,
                "activeStatusBefore": None, "candidateStatusAfter": decision["audit"]["status"],
                "workflowStatus": "QUARANTINED_MATERIAL", "workflow_completed": True,
                "blockingReason": decision["materialIssue"]["classification"],
                "sourceSnapshot": before, "materialIssue": decision["materialIssue"],
                "candidatePath": decision["candidatePath"],
                "candidateFingerprint": decision["candidateFingerprint"],
                "finalReportPath": str(report_path), "activeChanged": False, "published": False}
      self.ledger["records"][uid] = record
      self._save_ledger()
      self._log_event("MATERIAL_QUARANTINED", unit_id=uid, qualityStatus=record["candidateStatusAfter"])
      return record
    if budget_before >= 2:
      raise RuntimeError("Historical attempt budget exhausted; no generation permitted")
    if prior and not prior.get("inheritedOnly"):
      if prior.get("sourceSnapshot") != before:
        raise RuntimeError("Inputs changed since checkpoint")
      if prior.get("workflow_completed"):
        # Completed results must still exist and represent the same candidate.
        if prior.get("candidatePath"):
          if compute_dir_fingerprint(Path(prior["candidatePath"])) != prior.get("candidateFingerprint"):
            raise RuntimeError("Completed candidate changed or disappeared")
        return prior
      raise RuntimeError("Interrupted attempt requires manual reconciliation; budget remains consumed")

    baseline = audit_book_authoritative(book)
    rec = {
      "unitId": uid, "attempts": budget_before, "activeStatusBefore": baseline["status"],
      "candidateStatusAfter": "PENDING", "sourceSnapshot": before,
      "blockingReason": input_blocker(unit), "activeChanged": False, "published": False,
      "candidatePath": None, "finalReportPath": None, "workflow_completed": False,
    }
    self.ledger["records"][uid] = rec
    if rec["blockingReason"]:
      rec.update(candidateStatusAfter="UNSUPPORTED" if rec["blockingReason"] == "MISSING_EPUB"
                 else "NEEDS_REVIEW", workflow_completed=True)
      self._save_ledger()
      return rec
    if baseline["status"] == "PASS":
      rec.update(candidateStatusAfter="PASS", workflow_completed=True)
      self._save_ledger()
      return rec
    if baseline["status"] == "NEEDS_REVIEW":
      rec.update(candidateStatusAfter="NEEDS_REVIEW", workflow_completed=True,
                 blockingReason="INDEPENDENT_REFERENCE_REQUIRED")
      self._save_ledger()
      return rec

    durations = [t["measured_duration"] for t in unit["audio_tracks"]]
    if any(type(value) not in (int, float) or not math.isfinite(value) or value <= 0
           for value in durations):
      raise ValueError("Invalid inventoried audio duration")
    duration = max(durations)
    mode = "stream" if duration > 1800 else "universal"
    attempt_number = budget_before + 1
    attempt_name = f"attempt-{attempt_number:02d}"
    candidate = self.run_dir / "candidates" / sanitize_slug(uid) / attempt_name
    if candidate.exists():
      raise RuntimeError("Attempt directory already exists; refusing overwrite or budget reset")
    rec.update(attempts=attempt_number, candidatePath=str(candidate), generationMode=mode,
               parameters={"blockSeconds": 1800} if mode == "stream"
                          else {"maxSampleSeconds": duration + 1, "maxTracks": None},
               candidateStatusAfter="RUNNING")
    # Reserve the attempt durably before invoking any costly/mutating generator.
    self._save_ledger()
    self._log_event("ATTEMPT_STARTED", unit_id=uid, attempt=attempt_number)
    try:
      if mode == "stream":
        align_volume_full_stream(book, candidate, block_duration_s=1800)
      else:
        align_single_book_universal(book, candidate, max_sample_seconds=duration + 1, max_tracks=None)
      report = audit_book_authoritative(candidate, book_dir=book)
      report_path = self.run_dir / "audits" / sanitize_slug(uid) / f"{attempt_name}.json"
      atomic_json(report_path, report)
      rec.update(candidateStatusAfter=report["status"], finalReportPath=str(report_path),
                 candidateFingerprint=compute_dir_fingerprint(candidate))
      manifest = json.loads((candidate / "readalong.manifest.json").read_text())
      if manifest.get("sampleAligned") is not False:
        raise RuntimeError("Full-book run produced a sampled candidate")
      if code_identity() != self.identity["codeSha256"]:
        raise RuntimeError("Code changed during processing")
    finally:
      if snapshot(book) != before:
        raise RuntimeError("Source or active assets changed during generation")
    self._save_ledger()
    if report["status"] == "FAILED":
      # Diagnostics require review before any retry; smaller blocks are not a
      # valid automatic repair for DOM corruption or lexical algorithm defects.
      self.trigger_stop("Candidate failed hard gates; review before any further book or retry", uid,
                        {"reportPath": str(report_path), "errors": report.get("errors", [])})
    rec.update(workflow_completed=True,
               blockingReason="INDEPENDENT_REFERENCE_REQUIRED" if report["status"] != "PASS" else None)
    self._save_ledger()
    self._log_event("ATTEMPT_AUDITED", unit_id=uid, status=report["status"])
    return rec


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("run_dir", type=Path)
  parser.add_argument("--unit", help="Explicit unit ID; omit only for an authorized full batch")
  args = parser.parse_args()
  try:
    remapper = BatchRemapper(args.run_dir, require_gate=True)
    units = [u for u in remapper.units if u["unit_id"] == args.unit] if args.unit else remapper.units
    if not units:
      raise ValueError("Requested unit not found")
    results = [remapper.run_unit(unit) for unit in units]
    return 0 if all(result["candidateStatusAfter"] == "PASS" for result in results) else 2
  except (OSError, ValueError, KeyError, RuntimeError) as exc:
    print(json.dumps({"status": "STOPPED", "error": str(exc)}, ensure_ascii=False))
    return 2


if __name__ == "__main__":
  raise SystemExit(main())
