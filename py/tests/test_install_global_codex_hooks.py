"""Tests for user-level Codex hook registration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install_global_codex_hooks import install_global_codex
from uninstall_global_hooks import uninstall_global


def _make_install(tmp_path: Path) -> Path:
    install = tmp_path / "aftertone"
    (install / "py").mkdir(parents=True)
    (install / "py" / "speak_summary_prepare.py").write_text("# stub\n", encoding="utf-8")
    tpl = install / "scripts" / "codex-global"
    tpl.mkdir(parents=True)
    (tpl / "aftertone-codex-speak-on-stop.sh").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
    (tpl / "hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "bash __AFTERTONE_CODEX_STOP__",
                                    "timeout": 30,
                                }
                            ]
                        }
                    ],
                    "SubagentStop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "bash __AFTERTONE_CODEX_STOP__",
                                    "timeout": 30,
                                }
                            ]
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    return install


def test_install_global_codex_merges_stop_hooks(tmp_path: Path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    existing = {
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {"type": "command", "command": "python keep_me.py", "timeout": 5}
                    ]
                }
            ]
        }
    }
    codex_dir = fake_home / ".codex"
    codex_dir.mkdir()
    (codex_dir / "hooks.json").write_text(json.dumps(existing), encoding="utf-8")

    install = _make_install(tmp_path)

    install_global_codex(install_dir=install)

    wrapper = fake_home / ".cursor" / "hooks" / "aftertone-codex-speak-on-stop.sh"
    assert wrapper.is_file()
    hooks = json.loads((codex_dir / "hooks.json").read_text(encoding="utf-8"))
    stop_commands = [
        h["command"]
        for group in hooks["hooks"]["Stop"]
        for h in group.get("hooks", [])
        if isinstance(h, dict)
    ]
    assert "python keep_me.py" in stop_commands
    assert any("aftertone-codex-speak-on-stop" in cmd for cmd in stop_commands)
    assert any(
        "aftertone-codex-speak-on-stop" in h["command"]
        for group in hooks["hooks"]["SubagentStop"]
        for h in group.get("hooks", [])
        if isinstance(h, dict)
    )


def test_uninstall_global_removes_codex_files_and_entries(tmp_path: Path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    install = _make_install(tmp_path)
    install_global_codex(install_dir=install)

    uninstall_global()

    assert not (fake_home / ".cursor" / "hooks" / "aftertone-codex-speak-on-stop.sh").exists()
    hooks_path = fake_home / ".codex" / "hooks.json"
    if hooks_path.exists():
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
        assert "aftertone-codex-speak-on-stop" not in json.dumps(hooks)
