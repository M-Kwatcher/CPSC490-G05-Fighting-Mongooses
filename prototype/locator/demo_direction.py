"""Demo: how two hydrophones tell which direction a sound came from (#17).

A fake whale call is placed at a chosen direction, two simulated hydrophones
record it with noise, and the locator estimates the direction from the tiny
difference in arrival time. The plots show each step of that process.

    python -m locator.demo_direction                     interactive window
    python -m locator.demo_direction --scenario 17       start on scenario 17 of 20
    python -m locator.demo_direction --summary           true vs estimated for all scenarios
    python -m locator.demo_direction --angle 25 --noise 0.5 --out demo.png    save a picture

In the window: the sliders change the true angle, the noise, and the spacing
between the hydrophones. "New noise" repeats the test with different random
noise. "Next scenario" steps through the 20 test scenarios from scenarios.py.
"""

import argparse
from dataclasses import dataclass

import matplotlib
import numpy as np
from scipy.signal import correlate, correlation_lags

from locator.config import SAMPLE_RATE, SPEED_OF_SOUND
from locator.scenarios import (CALL_DURATION_S, RANGE_M, SCENARIOS, TOLERANCE_DEG,
                               passRate, runAll)
from locator.simulate import makeSound, recordAtHydrophones, sourceAtAngle
from locator.tdoa import estimateAngle, findDelay


@dataclass
class State:
    """Everything the picture depends on."""

    angleDeg: float = 30.0
    noiseLevel: float = 0.3
    spacingM: float = 10.0
    seed: int = 1
    scenarioIndex: int = None    # None = free play; otherwise an index into SCENARIOS


def loadScenario(state, index):
    """Copy a scenario's settings into the state."""
    s = SCENARIOS[index]
    state.angleDeg, state.noiseLevel, state.spacingM = s.trueAngleDeg, s.noiseLevel, s.spacingM
    state.seed, state.scenarioIndex = s.seed, index


def simulate(state):
    """Run the simulator for the state. Returns the recordings and the true delay."""
    hydrophones = [(0.0, 0.0), (state.spacingM, 0.0)]
    sound = makeSound(CALL_DURATION_S)
    source = sourceAtAngle(state.angleDeg, RANGE_M, hydrophones)
    h1, h2 = recordAtHydrophones(sound, source, state.noiseLevel, hydrophones, seed=state.seed)

    distances = [np.hypot(source[0] - x, source[1] - y) for x, y in hydrophones]
    closest = min(distances)
    delays = [round((r - closest) / SPEED_OF_SOUND * SAMPLE_RATE) for r in distances]
    trueLagSamples = delays[0] - delays[1]    # positive = H1 hears it later than H2
    return h1, h2, trueLagSamples


def drawGeometry(ax, state, estimate, delayS):
    """Top-down view: hydrophones, true direction, estimated direction, readout."""
    ax.clear()
    ax.set_aspect("equal")
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-0.95, 1.4)
    ax.axis("off")

    arc = np.radians(np.linspace(-90, 90, 100))
    ax.plot(np.sin(arc), np.cos(arc), color="lightgray", linewidth=1)
    ax.plot([-1.0, 1.0], [0, 0], color="lightgray", linewidth=1)
    ax.text(-1.3, 1.02, "front half only:\nfront and back look\nthe same to two\nhydrophones", fontsize=8,
            color="gray", va="top")

    trueRad, estRad = np.radians(state.angleDeg), np.radians(estimate)
    direction = np.array([np.sin(trueRad), np.cos(trueRad)])
    across = np.array([np.cos(trueRad), -np.sin(trueRad)])
    wave = [1.2 * direction + k * across for k in (-0.45, 0.45)]
    ax.plot([wave[0][0], wave[1][0]], [wave[0][1], wave[1][1]], "--", color="tab:cyan",
            linewidth=1.5, label="sound wavefront")

    ax.annotate("", xy=(np.sin(trueRad), np.cos(trueRad)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="tab:green", linewidth=2.5))
    ax.annotate("", xy=(0.85 * np.sin(estRad), 0.85 * np.cos(estRad)), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="tab:red", linewidth=2.5, linestyle="--"))
    ax.plot([], [], color="tab:green", linewidth=2.5, label=f"true direction {state.angleDeg:.1f}°")
    ax.plot([], [], color="tab:red", linewidth=2.5, linestyle="--", label=f"estimate {estimate:.1f}°")

    ax.plot([-0.12, 0.12], [0, 0], "o", color="black", markersize=9)
    ax.text(-0.12, -0.09, "H1", ha="center", va="top", fontweight="bold")
    ax.text(0.12, -0.09, "H2", ha="center", va="top", fontweight="bold")
    ax.text(0, -0.24, f"{state.spacingM:g} m apart (not to scale)", ha="center", fontsize=8, color="gray")
    ax.legend(loc="upper right", fontsize=8, frameon=False)

    ratio = SPEED_OF_SOUND * delayS / state.spacingM
    error = round(estimate - state.angleDeg, 1) + 0.0    # + 0.0 turns -0.0 into 0.0
    ok = abs(error) <= TOLERANCE_DEG
    clipped = "   (clipped: delay larger than physically possible)" if abs(ratio) > 1 else ""
    lines = [
        f"delay H1 vs H2: {delayS * SAMPLE_RATE:.0f} samples = {delayS * 1000:.3f} ms",
        f"angle = arcsin(c x delay / d) = arcsin({SPEED_OF_SOUND:.0f} x {delayS:.5f} / {state.spacingM:g})",
        f"      = arcsin({ratio:.3f}) = {estimate:.1f}°{clipped}",
        f"error {error:+.1f}°   {'within' if ok else 'OUTSIDE'} the {TOLERANCE_DEG:g}° target",
    ]
    ax.text(0, -0.40, "\n".join(lines), ha="center", va="top", fontsize=9, family="monospace",
            color="black" if ok else "tab:red")


