"""Smoke run: one fake whale, check the locator end to end (no plots)."""

from locator.config import DISTANCE_HYDROPHONES, HYDROPHONES
from locator.locate import estimateDistance
from locator.simulate import makeSound, recordAtHydrophones, sourceAtAngle
from locator.tdoa import estimateAngle

sound = makeSound(0.05)

h1, h2 = recordAtHydrophones(sound, sourceAtAngle(30, 2000), noiseLevel=0.3, seed=1)
spacing = HYDROPHONES[1][0] - HYDROPHONES[0][0]
print(f"direction: {estimateAngle(h1, h2, spacing):.1f} deg (true 30)")

recordings = recordAtHydrophones(sound, sourceAtAngle(45, 100, DISTANCE_HYDROPHONES),
                                 noiseLevel=0.3, hydrophones=DISTANCE_HYDROPHONES, seed=1)
print(f"distance: {estimateDistance(recordings, DISTANCE_HYDROPHONES):.1f} m (true 100)")
print("smoke run OK")