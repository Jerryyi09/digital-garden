"""Freeze a stopped predecessor and process only unfinished books with the fast path."""
import argparse
from collections import Counter
from contextlib import ExitStack, contextmanager
import errno
import fcntl
import hashlib
import json
from pathlib import Path
import sys
import time

from tools.readalong.batch_candidate_remapper import atomic_json, code_identity, input_blocker, sanitize_slug
from tools.readalong.config import resolve_model_path
from tools.readalong.input_inventory import model_fingerprint
from tools.readalong_fast.pipeline import InputCache, SpeechCache, file_hash, generate, stat_key
from tools.readalong_fast.decoding import AudioDecodeIssue, DecodeEnvironmentError

UNFINISHED = {"NOT_RUN", "ATTEMPT_RESERVED", "PREFLIGHT_ERROR", "INTERRUPTED_PER_UNIT_ERROR"}


def fast_identity():
  digest = hashlib.sha256(code_identity().encode())
  for p in sorted(Path(__file__).parent.glob("*.py")):
    digest.update(p.name.encode())
    digest.update(p.read_bytes())
  digest.update((Path(__file__).parent.parent/"readalong/material-exceptions.json").read_bytes())
  return digest.hexdigest()


@contextmanager
def locked(path):
  with Path(path).open("a") as stream:
    try:
      fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
      raise RuntimeError(f"BATCH_STILL_RUNNING: {path}; stop the predecessor safely before handoff") from exc
    yield


def select_unfinished(records, units):
  if set(records) != {u["unit_id"] for u in units}:
    raise ValueError("Predecessor ledger does not conserve physical inventory")
  selected, carried = [], {}
  for unit in units:
    uid = unit["unit_id"]
    row = records[uid]
    if row.get("workflow_status") not in UNFINISHED | {"COMPLETED", "BLOCKED_INPUT"}:
      raise ValueError("Unknown predecessor workflow; do not silently drop a book")
    if row.get("unit_id") != uid or type(row.get("attempts")) is not int or not 0 <= row["attempts"] <= 3:
      raise ValueError("Invalid predecessor attempt ledger")
    if row.get("workflow_status") in UNFINISHED and row["attempts"] < 3:
      selected.append(uid)
    else:
      carried[uid] = row
  return selected, carried


