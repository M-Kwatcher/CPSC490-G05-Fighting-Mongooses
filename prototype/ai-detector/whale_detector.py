# Creates/further trains a model to detect whale calls and
# ignore any other noises possibly created.
# Also detects whale noises created from a given audio file (#10/12)

import argparse
import csv
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

# Reuse the exact preprocessing used to build the classes
from boat_noise_class import load_audio, make_windows, is_usable, normalize, pcen_mel


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
def load_split(split, boat_dir, whale_dir, extra_dirs):
    Xs, ys, snrs = [], [], []

    def add(path, label, snr_key=False):
        d = np.load(path)
        n = len(d["X"])
        Xs.append(d["X"])
        ys.append(np.full(n, label, dtype=np.int64))
        snrs.append(d["snr"] if snr_key and "snr" in d.files else np.full(n, np.nan, np.float32))

    p = Path(boat_dir) / f"boat_noise_{split}.npz"
    if p.exists():
        add(p, 0)
    p = Path(whale_dir) / f"whale_call_{split}.npz"
    if p.exists():
        add(p, 1, snr_key=True)
    for d in extra_dirs or []:
        for q in sorted(Path(d).glob(f"*_{split}.npz")):
            add(q, 0)
    if not Xs:
        raise SystemExit(f"No data found for split '{split}'")
    return np.concatenate(Xs), np.concatenate(ys), np.concatenate(snrs)


