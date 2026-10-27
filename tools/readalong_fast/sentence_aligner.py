"""Sentence-level alignment core: Coarse paragraph indexing + DOM-bound sentence refinement.

Guarantees:
1. Outer paragraph id="fast-..." strictly preserved.
2. mark_sentences splits text inside each paragraph into sentence spans.
3. Each paragraph timeline segment is refined into its exact child sentence spans.
4. Monotone time projection via words within the paragraph's acoustic interval.
5. Inherits speechUnitId so audit metrics strictly preserve high localization ratios.
"""
from collections import Counter, defaultdict
from bisect import bisect_left, bisect_right
from difflib import SequenceMatcher
import hashlib
from pathlib import Path
import re
from typing import List, Dict, Any, Tuple

from bs4 import BeautifulSoup
from tools.readalong.engine.mark_sentence import mark_sentences, _build_char_map
from tools.readalong.authoritative_validator import safe_path, DOMFragmentExtractor
from tools.readalong_fast.matcher import tokens


def normalize_token(word: str) -> str:
  return re.sub(r"[^a-z0-9]", "", word.lower())


def prepare_marked_sentence_documents(
    text_dir: Path,
    spine_htmls: List[str]
) -> Dict[str, BeautifulSoup]:
  """Run mark_sentences on each spine document while preserving existing fast- IDs."""
  documents = {}
  for name in spine_htmls:
    path = safe_path(text_dir, name)
    raw = path.read_text(encoding="utf-8")
    doc_id = hashlib.sha256(name.encode()).hexdigest()[:16]
    marked = mark_sentences(raw, chapter_id=doc_id, language="english")
    soup = BeautifulSoup(marked, "html.parser")
    documents[f"text/{name}"] = soup
    safe_path(text_dir, name).write_text(str(soup), encoding="utf-8")
  return documents


