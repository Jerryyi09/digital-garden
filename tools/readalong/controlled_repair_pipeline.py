"""Bounded candidate generation, never implicit publication."""
import hashlib
import json
import os
import uuid
from pathlib import Path

from tools.readalong.input_inventory import build_book_inventory
from tools.readalong.controlled_publisher import create_staging_revision

REPAIR_STATE_FILE = "readalong_repair_state.json"
MAX_RETRY_BUDGET = 2


def load_repair_state(book_dir):
  file = Path(book_dir) / REPAIR_STATE_FILE
  if file.exists():
    try:
      value = json.loads(file.read_text())
      if not isinstance(value, dict) or type(value.get("attempts")) is not int:
        raise ValueError("Bad repair state")
      return value
    except (ValueError, OSError):
      # Corruption must not silently reset the budget.
      return {"status": "NEEDS_REVIEW", "attempts": MAX_RETRY_BUDGET,
              "max_retries": MAX_RETRY_BUDGET, "failures": ["repair_state_corrupt"]}
  return {"book_id": Path(book_dir).name, "status": "INITIAL", "attempts": 0,
          "max_retries": MAX_RETRY_BUDGET, "failures": []}


def save_repair_state(book_dir, state):
  file = Path(book_dir) / REPAIR_STATE_FILE
  temp = file.with_name("." + uuid.uuid4().hex)
  temp.write_text(json.dumps(state, indent=2))
  os.replace(temp, file)


def attempt_book_repair_cycle(book_dir, force=False):
  book = Path(book_dir)
  state = load_repair_state(book)
  # A force request may re-inspect input, but cannot remove the retry budget.
  if state["attempts"] >= MAX_RETRY_BUDGET:
    state["status"] = "RETRY_BUDGET_EXHAUSTED"
    save_repair_state(book, state)
    return {"action": "BLOCKED", "state": state}
  if state["status"] in {"PERMANENT_FAILURE", "UNSUPPORTED", "NEEDS_REVIEW"} and not force:
    return {"action": "SKIPPED", "state": state}
  inventory = build_book_inventory(book)
  if inventory["status"] != "VALID":
    state["status"] = "PERMANENT_FAILURE" if inventory["status"] == "INVALID" else "NEEDS_REVIEW"
    save_repair_state(book, state)
    return {"action": "HALTED", "state": state}
  signature = hashlib.sha256(json.dumps({
    "inventory": inventory,
    "algorithm": hashlib.sha256((Path(__file__).parent / "universal_aligner.py").read_bytes()).hexdigest(),
    "model": os.environ.get("READALONG_MODEL_PATH", "default"),
  }, sort_keys=True).encode()).hexdigest()
  if signature == state.get("signature") and not force:
    state["status"] = "NEEDS_REVIEW"
    save_repair_state(book, state)
    return {"action": "NO_IMPROVEMENT", "state": state}
  state.update(signature=signature, attempts=state["attempts"]+1)
  # Persist the budget before work, so a killed worker cannot reset it.
  save_repair_state(book, state)
  stage = create_staging_revision(book)
  try:
    from tools.readalong.universal_aligner import align_single_book_universal
    result = align_single_book_universal(book, stage)
    state["status"] = result["status"]
  except Exception as exc:
    state["status"] = "NEEDS_REVIEW"
    state["failures"].append(str(exc))
  state["staging_dir"] = str(stage)
  save_repair_state(book, state)
  return {"action": "CANDIDATE_ONLY", "state": state}
