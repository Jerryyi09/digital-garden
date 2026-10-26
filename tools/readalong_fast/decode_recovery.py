"""Validate an explicit review of a legacy decode-only batch safety stop."""
import json
from pathlib import Path

from tools.readalong_fast.pipeline import file_hash


def validate_review(path, previous_run, inventory, records, current_code):
  """Authorize unstarted work only, never deletion or general STOP bypass."""
  path, previous_run = Path(path).resolve(strict=True), Path(previous_run).resolve(strict=True)
  review = json.loads(path.read_text())
  expected = {"schemaVersion": 1, "decision": "RESUME_UNSTARTED_QUARANTINE_AUDIO",
    "previousRun": str(previous_run), "codeSha256": current_code,
    "planSha256": file_hash(previous_run/"plan.json"),
    "resultsSha256": file_hash(previous_run/"results.json"),
    "inventorySha256": file_hash(previous_run/"inventory.json"),
    "stopSha256": file_hash(previous_run/"STOP.json")}
  if any(review.get(k) != v for k, v in expected.items()):
    raise ValueError("Decode recovery review does not bind the current code and stopped snapshot")
  stop = json.loads((previous_run/"STOP.json").read_text())
  uid = review.get("quarantinedUnitId")
  row = records.get(uid, {})
  if (stop.get("unit_id") != uid or not stop.get("error", "").startswith("AUDIO_DECODE_INCOMPLETE:")
      or row.get("workflow_status") != "PER_UNIT_ERROR"
      or not row.get("error", "").startswith("RuntimeError: AUDIO_DECODE_INCOMPLETE:")):
    raise ValueError("Only the reviewed legacy decode shortfall stop may be migrated")
  evidence_path = Path(review["evidencePath"]).resolve(strict=True)
  if file_hash(evidence_path) != review.get("evidenceSha256"):
    raise ValueError("Decode verification evidence changed")
  proof = json.loads(evidence_path.read_text())
  unit = next((u for u in inventory["units"] if u["unit_id"] == uid), None)
  if (not unit or proof.get("unitId") != uid or proof.get("sourceHashVerified") is not True
      or proof.get("sourceUnchanged") is not True or proof.get("activeUnchanged") is not True
      or proof.get("outcome") != "QUARANTINED_AUDIO" or proof.get("asrInvoked") is not False
      or proof.get("codeSha256") != current_code
      or proof.get("sourceSha256") not in {r["sha256"] for r in unit["audio_tracks"]}):
    raise ValueError("Decode recovery lacks bound read-only physical verification")
  diagnostic = Path(proof["decodeEvidencePath"]).resolve(strict=True)
  if file_hash(diagnostic) != proof.get("decodeEvidenceSha256"):
    raise ValueError("Physical decoder diagnostic changed")
  raw = json.loads(diagnostic.read_text())
  if (raw.get("status") != "QUARANTINE" or raw.get("parameters", {}).get("sourceSha256") != proof["sourceSha256"]
      or raw.get("reason") not in {"DECODER_REPORTED_ERRORS", "PCM_SHORTFALL", "EMPTY_OUTPUT"}
      or raw.get("requestedStart") != proof.get("requestedStart") or raw.get("requestedEnd") != proof.get("requestedEnd")):
    raise ValueError("Decoder evidence is not the reviewed physical interval")
  return uid, {"decodeReviewPath": str(path), "decodeReviewSha256": file_hash(path),
    "repairStopSha256": expected["stopSha256"], "decodeEvidencePath": str(evidence_path),
    "decodeEvidenceSha256": review["evidenceSha256"], "decodeDiagnosticPath": str(diagnostic),
    "decodeDiagnosticSha256": proof["decodeEvidenceSha256"]}
