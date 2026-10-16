"""Makes fake hydrophone recordings with a known source position (#15, #16)."""


def makeSound(durationS):
    """Return a short test sound (a chirp) as a NumPy array."""
    raise NotImplementedError


def recordAtHydrophones(sound, sourceXy, noiseLevel):
    """Return one delayed, noisy copy of the sound per hydrophone."""
    raise NotImplementedError