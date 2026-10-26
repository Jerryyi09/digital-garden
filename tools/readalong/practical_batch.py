"""Finite candidate adjudication and explicit personal-use publication; never ASR."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from tools.readalong.atomic_io import atomic_json
from tools.readalong.acoustic_evaluator import sha256
from tools.readalong.practical_publisher import audit_practical, publish_practical, exclude_readalong


def resolve_candidate(value):
  if not value:
    return None
  root = Path(value).resolve(strict=True)
  matches = [root] if (root/'readalong.manifest.json').is_file() else [p.parent for p in root.glob('*/readalong.manifest.json')]
  if len(matches) != 1:
    raise ValueError('No unambiguous physical candidate; do not pick the first result')
  return matches[0]


def run(ledger_path, inventory_paths, output, *, publish=False, book_root=None, units=(), material_policy=None, candidate_root=None):
  output = Path(output).resolve()
  if output.exists():
    raise ValueError('Use a new execution directory; preserve prior decisions')
  ledger_path = Path(ledger_path).resolve(strict=True)
  records = json.loads(ledger_path.read_text())['records']
  inventory = {}
  for path in inventory_paths:
    inventory.update({u['unit_id']: u for u in json.loads(Path(path).read_text())['units']})
  if units and any(uid not in records for uid in units):
    raise ValueError('Unknown requested unit')
  policies = json.loads(Path(material_policy).read_text())['entries'] if material_policy else []
  by_uid = {e['unitId']: e for e in policies}
  if len(by_uid) != len(policies):
    raise ValueError('Duplicate material policies')
  roots = [Path(u['book_dir']).resolve() for u in inventory.values()]
  if any(output == p or output.is_relative_to(p) for p in roots):
    raise ValueError('Execution output cannot be inside source books')
  if book_root and output.is_relative_to(Path(book_root).resolve()):
    raise ValueError('Execution output cannot be inside publication root')
  output.mkdir(parents=True)
  result = {'ledgerSha256': sha256(ledger_path), 'mode': 'PUBLISH' if publish else 'AUDIT',
    'newAsrSeconds': 0, 'records': {}}
  for uid, old in records.items():
    if units and uid not in units:
      continue
    row = {'unitId': uid, 'published': False, 'excludedOnServer': False}
    try:
      # Removed books are never probed, recreated or restored.
      state = old.get('workflow_status')
      prior_decision = old.get('decision')
      if state == 'USER_EXCLUDED' or prior_decision == 'OPERATOR_EXCLUDED':
        row.update(decision='OPERATOR_EXCLUDED', reason='Previously removed by user; not probed')
      elif state == 'SKIPPED_NO_EPUB' or prior_decision == 'SKIP_NO_EPUB':
        row.update(decision='SKIP_NO_EPUB', reason='No EPUB; no input supplementation requested')
      elif state == 'SCREEN_UNDETERMINED' or prior_decision in {'EXCLUDE_UNVERIFIED', 'EXCLUDE_READALONG'}:
        row.update(decision='EXCLUDE_UNVERIFIED', reason='No complete alignment evidence; audio-only, not a proven material mismatch')
        if prior_decision == 'EXCLUDE_READALONG':
          if not isinstance(old.get('audit'), dict) or old['audit'].get('publishAllowed') is not False:
            raise ValueError('Missing explicit exclusion evidence')
          row.update(decision='EXCLUDE_READALONG', reason='; '.join(old['audit']['reasons']), audit=old['audit'])
        if publish:
          book = (Path(book_root)/uid).resolve(strict=True) if book_root else Path(inventory[uid]['book_dir']).resolve(strict=True)
          if book_root and not book.is_relative_to(Path(book_root).resolve(strict=True)):
            raise ValueError('Publication target escapes selected root')
          row['excludedOnServer'] = exclude_readalong(book, row['reason'])['success']
      elif not old.get('candidatePath'):
        row.update(decision='NOT_GENERATED', reason='Missing cache or no complete candidate; not proof of wrong material')
      else:
        candidate = resolve_candidate(Path(candidate_root)/hashlib.sha256(uid.encode()).hexdigest()[:20]
          if candidate_root else old['candidatePath'])
        book = (Path(book_root)/uid).resolve(strict=True) if book_root else Path(inventory[uid]['book_dir']).resolve(strict=True)
        if book_root and not book.is_relative_to(Path(book_root).resolve(strict=True)):
          raise ValueError('Publication target escapes selected root')
        row['candidatePath'], row['bookDir'] = str(candidate), str(book)
        if publish:
          published = publish_practical(book, candidate, material=by_uid.get(uid))
          audit = published.get('audit')
          if published['success']:
            row.update(decision=audit['decision'], published=True, receipt=published['receipt'])
          elif audit and not audit['publishAllowed']:
            if audit.get('hardErrors'):
              raise ValueError('Destination/source or structural consistency failed; existing active left unchanged')
            excluded = exclude_readalong(book, '; '.join(audit['reasons']))
            row.update(decision='EXCLUDE_READALONG', excludedOnServer=excluded['success'])
          else:
            raise ValueError(str(published))
        else:
          audit = audit_practical(book, candidate, material=by_uid.get(uid))
          row['decision'] = audit['decision']
        row['audit'] = audit
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
      row.update(decision='EXECUTION_ERROR', reason=f'{type(exc).__name__}: {exc}')
    result['records'][uid] = row
    atomic_json(output/'results.json', result)
    print(uid, row['decision'], 'published' if row['published'] else '', flush=True)
  atomic_json(output/'summary.json', {'counts': dict(Counter(r['decision'] for r in result['records'].values())),
    'published': sum(r['published'] for r in result['records'].values()),
    'excludedOnServer': sum(r['excludedOnServer'] for r in result['records'].values()), 'newAsrSeconds': 0})
  return result


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--ledger', type=Path, required=True)
  parser.add_argument('--inventory', type=Path, action='append', required=True)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--book-root', type=Path, help='Explicit physical publication root, not virtual AList root')
  parser.add_argument('--candidate-root', type=Path, help='Transferred candidates indexed by SHA256(unitId)[:20]; never rewrites old ledgers')
  parser.add_argument('--material-policy', type=Path, help='Approved entries wrapper')
  parser.add_argument('--unit', action='append', default=[])
  parser.add_argument('--publish', action='store_true', help='Actually change selected active entry manifests')
  args = parser.parse_args()
  result = run(args.ledger, args.inventory, args.output, publish=args.publish, book_root=args.book_root,
    units=args.unit, material_policy=args.material_policy, candidate_root=args.candidate_root)
  raise SystemExit(2 if any(r['decision'] == 'EXECUTION_ERROR' for r in result['records'].values()) else 0)


if __name__ == '__main__':
  main()
