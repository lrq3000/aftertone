#!/usr/bin/env python3
"""Cross-platform Aftertone v2 CLI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from aftertone.config import cfg_enabled, load_config, summary_mode
from aftertone.doctor import run_doctor
from aftertone.paths import config_path, install_root, state_dir


def _repo(explicit: Path | None) -> Path:
    return install_root(explicit)


def _run_py_module(repo: Path, script: str, *args: str) -> int:
    py_dir = repo / "py"
    cmd = [sys.executable, str(py_dir / script), *args]
    return subprocess.call(cmd, cwd=str(py_dir))


def _run_uv(repo: Path, script: str, *args: str) -> int:
    py_dir = repo / "py"
    return subprocess.call(
        ["uv", "run", "python", script, *args],
        cwd=str(py_dir),
    )


def _invoke(repo: Path, script: str, *args: str) -> int:
    if (repo / "py" / ".venv").is_dir():
        return _run_uv(repo, script, *args)
    return _run_py_module(repo, script, *args)


def cmd_on(args: argparse.Namespace) -> int:
    return _invoke(_repo(args.repo_root), "speak_summary_toggle.py", "on")


def cmd_off(args: argparse.Namespace) -> int:
    return _invoke(_repo(args.repo_root), "speak_summary_toggle.py", "off")


def cmd_toggle(args: argparse.Namespace) -> int:
    return _invoke(_repo(args.repo_root), "speak_summary_toggle.py", "toggle")


def cmd_status(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    cfg = load_config(repo)
    port_file = state_dir(repo) / "tts-daemon.port"
    port = 8765
    if port_file.is_file():
        try:
            port = int(port_file.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    daemon = "down"
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=0.5) as r:
            if r.status == 200:
                daemon = "up"
    except (urllib.error.URLError, OSError):
        pass
    print(
        json.dumps(
            {
                "tts_enabled": cfg_enabled(cfg),
                "summary_mode": summary_mode(cfg),
                "lang": cfg.get("lang", "en"),
                "voice_type": cfg.get("voice_type", ""),
                "daemon": daemon,
                "port": port,
                "install_root": str(repo),
            },
            indent=2,
        )
    )
    return 0


def cmd_restart(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    return _invoke(repo, "tts_daemon_ctl.py", "restart", "--repo-root", str(repo))


def cmd_repair(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    rc = _invoke(repo, "install_global_hooks.py", "--install-dir", str(repo))
    if rc != 0:
        return rc
    _invoke(repo, "speak_summary_toggle.py", "on")
    _set_summary_mode_auto(config_path(repo))
    _invoke(repo, "sync_spoken_rule_lang.py")
    return cmd_restart(args)


def _set_summary_mode_auto(toml_path: Path) -> None:
    if not toml_path.is_file():
        return
    text = toml_path.read_text(encoding="utf-8")
    if re.search(r"^\s*summary_mode\s*=", text, re.MULTILINE):
        text = re.sub(
            r"^(\s*)summary_mode\s*=\s*\S+.*$",
            r'\1summary_mode = "auto"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
    else:
        text = text.rstrip() + '\n\n# v2 default: tag when present, else auto-extract\nsummary_mode = "auto"\n'
    text = re.sub(
        r"^(\s*)only_speak_spoken_summary\s*=\s*true\s*$",
        r"\1only_speak_spoken_summary = false",
        text,
        count=1,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    toml_path.write_text(text, encoding="utf-8")


def cmd_speak(args: argparse.Namespace) -> int:
    repo = _repo(args.repo_root)
    cfg = load_config(repo)
    port = int(cfg.get("port", 8765))
    port_file = state_dir(repo) / "tts-daemon.port"
    if port_file.is_file():
        try:
            port = int(port_file.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    payload = {
        "text": args.text,
        "totalStep": int(cfg.get("total_step", 8)),
        "speed": float(cfg.get("speed", 1.0)),
        "lang": str(cfg.get("lang", "en")),
        "mode": str(cfg.get("mode", "queue")).lower(),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/say",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(resp.status)
            return 0
    except urllib.error.URLError as exc:
        print(f"speak failed: {exc}", file=sys.stderr)
        return 1


def cmd_doctor(args: argparse.Namespace) -> int:
    return run_doctor(args.repo_root)


def cmd_prepare(args: argparse.Namespace) -> int:
    from aftertone.config import load_config
    from aftertone.hook_json import decode_hook_bytes, loads_hook_json
    from aftertone.prepare import prepare_payload

    path = Path(args.hook_json)
    hook = loads_hook_json(decode_hook_bytes(path.read_bytes()))
    repo = _repo(args.repo_root)
    out = prepare_payload(hook, load_config(repo), repo)
    if out:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print("{}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aftertone", description="Aftertone v2 CLI")
    parser.add_argument("--repo-root", type=Path, default=None, help="Install root")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, fn, help_text in (
        ("on", cmd_on, "Enable spoken TTS"),
        ("off", cmd_off, "Disable spoken TTS"),
        ("toggle", cmd_toggle, "Toggle spoken TTS"),
        ("status", cmd_status, "Show config and daemon status"),
        ("restart", cmd_restart, "Restart TTS daemon"),
        ("repair", cmd_repair, "Re-register hooks and set v2 defaults"),
        ("doctor", cmd_doctor, "Diagnostics"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.set_defaults(func=fn)

    sp = sub.add_parser("speak", help="Speak text via daemon")
    sp.add_argument("text", help="Text to synthesize")
    sp.set_defaults(func=cmd_speak)

    pp = sub.add_parser("prepare", help="Prepare payload from hook JSON file")
    pp.add_argument("hook_json", help="Path to hook JSON")
    pp.set_defaults(func=cmd_prepare)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
