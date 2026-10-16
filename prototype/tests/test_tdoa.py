import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from locator import config  # noqa: E402


def testConfigLoads():
    assert config.SPEED_OF_SOUND == 1500.0