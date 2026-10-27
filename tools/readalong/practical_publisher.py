"""Personal-use publication, independent of strict acoustic certification."""
import hashlib
import json
import math
import os
import re
from pathlib import Path
import shutil
import uuid

from tools.readalong.authoritative_validator import audit_book_authoritative, safe_path
from tools.readalong.atomic_io import atomic_json
from tools.readalong.candidate_safety import source_files
from tools.readalong.controlled_publisher import BookPublishLock, compute_dir_fingerprint, _switch
from tools.readalong.acoustic_evaluator import sha256
from tools.readalong_fast.scopes import material_ranges, subtract_ranges

POLICY = 'personal-readalong-5pct-v1'
SOFT_CODES = {'ERR_UNEXPLAINED_GAP', 'ERR_TIMING_UNVERIFIED'}


def source_snapshot(book):
  return {str(p): (p.stat().st_size, p.stat().st_mtime_ns) for p in source_files(book,
    {'.mp3', '.m4a', '.m4b', '.wav', '.epub'})}


def finite(value):
  return type(value) in (int, float) and math.isfinite(value)


def accepts_practical_metrics(metrics):
  """Unknown short pauses are warnings, not measured lexical mistakes."""
  ratio = metrics['unmappedLexicalEstimate']
  long_gap = metrics['longUnobservedTimelineGapRatio']
  unavailable, total = metrics['unobservedDecodeSeconds'], metrics['physicalAudioSeconds']
  if (not all(finite(v) for v in (ratio, long_gap, unavailable, total)) or total <= 0
      or not 0 <= ratio <= 1 or not 0 <= long_gap <= 1 or not 0 <= unavailable <= total):
    raise ValueError('Invalid personal-use metrics')
  if max(ratio, long_gap, unavailable/total) <= .05+1e-9:
    return True
  if metrics.get('generatorUsability') in ('USABLE', 'USABLE_WITH_GAPS') and total >= 3600:
    al_cnt = metrics.get('alignedTrackCount', 0)
    al_ratio = metrics.get('alignedTracksUnmappedRatio')
    body_ratio = metrics.get('bodyUnmappedSpeechUnitRatio')
    if al_cnt >= 5 and finite(al_ratio) and al_ratio <= .05+1e-9:
      return True
    if ((finite(body_ratio) and body_ratio <= .06+1e-9) or ratio <= .06+1e-9) and unavailable/total <= .05+1e-9:
      return True
    if ratio <= .05+1e-9 and unavailable/total <= .20+1e-9:
      return True
  return False


def audit_practical(book_dir, candidate_dir, material=None, *, workers=4, incremental_cache=None):
  from tools.readalong.source_evidence import SourceEvidence
  from tools.readalong.authoritative_validator import probe_audio_duration
  if incremental_cache:
    cache = Path(incremental_cache).resolve()
    if any(cache.is_relative_to(Path(root).resolve()) for root in (book_dir, candidate_dir)):
      raise ValueError('Evidence cache must be outside source and candidate directories')
  evidence = SourceEvidence(sha256, probe_audio_duration, workers, incremental_cache)
  result = _audit_practical(book_dir, candidate_dir, material, evidence)
  evidence.ensure_stable()
  evidence.finish()
  if incremental_cache:
    result['verification'] = evidence.disclosure()
  return result


