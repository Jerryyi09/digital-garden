"""Generate selected real-book candidates using only hash-keyed cached ASR.

No ASR calls, full-library execution, publication or artificial success fallback.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from tools.readalong.authoritative_validator import audit_book_authoritative
from tools.readalong.batch_candidate_remapper import atomic_json, code_identity, input_blocker, sanitize_slug, snapshot
from tools.readalong.controlled_publisher import compute_dir_fingerprint
from tools.readalong.universal_aligner import align_single_book_universal
from tools.readalong.universal_stream_aligner import align_volume_full_stream
from tools.readalong.usability_evaluator import evaluate_readalong_usability
from tools.readalong.validator import compute_sha256


def verify_samples(inventory_path, output, unit_ids, cache_roots, allow_asr=False):
  output = Path(output).resolve()
  inventory_path = Path(inventory_path).resolve(strict=True)
  inventory = json.loads(inventory_path.read_text())
  units = {u["unit_id"]: u for u in inventory["units"]}
  if not unit_ids or len(unit_ids) != len(set(unit_ids)) or any(uid not in units for uid in unit_ids):
    raise ValueError("Select explicit distinct physical inventory units")
  if output.exists():
    raise ValueError("Use a new verification output directory")
  if any(output.is_relative_to(Path(units[uid]["book_dir"]).resolve()) for uid in unit_ids):
    raise ValueError("Verification output must be outside books")
  output.mkdir(parents=True)
  os.environ["READALONG_CACHE_ONLY"] = "0" if allow_asr else "1"
  os.environ["READALONG_CACHE_ROOT"] = str(output / "cache")
  os.environ["READALONG_CACHE_READ_ROOTS"] = os.pathsep.join(str(Path(p).resolve()) for p in cache_roots)
  identity = code_identity()
  policy_path = Path(__file__).with_name("material-exceptions.json")
  policy = json.loads(policy_path.read_text())
  policy_hash = compute_sha256(policy_path)
  summary = {"code_sha256": identity, "inventory_sha256": compute_sha256(inventory_path),
    "scope": "selected-real-books-cache-only-not-full-library", "published": False,
    "listeningVerified": False, "asrMode": "cache-or-local-asr" if allow_asr else "cache-only", "records": []}
  for uid in unit_ids:
    unit = units[uid]
    if input_blocker(unit):
      raise ValueError(f"Blocked sample {uid}: {input_blocker(unit)}")
    book = Path(unit["book_dir"])
    before = snapshot(book)
    expected = {t["rel_to_book"]: t["sha256"] for t in unit["audio_tracks"] + unit["epubs"]}
    if before["sources"] != expected:
      raise ValueError(f"Sample changed since physical inventory: {uid}")
    fingerprint = hashlib.sha256(json.dumps(before["sources"], sort_keys=True).encode()).hexdigest()
    material = next((e for e in policy["entries"] if e["unitId"] == uid), None)
    if material and material["sourceFingerprint"] != fingerprint:
      raise ValueError("Material policy source identity mismatch")
    dest = output / sanitize_slug(uid)
    record = {"unit_id": uid, "source_fingerprint": fingerprint, "candidate_path": str(dest)}
    try:
      duration = max(t["measured_duration"] for t in unit["audio_tracks"])
      if duration > 1800:
        align_volume_full_stream(book, dest, confirmed_reorders="auto_unique")
      else:
        align_single_book_universal(book, dest, max_sample_seconds=duration+1, confirmed_reorders="auto_unique")
      audit = audit_book_authoritative(dest, book_dir=book)
      audit["sourceFingerprint"] = fingerprint
      evaluation = evaluate_readalong_usability(audit, material)
      audit["usabilityEvaluation"] = evaluation
      audit["readalongUsability"] = evaluation["readalongUsability"]
      atomic_json(output / (sanitize_slug(uid)+"-audit.json"), audit)
      record.update(evaluation=evaluation, candidate_fingerprint=compute_dir_fingerprint(dest),
                    certificationStatus=audit["status"], errorCodes=[e["code"] for e in audit["errors"]])
    except Exception as exc:
      record.update(error=f"{type(exc).__name__}: {exc}", readalongUsability="SCRIPT_ERROR")
    finally:
      if (snapshot(book) != before or identity != code_identity()
          or policy_hash != compute_sha256(policy_path)):
        raise RuntimeError("Source/active/code/policy changed during verification")
    record["sourceUnchanged"] = True
    summary["records"].append(record)
    atomic_json(output / "verification.json", summary)
    print(json.dumps(record, ensure_ascii=False), flush=True)
  return summary


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--inventory", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--unit", action="append", required=True)
  parser.add_argument("--cache-read-root", type=Path, action="append", required=True)
  parser.add_argument("--allow-asr", action="store_true", help="Allow real local ASR for missing caches on selected samples only")
  args = parser.parse_args()
  summary = verify_samples(args.inventory, args.output, args.unit, args.cache_read_root, args.allow_asr)
  return 2 if any(r.get("error") or r.get("evaluation", {}).get("readalongUsability") not in {"USABLE", "USABLE_WITH_GAPS"}
                  for r in summary["records"]) else 0


if __name__ == "__main__":
  raise SystemExit(main())
