"""Time difference of arrival: delay between two recordings -> direction (#15)."""


def findDelay(signalA, signalB):
    """Return how many seconds signalB lags signalA, using cross-correlation."""
    raise NotImplementedError


def delayToAngle(delayS, spacingM):
    """Return the direction in degrees.

    theta = arcsin(c * delay / d)
    c = speed of sound, delay = time gap, d = distance between hydrophones
    """
    raise NotImplementedError