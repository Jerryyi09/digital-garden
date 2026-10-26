"""Stratified block sampling to estimate a book's unmapped-speech ratio before a full run.

The sample unit is a real cache block, same geometry and engine as the full run, so
sampled blocks are written to the normal cache and are reused when the book is
processed for real. A full run is never skipped on the strength of this estimate:
the timeline is the deliverable, not a byproduct, so passing books still get mapped.

A verdict may only be SAMPLE_PASS or SAMPLE_MISMATCH when the evidence is decisive.
Anything ambiguous is reported as a borderline/moderate verdict that proceeds to a
full run, because a wrong SAMPLE_MISMATCH would silently drop a usable book.
"""
import hashlib

# Calibrated 2026-10-25 on real edition mismatches, zero new ASR. Source:
# private/readalong-library-reviews/asr-batch-screening-closeout-20261025/.
#
# The earlier MISMATCH rule ("every block <= 2% located") was calibrated only on
# constructed cross-book pairs, where the located ratio is exactly 0. A real
# same-book-different-edition mismatch always matches a few stray fragments, so
# its located ratio is 0.05-0.10 and the rule rejected all four real cases
# (Peter Pan, Tess, The Scarlet Letter, Great Expectations). The threshold must
# be calibrated on real edition mismatches, not constructed ones.
#
# MISMATCH_LOCATED_UPPER_CEILING = 0.20 sits between the two populations:
#   real mismatches: 0.016-0.072 overall located ratio -> 0.20 is 2.8x the max;
#   lowest non-mismatch (Resurrection): 0.40 -> 0.20 is half of it.
# The bootstrap interval's upper bound is used rather than the point estimate so
# that one lucky block widens the band instead of vetoing the whole verdict.
SAMPLE_BLOCKS = 6
MIN_SAMPLE_BLOCKS = 3
# The floor is on the sample's TOTAL evidence, not on each block: a book of many
# short tracks (Great Expectations: 179 tracks of 28-120s) can never reach 200
# tokens per track, yet six whole tracks still carry ~860 tokens of real speech.
# Judging per block read that as "not enough evidence" and kept a fully unmapped
# book on the full-run path. 1200 = 6 blocks x the old per-block floor, so the
# total evidence a decisive verdict needs is unchanged.
MIN_SAMPLE_TOKENS = 1200
# Appending strata is how a short-track book reaches the total; 12 caps the cost.
MAX_SAMPLE_BLOCKS = 12
# A block with almost no speech is silence or music, not evidence, so it does not
# count toward the block count.
MIN_BLOCK_TOKENS = 50
# Below this the stratum is a head/tail remnant of a longer track, not a sample.
MIN_MEASURE_SECONDS = 120.0
# Overall located ratio's bootstrap upper bound must fall below this.
MISMATCH_LOCATED_UPPER_CEILING = 0.20
# One block this well located means part of the book does match (an anthology),
# so the book must not be excluded automatically.
MISMATCH_BLOCK_VETO = 0.50
PASS_UPPER_CEILING = 0.05
BORDERLINE_LOW = 0.02
BORDERLINE_HIGH = 0.08
BOOTSTRAP_ROUNDS = 2000
BOOTSTRAP_SEED = 20261024
EDGE_HEAD = 0.16
EDGE_TAIL = 0.12

VERDICT_PASS = "SAMPLE_PASS"
VERDICT_MISMATCH = "SAMPLE_MISMATCH"
VERDICT_MODERATE = "SAMPLE_MODERATE"
VERDICT_EDITION_ZONE = "SAMPLE_EDITION_ZONE"
VERDICT_BORDERLINE = "SAMPLE_BORDERLINE"


def block_plan(duration, block_seconds=1800.0):
  """Same geometry the full run uses, so a sampled block is a cache hit later."""
  blocks, position = [], 0.0
  while position < duration:
    length = min(block_seconds, duration-position)
    blocks.append((position, length))
    position += length
  return blocks