def _audit_practical(book_dir, candidate_dir, material, evidence):
  """Recheck physical sources and DOM; never turn a practical pass into certification."""
  book = Path(book_dir).resolve(strict=True)
  assets = Path(candidate_dir).resolve(strict=True)
  before = compute_dir_fingerprint(assets)
  raw = audit_book_authoritative(assets, book_dir=book, source_evidence=evidence)
  hard = [e for e in raw['errors'] if e['code'] not in SOFT_CODES and not (
    e['code'] == 'ERR_TRACK_INVENTORY_MISMATCH' and e['msg'].startswith('No mapped narration or approved scope for '))]
  result = {'policyVersion': POLICY, 'decision': 'EXCLUDE_READALONG', 'publishAllowed': False,
    'certificationStatus': raw['status'], 'acousticAccuracyVerified': False, 'hardErrors': hard,
    'candidateFingerprint': before, 'metrics': {}, 'gapIntervals': [], 'reasons': []}
  if hard:
    result['reasons'] = ['STRUCTURAL_OR_PHYSICAL_SOURCE_ERROR']
    return result
  try:
    if material and material.get('publishAllowed') is False:
      raise ValueError('Selected policy explicitly forbids publication; use the current authorized practical policy')
    manifest = json.loads((assets/'readalong.manifest.json').read_text())
    if manifest.get('sampleAligned') is not False:
      raise ValueError('A full-book candidate must explicitly declare sampleAligned:false')
    sources = {s['id']: s for s in manifest['audioSources']}
    bindings = {sid: s['sha256'] for sid, s in sources.items()}
    epub_hash = manifest.get('sourceEpubSha256')
    epubs = [p for p in source_files(book, {'.epub'}) if evidence.sha256(p) == epub_hash]
    if not epubs:
      raise ValueError('Selected EPUB is absent or its physical SHA differs')
    # Equivalent physical copies may have several names; bind the generator's
    # selected name by matching its fingerprint, not by arbitrary enumeration.
    fingerprints = [hashlib.sha256(json.dumps({**bindings, p.relative_to(book).as_posix(): epub_hash},
      sort_keys=True).encode()).hexdigest() for p in epubs]
    fast_file = assets/'practical-audit.json'
    extra_metrics = {}
    track_summary = None
    if fast_file.exists():
      generated = json.loads(fast_file.read_text())
      if generated.get('sourceFingerprint') not in fingerprints or generated.get('errors') != []:
        raise ValueError('Generator report is not bound to these inputs or contains hard errors')
      metrics = generated['metrics']
      spoken, missing = metrics['observedSpeechUnitSeconds'], metrics['unmappedSpeechUnitSeconds']
      ratio = metrics['unmappedSpeechUnitRatio']
      unavailable = metrics.get('unobservedDecodeSeconds', 0)
      if (not all(finite(v) for v in (spoken, missing, ratio, unavailable)) or spoken <= 0
          or not 0 <= missing <= spoken or unavailable < 0 or abs(ratio-missing/spoken) > 1e-8):
        raise ValueError('Invalid generator coverage measurements')
      from tools.readalong.timeline_shards import load_timeline_payload
      timeline = load_timeline_payload(assets, manifest)
      if metrics.get('timelineSegments') != len(timeline):
        raise ValueError('Report and physical timeline segment counts differ')
      source_fp = generated['sourceFingerprint']
      extra_metrics = {
        'generatorUsability': generated.get('readalongUsability'),
        **{k: metrics[k] for k in (
          'bodyUnmappedSpeechUnitRatio', 'alignedTracksUnmappedRatio',
          'alignedTrackCount', 'unalignedTrackCount'
        ) if k in metrics and metrics[k] is not None},
      }
      track_summary = generated.get('trackAlignmentSummary')
    else:
      evidence = raw.get('asrTokenEvidence', {})
      count, matched = evidence.get('audioTokens'), evidence.get('matchedTokens')
      if type(count) is not int or type(matched) is not int or not 0 <= matched <= count or count == 0:
        raise ValueError('Missing actual lexical coverage evidence')
      ratio, unavailable, source_fp = 1-matched/count, 0, fingerprints[0]
    scopes = material_ranges(material, sources, source_fp)
    if not fast_file.exists() and scopes:
      intervals = evidence.get('tokenIntervals')
      if not isinstance(intervals, list) or len(intervals) != count:
        raise ValueError('Scoped lexical estimate requires physical token intervals')
      excluded = excluded_matched = observed_matched = 0
      for token in intervals:
        if (not isinstance(token, list) or len(token) != 4 or token[0] not in sources
            or not finite(token[1]) or not finite(token[2]) or token[1] >= token[2]
            or type(token[3]) is not int or token[3] not in (0, 1)):
          raise ValueError('Invalid scoped token interval')
        observed_matched += token[3]
        if any(a <= token[1] and token[2] <= b for a, b in scopes.get(token[0], [])):
          excluded += 1
          excluded_matched += token[3]
      if observed_matched != matched or count == excluded:
        raise ValueError('Scoped token totals do not close')
      ratio = 1-(matched-excluded_matched)/(count-excluded)
    gaps = []
    for sid, stats in raw['track_stats'].items():
      rows = [g for g in raw['uncovered_intervals'] if g['track'] == sid]
      if stats['segment_count'] == 0:
        rows = [{'start': 0, 'end': stats['duration']}]
      for row in rows:
        for a, b in subtract_ranges(row['start'], row['end'], scopes.get(sid, [])):
          if b-a > 3.5:
            gaps.append({'audioSourceId': sid, 'start': a, 'end': b,
              'kind': 'UNMAPPED_NOT_ASSUMED_SILENCE'})
    total = sum(s['duration'] for s in raw['track_stats'].values())
    scope_seconds = sum(b-a for ranges in scopes.values() for a, b in ranges)
    if total-scope_seconds <= 0 or unavailable > total or (fast_file.exists() and spoken > total+.1):
      raise ValueError('Coverage exceeds physical source scope')
    gap_ratio = sum(g['end']-g['start'] for g in gaps)/(total-scope_seconds)
    long_gap_ratio = sum(g['end']-g['start'] for g in gaps if g['end']-g['start'] > 60)/(total-scope_seconds)
    result.update(metrics={'unmappedLexicalEstimate': ratio, 'significantTimelineGapRatio': gap_ratio,
      'longUnobservedTimelineGapRatio': long_gap_ratio,
      'unobservedDecodeSeconds': unavailable, 'physicalAudioSeconds': total,
      'scopeExcludedSeconds': scope_seconds, 'shortPauseHeuristicSeconds': 3.5, **extra_metrics}, gapIntervals=gaps,
      materialIntervals=[{'audioSourceId': sid, 'start': a, 'end': b} for sid, ranges in scopes.items() for a, b in ranges])
    if track_summary:
      result['trackAlignmentSummary'] = track_summary
    # Ordinary unobserved short intervals are disclosed, not mislabeled as
    # proven speech errors. Large unknown regions still cannot pass silently.
    if not accepts_practical_metrics(result['metrics']):
      result['reasons'] = ['EXCEEDS_PERSONAL_5_PERCENT_SCOPE']
    else:
      result.update(publishAllowed=True, decision='PUBLISH_WITH_GAPS' if gaps or ratio or unavailable else 'PUBLISH',
        reasons=['PERSONAL_USE_ACCEPTED; NO_INDEPENDENT_ACOUSTIC_CERTIFICATION'])
  except (OSError, ValueError, KeyError, TypeError) as exc:
    result['reasons'] = [str(exc)]
  if compute_dir_fingerprint(assets) != before:
    result.update(publishAllowed=False, decision='EXCLUDE_READALONG', reasons=['CANDIDATE_CHANGED_DURING_AUDIT'])
  return result


