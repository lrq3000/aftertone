"""Tests for user-level OpenCode plugin registration."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from install_global_opencode_hooks import install_global_opencode
from uninstall_global_hooks import uninstall_global


def _make_install(tmp_path: Path) -> Path:
    install = tmp_path / "aftertone"
    (install / "py").mkdir(parents=True)
    (install / "py" / "speak_summary_prepare.py").write_text("# stub\n", encoding="utf-8")
    tpl = install / "scripts" / "opencode-global"
    tpl.mkdir(parents=True)
    (tpl / "aftertone-plugin.js").write_text(
        "export const AftertonePlugin = async () => ({})\n", encoding="utf-8"
    )
    (tpl / "spoken-summary.md").write_text(
        "# Aftertone spoken summaries\n", encoding="utf-8"
    )
    return install


def test_install_global_opencode_copies_plugin_and_rule(tmp_path: Path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    install = _make_install(tmp_path)

    install_global_opencode(install_dir=install)

    config = fake_home / ".config" / "opencode"
    plugin = config / "plugins" / "aftertone.js"
    rule = config / "rules" / "aftertone-spoken-summary.md"
    marker = config / "aftertone-install-dir"
    assert plugin.read_text(encoding="utf-8").startswith("export const AftertonePlugin")
    assert rule.read_text(encoding="utf-8").startswith("# Aftertone")
    assert marker.read_text(encoding="utf-8").strip() == str(install.resolve())


def test_uninstall_global_removes_opencode_files(tmp_path: Path, monkeypatch) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    install = _make_install(tmp_path)
    install_global_opencode(install_dir=install)

    uninstall_global()

    config = fake_home / ".config" / "opencode"
    assert not (config / "plugins" / "aftertone.js").exists()
    assert not (config / "rules" / "aftertone-spoken-summary.md").exists()
    assert not (config / "aftertone-install-dir").exists()
