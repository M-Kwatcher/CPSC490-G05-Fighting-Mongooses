import numpy as np
from prototype.locator.config import SPEED_OF_SOUND
from prototype.locator.tdoa import delayToAngle

def test_delayToAngle_uses_seawater_speed():
    #Arrange
    delayS = 0.001 #1 millisecond delay
    spacingM = 1.0 # hydrophones 1 meter apart

    #Expected ratio = (c * delay) / spacing
    expected_ratio = SPEED_OF_SOUND * delayS / spacingM

    #Clip to [-1, 1] just like the function does
    expected_ratio = np.clip(expected_ratio, -1.0, 1.0)

    #Expected angle in degrees
    expected_angle = float(np.degrees(np.arcsin(expected_ratio)))

    #Act
    angle = delayToAngle(delayS, spacingM)

    #Assert
    assert abs(angle - expected_angle) < 1e-6