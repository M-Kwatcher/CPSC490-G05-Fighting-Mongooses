"""Tests for #16: estimate the distance of a sound within 10%."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from locator import config  # noqa: E402
from locator.locate import estimateDistance, predictedDelays  # noqa: E402
from locator.simulate import makeSound, recordAtHydrophones, sourceAtAngle  # noqa: E402

ARRAY = config.DISTANCE_HYDROPHONES


def testPredictedDelaysHandExample():
    """Notes problem 14: H1 (0,0), H2 (10,0), H3 (0,10), source at (30,40)."""
    delays = predictedDelays((30, 40), [(0, 0), (10, 0), (0, 10)])
    assert delays[0] * 1000 == pytest.approx(-3.519, abs=0.001)
    assert delays[1] * 1000 == pytest.approx(-5.049, abs=0.001)


def testPredictedDelaysZeroAtEqualDistance():
    """A source the same distance from every hydrophone gives no delays."""
    delays = predictedDelays((25, 25), ARRAY)
    assert list(delays) == pytest.approx([0, 0, 0])


@pytest.mark.parametrize("trueDistance", [25, 50, 100, 200, 500])
@pytest.mark.parametrize("angleDeg", [-60, 0, 45, 120])
def testDistanceWithin10PercentWithNoise(trueDistance, angleDeg):
    """Acceptance criterion: within 10% of the true distance in a simulated setup."""
    sound = makeSound(0.05)
    source = sourceAtAngle(angleDeg, trueDistance, ARRAY)
    recordings = recordAtHydrophones(sound, source, noiseLevel=0.3, hydrophones=ARRAY,
                                     seed=trueDistance + angleDeg + 100)
    estimate = estimateDistance(recordings, ARRAY)
    assert abs(estimate - trueDistance) / trueDistance <= 0.10