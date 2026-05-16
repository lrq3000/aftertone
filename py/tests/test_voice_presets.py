"""Tests for voice_presets display names."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from voice_presets import resolve_voice_preset_id, voice_picker_label


def test_picker_label():
    assert voice_picker_label("F4") == "Confident (F4)"
    assert voice_picker_label("M1") == "Upbeat (M1)"


def test_resolve_by_display_name():
    assert resolve_voice_preset_id("Confident") == "F4"
    assert resolve_voice_preset_id("f4") == "F4"
    assert resolve_voice_preset_id("Upbeat") == "M1"


def test_resolve_unknown():
    assert resolve_voice_preset_id("not-a-voice") is None
