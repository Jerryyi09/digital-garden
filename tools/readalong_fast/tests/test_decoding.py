"""A bad book must not become good PCM or stop unrelated books."""
import errno
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools.readalong_fast.decoding import AudioDecodeIssue, DecodeEnvironmentError, decode_pcm
from tools.readalong_fast.pipeline import SpeechCache


class DecodeTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root = Path(self.temp.name)

  def test_healthy_pcm_is_bounded_and_diagnostic_is_preserved(self):
    proc = SimpleNamespace(stdout=b"\0"*(6*16000*4), stderr=b"", returncode=0)
    with patch("tools.readalong_fast.decoding.subprocess.run", return_value=proc):
      pcm, report = decode_pcm(Path("unused"), 30, 5, self.root/"decode.json", {})
    self.assertEqual(len(pcm), 5*16000*4)
    self.assertEqual(report["status"], "DECODED")
    self.assertEqual(report["returnedPcmSeconds"], 6)

  def test_shortfall_is_quarantined_before_asr_not_padded(self):
    proc = SimpleNamespace(stdout=b"\0"*(71827*4), stderr=b"", returncode=0)
    cache = SpeechCache(self.root, [], "a"*64, tolerant_decode=False)
    with patch("tools.readalong_fast.decoding.subprocess.run", return_value=proc), \
         patch("tools.readalong_fast.pipeline.transcription_backend") as backend:
      with self.assertRaises(AudioDecodeIssue) as raised:
        cache.chunk(Path("unused.mp3"), "b"*64, 0, 5)
    self.assertFalse(backend.called)
    report = json.loads(Path(raised.exception.evidence_path).read_text())
    self.assertAlmostEqual(report["decodedSeconds"], 4.4891875)
    self.assertFalse(report["missingIntervalLocationKnown"])
    self.assertFalse([p for p in self.root.glob("*.json") if not p.name.endswith(".decode.json")])

  def test_corrupt_decoder_stderr_is_not_ignored_even_with_exit_zero_and_full_duration(self):
    proc = SimpleNamespace(stdout=b"\0"*(5*16000*4), stderr=b"[aac] Invalid data found when processing input", returncode=0)
    with patch("tools.readalong_fast.decoding.subprocess.run", return_value=proc):
      with self.assertRaises(AudioDecodeIssue) as raised:
        decode_pcm(Path("unused"), 30, 5, self.root/"decode.json", {})
    self.assertEqual(raised.exception.report["reason"], "DECODER_REPORTED_ERRORS")

  def test_empty_output_is_book_local(self):
    proc = SimpleNamespace(stdout=b"", stderr=b"", returncode=0)
    with patch("tools.readalong_fast.decoding.subprocess.run", return_value=proc):
      with self.assertRaises(AudioDecodeIssue) as raised:
        decode_pcm(Path("unused"), 0, 5, self.root/"decode.json", {})
    self.assertEqual(raised.exception.report["reason"], "EMPTY_OUTPUT")

  def test_system_errors_are_not_downgraded_to_bad_material(self):
    for message, number in [(b"No space left on device", errno.ENOSPC), (b"Input/output error", errno.EIO),
        (b"Permission denied", errno.EACCES), (b"Cannot allocate memory", errno.ENOMEM)]:
      with self.subTest(message=message), patch("tools.readalong_fast.decoding.subprocess.run",
          return_value=SimpleNamespace(stdout=b"", stderr=message, returncode=1)):
        with self.assertRaises(OSError) as raised:
          decode_pcm(Path("unused"), 0, 5, self.root/"decode.json", {})
        self.assertEqual(raised.exception.errno, number)

  def test_missing_decoder_and_signalled_process_are_system_faults(self):
    for code, text in [(1, b"Unknown decoder 'aac'"), (-9, b"")]:
      with self.subTest(code=code), patch("tools.readalong_fast.decoding.subprocess.run",
          return_value=SimpleNamespace(stdout=b"", stderr=text, returncode=code)):
        with self.assertRaises(DecodeEnvironmentError):
          decode_pcm(Path("unused"), 0, 5, self.root/"decode.json", {})

  def test_missing_executable_is_not_swallowed(self):
    with patch("tools.readalong_fast.decoding.subprocess.run", side_effect=FileNotFoundError(2, "missing", "ffmpeg")):
      with self.assertRaises(FileNotFoundError):
        decode_pcm(Path("unused"), 0, 5, self.root/"decode.json", {})
