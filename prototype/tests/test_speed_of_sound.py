import sys
from pathlib import Path
import pytest

# Add repo root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from locator import config  # noqa: E402
from locator.tdoa import delayToAngle  # noqa: E402


def testSpeedOfSoundIsSeawater():
    assert config.SPEED_OF_SOUND == 1500.0


def testDelayToAngleUsesSeawaterSpeed():
    # 3.33 ms at 10 m spacing is 30 degrees only at 1,500 m/s (343 m/s would give ~6.6)
    assert delayToAngle(1 / 300, 10) == pytest.approx(30.0)
