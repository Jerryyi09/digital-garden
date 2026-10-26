#!/usr/bin/env python3
"""
Occurrence & Reversible Token Mapping Model (RA-05 Core)

1. Ground Truth preservation: Original text is immutable; normalization is reversible.
2. Token occurrences track exact character offsets in DOM.
3. Allows multi-token range per fragment and cross-track occurrence mapping.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple


@dataclass
class TokenOccurrence:
    token_idx: int
    raw_token: str
    norm_token: str
    char_start: int
    char_end: int


@dataclass
class FragmentMapping:
    document: str
    fragment_id: str
    token_start: int
    token_end: int
    audio_source_id: str
    audio_start: float
    audio_end: float
    matched_ratio: float
    review_status: str = "unreviewed"


def tokenize_reversible(raw_text: str) -> List[TokenOccurrence]:
    """
    Extracts tokens while maintaining exact character offsets to the raw text.
    Reversible: raw_text[char_start:char_end] == raw_token.
    """
    tokens = []
    # Match alphanumeric token sequences
    for m in re.finditer(r"\b[\w'’\-]+\b", raw_text):
        raw_token = m.group(0)
        norm_token = re.sub(r"[^\w]", "", raw_token.lower())
        if norm_token:
            tokens.append(TokenOccurrence(
                token_idx=len(tokens),
                raw_token=raw_token,
                norm_token=norm_token,
                char_start=m.start(),
                char_end=m.end()
            ))
    return tokens


def build_fragment_occurrence_entry(
    document: str,
    fragment_id: str,
    text: str,
    audio_source_id: str,
    start: float,
    end: float,
    matched_words: int,
    total_words: int
) -> Dict[str, Any]:
    """Generates a closed, typed schema fragment entry for timeline.json."""
    ratio = round(matched_words / max(1, total_words), 3)
    return {
        "audioSourceId": audio_source_id,
        "start": round(float(start), 3),
        "end": round(float(end), 3),
        "document": document,
        "fragment": fragment_id,
        "text": text,
        "matchedWordRatio": ratio,
        "reviewStatus": "unreviewed",
        "timingStatus": "TIMING_UNVERIFIED"
    }
