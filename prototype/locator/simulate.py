"""Makes fake hydrophone recordings with a known source position (#15, #16)."""

import numpy as np
from scipy.signal import chirp

from locator.config import HYDROPHONES, SAMPLE_RATE, SPEED_OF_SOUND


def makeSound(durationS):
    """Return a short test sound (a chirp) as a NumPy array."""
    t = np.arange(int(durationS * SAMPLE_RATE)) / SAMPLE_RATE
    sound = chirp(t, f0=500, f1=3000, t1=durationS)   # sweeps 500 Hz -> 3000 Hz
    fade = np.hanning(len(sound))                      # smooth start and end
    return sound * fade


def delayBySamples(sound, delaySamples):
    """Return a copy of the sound that starts delaySamples later (same length)."""
    padded = np.concatenate([np.zeros(delaySamples), sound])
    return padded[:len(sound)]


def sourceAtAngle(angleDeg, rangeM, hydrophones=HYDROPHONES):
    """Return the (x, y) of a source rangeM away from the array center.

    0 degrees = straight ahead (+y). Positive angles lean toward the last
    hydrophone in the list (+x side).
    """
    centerX = np.mean([h[0] for h in hydrophones])
    centerY = np.mean([h[1] for h in hydrophones])
    angleRad = np.radians(angleDeg)
    return (centerX + rangeM * np.sin(angleRad), centerY + rangeM * np.cos(angleRad))


def recordAtHydrophones(sound, sourceXy, noiseLevel, hydrophones=HYDROPHONES, seed=None):
    """Return one delayed, noisy copy of the sound per hydrophone.

    Each hydrophone hears the sound later the farther away it is. The closest
    hydrophone starts at sample 0; the others start later by
    (extra distance / speed of sound) seconds, rounded to whole samples.
    noiseLevel is the standard deviation of the added noise (sound peaks at 1).
    """
    rng = np.random.default_rng(seed)
    distances = [np.hypot(sourceXy[0] - x, sourceXy[1] - y) for x, y in hydrophones]
    closest = min(distances)
    delays = [round((r - closest) / SPEED_OF_SOUND * SAMPLE_RATE) for r in distances]

    totalLength = len(sound) + max(delays)
    recordings = []
    for delaySamples in delays:
        recording = np.zeros(totalLength)
        recording[delaySamples:delaySamples + len(sound)] = sound
        recording += rng.normal(0, noiseLevel, totalLength)
        recordings.append(recording)
    return recordings

