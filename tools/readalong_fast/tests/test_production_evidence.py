"""Production opt-in cache and parallel verification preserve audit verdicts."""
import json
from unittest.mock import patch

from tools.readalong.practical_publisher import audit_practical
from tools.readalong_fast.tests import test_audit_options as fixtures


class ProductionEvidenceTests(fixtures.AuditOptionTests):
  def setUp(self):
    super().setUp()
    self.cache = self.candidate.parent/'evidence.json'
    audit_practical(self.book, self.candidate, incremental_cache=self.cache)

  def assert_rejected_equally(self):
    expected = audit_practical(self.book, self.candidate, workers=1)
    self.assertFalse(expected['publishAllowed'])
    self.assertEqual(audit_practical(self.book, self.candidate, workers=4), expected)
    incremental = audit_practical(self.book, self.candidate, incremental_cache=self.cache)
    incremental.pop('verification')
    self.assertEqual(incremental, expected)

  def test_warm_cache_reuses_only_source_evidence(self):
    with patch('tools.readalong.practical_publisher.sha256', side_effect=AssertionError('Unexpected source read')):
      report = audit_practical(self.book, self.candidate, incremental_cache=self.cache)
    self.assertTrue(report['publishAllowed'])
    self.assertGreater(report['verification']['reusedEvidenceCount'], 0)
    self.assertFalse(report['verification']['independentFullRead'])

  def test_default_does_not_reuse_persistent_cache(self):
    self.assertNotIn('verification', audit_practical(self.book, self.candidate))
    self.assertEqual(audit_practical(self.book, self.candidate, workers=1),
                     audit_practical(self.book, self.candidate, workers=4))

  def test_cache_cannot_overwrite_candidate(self):
    with self.assertRaises(ValueError):
      audit_practical(self.book, self.candidate, incremental_cache=self.candidate/'evidence.json')

  def test_bad_cache_version_fails_closed(self):
    self.cache.write_text(json.dumps({'version': 999, 'rows': {}}))
    with self.assertRaises(ValueError):
      audit_practical(self.book, self.candidate, incremental_cache=self.cache)
