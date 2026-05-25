"""Cursor hook stdin decoding and JSON parse (Windows-safe)."""

from __future__ import annotations

import json
import os
import re

_INVALID_JSON_ESCAPE = re.compile(r'(?<!\\)\\(?!["\\/bfnrtu])')


def decode_hook_bytes(raw: bytes) -> str:
    if not raw:
        return ""
    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16-le")
    if raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16-be")
    if len(raw) >= 4 and raw[0] in (0x7B, 0x20, 0x09) and raw[1] == 0:
        return raw.decode("utf-16-le")
    return raw.decode("utf-8-sig", errors="replace")


def loads_hook_json(raw: str) -> dict:
    text = (raw or "").strip()
    if not text:
        return _apply_env_overrides({})
    try:
        obj = json.loads(text)
        return _apply_env_overrides(obj if isinstance(obj, dict) else {})
    except json.JSONDecodeError:
        fixed = _INVALID_JSON_ESCAPE.sub(r"\\\\", text)
        obj = json.loads(fixed)
        return _apply_env_overrides(obj if isinstance(obj, dict) else {})


def _apply_env_overrides(hook: dict) -> dict:
    forced_adapter = os.environ.get("AFTERTONE_FORCE_ADAPTER", "").strip().lower()
    if forced_adapter and not hook.get("adapter"):
        hook = dict(hook)
        hook["adapter"] = forced_adapter
    return hook
