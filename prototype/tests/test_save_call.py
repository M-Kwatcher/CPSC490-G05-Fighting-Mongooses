import os
import numpy as np
from prototype.locator.save_call import save_call
from prototype.locator.simulate import detect_and_save_calls, SAMPLE_RATE

def test_save_call_creates_file(tmp_path):
    audio_bytes = b"\x00\x01\x02\x03" * 100
    hydrophone_id = 3

    record = save_call(
        audio_bytes=audio_bytes,
        hydrophone_id=hydrophone_id,
        sample_rate=SAMPLE_RATE,
        output_dir=str(tmp_path),
    )

    assert os.path.exists(record["filepath"])
    assert record["hydrophone_id"] == hydrophone_id
    assert "timestamp" in record

def test_detect_and_save_calls(tmp_path):
    loud = np.ones(1000) * 0.5
    quiet = np.ones(1000) * 0.01

    saved = detect_and_save_calls(
        recordings=[loud, quiet],
        hydrophone_ids=[0, 1],
        threshold=0.3,
    )

    assert len(saved) == 1
    assert saved[0]["hydrophone_id"] == 0