"""Compare saved baseline modules with current pure-CPU hot paths."""
import argparse
import importlib.util
import json
from pathlib import Path
from statistics import median
from time import perf_counter

from tools.readalong_fast import matcher
from tools.readalong import authoritative_validator as validator


def load(path, name):
  spec = importlib.util.spec_from_file_location(name, path)
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


def measure(fn, repeats=5):
  samples = []
  for _ in range(repeats):
    start = perf_counter()
    result = fn()
    samples.append(perf_counter()-start)
  return result, median(samples)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--baseline-matcher', required=True)
  parser.add_argument('--baseline-validator', required=True)
  parser.add_argument('--candidate', required=True)
  args = parser.parse_args()
  old = load(args.baseline_matcher, 'baseline_matcher')
  old_validator = load(args.baseline_validator, 'baseline_validator')
  rows = json.loads((Path(args.candidate)/'timeline.json').read_text())
  # Use real mapped text; deterministic corruptions exercise fallback matching.
  book, paragraphs, queries = [], [], []
  for row in rows[:400]:
    words = matcher.tokens(row['text'])
    if len(words) < 12:
      continue
    offset = len(book)
    paragraphs.append({'offset': offset, 'document': row['document'],
                       'fragment': row['fragment'], 'text': row['text']})
    book.extend(words)
    query = words[:60]
    queries.append((' '.join(query), offset))
    altered = ['unrecognized' if i % 5 == 0 else w for i, w in enumerate(query)]
    queries.append((' '.join(altered), offset))
  results = {}
  outputs = []
  for label, module in [('before', old), ('after', matcher)]:
    index = module.ParagraphIndex(book, paragraphs)
    def run():
      return [(index.locate(q, c), dict(index.last_diagnostic)) for q, c in queries]
    output, seconds = measure(run)
    outputs.append(output)
    results[label] = seconds
  assert outputs[0] == outputs[1], 'Mapping or diagnostic changed'
  results.update(speedup=results['before']/results['after'], queries=len(queries), equal=True)
  dom_results, dom_outputs = {}, []
  documents = sorted({row['document'] for row in rows})
  contents = [(Path(args.candidate)/name).read_text() for name in documents]
  for label, module in [('before', old_validator), ('after', validator)]:
    def run_dom():
      output = []
      for html in contents:
        dom = module.DOMFragmentExtractor()
        dom.feed(html)
        dom.close()
        output.append((dom.id_to_text, dom.seen_ids, dom.duplicate_ids))
      return output
    output, seconds = measure(run_dom)
    dom_outputs.append(output)
    dom_results[label] = seconds
  assert dom_outputs[0] == dom_outputs[1], 'DOM result changed'
  dom_results.update(speedup=dom_results['before']/dom_results['after'], documents=len(contents), equal=True)
  def paths(cached):
    resolved = {}
    output = []
    for row in rows:
      name = row['document']
      if not cached or name not in resolved:
        resolved[name] = validator.safe_path(Path(args.candidate), name)
      output.append(resolved[name].is_file())
    return output
  before_paths, before_seconds = measure(lambda: paths(False))
  after_paths, after_seconds = measure(lambda: paths(True))
  assert before_paths == after_paths
  print(json.dumps({'matcher': results, 'dom': dom_results, 'documentPaths': {
    'before': before_seconds, 'after': after_seconds,
    'speedup': before_seconds/after_seconds, 'segments': len(rows), 'equal': True}}, indent=2))


if __name__ == '__main__':
  main()
