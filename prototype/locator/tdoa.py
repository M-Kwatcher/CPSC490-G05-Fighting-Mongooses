"""Time difference of arrival: delay between two recordings -> direction (#15)."""

import numpy as np
from scipy.signal import correlate, correlation_lags

from locator.config import SAMPLE_RATE, SPEED_OF_SOUND


def findDelay(signalA, signalB):
    """Return how many seconds signalB lags signalA, using cross-correlation.

    Positive = signalB heard the sound later. See notes section 6.
    """
    corr = correlate(signalB, signalA)
    lags = correlation_lags(len(signalB), len(signalA))
    delaySamples = lags[np.argmax(corr)]
    return delaySamples / SAMPLE_RATE


def delayToAngle(delayS, spacingM):
    """Return the direction in degrees.

    theta = arcsin(c * delay / d)
    c = speed of sound, delay = time gap, d = distance between hydrophones
    The ratio is clipped to [-1, 1] because noise can push it slightly past 1.
    """
    ratio = np.clip(SPEED_OF_SOUND * delayS / spacingM, -1.0, 1.0)
    return float(np.degrees(np.arcsin(ratio)))


def estimateAngle(recordingH1, recordingH2, spacingM):
    """Return the direction in degrees from two hydrophone recordings.

    Positive angles = the sound came from the H2 side (H2 heard it first).
    """
    delayS = findDelay(recordingH2, recordingH1)   # how much later H1 heard it
    return delayToAngle(delayS, spacingM)