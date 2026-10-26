"""Verify batched decoding on one real 1800s block: global time reconstruction, monotonicity,
normalize_native verdicts, determinism, batch-composition invariance. Read-only; writes nothing."""
import hashlib, json, subprocess, sys, time
from collections import Counter
import numpy as np
sys.path.insert(0, "/Users/jerryyi/digital-garden")
from tools.readalong.config import resolve_model_path
from tools.readalong_fast.pipeline import normalize_native
from mlx_whisperx.backend.mlx_whisper.transcribe import transcribe, transcribe_chunks_batched
from mlx_whisperx.backend.mlx_whisper.tokenizer import get_tokenizer

AUDIO, START, DUR = sys.argv[1], float(sys.argv[2]), 1800.0
MODEL = str(resolve_model_path())
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(START), "-i", AUDIO, "-t", str(DUR), "-map", "0:a:0",
                      "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "pipe:1"], capture_output=True, check=True).stdout
pcm = np.frombuffer(raw, dtype="<f4").copy()
END = START + len(pcm) / 16000
tok = get_tokenizer(False, language="en"); TB, EOT = tok.timestamp_begin, tok.eot
KW = dict(path_or_hf_repo=MODEL, language="en", word_timestamps=False, fp16=True)

def cuts(x, target=28.0, search=6.0, hop=0.05):
    out, pos, w = [0], 0, int(hop*16000)
    while len(x)-pos > 30*16000:
        lo, hi = pos+int((target-search)*16000), pos+int(target*16000)
        f = x[lo:hi][:(hi-lo)//w*w].reshape(-1, w)
        pos = lo+int(np.argmin((f**2).mean(1)))*w+w//2
        out.append(pos)
    return out

def rebuild(out, bounds):
    """Timestamp tokens are window-relative; add the window's own start. A timestamp
    past the window's real PCM length is a prediction into padding, not observed audio."""
    rows, beyond = [], 0
    for o, (a, b) in zip(out, bounds):
        off, wl = a/16000, (b-a)/16000
        cur, s = [], None
        for t in o["tokens"]:
            if t >= TB:
                ts = (t-TB)*0.02
                if s is None or not cur: s = ts
                else:
                    rows.append([off+s, off+ts, tok.decode(cur), off+wl]); cur, s = [], ts
            elif t < EOT:
                cur.append(t)
        if cur:  # text with no closing timestamp: keep as untrusted, bounded by real PCM
            rows.append([off+(s or 0), off+wl, tok.decode(cur), off+wl, "open"])
    segs = []
    for r in rows:
        a, b, text, wend = r[0], r[1], r[2], r[3]
        if b > wend+1e-6: beyond += 1
        segs.append({"start": START+a, "end": START+min(b, wend), "text": text,
                     **({"timingRejected": True} if len(r) > 4 else {})})
    return segs, beyond

def report(name, segs, beyond=0):
    viol = sum(1 for p, q in zip(segs, segs[1:]) if q["start"] < p["end"]-1e-6)
    cover = sum(s["end"]-s["start"] for s in segs)
    clean, diag = normalize_native([dict(s) for s in segs], START, END)
    reasons = Counter(d["reason"] for d in diag)
    lost = sum(s["end"]-s["start"] for s in clean if s.get("timingRejected"))
    sha = hashlib.sha256(json.dumps([[round(s["start"], 3), round(s["end"], 3), s["text"]] for s in segs]).encode()).hexdigest()[:12]
    print(f"{name:<22} segs={len(segs):4d} cover={cover:7.1f}s/{END-START:.0f}s overlaps={viol:3d} "
          f"pastWindowEnd={beyond:3d} untrusted={reasons.get('UNTRUSTED_BOUNDARY_OR_OVERLAP',0):3d} "
          f"untrustedSec={lost:5.1f} reasons={dict(reasons)} sha={sha}")
    return sha

transcribe(pcm[:480000], condition_on_previous_text=False, verbose=None, **KW)
t = time.perf_counter()
ser = transcribe(pcm, condition_on_previous_text=False, verbose=None, **KW)["segments"]
st = time.perf_counter()-t
report(f"serial {DUR/st:.0f}x", [{"start": START+s["start"], "end": START+s["end"], "text": s["text"]} for s in ser])

c = cuts(pcm); bounds = list(zip(c, c[1:]+[len(pcm)]))
chunks = [pcm[a:b] for a, b in bounds]
print(f"windows={len(chunks)} len min/max={min(b-a for a,b in bounds)/16000:.1f}/{max(b-a for a,b in bounds)/16000:.1f}s nonOverlapping=True")
shas = []
for run in range(3):
    t = time.perf_counter()
    out = transcribe_chunks_batched(chunks, batch_size=16, **KW)
    dt = time.perf_counter()-t
    segs, beyond = rebuild(out, bounds)
    shas.append(report(f"silence-b16 run{run} {DUR/dt:.0f}x", segs, beyond))
print("deterministic across 3 runs:", len(set(shas)) == 1)
out8 = transcribe_chunks_batched(chunks, batch_size=8, **KW)
s8, b8 = rebuild(out8, bounds)
print("batch8 == batch16:", report("silence-b8", s8, b8) == shas[0])

# Reproduce the reported failure mode: overlapping 30s windows at 25s stride, no dedup
ov = [(i, min(i+480000, len(pcm))) for i in range(0, len(pcm), 400000)]
outo = transcribe_chunks_batched([pcm[a:b] for a, b in ov], batch_size=16, **KW)
so, bo = rebuild(outo, ov)
so.sort(key=lambda s: s["start"])
report(f"overlap25s n={len(ov)}", so, bo)
