# Converts audio files into .npz so that the ai can
# better learn and understand how different whale
# calls are made, and what to listen for (#10/12)

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from boat_noise_class import (AUDIO_EXTS, load_audio, normalize, pcen_mel,
                              mix_at_snr, split_sources)


# ----------------------------------------------------------------------------
# Annotations
# ----------------------------------------------------------------------------
def read_annotations(src, csv_path):
    """Return {file_path: [(start_s, end_s), ...]}."""
    src = Path(src)
    calls = {}
    if csv_path:
        with open(csv_path, newline="") as fh:
            for row in csv.DictReader(fh):
                f = src / row["file"]
                s, e = float(row["start_s"]), float(row["end_s"])
                if e > s:
                    calls.setdefault(f, []).append((s, e))
    else:
        for f in src.rglob("*"):
            if f.suffix.lower() in AUDIO_EXTS:
                calls[f] = [None]   # None = whole file is the call
    if not calls:
        raise SystemExit("No calls found. Check --src and --annotations.")
    return calls


# ----------------------------------------------------------------------------
# Window extraction
# ----------------------------------------------------------------------------
def fade(x, frac=0.1):
    """Hann fade-in/out so isolated calls do not click when overlaid."""
    n = max(1, int(len(x) * frac))
    ramp = np.hanning(2 * n)
    x = x.copy()
    x[:n] *= ramp[:n]
    x[-n:] *= ramp[n:]
    return x


def isolate_call(y, sr, span, win):
    """Cut the call out of the recording (cropped to the window length)."""
    if span is None:
        seg = y
    else:
        seg = y[int(span[0] * sr):int(span[1] * sr)]
    seg = seg[:win]
    seg = seg - np.mean(seg) if len(seg) else seg
    return fade(seg) if len(seg) > 10 else seg


def natural_window(y, sr, span, win, rng):
    """Window from the original recording with the call at a random position."""
    if span is None:
        start = 0
        seg = y[:win]
    else:
        c0, c1 = int(span[0] * sr), int(span[1] * sr)
        call_len = min(c1 - c0, win)
        lo = max(0, c1 - win)                 # earliest start that still contains the call end
        hi = max(lo, min(c0, len(y) - win))   # latest start that still contains the call start
        start = int(rng.integers(lo, hi + 1)) if hi >= lo else 0
        seg = y[start:start + win]
    if len(seg) < win:
        seg = np.pad(seg, (0, win - len(seg)))
    return seg


# ----------------------------------------------------------------------------
# Builder
# ----------------------------------------------------------------------------
def load_boat_audio(boat_dir, split, win):
    p = Path(boat_dir) / f"boat_noise_{split}.npz"
    if not p.exists():
        return None
    d = np.load(p)
    if "audio" not in d.files:
        raise SystemExit(f"{p} has no raw audio; rerun boat_noise_class.py without --no_audio")
    audio = d["audio"]
    if audio.shape[1] != win:
        raise SystemExit(f"Window mismatch: boat={audio.shape[1]} samples, whale={win}. "
                         "Use the same --sr and --win for both scripts.")
    return audio


def build_whale_class(a):
    rng = np.random.default_rng(a.seed)
    win = int(a.win * a.sr)
    calls = read_annotations(a.src, a.annotations)
    splits = split_sources(list(calls.keys()), seed=a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []

    for split, files in splits.items():
        boat = load_boat_audio(a.boat, split, win) if a.boat else None
        if a.boat and boat is None:
            print(f"[warn] no boat_noise_{split}.npz; skipping synthetic mixes for {split}")
        feats, audio, snrs = [], [], []

        def add(w, kind, f, span, snr=np.nan):
            w = normalize(w)
            feats.append(pcen_mel(w, a.sr, n_mels=a.n_mels, fmin=a.fmin, fmax=a.fmax))
            if not a.no_audio:
                audio.append(w)
            snrs.append(snr)
            manifest.append({"split": split, "source": str(f), "span_s": span,
                             "kind": kind, "snr_db": None if np.isnan(snr) else float(snr),
                             "label": "whale_call"})

        for f in files:
            y = load_audio(f, a.sr)
            for span in calls[f]:
                # natural windows: several random placements of the same call
                for _ in range(a.natural_per_call):
                    add(natural_window(y, a.sr, span, win, rng), "natural", f, span)

                # synthetic windows: isolated call on real boat noise
                if boat is not None and a.synth_per_call:
                    call = isolate_call(y, a.sr, span, win)
                    if len(call) < 10 or np.sqrt(np.mean(call ** 2)) < 1e-6:
                        continue
                    for _ in range(a.synth_per_call):
                        noise = boat[rng.integers(len(boat))]
                        snr = float(rng.uniform(a.snr_min, a.snr_max))
                        mix, _off = mix_at_snr(call, noise, snr, rng)
                        add(mix, "synthetic", f, span, snr)

        if feats:
            np.savez_compressed(
                out / f"whale_call_{split}.npz",
                X=np.stack(feats),
                y=np.ones(len(feats), dtype=np.int64),      # remap to your class index later
                snr=np.array(snrs, dtype=np.float32),       # NaN for natural windows
                **({"audio": np.stack(audio)} if not a.no_audio else {}),
            )
        print(f"{split:5s}: {len(files)} files -> {len(feats)} windows "
              f"({sum(not np.isnan(s) for s in snrs)} synthetic)")

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Manifest written to {out / 'manifest.json'}")


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="folder of whale recordings")
    ap.add_argument("--annotations", help="CSV with file,start_s,end_s")
    ap.add_argument("--boat", help="folder with boat_noise_<split>.npz (for synthetic mixes)")
    ap.add_argument("--out", default= "data/whale_windows", help= "output folder")
    ap.add_argument("--sr", type=int, default=8000)
    ap.add_argument("--win", type=float, default=5.0)
    ap.add_argument("--n_mels", type=int, default=64)
    ap.add_argument("--fmin", type=float, default=20)
    ap.add_argument("--fmax", type=float, default=3500)
    ap.add_argument("--natural_per_call", type=int, default=2)
    ap.add_argument("--synth_per_call", type=int, default=3)
    ap.add_argument("--snr_min", type=float, default=-10)
    ap.add_argument("--snr_max", type=float, default=15)
    ap.add_argument("--no_audio", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    build_whale_class(ap.parse_args())