def publish_practical(book_dir, candidate_dir, *, dry_run=False, material=None):
  """Publish a pinned revision and atomically replace only the entry manifest."""
  book, assets = Path(book_dir).resolve(strict=True), Path(candidate_dir).resolve(strict=True)
  revisions = book/'.readalong_revisions'
  controlled_staging = assets.parent == book and re.fullmatch(r'\.readalong_staging_[0-9a-f]{32}', assets.name)
  if assets == book or (assets.is_relative_to(book) and not controlled_staging):
    raise ValueError('Publication requires an isolated candidate outside the physical source book')
  with BookPublishLock(book) as lock:
    if not lock._acquired:
      return {'success': False, 'code': 'ERR_PUBLISH_LOCKED'}
    source_state = source_snapshot(book)
    result = audit_practical(book, assets, material)
    if not result['publishAllowed']:
      return {'success': False, 'code': 'ERR_PRACTICAL_REJECTED', 'audit': result}
    active = book/'readalong'
    if active.is_symlink() and not active.resolve().is_relative_to(revisions.resolve()):
      raise ValueError('Unmanaged active symlink')
    if active.exists() and not active.is_dir():
      raise ValueError('Active path is not a directory')
    if dry_run:
      return {'success': True, 'dry_run': True, 'audit': result}
    revision_id = uuid.uuid4().hex
    revisions.mkdir(exist_ok=True)
    revision = revisions/revision_id
    previous_active_backup = None
    if active.is_dir() and not active.is_symlink():
      # Flat legacy releases are overwritten in place below. Keep their exact
      # active payload outside the publishable revision tree so rollback can
      # restore every file, not just the entry manifest.
      backup_root = book/'.readalong_rollback'/revision_id
      backup_root.mkdir(parents=True, exist_ok=False)
      previous_active_backup = backup_root/'active'
      shutil.copytree(active, previous_active_backup)
    shutil.copytree(assets, revision, ignore=lambda directory, names:
      [n for n in names if n in {'work', 'cache', 'pairing'}] if Path(directory) == assets else [])
    # Copy exclusions must not silently change the audited publication snapshot.
    original_files = [p for p in assets.rglob('*') if p.is_file() and not any(
      part in {'work', 'cache', 'pairing'} for part in p.relative_to(assets).parts)]
    if any(sha256(p) != sha256(revision/p.relative_to(assets)) for p in original_files):
      raise ValueError('Copied publication snapshot differs')
    if compute_dir_fingerprint(assets) != result['candidateFingerprint']:
      raise ValueError('Candidate changed before commit')
    if source_snapshot(book) != source_state:
      raise ValueError('Physical audio/EPUB changed during publication')
    manifest = json.loads((revision/'readalong.manifest.json').read_text())
    manifest['assetRevision'] = revision_id
    manifest['readalongEnabled'] = True
    manifest['practicalRelease'] = {'policyVersion': POLICY, 'decision': result['decision'],
      'acousticAccuracyVerified': False, 'metrics': result['metrics'], 'gapIntervals': result['gapIntervals']}
    atomic_json(revision/'readalong.manifest.json', manifest)
    previous_link = str(active.resolve()) if active.is_symlink() else None
    previous = (active/'readalong.manifest.json').read_bytes() if (active/'readalong.manifest.json').is_file() else None
    if previous is not None:
      (revision/'previous-entry-manifest.json').write_bytes(previous)
    receipt = {'policyVersion': POLICY, 'revision': revision_id, 'previousLink': previous_link,
      'previousManifestSha256': hashlib.sha256(previous).hexdigest() if previous is not None else None,
      'previousActiveBackup': str(previous_active_backup.relative_to(book)) if previous_active_backup else None,
      'audit': result}
    atomic_json(revision/'release-receipt.json', receipt)
    if active.is_symlink():
      _switch(book, revision)
    else:
      # Build the replacement beside the live directory and swap it in whole.
      # Copying file by file only ever added: a file the previous release had
      # and this one does not stayed behind, so the active tree accumulated
      # documents from several revisions at once and the reader could resolve
      # an anchor against a stale body.  The version directory keeps the full
      # payload, so rollback still restores whatever this replaces.
      staged = book/('.readalong_stage_'+uuid.uuid4().hex)
      staged.mkdir(parents=True)
      try:
        atomic_json(staged/'readalong.manifest.json', manifest)
        for fname in ('timeline.json', 'practical-audit.json'):
          if (revision/fname).is_file():
            shutil.copy2(revision/fname, staged/fname)
        if (revision/'text').is_dir():
          shutil.copytree(revision/'text', staged/'text')
        replaced = book/'.readalong_rollback'/revision_id/'replaced-active'
        replaced.parent.mkdir(parents=True, exist_ok=True)
        if replaced.exists():
          raise ValueError('Replaced active payload already exists; refusing to overwrite it')
        if active.exists():
          os.replace(active, replaced)
        os.replace(staged, active)
      except BaseException:
        shutil.rmtree(staged, ignore_errors=True)
        raise
    return {'success': True, 'active_dir': str(active), 'revision_dir': str(revision),
      'receipt': str(revision/'release-receipt.json'), 'audit': result}


