"""Scenario test for the direction estimator.

Requirement: the locator is run against at least 20 different scenarios and
must estimate the direction correctly in at least 80% of them.

A scenario is one fixed case: a true direction, a noise level, and a hydrophone
spacing. Each is run once with a fixed random seed, so the result is the same
every time. A scenario passes when the estimated angle is within
TOLERANCE_DEG of the true angle.

    python -m locator.scenarios           print the report; exit code 1 if it fails
"""

import sys
from dataclasses import dataclass

from locator.simulate import makeSound, recordAtHydrophones, sourceAtAngle
from locator.tdoa import estimateAngle

TOLERANCE_DEG = 15.0        # a scenario passes within this error: check against Objective 2.1 in the proposal
REQUIRED_PASS_RATE = 0.80   # at least 80% of scenarios must pass
REQUIRED_SCENARIOS = 20     # run at least 20 different scenarios
RANGE_M = 2000.0            # distance to the fake whale (far away, so the math assumptions hold)
CALL_DURATION_S = 0.05      # length of the test sound, same as smoke.py


@dataclass(frozen=True)
class Scenario:
    """One test case. Noise level is the standard deviation; the call peaks at 1."""

    name: str
    trueAngleDeg: float
    noiseLevel: float
    spacingM: float = 10.0
    seed: int = 0


def _scenarios():
    """Build the scenario list. Chosen in advance, as a mix of easy and hard cases."""
    rows = [
        # quiet and clean, angles spread across the range
        ("clean, far left", -75, 0.0, 10.0),
        ("clean, left", -45, 0.0, 10.0),
        ("clean, slightly left", -15, 0.0, 10.0),
        ("clean, straight ahead", 0, 0.0, 10.0),
        ("light noise, slightly right", 20, 0.3, 10.0),
        ("light noise, right", 50, 0.3, 10.0),
        ("light noise, far right", 80, 0.3, 10.0),
        # moderate noise, including wide angles where error grows
        ("moderate noise, far left", -80, 0.5, 10.0),
        ("moderate noise, left", -60, 1.0, 10.0),
        ("moderate noise, right", 35, 1.0, 10.0),
        ("moderate noise, wide right", 65, 1.0, 10.0),
        # close to the limit of what the method handles
        ("heavy noise, left", -50, 1.5, 10.0),
        ("heavy noise, right", 25, 1.5, 10.0),
        ("heavy noise, wide right", 70, 1.5, 10.0),
        # beyond the method's reliable range: failures are expected here
        ("very heavy noise, near ahead", 10, 2.0, 10.0),
        ("very heavy noise, left", -30, 2.0, 10.0),
        ("very heavy noise, right", 55, 2.0, 10.0),
        # different hydrophone spacings
        ("5 m spacing, moderate noise", 40, 1.0, 5.0),
        ("20 m spacing, moderate noise", -20, 1.0, 20.0),
        ("1 m spacing, light noise", 60, 0.5, 1.0),
    ]
    return [Scenario(name, angle, noise, spacing, seed=1000 + i)
            for i, (name, angle, noise, spacing) in enumerate(rows)]


SCENARIOS = _scenarios()


def runScenario(scenario):
    """Run one scenario. Returns (estimatedAngleDeg, errorDeg, passed)."""
    hydrophones = [(0.0, 0.0), (scenario.spacingM, 0.0)]
    sound = makeSound(CALL_DURATION_S)
    source = sourceAtAngle(scenario.trueAngleDeg, RANGE_M, hydrophones)
    h1, h2 = recordAtHydrophones(sound, source, scenario.noiseLevel, hydrophones,
                                 seed=scenario.seed)
    estimate = estimateAngle(h1, h2, scenario.spacingM)
    error = estimate - scenario.trueAngleDeg
    return estimate, error, abs(error) <= TOLERANCE_DEG


def runAll(scenarios=SCENARIOS):
    """Run every scenario. Returns a list of (scenario, estimate, error, passed)."""
    return [(s, *runScenario(s)) for s in scenarios]


def passRate(results):
    """Return the fraction of scenarios that passed."""
    return sum(1 for r in results if r[3]) / len(results)


def meetsRequirement(results):
    """True when there are enough scenarios and enough of them passed."""
    return len(results) >= REQUIRED_SCENARIOS and passRate(results) >= REQUIRED_PASS_RATE


def printReport(results):
    """Print one line per scenario, then the overall result."""
    print(f"Direction scenarios (pass = within {TOLERANCE_DEG:g} degrees)\n")
    print(f"{'#':>2}  {'scenario':<31} {'true':>6} {'noise':>6} {'space':>6} "
          f"{'estimate':>9} {'error':>7}  result")
    for i, (s, estimate, error, passed) in enumerate(results, start=1):
        print(f"{i:>2}  {s.name:<31} {s.trueAngleDeg:6.0f} {s.noiseLevel:6.2f} "
              f"{s.spacingM:5.0f}m {estimate:9.1f} {error:7.1f}  {'pass' if passed else 'FAIL'}")
    passed = sum(1 for r in results if r[3])
    rate = 100 * passRate(results)
    print(f"\n{passed} of {len(results)} scenarios passed ({rate:.0f}%); "
          f"requirement is at least {REQUIRED_PASS_RATE:.0%} of {REQUIRED_SCENARIOS}+ scenarios")
    print("REQUIREMENT MET" if meetsRequirement(results) else "REQUIREMENT NOT MET")


def main():
    results = runAll()
    printReport(results)
    sys.exit(0 if meetsRequirement(results) else 1)


if __name__ == "__main__":
    main()