def drawSignals(h1Ax, h2Ax, h1, h2):
    """The two recordings the hydrophones made."""
    timeMs = np.arange(len(h1)) / SAMPLE_RATE * 1000
    limit = max(np.max(np.abs(h1)), np.max(np.abs(h2)), 1.0) * 1.05
    for ax, data, name, color in ((h1Ax, h1, "H1 recording", "tab:blue"),
                                  (h2Ax, h2, "H2 recording", "tab:orange")):
        ax.clear()
        ax.plot(timeMs, data, color=color, linewidth=0.7)
        ax.set_ylim(-limit, limit)
        ax.set_title(name, fontsize=9, loc="left")
        ax.set_ylabel("amplitude", fontsize=8)
    h1Ax.set_xticklabels([])
    h2Ax.set_xlabel("time (ms)")


def drawCorrelation(ax, h1, h2, trueLagSamples, spacingM):
    """How well the recordings line up at each shift; the peak is the delay."""
    corr = correlate(h1, h2)
    lags = correlation_lags(len(h1), len(h2))
    peakLag = lags[np.argmax(corr)]
    lagMs = lags / SAMPLE_RATE * 1000
    limitMs = spacingM / SPEED_OF_SOUND * 1000          # largest delay physics allows

    ax.clear()
    ax.axvspan(-limitMs, limitMs, color="lightgray", alpha=0.35, label="possible delays (±d/c)")
    ax.plot(lagMs, corr / np.max(np.abs(corr)), color="black", linewidth=0.8)
    ax.axvline(trueLagSamples / SAMPLE_RATE * 1000, color="tab:green", linewidth=2, label="true delay")
    ax.plot(peakLag / SAMPLE_RATE * 1000, 1.0, "v", color="tab:red", markersize=9, label="peak = estimate")
    ax.set_xlim(-1.6 * limitMs, 1.6 * limitMs)
    ax.set_ylim(-1.05, 1.45)       # headroom so the legend does not cover the peak
    ax.set_title("cross-correlation: how well H1 and H2 match at each shift", fontsize=9, loc="left")
    ax.set_xlabel("shift of H1 relative to H2 (ms)")
    ax.set_ylabel("match", fontsize=8)
    ax.legend(fontsize=7, loc="upper left", ncol=3)


def redraw(fig, axes, state):
    """Redraw every panel for the current state."""
    h1, h2, trueLag = simulate(state)
    estimate = estimateAngle(h1, h2, state.spacingM)
    delayS = findDelay(h2, h1)

    drawGeometry(axes["geometry"], state, estimate, delayS)
    drawSignals(axes["h1"], axes["h2"], h1, h2)
    drawCorrelation(axes["corr"], h1, h2, trueLag, state.spacingM)

    if state.scenarioIndex is None:
        title = "Direction from two hydrophones (free play)"
    else:
        s = SCENARIOS[state.scenarioIndex]
        error = abs(estimate - state.angleDeg)
        verdict = "PASS" if error <= TOLERANCE_DEG else "FAIL"
        title = f"Scenario {state.scenarioIndex + 1} of {len(SCENARIOS)}: {s.name}  -  {verdict}"
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.canvas.draw_idle()


