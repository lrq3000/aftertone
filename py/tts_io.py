"""
Shared audio playback helpers for Supertonic TTS (CLI and daemon).

Prefers sounddevice (PortAudio). Falls back to ALSA `aplay` on Linux when
PortAudio is unavailable.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

import numpy as np
import soundfile as sf


def resolve_playback() -> str:
    try:
        import sounddevice as sd  # noqa: F401
    except (ImportError, OSError):
        pass
    else:
        return "sounddevice"
    if shutil.which("aplay"):
        return "aplay"
    return ""


def play_audio_blocking(audio: np.ndarray, sample_rate: int, backend: str) -> None:
    if audio.size == 0:
        return
    if backend == "sounddevice":
        import sounddevice as sd

        sd.play(audio.astype(np.float32, copy=False), sample_rate, blocking=True)
        return
    if backend == "aplay":
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        try:
            sf.write(path, audio, sample_rate, subtype="PCM_16")
            subprocess.run(["aplay", "-q", path], check=False)
        finally:
            if os.path.isfile(path):
                os.unlink(path)
        return
    raise RuntimeError(f"unknown playback backend: {backend}")
