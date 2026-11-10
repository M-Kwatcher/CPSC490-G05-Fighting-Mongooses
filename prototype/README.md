# Prototype — WILS (Whale Identification/Location System)

Proof-of-concept code for WILS, Group 5 "Fighting Mongooses". It grows every
sprint; the in-class checks demo from this folder.

Right now it holds:

- **`ai-detector/`** - Goal 1: being able to distinguish a whale call from
  ambient noise (#10) and boat noises (#12).
- **`locator/`** — Goal 2: where a whale call came from. Direction (#15) and
  distance (#16) from hydrophone recordings.
  Run `python -m locator.smoke` to check it end to end, or
  `python -m locator.demo_direction` for the interactive direction demo (#17).
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
python -m locator.demo_delay                        # plots a test sound and a copy 160 samples later
python login.py                                     # course example: prints a truncated session token
./ai-detector/pipeline --species                    # trains and evaluates the ai based on provided whale species (humpback, blue, or right are the specific labels)
python ai-detector/whale_detector detect --model    # has the ai run to detect whales based on the model provided (can use multiple)
python -m locator.demo_delay      # plots a test sound and a copy 160 samples later
python -m locator.smoke           # one fake whale through the whole locator, no plots
python -m locator.scenarios       # 20 direction scenarios (#17): pass/fail for each, then the overall rate
python -m locator.demo_direction  # interactive direction demo (#17): sliders for angle, noise, spacing
```

## How to test

```bash
cd prototype
python -m pytest tests -q       # all prototype tests
```

CI runs exactly these tests on every pull request (job **Prototype build &
tests**).

The direction requirement for #17 (at least 20 scenarios, at least 80% of
them passing) is checked by `tests/test_scenarios.py`.

## Status

| Sprint | Increment |
|---|---|
| v0 (Sep 27) | course example: login check (removed in Sprint 2) |
| Sprint 1 | proposal and project board (no new prototype code) |
| Sprint 2 | locator: direction from 2 hydrophones (#15, 17 tests) and distance from 4 hydrophones (#16, 22 tests)<br> ai detector: differentiating whale calls from background noise (#10) and from boat noises (#12) |
| Sprint 2 | locator: direction (#15, 17 tests), distance from 4 hydrophones (#16, 22 tests), saving calls (#13, 2 tests), smoke run, .env.example |
| Sprint 3 | locator: direction scenario test (20 scenarios, 80% requirement) and interactive direction demo (#17) |

## Locator (#15, #16, #17)

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
| `locator/scenarios.py` | Direction scenarios (#17): 20 fixed test cases, each scored against the 15° target, with a pass/fail report and the overall pass rate |
| `locator/demo_direction.py` | Interactive direction demo (#17): geometry, both recordings, the cross-correlation peak, and the arithmetic from delay to angle |
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

### What it proves — direction scenarios and demo (#17)

- `scenarios.py` runs 20 fixed scenarios with different angles, noise levels,
  and hydrophone spacings. A scenario passes when the estimated direction is
  within 15° of the true direction. The requirement is at least 20 scenarios
  with at least 80% passing, and `tests/test_scenarios.py` checks it.
- Result: 19 of 20 scenarios pass (95%). Scenario 17 (very heavy noise) fails:
  the noise is strong enough that the correlation peak lands in the wrong
  place. Hard cases like it are included on purpose.
- This tests direction only. Distance is covered separately (#16).

Run these from the `prototype` folder:

| Command | What it does |
|---|---|
| `python -m locator.scenarios` | Prints the result of each scenario, then the overall pass rate. Exits with an error if fewer than 80% pass. |
| `python -m locator.demo_direction` | Opens the interactive demo window. |
| `python -m locator.demo_direction --scenario 17` | Opens the demo on one scenario (1 to 20). |
| `python -m locator.demo_direction --summary` | Plots true against estimated angle for all 20 scenarios. |
| `python -m locator.demo_direction --angle 25 --noise 0.5 --out demo.png` | Saves a picture instead of opening a window. |

In the demo window:

- **Left:** the hydrophones, the true direction (green), the estimate (red),
  and the arithmetic that turns the delay into an angle.
- **Top right:** the two noisy recordings.
- **Bottom right:** the cross-correlation curve; its peak is the delay between
  the two hydrophones.
- **Sliders** change the true angle, the noise level, and the spacing.
  **New noise** repeats the test with different random noise, and
  **Next scenario** steps through the 20 scenarios, marking each PASS or FAIL.

Limits: all sound is simulated, with independent random noise, one source, and
a direct path (no echoes). The demo window needs a computer with a graphical
display.

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

## AI Detector (#10, #12)

Detects when a whale noise has been heard by training the ai
to understand the noises whales make, as well as seperating
these noises from other ones that could also be caught in
the recording, such as from boats or the ambient ocean noises.

| File | What it does |
|---|---|
| `ai-detector/whale_converter.py` | Converts audio files (.ogg, .flac, .wav, or .mp3) from a given folder into a .npz file for the ai to understand. How each whales data is captured varies (frequency, length of each individual sound in song) so the settings vary for the species. Stores the data in a folder located at ./data/<species>/whale |
| `ai-detector/boat_converter.py` | Works the same as whale_converter, but teaches the ai to recognize boat noises; also needs its settings to match that of the whale species so the ai can understand how it sounds at the differing frequency. Stores data in folder at ./data/<species>/boat |
| `ai-detector/ambient_converter.py` | Works the same as boat_converter, but teaches the ai to recognize ambient noises. Stores data in folder at ./data/<species>/ambient |
| `ai-detector/whale_detector.py` | Used to both train or detect whale calls, based on the command following it. When used to train, it takes data from the previously created folders based on the whale species and creates a model called <species>.pt. When used to detect, uses the provided model to try and detect the whale calls it is hearing. |
| `ai-detector/pipeline.sh` | Runs the above commands automatically, fitting the settings to match those of the species. --species <species> is how to label the species, or use all to train for all species. Data is automatically searched for in ./data, however the path can be defined using --data. Data file must have at least three folders, <species>_raw, boat_raw, and ambient_raw. |
| `ai-detector/evaluate_detector.py` | Evaluates the given model by providing it with brand new audio. Execution would look like python evaluate_detector.py --model model.pt --boat ./data/boat --extra_neg ./data/ambient --split test --out eval_out, with the model/folders reflecting that of what they're actually named or located. |

## How the Settings were Chosen

Each of these whales have their calls exist at different frequencies, so
changing the settings to match the given whale is important. While humpback
whales can reach up to 8 kHz, we decided to start training with up to 4 kHz
as to keep the cost of training cheaper. The individual noises in their songs
are also quick so a window of 4 seconds was chosen to capture all of it.
Blue whales have a much easier range to accommodate, as their calls are typically
in the 15-40 Hz range. However, their calls noises tend to last about 15 to 20
seconds, so they needed a longer window of 20 seconds. Lastly, the right whale
commonly makes a noise known as an upcall, that ranges between ~50-400 Hz. 
These noises are also shorter in duration like the humpback whale, so it has a
5 second window for capturing this audio.

## What it Proves - Whale Calls Distinct from Boats or Ambient Noise (#10, #12)

- `evaluate_detector.py` compares the provided audio against the model to test
  how well it can differentiate whale calls versus boats and ambient noise.
  It returns how well it was able to detect a whale as well as return how
  much or little it ignored other whales/noises.

## References (format correctly later)

[1] https://pubs.aip.org/asa/jasa/article/151/4/2558/2838297/Acoustic-detection-range-of-right-whale-upcalls

[2] http://dosits.org/galleries/audio-gallery/marine-mammals/baleen-whales/north-atlantic-right-whale/

[3] https://dosits.org/galleries/audio-gallery/marine-mammals/baleen-whales/blue-whale/

[4] https://www.whoi.edu/oceanus/feature/frequency-ranges-of-marine-animal-sounds/

[5] https://www.bodyglovehawaii.com/blog/all-about-whale-song/