def rollback_practical(book_dir, revision_id):
  """Restore the saved entry; never delete either revision or source material."""
  if not isinstance(revision_id, str) or len(revision_id) != 32 or any(c not in '0123456789abcdef' for c in revision_id):
    raise ValueError('Invalid practical revision ID')
  book = Path(book_dir).resolve(strict=True)
  with BookPublishLock(book) as lock:
    if not lock._acquired:
      return {'success': False, 'code': 'ERR_PUBLISH_LOCKED'}
    revision = safe_path(book, '.readalong_revisions/'+revision_id)
    receipt = json.loads((revision/'release-receipt.json').read_text())
    current = json.loads((book/'readalong/readalong.manifest.json').read_text())
    if current.get('assetRevision') != revision_id or receipt.get('policyVersion') != POLICY:
      raise ValueError('Rollback is not for the current practical release')
    previous = revision/'previous-entry-manifest.json'
    if not previous.is_file() or sha256(previous) != receipt.get('previousManifestSha256'):
      raise ValueError('No intact previous entry to restore')
    if receipt.get('entryOnly'):
      atomic_json(book/'readalong/readalong.manifest.json', json.loads(previous.read_text()))
    elif receipt.get('previousLink'):
      old = Path(receipt['previousLink']).resolve(strict=True)
      if not old.is_relative_to((book/'.readalong_revisions').resolve()):
        raise ValueError('Unmanaged previous revision')
      _switch(book, old)
    else:
      previous_manifest = json.loads(previous.read_text())
      backup_rel = receipt.get('previousActiveBackup')
      if backup_rel:
        backup = safe_path(book, backup_rel)
      else:
        # Older releases may already have a pinned revision even though the
        # active path was still a flat directory.
        old_revision = previous_manifest.get('assetRevision')
        backup = safe_path(book, f'.readalong_revisions/{old_revision}') if isinstance(old_revision, str) else None
      if backup is None or not backup.is_dir() or not (backup/'readalong.manifest.json').is_file():
        raise ValueError('No complete previous active payload is available for rollback')
      active = book/'readalong'
      restore_stage = book/('.readalong_restore_'+uuid.uuid4().hex)
      shutil.copytree(backup, restore_stage, ignore=shutil.ignore_patterns('release-receipt.json', 'previous-entry-manifest.json'))
      rollback_root = book/'.readalong_rollback'/revision_id
      rollback_root.mkdir(parents=True, exist_ok=True)
      rejected_active = rollback_root/'rejected-active'
      if rejected_active.exists():
        raise ValueError('Rejected active payload already exists; refusing to overwrite it')
      if active.is_symlink():
        active.unlink()
      elif active.exists():
        os.replace(active, rejected_active)
      os.replace(restore_stage, active)
    return {'success': True, 'restoredPreviousEntry': True}


