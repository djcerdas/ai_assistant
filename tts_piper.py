import subprocess
import os
from datetime import datetime

# Piper TTS binary and English voice model paths
PIPER_BIN = "/opt/ai_assistant/tools/piper_cli/piper"
PIPER_MODEL = "/opt/ai_assistant/models/piper/voice.onnx"
PIPER_CONFIG = "/opt/ai_assistant/models/piper/voice.onnx.json"


def speak(text: str) -> None:
    """
    Convert text to speech using offline Piper TTS and play the audio.
    """
    # Generate a unique filename to avoid collisions between TTS calls
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    wav = f"/tmp/tts_{ts}.wav"

    cmd = [
        PIPER_BIN,
        "--model", PIPER_MODEL,
        "--config", PIPER_CONFIG,
        "--output_file", wav
    ]

    # Run Piper and pass text through stdin
    result = subprocess.run(
        cmd,
        input=text.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Fail fast if TTS generation fails
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="ignore"))

    # Play generated audio and clean up temporary file
    subprocess.run(["aplay", "-q", wav], check=False)
    try:
        os.remove(wav)
    except OSError:
        pass
