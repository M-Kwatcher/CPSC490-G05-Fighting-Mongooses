# Converts audio files into .npz, so that the detector can learn
# to ignore empty noise in a whale call (#10)

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from boat_noise_class import (AUDIO_EXTS, load_audio, make_windows, is_usable,
                              normalize, pcen_mel, split_sources)


def read_exclusions(src, csv_path):
    """Return {resolved_file_path: [(start_s, end_s), ...]} of spans to avoid."""
    spans = {}
    if not csv_path:
        return spans
    with open(csv_path, newline="") as fh:
        for row in csv.DictReader(fh):
            f = (Path(src) / row["file"]).resolve()
            spans.setdefault(f, []).append((float(row["start_s"]), float(row["end_s"])))
    return spans


def overlaps(start_s, end_s, spans, pad=0.5):
    """True if [start_s, end_s] touches any excluded span (with a small safety margin)."""
    return any(start_s < e + pad and end_s > s - pad for s, e in spans)


def window_rms(w):
    return float(np.sqrt(np.mean(w ** 2)))


def build_ambient_class(a):
    src, out = Path(a.src), Path(a.out)
    files = [p for p in src.rglob("*") if p.suffix.lower() in AUDIO_EXTS]
    if not files:
        raise SystemExit(f"No audio files found under {src}")
    exclusions = read_exclusions(src, a.exclude)
    splits = split_sources(files, seed=a.seed)
    manifest, stats = [], {"loud": 0, "excluded": 0, "unusable": 0}

    for split, split_files in splits.items():
        feats, audio = [], []
        for f in split_files:
            y = load_audio(f, a.sr)
            wins = list(make_windows(y, a.sr, a.win, a.hop))
            if not wins:
                continue
            rms_all = np.array([window_rms(w) for _, w in wins])
            typical = float(np.median(rms_all[rms_all > 0])) if np.any(rms_all > 0) else 0.0
            spans = exclusions.get(f.resolve(), [])

            for (start, w), rms in zip(wins, rms_all):
                t0 = start / a.sr
                if overlaps(t0, t0 + a.win, spans):
                    stats["excluded"] += 1
                    continue
                if typical > 0 and rms > a.max_rms_ratio * typical:
                    stats["loud"] += 1                 # probably a boat, splash or bump
                    continue
                # low min_rms: genuinely quiet water must not be thrown away as "silence"
                if not is_usable(w, min_rms=a.min_rms):
                    stats["unusable"] += 1
                    continue
                w = normalize(w)
                feats.append(pcen_mel(w, a.sr, n_mels=a.n_mels, fmin=a.fmin, fmax=a.fmax))
                if not a.no_audio:
                    audio.append(w)
                manifest.append({"split": split, "source": str(f), "start_s": t0,
                                 "label": "ambient_water"})
        if feats:
            out.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                out / f"ambient_water_{split}.npz",
                X=np.stack(feats),
                y=np.zeros(len(feats), dtype=np.int64),
                **({"audio": np.stack(audio)} if not a.no_audio else {}),
            )
        print(f"{split:5s}: {len(split_files)} files -> {len(feats)} windows")

    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Skipped: {stats['excluded']} overlapping excluded spans, "
          f"{stats['loud']} too loud (likely boats/splashes), {stats['unusable']} unusable")
    print(f"Manifest written to {out / 'manifest.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="folder of quiet-water recordings")
    ap.add_argument("--out", default= "data/ambient_windows", help= "output folder")
    ap.add_argument("--exclude", help="CSV file,start_s,end_s of spans to skip (e.g. whale calls)")
    ap.add_argument("--sr", type=int, default=8000)
    ap.add_argument("--win", type=float, default=5.0)
    ap.add_argument("--hop", type=float, default=2.5)
    ap.add_argument("--n_mels", type=int, default=64)
    ap.add_argument("--fmin", type=float, default=20)
    ap.add_argument("--fmax", type=float, default=3500)
    ap.add_argument("--max_rms_ratio", type=float, default=3.0,
                    help="skip windows louder than this multiple of the file's median level")
    ap.add_argument("--min_rms", type=float, default=1e-6,
                    help="silence floor (lower than the boat script so quiet water is kept)")
    ap.add_argument("--no_audio", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    build_ambient_class(ap.parse_args())
