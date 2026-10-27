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
