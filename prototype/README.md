# Prototype — WILS (Whale Identification/Location System)

Proof-of-concept code for WILS, Group 5 "Fighting Mongooses". It grows every
sprint; the in-class checks demo from this folder.

Right now it holds:

- **`locator/`** — Goal 2: where a whale call came from. Direction (#15) and
  distance (#16) from hydrophone recordings.
  Run `python -m locator.smoke` to check it end to end.
- **`locator/save_call.py`** — saves detected calls as .wav files with a
  timestamp and hydrophone ID (#13).

## Setup (once, from the repository root)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (Mac/Linux: source .venv/bin/activate)
pip install -r prototype/requirements.txt pytest
copy prototype\.env.example prototype\.env   # Mac/Linux: cp; then fill in your values
```

## How to run

```bash
cd prototype
python -m locator.demo_delay      # plots a test sound and a copy 160 samples later
python -m locator.smoke           # one fake whale through the whole locator, no plots
```

## How to test

```bash
cd prototype
python -m pytest tests -q         # 41 tests
```

CI runs exactly these tests on every pull request (job **Prototype build &
tests**).

## Status

| Sprint | Increment |
|---|---|
| v0 (Sep 27) | course example: login check (removed in Sprint 2) |
| Sprint 1 | proposal and project board (no new prototype code) |
| Sprint 2 | locator: direction (#15, 17 tests), distance from 4 hydrophones (#16, 22 tests), saving calls (#13, 2 tests), smoke run, .env.example |

## Locator (#15, #16)

Estimates where a whale call came from using the time difference of arrival
(TDOA) between hydrophones: a hydrophone farther from the whale hears the call
slightly later, and those small delays give the direction and distance.

| File | What it does |
|---|---|
| `locator/config.py` | Shared settings: speed of sound (1,500 m/s), sample rate (48 kHz), hydrophone positions |
| `locator/simulate.py` | Fake recordings for testing: a test sound, a source at a known angle and distance, delayed and noisy copies per hydrophone |
| `locator/tdoa.py` | Direction (#15): `findDelay` (cross-correlation), `delayToAngle`, `estimateAngle` |
| `locator/locate.py` | Distance (#16): `predictedDelays`, `estimatePosition` (least squares), `estimateDistance` |
| `locator/demo_delay.py` | Plot of a sound and its delayed copy |
| `locator/save_call.py` | Saves a detected call as a .wav with timestamp and hydrophone ID (#13) |
| `locator/smoke.py` | Smoke run: one fake whale, prints direction and distance |

### What it proves — direction (#15)

- `findDelay` measures the delay between two recordings with cross-correlation.
- `delayToAngle` turns that delay into a direction: θ = arcsin(c · Δt / d).
- With 2 hydrophones 10 m apart, the estimated direction is within 15° of the
  true direction from −80° to 80°, with noise as loud as the call itself.
- Known limit: 2 hydrophones cannot tell front from back, so angles are
  reported on the front side.

### What it proves — distance (#16)

- `estimatePosition` finds the source by fitting a position whose predicted
  delays (r_i − r_1) / c match the measured ones (`scipy.optimize.least_squares`,
  started from 36 guesses around the array so it doesn't get stuck).
- `estimateDistance` is the distance from the array center to that position.
- With 4 hydrophones in a 50 m square (`DISTANCE_HYDROPHONES`), the estimated
  distance is within 10% of the true distance from 25 m to 500 m, in front of
  and behind the array, with noise. A wider sweep (8 distances × 12 directions
  × 3 noise levels) passed 283 of 288 cases (98%).
- Why not 2–3 hydrophones 10 m apart: 2 can't measure distance at all, and 3
  at 10 m only stay within 10% out to about 50 m.

### References

[1] Callaghan and Berry, EE 98 senior design technical note on sound-source
direction estimation with a microphone array, Tufts University Electrical and
Computer Engineering Senior Design Handbook, 2023. [Online]. Available:
https://sites.tufts.edu/eeseniordesignhandbook/files/2023/05/ee98_shp_Callaghan_Berry.pdf
(accessed Oct. 16, 2026).

[2] The MathWorks, Inc., "Cross-Correlation of Delayed Signal in Noise,"
Signal Processing Toolbox Documentation. [Online]. Available:
https://www.mathworks.com/help/signal/ug/cross-correlation-of-delayed-signal-in-noise.html
(accessed Oct. 16, 2026).

[3] SciPy Developers, "scipy.signal.correlation_lags," SciPy Reference
Documentation. [Online]. Available:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlation_lags.html
(accessed Oct. 16, 2026).

[4] SciPy Developers, "scipy.optimize.least_squares," SciPy Reference
Documentation. [Online]. Available:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html
(accessed Oct. 25, 2026).