def exclude_readalong(book_dir, reason):
  """Disable only follow-along; preserve original audio and every old revision."""
  if not isinstance(reason, str) or not reason.strip():
    raise ValueError('An explicit exclusion reason is required')
  book = Path(book_dir).resolve(strict=True)
  with BookPublishLock(book) as lock:
    if not lock._acquired:
      return {'success': False, 'code': 'ERR_PUBLISH_LOCKED'}
    active = book/'readalong'
    entry = active/'readalong.manifest.json'
    if not entry.exists():
      return {'success': True, 'action': 'ALREADY_AUDIO_ONLY'}
    previous = entry.read_bytes()
    old_manifest = json.loads(previous)
    if old_manifest.get('readalongEnabled') is False:
      return {'success': True, 'action': 'ALREADY_AUDIO_ONLY'}
    revisions = book/'.readalong_revisions'
    if active.is_symlink() and not active.resolve().is_relative_to(revisions.resolve()):
      raise ValueError('Unmanaged active symlink')
    revision_id = uuid.uuid4().hex
    revision = revisions/revision_id
    revision.mkdir(parents=True)
    (revision/'previous-entry-manifest.json').write_bytes(previous)
    manifest = {'schemaVersion': 1, 'bookId': book.name, 'assetRevision': revision_id,
      'readalongEnabled': False, 'audioSources': [], 'timeline': 'timeline.json',
      'practicalRelease': {'policyVersion': POLICY, 'decision': 'AUDIO_ONLY', 'reason': reason}}
    atomic_json(revision/'readalong.manifest.json', manifest)
    atomic_json(revision/'timeline.json', [])
    atomic_json(revision/'release-receipt.json', {'policyVersion': POLICY, 'revision': revision_id,
      'previousLink': str(active.resolve()) if active.is_symlink() else None,
      'previousManifestSha256': hashlib.sha256(previous).hexdigest(), 'exclusionReason': reason,
      'entryOnly': not active.is_symlink()})
    if active.is_symlink():
      _switch(book, revision)
    else:
      atomic_json(entry, manifest)
    return {'success': True, 'action': 'AUDIO_ONLY', 'revision_dir': str(revision)}