def load_or_plan(predecessor, output, repair_from=None, decode_review=None):
  predecessor, output = Path(predecessor).resolve(strict=True), Path(output).resolve()
  inv_path, results_path = predecessor/"inventory.json", predecessor/"results.json"
  inventory = json.loads(inv_path.read_text())
  old = json.loads(results_path.read_text())
  if inventory.get("summary", {}).get("conservation_verified") is not True:
    raise ValueError("Predecessor physical inventory is not closed")
  if (old.get("schema_version") != 1 or old.get("campaign_id") != predecessor.name
      or old.get("inventory_sha256") != file_hash(inv_path)):
    raise ValueError("Predecessor ledger identity mismatch")
  meta = json.loads((predecessor/"campaign.json").read_text())
  if meta.get("inventory_sha256") != file_hash(inv_path):
    raise ValueError("Predecessor campaign/inventory identity mismatch")
  if (output == predecessor or output.is_relative_to(predecessor)
      or any(output.is_relative_to(Path(u["book_dir"]).resolve()) for u in inventory["units"])):
    raise ValueError("Continuation output must be separate from predecessor and sources")
  selected, carried = select_unfinished(old["records"], inventory["units"])
  identity = {"predecessor": str(predecessor), "inventorySha256": file_hash(inv_path),
              "predecessorResultsSha256": file_hash(results_path), "codeSha256": fast_identity(),
              "modelSha256": model_fingerprint(resolve_model_path())}
  repair_records = None
  quarantined_uid = None
  if decode_review is not None and repair_from is None:
    raise ValueError("Decode recovery requires an explicit stopped fast predecessor")
  if repair_from is not None:
    repair_from = Path(repair_from).resolve(strict=True)
    if output == repair_from or output.is_relative_to(repair_from):
      raise ValueError("Repair output must be separate from its immutable predecessor")
    prior_plan = json.loads((repair_from/"plan.json").read_text())
    prior = json.loads((repair_from/"results.json").read_text())
    frozen = prior_plan["identity"]
    if (prior.get("identity") != frozen or (repair_from/"STOP.json").exists() and decode_review is None
        or any(frozen.get(k) != identity[k] for k in ("predecessor", "inventorySha256", "predecessorResultsSha256", "modelSha256"))
        or json.loads((repair_from/"inventory.json").read_text()) != inventory):
      raise ValueError("Repair predecessor identity mismatch or safety stop")
    repair_records = prior["records"]
    if set(repair_records) != {u["unit_id"] for u in inventory["units"]}:
      raise ValueError("Repair predecessor does not conserve units")
    if decode_review is not None:
      from tools.readalong_fast.decode_recovery import validate_review
      quarantined_uid, binding = validate_review(decode_review, repair_from, inventory, repair_records, identity["codeSha256"])
      identity.update(binding)
    selected = []
    for uid, row in repair_records.items():
      if row.get("workflow_status") == "ATTEMPT_RESERVED":
        raise ValueError("Repair predecessor contains an unfinished running attempt")
      if row.get("origin") != "fast-continuation":
        if row != {"origin": "legacy-carry", "legacyRecord": old["records"][uid]}:
          raise ValueError("Carried predecessor evidence changed")
        continue
      inherited, attempts = row.get("inheritedAttempts"), row.get("newAttempts")
      if (type(inherited) is not int or type(attempts) is not int or inherited < 0 or attempts < 0
          or inherited != old["records"][uid]["attempts"] or inherited+attempts > 3):
        raise ValueError("Repair attempt budget is invalid")
      approved = any(row.get("error", "").startswith("ValueError: "+s) for s in
        ("INVALID_ASR_INTERVAL", "Duplicate original DOM IDs:", "Duplicate spine document"))
      eligible = (row.get("workflow_status") == "NOT_RUN" if decode_review is not None else
        row.get("workflow_status") == "PER_UNIT_ERROR" and approved)
      if eligible and inherited+attempts < 3:
        selected.append(uid)
    identity["repairFrom"] = str(repair_from)
    identity["repairPlanSha256"] = file_hash(repair_from/"plan.json")
    identity["repairResultsSha256"] = file_hash(repair_from/"results.json")
    identity["repairInventorySha256"] = file_hash(repair_from/"inventory.json")
  plan_path = output/"plan.json"
  if plan_path.exists():
    plan = json.loads(plan_path.read_text())
    if plan["identity"] != identity:
      raise ValueError("Frozen handoff changed; do not silently reselect or reset attempts")
    return plan, inventory
  if output.exists() and any(output.iterdir()):
    raise ValueError("New continuation directory must be empty")
  output.mkdir(parents=True, exist_ok=True)
  plan = {"schemaVersion": 1, "identity": identity, "selectedUnitIds": selected,
          "carriedUnitIds": list(carried), "scope": "reviewed-decode-stop-unstarted-only" if decode_review is not None else
            "reviewed-three-family-repair" if repair_records is not None else "unfinished-only", "strictCertification": False,
          "granularity": "paragraph-context", "createdAtUnix": time.time()}
  if repair_records is not None:
    records = repair_records
    if quarantined_uid is not None:
      row = records[quarantined_uid]
      row["decodeRecoveryPredecessorRecord"] = dict(row)
      row.update(workflow_status="QUARANTINED_AUDIO", readalongUsability="BLOCKED_INPUT",
        reason="AUDIO_DECODE_REVIEW_REQUIRED", fullAudioProcessed=False,
        decodeEvidencePath=identity["decodeEvidencePath"], published=False)
    plan["retainedUnitIds"] = [uid for uid in records if uid not in selected]
    for uid in selected:
      records[uid]["repairPredecessorRecord"] = dict(records[uid])
      records[uid].update(workflow_status="NOT_RUN", readalongUsability="NOT_RUN",
        retryReason="Reviewed code recovery; historical attempts retained")
  else:
    records = {uid: {"origin": "legacy-carry", "legacyRecord": row} for uid, row in carried.items()}
    for uid in selected:
      records[uid] = {"unit_id": uid, "origin": "fast-continuation", "workflow_status": "NOT_RUN",
                      "inheritedAttempts": old["records"][uid]["attempts"], "newAttempts": 0,
                      "previousWorkflow": old["records"][uid]["workflow_status"]}
  atomic_json(output/"inventory.json", inventory)
  atomic_json(output/"results.json", {"identity": identity, "records": records})
  atomic_json(plan_path, plan)
  return plan, inventory


