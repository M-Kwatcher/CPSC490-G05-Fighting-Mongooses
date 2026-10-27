"""
Tests how well the given model is able to differentiate
boat noises and ambient noises from whale calls
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

from boat_noise_class import AUDIO_EXTS
from inspect_detector import load_groups, load_model, score_windows
from whale_detector import auc


# ----------------------------------------------------------------------------
# Statistics helpers
# ----------------------------------------------------------------------------
def wilson(k, n, z=1.96):
    """95% Wilson interval for a proportion k/n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def bootstrap_auc(scores, labels, n_boot=1000, seed=0):
    rng = np.random.default_rng(seed)
    pos, neg = scores[labels == 1], scores[labels == 0]
    vals = []
    for _ in range(n_boot):
        p = rng.choice(pos, len(pos)); n = rng.choice(neg, len(neg))
        vals.append(auc(np.concatenate([p, n]),
                        np.concatenate([np.ones(len(p), int), np.zeros(len(n), int)])))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def recall_at_fpr(scores, labels, target_fpr):
    thr = np.quantile(scores[labels == 0], 1 - target_fpr)
    return float(np.mean(scores[labels == 1] >= thr))


# ----------------------------------------------------------------------------
# Window-level evaluation
# ----------------------------------------------------------------------------
def evaluate_windows(groups, thr, out_dir):
    scores = np.concatenate([g["scores"] for g in groups])
    labels = np.concatenate([np.full(len(g["scores"]), g["label"]) for g in groups])
    snr = np.concatenate([g["snr"] for g in groups])
    kinds = np.concatenate([[m["kind"] or "?" for m in g["meta"]] for g in groups])
    pred = scores >= thr

    tp = int(np.sum(pred & (labels == 1))); fn = int(np.sum(~pred & (labels == 1)))
    fp = int(np.sum(pred & (labels == 0))); tn = int(np.sum(~pred & (labels == 0)))
    res = {
        "n_whale": tp + fn, "n_negative": fp + tn, "threshold": float(thr),
        "auc": float(auc(scores, labels)),
        "auc_ci": bootstrap_auc(scores, labels),
        "recall": tp / max(tp + fn, 1), "recall_ci": wilson(tp, tp + fn),
        "precision": tp / max(tp + fp, 1),
        "fpr": fp / max(fp + tn, 1), "fpr_ci": wilson(fp, fp + tn),
        "score_std": float(np.std(scores)),
        "recall_at_fpr": {f"{f:g}": recall_at_fpr(scores, labels, f) for f in (0.001, 0.01, 0.05)},
        "groups": {}, "synthetic_snr0_recall": None,
    }
    for g in groups:
        flagged = g["scores"] >= thr
        res["groups"][g["name"]] = {
            "label": g["label"], "n": len(flagged),
            ("fpr" if g["label"] == 0 else "recall"): float(flagged.mean()),
        }
    m = (labels == 1) & (kinds == "synthetic") & ~np.isnan(snr) & (snr >= 0)
    if m.sum():
        res["synthetic_snr0_recall"] = float(pred[m].mean())
        res["synthetic_snr0_n"] = int(m.sum())
    res["recall_by_snr"] = {}
    edges = [-np.inf, -5, 0, 5, 10, np.inf]
    for lo, hi in zip(edges[:-1], edges[1:]):
        mm = (labels == 1) & ~np.isnan(snr) & (snr >= lo) & (snr < hi)
        if mm.sum():
            res["recall_by_snr"][f"[{lo},{hi})"] = {"recall": float(pred[mm].mean()), "n": int(mm.sum())}

    plot_roc(scores, labels, thr, res, Path(out_dir) / "roc_and_scores.png")
    return res


