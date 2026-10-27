# Converts audio files into .npz so that model can learn to ignore
# boat noises when trying to detect a whale (#12)

import argparse
import json
import random
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

AUDIO_EXTS = {".wav", ".flac", ".mp3", ".ogg"}


# ----------------------------------------------------------------------------
# Loading and windowing
# ----------------------------------------------------------------------------
def load_audio(path, sr):
    """Load mono audio resampled to `sr`."""
    y, _ = librosa.load(str(path), sr=sr, mono=True)
    return y.astype(np.float32)


def make_windows(y, sr, win_s, hop_s):
    """Yield (start_sample, window) for fixed-length windows."""
    win, hop = int(win_s * sr), int(hop_s * sr)
    for start in range(0, max(len(y) - win, 0) + 1, hop):
        yield start, y[start:start + win]


def is_usable(w, min_rms=1e-4, clip_level=0.99, max_clip_frac=0.001):
    """Reject near-silent windows and heavily clipped ones (hydrophone overload)."""
    if len(w) == 0:
        return False
    rms = float(np.sqrt(np.mean(w ** 2)))
    clipped = float(np.mean(np.abs(w) >= clip_level))
    return rms >= min_rms and clipped <= max_clip_frac


def normalize(w):
    """Remove DC offset and scale to peak 1 (keeps relative spectral shape)."""
    w = w - np.mean(w)
    peak = np.max(np.abs(w))
    return w / peak if peak > 0 else w


# ----------------------------------------------------------------------------
# Features: PCEN mel spectrogram
# ----------------------------------------------------------------------------
def pcen_mel(w, sr, n_fft=None, hop_length=None, n_mels=64, fmin=10, fmax=None):
    """PCEN-normalised mel spectrogram, shape (n_mels, frames)."""
    n_fft = n_fft or int(0.25 * sr)           # 250 ms frames suit low-frequency calls
    hop_length = hop_length or n_fft // 4
    fmax = fmax or sr / 2
    # PCEN expects an un-logged, magnitude-scaled mel spectrogram
    mel = librosa.feature.melspectrogram(
        y=w, sr=sr, n_fft=n_fft, hop_length=hop_length,
        n_mels=n_mels, fmin=fmin, fmax=fmax, power=1.0,
    )
    S = mel * (2 ** 31)
    return librosa.pcen(S, sr=sr, hop_length=hop_length).astype(np.float32)


# ----------------------------------------------------------------------------
# Dataset builder with source-level splits
# ----------------------------------------------------------------------------
def split_sources(files, val_frac=0.15, test_frac=0.15, seed=0):
    """Assign whole recordings to train/val/test so windows never leak across splits."""
    files = sorted(files)
    random.Random(seed).shuffle(files)
    n = len(files)
    n_test = max(1, int(n * test_frac)) if n >= 3 else 0
    n_val = max(1, int(n * val_frac)) if n >= 3 else 0
    return {
        "test": files[:n_test],
        "val": files[n_test:n_test + n_val],
        "train": files[n_test + n_val:],
    }


def build_boat_noise_class(src, out, sr, win_s, hop_s, n_mels, fmin, fmax,
                           save_audio=True, seed=0):
    src, out = Path(src), Path(out)
    files = [p for p in src.rglob("*") if p.suffix.lower() in AUDIO_EXTS]
    if not files:
        raise SystemExit(f"No audio files found under {src}")

    splits = split_sources(files, seed=seed)
    manifest = []

    for split, split_files in splits.items():
        feats, audio = [], []
        for f in split_files:
            y = load_audio(f, sr)
            for start, w in make_windows(y, sr, win_s, hop_s):
                if not is_usable(w):
                    continue
                w = normalize(w)
                feats.append(pcen_mel(w, sr, n_mels=n_mels, fmin=fmin, fmax=fmax))
                if save_audio:
                    audio.append(w)
                manifest.append({"split": split, "source": str(f),
                                 "start_s": start / sr, "label": "boat_noise"})
        if feats:
            out.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                out / f"boat_noise_{split}.npz",
                X=np.stack(feats),
                y=np.zeros(len(feats), dtype=np.int64),   # remap to your class index later
                **({"audio": np.stack(audio)} if save_audio else {}),
            )
        print(f"{split:5s}: {len(split_files)} files -> {len(feats)} windows")

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Manifest written to {out / 'manifest.json'}")


# ----------------------------------------------------------------------------
# Augmentation: put a whale call on top of real boat noise at a chosen SNR
# ----------------------------------------------------------------------------
def mix_at_snr(call, noise, snr_db, rng=None):
    """
    Overlay `call` onto `noise` at the given SNR (dB). Both are 1-D float arrays
    at the same sample rate. The call is placed at a random offset inside the noise.
    Returns (mixture, call_start_sample).
    """
    rng = rng or np.random.default_rng()
    call = call[:len(noise)]
    offset = int(rng.integers(0, len(noise) - len(call) + 1))

    noise_rms = np.sqrt(np.mean(noise ** 2)) + 1e-12
    call_rms = np.sqrt(np.mean(call ** 2)) + 1e-12
    gain = noise_rms * (10 ** (snr_db / 20)) / call_rms

    mix = noise.copy()
    mix[offset:offset + len(call)] += gain * call
    peak = np.max(np.abs(mix))
    if peak > 1:
        mix /= peak
    return mix, offset


# ----------------------------------------------------------------------------
# Optional PyTorch dataset that streams the saved windows
# ----------------------------------------------------------------------------
class BoatNoiseDataset:
    """Loads boat_noise_<split>.npz; returns (spectrogram[1,mels,T], label)."""

    def __init__(self, npz_path, label=0):
        import torch  # imported lazily so prep works without torch
        self._torch = torch
        d = np.load(npz_path)
        self.X, self.label = d["X"], label

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        x = self._torch.from_numpy(self.X[i]).unsqueeze(0)
        return x, self.label


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="folder of vessel recordings")
    ap.add_argument("--out", default="data/boat_windows", help="output folder")
    ap.add_argument("--sr", type=int, default=8000)
    ap.add_argument("--win", type=float, default=5.0, help="window length (s)")
    ap.add_argument("--hop", type=float, default=2.5, help="hop length (s)")
    ap.add_argument("--n_mels", type=int, default=64)
    ap.add_argument("--fmin", type=float, default=20)
    ap.add_argument("--fmax", type=float, default=3500)
    ap.add_argument("--no_audio", action="store_true", help="don't store raw windows")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    build_boat_noise_class(a.src, a.out, a.sr, a.win, a.hop,
                           a.n_mels, a.fmin, a.fmax,
                           save_audio=not a.no_audio, seed=a.seed)
