"""Indexed chapter localization followed by bounded lexical matching."""
from bisect import bisect_right
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import hashlib
import re
import unicodedata

from bs4 import BeautifulSoup, Comment, Doctype, ProcessingInstruction
from tools.readalong.authoritative_validator import DOMFragmentExtractor, safe_path
from tools.readalong.exporter import READALONG_CSS_INJECTION
from tools.readalong.engine.mark_sentence import _build_char_map, _create_segment_spans

BLOCKS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "dt", "dd", "td", "th", "div"}


def tokens(text):
  # Normalize matching keys only; never rewrite the rendered source DOM.
  text = text.translate(str.maketrans({"’": "'", "‘": "'", "ʼ": "'"}))
  text = "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))
  return [w.replace("'", "") for w in re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", text)]


def strip_drama_labels(text):
  """Strip non-spoken drama speaker labels, line numbers, and footnote headers from the index token view."""
  if re.fullmatch(r"\s*\d+\s*", text):
    return ""
  if re.match(r"^\s*\d+\.\d+\.\d+\s+", text):
    return ""
  text = re.sub(r"^\s*\d+\s+(?=[A-Z‘'“\"])", "", text)
  if re.fullmatch(r"\s*[A-Z][A-Z0-9\s',\.\-]{0,30}\.?\s*", text):
    return ""
  text = re.sub(r"^\s*(?:[A-Z]{2,}(?:\s+[A-Z]{2,}){0,2})\.?\s+(?=[A-Z‘'“\"])", "", text)
  text = re.sub(r"(?<=[\.\?\!])\s+(?:[A-Z]{2,}(?:\s+[A-Z]{2,}){0,2})\.\s+", " ", text)
  text = re.sub(r"^\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\.\s+(?=[A-Z‘'“\"’])", "", text)
  text = re.sub(r"\(\s*(?:Enter|Exit|Exeunt|Aside|To\s+|Sings|Reads|Within|Draws|Dies|Stabs|Music|Flourish)[^\)]{0,60}\)", " ", text, flags=re.I)
  text = re.sub(r"\[\s*(?:Enter|Exit|Exeunt|Aside|To\s+|Sings|Reads|Within|Draws|Dies|Stabs|Music|Flourish)[^\]]{0,60}\]", " ", text, flags=re.I)
  text = re.sub(r"°\s*\d*", " ", text)
  return text


def is_non_play_apparatus(doc_name, doc_paras):
  """Identify scholarly apparatus/footnote spine docs in multi-document drama editions."""
  if not doc_paras:
    return True
  if len(doc_paras) <= 2 and re.match(r"^\s*\d+", doc_paras[0]["text"]):
    return True
  lower_name = doc_name.lower()
  if any(k in lower_name for k in ("commentary", "account", "chronology", "further_reading", "ftn", "_bm", "copyright", "endpage", "abouttheauthor", "globalbackad")):
    return True
  first_txt = doc_paras[0]["text"].strip().lower()
  if first_txt in (
      "commentary", "commentaries", "an account of the text", "suggested references",
      "general introduction", "note on the text", "publisher’s note", "publisher's note",
      "william shakespeare of stratford-upon-avon, gentleman", "the play in performance",
      "the theatrical world", "the texts of shakespeare", "the question of authorship",
  ):
    return True
  return False


def visible(node):
  return not isinstance(node, (Comment, Doctype, ProcessingInstruction)) and bool(node.strip()) and not any(
    p.name in {"head", "script", "style", "noscript"} or p.has_attr("hidden")
    or re.search(r"display\s*:\s*none|visibility\s*:\s*hidden", p.get("style", ""), re.I)
    for p in node.parents)


def prepare_paragraphs(root, spine, diagnostics=None):
  """Keep original inline DOM; mark leaf blocks and uncovered mixed-flow text."""
  docs, paragraphs, book_tokens, prepared = {}, [], [], {}
  diagnostics = diagnostics if diagnostics is not None else []
  for occurrence, name in enumerate(spine):
    if name in docs:
      # Prepare physical DOM once, but retain every reading-order occurrence.
      prior_paras, prior_tokens = prepared[name]
      base = len(book_tokens)
      paragraphs.extend({**p, "offset": base+p["offset"], "spineOccurrence": occurrence} for p in prior_paras)
      book_tokens.extend(prior_tokens)
      diagnostics.append({"reason": "REUSED_SPINE_DOCUMENT", "document": name, "spineOccurrence": occurrence})
      continue
    base, first = len(book_tokens), len(paragraphs)
    soup = BeautifulSoup(safe_path(root, name).read_text(encoding="utf-8"), "html.parser")
    ids = [n["id"] for n in soup.find_all(id=True)]
    used_ids, seen = set(ids), set()
    originals = set()
    for ordinal, node in enumerate(soup.find_all(id=True)):
      original = node["id"]
      if original in originals:
        ident = "fast-repair-"+hashlib.sha256(f"{name}:{ordinal}:{original}".encode()).hexdigest()[:20]
        while ident in used_ids:
          ident += "x"
        node["id"] = ident
        node["data-readalong-original-id"] = original
        used_ids.add(ident)
        diagnostics.append({"reason": "DUPLICATE_SOURCE_ID_RENAMED", "document": name,
          "originalId": original, "candidateId": ident,
          "linkPolicy": "Original fragment links retain the browser's first-target behavior; source ambiguity is not resolved"})
      originals.add(original)
    # Compute block ancestry once, rather than rescanning subtrees per text node.
    nonleaf = set()
    for block in soup.find_all(BLOCKS):
      for parent in block.parents:
        if parent.name in BLOCKS:
          nonleaf.add(id(parent))
    contexts = [b for b in soup.find_all(BLOCKS) if id(b) not in nonleaf]
    context_ids = {id(b) for b in contexts}
    for node in list((soup.body or soup).find_all(string=True)):
      if not visible(node):
        continue
      owner = next((p for p in node.parents if id(p) in context_ids), None)
      if owner is None:
        owner = soup.new_tag("span")
        node.wrap(owner)
        contexts.append(owner)
        context_ids.add(id(owner))
    # A publisher may put an entire chapter in one paragraph/div. Split only
    # oversized contexts using the existing DOM-preserving reconstruction, not
    # the expensive whole-book sentence tokenizer or proportional timestamps.
    for ordinal, owner in enumerate(contexts):
      text = owner.get_text("")
      word_matches = list(re.finditer(r"\S+", text))
      if len(word_matches) <= 160:
        continue
      if len(text) > 2_000_000:
        raise ValueError("Oversized text block needs input review")
      char_map, linear, zero_nodes = _build_char_map(owner)
      word_matches = list(re.finditer(r"\S+", linear))
      prefix = "fast-long-"+hashlib.sha256((name+str(ordinal)).encode()).hexdigest()[:16]+"-"
      while any(ident.startswith(prefix) for ident in used_ids):
        prefix += "x"
      boundaries = [(0 if i == 0 else word_matches[i].start(),
                     word_matches[i+80].start() if i+80 < len(word_matches) else len(linear))
                    for i in range(0, len(word_matches), 80)]
      spans = _create_segment_spans(boundaries, char_map, zero_nodes, prefix, 0)
      can_split_siblings = owner.name in {"p", "div", "blockquote", "li"} and owner.parent is not None
      tag_name = owner.name if owner.name in BLOCKS else "p"
      blocks = []
      for idx, span in enumerate(spans):
        block = soup.new_tag(tag_name, attrs=dict(owner.attrs))
        block["id"] = f"{prefix}{idx}"
        for child in list(span.children):
          block.append(child.extract())
        blocks.append(block)
      if can_split_siblings:
        for block in blocks:
          owner.insert_before(block)
          context_ids.add(id(block))
          used_ids.add(block["id"])
        context_ids.remove(id(owner))
        owner.decompose()
      else:
        owner.clear()
        for block in blocks:
          owner.append(block)
          context_ids.add(id(block))
          used_ids.add(block["id"])
        context_ids.remove(id(owner))
    for node in list((soup.body or soup).find_all(string=True)):
      if not visible(node):
        continue
      owner = next((p for p in node.parents if id(p) in context_ids), None)
      if owner is None:
        raise ValueError("Visible text is outside paragraph contexts")
      if id(owner) in seen:
        continue
      seen.add(id(owner))
      if not owner.get("id"):
        ident = "fast-" + hashlib.sha256((name+":"+str(len(paragraphs))).encode()).hexdigest()[:20]
        while ident in used_ids:
          ident += "x"
        owner["id"] = ident
        used_ids.add(ident)
      parser = DOMFragmentExtractor()
      parser.feed(str(owner))
      parser.close()
      text = parser.id_to_text.get(owner["id"], "")
      raw_visible = "".join(str(n) for n in owner.find_all(string=True) if visible(n))
      text_tokens = tokens(strip_drama_labels(raw_visible))
      if not text_tokens:
        continue
      paragraphs.append({"document": "text/"+name, "fragment": owner["id"], "text": text,
                         "offset": len(book_tokens), "length": len(text_tokens),
                         "tokens": text_tokens, "spineOccurrence": occurrence})
      book_tokens.extend(text_tokens)
    if not soup.head:
      head = soup.new_tag("head")
      (soup.html or soup).insert(0, head)
    style = soup.new_tag("style")
    style["data-readalong-fast"] = "paragraph-context"
    style.string = READALONG_CSS_INJECTION
    soup.head.append(style)
    docs[name] = soup
    prepared[name] = ([{**p, "offset": p["offset"]-base} for p in paragraphs[first:]], book_tokens[base:].copy())
  if len(docs) > 3:
    by_doc = defaultdict(list)
    for p in paragraphs:
      by_doc[p["document"]].append(p)
    apparatus_docs = {d for d, ps in by_doc.items() if is_non_play_apparatus(d, ps)}
    # In drama editions that have apparatus docs, also exclude scholarly Introductions that quote the play
    if apparatus_docs:
      for d, ps in by_doc.items():
        if "introduction" in d.lower() or (ps and ps[0]["text"].strip().lower() in ("introduction", "about the author")):
          apparatus_docs.add(d)
      kept_paras, kept_tokens = [], []
      for p in paragraphs:
        if p["document"] in apparatus_docs:
          continue
        ptoks = p.get("tokens") or tokens(strip_drama_labels(p["text"]))
        kept_paras.append({k: v for k, v in {**p, "offset": len(kept_tokens), "length": len(ptoks)}.items() if k != "tokens"})
        kept_tokens.extend(ptoks)
      if kept_tokens:
        paragraphs, book_tokens = kept_paras, kept_tokens
  for p in paragraphs:
    p.pop("tokens", None)
  if not book_tokens:
    raise ValueError("No visible English book tokens")
  return docs, paragraphs, book_tokens


class ParagraphIndex:
  """Never run SequenceMatcher over the entire book or entire audio stream."""
  def __init__(self, book_tokens, paragraphs):
    self.book = book_tokens
    self.paragraphs = paragraphs
    self.offsets = [p["offset"] for p in paragraphs]
    self.index = defaultdict(list)
    self.gram3 = defaultdict(list)
    self.metrics = Counter()
    self.last_diagnostic = {}
    for pos in range(max(0, len(book_tokens)-4)):
      gram = tuple(book_tokens[pos:pos+5])
      # Common phrases are not useful global location evidence.
      if len(self.index[gram]) <= 32:
        self.index[gram].append(pos)
    for pos in range(max(0, len(book_tokens)-2)):
      g3 = tuple(book_tokens[pos:pos+3])
      if len(self.gram3[g3]) <= 64:
        self.gram3[g3].append(pos)

  def _paragraph_for(self, candidate):
    counts = Counter()
    for start, size in candidate["matches"]:
      for pos in range(start, start+size):
        counts[max(0, bisect_right(self.offsets, pos)-1)] += 1
    return self.paragraphs[counts.most_common(1)[0][0]]

  def _enhanced_fallback(self, query, cursor, has_context):
    if len(query) < 3 or len(query) > 180:
      return None
    windows = []
    if has_context:
      windows.append((max(0, cursor-120), min(len(self.book), cursor+max(len(query)*2, 180))))
      windows.append((max(0, cursor-220), min(len(self.book), cursor+400)))
    if len(query) >= 6:
      votes3 = Counter()
      for i in range(max(0, len(query)-2)):
        pts = self.gram3.get(tuple(query[i:i+3]), ())
        if pts:
          for pos in pts:
            b = max(0, pos-i)//24*24
            votes3[b] += 1/len(pts)
      for b, _ in votes3.most_common(6):
        windows.append((max(0, b-24), min(len(self.book), b+len(query)*2+48)))
    if not windows:
      return None
    q_str = " ".join(query)
    # Reuse the fixed query index across candidate windows.
    token_matcher = SequenceMatcher(None, [], query, autojunk=False)
    char_matcher = SequenceMatcher(None, "", q_str, autojunk=False)
    candidates = []
    for lo, hi in dict.fromkeys(windows):
      if hi <= lo or hi-lo > 520:
        continue
      is_local = has_context and lo <= cursor+220 and hi >= cursor-130
      if len(query) < 12 and not is_local:
        continue
      self.metrics["windowComparisons"] += 1
      self.metrics["comparedBookTokens"] += hi-lo
      token_matcher.set_seq1(self.book[lo:hi])
      blocks = [b for b in token_matcher.get_matching_blocks() if b.size]
      if not blocks:
        continue
      matched = sum(b.size for b in blocks)
      unique_q_matched = matched
      if len(query) >= 4:
        b_start, b_end = lo+blocks[0].a, lo+blocks[-1].a+blocks[-1].size
        span_toks = set(self.book[max(lo, b_start-2):min(hi, b_end+2)])
        explained = sum(1 for w in query if w in span_toks)
        # Only count repeated-line coverage when at least 2 distinct blocks or high unique coverage
        if explained > unique_q_matched and b_end-b_start <= len(query)+16 and len(span_toks & set(query)) >= min(4, len(set(query))):
          unique_q_matched = explained
      ratio = unique_q_matched/len(query)
      best_slice = None
      if is_local:
        best_char_sim = 0.0
        for blk in blocks:
          s0 = max(lo, min(hi-1, lo+blk.a-blk.b))
          e0 = min(hi, s0+max(1, len(query)))
          sub_str = " ".join(self.book[s0:e0])
          char_matcher.set_seq1(sub_str)
          cs = char_matcher.ratio()
          if cs > best_char_sim:
            best_char_sim = cs
            best_slice = (s0, e0)
        if best_char_sim >= 0.58 and best_char_sim*0.88 > ratio:
          ratio = best_char_sim*0.88
      min_ratio = 0.46 if is_local else 0.68
      if not is_local and max(b.size for b in blocks) < 4 and unique_q_matched < len(query)*0.75:
        continue
      if ratio >= min_ratio:
        start, end = lo+blocks[0].a, lo+blocks[-1].a+blocks[-1].size
        if end-start > max(len(query)*2.4, len(query)+24) and best_slice is not None:
          start, end = best_slice
        if len(query) < 12 and not (has_context and cursor-120 <= start <= cursor+200):
          continue
        if end-start > max(len(query)*2.4, len(query)+24):
          continue
        match_spans = [(lo+b.a, b.size) for b in blocks if lo+b.a >= start and lo+b.a < end] or [(start, max(1, end-start))]
        eff_score = ratio+(0.18 if is_local else 0.0)
        candidates.append({"start": start, "end": end, "score": min(1.0, ratio), "eff_score": eff_score,
                           "matched": unique_q_matched, "matches": match_spans, "is_local": is_local})
    if not candidates:
      return None
    c0 = cursor if has_context else 0
    candidates.sort(key=lambda c: (c["eff_score"], -abs(c["start"]-c0)), reverse=True)
    best = candidates[0]
    target = self._paragraph_for(best)
    if not best["is_local"]:
      competitors = [c for c in candidates[1:] if abs(c["start"]-best["start"]) > max(32, len(query))
                     and c["score"] >= best["score"]-.03
                     and (self._paragraph_for(c)["document"], self._paragraph_for(c)["fragment"]) != (target["document"], target["fragment"])]
      if competitors:
        self.metrics["ambiguousUnits"] += 1
        self.last_diagnostic["reason"] = "AMBIGUOUS_MATCH"
        return None
    self.last_diagnostic.update(reason="MATCHED", score=best["score"],
      document=target["document"], fragment=target["fragment"],
      locationMode="LOCAL_CONTEXT" if best["is_local"] else "GLOBAL_ANCHOR")
    return {k: v for k, v in {**best, "paragraph": target, "contextOnly": True}.items() if k not in ("eff_score", "is_local")}

  def locate(self, heard, cursor=None):
    has_context = cursor is not None
    cursor = cursor if has_context else 0
    query = tokens(heard)
    self.last_diagnostic = {"reason": "UNRESOLVED", "queryTokens": len(query),
                            "hasContext": has_context, "rejections": {}}
    def miss(reason):
      self.last_diagnostic["reason"] = reason
      return None
    if not query or len(query) > 180:
      return miss("EMPTY_QUERY" if not query else "QUERY_TOO_LONG")
    votes = Counter()
    seed_starts = defaultdict(list)
    for i in range(max(0, len(query)-4)):
      positions = self.index.get(tuple(query[i:i+5]), ())
      if len(positions) > 32:
        continue
      for pos in positions:
        # Cluster nearby offsets, tolerating a few ASR insertions/deletions.
        bucket = max(0, pos-i)//32*32
        votes[bucket] += 1/len(positions)
        seed_starts[bucket].append(max(0, pos-i))
    near = [v for v, _ in votes.most_common() if cursor-160 <= v <= cursor+2000]
    global_positions = [v for v, _ in votes.most_common(8)]
    self.last_diagnostic["anchorBuckets"] = len(votes)
    if not votes and len(query) < 12:
      # A short phrase needs unique local context, not a global best guess.
      if not has_context:
        return miss("SHORT_QUERY_WITHOUT_CONTEXT")
      lo, hi = max(0, cursor-24), min(len(self.book)-len(query)+1, cursor+80)
      exact = [i for i in range(lo, hi) if self.book[i:i+len(query)] == query]
      if len(exact) == 1 and len(query) >= 3:
        positions = exact
      else:
        fb = self._enhanced_fallback(query, cursor, has_context)
        if fb is not None:
          return fb
        return miss("NO_SAFE_LOCAL_SHORT_MATCH")
    else:
      positions = list(dict.fromkeys(near[:3]+global_positions))
    if not positions:
      fb = self._enhanced_fallback(query, cursor, has_context)
      if fb is not None:
        return fb
      return miss("NO_RELIABLE_ANCHOR")
    candidates = []
    rejections = Counter()
    token_matcher = SequenceMatcher(None, [], query, autojunk=False)
    for guess in positions:
      # Exact n-gram seeds estimate the query origin more accurately than the
      # quantized vote bucket. Try their bounded neighborhood first so isolated
      # common words far before the anchor cannot inflate a correct match span.
      seeds = sorted(seed_starts.get(guess, [guess]))
      origin = seeds[len(seeds)//2]
      windows = [(max(0, origin-8), min(len(self.book), origin+len(query)+16)),
                 (max(0, guess-48), min(len(self.book), guess+len(query)+96))]
      # Cap pathological long ASR segments. The caller splits only when real
      # word boundaries exist; otherwise an oversized segment remains unlocated.
      for lo, hi in dict.fromkeys(windows):
        if len(query) > 180 or hi-lo > 400:
          continue
        self.metrics["windowComparisons"] += 1
        self.metrics["comparedBookTokens"] += hi-lo
        token_matcher.set_seq1(self.book[lo:hi])
        blocks = [b for b in token_matcher.get_matching_blocks() if b.size]
        matched = sum(b.size for b in blocks)
        if not blocks or matched/max(1, len(query)) < .72:
          rejections["LOW_LEXICAL_MATCH"] += 1
          continue
        start, end = lo+blocks[0].a, lo+blocks[-1].a+blocks[-1].size
        if len(query) < 12 and (not has_context or not cursor-24 <= start <= cursor+80):
          rejections["SHORT_GLOBAL_RELOCATION_UNSAFE"] += 1
          continue
        if end-start > max(len(query)*1.8, len(query)+12):
          rejections["SPAN_TOO_WIDE"] += 1
          continue
        if len(query) >= 12 and max(b.size for b in blocks) < 5:
          rejections["INSUFFICIENT_CONTIGUOUS_MATCH"] += 1
          continue
        score = matched/len(query)
        candidates.append({"start": start, "end": end, "score": score, "matched": matched,
                           "matches": [(lo+b.a, b.size) for b in blocks]})
        break
    self.last_diagnostic.update(candidateCount=len(candidates), rejections=dict(rejections))
    if not candidates:
      fb = self._enhanced_fallback(query, cursor, has_context)
      if fb is not None:
        return fb
      return miss("CANDIDATE_REJECTED")
    candidates.sort(key=lambda c: (c["score"], -abs(c["start"]-cursor)), reverse=True)
    best = candidates[0]
    target = self._paragraph_for(best)
    competitors = [c for c in candidates[1:] if abs(c["start"]-best["start"]) > max(32, len(query))
                   and c["score"] >= best["score"]-.03
                   and (self._paragraph_for(c)["document"], self._paragraph_for(c)["fragment"]) != (target["document"], target["fragment"])]
    if competitors:
      # Only prior playback continuity can disambiguate equal repeated wording.
      local = [c for c in [best]+competitors if cursor-24 <= c["start"] <= cursor+80]
      if not has_context or len({c["start"] for c in local}) != 1:
        self.metrics["ambiguousUnits"] += 1
        return miss("AMBIGUOUS_MATCH")
      best = local[0]
    # If cursor is known and best jumped >1500 tokens away, check if there is a strong local match first
    if has_context and abs(best["start"]-cursor) > 1500 and best["score"] < 0.88:
      fb = self._enhanced_fallback(query, cursor, has_context)
      if fb is not None and abs(fb["start"]-cursor) <= 220:
        return fb
    para = self._paragraph_for(best)
    self.last_diagnostic.update(reason="MATCHED", score=best["score"],
      document=para["document"], fragment=para["fragment"],
      locationMode="LOCAL_CONTEXT" if has_context and cursor-24 <= best["start"] <= cursor+80 else "GLOBAL_ANCHOR")
    return {**best, "paragraph": para, "contextOnly": True}

  def locate_detailed(self, heard, cursor=None):
    """Expose bounded evidence, not an unsupported material-mismatch verdict."""
    match = self.locate(heard, cursor)
    return {"match": match, "diagnostic": dict(self.last_diagnostic)}