def plot_roc(scores, labels, thr, res, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = np.argsort(-scores)
    l = labels[order]
    tpr = np.concatenate([[0], np.cumsum(l == 1) / max((l == 1).sum(), 1)])
    fpr = np.concatenate([[0], np.cumsum(l == 0) / max((l == 0).sum(), 1)])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
    a1.plot(fpr, tpr, lw=1.5)
    a1.plot([0, 1], [0, 1], "k:", lw=0.8)
    a1.plot(res["fpr"], res["recall"], "ro", label=f"saved threshold {thr:.2f}")
    a1.set_xlabel("false-alarm rate"); a1.set_ylabel("recall")
    a1.set_title(f"ROC (AUC {res['auc']:.3f})"); a1.legend()
    bins = np.linspace(0, 1, 31)
    a2.hist(scores[labels == 0], bins=bins, alpha=0.6, label="not whale")
    a2.hist(scores[labels == 1], bins=bins, alpha=0.6, label="whale")
    a2.axvline(thr, color="red", ls="--")
    a2.set_xlabel("detector score"); a2.set_ylabel("windows"); a2.legend(); a2.set_yscale("log")
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


# ----------------------------------------------------------------------------
# Event-level evaluation
# ----------------------------------------------------------------------------
def events_from_probs(starts, probs, thr, hop, win, smooth):
    """Same smoothing + hysteresis as `whale_detector.py detect`."""
    probs = np.asarray(probs, dtype=float)
    sm = np.convolve(probs, np.ones(smooth) / smooth, mode="same") if smooth > 1 else probs
    events, on, t0, peak = [], False, None, 0.0
    for t, sc in zip(starts, sm):
        if not on and sc >= thr:
            on, t0, peak = True, t, sc
        elif on:
            peak = max(peak, sc)
            if sc < 0.7 * thr:
                events.append((t0, t + hop, float(peak))); on = False
    if on:
        events.append((t0, starts[-1] + win, float(peak)))
    return events


def match_events(events, calls, tol):
    """Return (detected_flags per call, false_event_flags per event)."""
    def hit(ev, c):
        return ev[0] < c[1] + tol and ev[1] > c[0] - tol
    detected = [any(hit(e, c) for e in events) for c in calls]
    false_ev = [not any(hit(e, c) for c in calls) for e in events]
    return detected, false_ev


def read_annotations(path):
    calls = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            calls.setdefault(Path(row["file"]).name, []).append((float(row["start_s"]), float(row["end_s"])))
    return calls


def probs_for_file(path, model, ck, dev, hop, batch=256):
    from boat_noise_class import load_audio, make_windows, is_usable, normalize, pcen_mel
    p = ck["prep"]
    y = load_audio(path, p["sr"])
    starts, probs, feats, fstarts = [], [], [], []

    def flush():
        if feats:
            probs.extend(score_windows(model, ck, dev, np.stack(feats)).tolist())
            starts.extend(fstarts)
            feats.clear(); fstarts.clear()

    for s, w in make_windows(y, p["sr"], p["win"], hop):
        if not is_usable(w):
            continue
        feats.append(pcen_mel(normalize(w), p["sr"], n_mels=p["n_mels"], fmin=p["fmin"], fmax=p["fmax"]))
        fstarts.append(s / p["sr"])
        if len(feats) >= batch:
            flush()
    flush()
    return starts, probs, len(y) / p["sr"]


def evaluate_events(files, annotations, get_probs, thr, win, hop, smooth, tol, out_dir):
    """get_probs(path) -> (starts, probs, duration_s)."""
    total_hours, n_calls, n_detected, n_events, n_false = 0.0, 0, 0, 0, 0
    missed, falses = [], []
    for f in files:
        starts, probs, dur = get_probs(f)
        total_hours += dur / 3600
        calls = annotations.get(Path(f).name, [])
        events = events_from_probs(starts, probs, thr, hop, win, smooth) if starts else []
        det, fe = match_events(events, calls, tol)
        n_calls += len(calls); n_detected += sum(det)
        n_events += len(events); n_false += sum(fe)
        missed += [(Path(f).name, s, e) for (s, e), d in zip(calls, det) if not d]
        falses += [(Path(f).name, ev[0], ev[1], ev[2]) for ev, bad in zip(events, fe) if bad]
        if not calls:
            print(f"[note] no annotations for {Path(f).name}; every event there counts as a false alarm")

    with open(Path(out_dir) / "missed_calls.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["file", "start_s", "end_s"])
        w.writerows([(a, f"{b:.1f}", f"{c:.1f}") for a, b, c in missed])
    with open(Path(out_dir) / "false_alarms.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["file", "start_s", "end_s", "peak_prob"])
        w.writerows([(a, f"{b:.1f}", f"{c:.1f}", f"{d:.3f}") for a, b, c, d in falses])

    return {
        "hours": total_hours, "n_calls": n_calls, "calls_detected": n_detected,
        "event_recall": n_detected / max(n_calls, 1),
        "event_recall_ci": wilson(n_detected, n_calls),
        "n_events": n_events, "false_alarms": n_false,
        "false_alarms_per_hour": n_false / max(total_hours, 1e-9),
        "event_precision": (n_events - n_false) / max(n_events, 1),
    }


# ----------------------------------------------------------------------------
# Pass/fail
# ----------------------------------------------------------------------------
def run_checks(win_res, ev_res, a):
    checks = [
        ("model output varies (not a constant)", win_res["score_std"], ">=", 0.01),
        ("window AUC", win_res["auc"], ">=", a.min_auc),
        ("window recall at saved threshold", win_res["recall"], ">=", a.min_recall),
        ("window false-alarm rate", win_res["fpr"], "<=", a.max_fpr),
    ]
    if win_res["synthetic_snr0_recall"] is not None:
        checks.append(("recall, calls over boat noise at SNR >= 0 dB",
                       win_res["synthetic_snr0_recall"], ">=", a.min_recall_snr0))
    neg = [(n, v["fpr"]) for n, v in win_res["groups"].items() if v["label"] == 0]
    if neg:
        worst = max(neg, key=lambda t: t[1])
        checks.append((f"worst negative group false-alarm rate ({worst[0]})", worst[1], "<=", a.max_group_fpr))
    if ev_res:
        checks.append(("event recall (annotated calls found)", ev_res["event_recall"], ">=", a.min_event_recall))
        checks.append(("false alarms per hour", ev_res["false_alarms_per_hour"], "<=", a.max_fa_per_hour))
    out = []
    for name, val, op, target in checks:
        ok = val >= target if op == ">=" else val <= target
        out.append((name, val, op, target, bool(ok)))
    return out


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default= "model.pt")
    ap.add_argument("--boat", default= "data/boat_windows")
    ap.add_argument("--whale", default= "data/whale_windows")
    ap.add_argument("--extra_neg", default= "data/ambient_windows", nargs="*")
    ap.add_argument("--split", default="test", choices=["val", "test"])
    ap.add_argument("--threshold", type=float, help="override the saved threshold (not recommended)")
    ap.add_argument("--out", default="eval_out")
    ap.add_argument("--long_dir", help="folder of long, fully annotated test recordings")
    ap.add_argument("--annotations", help="CSV file,start_s,end_s for --long_dir")
    ap.add_argument("--hop", type=float)
    ap.add_argument("--smooth", type=int, default=3)
    ap.add_argument("--tol", type=float, default=2.0, help="seconds of slack when matching events to calls")
    # pass/fail targets (placeholders: set them from what your use needs)
    ap.add_argument("--min_auc", type=float, default=0.95)
    ap.add_argument("--min_recall", type=float, default=0.80)
    ap.add_argument("--min_recall_snr0", type=float, default=0.90)
    ap.add_argument("--max_fpr", type=float, default=0.02)
    ap.add_argument("--max_group_fpr", type=float, default=0.05)
    ap.add_argument("--min_event_recall", type=float, default=0.80)
    ap.add_argument("--max_fa_per_hour", type=float, default=2.0)
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    model, ck, dev = load_model(a.model)
    thr = a.threshold if a.threshold is not None else ck["threshold"]
    p = ck["prep"]

    groups = load_groups(a.split, a.boat, a.whale, a.extra_neg)
    for g in groups:
        g["scores"] = score_windows(model, ck, dev, g["X"])
    win_res = evaluate_windows(groups, thr, out)

    ev_res = None
    if a.long_dir:
        if not a.annotations:
            raise SystemExit("--long_dir needs --annotations")
        files = sorted(f for f in Path(a.long_dir).rglob("*") if f.suffix.lower() in AUDIO_EXTS)
        if not files:
            raise SystemExit(f"No audio under {a.long_dir}")
        hop = a.hop or p["win"] / 2
        ev_res = evaluate_events(
            files, read_annotations(a.annotations),
            lambda f: probs_for_file(f, model, ck, dev, hop), thr, p["win"], hop, a.smooth, a.tol, out)

    checks = run_checks(win_res, ev_res, a)

    # ---- report
    r = win_res
    print(f"\n=== WINDOW LEVEL ({a.split} split) | {r['n_whale']} whale, {r['n_negative']} negative windows ===")
    print(f"AUC                : {r['auc']:.3f}  (95% CI {r['auc_ci'][0]:.3f}-{r['auc_ci'][1]:.3f})")
    print(f"Recall             : {r['recall']:.3f}  (95% CI {r['recall_ci'][0]:.3f}-{r['recall_ci'][1]:.3f})  at threshold {thr:.3f}")
    print(f"Precision          : {r['precision']:.3f}")
    print(f"False-alarm rate   : {r['fpr']:.4f}  (95% CI {r['fpr_ci'][0]:.4f}-{r['fpr_ci'][1]:.4f})")
    for f, v in r["recall_at_fpr"].items():
        print(f"Recall at {float(f) * 100:g}% FPR : {v:.3f}")
    for n, v in r["groups"].items():
        k = "false-alarm rate" if v["label"] == 0 else "recall"
        print(f"  group {n:<16s} n={v['n']:<6d} {k}: {v.get('fpr', v.get('recall')):.3f}")
    for k, v in r["recall_by_snr"].items():
        print(f"  SNR {k:<12s} n={v['n']:<5d} recall: {v['recall']:.3f}")
    if ev_res:
        e = ev_res
        print(f"\n=== EVENT LEVEL | {e['hours']:.2f} h of audio, {e['n_calls']} annotated calls ===")
        print(f"Calls found        : {e['calls_detected']}/{e['n_calls']} = {e['event_recall']:.3f}  "
              f"(95% CI {e['event_recall_ci'][0]:.3f}-{e['event_recall_ci'][1]:.3f})")
        print(f"False alarms       : {e['false_alarms']}  ({e['false_alarms_per_hour']:.2f} per hour)")
        print(f"Event precision    : {e['event_precision']:.3f}")
        print(f"Details            : {out / 'missed_calls.csv'}, {out / 'false_alarms.csv'}")

    print("\n=== CHECKS ===")
    for name, val, op, target, ok in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {val:.3f} (need {op} {target:g})")
    small = min(r["n_whale"], r["n_negative"])
    if small < 100:
        print(f"\n[warn] only {small} windows in the smaller class: the intervals above are wide, "
              "so treat these numbers as rough.")

    (out / "results.json").write_text(json.dumps(
        {"window": win_res, "event": ev_res,
         "checks": [dict(name=n, value=v, op=o, target=t, passed=ok) for n, v, o, t, ok in checks]},
        indent=2, default=float))
    print(f"\nSaved {out / 'results.json'} and {out / 'roc_and_scores.png'}")
    sys.exit(0 if all(c[4] for c in checks) else 1)


if __name__ == "__main__":
    main()
