"""Final workflow decisions must not loop back into an unowned REVIEW state."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.readalong.practical_batch import run, resolve_candidate


class PracticalBatchTests(unittest.TestCase):
  def test_removed_missing_and_screened_inputs_have_distinct_finite_decisions(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      ledger = root/'ledger.json'
      records = {uid: {'workflow_status': state} for uid, state in [
        ('removed', 'USER_EXCLUDED'), ('no-epub', 'SKIPPED_NO_EPUB'),
        ('no-cache', 'CACHE_REQUIRED'), ('screen', 'SCREEN_UNDETERMINED')]}
      ledger.write_text(json.dumps({'records': records}))
      inventory = root/'inventory.json'
      inventory.write_text(json.dumps({'units': []}))
      with patch('tools.readalong.practical_batch.audit_practical', side_effect=AssertionError('No candidate to audit')):
        result = run(ledger, [inventory], root/'execution')
      self.assertEqual([r['decision'] for r in result['records'].values()],
        ['OPERATOR_EXCLUDED', 'SKIP_NO_EPUB', 'NOT_GENERATED', 'EXCLUDE_UNVERIFIED'])
      self.assertFalse(any(r['published'] for r in result['records'].values()))

  def test_multiple_physical_candidates_do_not_pick_the_first(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      for name in ('one', 'two'):
        (root/name).mkdir()
        (root/name/'readalong.manifest.json').write_text('{}')
      with self.assertRaisesRegex(ValueError, 'unambiguous'):
        resolve_candidate(root)
      book = root/'book'
      book.mkdir()
      ledger, inventory = root/'ledger.json', root/'inventory.json'
      ledger.write_text(json.dumps({'records': {'book': {'workflow_status': 'COMPLETED',
        'candidatePath': str(root/'one')}}}))
      inventory.write_text(json.dumps({'units': [{'unit_id': 'book', 'book_dir': str(book)}]}))
      rejected = {'success': False, 'audit': {'publishAllowed': False, 'hardErrors': [{'code': 'ERR_AUDIO_SHA256_MISMATCH'}]}}
      with patch('tools.readalong.practical_batch.publish_practical', return_value=rejected), \
           patch('tools.readalong.practical_batch.exclude_readalong', side_effect=AssertionError('Must not disable changed input')):
        result = run(ledger, [inventory], root/'execution', publish=True)
      self.assertEqual(result['records']['book']['decision'], 'EXECUTION_ERROR')

  def test_existing_execution_is_never_overwritten(self):
    with tempfile.TemporaryDirectory() as tmp:
      with self.assertRaisesRegex(ValueError, 'new execution'):
        run('unused', [], Path(tmp))
