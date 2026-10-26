"""Load ASR once and surface environment failures without repeated native imports."""
_backend = None
_error = None


def transcription_backend():
  global _backend, _error
  if _error is not None:
    raise RuntimeError(f"ASR_RUNTIME_UNAVAILABLE: {_error}")
  if _backend is None:
    try:
      # Probe Metal first: importing the larger backend after a failed native
      # initialization can otherwise abort the process with duplicate enums.
      import mlx.core
      from mlx_whisperx.backend.mlx_whisper.transcribe import transcribe
      _backend = transcribe
    except Exception as exc:
      _error = f"{type(exc).__name__}: {exc}"
      raise RuntimeError(f"ASR_RUNTIME_UNAVAILABLE: {_error}") from exc
  return _backend
