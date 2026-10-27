"""Shared settings for the locator. Change values here only."""

SPEED_OF_SOUND = 1500.0   # m/s, seawater (#18)
SAMPLE_RATE = 48000       # samples per second

# Hydrophone positions in meters (x, y). Two for #15; a third gets added for #16.
HYDROPHONES = [(0.0, 0.0), (10.0, 0.0)]

# Four hydrophones in a 50 m square, for distance (#16). 10 m spacing is too
# small to measure distance within 10% past about 50 m (see the math notes).
DISTANCE_HYDROPHONES = [(0.0, 0.0), (50.0, 0.0), (0.0, 50.0), (50.0, 50.0)]