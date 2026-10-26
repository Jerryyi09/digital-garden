"""Export only accepted candidate assets and a standard-library publication runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from tools.readalong.atomic_io import atomic_json
from tools.readalong.acoustic_evaluator import sha256
from tools.readalong.controlled_publisher import compute_dir_fingerprint


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--decisions', type=Path, required=True)
  parser.add_argument('--inventory', type=Path, action='append', required=True)
  parser.add_argument('--material-policy', type=Path, required=True)
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  out = args.output.resolve()
  decisions = json.loads(args.decisions.read_text())
  roots = [Path(r['candidatePath']).resolve() for r in decisions['records'].values() if r.get('candidatePath')]
  source_books = [Path(u['book_dir']).resolve() for p in args.inventory for u in json.loads(p.read_text())['units']]
  if out.exists() or any(out == p or out.is_relative_to(p) for p in roots+source_books):
    raise ValueError('Bundle requires a new directory outside candidates and source books')
  out.mkdir(parents=True)
  project = Path(__file__).resolve().parents[2]
  runtime = ['__init__.py', 'atomic_io.py', 'source_evidence.py', 'acoustic_evaluator.py', 'authoritative_validator.py',
    'controlled_publisher.py', 'practical_publisher.py', 'practical_batch.py', 'candidate_safety.py',
    'input_inventory.py', 'usability_evaluator.py', 'readalong_cli.py']
  for relative in [Path('tools/readalong')/name for name in runtime]+[
      Path('tools/readalong_fast/__init__.py'), Path('tools/readalong_fast/scopes.py')]:
    target = out/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(project/relative, target)
  inputs = []
  for i, inventory in enumerate(args.inventory):
    filename = f'inventory-{i}.json'
    shutil.copyfile(inventory, out/filename)
    inputs.append(filename)
  shutil.copyfile(args.decisions, out/'decisions.json')
  shutil.copyfile(args.material_policy, out/'material-policy.json')
  accepted = []
  for uid, row in decisions['records'].items():
    if row['decision'] not in {'PUBLISH', 'PUBLISH_WITH_GAPS'}:
      continue
    source = Path(row['candidatePath']).resolve(strict=True)
    if compute_dir_fingerprint(source) != row['audit']['candidateFingerprint']:
      raise ValueError(f'Candidate changed after adjudication: {uid}')
    destination = out/'candidates'/hashlib.sha256(uid.encode()).hexdigest()[:20]
    shutil.copytree(source, destination, ignore=lambda path, names:
      [n for n in names if n in {'work', 'cache', 'pairing'}] if Path(path) == source else [])
    if compute_dir_fingerprint(source) != row['audit']['candidateFingerprint']:
      raise ValueError(f'Candidate changed during bundle copy: {uid}')
    accepted.append(uid)
  atomic_json(out/'bundle.json', {'acceptedUnits': accepted, 'inventories': inputs,
    'audioAndOriginalEpubIncluded': False, 'filesSha256': {
      p.relative_to(out).as_posix(): sha256(p) for p in out.rglob('*') if p.is_file()}})
  print(json.dumps({'output': str(out), 'acceptedCandidates': len(accepted), 'sourceMediaCopied': False}, ensure_ascii=False))


if __name__ == '__main__':
  main()
