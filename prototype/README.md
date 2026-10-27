# Prototype — WILS (Whale Identification/Location System)

Proof-of-concept code for WILS, Group 5 "Fighting Mongooses". It grows every
sprint; the in-class checks demo from this folder.

Right now it holds:

- **`ai-detector/`** - Goal 1: being able to distinguish a whale call from
  ambient noise (#10) and boat noises (#12).
- **`locator/`** — Goal 2: where a whale call came from. Direction (#15) and
  distance (#16) from hydrophone recordings.
- **`login.py`** — the course's example slice (story #3, task #5), kept as a
  reference for the shape: a small module, a test per acceptance criterion,
  and run instructions that work on a fresh machine.

## Setup (once, from the repository root)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (Mac/Linux: source .venv/bin/activate)
pip install -r prototype/requirements.txt pytest
```

## How to run

```bash
cd prototype
python -m locator.demo_delay         # plots a test sound and a copy 160 samples later
python login.py                      # course example: prints a truncated session token
python ai-detector.whale_converter ./whale_noises      # takes in audio files (wav, flac, mp3, or ogg) from a given folder (in this case named whale_noises), and adds the data into a folder ./data/whale_windows
python ai-detector.boat_converter ./boat_noises        # same as whale converter, but for boat noises (./data/boat_windows)
python ai-detector.ambient_converter ./ambient_noises  # same as whale converter, but for ambient/empty ocean noises (./data/ambient_windows)
python ai-detector.whale_detector train                # takes data from ./data to train the model, and saves it to model.pt
python ai-detector.whale_detector detect noise.wav     # uses the trained model to detect if there's a whale noise in the provided audio file
```

## How to test

```bash
cd prototype
python -m pytest tests -q         # 43 tests
```

CI runs exactly these tests on every pull request (job **Prototype build &
tests**).

## Status

| Sprint | Increment |
|---|---|
| v0 (Sep 27) | course example: login check + 4 tests |
| Sprint 1 | proposal and project board (no new prototype code) |
| Sprint 2 | locator: direction from 2 hydrophones (#15, 17 tests) and distance from 4 hydrophones (#16, 22 tests) |

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
