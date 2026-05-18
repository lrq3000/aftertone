#!/usr/bin/env python3
"""Rewrite Cursor hook stdin as UTF-8; parse JSON with Windows path escape fixes."""

from __future__ import annotations

import sys
from pathlib import Path

from aftertone.hook_json import decode_hook_bytes


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: hook_stdin_normalize.py <path>", file=sys.stderr)
        raise SystemExit(2)
    path = Path(sys.argv[1])
    raw = path.read_bytes()
    if not raw.strip():
        return
    text = decode_hook_bytes(raw).lstrip("\ufeff")
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