def _summary(output, plan, records):
  states = Counter()
  for row in records.values():
    if row["origin"] == "legacy-carry":
      states["CARRIED_UNCHANGED"] += 1
    else:
      states[row.get("readalongUsability", row.get("workflow_status", "NOT_RUN"))] += 1
  result = {"totalUnits": len(records), "selectedUnits": len(plan["selectedUnitIds"]),
            "states": dict(states), "published": False, "listeningVerified": False,
            "note": "Carried results are old outcomes, not newly mapped successes"}
  selected = [records[uid] for uid in plan["selectedUnitIds"]]
  retained = [row for uid, row in records.items() if uid not in plan["selectedUnitIds"]]
  def usable(row):
    value = row.get("legacyRecord", row)
    return value.get("readalongUsability", value.get("readalong_usability")) in {"USABLE", "USABLE_WITH_GAPS"}
  result.update(retainedUnits=len(retained),
    selectedStates=dict(Counter(r.get("workflow_status", "NOT_RUN") for r in selected)),
    newCompleteCandidates=sum(r.get("workflow_status") == "COMPLETED" and r.get("fullAudioProcessed") is True for r in selected),
    newlyUsable=sum(usable(r) for r in selected), retainedUsable=sum(usable(r) for r in retained),
    totalUsable=sum(usable(r) for r in records.values()),
    budgetExhausted=sum(r.get("inheritedAttempts", 0)+r.get("newAttempts", 0) >= 3
      if r.get("origin") != "legacy-carry" else r["legacyRecord"].get("attempts", 0) >= 3 for r in records.values()))
  def used_up(row):
    return (row["legacyRecord"].get("attempts", 0) >= 3 if row.get("origin") == "legacy-carry"
      else row.get("inheritedAttempts", 0)+row.get("newAttempts", 0) >= 3)
  result["budgetExhaustedNeedsAction"] = sum(used_up(r) and not usable(r)
    and r.get("legacyRecord", r).get("workflow_status") != "BLOCKED_INPUT" for r in records.values())
  atomic_json(output/"summary.json", result)
  return result


