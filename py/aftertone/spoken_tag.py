"""Parse <spoken_summary> blocks from assistant text."""

from __future__ import annotations

import re

_SPOKEN_SUMMARY_OPEN = re.compile(r"<spoken_summary(\s[^>]*)?>", re.IGNORECASE)
_SPOKEN_SUMMARY_CLOSE = re.compile(r"</spoken_summary>", re.IGNORECASE)
_SPOKEN_STATE_ATTR = re.compile(
    r"""\bstate\s*=\s*["']?([a-z_]+)["']?""",
    flags=re.IGNORECASE,
)


def last_spoken_summary_span(raw: str) -> tuple[int, int, str, str | None] | None:
    closes = list(_SPOKEN_SUMMARY_CLOSE.finditer(raw))
    if not closes:
        return None
    close_m = closes[-1]
    close_start, close_end = close_m.start(), close_m.end()
    opens = [m for m in _SPOKEN_SUMMARY_OPEN.finditer(raw[:close_start])]
    if not opens:
        return None
    open_m = opens[-1]
    attrs = open_m.group(1) or ""
    inner = raw[open_m.end() : close_start].strip()
    state: str | None = None
    if attrs:
        sm = _SPOKEN_STATE_ATTR.search(attrs)
        if sm:
            state = sm.group(1).lower()
    return open_m.start(), close_end, inner, state


def parse_spoken_summary(raw: str) -> tuple[str | None, str | None]:
    span = last_spoken_summary_span(raw)
    if not span:
        return None, None
    _start, _end, inner, state = span
    if not inner:
        return None, state
    return inner, state


def without_spoken_block(raw: str) -> str:
    out = raw
    while True:
        span = last_spoken_summary_span(out)
        if not span:
            break
        start, end, _inner, _state = span
        out = (out[:start] + " " + out[end:]).strip()
    return out
