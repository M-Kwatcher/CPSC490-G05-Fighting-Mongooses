# Prototype

Proof-of-concept code for 〈project title〉. **Prototype v0 is due Sep 27** with
the proposal, and it grows every sprint; the Week-8 in-class check demos from
this folder.

This example implements the login slice behind story
[#3](../../../issues/3) and task [#5](../../../issues/5) — deliberately tiny,
because a prototype exists to answer one risky question, not to be the
product. **Replace it with yours** and keep the shape: a small module, a test
per acceptance criterion, and run instructions below that work on a machine
that has never seen your project.

## How to run

```bash
cd prototype
python login.py                 # smoke run: prints a truncated session token
```

## How to test
```bash
cd prototype
pip install pytest              # once
python -m pytest tests -q       # 4 tests
```

CI runs exactly these tests on every pull request (job **Prototype build &
tests**). If you use Node instead of Python, put a `package.json` here with a
`test` script and CI will detect and run that instead.

## What it proves

That credentials can be checked and a session token issued, with unknown-user
and wrong-password failures indistinguishable to the caller — the riskiest
assumption in 〈the epic this belongs to〉.

## Status

| Sprint | Increment |
|---|---|
| v0 (Sep 27) | login check + 4 tests (this example) |
| Sprint 1 | 〈what you added〉 |
| Sprint 2 | locator: direction from 2 hydrophones (#15) + 17 tests |


## Locator (#15, #16)

Estimates where a whale call came from using the time difference of arrival
(TDOA) between hydrophones. All settings (speed of sound, sample rate,
hydrophone positions) live in `locator/config.py`.

### How to run

```bash
cd prototype
python -m locator.demo_delay     # plots a test sound and a copy 160 samples later
```

### How to test

```bash
cd prototype
pip install -r requirements.txt pytest   # once
python -m pytest tests -q
```

### What it proves (#15)

- `findDelay` measures the delay between two recordings with cross-correlation.
- `delayToAngle` turns that delay into a direction: θ = arcsin(c · Δt / d).
- In a simulated two-hydrophone setup (10 m apart, 1,500 m/s, 48 kHz), the
  estimated direction is within 15° of the true direction from −80° to 80°,
  with noise as loud as the call itself.
- Known limit: two hydrophones cannot tell front from back, so angles are
  reported on the front side.

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