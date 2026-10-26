"""Metadata language codes are hints, not audio-language measurements."""


def normalized_language(value):
  if not isinstance(value, str):
    return None
  root = value.strip().lower().replace('_', '-').split('-')[0]
  if root in {'', 'und', 'unknown', 'none', 'null', 'mul', 'zxx'}:
    return None
  return 'en' if root in {'en', 'eng'} else root
