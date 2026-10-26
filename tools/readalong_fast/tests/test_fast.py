"""Fast mode must save work without confusing a sample with full coverage."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from bs4 import BeautifulSoup
from tools.readalong_fast.matcher import ParagraphIndex, prepare_paragraphs, tokens
from tools.readalong_fast.pipeline import InputCache, SpeechCache, audit_candidate, auto_exclude_mismatch, file_hash, generate, words_to_units, normalize_native, context_units
from tools.readalong_fast.resume import locked, select_unfinished, run, fast_identity
from tools.readalong_fast.decoding import AudioDecodeIssue, DecodeEnvironmentError


def block_rows(text):
  """Sampling fetches real grid blocks, so a whole-track stub is not enough.

  Returns a `chunk` side_effect shaped like a real cache block: rows in block-relative
  coordinates, since the sampler measures its strata with an offset inside the block."""
  def rows(path, sha, start, duration, *rest):
    return [{"start": start+i*15.0, "end": start+i*15.0+15, "text": text}
            for i in range(max(1, int(duration//15)))]
  return rows


class MatcherTests(unittest.TestCase):
  def prepare(self, html):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    path = Path(self.temp.name)
    (path/"c.html").write_text(html)
    return prepare_paragraphs(path, ["c.html"])

  def test_mixed_flow_and_inline_text_preserved(self):
    html = '<html><body><li>Direct <em id="keep">inline</em> words<p>Nested paragraph text.</p>Trailing words.</li><!-- ignore --></body></html>'
    docs, paras, book = self.prepare(html)
    self.assertEqual(BeautifulSoup(html, "html.parser").body.get_text(), docs["c.html"].body.get_text())
    self.assertTrue(docs["c.html"].find(id="keep"))
    self.assertEqual(book, tokens("Direct inline words Nested paragraph text. Trailing words."))
    self.assertEqual(len({p["fragment"] for p in paras}), len(paras))

  def test_duplicate_original_ids_repaired_without_changing_text_or_first_link(self):
    docs, paras, _ = self.prepare('<p id="x">one two three</p><p id="x">four five six</p><a href="#x">link</a>')
    soup = docs["c.html"]
    ids = [n["id"] for n in soup.find_all(id=True)]
    self.assertEqual(len(ids), len(set(ids)))
    self.assertEqual(soup.find(id="x").get_text(), "one two three")
    self.assertEqual(soup.a["href"], "#x")
    self.assertEqual(soup.find(attrs={"data-readalong-original-id": "x"}).get_text(), "four five six")

  def test_long_book_locates_late_chapter_with_bounded_windows(self):
    paras = [{"offset": i*100, "length": 100, "document": str(i), "fragment": str(i), "text": str(i)} for i in range(1000)]
    book = [f"token{i}" for i in range(100000)]
    index = ParagraphIndex(book, paras)
    result = index.locate(" ".join(book[92120:92160]))
    self.assertEqual(result["start"], 92120)
    self.assertEqual(result["paragraph"]["document"], "921")
    self.assertLess(index.metrics["comparedBookTokens"], 4000)

  def test_ambiguous_repeated_chapters_do_not_pick_first(self):
    phrase = tokens("alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu")
    book = phrase+[f"gap{i}" for i in range(200)]+phrase
    paras = [{"offset": 0, "length": 212, "document": "a", "fragment": "a"}, {"offset": 212, "length": 12, "document": "b", "fragment": "b"}]
    self.assertIsNone(ParagraphIndex(book, paras).locate(" ".join(phrase)))

  def test_no_match_does_not_create_location(self):
    index = ParagraphIndex(tokens("one two three four five six seven eight nine ten"), [{"offset": 0}])
    self.assertIsNone(index.locate("a totally unrelated sentence describes purple elephants and winter storms"))

  def test_duplicate_spine_retains_order_but_shares_physical_dom(self):
    text = " ".join(f"word{i}" for i in range(70))
    self.prepare('<html><body><p>'+text+'</p></body></html>')
    diag = []
    docs, paras, book = prepare_paragraphs(Path(self.temp.name), ["c.html", "c.html"], diag)
    self.assertEqual(len(docs), 1)
    self.assertEqual(len(book), 140)
    self.assertEqual([p["offset"] for p in paras], [0, 70])
    self.assertEqual([p["spineOccurrence"] for p in paras], [0, 1])
    self.assertEqual(paras[0]["fragment"], paras[1]["fragment"])
    self.assertIsNotNone(ParagraphIndex(book, paras).locate(" ".join(book[:20])))
    self.assertEqual(diag[0]["reason"], "REUSED_SPINE_DOCUMENT")

  def test_oversized_paragraph_split_preserves_inline_ids_and_visible_text(self):
    text = " ".join(f"word{i}" for i in range(350))
    html = '<html><body><p id="original"><em id="link-target">'+text+'</em></p></body></html>'
    docs, paras, book = self.prepare(html)
    self.assertEqual(docs["c.html"].body.get_text(), text)
    self.assertGreater(len(paras), 3)
    self.assertTrue(all(p["length"] <= 80 for p in paras))
    self.assertEqual(len(docs["c.html"].find_all(id="link-target")), 1)
    self.assertEqual(len(book), 350)


class CacheTests(unittest.TestCase):
  def test_native_padding_and_zero_length_do_not_abort_real_audio(self):
    raw = [{"start": 0, "end": 4, "text": "Valid speech"},
      {"start": 4, "end": 4, "text": "Ghost"},
      {"start": 4, "end": 10.06, "text": "Valid final speech"},
      {"start": 10.06, "end": 17, "text": "Padding hallucination"}]
    rows, diag = normalize_native(raw, 0, 10)
    self.assertEqual([(r["start"], r["end"]) for r in rows], [(0, 4), (4, 10)])
    self.assertEqual({d["reason"] for d in diag}, {"ZERO_DURATION", "INTERSECTED_WITH_DECODED_AUDIO", "OUTSIDE_DECODED_AUDIO"})

  def test_conflicts_remain_unmapped_and_cannot_merge_into_valid_speech(self):
    rows, diag = normalize_native([{"start": 0, "end": 5, "text": "valid"},
      {"start": 4, "end": 7, "text": "conflict"},
      {"start": 7, "end": 10, "text": "valid final"}], 0, 10)
    self.assertTrue(rows[1]["timingRejected"])
    self.assertEqual(len(context_units(rows)), 3)
    self.assertEqual(diag[0]["reason"], "UNTRUSTED_BOUNDARY_OR_OVERLAP")

  def test_nonfinite_and_reversed_output_are_explicit_diagnostics(self):
    rows, diag = normalize_native([{"start": float("nan"), "end": 2, "text": "bad"},
      {"start": 4, "end": 2, "text": "bad"}], 0, 10)
    self.assertFalse(rows)
    json.dumps(diag, allow_nan=False)
    self.assertEqual(len(diag), 2)

  def test_word_grouping_retains_real_boundaries(self):
    words = [{"word": "word", "start": i, "end": i+.5} for i in range(30)]
    rows = words_to_units(words, 0, 30)
    self.assertEqual(rows[0]["start"], 0)
    self.assertEqual(rows[-1]["end"], 29.5)
    self.assertTrue(all(r["end"]-r["start"] <= 20 for r in rows))

  def test_input_hash_reused_until_file_stat_changes(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      source = root/"audio"
      source.write_bytes(b"original")
      cache = InputCache(root/"inputs.json")
      sha = file_hash(source)
      cache.verify(source, sha)
      with patch("tools.readalong_fast.pipeline.file_hash", side_effect=AssertionError("must not hash twice")):
        cache.verify(source, sha)
      source.write_bytes(b"changed")
      with self.assertRaisesRegex(RuntimeError, "SOURCE_CHANGED"):
        cache.verify(source, sha)

  def test_valid_word_cache_avoids_asr_and_audio_conversion(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      (root/"old.json").write_text(json.dumps([{"word": "Hello", "start": 0, "end": 1}]))
      cache = SpeechCache(root/"new", [root], "a"*64, cache_only=True)
      rows = cache.lookup_words(["old.json"], 0, 10)
      self.assertEqual(rows[0]["text"], "Hello")
      self.assertEqual(cache.stats["legacyCachedAudioSeconds"], 10)

  def test_native_asr_uses_segment_times_and_reuses_its_cache(self):
    import numpy as np
    from types import SimpleNamespace
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      cache = SpeechCache(root, [], "a"*64)
      backend = unittest.mock.Mock(return_value={"segments": [{"start": 0, "end": 5, "text": "Some real speech"}]})
      with patch("tools.readalong_fast.pipeline.subprocess.run", return_value=SimpleNamespace(stdout=np.zeros(16000*5, dtype="<f4").tobytes())) as decode, \
           patch("tools.readalong_fast.pipeline.transcription_backend", return_value=backend):
        first = cache.chunk(Path("unused.mp3"), "b"*64, 30.0, 5.0)
        second = cache.chunk(Path("renamed.mp3"), "b"*64, 30.0, 5.0)
      self.assertFalse(backend.call_args.kwargs["word_timestamps"])
      self.assertEqual(first, second)
      self.assertEqual(first[0]["start"], 30)
      self.assertEqual(first[0]["end"], 35)
      self.assertEqual(backend.call_count, 1)
      self.assertEqual(decode.call_count, 1)
      self.assertEqual(cache.stats["segmentCachedAudioSeconds"], 5)

  def test_pcm_is_bounded_and_rejected_cache_rows_do_not_become_trusted(self):
    import numpy as np
    from types import SimpleNamespace
    with tempfile.TemporaryDirectory() as tmp:
      cache = SpeechCache(Path(tmp), [], "a"*64)
      backend = unittest.mock.Mock(return_value={"segments": [
        {"start": 0, "end": 2, "text": "valid"},
        {"start": 2, "end": 7, "text": "padding contaminated"}]})
      with patch("tools.readalong_fast.pipeline.subprocess.run", return_value=SimpleNamespace(stdout=np.zeros(16000*6, dtype="<f4").tobytes())), \
           patch("tools.readalong_fast.pipeline.transcription_backend", return_value=backend):
        first = cache.chunk(Path("unused.mp3"), "b"*64, 0, 5)
        second = cache.chunk(Path("unused.mp3"), "b"*64, 0, 5)
      self.assertEqual(len(backend.call_args.args[0]), 16000*5)
      self.assertTrue(first[-1]["timingRejected"])
      self.assertTrue(second[-1]["timingRejected"])
      self.assertTrue(list(Path(tmp).glob("*.raw.json")))


class ContinuationTests(unittest.TestCase):
  def test_completed_and_reviewed_books_never_selected_again(self):
    states = ["COMPLETED", "BLOCKED_INPUT", "NOT_RUN", "ATTEMPT_RESERVED", "PREFLIGHT_ERROR", "INTERRUPTED_PER_UNIT_ERROR"]
    units = [{"unit_id": str(i)} for i in range(len(states))]
    records = {str(i): {"unit_id": str(i), "workflow_status": s, "attempts": int(s == "ATTEMPT_RESERVED")} for i, s in enumerate(states)}
    selected, carried = select_unfinished(records, units)
    self.assertEqual(selected, ["2", "3", "4", "5"])
    self.assertEqual(set(carried), {"0", "1"})

  def test_exhausted_budget_is_carried_not_reset(self):
    selected, carried = select_unfinished({"a": {"unit_id": "a", "workflow_status": "ATTEMPT_RESERVED", "attempts": 3}}, [{"unit_id": "a"}])
    self.assertFalse(selected)
    self.assertEqual(carried["a"]["attempts"], 3)

  def test_active_predecessor_lock_refuses_handoff(self):
    with tempfile.TemporaryDirectory() as tmp:
      path = Path(tmp)/"lock"
      with locked(path):
        with self.assertRaisesRegex(RuntimeError, "BATCH_STILL_RUNNING"):
          with locked(path):
            self.fail("must not acquire twice")


class GenerationTests(unittest.TestCase):
  def test_failed_context_falls_back_only_to_real_segment_boundaries(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      book = root/"book"
      book.mkdir()
      (book/"a.mp3").write_bytes(b"synthetic-audio")
      text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
      with zipfile.ZipFile(book/"b.epub", "w") as z:
        z.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
        z.writestr("content.opf", '<package><manifest><item id="c" href="c.html"/></manifest><spine><itemref idref="c"/></spine></package>')
        z.writestr("c.html", '<html><body><p>'+text+'</p></body></html>')
      unit = {"book_dir": str(book), "audio_tracks": [{"rel_to_book": "a.mp3", "sha256": file_hash(book/"a.mp3"), "measured_duration": 10}],
        "epubs": [{"rel_to_book": "b.epub", "sha256": file_hash(book/"b.epub")}]}
      # A non-book credit followed by real narration must not lose the narration.
      rows = context_units([{"start": 0, "end": 7, "text": "unrelated credit "*20},
        {"start": 7, "end": 10, "text": text}])
      cache = SpeechCache(root/"cache", [], "a"*64, True)
      with patch.object(cache, "whole_legacy_track", return_value=rows), \
           patch.object(cache, "chunk", side_effect=block_rows(text)):
        report = generate(unit, root/"candidate", cache, InputCache(root/"inputs.json"))
      timeline = json.loads((root/"candidate/timeline.json").read_text())
      self.assertEqual([(r["start"], r["end"]) for r in timeline], [(7, 10)])
      self.assertEqual(report["metrics"]["unmappedSpeechUnitRatio"], .7)
      self.assertEqual(report["matchingStats"]["observedBoundaryFallbacks"], 1)
      self.assertEqual(report["readalongUsability"], "REVIEW_MAPPING")

  def test_full_generation_with_cached_speech_and_single_practical_audit(self):
    with tempfile.TemporaryDirectory() as tmp:
      root = Path(tmp)
      book = root/"book"
      book.mkdir()
      (book/"a.mp3").write_bytes(b"synthetic-audio")
      text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
      with zipfile.ZipFile(book/"b.epub", "w") as z:
        z.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
        z.writestr("content.opf", '<package><manifest><item id="c" href="c.html"/></manifest><spine><itemref idref="c"/></spine></package>')
        z.writestr("c.html", '<html><body><p>'+text+'</p></body></html>')
      unit = {"book_dir": str(book), "audio_tracks": [{"rel_to_book": "a.mp3", "sha256": file_hash(book/"a.mp3"), "measured_duration": 10}],
        "epubs": [{"rel_to_book": "b.epub", "sha256": file_hash(book/"b.epub")} ]}
      cache = SpeechCache(root/"cache", [], "a"*64, True)
      with patch.object(cache, "whole_legacy_track", return_value=[{"start": 0, "end": 10, "text": text}]), \
           patch.object(cache, "chunk", side_effect=block_rows(text)):
        report = generate(unit, root/"candidate", cache, InputCache(root/"inputs.json"))
      self.assertEqual(report["readalongUsability"], "USABLE")
      self.assertEqual(report["certificationStatus"], "NOT_REQUESTED")
      self.assertFalse((book/"readalong").exists())
      self.assertFalse((root/"candidate/quality.json").exists())
      self.assertTrue((root/"candidate/timeline.json").exists())
      self.assertIn(".readalong-active", (root/"candidate/text/c.html").read_text())

  def test_empty_timeline_cannot_pass(self):
    report = audit_candidate([], [], {"a": {"duration": 500}}, {}, [])
    self.assertEqual(report["readalongUsability"], "REVIEW_MAPPING")


class AutoExclusionTests(unittest.TestCase):
  """A confirmed mismatch registers follow-along off, except on a published book."""

  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)
    self.book = self.root/"book"
    self.book.mkdir()

  def publish(self, released):
    entry = self.book/"readalong"
    entry.mkdir(exist_ok=True)
    manifest = {"schemaVersion": 1, "bookId": "book", "readalongEnabled": True,
                "audioSources": [], "timeline": "timeline.json"}
    if released:
      manifest["practicalRelease"] = {"policyVersion": "practical-release-v1",
        "decision": "USABLE_WITH_GAPS", "acousticAccuracyVerified": False}
    (entry/"readalong.manifest.json").write_text(json.dumps(manifest))

  def test_registration_writes_a_complete_receipt(self):
    # A book that has only ever been generated, never published: its entry has no
    # practicalRelease, so a mismatch registers it.
    self.publish(False)
    detail = {"locatedRatio": 0.0164, "locatedUpper": 0.0368, "maxBlockLocatedRatio": 0.0594, "blocks": 6}
    result = auto_exclude_mismatch(self.book, detail, "SAMPLE_MISMATCH")
    self.assertTrue(result["registered"])
    self.assertEqual(result["action"], "AUDIO_ONLY")
    self.assertIn("SAMPLE_MISMATCH", result["reason"])
    revision = Path(result["result"]["revision_dir"])
    manifest = json.loads((revision/"readalong.manifest.json").read_text())
    self.assertFalse(manifest["readalongEnabled"])
    self.assertEqual(manifest["practicalRelease"]["decision"], "AUDIO_ONLY")
    self.assertIn("SAMPLE_MISMATCH", manifest["practicalRelease"]["reason"])
    receipt = json.loads((revision/"release-receipt.json").read_text())
    self.assertTrue(receipt["policyVersion"])
    self.assertEqual(receipt["revision"], manifest["assetRevision"])
    self.assertEqual(receipt["exclusionReason"], result["reason"])
    self.assertIsNotNone(receipt["previousManifestSha256"])
    self.assertEqual(json.loads((revision/"timeline.json").read_text()), [])
    # The verdict detail is carried into the reason so a reader can audit it.
    for field in ("locatedRatio", "locatedUpper", "maxBlockLocatedRatio", "blocks"):
      self.assertIn(str(detail[field]), result["reason"])

  def test_published_book_guardrail_writes_nothing(self):
    self.publish(True)
    entry = self.book/"readalong/readalong.manifest.json"
    before = entry.read_bytes()
    result = auto_exclude_mismatch(self.book, {"blocks": 6}, "SAMPLE_MISMATCH")
    self.assertFalse(result["registered"])
    self.assertEqual(result["reason"], "PUBLISHED_BOOK_NOT_AUTO_EXCLUDED")
    self.assertEqual(entry.read_bytes(), before)
    self.assertFalse((self.book/".readalong_revisions").exists())

  def test_constructed_mismatch_outside_a_book_dir_never_registers(self):
    # A calibration case pairs one book's audio with another's EPUB, so it has no
    # book directory of its own and must never touch any manifest.
    outside = self.root/"calibration-case"
    outside.mkdir()
    result = auto_exclude_mismatch(outside, {"blocks": 6}, "SAMPLE_MISMATCH")
    self.assertTrue(result["registered"])
    self.assertEqual(result["action"], "ALREADY_AUDIO_ONLY")
    self.assertFalse((outside/"readalong").exists())
    self.assertFalse((outside/".readalong_revisions").exists())


class RunnerIntegrationTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)
    self.old = self.root/"old"
    self.old.mkdir()
    self.output = self.root/"new"
    self.book = self.root/"book"
    self.book.mkdir()
    self.text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    (self.book/"a.mp3").write_bytes(b"synthetic-audio")
    with zipfile.ZipFile(self.book/"b.epub", "w") as z:
      z.writestr("META-INF/container.xml", '<container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
      z.writestr("content.opf", '<package><manifest><item id="c" href="c.html"/></manifest><spine><itemref idref="c"/></spine></package>')
      z.writestr("c.html", '<html><body><p>'+self.text+'</p></body></html>')
    unit = {"unit_id": "books/pending", "book_dir": str(self.book), "audio_count": 1,
      "audio_tracks": [{"rel_to_book": "a.mp3", "sha256": file_hash(self.book/"a.mp3"), "measured_duration": 10}],
      "epubs": [{"rel_to_book": "b.epub", "sha256": file_hash(self.book/"b.epub"), "valid_zip": True}],
      "detected_languages": ["en"]}
    inv = {"summary": {"conservation_verified": True}, "units": [{**unit, "unit_id": "books/done"}, unit]}
    (self.old/"inventory.json").write_text(json.dumps(inv))
    digest = file_hash(self.old/"inventory.json")
    records = {"books/done": {"unit_id": "books/done", "workflow_status": "COMPLETED", "attempts": 1, "readalong_usability": "REVIEW_MAPPING"},
      "books/pending": {"unit_id": "books/pending", "workflow_status": "NOT_RUN", "attempts": 0}}
    (self.old/"results.json").write_text(json.dumps({"schema_version": 1, "campaign_id": "old", "inventory_sha256": digest, "records": records}))
    (self.old/"campaign.json").write_text(json.dumps({"inventory_sha256": digest}))

  def add_remaining(self):
    inv = json.loads((self.old/"inventory.json").read_text())
    inv["units"].append({**inv["units"][1], "unit_id": "books/remaining"})
    (self.old/"inventory.json").write_text(json.dumps(inv))
    sha = file_hash(self.old/"inventory.json")
    data = json.loads((self.old/"results.json").read_text())
    data["inventory_sha256"] = sha
    data["records"]["books/remaining"] = {"unit_id": "books/remaining", "workflow_status": "NOT_RUN", "attempts": 0}
    (self.old/"results.json").write_text(json.dumps(data))
    (self.old/"campaign.json").write_text(json.dumps({"inventory_sha256": sha}))

  def stopped_decode_review(self):
    self.add_remaining()
    run(self.old, self.output, plan_only=True)
    data = json.loads((self.output/"results.json").read_text())
    data["records"]["books/pending"].update(workflow_status="PER_UNIT_ERROR", newAttempts=1,
      error="RuntimeError: AUDIO_DECODE_INCOMPLETE: requested=5 decoded=4.4")
    (self.output/"results.json").write_text(json.dumps(data))
    (self.output/"STOP.json").write_text(json.dumps({"unit_id": "books/pending", "error": "AUDIO_DECODE_INCOMPLETE: requested=5 decoded=4.4"}))
    raw = {"status": "QUARANTINE", "reason": "PCM_SHORTFALL", "parameters": {"sourceSha256": file_hash(self.book/"a.mp3")},
      "requestedStart": 0, "requestedEnd": 5}
    diagnostic = self.root/"decode.json"
    diagnostic.write_text(json.dumps(raw))
    proof = self.root/"proof.json"
    proof.write_text(json.dumps({"unitId": "books/pending", "sourceHashVerified": True,
      "sourceUnchanged": True, "activeUnchanged": True, "outcome": "QUARANTINED_AUDIO", "asrInvoked": False,
      "codeSha256": fast_identity(), "sourceSha256": file_hash(self.book/"a.mp3"), "requestedStart": 0, "requestedEnd": 5,
      "decodeEvidencePath": str(diagnostic), "decodeEvidenceSha256": file_hash(diagnostic)}))
    review = self.root/"review.json"
    review.write_text(json.dumps({"schemaVersion": 1, "decision": "RESUME_UNSTARTED_QUARANTINE_AUDIO",
      "previousRun": str(self.output.resolve()), "codeSha256": fast_identity(),
      "planSha256": file_hash(self.output/"plan.json"), "resultsSha256": file_hash(self.output/"results.json"),
      "inventorySha256": file_hash(self.output/"inventory.json"), "stopSha256": file_hash(self.output/"STOP.json"),
      "quarantinedUnitId": "books/pending", "evidencePath": str(proof), "evidenceSha256": file_hash(proof)}))
    return review

  def test_decode_quarantine_continues_next_book_and_never_auto_retries(self):
    self.add_remaining()
    from tools.readalong_fast.pipeline import generate as real_generate
    def generate_with_bad_book(unit, dest, *args, **kwargs):
      if unit["unit_id"] == "books/pending":
        dest.mkdir(parents=True)
        raise AudioDecodeIssue(dest/"decode.json", {"reason": "PCM_SHORTFALL", "requestedSeconds": 5, "decodedSeconds": 4.4})
      return real_generate(unit, dest, *args, **kwargs)
    with patch("tools.readalong_fast.resume.generate", side_effect=generate_with_bad_book) as generate_mock, \
         patch.object(SpeechCache, "whole_legacy_track", return_value=[{"start": 0, "end": 10, "text": self.text}]), \
         patch.object(SpeechCache, "chunk", side_effect=block_rows(self.text)):
      first = run(self.old, self.output, cache_only=True)
      run(self.old, self.output, cache_only=True)
    self.assertEqual(generate_mock.call_count, 2)
    self.assertEqual(first["newCompleteCandidates"], 1)
    rows = json.loads((self.output/"results.json").read_text())["records"]
    self.assertEqual(rows["books/pending"]["workflow_status"], "QUARANTINED_AUDIO")
    self.assertEqual(rows["books/pending"]["newAttempts"], 1)
    self.assertEqual(rows["books/remaining"]["workflow_status"], "COMPLETED")
    self.assertFalse((self.output/"STOP.json").exists())

  def test_decoder_environment_failure_still_stops_batch(self):
    with patch("tools.readalong_fast.resume.generate", side_effect=DecodeEnvironmentError("FFMPEG_ENVIRONMENT: missing decoder")):
      with self.assertRaises(DecodeEnvironmentError):
        run(self.old, self.output, cache_only=True)
    self.assertTrue((self.output/"STOP.json").exists())

  def test_reviewed_decode_stop_migrates_only_unstarted_and_preserves_budget_and_stop(self):
    review = self.stopped_decode_review()
    before = file_hash(self.output/"results.json"), file_hash(self.output/"STOP.json")
    repaired = self.root/"decode-recovery"
    plan_summary = run(self.old, repaired, repair_from=self.output, decode_review=review, plan_only=True)
    self.assertEqual(plan_summary["selectedUnits"], 1)
    rows = json.loads((repaired/"results.json").read_text())["records"]
    self.assertEqual(rows["books/pending"]["workflow_status"], "QUARANTINED_AUDIO")
    self.assertEqual(rows["books/pending"]["newAttempts"], 1)
    with patch.object(SpeechCache, "whole_legacy_track", return_value=[{"start": 0, "end": 10, "text": self.text}]), \
         patch.object(SpeechCache, "chunk", side_effect=block_rows(self.text)):
      result = run(self.old, repaired, repair_from=self.output, decode_review=review, cache_only=True)
    self.assertEqual(result["newlyUsable"], 1)
    self.assertEqual(before, (file_hash(self.output/"results.json"), file_hash(self.output/"STOP.json")))

  def test_stop_cannot_be_bypassed_without_review(self):
    self.stopped_decode_review()
    with self.assertRaisesRegex(ValueError, "identity mismatch or safety stop"):
      run(self.old, self.root/"recovery", repair_from=self.output, plan_only=True)

  def test_changed_stop_or_proof_refuses_recovery(self):
    review = self.stopped_decode_review()
    proof = self.root/"proof.json"
    proof.write_text(proof.read_text()+" ")
    with self.assertRaisesRegex(ValueError, "evidence changed"):
      run(self.old, self.root/"recovery", repair_from=self.output, decode_review=review, plan_only=True)

  def test_non_decode_safety_stop_is_never_released_by_decode_review(self):
    review = self.stopped_decode_review()
    (self.output/"STOP.json").write_text(json.dumps({"unit_id": "books/pending", "error": "SOURCE_CHANGED: input"}))
    data = json.loads(review.read_text())
    data["stopSha256"] = file_hash(self.output/"STOP.json")
    review.write_text(json.dumps(data))
    with self.assertRaisesRegex(ValueError, "Only the reviewed legacy decode"):
      run(self.old, self.root/"recovery", repair_from=self.output, decode_review=review, plan_only=True)

  def test_real_handoff_and_resume_leave_completed_books_and_predecessor_unchanged(self):
    before = file_hash(self.old/"results.json")
    speech = [{"start": 0, "end": 10, "text": self.text}]
    with patch.object(SpeechCache, "whole_legacy_track", return_value=speech) as read, \
         patch.object(SpeechCache, "chunk", side_effect=block_rows(self.text)):
      result = run(self.old, self.output, cache_only=True)
      again = run(self.old, self.output, cache_only=True)
    self.assertEqual(result["states"], {"CARRIED_UNCHANGED": 1, "USABLE": 1})
    self.assertEqual(result, again)
    self.assertEqual(read.call_count, 1)
    self.assertEqual(before, file_hash(self.old/"results.json"))
    data = json.loads((self.output/"results.json").read_text())
    self.assertEqual(data["records"]["books/pending"]["newAttempts"], 1)

  def test_mutated_predecessor_refuses_resume(self):
    run(self.old, self.output, plan_only=True)
    data = json.loads((self.old/"results.json").read_text())
    data["records"]["books/pending"]["attempts"] = 1
    (self.old/"results.json").write_text(json.dumps(data))
    with self.assertRaisesRegex(ValueError, "Frozen handoff changed"):
      run(self.old, self.output, plan_only=True)

  def test_explicit_repair_migration_preserves_failures_counts_and_finished_records(self):
    with patch("tools.readalong_fast.resume.generate", side_effect=ValueError("Duplicate spine document")):
      run(self.old, self.output, cache_only=True)
    before = file_hash(self.output/"results.json")
    repaired = self.root/"repair"
    with patch("tools.readalong_fast.resume.fast_identity", return_value="b"*64):
      with self.assertRaisesRegex(ValueError, "Frozen handoff changed"):
        run(self.old, self.output, plan_only=True)
      plan = run(self.old, repaired, repair_from=self.output, plan_only=True)
      self.assertEqual(plan["selectedUnits"], 1)
      row = json.loads((repaired/"results.json").read_text())["records"]["books/pending"]
      self.assertEqual(row["newAttempts"], 1)
      self.assertEqual(row["repairPredecessorRecord"]["workflow_status"], "PER_UNIT_ERROR")
      with patch.object(SpeechCache, "whole_legacy_track", return_value=[{"start": 0, "end": 10, "text": self.text}]), \
         patch.object(SpeechCache, "chunk", side_effect=block_rows(self.text)):
        result = run(self.old, repaired, repair_from=self.output, cache_only=True)
      self.assertEqual(result["newlyUsable"], 1)
      self.assertEqual(result["newCompleteCandidates"], 1)
      row = json.loads((repaired/"results.json").read_text())["records"]["books/pending"]
      self.assertEqual(row["newAttempts"], 2)
    self.assertEqual(before, file_hash(self.output/"results.json"))

  def test_repair_never_resets_exhausted_budget_or_retries_unknown_failures(self):
    with patch("tools.readalong_fast.resume.generate", side_effect=ValueError("Duplicate spine document")):
      run(self.old, self.output, cache_only=True)
    data = json.loads((self.output/"results.json").read_text())
    data["records"]["books/pending"]["newAttempts"] = 3
    (self.output/"results.json").write_text(json.dumps(data))
    result = run(self.old, self.root/"repair", repair_from=self.output, plan_only=True)
    self.assertEqual(result["selectedUnits"], 0)
    self.assertEqual(result["budgetExhausted"], 1)
    data["records"]["books/pending"].update(newAttempts=1, error="ValueError: unrelated bug")
    (self.output/"results.json").write_text(json.dumps(data))
    result = run(self.old, self.root/"repair-other", repair_from=self.output, plan_only=True)
    self.assertEqual(result["selectedUnits"], 0)

  def test_running_predecessor_cannot_create_a_plan(self):
    with locked(self.old/".session.lock"):
      with self.assertRaisesRegex(RuntimeError, "BATCH_STILL_RUNNING"):
        run(self.old, self.output, plan_only=True)
    self.assertFalse(self.output.exists())

  def test_old_interrupted_attempts_are_inherited_not_reset(self):
    old = json.loads((self.old/"results.json").read_text())
    old["records"]["books/pending"].update(workflow_status="ATTEMPT_RESERVED", attempts=2)
    (self.old/"results.json").write_text(json.dumps(old))
    with patch.object(SpeechCache, "whole_legacy_track", return_value=[{"start": 0, "end": 10, "text": self.text}]), \
         patch.object(SpeechCache, "chunk", side_effect=block_rows(self.text)):
      run(self.old, self.output, cache_only=True)
    row = json.loads((self.output/"results.json").read_text())["records"]["books/pending"]
    self.assertEqual(row["inheritedAttempts"], 2)
    self.assertEqual(row["newAttempts"], 1)
    self.assertEqual(row["workflow_status"], "COMPLETED")

  def test_distributed_screen_does_not_claim_full_book_mapping(self):
    unit = json.loads((self.old/"inventory.json").read_text())["units"][1]
    unit["audio_tracks"][0]["measured_duration"] = 14400
    cache = SpeechCache(self.root/"cache", [], "a"*64, True)
    unrelated = "Clouds thunder mountains rivers ocean winter summer spring autumn planets stars universe galaxies distant space"
    # Sampling now reads real grid blocks, so the stub is the block fetch itself.
    # Enough speech to decide, none of it in this EPUB: a confirmed mismatch is
    # reported as REVIEW_MAPPING and never as a certified full-book mapping.
    def block_rows(path, sha, start, duration, *rest):
      return [{"start": start+i*15.0, "end": start+i*15.0+15, "text": unrelated}
              for i in range(int(duration//15))]
    with patch.object(InputCache, "duration", return_value=14400), \
         patch.object(cache, "chunk", side_effect=block_rows):
      report = generate(unit, self.root/"screen-only", cache, InputCache(self.root/"input-cache.json"))
    self.assertEqual(report["stage"], "SCREEN_REVIEW")
    self.assertEqual(report["readalongUsability"], "REVIEW_MAPPING")
    self.assertEqual(report["materialAssessment"], "MISMATCH_CONFIRMED")
    self.assertFalse(report["fullAudioProcessed"])
    self.assertTrue(report["materialMismatchConfirmed"])
    self.assertFalse((self.root/"screen-only/timeline.json").exists())

  def test_completed_fast_candidate_disappearance_is_not_silent_success(self):
    with patch.object(SpeechCache, "whole_legacy_track", return_value=[{"start": 0, "end": 10, "text": self.text}]), \
         patch.object(SpeechCache, "chunk", side_effect=block_rows(self.text)):
      run(self.old, self.output, cache_only=True)
    row = json.loads((self.output/"results.json").read_text())["records"]["books/pending"]
    (Path(row["candidatePath"])/"timeline.json").write_text("[]")
    with self.assertRaisesRegex(RuntimeError, "candidate changed or disappeared"):
      run(self.old, self.output, cache_only=True)


if __name__ == "__main__":
  unittest.main()