def stratified_blocks(tracks, count=SAMPLE_BLOCKS, block_seconds=1800.0):
  """One block per stratum, spread across the book and away from apparatus zones.

  Each track's head 16% and tail 12% match the edition front/back ranges the full
  run excludes, so samples are not spent on credits or publisher interviews.
  The unit stays on the full run's block grid: an aligned block is a cache hit
  later, whereas an arbitrary offset would force new ASR for the same audio.

  A book of many short tracks has almost no 1800s grid blocks, so the grid alone
  would starve it of samples (179 tracks yielded 2). Those books are sampled by
  whole track instead, which is still a cache hit: a short track is one block."""
  total = sum(t["duration"] for t in tracks)
  if total <= 0:
    return []
  usable = []
  for track in tracks:
    head, tail = track["duration"]*EDGE_HEAD, track["duration"]*EDGE_TAIL
    for start, length in block_plan(track["duration"], block_seconds):
      lo, hi = max(start, head), min(start+length, track["duration"]-tail)
      # A stratum too short to hold a few hundred tokens cannot carry a verdict,
      # and its ratio would swing on a handful of words.
      if hi-lo >= MIN_MEASURE_SECONDS:
        usable.append({"audioSourceId": track["audioSourceId"], "start": start, "duration": length,
          "measureStart": lo, "measureDuration": hi-lo})
  if not usable:
    usable = short_track_samples(tracks)
  if len(usable) <= count:
    return usable
  chosen, seen = [], set()
  for i in range(count):
    target = total*(i+0.5)/count
    pick = min(usable, key=lambda b: abs(_offset(tracks, b)-target))
    key = (pick["audioSourceId"], round(pick["start"], 3))
    if key not in seen:
      seen.add(key)
      chosen.append(pick)
  return sorted(chosen, key=lambda b: (b["audioSourceId"], b["start"]))


def short_track_samples(tracks, count=SAMPLE_BLOCKS):
  """One whole short track per stratum, for books the 1800s grid cannot serve.

  Measuring a whole track keeps the sample self-contained, so the head/tail trim
  and MIN_MEASURE_SECONDS are both skipped: on a 55s track they would leave
  nothing to measure, and a book of 179 such tracks would fall back to the two
  long ones and never reach SAMPLE_BLOCKS. Track count, not track length, is what
  bounds the sample here."""
  usable = [t for t in tracks if t["duration"] > 0]
  if not usable:
    return []
  if len(usable) <= count:
    return [{"audioSourceId": t["audioSourceId"], "start": 0.0, "duration": t["duration"],
             "measureStart": 0.0, "measureDuration": t["duration"]} for t in usable]
  total = sum(t["duration"] for t in usable)
  chosen, seen = [], set()
  for i in range(count):
    target = total*(i+0.5)/count
    offset, pick = 0.0, usable[-1]
    for track in usable:
      if offset+track["duration"]/2 >= target:
        pick = track
        break
      offset += track["duration"]
    if pick["audioSourceId"] not in seen:
      seen.add(pick["audioSourceId"])
      chosen.append({"audioSourceId": pick["audioSourceId"], "start": 0.0,
        "duration": pick["duration"], "measureStart": 0.0, "measureDuration": pick["duration"]})
  return chosen


def extend_strata(tracks, chosen, count=MAX_SAMPLE_BLOCKS):
  """More whole-track strata, for a short-track book whose first sample was too thin.

  The total-evidence floor can fail on a book of many short tracks even when the
  verdict is unambiguous. Appending neighbouring whole tracks is the only way to
  raise the total without measuring a longer window than a track has. Tracks
  already sampled are skipped, so this strictly adds evidence."""
  if not chosen:
    return []
  usable = [t for t in tracks if t["duration"] > 0]
  seen = {b["audioSourceId"] for b in chosen}
  extra = []
  for track in usable:
    if len(chosen)+len(extra) >= count:
      break
    if track["audioSourceId"] in seen:
      continue
    seen.add(track["audioSourceId"])
    extra.append({"audioSourceId": track["audioSourceId"], "start": 0.0,
      "duration": track["duration"], "measureStart": 0.0, "measureDuration": track["duration"]})
  return extra


def _offset(tracks, block):
  total = 0.0
  for track in tracks:
    if track["audioSourceId"] == block["audioSourceId"]:
      return total+block["start"]
    total += track["duration"]
  return total


