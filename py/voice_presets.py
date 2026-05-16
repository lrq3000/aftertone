"""Supertonic-3 built-in voice display names.

Labels match https://supertone-inc.github.io/supertonic-py/voices/
TOML and the daemon still use ids (M1, F2, …).
"""

from __future__ import annotations

# id -> short display name
VOICE_LABELS: dict[str, str] = {
    "M1": "Upbeat",
    "M2": "Deep calm",
    "M3": "Authoritative",
    "M4": "Gentle",
    "M5": "Warm",
    "F1": "Calm",
    "F2": "Cheerful",
    "F3": "Announcer",
    "F4": "Confident",
    "F5": "Soothing",
}

DEFAULT_VOICE_ORDER: tuple[str, ...] = (
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "M1",
    "M2",
    "M3",
    "M4",
    "M5",
)


def voice_display_name(preset_id: str) -> str:
    key = preset_id.strip().removesuffix(".json").upper()
    return VOICE_LABELS.get(key, key)


def voice_picker_label(preset_id: str) -> str:
    key = preset_id.strip().removesuffix(".json").upper()
    name = voice_display_name(key)
    if name == key:
        return key
    return f"{name} ({key})"


def voice_picker_line(preset_id: str) -> str:
    key = preset_id.strip().removesuffix(".json").upper()
    return f"{key}|{voice_picker_label(key)}"


def resolve_voice_preset_id(arg: str) -> str | None:
    """Map preset id or display name to canonical id (M1, F2, …)."""
    raw = arg.strip().removesuffix(".json")
    if not raw:
        return None
    key = raw.upper()
    if key in VOICE_LABELS:
        return key
    low = raw.lower()
    for pid, label in VOICE_LABELS.items():
        if low == label.lower():
            return pid
    return None