def buildWindow(state):
    """Create the figure with its panels, sliders, and buttons."""
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Button, Slider

    fig = plt.figure(figsize=(13, 7.8))
    grid = fig.add_gridspec(3, 2, left=0.05, right=0.97, top=0.92, bottom=0.27,
                            wspace=0.18, hspace=0.6)
    axes = {"geometry": fig.add_subplot(grid[:, 0]), "h1": fig.add_subplot(grid[0, 1]),
            "h2": fig.add_subplot(grid[1, 1]), "corr": fig.add_subplot(grid[2, 1])}

    angleSlider = Slider(fig.add_axes([0.12, 0.17, 0.34, 0.03]), "angle (°)", -85, 85,
                         valinit=state.angleDeg)
    noiseSlider = Slider(fig.add_axes([0.12, 0.115, 0.34, 0.03]), "noise", 0.0, 3.0,
                         valinit=state.noiseLevel)
    spacingSlider = Slider(fig.add_axes([0.12, 0.06, 0.34, 0.03]), "spacing (m)", 1, 20,
                           valinit=state.spacingM)
    newNoise = Button(fig.add_axes([0.58, 0.115, 0.15, 0.06]), "New noise")
    nextScenario = Button(fig.add_axes([0.76, 0.115, 0.18, 0.06]), "Next scenario")

    def onSlider(_):
        state.angleDeg, state.noiseLevel, state.spacingM = (
            angleSlider.val, noiseSlider.val, spacingSlider.val)
        state.scenarioIndex = None          # moving a slider leaves scenario mode
        redraw(fig, axes, state)

    def onNewNoise(_):
        state.seed += 1
        redraw(fig, axes, state)

    def onNextScenario(_):
        index = 0 if state.scenarioIndex is None else (state.scenarioIndex + 1) % len(SCENARIOS)
        loadScenario(state, index)
        for slider, value in ((angleSlider, state.angleDeg), (noiseSlider, state.noiseLevel),
                              (spacingSlider, state.spacingM)):
            slider.eventson = False          # set the slider without triggering onSlider
            slider.set_val(value)
            slider.eventson = True
        redraw(fig, axes, state)

    angleSlider.on_changed(onSlider)
    noiseSlider.on_changed(onSlider)
    spacingSlider.on_changed(onSlider)
    newNoise.on_clicked(onNewNoise)
    nextScenario.on_clicked(onNextScenario)

    fig._widgets = (angleSlider, noiseSlider, spacingSlider, newNoise, nextScenario)  # keep alive
    redraw(fig, axes, state)
    return fig


def buildSummary():
    """One picture for all scenarios: true angle against estimated angle."""
    import matplotlib.pyplot as plt

    results = runAll()
    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.plot([-90, 90], [-90, 90], color="gray", linewidth=1, label="perfect")
    ax.fill_between([-90, 90], [-90 - TOLERANCE_DEG, 90 - TOLERANCE_DEG],
                    [-90 + TOLERANCE_DEG, 90 + TOLERANCE_DEG], color="tab:green", alpha=0.15,
                    label=f"within {TOLERANCE_DEG:g}°")
    for i, (s, estimate, error, passed) in enumerate(results, start=1):
        ax.plot(s.trueAngleDeg, estimate, "o" if passed else "X", markersize=10 if passed else 13,
                color="tab:green" if passed else "tab:red")
        ax.annotate(str(i), (s.trueAngleDeg, estimate), textcoords="offset points",
                    xytext=(6, 5), fontsize=8)
    ax.set_xlabel("true angle (°)")
    ax.set_ylabel("estimated angle (°)")
    ax.set_xlim(-90, 90)
    ax.set_ylim(-90, 90)
    ax.set_aspect("equal")
    ax.legend(loc="upper left", fontsize=8)
    passed = sum(1 for r in results if r[3])
    ax.set_title(f"{passed} of {len(results)} scenarios passed ({100 * passRate(results):.0f}%)\n"
                 f"numbers match the scenario list; X = failed", fontsize=11)
    fig.tight_layout()
    return fig


def main():
    parser = argparse.ArgumentParser(description="Demo of direction estimation from two hydrophones.")
    parser.add_argument("--angle", type=float, default=30.0, help="true direction in degrees")
    parser.add_argument("--noise", type=float, default=0.3, help="noise level (std. deviation)")
    parser.add_argument("--spacing", type=float, default=10.0, help="hydrophone spacing in meters")
    parser.add_argument("--seed", type=int, default=1, help="random seed for the noise")
    parser.add_argument("--scenario", type=int, help="start on this scenario number (1 to 20)")
    parser.add_argument("--summary", action="store_true", help="show all scenarios in one plot")
    parser.add_argument("--out", help="save the picture to this file instead of opening a window")
    args = parser.parse_args()

    if args.out:
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    state = State(args.angle, args.noise, args.spacing, args.seed)
    if args.scenario is not None:
        if not 1 <= args.scenario <= len(SCENARIOS):
            parser.error(f"--scenario must be between 1 and {len(SCENARIOS)}")
        loadScenario(state, args.scenario - 1)

    fig = buildSummary() if args.summary else buildWindow(state)
    if args.out:
        fig.savefig(args.out, dpi=130)
        print(f"saved {args.out}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
