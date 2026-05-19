#!/usr/bin/env python3
"""Remove Aftertone user-level Cursor hooks (~/.cursor/hooks.json)."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from install_global_hooks import _AFTER_AGENT, _CMD


def _remove_aftertone_hook_entries(hooks_data: dict) -> tuple[dict, int]:
    """Drop Aftertone afterAgentResponse entries; return (updated doc, removed count)."""
    out = dict(hooks_data)
    hooks = dict(out.get("hooks") or {})
    entries = list(hooks.get(_AFTER_AGENT) or [])
    kept = [e for e in entries if not (isinstance(e, dict) and e.get("command") == _CMD)]
    removed = len(entries) - len(kept)
    if kept:
        hooks[_AFTER_AGENT] = kept
    else:
        hooks.pop(_AFTER_AGENT, None)
    out["hooks"] = hooks
    return out, removed


def uninstall_global(*, dry_run: bool = False) -> None:
    user_cursor = Path.home() / ".cursor"
    user_hooks = user_cursor / "hooks"
    user_hooks_json = user_cursor / "hooks.json"

    hook_files = [
        user_hooks / "aftertone-install-dir",
        user_hooks / "aftertone-speak_summary.sh",
        user_hooks / "aftertone-root.sh",
    ]
    command_glob = "aftertone-*.md"
    rule_file = user_cursor / "rules" / "spoken-summary.mdc"

    if dry_run:
        print(f"would remove hook files under {user_hooks} (aftertone-*)")
        if user_hooks_json.is_file():
            print(f"would strip Aftertone entries from {user_hooks_json}")
        cmds = user_cursor / "commands"
        if cmds.is_dir():
            print(f"would remove {cmds}/{command_glob}")
        if rule_file.is_file():
            print(f"would remove {rule_file}")
        return

    user_hooks_json_exists = user_hooks_json.is_file()
    removed_hooks = 0
    if user_hooks_json_exists:
        existing = json.loads(user_hooks_json.read_text(encoding="utf-8"))
        updated, removed_hooks = _remove_aftertone_hook_entries(existing)
        if removed_hooks:
            backup = user_hooks_json.with_suffix(f".json.bak.{int(time.time())}")
            shutil.copy2(user_hooks_json, backup)
            if updated.get("hooks"):
                user_hooks_json.write_text(
                    json.dumps(updated, indent=2) + "\n", encoding="utf-8"
                )
            else:
                user_hooks_json.unlink()
            print(f"backup: {backup}")

    for path in hook_files:
        if path.is_file():
            path.unlink()
            print(f"removed: {path}")

    commands_dir = user_cursor / "commands"
    if commands_dir.is_dir():
        for cmd in sorted(commands_dir.glob(command_glob)):
            cmd.unlink()
            print(f"removed: {cmd}")

    if rule_file.is_file():
        rule_file.unlink()
        print(f"removed: {rule_file}")

    if removed_hooks:
        print(f"removed {removed_hooks} afterAgentResponse hook(s) from {user_hooks_json}")
    elif user_hooks_json_exists:
        print(f"no Aftertone hook entries in {user_hooks_json}")
    else:
        print(f"no {user_hooks_json} (nothing to edit)")


def main() -> None:
    p = argparse.ArgumentParser(
        description="Uninstall Aftertone user-level Cursor hooks."
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    uninstall_global(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