def refine_timeline_by_dom(
    paragraph_timeline: List[Dict[str, Any]],
    documents: Dict[str, BeautifulSoup],
    ordered_words: List[Dict[str, Any]],
    track_durations: Dict[str, float] = None
) -> List[Dict[str, Any]]:
  """Refine each paragraph segment in paragraph_timeline into its child sentence segments."""
  sentence_timeline = []

  # Group words by audioSourceId
  track_words = defaultdict(list)
  for w in ordered_words:
    track_words[w.get("audioSourceId", "")].append(w)
  dom_text_cache = {}
  paragraph_rows_cache = {}
  paragraph_match_cache = {}
  sentence_cache = {}
  node_text_cache = {}
  document_ids = {}
  global_ids = {}
  for key, soup in documents.items():
    ids = {}
    for element in soup.find_all(id=True):
      ids.setdefault(element["id"], element)
      global_ids.setdefault(element["id"], (key, soup, element))
    document_ids[id(soup)] = ids
  track_intervals = {}
  for sid, words in track_words.items():
    starts = [word["start"] for word in words]
    if starts == sorted(starts):
      max_ends = []
      latest = float("-inf")
      for word in words:
        latest = max(latest, word["end"])
        max_ends.append(latest)
      track_intervals[sid] = (starts, max_ends)

  def remember_id(soup, node, fragment):
    node["id"] = fragment
    document_ids[id(soup)].setdefault(fragment, node)
    # Preserve document iteration order when a recovered ID already exists elsewhere.
    for key, candidate_soup in documents.items():
      candidate = document_ids[id(candidate_soup)].get(fragment)
      if candidate is not None:
        global_ids[fragment] = (key, candidate_soup, candidate)
        break

  def paragraph_rows(soup):
    cache_key = id(soup)
    if cache_key not in paragraph_rows_cache:
      paragraph_rows_cache[cache_key] = [
        (element, tokens(element.get_text(" ", strip=True)))
        for element in soup.find_all(["p", "div", "li", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6"])
        if element.find("span", id=re.compile(r"segment\d+"))
      ]
    return paragraph_rows_cache[cache_key]

  def authoritative_dom_text(soup, fragment):
    cache_key = id(soup)
    if cache_key not in dom_text_cache:
      parser = DOMFragmentExtractor()
      parser.feed(str(soup))
      parser.close()
      dom_text_cache[cache_key] = parser.id_to_text
    return dom_text_cache[cache_key].get(fragment, "")

  for p_idx, p_seg in enumerate(paragraph_timeline):
    doc_key = p_seg["document"]
    sid = p_seg["audioSourceId"]
    p_start = p_seg["start"]
    p_end = p_seg["end"]
    p_text = p_seg.get("text", "")
    unit_id = p_seg.get("speechUnitId", "0")
    occ_id = p_seg.get("occurrenceId", "0")
    frag_id = p_seg["fragment"]
    p_start = max(0, p_start)
    if track_durations and sid in track_durations:
      p_end = min(p_end, track_durations[sid])
    fallback_occurrence = f"{occ_id}:fallback:{frag_id}:{p_seg.get('start', 0):.3f}:{p_idx}"

    # Invalid/zero-duration coarse rows cannot safely become highlight segments.
    # Keep the boundary resolver strict instead of manufacturing playback time.
    if not isinstance(p_start, (int, float)) or not isinstance(p_end, (int, float)) or p_end <= p_start:
      continue

    soup = documents.get(doc_key.removeprefix("text/")) or documents.get(doc_key)
    if not soup:
      sentence_timeline.append({**p_seg, "start": p_start, "end": p_end,
        "occurrenceId": fallback_occurrence, "timingStatus": "SENTENCE_FROM_PARAGRAPH"})
      continue

    # Locate paragraph node by fragment ID
    node = document_ids[id(soup)].get(frag_id)
    if node is None and frag_id in global_ids:
      candidate_key, soup, node = global_ids[frag_id]
      doc_key = f"text/{candidate_key}"
    if not node and p_text:
      match_key = (id(soup), p_text)
      if match_key in paragraph_match_cache:
        node = paragraph_match_cache[match_key]
      else:
        wanted = tokens(p_text)
        rows = paragraph_rows(soup)
        candidates = [element for element, candidate_tokens in rows if candidate_tokens == wanted]
        if candidates:
          node = min(candidates, key=lambda element: len(element.find_all(["p", "div", "li", "blockquote"])))
        else:
          # Sentence marking can replace the synthetic paragraph wrapper. Recover
          # its paragraph container by a strict token-window match in the marked DOM.
          best = None
          fuzzy_threshold = .89 if len(wanted) >= 10 else (.98 if len(wanted) >= 5 else .999)
          wanted_counts = Counter(wanted)
          window_scores = {}
          for element, candidate_tokens in rows:
            if not candidate_tokens or len(wanted) < 3:
              continue
            min_window_size = max(3, len(wanted)-2)
            for start in range(max(0, len(candidate_tokens)-min_window_size+1)):
              joined, next_token = "", start
              while next_token < len(candidate_tokens) and len(joined) < len(wanted[0]):
                joined += candidate_tokens[next_token]
                next_token += 1
              if joined != wanted[0]:
                continue
              consumed = next_token - start
              for window_size in range(min_window_size, len(wanted)+3):
                window = [wanted[0], *candidate_tokens[next_token:next_token+window_size-consumed]]
                if len(window) < max(3, int(len(wanted)*.9)):
                  continue
                window_key = tuple(window)
                if window_key not in window_scores:
                  # Multiset overlap is an upper bound on ordered matching.
                  # A rejected window cannot reach the unchanged acceptance threshold.
                  overlap = sum(min(count, wanted_counts[word]) for word, count in Counter(window).items())
                  upper = 2.0 * overlap / (len(wanted) + len(window))
                  window_scores[window_key] = (SequenceMatcher(None, wanted, window, autojunk=False).ratio()
                    if upper >= fuzzy_threshold and (best is None or upper > best[0]) else -1.0)
                ratio = window_scores[window_key]
                if ratio >= fuzzy_threshold and (best is None or ratio > best[0]):
                  best = (ratio, element)
          fuzzy_threshold = .89 if len(wanted) >= 10 else (.98 if len(wanted) >= 5 else .999)
          if best and best[0] >= fuzzy_threshold:
            node = best[1]
        paragraph_match_cache[match_key] = node
      if node is not None:
        if node.get("id"):
          frag_id = node["id"]
        else:
          remember_id(soup, node, frag_id)
    if not node:
      sentence_timeline.append({**p_seg, "document": doc_key, "fragment": frag_id,
        "start": p_start, "end": p_end, "text": p_text,
        "occurrenceId": fallback_occurrence, "timingStatus": "SENTENCE_FROM_PARAGRAPH"})
      continue
    paragraph_text = authoritative_dom_text(soup, frag_id)
    if not paragraph_text:
      if id(node) not in node_text_cache:
        node_text_cache[id(node)] = _build_char_map(node)[1].strip()
      paragraph_text = node_text_cache[id(node)] or p_text

    # DOM contents are stable throughout refinement; reuse extracted sentence rows.
    cache_key = id(node)
    if cache_key not in sentence_cache:
      spans = node.find_all("span", id=re.compile(r"segment\d+"))
      sub_sentences = []
      for s_node in spans:
        _, s_text, _ = _build_char_map(s_node)
        s_tokens = tokens(s_text)
        if s_tokens:
          sub_sentences.append({"fragment": s_node["id"], "text": s_text.strip(), "tokens": s_tokens})
      sentence_cache[cache_key] = (bool(spans), sub_sentences)
    has_spans, sub_sentences = sentence_cache[cache_key]
    if not has_spans:
      sentence_timeline.append({**p_seg, "document": doc_key, "fragment": frag_id,
        "start": p_start, "end": p_end, "text": paragraph_text,
        "occurrenceId": fallback_occurrence, "timingStatus": "SENTENCE_FROM_PARAGRAPH"})
      continue

    if len(sub_sentences) <= 1:
      # A one-sentence paragraph has no fine-grained timing evidence here;
      # retain the paragraph anchor unless the global projection later covers it.
      source_fragment = sub_sentences[0]["fragment"] if sub_sentences else None
      sentence_timeline.append({
        **p_seg,
        "document": doc_key,
        "start": p_start, "end": p_end,
        "fragment": frag_id,
        "sourceSentenceFragment": source_fragment,
        "text": paragraph_text,
        "occurrenceId": fallback_occurrence,
        "timingStatus": "SENTENCE_FROM_PARAGRAPH"
      })
      continue

    # Multi-sentence paragraph: align words in [p_start - 0.5, p_end + 0.5]
    candidates = track_words.get(sid, [])
    if sid in track_intervals:
      starts, max_ends = track_intervals[sid]
      candidates = candidates[bisect_left(max_ends, p_start - 0.5):bisect_right(starts, p_end + 0.5)]
    cand_words = [w for w in candidates
                  if w["end"] >= p_start - 0.5 and w["start"] <= p_end + 0.5]

    book_tokens = []
    token_to_sub_idx = []
    for s_i, sent in enumerate(sub_sentences):
      for tok in sent["tokens"]:
        book_tokens.append(tok)
        token_to_sub_idx.append(s_i)

    audio_toks = [normalize_token(w.get("word") or "") for w in cand_words]
    matcher = SequenceMatcher(None, book_tokens, audio_toks, autojunk=False)

    sub_matched_words = defaultdict(list)
    for b_idx, a_idx, size in matcher.get_matching_blocks():
      for step in range(size):
        s_i = token_to_sub_idx[b_idx + step]
        sub_matched_words[s_i].append(cand_words[a_idx + step])

    last_sub_end = p_start
    total_sub = len(sub_sentences)

    for s_i, sent in enumerate(sub_sentences):
      m_words = sub_matched_words.get(s_i, [])
      if m_words:
        s_time = max(m_words[0]["start"], last_sub_end)
        e_time = min(m_words[-1]["end"], p_end)
        if s_time >= p_end or e_time <= s_time:
          continue
        if e_time < s_time + 0.3:
          e_time = min(p_end, s_time + max(0.3, len(sent["tokens"]) * 0.25))
        if s_i == total_sub - 1:
          e_time = min(p_end, max(e_time, p_end))

        sentence_timeline.append({
          "audioSourceId": sid,
          "start": round(s_time, 2),
          "end": round(e_time, 2),
          "document": doc_key,
          "fragment": sent["fragment"],
          "sourceSentenceFragment": sent["fragment"],
          "text": sent["text"],
          "occurrenceId": occ_id,
          "speechUnitId": unit_id,
          "timingStatus": "SENTENCE_EXACT" if len(m_words) >= 2 else "SENTENCE_PARTIAL"
        })
        last_sub_end = round(e_time, 2)
      else:
        # Fallback proportionally inside paragraph duration
        dur_slice = max(0.6, (p_end - p_start) / total_sub)
        s_time = last_sub_end
        e_time = min(p_end, s_time + dur_slice) if s_i < total_sub - 1 else p_end
        if s_time >= p_end or e_time <= s_time:
          continue

        sentence_timeline.append({
          "audioSourceId": sid,
          "start": round(s_time, 2),
          "end": round(e_time, 2),
          "document": doc_key,
          "fragment": frag_id,
          "sourceSentenceFragment": sent["fragment"],
          # Keep the sentence payload bounded. The DOM anchor remains the
          # paragraph fallback, but copying the whole paragraph into every
          # sentence row can multiply a long block into a gigabyte timeline.
          "text": sent["text"],
          "occurrenceId": f"{fallback_occurrence}:{s_i}",
          "speechUnitId": unit_id,
          "timingStatus": "SENTENCE_FROM_PARAGRAPH"
        })
        last_sub_end = round(e_time, 2)

  return sentence_timeline


def locate_gap_blocks(sentence_timeline, documents, ordered_words):
  """Time the unlocated anchors that sit between two located ones.

  A heading, a one-line dedication or a bare URL line carries no coarse match of
  its own, so nothing ever assigns it a time and the reader never highlights it.
  The same is true of a sentence inside a paragraph whose other sentences did
  match.  The audio that speaks it does exist: it occupies the silence between
  the last segment before it and the first segment after it.

  The search window is exactly that gap.  Widening it would let a short anchor
  match a coincidental phrase elsewhere on the track, which is the failure mode
  that makes an unbounded search unusable on a multi-hour recording.
  """
  by_track = defaultdict(list)
  for seg in sentence_timeline:
    by_track[seg.get("audioSourceId", "")].append(seg)
  # Sorted starts with a running maximum of ends, so a window query can binary
  # search both bounds and still be exact for overlapping segments.
  occupied_by_track = {}
  for track, rows in by_track.items():
    rows.sort(key=lambda row: row.get("start", 0))
    starts, running, latest = [], [], float("-inf")
    for row in rows:
      starts.append(row.get("start", 0))
      latest = max(latest, row.get("end", 0))
      running.append(latest)
    occupied_by_track[track] = (starts, running)

  located = defaultdict(set)
  rows_by_anchor = defaultdict(list)
  for seg in sentence_timeline:
    for key in ("fragment", "sourceSentenceFragment"):
      anchor = seg.get(key)
      if anchor:
        located[seg.get("document", "")].add(anchor)
        rows_by_anchor[anchor].append(seg)
  for rows in rows_by_anchor.values():
    rows.sort(key=lambda row: row.get("start", 0))

  words_by_track = defaultdict(list)
  for word in ordered_words:
    words_by_track[word.get("audioSourceId", "")].append(word)
  word_starts_by_track = {}
  for track, rows in words_by_track.items():
    rows.sort(key=lambda row: row.get("start", 0))
    word_starts_by_track[track] = [row["start"] for row in rows]

  # DOM reading order, so an anchor's neighbours are the ones the listener hears
  # next to it.  Keys are the ``text/<spine entry>`` spelling the timeline uses
  # in its ``document`` field, which is what ``prepare_documents`` records on
  # every fragment; ``documents`` itself is keyed by the bare spine entry.
  # ``prepare_documents`` walks the spine in reading order, so its dict order is
  # the order a listener hears these documents in.
  #
  # One pass builds everything the loop below needs: the anchors in order, each
  # anchor's sibling anchors, and the nearest located anchor on either side.
  # Scanning per anchor instead is quadratic on a book with tens of thousands of
  # segments, which is what a long novel looks like.
  flat = []
  siblings_of = {}
  for doc_index, (name, soup) in enumerate(documents.items()):
    doc_key = f"text/{name}"
    doc_located = located.get(doc_key, set())
    for element in soup.find_all(True, id=True):
      ident = element["id"]
      if not (SEGMENT_SPAN_ID.search(ident) or BLOCK_ANCHOR_ID.match(ident)):
        continue
      parent = element.parent
      if parent is not None and parent.name in BLOCK_TAGS:
        siblings_of.setdefault(id(parent), []).append(ident)
      # A wrapper around other anchors is a container, not an anchor itself --
      # unless the timeline addresses it directly, in which case it is both.
      if ident not in doc_located and any(
          SEGMENT_SPAN_ID.search(child["id"]) or BLOCK_ANCHOR_ID.match(child["id"])
          for child in element.find_all(True, id=True, recursive=False)):
        continue
      flat.append((doc_index, doc_key, len(flat), ident, element,
                   id(parent) if parent is not None else None))

  previous_located = [None] * len(flat)
  following_located = [None] * len(flat)
  last = None
  for index, (_, doc_key, _, ident, _, _) in enumerate(flat):
    previous_located[index] = last
    if ident in located.get(doc_key, ()):
      last = ident
  last = None
  for index in range(len(flat) - 1, -1, -1):
    _, doc_key, _, ident, _, _ = flat[index]
    following_located[index] = last
    if ident in located.get(doc_key, ()):
      last = ident

  additions = []
  claimed = {}
  for flat_index, (doc_index, doc_key, position, ident, element, parent_id) in enumerate(flat):
    if ident in located.get(doc_key, set()):
      continue
    element_text = element.get_text(" ", strip=True)
    anchor_tokens = tokens(element_text)
    if len(anchor_tokens) < MIN_GAP_MATCH_WORDS:
      continue
    norm_anchor = {normalize_token(t) for t in anchor_tokens if normalize_token(t)}
    if len(norm_anchor) < MIN_GAP_MATCH_WORDS:
      continue
    # A sentence whose siblings inside the same block did match is bounded by
    # that block's own span, not by the surrounding anchors: the block already
    # owns those seconds and the sentence is spoken inside them.  Otherwise fall
    # back to the silence between the nearest located anchors on either side.
    candidates = []
    siblings = [row for sibling in siblings_of.get(parent_id, ()) if sibling != ident
                for row in rows_by_anchor.get(sibling, [])]
    if siblings:
      tracks = {row.get("audioSourceId", "") for row in siblings}
      if len(tracks) == 1:
        candidates.append((tracks.pop(),
                           min(row.get("start", 0) for row in siblings),
                           max(row.get("end", 0) for row in siblings)))
    previous = rows_by_anchor.get(previous_located[flat_index] or "", [])
    following = rows_by_anchor.get(following_located[flat_index] or "", [])
    track = previous[0].get("audioSourceId", "") if previous else ""
    if previous and following and all(row.get("audioSourceId", "") == track for row in following):
      candidates.append((track,
                         max(row.get("end", 0) for row in previous),
                         min(row.get("start", 0) for row in following)))
    if previous and all(row.get("audioSourceId", "") == track for row in previous):
      # The next located anchor can sit earlier on the track: end matter such as
      # an index or a colophon is read back at the front of the book, so the
      # following document is not necessarily the following audio.  Whenever the
      # neighbour window is empty or reversed, fall back to a bounded distance
      # past the predecessor -- bounded so a stray match is never hunted for
      # across the whole recording.
      trailing_start = max(row.get("end", 0) for row in previous)
      neighbour_end = min((row.get("start", 0) for row in following), default=None)
      if neighbour_end is None or neighbour_end <= trailing_start:
        candidates.append((track, trailing_start, trailing_start + MAX_TRAILING_GAP_SECONDS))

    matched = None
    for track, gap_start, gap_end in candidates:
      if gap_end <= gap_start:
        continue
      # The bounds come from the page, but a segment belonging to some other
      # document can still occupy part of that stretch.  Trim the window to the
      # free intervals so the anchor can only land in real silence.
      windows = _free_windows(occupied_by_track.get(track, ((), ())), gap_start, gap_end,
                              claimed.get(track, ()))
      if not windows:
        continue
      track_words = words_by_track.get(track, [])
      word_starts = word_starts_by_track.get(track, [])
      words = []
      for lo, hi in windows:
        lo_index = bisect_left(word_starts, lo)
        hi_index = bisect_right(word_starts, hi)
        for word in track_words[lo_index:hi_index]:
          if lo < word["end"] and word["start"] < hi:
            words.append(word)
      if not words:
        continue
      norm_words = {normalize_token(w.get("word") or "") for w in words}
      if len(norm_anchor & norm_words) < MIN_GAP_MATCH_WORDS:
        continue
      matched = _align_anchor_within(element, words, windows, anchor_tokens=anchor_tokens)
      if matched is not None:
        break
    if matched is None:
      continue
    start, end, matched_words = matched
    addition = {
      "audioSourceId": track,
      "start": round(start, 2),
      "end": round(end, 2),
      "document": doc_key,
      "fragment": ident,
      "sourceSentenceFragment": ident,
      "text": element_text,
      "occurrenceId": f"gap:{doc_index}:{position}",
      "timingStatus": "SENTENCE_EXACT" if matched_words >= 2 else "SENTENCE_PARTIAL",
    }
    additions.append(addition)
    # Claim the stretch at once, so two anchors inside one long silence cannot
    # both be handed the same seconds.
    claimed.setdefault(track, []).append((start, end))
  return additions


BLOCK_TAGS = frozenset(("p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "figcaption"))
SEGMENT_SPAN_ID = re.compile(r"segment\d+$")
BLOCK_ANCHOR_ID = re.compile(r"^(?:c?fast-|_idContainer)")
MIN_GAP_MATCH_RATIO = 0.75
MIN_GAP_MATCH_WORDS = 2
SHORT_ANCHOR_WORDS = 3
MAX_TRAILING_GAP_SECONDS = 30.0


def _free_windows(spans, low, high, extra=()):
  """Intervals inside [low, high] that no existing segment occupies.

  ``spans`` is a per-track ``(starts, ends)`` index sorted by start, so a lookup
  touches only the segments near the window instead of the whole track.  Books
  with tens of thousands of segments otherwise spend minutes here.
  """
  starts, ends = spans
  first = bisect_left(ends, low)
  last = bisect_right(starts, high)
  occupied = sorted(zip(starts[first:last], ends[first:last]))
  for start, end in extra:
    if end > low and start < high:
      occupied.append((max(low, start), min(high, end)))
  occupied.sort()
  windows = []
  cursor = low
  for start, end in occupied:
    if end <= cursor:
      continue
    if start > cursor:
      windows.append((cursor, start))
    cursor = end
    if cursor >= high:
      break
  if cursor < high:
    windows.append((cursor, high))
  return windows


def _align_anchor_within(element, words, windows, anchor_tokens=None):
  """Locate an anchor inside the free windows using the same lexical evidence.

  The match is accepted only when every word it claims sits inside one window;
  a match that reaches across an occupied stretch is a coincidence, not the
  anchor's own audio.
  """
  if anchor_tokens is None:
    text = element.get_text(" ", strip=True)
    anchor_tokens = tokens(text)
  if len(anchor_tokens) < MIN_GAP_MATCH_WORDS:
    return None
  audio_tokens = [normalize_token(word.get("word") or "") for word in words]
  matcher = SequenceMatcher(None, anchor_tokens, audio_tokens, autojunk=False)
  matched = [block for block in matcher.get_matching_blocks() if block.size]
  if not matched:
    return None
  covered = sum(block.size for block in matched)
  # A three-word anchor -- a URL line, a short heading -- has no room for a
  # ratio test: ASR misspells one proper noun and the ratio collapses below any
  # threshold worth setting.  Those anchors are accepted on the absolute count
  # their neighbours already establish; longer ones must also clear the ratio.
  if covered < MIN_GAP_MATCH_WORDS:
    return None
  if len(anchor_tokens) > SHORT_ANCHOR_WORDS and covered / len(anchor_tokens) < MIN_GAP_MATCH_RATIO:
    return None
  first = min(block.b for block in matched)
  last = max(block.b + block.size - 1 for block in matched)
  start, end = words[first]["start"], words[last]["end"]
  if end <= start:
    return None
  if not any(lo <= start and end <= hi for lo, hi in windows):
    return None
  return start, end, covered


def merge_stream_projection_with_paragraph_fallback(projected, paragraph_refinement):
  """Keep global lexical hits and add only paragraph-local sentence fallbacks."""
  projected_by_sentence = defaultdict(list)
  for seg_idx, seg in enumerate(projected):
    projected_by_sentence[(seg.get("audioSourceId"), seg.get("document"), seg.get("fragment"))].append(seg)

  fallbacks = []
  for coarse in paragraph_refinement:
    source_fragment = coarse.get("sourceSentenceFragment") or coarse.get("fragment")
    key = (coarse.get("audioSourceId"), coarse.get("document"), source_fragment)
    exact = [seg for seg in projected_by_sentence.get(key, [])
      if seg.get("end", 0) > coarse.get("start", 0) and seg.get("start", 0) < coarse.get("end", 0)]
    if not exact:
      fallbacks.append(coarse)
  disjoint_fallbacks = []
  for fallback in sorted(fallbacks, key=lambda row: (row.get("audioSourceId", ""), row.get("start", 0))):
    prior = disjoint_fallbacks[-1] if disjoint_fallbacks else None
    if prior and prior.get("audioSourceId") == fallback.get("audioSourceId") and fallback["start"] < prior["end"]:
      same_anchor = prior.get("document") == fallback.get("document") and prior.get("fragment") == fallback.get("fragment")
      if same_anchor:
        prior["end"] = max(prior["end"], fallback["end"])
        continue
      fallback = {**fallback, "start": prior["end"]}
      if fallback["end"] <= fallback["start"]:
        continue
    disjoint_fallbacks.append(fallback)
  fallbacks = disjoint_fallbacks
  # A global hit can land inside an independently located paragraph's coarse
  # interval. Preserve that observed interval but use the coarse paragraph DOM
  # anchor, avoiding both a false fine anchor and overlapping timeline rows.
  fallback_tracks = defaultdict(list)
  for idx, fallback in enumerate(fallbacks):
    fallback_tracks[fallback.get("audioSourceId")].append((idx, fallback))
  fallback_intervals = {
    sid: ([row.get("start", 0) for _, row in rows], [row.get("end", 0) for _, row in rows])
    for sid, rows in fallback_tracks.items()
  }
  consumed = set()
  merged = []
  for seg_idx, seg in enumerate(projected):
    sid = seg.get("audioSourceId")
    starts, ends = fallback_intervals.get(sid, ([], []))
    # Fallbacks are already disjoint and sorted within each track. Preserve
    # their original order so equal-overlap ties still choose the first row.
    overlaps = fallback_tracks.get(sid, [])[bisect_right(ends, seg.get("start", 0)):
                                             bisect_left(starts, seg.get("end", 0))]
    if overlaps:
      idx, fallback = max(overlaps, key=lambda row: min(seg["end"], row[1]["end"])-max(seg["start"], row[1]["start"]))
      consumed.update(index for index, _ in overlaps)
      merged.append({**seg, "document": fallback["document"], "fragment": fallback["fragment"],
        "text": fallback.get("text", seg.get("text", "")),
        "occurrenceId": f"{fallback.get('occurrenceId', '0')}:projected:{seg_idx}",
        "timingStatus": fallback.get("timingStatus", "SENTENCE_FROM_PARAGRAPH"),
        "sourceSentenceFragment": fallback.get("sourceSentenceFragment")})
    else:
      merged.append(seg)
  merged.extend(fallback for idx, fallback in enumerate(fallbacks) if idx not in consumed)
  # Some upstream coarse matches round to a zero-width interval. They are not
  # playable/highlightable evidence and must not reach the strict resolver.
  merged = [seg for seg in merged if isinstance(seg.get("start"), (int, float))
    and isinstance(seg.get("end"), (int, float)) and seg["end"] > seg["start"]]
  ordered = sorted(merged,
    key=lambda seg: (seg.get("audioSourceId", ""), seg.get("start", 0), seg.get("end", 0)))
  seen = set()
  for index, seg in enumerate(ordered):
    key = (seg.get("audioSourceId"), seg.get("document"), seg.get("fragment"), seg.get("occurrenceId", "0"))
    if key in seen:
      base = str(seg.get("occurrenceId", "0"))
      suffix = index
      while (*key[:3], f"{base}:repeat:{suffix}") in seen:
        suffix += 1
      seg["occurrenceId"] = f"{base}:repeat:{suffix}"
      key = (*key[:3], seg["occurrenceId"])
    seen.add(key)
  return ordered