def run(predecessor, output, *, plan_only=False, max_units=None, unit_ids=None, cache_only=False, cache_roots=(), retry_ids=(), retry_reason=None, skip_material_screen=False, repair_from=None, decode_review=None, asr_engine="batch"):
  predecessor, output = Path(predecessor).resolve(strict=True), Path(output).resolve()
  # Acquire predecessor locks before creating a plan or doing expensive work.
  with ExitStack() as stack:
    for name in (".session.lock", ".campaign.lock"):
      stack.enter_context(locked(predecessor/name))
    if repair_from is not None:
      stack.enter_context(locked(Path(repair_from)/".fast.lock"))
    plan, inventory = load_or_plan(predecessor, output, repair_from, decode_review)
    stack.enter_context(locked(output/".fast.lock"))
    data = json.loads((output/"results.json").read_text())
    if data.get("identity") != plan["identity"]:
      raise ValueError("Continuation ledger identity mismatch")
    records = data["records"]
    if set(records) != {u["unit_id"] for u in inventory["units"]}:
      raise ValueError("Continuation ledger unit conservation failed")
    if plan_only:
      return _summary(output, plan, records)
    if (output/"STOP.json").exists():
      raise RuntimeError("Continuation is stopped; preserve evidence and review before resuming")
    input_cache = InputCache(output/"verified-inputs.json")
    roots = [predecessor/"cache", Path.home()/".cache/digital-garden/transcripts"]+list(cache_roots)
    if repair_from is not None:
      roots.insert(0, Path(repair_from)/"cache")
    policy_path = Path(__file__).parent.parent/"readalong/material-exceptions.json"
    policy = json.loads(policy_path.read_text())
    materials = {e["unitId"]: e for e in policy["entries"]}
    model_stats = {str(p): stat_key(p) for p in resolve_model_path().rglob("*") if p.is_file()}
    units = {u["unit_id"]: u for u in inventory["units"]}
    selected = plan["selectedUnitIds"]
    if retry_ids:
      if not retry_reason or not set(retry_ids).issubset(selected):
        raise ValueError("Explicit retries require selected unfinished books and a reason")
      unit_ids = list(set(unit_ids or []) | set(retry_ids))
    if unit_ids:
      if not set(unit_ids).issubset(selected):
        raise ValueError("Requested book was already completed/carried or is not selected")
      selected = [uid for uid in selected if uid in unit_ids]
    processed = 0
    for uid in selected:
      row, unit = records[uid], units[uid]
      if row["origin"] != "fast-continuation":
        raise ValueError("Carried records cannot be regenerated by this entrypoint")
      if row.get("workflow_status") in {"COMPLETED", "BLOCKED_INPUT", "QUARANTINED_AUDIO"}:
        if row["workflow_status"] == "COMPLETED":
          dest = Path(row["candidatePath"])
          current = {str(p.relative_to(dest)): stat_key(p) for p in dest.rglob("*") if p.is_file()}
          if not current or current != row.get("candidateStats"):
            raise RuntimeError("Completed fast candidate changed or disappeared; review instead of silent reuse")
        continue
      if row.get("workflow_status") in {"PER_UNIT_ERROR", "INCOMPLETE_ATTEMPT", "SCREEN_REVIEW"} and uid not in retry_ids:
        continue
      if max_units is not None and processed >= max_units:
        break
      if row.get("workflow_status") == "ATTEMPT_RESERVED":
        row["workflow_status"] = "INCOMPLETE_ATTEMPT"
        row["note"] = "Interrupted fast attempt retained; explicit --retry-unit with reason is required"
        atomic_json(output/"results.json", data)
        continue
      if (type(row.get("newAttempts")) is not int or type(row.get("inheritedAttempts")) is not int
          or not 0 <= row["inheritedAttempts"]+row["newAttempts"] < 3):
        raise ValueError("Attempt budget exhausted or invalid")
      blocker = input_blocker(unit, allow_epub_pairing=True)
      if blocker:
        row.update(workflow_status="BLOCKED_INPUT", readalongUsability="BLOCKED_INPUT", reason=blocker)
        atomic_json(output/"results.json", data)
        continue
      attempt = row["inheritedAttempts"]+row["newAttempts"]+1
      dest = output/"candidates"/sanitize_slug(uid)/f"attempt-{attempt:02d}"
      if dest.exists():
        raise ValueError("Unregistered candidate exists; do not overwrite it")
      if row.get("newAttempts", 0):
        row.setdefault("attemptHistory", []).append({k: row.get(k) for k in
          ("workflow_status", "newAttempts", "candidatePath", "error", "startedAtUnix", "finishedAtUnix")})
        row["retryReason"] = retry_reason or row.get("retryReason")
      for key in ("error", "reportPath", "metrics", "timings", "fullAudioProcessed", "speechCacheStats", "candidateStats"):
        row.pop(key, None)
      row.update(workflow_status="ATTEMPT_RESERVED", newAttempts=row["newAttempts"]+1,
                 candidatePath=str(dest), startedAtUnix=time.time())
      atomic_json(output/"results.json", data)
      print(f"[{processed+1}] Mapping {uid}", flush=True)
      local_roots = roots+list((predecessor/"candidates"/sanitize_slug(uid)).glob("*/work"))
      cache = SpeechCache(output/"cache", local_roots, plan["identity"]["modelSha256"], cache_only,
        asr_engine=asr_engine)
      try:
        report = generate(unit, dest, cache, input_cache, materials.get(uid), screen=not skip_material_screen)
        row.update(workflow_status=report.get("stage", "COMPLETED"), readalongUsability=report["readalongUsability"],
                   reportPath=str(dest/"practical-audit.json"), timings=report["timings"],
                   speechCacheStats=report["speechCacheStats"], metrics=report["metrics"],
                   fullAudioProcessed=report["fullAudioProcessed"])
        row["candidateStats"] = {str(p.relative_to(dest)): stat_key(p) for p in dest.rglob("*") if p.is_file()}
      except AudioDecodeIssue as exc:
        report = {"workflow_status": "QUARANTINED_AUDIO", "readalongUsability": "BLOCKED_INPUT",
          "reason": "AUDIO_DECODE_REVIEW_REQUIRED", "fullAudioProcessed": False, "published": False,
          "evidencePath": exc.evidence_path, "decodeIssue": exc.report,
          "note": "No complete mapping was produced; the suspect PCM was not transcribed. Other books may continue."}
        atomic_json(dest/"decode-quarantine.json", report)
        row.update({k: v for k, v in report.items() if k != "decodeIssue"})
        row["reportPath"] = str(dest/"decode-quarantine.json")
      except Exception as exc:
        row.update(workflow_status="PER_UNIT_ERROR", readalongUsability="SCRIPT_ERROR", error=f"{type(exc).__name__}: {exc}")
        missing_source = (isinstance(exc, FileNotFoundError) and exc.filename is not None
          and (str(exc.filename) == "ffmpeg" or Path(exc.filename).resolve().is_relative_to(Path(unit["book_dir"]).resolve())))
        critical = (any(t in str(exc) for t in ("SOURCE_CHANGED", "ASR_RUNTIME_UNAVAILABLE", "path traversal", "Path escapes", "Unsafe EPUB"))
                    or any(t in str(exc).lower() for t in ("out of memory", "no metal device", "bad_alloc", "device lost"))
                    or missing_source
                    or isinstance(exc, (DecodeEnvironmentError, MemoryError))
                    or isinstance(exc, OSError) and exc.errno in {errno.ENOSPC, errno.EIO, errno.EROFS, errno.EACCES, errno.ENOMEM})
        if critical:
          atomic_json(output/"STOP.json", {"unit_id": uid, "error": str(exc), "sourceUnchanged": "not_assumed"})
          atomic_json(output/"results.json", data)
          _summary(output, plan, records)
          raise
      finally:
        row["finishedAtUnix"] = time.time()
        atomic_json(output/"results.json", data)
      if (fast_identity() != plan["identity"]["codeSha256"]
          or file_hash(predecessor/"results.json") != plan["identity"]["predecessorResultsSha256"]
          or file_hash(predecessor/"inventory.json") != plan["identity"]["inventorySha256"]
          or repair_from is not None and (file_hash(Path(repair_from)/"results.json") != plan["identity"]["repairResultsSha256"]
            or file_hash(Path(repair_from)/"plan.json") != plan["identity"]["repairPlanSha256"]
            or file_hash(Path(repair_from)/"inventory.json") != plan["identity"]["repairInventorySha256"])
          or decode_review is not None and (file_hash(decode_review) != plan["identity"]["decodeReviewSha256"]
            or file_hash(Path(repair_from)/"STOP.json") != plan["identity"]["repairStopSha256"]
            or file_hash(plan["identity"]["decodeEvidencePath"]) != plan["identity"]["decodeEvidenceSha256"]
            or file_hash(plan["identity"]["decodeDiagnosticPath"]) != plan["identity"]["decodeDiagnosticSha256"])
          or model_stats != {str(p): stat_key(p) for p in resolve_model_path().rglob("*") if p.is_file()}):
        atomic_json(output/"STOP.json", {"error": "Code, predecessor or model changed"})
        raise RuntimeError("Frozen execution identity changed")
      processed += 1
      _summary(output, plan, records)
    return _summary(output, plan, records)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--from-run", type=Path, required=True)
  parser.add_argument("--output", type=Path, required=True)
  parser.add_argument("--repair-from", type=Path, help="Explicit immutable fast-run migration; only the three reviewed failure families")
  parser.add_argument("--decode-recovery-review", type=Path, help="Bound approval to quarantine a legacy decode stop and resume unstarted books only")
  parser.add_argument("--plan-only", action="store_true")
  parser.add_argument("--max-units", type=int)
  parser.add_argument("--unit", action="append")
  parser.add_argument("--cache-only", action="store_true")
  parser.add_argument("--cache-read-root", type=Path, action="append", default=[])
  parser.add_argument("--retry-unit", action="append", default=[])
  parser.add_argument("--retry-reason")
  parser.add_argument("--skip-material-screen", action="store_true", help="Explicit operator decision only; no automatic bypass")
  parser.add_argument("--asr-engine", choices=("serial", "batch", "words"), default="batch",
    help="New-ASR engine for cache misses; batch is mlx-batch-silence-v1 and is the default")
  args = parser.parse_args()
  if args.max_units is not None and args.max_units <= 0:
    parser.error("--max-units must be positive")
  if args.retry_unit and not args.retry_reason:
    parser.error("--retry-unit requires --retry-reason; no blind retry loops")
  result = run(args.from_run, args.output, plan_only=args.plan_only, max_units=args.max_units,
               unit_ids=args.unit, cache_only=args.cache_only, cache_roots=args.cache_read_root,
               retry_ids=args.retry_unit, retry_reason=args.retry_reason, skip_material_screen=args.skip_material_screen,
               repair_from=args.repair_from, decode_review=args.decode_recovery_review,
               asr_engine=args.asr_engine)
  print(json.dumps(result, ensure_ascii=False, indent=2))
  if args.plan_only:
    return 0
  return 2 if any(k not in {"CARRIED_UNCHANGED", "USABLE", "USABLE_WITH_GAPS", "BLOCKED_INPUT"} and v for k, v in result["states"].items()) else 0


if __name__ == "__main__":
  sys.exit(main())
