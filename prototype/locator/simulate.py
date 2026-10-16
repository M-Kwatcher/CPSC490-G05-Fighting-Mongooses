"""Makes fake hydrophone recordings with a known source position (#15, #16)."""

import numpy as np
from scipy.signal import chirp

from locator.config import SAMPLE_RATE


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


def recordAtHydrophones(sound, sourceXy, noiseLevel):
    """Return one delayed, noisy copy of the sound per hydrophone."""
    raise NotImplementedError