class SpecDataset(Dataset):
    def __init__(self, X, y, mean, std, augment=False):
        self.X, self.y, self.mean, self.std, self.augment = X, y, mean, std, augment

    def __len__(self):
        return len(self.X)

    def __getitem__(self, i):
        x = (self.X[i] - self.mean) / self.std
        if self.augment:
            x = self._augment(x.copy())
        return torch.from_numpy(x).unsqueeze(0).float(), float(self.y[i])

    @staticmethod
    def _augment(x):
        m, t = x.shape
        # random time shift, small frequency mask, small time mask
        x = np.roll(x, np.random.randint(-t // 8, t // 8 + 1), axis=1)
        f = np.random.randint(0, max(2, m // 10))
        f0 = np.random.randint(0, m - f + 1)
        x[f0:f0 + f, :] = 0
        w = np.random.randint(0, max(2, t // 10))
        w0 = np.random.randint(0, t - w + 1)
        x[:, w0:w0 + w] = 0
        return x


# ----------------------------------------------------------------------------
# Model: small CNN on PCEN mel spectrograms, one logit out (whale vs not)
# ----------------------------------------------------------------------------
class WhaleCNN(nn.Module):
    def __init__(self, ch=(16, 32, 64, 96), dropout=0.3):
        super().__init__()
        layers, c_in = [], 1
        for c in ch:
            layers += [nn.Conv2d(c_in, c, 3, padding=1), nn.BatchNorm2d(c),
                       nn.ReLU(inplace=True), nn.MaxPool2d(2, ceil_mode=True)]
            c_in = c
        self.features = nn.Sequential(*layers)
        self.head = nn.Sequential(nn.Dropout(dropout), nn.Linear(c_in, 1))

    def forward(self, x):
        x = self.features(x)
        x = F.adaptive_avg_pool2d(x, 1).flatten(1)   # works for any window length
        return self.head(x).squeeze(1)


# ----------------------------------------------------------------------------
# Metrics (numpy only)
# ----------------------------------------------------------------------------
def auc(scores, labels):
    pos, neg = scores[labels == 1], scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    order = np.argsort(np.concatenate([pos, neg]))
    ranks = np.empty(len(order))
    ranks[order] = np.arange(1, len(order) + 1)
    return (ranks[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def threshold_for_fpr(neg_scores, target_fpr):
    """Smallest threshold giving at most target_fpr false positives on negatives."""
    return float(np.quantile(neg_scores, 1 - target_fpr))


def report(scores, labels, snr, thr, title):
    pred = scores >= thr
    tp = int(np.sum(pred & (labels == 1))); fn = int(np.sum(~pred & (labels == 1)))
    fp = int(np.sum(pred & (labels == 0))); tn = int(np.sum(~pred & (labels == 0)))
    rec = tp / max(tp + fn, 1); fpr = fp / max(fp + tn, 1)
    prec = tp / max(tp + fp, 1)
    print(f"[{title}] AUC={auc(scores, labels):.3f}  thr={thr:.3f}  "
          f"recall={rec:.3f}  precision={prec:.3f}  FPR={fpr:.4f}  (TP={tp} FN={fn} FP={fp} TN={tn})")
    mask = (labels == 1) & ~np.isnan(snr)
    if mask.any():
        edges = [-np.inf, -5, 0, 5, 10, np.inf]
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = mask & (snr >= lo) & (snr < hi)
            if m.sum():
                print(f"    SNR [{lo:>5}, {hi:>5}) dB: recall={pred[m].mean():.3f}  n={int(m.sum())}")


@torch.no_grad()
def predict(model, loader, device):
    model.eval()
    out = []
    for x, _ in loader:
        out.append(torch.sigmoid(model(x.to(device))).cpu().numpy())
    return np.concatenate(out)


# ----------------------------------------------------------------------------
# Train
# ----------------------------------------------------------------------------
def train(a):
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    Xtr, ytr, _ = load_split("train", a.boat, a.whale, a.extra_neg)
    Xva, yva, snrva = load_split("val", a.boat, a.whale, a.extra_neg)
    mean, std = float(Xtr.mean()), float(Xtr.std() + 1e-6)
    print(f"train: {len(Xtr)} windows ({int(ytr.sum())} whale)   val: {len(Xva)} ({int(yva.sum())} whale)")

    # balance classes by sampling
    cls_w = 1.0 / np.bincount(ytr, minlength=2).clip(1)
    sampler = WeightedRandomSampler(cls_w[ytr], num_samples=len(ytr), replacement=True)
    tr = DataLoader(SpecDataset(Xtr, ytr, mean, std, augment=True), batch_size=a.batch,
                    sampler=sampler, num_workers=0)
    va = DataLoader(SpecDataset(Xva, yva, mean, std), batch_size=a.batch)

    model = WhaleCNN().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=a.epochs)
    lossf = nn.BCEWithLogitsLoss()

    best, best_state = -1, None
    for ep in range(1, a.epochs + 1):
        model.train(); tot = 0
        for x, y in tr:
            x, y = x.to(device), y.float().to(device)
            opt.zero_grad()
            loss = lossf(model(x), y)
            loss.backward(); opt.step()
            tot += loss.item() * len(x)
        sched.step()
        s = predict(model, va, device)
        a_ = auc(s, yva)
        print(f"epoch {ep:3d}  loss={tot / len(Xtr):.4f}  val AUC={a_:.4f}")
        if a_ > best:
            best, best_state = a_, {k: v.cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    s = predict(model, va, device)
    thr = threshold_for_fpr(s[yva == 0], a.target_fpr)
    report(s, yva, snrva, thr, "val")

    # held-out test set (separate recordings)
    try:
        Xte, yte, snrte = load_split("test", a.boat, a.whale, a.extra_neg)
        te = DataLoader(SpecDataset(Xte, yte, mean, std), batch_size=a.batch)
        report(predict(model, te, device), yte, snrte, thr, "test")
    except SystemExit:
        print("No test split found; skipping test report.")

    torch.save({
        "state": best_state, "mean": mean, "std": std, "threshold": thr,
        "prep": dict(sr=a.sr, win=a.win, n_mels=a.n_mels, fmin=a.fmin, fmax=a.fmax),
    }, a.out)
    print(f"Saved {a.out}")


# ----------------------------------------------------------------------------
# Detect on a long recording
# ----------------------------------------------------------------------------
def detect(a):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ck = torch.load(a.model, map_location=device)
    p = ck["prep"]
    model = WhaleCNN().to(device); model.load_state_dict(ck["state"]); model.eval()
    thr = a.threshold if a.threshold is not None else ck["threshold"]

    y = load_audio(a.audio, p["sr"])
    hop = a.hop or p["win"] / 2
    starts, feats = [], []
    for s, w in make_windows(y, p["sr"], p["win"], hop):
        if not is_usable(w):
            continue
        feats.append(pcen_mel(normalize(w), p["sr"], n_mels=p["n_mels"], fmin=p["fmin"], fmax=p["fmax"]))
        starts.append(s / p["sr"])
    if not feats:
        raise SystemExit("No usable windows in the recording.")

    x = (np.stack(feats) - ck["mean"]) / ck["std"]
    with torch.no_grad():
        probs = torch.sigmoid(model(torch.from_numpy(x).unsqueeze(1).float().to(device))).cpu().numpy()

    # smooth over neighbouring windows so one noisy window does not trigger an alert
    k = a.smooth
    smooth = np.convolve(probs, np.ones(k) / k, mode="same") if k > 1 else probs

    # hysteresis: start an event above thr, end it when below 0.7*thr
    events, on, t0 = [], False, None
    for t, sc in zip(starts, smooth):
        if not on and sc >= thr:
            on, t0, peak = True, t, sc
        elif on:
            peak = max(peak, sc)
            if sc < 0.7 * thr:
                events.append((t0, t + hop, peak)); on = False
    if on:
        events.append((t0, starts[-1] + p["win"], peak))

    with open(a.events, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["start_s", "end_s", "peak_prob"])
        w.writerows([(f"{s:.1f}", f"{e:.1f}", f"{pk:.3f}") for s, e, pk in events])
    hours = len(y) / p["sr"] / 3600
    print(f"{len(events)} events in {hours:.2f} h ({len(events) / max(hours, 1e-9):.1f}/h) -> {a.events}")


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train")
    t.add_argument("--boat", default= "data/boat_windows")
    t.add_argument("--whale", default= "data/whale_windows")
    t.add_argument("--extra_neg", default= "data/ambient_windows", nargs="*", help="folders with extra label-0 *_<split>.npz")
    t.add_argument("--out", default="model.pt")
    t.add_argument("--sr", type=int, default= 8000)
    t.add_argument("--win", type=float, default= 5.0)
    t.add_argument("--n_mels", type=int, default=64)
    t.add_argument("--fmin", type=float, default=20)
    t.add_argument("--fmax", type=float, default=3500)
    t.add_argument("--epochs", type=int, default=30)
    t.add_argument("--batch", type=int, default=32)
    t.add_argument("--lr", type=float, default=1e-3)
    t.add_argument("--target_fpr", type=float, default=0.01,
                   help="false-positive rate on negative windows used to pick the threshold")
    t.add_argument("--seed", type=int, default=0)
    t.set_defaults(fn=train)

    d = sub.add_parser("detect")
    d.add_argument("--model", required=True)
    d.add_argument("--audio", required=True)
    d.add_argument("--events", default="events.csv")
    d.add_argument("--hop", type=float, default=2.5, help="seconds between windows")
    d.add_argument("--smooth", type=int, default=3, help="windows to average")
    d.add_argument("--threshold", type=float, default=None)
    d.set_defaults(fn=detect)

    args = ap.parse_args()
    args.fn(args)
