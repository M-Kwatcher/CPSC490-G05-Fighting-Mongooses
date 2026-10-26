"""Step 5 demo: make a test sound, delay a copy, and plot both."""

import matplotlib.pyplot as plt
import numpy as np

from locator.config import SAMPLE_RATE
from locator.simulate import delayBySamples, makeSound

sound = makeSound(0.05)                 # 50 ms test sound
delaySamples = 160                      # 160 samples = 3.33 ms -> 30 degrees
delayed = delayBySamples(sound, delaySamples)

timeMs = np.arange(len(sound)) / SAMPLE_RATE * 1000

fig, (top, bottom) = plt.subplots(2, 1, sharex=True)
top.plot(timeMs, sound)
top.set_title("H1 hears it first")
bottom.plot(timeMs, delayed, color="tab:orange")
bottom.set_title(f"H2 hears it {delaySamples} samples later")
bottom.set_xlabel("time (ms)")
plt.tight_layout()
plt.show()