def bootstrap_interval(samples, rounds=BOOTSTRAP_ROUNDS, seed=BOOTSTRAP_SEED):
  """Deterministic interval over blocks: same inputs always give the same band."""
  if not samples:
    return None, None
  if len(samples) == 1:
    return 0.0, 1.0
  observed = [s["observedSeconds"] for s in samples]
  missing = [s["missingSeconds"] for s in samples]
  ratios = []
  for i in range(rounds):
    # A hash-driven index keeps this reproducible without a global RNG stream.
    digest = hashlib.sha256(f"{seed}:{i}".encode()).digest()
    picks = [digest[j % len(digest)] % len(samples) for j in range(len(samples))]
    sp = sum(observed[j] for j in picks)
    un = sum(missing[j] for j in picks)
    ratios.append(un/sp if sp > 0 else 0.0)
  ratios.sort()
  lo = ratios[int(0.025*len(ratios))]
  hi = ratios[min(len(ratios)-1, int(0.975*len(ratios)))]
  return lo, hi


def classify(samples, total_blocks=None, tokens_ok=None, edge_zone_only=False):
  """Verdict for the sampled evidence. Defaults to a verdict that runs the book.

  `tokens_ok` is the caller's aggregate evidence check; when omitted it is derived
  from the samples, so a caller that already filtered silent blocks gets the same
  answer either way."""
  if len(samples) < MIN_SAMPLE_BLOCKS:
    return VERDICT_BORDERLINE, {"reason": "TOO_FEW_SAMPLE_BLOCKS", "blocks": len(samples)}
  if tokens_ok is None:
    tokens_ok = sum(s.get("tokens", 0) for s in samples) >= MIN_SAMPLE_TOKENS
  if not tokens_ok:
    return VERDICT_BORDERLINE, {"reason": "INSUFFICIENT_ASR_TOKENS",
      "tokens": sum(s.get("tokens", 0) for s in samples)}
  observed = sum(s["observedSeconds"] for s in samples)
  missing = sum(s["missingSeconds"] for s in samples)
  if observed <= 0:
    return VERDICT_BORDERLINE, {"reason": "NO_OBSERVED_SPEECH"}
  located_ratio = 1-missing/observed
  lo, hi = bootstrap_interval(samples)
  per_block = [1-s["missingSeconds"]/s["observedSeconds"] for s in samples if s["observedSeconds"] > 0]
  max_block = max(per_block) if per_block else None
  detail = {"locatedRatio": located_ratio, "intervalLow": lo, "intervalHigh": hi,
    "blocks": len(samples), "observedSeconds": observed, "missingSeconds": missing,
    "maxBlockLocatedRatio": max_block, "locatedUpper": None if lo is None else 1-lo}
  if edge_zone_only:
    return VERDICT_EDITION_ZONE, detail
  # Mismatch, symmetric with PASS: the bootstrap interval over the located ratio,
  # plus a per-block veto. The interval upper bound is the located upper bound,
  # which is 1 - (unmapped interval lower bound). The veto only applies once the
  # interval test has already passed: on a book whose blocks are all located it
  # carries no information, and firing it there would block every PASS.
  if len(samples) >= SAMPLE_BLOCKS and lo is not None:
    located_upper = detail["locatedUpper"]
    if located_upper < MISMATCH_LOCATED_UPPER_CEILING:
      if max_block is not None and max_block >= MISMATCH_BLOCK_VETO:
        return VERDICT_BORDERLINE, {**detail, "reason": "A_BLOCK_MATCHES"}
      return VERDICT_MISMATCH, detail
  if hi is not None and hi < PASS_UPPER_CEILING and lo is not None and lo < BORDERLINE_LOW:
    return VERDICT_PASS, detail
  if per_block and max(per_block) > 0.9 and min(per_block) < 0.1:
    return VERDICT_BORDERLINE, {**detail, "reason": "BIMODAL_BLOCKS"}
  if lo is not None and hi is not None and lo < BORDERLINE_HIGH and hi >= PASS_UPPER_CEILING:
    return VERDICT_MODERATE, detail
  return VERDICT_BORDERLINE, detail


def verdict_runs_full_book(verdict):
  """Only a confirmed mismatch skips the full run; everything else proceeds."""
  return verdict != VERDICT_MISMATCH
