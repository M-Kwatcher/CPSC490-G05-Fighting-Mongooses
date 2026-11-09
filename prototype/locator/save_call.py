import datetime
import os
import wave

def save_call(audio_bytes, hydrophone_id, sample_rate, output_dir="calls"):
    os.makedirs(output_dir, exist_ok=True)

    # Use a Windows-safe timestamp ( no colons)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    filename = f"{timestamp}_H{hydrophone_id}.wav"
    filepath = os.path.join(output_dir, filename)

    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)          # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(audio_bytes)

    return {
        "timestamp": timestamp,
        "hydrophone_id": hydrophone_id,
        "filepath": filepath,
    }