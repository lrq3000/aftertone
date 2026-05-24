#!/usr/bin/env python3
"""Register Aftertone user-level Codex hooks (~/.codex/hooks.json)."""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import sys
import time
from pathlib import Path

_MARKER = "aftertone-codex-speak-on-stop"
_STOP_CMD = "bash __AFTERTONE_CODEX_STOP__"


def _strip_aftertone_entries(hooks: dict) -> dict:
    out: dict = {}
    for event, entries in hooks.items():
        if not isinstance(entries, list):
            out[event] = entries
            continue
        kept_groups: list = []
        for group in entries:
            if not isinstance(group, dict):
                kept_groups.append(group)
                continue
            inner = group.get("hooks")
            if not isinstance(inner, list):
                kept_groups.append(group)
                continue
            filtered = [
                h
                for h in inner
                if isinstance(h, dict) and _MARKER not in (h.get("command") or "")
            ]
            if filtered:
                g = dict(group)
                g["hooks"] = filtered
                kept_groups.append(g)
        if kept_groups:
            out[event] = kept_groups
    return out


def _merge_hooks(existing: dict, fragment: dict) -> dict:
    out = dict(existing)
    hooks = _strip_aftertone_entries(dict(out.get("hooks") or {}))
    for event, entries in (fragment.get("hooks") or {}).items():
        cur = list(hooks.get(event) or [])
        seen_cmds: set[str] = set()
        for group in cur:
            if not isinstance(group, dict):
                continue
            for hook in group.get("hooks") or []:
                if isinstance(hook, dict) and hook.get("command"):
                    seen_cmds.add(str(hook["command"]))
        for group in entries:
            if not isinstance(group, dict):
                continue
            new_group = dict(group)
            inner = []
            for hook in new_group.get("hooks") or []:
                if not isinstance(hook, dict):
                    continue
                cmd = hook.get("command")
                if cmd in seen_cmds:
                    continue
                inner.append(hook)
                if cmd:
                    seen_cmds.add(str(cmd))
            if inner:
                new_group["hooks"] = inner
                cur.append(new_group)
        hooks[event] = cur
    out["hooks"] = hooks
    return out


def _substitute_commands(obj: object, stop: str) -> object:
    if isinstance(obj, dict):
        return {k: _substitute_commands(v, stop) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute_commands(x, stop) for x in obj]
    if isinstance(obj, str):
        return obj.replace(_STOP_CMD, stop).replace("__AFTERTONE_CODEX_STOP__", stop)
    return obj


def install_global_codex(*, install_dir: Path, dry_run: bool = False) -> None:
    install_dir = install_dir.expanduser().resolve()
    marker = install_dir / "py" / "speak_summary_prepare.py"
    if not marker.is_file():
        raise SystemExit(f"not an Aftertone install: {install_dir}")

    template_dir = install_dir / "scripts" / "codex-global"
    wrapper_src = template_dir / "aftertone-codex-speak-on-stop.sh"
    fragment_src = template_dir / "hooks.json"
    if not wrapper_src.is_file() or not fragment_src.is_file():
        raise SystemExit(f"missing templates under {template_dir}")

    user_hooks = Path.home() / ".cursor" / "hooks"
    user_codex = Path.home() / ".codex"
    hooks_json = user_codex / "hooks.json"
    dest_wrapper = user_hooks / "aftertone-codex-speak-on-stop.sh"
    stop_cmd = f'bash "{dest_wrapper.resolve()}"'

    if dry_run:
        print(f"would copy {wrapper_src} -> {dest_wrapper}")
        print(f"would merge {hooks_json}")
        return

    user_hooks.mkdir(parents=True, exist_ok=True)
    user_codex.mkdir(parents=True, exist_ok=True)
    shutil.copy2(wrapper_src, dest_wrapper)
    if sys.platform != "win32":
        dest_wrapper.chmod(
            dest_wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )

    fragment = json.loads(fragment_src.read_text(encoding="utf-8-sig"))
    fragment = _substitute_commands(fragment, stop_cmd)
    if hooks_json.is_file():
        existing = json.loads(hooks_json.read_text(encoding="utf-8-sig"))
        backup = hooks_json.with_suffix(f".json.bak.{int(time.time())}")
        shutil.copy2(hooks_json, backup)
        merged = _merge_hooks(existing, fragment)
        print(f"backup: {backup}")
    else:
        merged = fragment

    hooks_json.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"Global Codex hooks: {hooks_json}")
    print("In Codex: run `/hooks` and trust the Aftertone Stop hook if prompted.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Aftertone user-level Codex hooks.")
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    install_global_codex(install_dir=args.install_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
