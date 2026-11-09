"""Estimate where a sound came from and how far away it is (#16)."""

import numpy as np
from scipy.optimize import least_squares

from locator.config import SPEED_OF_SOUND
from locator.tdoa import findDelay


def arrayCenter(hydrophones):
    """Return the (x, y) middle point of the hydrophones."""
    return (float(np.mean([h[0] for h in hydrophones])),
            float(np.mean([h[1] for h in hydrophones])))


def predictedDelays(sourceXy, hydrophones):
    """Return how much later (seconds) each hydrophone after the first hears
    a sound from sourceXy, compared to the first hydrophone.

    delay_i = (r_i - r_1) / c   (notes section 7)
    """
    distances = [np.hypot(sourceXy[0] - x, sourceXy[1] - y) for x, y in hydrophones]
    return np.array([(r - distances[0]) / SPEED_OF_SOUND for r in distances[1:]])

def measuredDelays(recordings):
    """Return how much later (seconds) each recording after the first heard the sound."""
    return np.array([findDelay(recordings[0], recording) for recording in recordings[1:]])


def estimatePosition(recordings, hydrophones):
    """Return the (x, y) that best explains the measured delays.

    least_squares nudges a guessed position until its predicted delays match
    the measured ones. It can get stuck on a wrong spot, so we start from
    guesses all around the array and keep the best fit.
    """
    measured = measuredDelays(recordings)
    centerX, centerY = arrayCenter(hydrophones)

    def mismatch(xy):
        return (predictedDelays(xy, hydrophones) - measured) * 1000   # in ms

    bestFit = None
    for angleDeg in range(0, 360, 30):
        for rangeM in (20, 100, 500):
            angleRad = np.radians(angleDeg)
            guess = [centerX + rangeM * np.sin(angleRad), centerY + rangeM * np.cos(angleRad)]
            fit = least_squares(mismatch, guess)
            if bestFit is None or fit.cost < bestFit.cost:
                bestFit = fit
    return (float(bestFit.x[0]), float(bestFit.x[1]))

def estimateDistance(recordings, hydrophones):
    """Return the distance (m) from the array center to the estimated source."""
    x, y = estimatePosition(recordings, hydrophones)
    centerX, centerY = arrayCenter(hydrophones)
    return float(np.hypot(x - centerX, y - centerY))