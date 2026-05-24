#!/usr/bin/env python3
"""Register Aftertone user-level OpenCode plugin files."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def install_global_opencode(*, install_dir: Path, dry_run: bool = False) -> None:
    install_dir = install_dir.expanduser().resolve()
    marker = install_dir / "py" / "speak_summary_prepare.py"
    if not marker.is_file():
        raise SystemExit(f"not an Aftertone install: {install_dir}")

    template_dir = install_dir / "scripts" / "opencode-global"
    plugin_src = template_dir / "aftertone-plugin.js"
    rule_src = template_dir / "spoken-summary.md"
    if not plugin_src.is_file() or not rule_src.is_file():
        raise SystemExit(f"missing templates under {template_dir}")

    user_opencode = Path.home() / ".config" / "opencode"
    plugin_dest = user_opencode / "plugins" / "aftertone.js"
    rule_dest = user_opencode / "rules" / "aftertone-spoken-summary.md"
    marker_dest = user_opencode / "aftertone-install-dir"

    if dry_run:
        print(f"would copy {plugin_src} -> {plugin_dest}")
        print(f"would copy {rule_src} -> {rule_dest}")
        print(f"would write {marker_dest} -> {install_dir}")
        return

    plugin_dest.parent.mkdir(parents=True, exist_ok=True)
    rule_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(plugin_src, plugin_dest)
    shutil.copy2(rule_src, rule_dest)
    marker_dest.write_text(f"{install_dir}\n", encoding="utf-8")

    print(f"Global OpenCode plugin: {plugin_dest}")
    print(f"Global OpenCode spoken-summary rule: {rule_dest}")
    print("Restart OpenCode so it reloads global plugins.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Install Aftertone user-level OpenCode plugin.")
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    install_global_opencode(install_dir=args.install_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
