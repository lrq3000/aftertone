"""Tests for tts_daemon_ctl port / voice verification helpers."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tts_daemon_ctl as ctl


def test_voice_style_abs_from_voice_type(tmp_path, monkeypatch):
    hooks = tmp_path / ".cursor" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "speak_summary.toml").write_text(
        'voice_type = "M3"\nvoice_style = ""\nport = 8765\n',
        encoding="utf-8",
    )
    cfg = ctl._load_hook_config(tmp_path)
    got = ctl._voice_style_abs(tmp_path, cfg)
    assert got.name == "M3.json"
    assert "voice_styles" in str(got)


def test_verify_daemon_ready_rejects_wrong_voice(monkeypatch, tmp_path):
    voice = tmp_path / "M3.json"
    voice.write_text("{}", encoding="utf-8")
    other = tmp_path / "F2.json"
    other.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(ctl, "_listener_pid_on_port", lambda _port: 12345)
    monkeypatch.setattr(
        ctl,
        "_fetch_healthz",
        lambda _port: {"voice": str(other.resolve()), "ready": True},
    )
    ok, err, listener = ctl._verify_daemon_ready(8765, voice)
    assert not ok
    assert "F2" in err
    assert listener == 12345


def test_verify_daemon_ready_accepts_matching_voice(monkeypatch, tmp_path):
    voice = tmp_path / "M3.json"
    voice.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(ctl, "_listener_pid_on_port", lambda _port: 42)
    monkeypatch.setattr(
        ctl,
        "_fetch_healthz",
        lambda _port: {"voice": str(voice.resolve()), "ready": True},
    )
    ok, err, listener = ctl._verify_daemon_ready(8765, voice)
    assert ok, err
    assert listener == 42
