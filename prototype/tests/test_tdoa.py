"""Tests for #15: estimate the direction of a sound within 15 degrees."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from locator import config  # noqa: E402
from locator.simulate import (  # noqa: E402
    delayBySamples, makeSound, recordAtHydrophones, sourceAtAngle)
from locator.tdoa import delayToAngle, estimateAngle, findDelay  # noqa: E402

SPACING = config.HYDROPHONES[1][0] - config.HYDROPHONES[0][0]   # 10 m


def testConfigLoads():
    assert config.SPEED_OF_SOUND == 1500.0


def testFindDelayKnownShift():
    sound = makeSound(0.05)
    delayed = delayBySamples(sound, 160)
    assert findDelay(sound, delayed) == pytest.approx(160 / config.SAMPLE_RATE)


def testFindDelaySignTellsWhoIsLater():
    sound = makeSound(0.05)
    delayed = delayBySamples(sound, 160)
    assert findDelay(delayed, sound) == pytest.approx(-160 / config.SAMPLE_RATE)


def testDelayToAngleKnownValues():
    assert delayToAngle(0.0, 10) == pytest.approx(0.0)
    assert delayToAngle(1 / 300, 10) == pytest.approx(30.0)    # 3.33 ms -> 30 deg
    assert delayToAngle(10 / 1500, 10) == pytest.approx(90.0)  # max delay


def testDelayToAngleClipsNoisyRatio():
    assert delayToAngle(0.0068, 10) == pytest.approx(90.0)     # ratio 1.02 -> 90


def testStraightAheadGivesNoDelay():
    sound = makeSound(0.05)
    h1, h2 = recordAtHydrophones(sound, sourceAtAngle(0, 2000), noiseLevel=0, seed=1)
    assert findDelay(h1, h2) == 0


@pytest.mark.parametrize("trueAngle", [-80, -60, -45, -30, -15, 0, 15, 30, 45, 60, 80])
def testAngleWithin15DegreesWithNoise(trueAngle):
    """Acceptance criterion: within 15 degrees in a simulated two-hydrophone setup."""
    sound = makeSound(0.05)
    source = sourceAtAngle(trueAngle, 2000)
    h1, h2 = recordAtHydrophones(sound, source, noiseLevel=0.3, seed=trueAngle + 100)
    estimate = estimateAngle(h1, h2, SPACING)
    assert abs(estimate - trueAngle) <= 15